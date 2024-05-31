import pykwl as kwl
import sys

from collections import defaultdict, deque
from pathlib import Path
from pymimir import Atom, Domain, DomainParser, GroundedSuccessorGenerator, Problem, ProblemParser, State, StateSpace
from typing import List, Tuple, Union, Dict, Any, Deque
from itertools import combinations
from dataclasses import dataclass


from .performance import memory_usage
from .logger import initialize_logger, add_console_handler
from .state_graph import StateGraph
from .color_function import ColorFunction
from .exact import Driver as ExactDriver, create_pynauty_undirected_vertex_colored_graph, compute_nauty_certificate


def to_uvc_graph(state: State, coloring_function : ColorFunction, mark_true_goal_atoms: bool) -> kwl.EdgeColoredGraph:
    state_graph = StateGraph(state, coloring_function, mark_true_goal_atoms)
    initial_coloring = state_graph.compute_initial_coloring(coloring_function)
    # remap colors to obtain canonical surjective l={1,...,n}
    color_remap = dict()
    for color in sorted(initial_coloring):
        if color not in color_remap:
            color_remap[color] = len(color_remap)

    # state uvc already has antiparallel edges. Hence, we set directed to True here
    wl_graph = kwl.EdgeColoredGraph(False)
    for vertex_id, vertex in enumerate(state_graph._vertices):
        wl_graph.add_node(color_remap[initial_coloring[vertex_id]])
    for vertex_id, vertex in enumerate(state_graph._vertices):
        for outgoing_vertex_id in state_graph._outgoing_vertices[vertex_id]:
            wl_graph.add_edge(vertex_id, outgoing_vertex_id)
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
        domain_parser = DomainParser(str(self._domain_file_path))
        self._domain = domain_parser.parse()
        self._coloring_function = ColorFunction(self._domain)
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
            print("=========================================================")
        exit(1)

        return instances


    def _preprocess_data(self, instances: List[InstanceData]) -> Dict[int, Dict[Any, Tuple[int, State, int]]]:
        partitioning_by_canonical_initial_coloring = defaultdict(defaultdict)

        for instance_id, instance in enumerate(instances):
            for equivalence_class_key, state in instance.class_representatives.items():

                state_graph = StateGraph(state, self._coloring_function)

                canonical_initial_coloring = tuple(sorted(state_graph.compute_initial_coloring(self._coloring_function)))

                # Deadend states have goal distance infinity represented with -1
                goal_distance = instance.goal_distances.get(state, -1)

                partitioning_by_canonical_initial_coloring[canonical_initial_coloring][equivalence_class_key] = (instance_id, state, goal_distance)

        initial_number_of_states = sum(instance.num_total_states for instance in instances)
        final_number_of_states = sum(len(partition) for partition in partitioning_by_canonical_initial_coloring.values())

        return initial_number_of_states, final_number_of_states, partitioning_by_canonical_initial_coloring

    def _validate_1_wl_correctness(self, instances: List[InstanceData], partitioning: Dict[int, Dict[Any, Tuple[int, State, int]]]):
        total_conflicts = 0
        value_conflicts = 0
        total_conflicts_same_instance = 0
        value_conflicts_same_instance = 0

        for num_vertices, partition in partitioning.items():

            histogram_to_datas = defaultdict(list)

            for certificate, (instance_id, state, v_star) in partition.items():

                wl_graph = to_uvc_graph(state, self._coloring_function, self._mark_true_goal_atoms)

                histogram = tuple(kwl.CanonicalColorRefinement.histogram(kwl.CanonicalColorRefinement(False).calculate(wl_graph)))

                histogram_to_datas[histogram].append((instance_id, state, v_star))


            for _, datas in histogram_to_datas.items():
                for (instance_id_1, state_1, v_star_1), (instance_id_2, state_2, v_star_2) in combinations(datas, 2):

                    total_conflicts += 1
                    if instance_id_1 == instance_id_2:
                        total_conflicts_same_instance += 1
                    if v_star_1 != v_star_2:
                        value_conflicts += 1
                        if instance_id_1 == instance_id_2:
                            value_conflicts_same_instance += 1
                        self._logger.info(f"[CanonicalColorRefinement] Value conflict!")
                    else:
                        self._logger.info(f"[CanonicalColorRefinement] Conflict!")

                    self._logger.info(f" > Instance 1: {instances[instance_id_1].problem_file_path}")
                    self._logger.info(f" > Instance 2: {instances[instance_id_2].problem_file_path}")
                    self._logger.info(f" > Cost: {v_star_1}; State 1: {state_1.get_atoms()}")
                    self._logger.info(f" > Cost: {v_star_2}; State 2: {state_2.get_atoms()}")


        return total_conflicts, value_conflicts, total_conflicts_same_instance, value_conflicts_same_instance


    def _validate_wl_correctness_iteratively(self, k, instances: List[InstanceData], partition: List[Tuple[int, State, int, kwl.EdgeColoredGraph, kwl.GraphColoring, kwl.GraphColoring]]):
        """ The idea of the iterative solution is to run a standard DFS.
            Each node gets it own instantiation of WL because the colors in such a partition are identical.
        """

        total_conflicts = 0
        value_conflicts = 0
        total_conflicts_same_instance = 0
        value_conflicts_same_instance = 0
        max_num_iterations = 0

        @dataclass
        class SearchNode:
            wl : kwl.WeisfeilerLeman
            partition: List[Tuple[int, State, int, kwl.EdgeColoredGraph, kwl.GraphColoring, kwl.GraphColoring]]
            num_previous_iterations: int

        queue : Deque[SearchNode] = deque()
        queue.append(SearchNode(kwl.WeisfeilerLeman(k, self._ignore_counting), partition, 0))

        while queue:
            cur_node = queue.pop()
            cur_wl = cur_node.wl
            cur_partition = cur_node.partition
            cur_num_prev_iterations = cur_node.num_previous_iterations

            # 1.1 Run 1-WL until colors start divering
            is_stable_state = dict()
            for (instance_id, state, v_star, wl_graph, current_coloring, next_coloring) in cur_partition:
                is_stable_state[state] = False

            num_iterations = cur_num_prev_iterations

            colorings = set()

            colorings_by_state = dict()

            while True:
                all_stable = True

                num_iterations += 1
                max_num_iterations = max(max_num_iterations, num_iterations)

                next_partition = []
                for (instance_id, state, v_star, wl_graph, current_coloring, next_coloring) in cur_partition:

                    if is_stable_state[state]:
                        next_partition.append((instance_id, state, v_star, wl_graph, current_coloring, next_coloring))
                        continue

                    is_stable = cur_wl.compute_next_coloring(wl_graph, current_coloring, next_coloring)

                    if is_stable:
                        is_stable_state[state] = True
                    else:
                        all_stable = False

                    colors, counts = next_coloring.get_frequencies()
                    coloring = (num_iterations, tuple(colors), tuple(counts))
                    colorings.add(coloring)
                    colorings_by_state[state] = coloring

                    next_partition.append((instance_id, state, v_star, wl_graph, next_coloring, current_coloring))

                cur_partition = next_partition

                if len(colorings) > 1:
                    # Detected diverging state colorings
                    break

                if all_stable:
                    # All are stable
                    break

            # 1.2 Compute the new partitioning
            partitioning = defaultdict(list)
            for (instance_id, state, v_star, wl_graph, current_coloring, next_coloring) in cur_partition:
                coloring = colorings_by_state[state]

                partitioning[coloring].append((instance_id, state, v_star, wl_graph, current_coloring, next_coloring))

            # 2. Recursively refine new partitioning
            for coloring, sub_partition in partitioning.items():
                if len(sub_partition) == 1:
                    # Base case 1: partition is singleton set. There cannot be any conflicts.
                    pass
                elif all(is_stable_state[state] for _, state, _, _, _, _ in sub_partition):
                    # Base case 2: all colors in the partition are stable

                    if len(sub_partition) > 1:

                        self._logger.info(f" > Color: {str(coloring)}")
                        self._logger.info(f" > Goal: {state.get_problem().goal}")

                        for (instance_id_1, state_1, v_star_1, _, _, _), (instance_id_2, state_2, v_star_2, _, _, _) in combinations(sub_partition, 2):

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

                else:
                    # Inductive case:

                    queue.append(SearchNode(kwl.WeisfeilerLeman(k, self._ignore_counting), sub_partition, num_iterations))

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

                # Extend partition by graph and graph colorings
                partition_ext = []
                # Use empty kwl just to allocate initialized GraphColorings
                wl = kwl.WeisfeilerLeman(k, self._ignore_counting)
                for instance_id, state, v_star in partition:
                    wl_graph = to_graph(state)
                    current_coloring = wl.compute_initial_coloring(wl_graph)
                    # We only care data compatibility between current and next coloring, so we can call compute_initial_coloring again.
                    next_coloring = wl.compute_initial_coloring(wl_graph)
                    partition_ext.append((instance_id, state, v_star, wl_graph, current_coloring, next_coloring))

                total_conflicts_i, value_conflicts_i, total_conflicts_same_instance_i, value_conflicts_same_instance_i, max_num_iterations_i = self._validate_wl_correctness_iteratively(k, instances, partition_ext)

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

        self._logger.info("[WL] Run validation...")
        total_conflicts, value_conflicts, total_conflicts_same_instance, value_conflicts_same_instance = self._validate_1_wl_correctness(instances, partitioning_by_num_vertices)

        self._logger.info("[Results] Ran to completion.")
        self._logger.info(f"[Results] Domain: {self._domain_file_path}")
        self._logger.info(f"[Results] Configuration: [enable_pruning = {self._enable_pruning}, max_num_states = {self._max_num_states}, ignore_counting = {self._ignore_counting}, mark_true_goal_atoms = {self._mark_true_goal_atoms}]")
        self._logger.info(f"[Results] Table row: [# = {len(instances)}, #P = {final_number_of_states}, #S = {initial_number_of_states}, #C = {total_conflicts}, #V = {value_conflicts}, #C/same = {total_conflicts_same_instance}, #V/same = {value_conflicts_same_instance}]")
        self._logger.info(f"[Results] Peak memory usage: {int(memory_usage())} MiB.")