import pykwl as kwl
import sys

from collections import defaultdict
from pathlib import Path
from pymimir import Atom, Domain, DomainParser, GroundedSuccessorGenerator, Problem, ProblemParser, State, StateSpace
from typing import List, Tuple, Union, Dict, Any
from itertools import combinations
from dataclasses import dataclass

from .search_node import SearchNode
from .logger import initialize_logger, add_console_handler
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
    class_representatives: Dict[Any, State]
    num_total_states: int


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

        equivalence_class_key_to_i = dict()

        for i, problem_file_path in enumerate(self._problem_file_paths):
            try:
                exact_driver = ExactDriver(self._domain_file_path, problem_file_path, "ERROR", False, enable_pruning=self._enable_pruning, max_num_states=self._max_num_states, coloring_function=self._coloring_function)
                _, _, goal_distances, class_representatives, search_nodes = exact_driver.run()

            except MemoryError:
                self._logger.error(f"Out of memory when generating data for problem: {problem_file_path}")
                continue

            if goal_distances is None:
                continue

            ## Prune isomorphic states
            existing_equivalence_keys = []
            for equivalence_class_key in class_representatives:
                if equivalence_class_key in equivalence_class_key_to_i:
                    existing_equivalence_keys.append(equivalence_class_key)

            for equivalence_class_key in existing_equivalence_keys:
                del class_representatives[equivalence_class_key]

            for equivalence_class_key in class_representatives:
                equivalence_class_key_to_i[equivalence_class_key] = i

            self._logger.info(f"[Nauty] instance = {i}, #representatives = {len(class_representatives)}, #generated nodes = {len(search_nodes)}, #isomorphic representatives across instances = {len(existing_equivalence_keys)}")

            instances.append(InstanceData(i, problem_file_path, goal_distances, class_representatives, len(search_nodes)))

        return instances


    def _preprocess_data(self, instances: List[InstanceData]) -> Dict[int, Dict[Any, Tuple[int, State, int]]]:
        partitioning_by_num_vertices = defaultdict(defaultdict)

        for instance_id, instance in enumerate(instances):
            for equivalence_class_key, state in instance.class_representatives.items():

                num_vertices = StateGraph.get_num_vertices(state)

                # Deadend states have goal distance infinity represented with -1
                goal_distance = instance.goal_distances.get(state, -1)

                partitioning_by_num_vertices[num_vertices][equivalence_class_key] = (instance_id, state, goal_distance)


        initial_number_of_states = sum(instance.num_total_states for instance in instances)
        final_number_of_states = sum(len(partition) for partition in partitioning_by_num_vertices.values())

        return initial_number_of_states, final_number_of_states, partitioning_by_num_vertices


    def _validate_wl_correctness_recursively(self, k, num_iterations: int, instances: List[InstanceData], partition: List[Tuple[int, State, int]], to_graph):
        total_conflicts = 0
        value_conflicts = 0
        total_conflicts_same_instance = 0
        value_conflicts_same_instance = 0

        # 1. Instantiate 1-WL
        wl = kwl.WeisfeilerLeman(k, self._ignore_counting)

        # 2. Compute repartitioning
        partioning = defaultdict(list)
        is_stable_state = dict()
        for (instance_id, state, v_star) in partition:
            wl_graph = to_graph(state)
            is_stable, num_iterations, colors, counts = wl.compute_coloring(wl_graph, num_iterations)
            coloring = (num_iterations, tuple(colors), tuple(counts))
            partioning[coloring].append((instance_id, state, v_star))
            is_stable_state[state] = is_stable

        # 3. Recursively refine partitions
        max_num_iterations = 0
        for coloring, sub_partition in partioning.items():
            # Base case 1: all colors in the partition are stable
            if all(is_stable_state[state] for _, state, _ in sub_partition):

                max_num_iterations = max(max_num_iterations, num_iterations)

                if len(sub_partition) > 1:

                    self._logger.info(f" > Color: {str(coloring)}")
                    self._logger.info(f" > Goal: {state.get_problem().goal}")

                    for (instance_id_1, state_1, v_star_1), (instance_id_2, state_2, v_star_2) in combinations(sub_partition, 2):

                        total_conflicts += 1
                        if instance_id_1 == instance_id_2:
                            total_conflicts_same_instance += 1
                        if v_star_1 != v_star_2:
                            value_conflicts += 1
                            if instance_id_1 == instance_id_2:
                                value_conflicts_same_instance += 1
                            self._logger.info(f"[{k}-FWL] Value conflict!")
                        else:
                            self._logger.info(f"[{k}-FWL] Conflict!")

                        self._logger.info(f" > Instance 1: {instances[instance_id_1].problem_file_path}")
                        self._logger.info(f" > Instance 2: {instances[instance_id_2].problem_file_path}")
                        self._logger.info(f" > Cost: {v_star_1}; State 1: {state_1.get_atoms()}")
                        self._logger.info(f" > Cost: {v_star_2}; State 2: {state_2.get_atoms()}")

                continue

            total_conflicts_i, value_conflicts_i, total_conflicts_same_instance_i, value_conflicts_same_instance_i, max_num_iterations_i = self._validate_wl_correctness_recursively(k, num_iterations+1, instances, sub_partition, to_graph)

            total_conflicts += total_conflicts_i
            value_conflicts += value_conflicts_i
            total_conflicts_same_instance += total_conflicts_same_instance_i
            value_conflicts_same_instance += value_conflicts_same_instance_i
            max_num_iterations = max(max_num_iterations, max_num_iterations_i)

        # self._logger.info(f"Finished partition with color function size {wl.get_coloring_function_size()}")

        return total_conflicts, value_conflicts, total_conflicts_same_instance, value_conflicts_same_instance, max_num_iterations


    def _validate_wl_correctness(self, instances: List[InstanceData], data: Dict[int, Dict[Any, Tuple[int, State, int]]], to_graph) -> Tuple[bool, int]:
        # Test representatives from each partition to see if two are mapped to the same class.

        k_max = 2

        total_conflicts = [0] * (k_max + 1)
        value_conflicts = [0] * (k_max + 1)

        total_conflicts_same_instance = [0] * (k_max + 1)
        value_conflicts_same_instance = [0] * (k_max + 1)

        max_num_iterations = [0] * (k_max + 1)

        candidate_partitions = []
        for i, key in enumerate(sorted(data.keys())):
            partition = data[key]
            candidate_partitions.append(list(partition.values()))

        for k in range(1, 3):

            next_candidate_partitions = []

            for i, partition in enumerate(candidate_partitions):

                self._logger.info(f"Processing pairs of partition {i} with size {len(partition)}")

                total_conflicts_i, value_conflicts_i, total_conflicts_same_instance_i, value_conflicts_same_instance_i, max_num_iterations_i = self._validate_wl_correctness_recursively(k, 1, instances, partition, to_graph)

                total_conflicts[k] += total_conflicts_i
                value_conflicts[k] += value_conflicts_i
                total_conflicts_same_instance[k] += total_conflicts_same_instance_i
                value_conflicts_same_instance[k] += value_conflicts_same_instance_i
                max_num_iterations[k] = max(max_num_iterations[k], max_num_iterations_i)

                if total_conflicts_i != 0 or value_conflicts_i != 0:
                    next_candidate_partitions.append(partition)

            self._logger.info(f"[{k}-WL] #C = {total_conflicts[k]}, #V = {value_conflicts[k]}, #C/same = {total_conflicts_same_instance[k]}, #V/same = {value_conflicts_same_instance[k]}]")

            if not next_candidate_partitions:
                break

            candidate_partitions = next_candidate_partitions

        return total_conflicts, value_conflicts, total_conflicts_same_instance, value_conflicts_same_instance, max_num_iterations


    def run(self):
        """ Main loop for computing k-WL and Aut(S(P)) for state space S(P).
        """
        print("Domain file:", self._domain_file_path)
        for i, problem_file_path in enumerate(self._problem_file_paths):
            print(f"Problem {i} file:", problem_file_path)
        print()

        self._logger.info("[Nauty] Generating representatives...")
        instances = self._generate_data()

        self._logger.info("[Data preprocessing] Preprocessing data...")
        initial_number_of_states, final_number_of_states, partitioning_by_num_vertices = self._preprocess_data(instances)
        self._logger.info(f"[Data processing] Number of partitions by num vertices: {len(partitioning_by_num_vertices)}")
        self._logger.info(f"[Data processing] Initial number of states: {initial_number_of_states}")
        self._logger.info(f"[Data processing] Final number of states: {final_number_of_states}")

        if not instances:
            self._logger.info(f"[Preprocessing] State spaces are too large. Aborting.")
            return

        coloring_function = KeyToInt()

        self._logger.info("[WL] Run validation...")
        total_conflicts, value_conflicts, total_conflicts_same_instance, value_conflicts_same_instance, max_num_iterations = self._validate_wl_correctness(instances, partitioning_by_num_vertices, lambda state: to_uvc_graph(state, coloring_function, self._mark_true_goal_atoms))

        self._logger.info("[Results] Ran to completion.")
        self._logger.info(f"[Results] Domain: {self._domain_file_path}")
        self._logger.info(f"[Results] Configuration: [enable_pruning = {self._enable_pruning}, max_num_states = {self._max_num_states}, ignore_counting = {self._ignore_counting}, mark_true_goal_atoms = {self._mark_true_goal_atoms}]")
        self._logger.info(f"[Results] Table row: [# = {len(instances)}, #P = {final_number_of_states}, #S = {initial_number_of_states}, #I = {max_num_iterations[1:]}, #C = {total_conflicts[1:]}, #V = {value_conflicts[1:]}, #C/same = {total_conflicts_same_instance[1:]}, #V/same = {value_conflicts_same_instance[1:]}]")
