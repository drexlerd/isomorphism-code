import pykwl as kwl

from collections import defaultdict
from pathlib import Path
from pymimir import Atom, Domain, DomainParser, GroundedSuccessorGenerator, Problem, ProblemParser, State, StateSpace
from tqdm import tqdm
from typing import List, Tuple, Union

from .logger import initialize_logger, add_console_handler
from .state_graph import StateGraph
from .key_to_int import KeyToInt
from .exact import create_pynauty_undirected_vertex_colored_graph, compute_nauty_certificate


def to_uvc_graph(state: State, coloring_function : KeyToInt, mark_true_goal_atoms: bool) -> kwl.Graph:
    state_graph = StateGraph(state, coloring_function, mark_true_goal_atoms)
    uvc_vertices = state_graph.uvc_graph.vertices
    uvc_edges = state_graph.uvc_graph.adj_list
    to_wl_vertex = {}
    wl_graph = kwl.Graph(False)
    for vertex_id, vertex_data in uvc_vertices.items():
        to_wl_vertex[vertex_id] = wl_graph.add_node(vertex_data.color.value)
    for vertex_id, adjacent_ids in uvc_edges.items():
        for adjacent_id in adjacent_ids:
            wl_graph.add_edge(to_wl_vertex[vertex_id], to_wl_vertex[adjacent_id])
    return wl_graph



class Driver:
    def __init__(self, data_path : Path, verbosity: str, ignore_counting: bool, mark_true_goal_atoms: bool):
        self._domain_file_path = (data_path / "domain.pddl").resolve()
        self._problem_file_paths = [file.resolve() for file in data_path.iterdir() if file.is_file() and file.name != "domain.pddl"]
        self._logger = initialize_logger("wl")
        self._logger.setLevel(verbosity)
        self._verbosity = verbosity.upper()
        self._ignore_counting = ignore_counting
        self._mark_true_goal_atoms = mark_true_goal_atoms
        add_console_handler(self._logger)


    def _parse_instances(self) -> Tuple[Domain, List[Problem]]:
        domain_parser = DomainParser(str(self._domain_file_path))
        domain = domain_parser.parse()
        problems = []
        for problem_file_path in self._problem_file_paths:
            problem_parser = ProblemParser(str(problem_file_path))
            problem = problem_parser.parse(domain)
            problems.append(problem)
        return domain, problems


    def _generate_state_spaces(self, problems: List[Problem]) -> List[StateSpace]:
        state_spaces = []
        for problem in problems:
            successor_generator = GroundedSuccessorGenerator(problem)
            state_space = StateSpace.new(problem, successor_generator, 1000)

            if state_space is None:
                continue

            state_spaces.append(state_space)
        return state_spaces


    def _partition_with_nauty(self, states: List[State], coloring_function: KeyToInt, progress_bar: bool) -> List[List[State]]:
        partitions = defaultdict(list)
        for state in tqdm(states, mininterval=0.5, disable=not progress_bar):
            state_graph = StateGraph(state, coloring_function, mark_true_goal_atoms=False)
            nauty_certificate = compute_nauty_certificate(create_pynauty_undirected_vertex_colored_graph(state_graph.uvc_graph))
            exact_key = (nauty_certificate, state_graph.uvc_graph.get_colors())
            partitions[exact_key].append(state)

        return list(partitions.values())


    def _partition_with_wl(self, statess: List[List[State]], k: int, to_graph, progress_bar: bool) -> List[List[List[State]]]:
        partitions = defaultdict(list)
        wl = kwl.WeisfeilerLeman(k, self._ignore_counting)
        partitionss = []
        for states in statess:
            for state in tqdm(states, mininterval=0.5, disable=not progress_bar):
                wl_graph = to_graph(state)
                num_iterations, colors, counts = wl.compute_coloring(wl_graph)
                coloring = (num_iterations, tuple(colors), tuple(counts))
                partitions[coloring].append(state)
            partitionss.append(list(partitions.values()))
        return partitionss


    def _validate_wl_correctness(self, state_spaces: List[StateSpace], partitionss: List[List[List[State]]], k: int, to_graph, progress_bar: bool) -> Tuple[bool, int]:
        # Check whether the to_graph function can handle states of this sort.
        for partitions in partitionss:
            if to_graph(partitions[0][0]) is None: return False, -1

        # Test representatives from each partition to see if two are mapped to the same class.
        correct = True
        total_conflicts = 0
        value_conflicts = 0
        wl = kwl.WeisfeilerLeman(k, self._ignore_counting)
        state_colorings = defaultdict(set)

        for i, partitions in enumerate(partitionss):
            for partition in partitions:
                representative = partition[0]
                wl_graph = to_graph(representative)
                num_iterations, colors, counts = wl.compute_coloring(wl_graph)
                coloring = (num_iterations, tuple(colors), tuple(counts))
                state_colorings[coloring].add((representative, i))

        for coloring, representative_infos in state_colorings.items():
            representative_infos = list(representative_infos)

            if len(representative_infos) == 1:
                continue

            correct = False

            for i, (representative_1, i_1) in enumerate(representative_infos):
                v_star_1 = state_spaces[i_1].get_distance_to_goal_state(representative_1)
                for representative_2, i_2 in representative_infos[i_1:]:
                    v_star_2 = state_spaces[i_2].get_distance_to_goal_state(representative_2)

                    if v_star_1 == v_star_2:
                        # Only count conflicts with different v* values
                        continue

                    if i_1 == i_2:
                        # Only count conflicts between instances
                        continue

                    total_conflicts += len(representative_infos) * (len(representative_infos)-1)
                    value_conflicts += len(representative_infos) * (len(representative_infos)-1)

                    self._logger.info(f"[{k}-FWL] Conflict!")
                    self._logger.info(f" > Goal {i_1}: {representative_1.get_problem().goal}")
                    self._logger.info(f" > Goal {i_2}: {representative_2.get_problem().goal}")
                    self._logger.info(f" > Cost: {v_star_1}; State {i_1}: {representative_1.get_atoms()}")
                    self._logger.info(f" > Cost: {v_star_2}; State {i_2}: {representative_2.get_atoms()}")

        return correct, total_conflicts, value_conflicts


    def run(self):
        """ Main loop for computing k-WL and Aut(S(P)) for state space S(P).
        """
        print("Domain file:", self._domain_file_path)
        for i, problem_file_path in enumerate(self._problem_file_paths):
            print(f"Problem {i} file:", problem_file_path)
        print()

        _, problems = self._parse_instances()

        progress_bar = self._verbosity == "DEBUG"

        # Generate the state space we will analyze.
        self._logger.info("[Preprocessing] Generating state space...")
        state_spaces = self._generate_state_spaces(problems)

        if not state_spaces:
            self._logger.info(f"[Preprocessing] State spaces are too large. Aborting.")
            return

        statess = []
        for i, state_space in enumerate(state_spaces):
            states = state_space.get_states()
            statess.append(states)
            self._logger.info(f"[Preprocessing] States {i}: {len(states)}")

        # Generate exact equivalence classes.
        coloring_function = KeyToInt()

        self._logger.info("[Nauty] Computing...")
        partitionss = []
        for i, states in enumerate(statess):
            partitions = self._partition_with_nauty(states, coloring_function, progress_bar)
            partitionss.append(partitions)
            self._logger.info(f"[Nauty] Partitions {i}: {len(partitions)}")

        # If WL is implemented correctly, then validating correctness the way we do is safe.
        # However, double check by partitioning with WL and if more partitions than with Nauty is found, then something is wrong.
        if self._verbosity == "DEBUG":
            def run_partition_config(k: int):
                uvc_c_org_wl_1_partitions_wl_s = self._partition_with_wl(statess, k, lambda state: to_uvc_graph(state, coloring_function, self._mark_true_goal_atoms), progress_bar)
                tag = f"DEBUG, UVC"
                for i, uvc_c_org_wl_1_partitions_wl in enumerate(uvc_c_org_wl_1_partitions_wl_s):
                    self._logger.info(f"[{tag}] {k}-WL partitions {i}: {len(uvc_c_org_wl_1_partitions_wl)}")

            # 1-FWL
            run_partition_config(1)

            # 2-FWL
            run_partition_config(2)

        def run_validation_config(k: int) -> bool:
            correct, total_conflicts, value_conflicts = self._validate_wl_correctness(state_spaces, partitionss, k, lambda state: to_uvc_graph(state, coloring_function, self._mark_true_goal_atoms), progress_bar)
            tag = f"{k}-FWL, UVC"
            if (not correct) and (total_conflicts < 0): self._logger.info(f"[{tag}] Graph cannot be constructed. Skipping.")
            else: self._logger.info(f"[{tag}] Valid: {correct}; Total Conflicts: {total_conflicts}; Value Conflicts: {value_conflicts}")
            return correct

        # 1-FWL
        valid_1ff = run_validation_config(1)

        # 2-FWL
        if not valid_1ff: run_validation_config(2)

        self._logger.info("Ran to completion.")
