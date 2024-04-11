from collections import defaultdict
from pathlib import Path
from pymimir import DomainParser, ProblemParser, GroundedSuccessorGenerator, StateSpace

from .logger import initialize_logger, add_console_handler
from .state_graph import StateGraph
from .wl_algorithm import WeisfeilerLeman
from .wl_graph import Graph as WLGraph


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
        self._logger.info(f"# states: {state_space.num_states()}")
        if not state_space:
            print("Too many states. Aborting.")
            raise Exception("state space is too large")

        # Generate equivalence classes according to an exact algorithm,
        # as well as according to the k-WL algorithm on an undirected node labeled graph.
        wl = WeisfeilerLeman()
        uvc_exact_equivalence_classes = defaultdict(set)
        uvc_wl_equivalence_classes = defaultdict(set)
        self._logger.info("Generating equivalence classes...")
        for state in state_space.get_states():
            # Exact algorithm
            state_graph = StateGraph(state)
            exact_key = (state_graph.nauty_certificate, state_graph.uvc_graph.get_colors())
            uvc_exact_equivalence_classes[exact_key].add(state)
            # WL algorithm
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
            uvc_wl_equivalence_classes[wl_key].add(state)
        self._logger.info(f"# uvc exact equivalence classes: {len(uvc_exact_equivalence_classes)}")
        self._logger.info(f"# uvc wl equivalence classes: {len(uvc_wl_equivalence_classes)}")

        # Generate equivalence classes according to the k-WL algorithm, on a directed and and edge labeled graph.
        wl = WeisfeilerLeman()
        dec_wl_equivalence_classes = defaultdict(set)
        for state in state_space.get_states():
            wl_graph = WLGraph(True)
            to_node = {}
            for object in state.get_problem().objects:
                to_node[object] = wl_graph.add_node()
            # helper function for adding edges
            def add_colored_edge(atom, offset):
                if atom.predicate.arity == 1:
                    node = to_node[atom.terms[0]]
                    wl_graph.add_edge(node, node, atom.predicate.id + offset)
                elif atom.predicate.arity == 2:
                    source_node = to_node[atom.terms[0]]
                    target_node = to_node[atom.terms[1]]
                    wl_graph.add_edge(source_node, target_node, atom.predicate.id + offset)
                else:
                    raise Exception("predicate arity is not 1 or 2")
            # Add state edges
            for atom in state.get_atoms():
                add_colored_edge(atom, 0)
            # Add goal edges
            for literal in state.get_problem().goal:
                assert not literal.negated
                add_colored_edge(literal.atom, len(state.get_problem().domain.predicates))
            # Compute histogram and add state to equivalence class
            wl_key = wl.compute_coloring(wl_graph)
            dec_wl_equivalence_classes[wl_key].add(state)

        self._logger.info(f"# dec wl equivalence classes: {len(dec_wl_equivalence_classes)}")
