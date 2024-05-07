import sys
import time

from pathlib import Path
from collections import defaultdict, deque
from typing import Dict

from pymimir import DomainParser, ProblemParser, LiftedSuccessorGenerator, State
from pynauty import Graph as NautyGraph, certificate

from .state_graph import StateGraph
from .logger import initialize_logger, add_console_handler
from .search_node import SearchNode, CreatingInfo
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

class Driver:
    def __init__(self, domain_file_path : Path, problem_file_path : Path, verbosity: str, dump_dot: bool, enable_pruning: bool):
        self._domain_file_path = domain_file_path
        self._problem_file_path = problem_file_path
        self._dump_dot = dump_dot
        self._enable_pruning = enable_pruning
        self._logger = initialize_logger("exact")
        self._logger.setLevel(verbosity)
        add_console_handler(self._logger)

    def run(self):
        """ Main loop for computing Aut(S(P)) for state space S(P).
        """
        print("Domain file:", self._domain_file_path)
        print("Problem file:", self._problem_file_path)
        print()

        num_generated_states = 0
        equivalence_class_to_index = dict()
        class_index_to_states = defaultdict(set)

        domain_parser = DomainParser(str(self._domain_file_path))
        domain = domain_parser.parse()
        problem_parser = ProblemParser(str(self._problem_file_path))
        problem = problem_parser.parse(domain)
        successor_generator = LiftedSuccessorGenerator(problem)

        self._logger.info("Started generating Aut(G)")
        start_time = time.time()
        initial_state = problem.create_state(problem.initial)
        queue = deque()
        queue.append(initial_state)
        closed_list = set()
        closed_list.add(initial_state)
        search_nodes : Dict[State, SearchNode] = dict()
        search_nodes[initial_state] = SearchNode(creating_infos=[])
        num_generated_states += 1

        coloring_function = KeyToInt()

        while queue:
            cur_state = queue.popleft()

            state_graph = StateGraph(cur_state, coloring_function, mark_true_goal_atoms=False)
            nauty_certificate = compute_nauty_certificate(create_pynauty_undirected_vertex_colored_graph(state_graph.uvc_graph))

            if (num_generated_states % 100 == 1):
                # Overwrite the line in the loop
                print(f"\rAverage time per state: {(time.time() - start_time) / num_generated_states:.3f} seconds", end="")
                sys.stdout.flush()

            equivalence_class_key = (nauty_certificate, state_graph.uvc_graph.get_colors())
            if self._enable_pruning and equivalence_class_key in equivalence_class_to_index:
                # Prune if represenative already exists
                continue

            if equivalence_class_key not in equivalence_class_to_index:
                equivalence_class_to_index[equivalence_class_key] = len(equivalence_class_to_index)
            class_index = equivalence_class_to_index[equivalence_class_key]
            class_index_to_states[class_index].add(state_graph.state)

            if self._dump_dot:
                state_graph.uvc_graph.to_dot(f"outputs/uvcs/{class_index}/{num_generated_states}.gc")

            for applicable_action in successor_generator.get_applicable_actions(cur_state):
                suc_state = applicable_action.apply(cur_state)

                if suc_state in closed_list:
                    # Prune if state already in closed list
                    search_nodes[suc_state].creating_infos.append(CreatingInfo(cur_state, applicable_action))
                    continue
                closed_list.add(suc_state)
                search_nodes[suc_state] = SearchNode(creating_infos=[CreatingInfo(cur_state, applicable_action)])

                num_generated_states += 1

                queue.append(suc_state)
        print()

        end_time = time.time()
        runtime = end_time - start_time
        self._logger.info("Finished generating Aut(G)")
        print(f"Total time: {runtime:.2f} seconds")
        print("Number of generated states:", num_generated_states)
        print("Number of equivalence classes:", len(equivalence_class_to_index))
        print()

        return domain, problem, search_nodes, class_index_to_states