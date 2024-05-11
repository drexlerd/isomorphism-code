import pykwl as kwl
import sys

from collections import defaultdict
from pathlib import Path
from pymimir import Atom, Domain, DomainParser, GroundedSuccessorGenerator, Problem, ProblemParser, State, StateSpace
from typing import List, Tuple, Union, Dict, Any
from itertools import combinations
from dataclasses import dataclass

from .search_node import SearchNode
from .logger import initialize_logger, add_console_handler, flush_handlers
from .state_graph import StateGraph
from .key_to_int import KeyToInt
from .exact import Driver as ExactDriver, create_pynauty_undirected_vertex_colored_graph, compute_nauty_certificate


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


@dataclass
class InstanceData:
    id: int
    problem_file_path: str
    goal_distances: Dict[State, int]
    representatives: List[State]
    search_nodes: Dict[State, SearchNode]


class Driver:
    def __init__(self, data_path : Path, verbosity: str, enable_pruning: bool, max_num_states: int, ignore_counting: bool, mark_true_goal_atoms: bool):
        self._domain_file_path = (data_path / "domain.pddl").resolve()
        self._problem_file_paths = [file.resolve() for file in data_path.iterdir() if file.is_file() and file.name != "domain.pddl"]
        self._coloring_function = KeyToInt()
        self._logger = initialize_logger("wl")
        self._logger.setLevel(verbosity)
        self._verbosity = verbosity.upper()
        self._enable_pruning = enable_pruning
        self._max_num_states = max_num_states
        self._ignore_counting = ignore_counting
        self._mark_true_goal_atoms = mark_true_goal_atoms
        add_console_handler(self._logger)


    def _generate_data(self) -> List[InstanceData]:
        instances = []

        for i, problem_file_path in enumerate(self._problem_file_paths):
            try:
                exact_driver = ExactDriver(self._domain_file_path, problem_file_path, "ERROR", False, enable_pruning=self._enable_pruning, max_num_states=self._max_num_states, coloring_function=self._coloring_function)
                _, _, goal_distances, representatives, search_nodes = exact_driver.run()
            except MemoryError:
                self._logger.error(f"Out of memory when generating data for problem: {problem_file_path}")
                flush_handlers(self._logger)
                continue

            if goal_distances is None:
                continue

            self._logger.info(f"[Nauty] instance = {i}, #representatives = {len(representatives)}, #generated nodes = {len(search_nodes)}")
            flush_handlers(self._logger)

            instances.append(InstanceData(i, problem_file_path, goal_distances, representatives, search_nodes))

        return instances


    def _preprocess_data(self, instances: List[InstanceData]) -> Dict[int, Dict[Any, Tuple[State, int]]]:
        partitioning_by_num_vertices = defaultdict(defaultdict)

        for instance_id, instance in enumerate(instances):
            for state, goal_distance in instance.goal_distances.items():

                equivalence_key = instance.search_nodes[state].equivalence_class_key

                num_vertices = StateGraph.get_num_vertices(state)

                partitioning_by_num_vertices[num_vertices][equivalence_key] = (instance_id, state, goal_distance)


        initial_number_of_states = sum(len(instance.search_nodes) for instance in instances)
        final_number_of_states = sum(len(partition) for partition in partitioning_by_num_vertices.values())

        print("[Data processing] Number of partitions by num vertices:", len(partitioning_by_num_vertices))
        print("[Data processing] Initial number of states:", initial_number_of_states)
        print("[Data processing] Final number of states:", final_number_of_states)
        sys.stdout.flush()

        return initial_number_of_states, final_number_of_states, partitioning_by_num_vertices


    def _validate_wl_correctness(self, instances: List[InstanceData], data: Dict[int, Dict[Any, Tuple[State, int]]], to_graph) -> Tuple[bool, int]:
        # Check whether the to_graph function can handle states of this sort.
        #for instance in instances:
        #    if to_graph(instance.representatives[0]) is None: return False, -1, -1

        # Test representatives from each partition to see if two are mapped to the same class.

        k_max = 2

        total_conflicts = [0] * (k_max + 1)
        value_conflicts = [0] * (k_max + 1)

        total_conflicts_same_instance = [0] * (k_max + 1)
        value_conflicts_same_instance = [0] * (k_max + 1)

        count = 0

        for i, key in enumerate(sorted(data.keys())):
            partition = data[key]

            self._logger.info(f"Processing pairs of partition {i} (#vertices in object graph is {key}) with size {len(partition)}")
            flush_handlers(self._logger)

            for (instance_id_1, state_1, v_star_1), (instance_id_2, state_2, v_star_2) in combinations(partition.values(), 2):

                if (count > 0 and count % 10_000 == 0):
                    self._logger.info(f"Finished {count} pairs.")
                    flush_handlers(self._logger)

                count += 1

                for k in range(1, k_max + 1):
                    wl = kwl.WeisfeilerLeman(k, self._ignore_counting)

                    wl_graph_1 = to_graph(state_1)
                    num_iterations_1, colors_1, counts_1 = wl.compute_coloring(wl_graph_1)
                    coloring_1 = (num_iterations_1, tuple(colors_1), tuple(counts_1))

                    wl_graph_2 = to_graph(state_2)
                    num_iterations_2, colors_2, counts_2 = wl.compute_coloring(wl_graph_2)
                    coloring_2 = (num_iterations_2, tuple(colors_2), tuple(counts_2))

                    if (coloring_1 != coloring_2):
                        break

                    total_conflicts[k] += 1
                    if instance_id_1 == instance_id_2:
                        total_conflicts_same_instance[k] += 1
                    if v_star_1 != v_star_2:
                        value_conflicts[k] += 1
                        if instance_id_1 == instance_id_2:
                            value_conflicts_same_instance[k] += 1
                        self._logger.info(f"[{k}-FWL] Value conflict!")
                    else:
                        self._logger.info(f"[{k}-FWL] Conflict!")

                    self._logger.info(f" > Instance 1: {instances[instance_id_1].problem_file_path}")
                    self._logger.info(f" > Instance 2: {instances[instance_id_2].problem_file_path}")
                    self._logger.info(f" > Goal 1: {state_1.get_problem().goal}")
                    self._logger.info(f" > Goal 2: {state_2.get_problem().goal}")
                    self._logger.info(f" > Cost 1: {v_star_1}; State 1: {state_1.get_atoms()}")
                    self._logger.info(f" > Cost 2: {v_star_2}; State 2: {state_2.get_atoms()}")
                    self._logger.info(f" > Color 1: {str(coloring_1)}")
                    self._logger.info(f" > Color 2: {str(coloring_2)}")
                    flush_handlers(self._logger)

                    if k == 2:
                        state_graph_1 = StateGraph(state_1, self._coloring_function)
                        state_graph_2 = StateGraph(state_2, self._coloring_function)

                        nauty_certificate_1 = compute_nauty_certificate(create_pynauty_undirected_vertex_colored_graph(state_graph_1.uvc_graph))
                        equivalence_class_key_1 = (nauty_certificate_1, state_graph_1.uvc_graph.get_color_histogram())

                        nauty_certificate_2 = compute_nauty_certificate(create_pynauty_undirected_vertex_colored_graph(state_graph_2.uvc_graph))
                        equivalence_class_key_2 = (nauty_certificate_2, state_graph_2.uvc_graph.get_color_histogram())

                        assert (equivalence_class_key_1 != equivalence_class_key_2)

        return total_conflicts, value_conflicts, total_conflicts_same_instance, value_conflicts_same_instance


    def run(self):
        """ Main loop for computing k-WL and Aut(S(P)) for state space S(P).
        """
        print("Domain file:", self._domain_file_path)
        for i, problem_file_path in enumerate(self._problem_file_paths):
            print(f"Problem {i} file:", problem_file_path)
        print()
        sys.stdout.flush()

        self._logger.info("[Nauty] Generating representatives...")
        instances = self._generate_data()

        self._logger.info("[Data preprocessing] Preprocessing data...")
        initial_number_of_states, final_number_of_states, partitioning_by_num_vertices = self._preprocess_data(instances)

        if not instances:
            self._logger.info(f"[Preprocessing] State spaces are too large. Aborting.")
            flush_handlers(self._logger)
            return

        coloring_function = KeyToInt()

        self._logger.info("[WL] Run validation...")
        total_conflicts, value_conflicts, total_conflicts_same_instance, value_conflicts_same_instance = self._validate_wl_correctness(instances, partitioning_by_num_vertices, lambda state: to_uvc_graph(state, coloring_function, self._mark_true_goal_atoms))

        self._logger.info("[Results] Ran to completion.")
        self._logger.info(f"[Results] Domain: {self._domain_file_path}")
        self._logger.info(f"[Results] Configuration: [enable_pruning = {self._enable_pruning}, max_num_states = {self._max_num_states}, ignore_counting = {self._ignore_counting}, mark_true_goal_atoms = {self._mark_true_goal_atoms}]")
        self._logger.info(f"[Results] Table row: [# = {len(instances)}, #P = {final_number_of_states}, #S = {initial_number_of_states}, #C = {total_conflicts[1:]}, #V = {value_conflicts[1:]}, #C/same = {total_conflicts_same_instance[1:]}, #V/same = {value_conflicts_same_instance[1:]}]")
        flush_handlers(self._logger)
