from collections import defaultdict
from pathlib import Path
from pymimir import DomainParser, ProblemParser, Domain, Problem, GroundedSuccessorGenerator, StateSpace, State
from tqdm import tqdm
from typing import List, Tuple

from .logger import initialize_logger, add_console_handler
from .state_graph import StateGraph
from .wl_algorithm import WeisfeilerLeman
from .wl_graph import Graph as WLGraph


def to_uvc_graph(state: State) -> WLGraph:
    state_graph = StateGraph(state, skip_nauty=True)
    uvc_vertices = state_graph._uvc_graph._vertices
    uvc_edges = state_graph._uvc_graph._adj_list
    to_wl_vertex = {}
    wl_graph = WLGraph(False)
    for vertex_id, vertex_data in uvc_vertices.items():
        to_wl_vertex[vertex_id] = wl_graph.add_vertex(vertex_data.color.value)
    for vertex_id, adjacent_ids in uvc_edges.items():
        for adjacent_id in adjacent_ids:
            wl_graph.add_edge(to_wl_vertex[vertex_id], to_wl_vertex[adjacent_id])
    return wl_graph


def to_dec_graph(state: State) -> WLGraph:
    wl_graph = WLGraph(True)
    to_wl_vertex = {}
    # Add nodes.
    for object in state.get_problem().objects:
        to_wl_vertex[object] = wl_graph.add_vertex()
    # Helper function for adding edges.
    def add_labeled_edge(atom, offset):
        # Nullary atoms are added as self-edges for all vertices.
        if atom.predicate.arity == 0:
            for vertex in to_wl_vertex.values():
                wl_graph.add_edge(vertex, vertex, atom.predicate.id + offset)
        # Unary atoms are added as self-edges.
        elif atom.predicate.arity == 1:
            vertex = to_wl_vertex[atom.terms[0]]
            wl_graph.add_edge(vertex, vertex, atom.predicate.id + offset)
        # Binary atoms are added as directed edges.
        elif atom.predicate.arity == 2:
            src_vertex = to_wl_vertex[atom.terms[0]]
            dst_vertex = to_wl_vertex[atom.terms[1]]
            wl_graph.add_edge(src_vertex, dst_vertex, atom.predicate.id + offset)
        else:
            raise RuntimeError("ternary predicate")
    # Add edges.
    try:
        # Add state edges.
        for atom in state.get_atoms():
            add_labeled_edge(atom, 0)
        # Add goal edges.
        for literal in state.get_problem().goal:
            assert not literal.negated
            add_labeled_edge(literal.atom, len(state.get_problem().domain.predicates))
        # Add types
        if len(state.get_problem().domain.types) > 1:
            raise NotImplementedError()
        return wl_graph
    except:
        return None


class Driver:
    def __init__(self, domain_file_path : Path, problem_file_path : Path, verbosity: str):
        self._domain_file_path = domain_file_path
        self._problem_file_path = problem_file_path
        self._logger = initialize_logger("wl")
        self._logger.setLevel(verbosity)
        self._verbosity = verbosity.upper()
        add_console_handler(self._logger)


    def _parse_instance(self) -> Tuple[Domain, Problem]:
        domain_parser = DomainParser(str(self._domain_file_path))
        problem_parser = ProblemParser(str(self._problem_file_path))
        domain = domain_parser.parse()
        problem = problem_parser.parse(domain)
        return domain, problem


    def _generate_states(self, problem: Problem) -> (List[State] | None):
        successor_generator = GroundedSuccessorGenerator(problem)
        state_space = StateSpace.new(problem, successor_generator, 1_000_000)
        if state_space is not None: return state_space.get_states()
        else: return None


    def _partition_with_nauty(self, states: List[State]) -> List[List[State]]:
        partitions = defaultdict(list)
        for state in tqdm(states, mininterval=0.5):
            state_graph = StateGraph(state, skip_nauty=False)
            exact_key = state_graph.nauty_certificate, state_graph.uvc_graph.get_colors()
            partitions[exact_key].append(state)
        return list(partitions.values())


    def _partition_with_wl(self, states: List[State], k, to_graph) -> List[List[State]]:
        partitions = defaultdict(list)
        wl = WeisfeilerLeman(k)
        for state in tqdm(states, mininterval=0.5):
            wl_graph = to_graph(state)
            wl_key = wl.compute_coloring(wl_graph)
            partitions[wl_key].append(state)
        return list(partitions.values())


    def _validate_wl_correctness(self, partitions: List[List[State]], k, to_graph) -> Tuple[bool, int]:
        # Check whether the to_graph function can handle states of this sort.
        if to_graph(partitions[0][0]) is None: return False, -1
        # Test representatives from each partition to see if two are mapped to the same class.
        correct = True
        conflicts = 0
        wl = WeisfeilerLeman(k)
        state_colorings = {}
        for partition in tqdm(partitions, mininterval=0.5):
            representative = partition[0]
            wl_graph = to_graph(representative)
            coloring = wl.compute_coloring(wl_graph)
            if coloring in state_colorings:
                correct = False
                conflicts += 1
                self._logger.info(f"[{k}-FWL] Conflict: {state_colorings[coloring]} and {representative}")
            else:
                state_colorings[coloring] = representative
        return correct, conflicts


    def run(self):
        """ Main loop for computing k-WL and Aut(S(P)) for state space S(P).
        """
        print("Domain file:", self._domain_file_path)
        print("Problem file:", self._problem_file_path)
        print()

        _, problem = self._parse_instance()

        # Generate the state space we will analyze.
        self._logger.info("[Preprocessing] Generating state space...")
        states = self._generate_states(problem)
        if states is None:
            self._logger.info(f"[Preprocessing] State space is too large. Aborting.")
            return
        self._logger.info(f"[Preprocessing] States: {len(states)}")

        # Generate exact equivalence classes.
        partitions = self._partition_with_nauty(states)
        self._logger.info(f"[Nauty] Partitions: {len(partitions)} ")

        # If WL is implemented correctly, then validating correctness the way we do is safe.
        # However, double check by partitioning with WL and if more partitions than with Nauty is found, then something is wrong.
        if self._verbosity == "DEBUG":
            uvc_wl_1_partitions = self._partition_with_wl(states, 1, to_uvc_graph)
            self._logger.info(f"[DEBUG] 1-WL partitions: {len(uvc_wl_1_partitions)} ")

        # Validate 1-FWL on the DEC graph.
        self._logger.info("[1-FWL, DEC] Validating...")
        dec_correct_1, dec_conflicts_1 = self._validate_wl_correctness(partitions, 1, to_dec_graph)
        if (not dec_correct_1) and (dec_conflicts_1 < 0): self._logger.info(f"[1-FWL, DEC] Graph cannot be constructed. Skipping.")
        else: self._logger.info(f"[1-FWL, DEC] Valid: {dec_correct_1}; Conflicts: {dec_conflicts_1}")

        # Validate 1-FWL on the UVC graph.
        self._logger.info("[1-FWL, UVC] Validating...")
        uvc_correct_1, uvc_conflicts_1 = self._validate_wl_correctness(partitions, 1, to_uvc_graph)
        if (not uvc_correct_1) and (uvc_conflicts_1 < 0): self._logger.info(f"[1-FWL, UVC] Graph cannot be constructed. Skipping.")
        else: self._logger.info(f"[1-FWL, UVC] Valid: {uvc_correct_1}; Conflicts: {uvc_conflicts_1}")

        # If 1-FWL produces conflicts on the DEC graph, test 2-FWL.
        if not dec_correct_1:
            self._logger.info("[2-FWL, DEC] Validating...")
            dec_correct_2, dec_conflicts_2 = self._validate_wl_correctness(partitions, 2, to_dec_graph)
            if (not dec_correct_2) and (dec_conflicts_2 < 0): self._logger.info(f"[2-FWL, DEC] Graph cannot be constructed. Skipping.")
            else: self._logger.info(f"[2-FWL, DEC] Valid: {dec_correct_2}; Conflicts: {dec_conflicts_2}")

        # If 1-FWL produces conflicts on the UVC graph, test 2-FWL.
        if not uvc_correct_1:
            self._logger.info("[2-FWL, UVC] Validating...")
            uvc_correct_2, uvc_conflicts_2 = self._validate_wl_correctness(partitions, 2, to_uvc_graph)
            if (not uvc_correct_2) and (uvc_conflicts_2 < 0): self._logger.info(f"[2-FWL, UVC] Graph cannot be constructed. Skipping.")
            else: self._logger.info(f"[2-FWL, UVC] Valid: {uvc_correct_2}; Conflicts: {uvc_conflicts_2}")
