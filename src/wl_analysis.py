from collections import defaultdict
from pathlib import Path
from pymimir import DomainParser, ProblemParser, GroundedSuccessorGenerator, StateSpace, State
from tqdm import tqdm
from typing import Any, Dict, Set

from .logger import initialize_logger, add_console_handler
from .state_graph import StateGraph
from .wl_algorithm import WeisfeilerLeman
from .wl_graph import Graph as WLGraph


def add_to_class_uvc_exact(equivalence_classes: Dict[Any, Set], state_graph: StateGraph, state : State):
    exact_key = state_graph.nauty_certificate, state_graph.uvc_graph.get_colors()
    equivalence_classes[exact_key].add(state)


def add_to_class_uvc_wl(equivalence_classes: Dict[Any, Set], wl: WeisfeilerLeman, state_graph: StateGraph, state : State):
    uvc_vertices = state_graph._uvc_graph._vertices
    uvc_edges = state_graph._uvc_graph._adj_list
    to_wl_vertex = {}
    wl_graph = WLGraph(False)
    for [vertex_id, vertex_data] in uvc_vertices.items():
        to_wl_vertex[vertex_id] = wl_graph.add_node(vertex_data.color.value)
    for [vertex_id, adjacent_ids] in uvc_edges.items():
        for adjacent_id in adjacent_ids:
            wl_graph.add_edge(to_wl_vertex[vertex_id], to_wl_vertex[adjacent_id])
    # Compute histogram and add state to equivalence class
    wl_key = wl.compute_coloring(wl_graph)
    equivalence_classes[wl_key].add(state)


def add_to_class_dec_wl(equivalence_classes: Dict[Any, Set], wl: WeisfeilerLeman, state : State):
    wl_graph = WLGraph(True)
    to_wl_vertex = {}
    # Add nodes.
    for object in state.get_problem().objects:
        to_wl_vertex[object] = wl_graph.add_node()
    # Helper function for adding edges.
    def add_labeled_edge(atom, offset):
        if atom.predicate.arity == 0:
            pass  # Add some information?
            raise Exception("predicate arity is not 1 or 2")
        elif atom.predicate.arity == 1:
            vertex = to_wl_vertex[atom.terms[0]]
            wl_graph.add_edge(vertex, vertex, atom.predicate.id + offset)
        elif atom.predicate.arity == 2:
            src_vertex = to_wl_vertex[atom.terms[0]]
            dst_vertex = to_wl_vertex[atom.terms[1]]
            wl_graph.add_edge(src_vertex, dst_vertex, atom.predicate.id + offset)
        else:
            raise Exception("predicate arity is not 1 or 2")
    # TODO: Add type edges.
    # Add state edges.
    for atom in state.get_atoms():
        add_labeled_edge(atom, 0)
    # Add goal edges.
    for literal in state.get_problem().goal:
        assert not literal.negated
        add_labeled_edge(literal.atom, len(state.get_problem().domain.predicates))
    # Compute histogram and add state to equivalence class.
    wl_key = wl.compute_coloring(wl_graph)
    equivalence_classes[wl_key].add(state)
    if len(equivalence_classes[wl_key]) > 1:
        pass


class Driver:
    def __init__(self, domain_file_path : Path, problem_file_path : Path, verbosity: str):
        self._domain_file_path = domain_file_path
        self._problem_file_path = problem_file_path
        self._logger = initialize_logger("wl")
        self._logger.setLevel(verbosity)
        add_console_handler(self._logger)

    def run(self):
        """ Main loop for computing k-WL and Aut(S(P)) for state space S(P).
        """
        print("Domain file:", self._domain_file_path)
        print("Problem file:", self._problem_file_path)
        print()

        # Parse the domain and the problem.
        domain_parser = DomainParser(str(self._domain_file_path))
        problem_parser = ProblemParser(str(self._problem_file_path))
        domain = domain_parser.parse()
        problem = problem_parser.parse(domain)

        # Generate the state space we will analyze.
        self._logger.info("Generating state space...")
        successor_generator = GroundedSuccessorGenerator(problem)
        state_space = StateSpace.new(problem, successor_generator, 1_000_000)
        states = state_space.get_states()
        self._logger.info(f"# states: {state_space.num_states()}")
        if not state_space:
            print("Too many states. Aborting.")
            raise Exception("state space is too large")

        # Generate equivalence classes according to an exact algorithm,
        # as well as according to the k-WL algorithm on an undirected node labeled graph.
        wl = WeisfeilerLeman(1)
        uvc_exact_equivalence_classes = defaultdict(set)
        uvc_wl_equivalence_classes = defaultdict(set)
        # uvc_wl_debug_equivalence_classes = defaultdict(set)
        self._logger.info("Generating equivalence classes...")
        for state in tqdm(states):
            state_graph = StateGraph(state)
            add_to_class_uvc_exact(uvc_exact_equivalence_classes, state_graph, state)
            add_to_class_uvc_wl(uvc_wl_equivalence_classes, wl, state_graph, state)
        self._logger.info(f"# uvc exact equivalence classes: {len(uvc_exact_equivalence_classes)}")
        self._logger.info(f"# uvc wl equivalence classes: {len(uvc_wl_equivalence_classes)}")
        # self._logger.info(f"# uvc wl debug equivalence classes: {len(uvc_wl_debug_equivalence_classes)}")

        # Generate equivalence classes according to the k-WL algorithm, on a directed and and edge labeled graph.
        wl = WeisfeilerLeman(2)
        dec_wl_equivalence_classes = defaultdict(set)
        for state in tqdm(states):
            add_to_class_dec_wl(dec_wl_equivalence_classes, wl, state)
        self._logger.info(f"# dec wl equivalence classes: {len(dec_wl_equivalence_classes)}")

        # Sanity check that each method produces classes of the same size.
        uvc_exact_histogram = [len(eq_class) for eq_class in uvc_exact_equivalence_classes.values()]
        uvc_exact_histogram.sort()
        uvc_wl_histogram = [len(eq_class) for eq_class in uvc_wl_equivalence_classes.values()]
        uvc_wl_histogram.sort()
        dec_wl_histogram = [len(eq_class) for eq_class in dec_wl_equivalence_classes.values()]
        dec_wl_histogram.sort()
        self._logger.info(f"uvc exact == uvc wl: {uvc_exact_histogram == uvc_wl_histogram}")
        self._logger.info(f"uvc exact == dec wl: {uvc_exact_histogram == dec_wl_histogram}")
        self._logger.info(f"uvc wl == dec wl: {uvc_wl_histogram == dec_wl_histogram}")
