import pykwl as kwl

from collections import defaultdict
from pathlib import Path
from pymimir import Atom, Domain, DomainParser, GroundedSuccessorGenerator, Problem, ProblemParser, State, StateSpace
from tqdm import tqdm
from typing import List, Tuple, Union

from .logger import initialize_logger, add_console_handler
from .state_graph import StateGraph
from .color_function import KeyToInt
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


# def to_dec_graph(state: State) -> kwl.Graph:
#     wl_graph = kwl.Graph(True)
#     to_wl_vertex = {}
#     # Add nodes.
#     for object in state.get_problem().objects:
#         to_wl_vertex[object] = wl_graph.add_node()
#     # Helper function for adding edges.
#     def add_labeled_edge(atom: Atom, offset: int):
#         # Nullary atoms are added as self-edges for all vertices.
#         if atom.predicate.arity == 0:
#             for vertex in to_wl_vertex.values():
#                 wl_graph.add_edge(vertex, vertex, atom.predicate.id + offset)
#         # Unary atoms are added as self-edges.
#         elif atom.predicate.arity == 1:
#             vertex = to_wl_vertex[atom.terms[0]]
#             wl_graph.add_edge(vertex, vertex, atom.predicate.id + offset)
#         # Binary atoms are added as directed edges.
#         elif atom.predicate.arity == 2:
#             src_vertex = to_wl_vertex[atom.terms[0]]
#             dst_vertex = to_wl_vertex[atom.terms[1]]
#             wl_graph.add_edge(src_vertex, dst_vertex, atom.predicate.id + offset)
#         else:
#             raise RuntimeError("ternary predicate")
#     # Add edges.
#     try:
#         # Add state edges.
#         for atom in state.get_atoms():
#             add_labeled_edge(atom, 0)
#         # Add goal edges.
#         for literal in state.get_problem().goal:
#             assert not literal.negated
#             add_labeled_edge(literal.atom, len(state.get_problem().domain.predicates))
#         # Add types
#         if len(state.get_problem().domain.types) > 1:
#             raise NotImplementedError()
#         return wl_graph
#     except:
#         return None


class Driver:
    def __init__(self, domain_file_path : Path, problem_file_path : Path, verbosity: str, ignore_counting: bool, mark_true_goal_atoms: bool):
        self._domain_file_path = domain_file_path
        self._problem_file_path = problem_file_path
        self._logger = initialize_logger("wl")
        self._logger.setLevel(verbosity)
        self._verbosity = verbosity.upper()
        self._ignore_counting = ignore_counting
        self._mark_true_goal_atoms = mark_true_goal_atoms
        add_console_handler(self._logger)


    def _parse_instance(self) -> Tuple[Domain, Problem]:
        domain_parser = DomainParser(str(self._domain_file_path))
        problem_parser = ProblemParser(str(self._problem_file_path))
        domain = domain_parser.parse()
        problem = problem_parser.parse(domain)
        return domain, problem


    def _generate_state_space(self, problem: Problem) -> Union[StateSpace, None]:
        successor_generator = GroundedSuccessorGenerator(problem)
        return StateSpace.new(problem, successor_generator, 1_000_000)


    def _partition_with_nauty(self, states: List[State], coloring_function: KeyToInt, progress_bar: bool) -> List[List[State]]:
        partitions = defaultdict(list)
        for state in tqdm(states, mininterval=0.5, disable=not progress_bar):
            state_graph = StateGraph(state, coloring_function, mark_true_goal_atoms=False)
            nauty_certificate = compute_nauty_certificate(create_pynauty_undirected_vertex_colored_graph(state_graph.uvc_graph))
            exact_key = (nauty_certificate, state_graph.uvc_graph.get_color_histogram())
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


    def _validate_wl_correctness(self, state_space: StateSpace, partitions: List[List[State]], k: int, to_graph, progress_bar: bool) -> Tuple[bool, int]:
        # Check whether the to_graph function can handle states of this sort.
        if to_graph(partitions[0][0]) is None: return False, -1
        # Test representatives from each partition to see if two are mapped to the same class.
        correct = True
        total_conflicts = 0
        value_conflicts = 0
        wl = kwl.WeisfeilerLeman(k, self._ignore_counting)
        state_colorings = {}
        for partition in tqdm(partitions, mininterval=0.5, disable=not progress_bar):
            representative = partition[0]
            wl_graph = to_graph(representative)
            num_iterations, colors, counts = wl.compute_coloring(wl_graph)
            coloring = (num_iterations, tuple(colors), tuple(counts))
            if coloring in state_colorings:
                state_value = state_space.get_distance_to_goal_state(state_colorings[coloring])
                state_atoms = state_colorings[coloring].get_atoms()
                representative_value = state_space.get_distance_to_goal_state(representative)
                representative_atoms = representative.get_atoms()
                self._logger.info(f"[{k}-FWL] Conflict!")
                self._logger.info(f" > Goal: {representative.get_problem().goal}")
                self._logger.info(f" > Cost: {state_value}; State: {state_atoms}")
                self._logger.info(f" > Cost: {representative_value}; State: {representative_atoms}")
                correct = False
                total_conflicts += 1
                value_conflicts += 1 if state_value != representative_value else 0
            else:
                state_colorings[coloring] = representative
        return correct, total_conflicts, value_conflicts


    def run(self):
        """ Main loop for computing k-WL and Aut(S(P)) for state space S(P).
        """
        print("Domain file:", self._domain_file_path)
        print("Problem file:", self._problem_file_path)
        print()

        _, problem = self._parse_instance()
        progress_bar = self._verbosity == "DEBUG"

        # Generate the state space we will analyze.
        self._logger.info("[Preprocessing] Generating state space...")
        state_space = self._generate_state_space(problem)

        if state_space is None:
            self._logger.info(f"[Preprocessing] State space is too large. Aborting.")
            return

        states = state_space.get_states()
        self._logger.info(f"[Preprocessing] States: {len(states)}")

        # Generate exact equivalence classes.
        coloring_function = KeyToInt()

        self._logger.info("[Nauty] Computing...")
        partitions = self._partition_with_nauty(states, coloring_function, progress_bar)
        self._logger.info(f"[Nauty] Partitions: {len(partitions)}")

        # If WL is implemented correctly, then validating correctness the way we do is safe.
        # However, double check by partitioning with WL and if more partitions than with Nauty is found, then something is wrong.
        if self._verbosity == "DEBUG":
            def run_partition_config(k: int):
                uvc_c_org_wl_1_partitions_wl = self._partition_with_wl(states, k, lambda state: to_uvc_graph(state, coloring_function, self._mark_true_goal_atoms), progress_bar)
                tag = f"DEBUG, UVC"
                self._logger.info(f"[{tag}] {k}-WL partitions: {len(uvc_c_org_wl_1_partitions_wl)}")

            # 1-FWL
            run_partition_config(1)

            # 2-FWL
            run_partition_config(2)

        def run_validation_config(k: int) -> bool:
            correct, total_conflicts, value_conflicts = self._validate_wl_correctness(state_space, partitions, k, lambda state: to_uvc_graph(state, coloring_function, self._mark_true_goal_atoms), progress_bar)
            tag = f"{k}-FWL, UVC"
            if (not correct) and (total_conflicts < 0): self._logger.info(f"[{tag}] Graph cannot be constructed. Skipping.")
            else: self._logger.info(f"[{tag}] Valid: {correct}; Total Conflicts: {total_conflicts}; Value Conflicts: {value_conflicts}")
            return correct

        # 1-FWL
        valid_1ff = run_validation_config(1)

        # 2-FWL
        if not valid_1ff: run_validation_config(2)

        self._logger.info("Ran to completion.")
