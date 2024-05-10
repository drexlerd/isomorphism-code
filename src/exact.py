import sys
import time

from pathlib import Path
from collections import defaultdict, deque
from typing import Dict

from pymimir import DomainParser, ProblemParser, LiftedSuccessorGenerator, State
from pynauty import Graph as NautyGraph, certificate

from .state_graph import StateGraph
from .logger import initialize_logger, add_console_handler
from .search_node import SearchNode
from .key_to_int import KeyToInt
from .uvc_graph import UVCGraph


def create_pynauty_undirected_vertex_colored_graph(uvc_graph: UVCGraph) -> NautyGraph:
        # remap vertex indices
        old_to_new_vertex_index = dict()
        for vertex in uvc_graph.vertices.values():
            old_to_new_vertex_index[vertex.id] = len(old_to_new_vertex_index)
        adjacency_dict = defaultdict(set)
        for source_id, target_ids in uvc_graph.adj_list.items():
            adjacency_dict[old_to_new_vertex_index[source_id]] = set(old_to_new_vertex_index[target_id] for target_id in target_ids)
        # compute vertex partitioning
        color_to_vertices = defaultdict(set)
        for vertex in uvc_graph.vertices.values():
            color_to_vertices[vertex.color.value].add(old_to_new_vertex_index[vertex.id])
        color_to_vertices = dict(sorted(color_to_vertices.items()))
        vertex_coloring = list(color_to_vertices.values())

        graph = NautyGraph(
            number_of_vertices=len(old_to_new_vertex_index),
            directed=False,
            adjacency_dict=adjacency_dict,
            vertex_coloring=vertex_coloring)
        return graph

def compute_nauty_certificate(nauty_graph: NautyGraph):
    return certificate(nauty_graph)

logger = initialize_logger("exact")
add_console_handler(logger)

class Driver:
    def __init__(self, domain_file_path : Path, problem_file_path : Path, verbosity: str, dump_dot: bool, enable_pruning: bool, max_num_states: int, coloring_function: KeyToInt = None):
        self._domain_file_path = domain_file_path
        self._problem_file_path = problem_file_path
        self._dump_dot = dump_dot
        self._enable_pruning = enable_pruning
        self._max_num_states = max_num_states
        self._coloring_function = coloring_function if coloring_function is not None else KeyToInt()

        global logger
        logger.setLevel(verbosity)
        self._logger = logger


    def run(self):
        """ Main loop for computing Aut(S(P)) for state space S(P).
        """
        self._logger.info(f"Domain file: {self._domain_file_path}")
        self._logger.info(f"Problem file: {self._problem_file_path}")

        class_states = defaultdict(set)
        class_representative = dict()

        domain_parser = DomainParser(str(self._domain_file_path))
        domain = domain_parser.parse()
        problem_parser = ProblemParser(str(self._problem_file_path))
        problem = problem_parser.parse(domain)
        successor_generator = LiftedSuccessorGenerator(problem)

        self._logger.info("Started generating Aut(G)")
        start_time = time.time()
        initial_state = problem.create_state(problem.initial)
        state_graph = StateGraph(initial_state, self._coloring_function, mark_true_goal_atoms=False)
        nauty_certificate = compute_nauty_certificate(create_pynauty_undirected_vertex_colored_graph(state_graph.uvc_graph))
        equivalence_class_key = (nauty_certificate, state_graph.uvc_graph.get_color_histogram())
        class_representative[equivalence_class_key] = initial_state
        class_states[equivalence_class_key].add(initial_state)

        queue = deque()
        queue.append(initial_state)
        closed_list = set()
        closed_list.add(initial_state)
        search_nodes : Dict[State, SearchNode] = dict()
        search_nodes[initial_state] = SearchNode([], 0, equivalence_class_key)
        goal_states = set()

        while queue:
            cur_state = queue.popleft()
            cur_search_node = search_nodes[cur_state]
            cur_representative = class_representative[cur_search_node.equivalence_class_key]

            if cur_state.literals_hold(problem.goal):
                goal_states.add(cur_state)

            for applicable_action in successor_generator.get_applicable_actions(cur_state):
                suc_state = applicable_action.apply(cur_state)

                if suc_state in closed_list:
                    # State has already been generated
                    suc_representative = class_representative[search_nodes[suc_state].equivalence_class_key]
                    if self._enable_pruning:
                        # Pruning case: use representative states
                        search_nodes[suc_representative].parent_states.append(cur_representative)
                    else:
                        # Complete case: use original states
                        search_nodes[suc_state].parent_states.append(cur_state)
                    continue

                state_graph = StateGraph(suc_state, self._coloring_function, mark_true_goal_atoms=False)
                nauty_certificate = compute_nauty_certificate(create_pynauty_undirected_vertex_colored_graph(state_graph.uvc_graph))
                equivalence_class_key = (nauty_certificate, state_graph.uvc_graph.get_color_histogram())

                if equivalence_class_key not in class_representative:
                    class_representative[equivalence_class_key] = suc_state
                    if self._dump_dot:
                        state_graph.uvc_graph.to_dot(f"outputs/uvcs/{len(class_representative)}/{len(search_nodes)}.gc")
                class_states[equivalence_class_key].add(suc_state)

                suc_representative = class_representative[equivalence_class_key]

                if self._enable_pruning:
                    closed_list.add(suc_state)
                    queue.append(suc_representative)
                    search_nodes[suc_state] = SearchNode([cur_representative,], cur_search_node.g_value + 1, equivalence_class_key)
                else:
                    closed_list.add(suc_state)
                    queue.append(suc_state)
                    search_nodes[suc_state] = SearchNode([cur_state,], cur_search_node.g_value + 1, equivalence_class_key)

                if (len(search_nodes) >= self._max_num_states):
                    return [None] * 5

        queue = deque()
        goal_distances = dict()
        for goal_state in goal_states:
            queue.append(goal_state)
            goal_distances[goal_state] = 0

        while queue:
            cur_state = queue.popleft()

            for pre_state in search_nodes[cur_state].parent_states:

                if pre_state in goal_distances:
                    continue

                goal_distances[pre_state] = goal_distances[cur_state] + 1
                queue.append(pre_state)



        end_time = time.time()
        runtime = end_time - start_time
        self._logger.info("Finished generating Aut(G)")
        self._logger.info(f"Total time: {runtime:.2f} seconds")
        self._logger.info(f"Number of generated states: {len(search_nodes)}")
        self._logger.info(f"Number of equivalence classes: {len(class_representative)}")

        return domain, problem, goal_distances, list(class_representative.values()), search_nodes