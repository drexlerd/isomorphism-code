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
    def __init__(self, domain_file_path : Path, problem_file_path_1 : Path, problem_file_path_2 : Path, verbosity: str, ignore_counting: bool, mark_true_goal_atoms: bool):
        self._domain_file_path = domain_file_path
        self._problem_file_path_1 = problem_file_path_1
        self._problem_file_path_2 = problem_file_path_2
        self._logger = initialize_logger("wl")
        self._logger.setLevel(verbosity)
        self._verbosity = verbosity.upper()
        self._ignore_counting = ignore_counting
        self._mark_true_goal_atoms = mark_true_goal_atoms
        add_console_handler(self._logger)


    def _parse_instances(self) -> Tuple[Domain, Problem]:
        domain_parser = DomainParser(str(self._domain_file_path))
        problem_parser_1 = ProblemParser(str(self._problem_file_path_1))
        problem_parser_2 = ProblemParser(str(self._problem_file_path_2))
        domain = domain_parser.parse()
        problem_1 = problem_parser_1.parse(domain)
        problem_2 = problem_parser_2.parse(domain)
        return domain, problem_1, problem_2


    def _generate_state_space(self, problem: Problem) -> Union[StateSpace, None]:
        successor_generator = GroundedSuccessorGenerator(problem)
        return StateSpace.new(problem, successor_generator, 1_000_000)


    def _partition_with_nauty(self, states: List[State], coloring_function: KeyToInt, progress_bar: bool) -> List[List[State]]:
        partitions = defaultdict(list)
        for state in tqdm(states, mininterval=0.5, disable=not progress_bar):
            state_graph = StateGraph(state, coloring_function, mark_true_goal_atoms=False)
            nauty_certificate = compute_nauty_certificate(create_pynauty_undirected_vertex_colored_graph(state_graph.uvc_graph))
            exact_key = (nauty_certificate, state_graph.uvc_graph.get_colors())
            partitions[exact_key].append(state)

        return list(partitions.values())


    def _partition_with_wl(self, states: List[State], k: int, to_graph, progress_bar: bool) -> List[List[State]]:
        partitions = defaultdict(list)
        wl = kwl.WeisfeilerLeman(k, self._ignore_counting)
        for state in tqdm(states, mininterval=0.5, disable=not progress_bar):
            wl_graph = to_graph(state)
            num_iterations, colors, counts = wl.compute_coloring(wl_graph)
            coloring = (num_iterations, tuple(colors), tuple(counts))
            partitions[coloring].append(state)
        return list(partitions.values())


    def _validate_wl_correctness(self, state_space_1: StateSpace, partitions_1: List[List[State]], state_space_2: StateSpace, partitions_2: List[List[State]], k: int, to_graph, progress_bar: bool) -> Tuple[bool, int]:
        # Check whether the to_graph function can handle states of this sort.
        if to_graph(partitions_1[0][0]) is None: return False, -1
        if to_graph(partitions_2[0][0]) is None: return False, -1
        # Test representatives from each partition to see if two are mapped to the same class.
        correct = True
        total_conflicts = 0
        value_conflicts = 0
        wl = kwl.WeisfeilerLeman(k, self._ignore_counting)
        state_colorings_1 = {}
        for partition in partitions_1:
            representative = partition[0]
            wl_graph = to_graph(representative)
            num_iterations, colors, counts = wl.compute_coloring(wl_graph)
            coloring = (num_iterations, tuple(colors), tuple(counts))
            state_colorings_1[coloring] = representative

        for partition_2 in partitions_2:
            representative_2 = partition_2[0]
            v_star_2 = state_space_2.get_distance_to_goal_state(representative_2)
            wl_graph = to_graph(representative_2)
            num_iterations, colors, counts = wl.compute_coloring(wl_graph)
            coloring_2 = (num_iterations, tuple(colors), tuple(counts))

            if coloring_2 in state_colorings_1:
                representative_1 = state_colorings_1[coloring_2]
                v_star_1 = state_space_1.get_distance_to_goal_state(representative_1)

                #if v_star_1 == v_star_2:
                    # Skip states with same v*
                #    continue

                self._logger.info(f"[{k}-FWL] Conflict!")
                self._logger.info(f" > Goal 1: {representative_1.get_problem().goal}")
                self._logger.info(f" > Goal 2: {representative_2.get_problem().goal}")
                self._logger.info(f" > Cost: {v_star_1}; State 1: {representative_1.get_atoms()}")
                self._logger.info(f" > Cost: {v_star_2}; State 2: {representative_2.get_atoms()}")
                correct = False
                total_conflicts += 1
                value_conflicts += 1

        return correct, total_conflicts, value_conflicts


    def run(self):
        """ Main loop for computing k-WL and Aut(S(P)) for state space S(P).
        """
        print("Domain file:", self._domain_file_path)
        print("Problem 1 file:", self._problem_file_path_1)
        print("Problem 2 file:", self._problem_file_path_2)
        print()

        _, problem_1, problem_2 = self._parse_instances()

        progress_bar = self._verbosity == "DEBUG"

        # Generate the state space we will analyze.
        self._logger.info("[Preprocessing] Generating state space...")
        state_space_1 = self._generate_state_space(problem_1)
        state_space_2 = self._generate_state_space(problem_2)

        if state_space_1 is None or state_space_2 is None:
            self._logger.info(f"[Preprocessing] State spaces are too large. Aborting.")
            return

        states_1 = state_space_1.get_states()
        states_2 = state_space_2.get_states()
        self._logger.info(f"[Preprocessing] States 1: {len(states_1)}")
        self._logger.info(f"[Preprocessing] States 2: {len(states_2)}")

        # Generate exact equivalence classes.
        coloring_function = KeyToInt()

        self._logger.info("[Nauty] Computing...")
        partitions_1 = self._partition_with_nauty(states_1, coloring_function, progress_bar)
        partitions_2 = self._partition_with_nauty(states_2, coloring_function, progress_bar)
        self._logger.info(f"[Nauty] Partitions 1: {len(partitions_1)}")
        self._logger.info(f"[Nauty] Partitions 2: {len(partitions_2)}")

        # If WL is implemented correctly, then validating correctness the way we do is safe.
        # However, double check by partitioning with WL and if more partitions than with Nauty is found, then something is wrong.
        if self._verbosity == "DEBUG":
            def run_partition_config(k: int):
                uvc_c_org_wl_1_partitions_wl_1 = self._partition_with_wl(states_1, k, lambda state: to_uvc_graph(state, coloring_function, self._mark_true_goal_atoms), progress_bar)
                uvc_c_org_wl_1_partitions_wl_2 = self._partition_with_wl(states_2, k, lambda state: to_uvc_graph(state, coloring_function, self._mark_true_goal_atoms), progress_bar)
                tag = f"DEBUG, UVC"
                self._logger.info(f"[{tag}] {k}-WL partitions 1: {len(uvc_c_org_wl_1_partitions_wl_1)}")
                self._logger.info(f"[{tag}] {k}-WL partitions 2: {len(uvc_c_org_wl_1_partitions_wl_2)}")

            # 1-FWL
            run_partition_config(1)

            # 2-FWL
            run_partition_config(2)

        def run_validation_config(k: int) -> bool:
            correct, total_conflicts, value_conflicts = self._validate_wl_correctness(state_space_1, partitions_1, state_space_2, partitions_2, k, lambda state: to_uvc_graph(state, coloring_function, self._mark_true_goal_atoms), progress_bar)
            tag = f"{k}-FWL, UVC"
            if (not correct) and (total_conflicts < 0): self._logger.info(f"[{tag}] Graph cannot be constructed. Skipping.")
            else: self._logger.info(f"[{tag}] Valid: {correct}; Total Conflicts: {total_conflicts}; Value Conflicts: {value_conflicts}")
            return correct

        # 1-FWL
        valid_1ff = run_validation_config(1)

        # 2-FWL
        if not valid_1ff: run_validation_config(2)

        self._logger.info("Ran to completion.")
