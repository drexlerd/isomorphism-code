import pykwl as kwl

from collections import defaultdict, deque
from pathlib import Path
from pymimir import PDDLFactories, PDDLParser, IAAG, ISSG, Problem, State
from typing import List, Tuple, Dict, Any, Deque
from itertools import combinations
from dataclasses import dataclass
import subprocess

import random
from .performance import memory_usage
from .logger import initialize_logger, add_console_handler
from .state_graph import StateGraph
from .color_function import ColorFunction
from .exact import Driver as ExactDriver, compute_nauty_certificate, create_pynauty_undirected_vertex_colored_graph


def to_uvc_graph(pddl_factories: PDDLFactories, problem: Problem,  state: State, coloring_function : ColorFunction, mark_true_goal_atoms: bool) -> kwl.EdgeColoredGraph:

    state_graph = StateGraph(pddl_factories, problem, state, coloring_function, mark_true_goal_atoms)
    initial_coloring = state_graph.compute_initial_coloring(coloring_function)

    # Remap colors to obtain canonical surjective l={1,...,l}
    color_remap = dict()
    for color in sorted(initial_coloring):
        if color not in color_remap:
            # +1 because first color starts at 1
            color_remap[color] = len(color_remap) + 1

    # StateGraph already has antiparallel edges. Hence, we set directed to True here
    wl_graph = kwl.EdgeColoredGraph(False)

    # Copy vertices and edges. The indices remain identical.
    for vertex_id in range(len(state_graph._vertices)):
        wl_graph.add_node(color_remap[initial_coloring[vertex_id]])

    for vertex_id in range(len(state_graph._vertices)):
        for outgoing_vertex_id in state_graph._outgoing_vertices[vertex_id]:
            if (vertex_id < outgoing_vertex_id):
                wl_graph.add_edge(vertex_id, outgoing_vertex_id)
    return wl_graph


@dataclass
class InstanceData:
    id: int
    problem_file_path: str
    parser: PDDLParser
    aag: IAAG
    ssg: ISSG
    goal_distances: Dict[State, int]
    class_representatives: Dict[Any, State]
    class_representatives_by_state_id: Dict[int, State]
    num_total_states: int


class Driver:
    def __init__(self, data_path : Path, verbosity: str, enable_pruning: bool, max_num_states: int, ignore_counting: bool, mark_true_goal_atoms: bool):
        self._domain_file_path = (data_path / "domain.pddl").resolve()
        self._problem_file_paths = [file.resolve() for file in data_path.iterdir() if file.is_file() and file.name != "domain.pddl"]
        self._coloring_function = None
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
            print(problem_file_path)
            if self._coloring_function is None:
                tmp_parser = PDDLParser(str(self._domain_file_path), str(problem_file_path))
                self._coloring_function = ColorFunction(tmp_parser.get_domain())

            try:
                exact_driver = ExactDriver(self._domain_file_path, problem_file_path, "ERROR", False, enable_pruning=self._enable_pruning, max_num_states=self._max_num_states, mark_true_goal_atoms=self._mark_true_goal_atoms, coloring_function=self._coloring_function)
                parser, aag, ssg, goal_distances, class_representatives, search_nodes = exact_driver.run()

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

            class_representatives_by_state_id = dict()
            for equivalence_class_key, state in class_representatives.items():
                equivalence_class_key_to_i[equivalence_class_key] = i
                class_representatives_by_state_id[state.get_id()] = state

            self._logger.info(f"[Nauty] instance = {i}, #representatives = {len(class_representatives)}, #generated nodes = {len(search_nodes)}, #isomorphic representatives across instances = {len(existing_equivalence_keys)}")

            instances.append(InstanceData(i, problem_file_path, parser, aag, ssg, goal_distances, class_representatives, class_representatives_by_state_id, len(search_nodes)))
        return instances


    def _preprocess_data(self, instances: List[InstanceData]) -> Dict[int, Dict[Any, Tuple[int, State, int]]]:
        partitioning_by_canonical_initial_coloring = defaultdict(defaultdict)

        for instance_id, instance in enumerate(instances):
            for equivalence_class_key, state in instance.class_representatives.items():

                state_graph = StateGraph(instance.parser.get_factories(), instance.parser.get_problem(), state, self._coloring_function, self._mark_true_goal_atoms)

                canonical_initial_coloring = tuple(sorted(state_graph.compute_initial_coloring(self._coloring_function)))

                # Deadend states have goal distance infinity represented with -1
                goal_distance = instance.goal_distances.get(state, -1)

                partitioning_by_canonical_initial_coloring[canonical_initial_coloring][equivalence_class_key] = (instance_id, state, goal_distance)

        initial_number_of_states = sum(instance.num_total_states for instance in instances)
        final_number_of_states = sum(len(partition) for partition in partitioning_by_canonical_initial_coloring.values())

        return initial_number_of_states, final_number_of_states, partitioning_by_canonical_initial_coloring

    def _validate_wl_correctness(self, instances: List[InstanceData], partitioning: Dict[int, Dict[Any, Tuple[int, State, int]]]):
        total_conflicts = [0] * 2
        value_conflicts = [0] * 2
        total_conflicts_same_instance = [0] * 2
        value_conflicts_same_instance = [0] * 2

        wl = kwl.CanonicalColorRefinement(False)

        for partition_id, partition in enumerate(partitioning.values()):

            partition_filename = f"partition_{partition_id}.1qm"

            # Dump quotient matrices to a file with format:
            # repr(quotient_matrix) instance_id state_id
            with open(partition_filename, "w") as file:
                for instance_id, state, v_star in partition.values():

                    wl_graph = to_uvc_graph(instances[instance_id].parser.get_factories(), instances[instance_id].parser.get_problem(), state, self._coloring_function, self._mark_true_goal_atoms)

                    wl.calculate(wl_graph, True)

                    quotient_matrix = wl.get_quotient_matrix_string()

                    file.write(f"{quotient_matrix} {instance_id} {state.get_id()} {v_star}\n")

            # Use sort command as follows to sort by first column
            # sort -k 1,1 data.txt

            # Call the sort command using subprocess
            sorted_partition_filename = f"partition_{partition_id}.1qm"
            try:
                subprocess.run(['sort', '-k1,1', '-o', sorted_partition_filename, partition_filename], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error during sorting: {e}")

            # Open the file for reading
            conflict_groups = []
            with open(sorted_partition_filename, "r") as file:
                prev_quotient_matrix_string = None
                prev_instance_id = None
                prev_state_id = None
                prev_v_star = None
                conflict_group = []
                for line in file:
                    quotient_matrix_string, instance_id, state_id, v_star = line.split()
                    instance_id = int(instance_id)
                    state_id = int(state_id)
                    v_star = int(v_star)

                    if prev_quotient_matrix_string is not None and prev_quotient_matrix_string == quotient_matrix_string:
                        # Collect conflicts of a group
                        if not conflict_group:
                            conflict_group.append((prev_instance_id, prev_state_id, prev_v_star))
                        conflict_group.append((instance_id, state_id, v_star))
                    else:
                        if conflict_group:
                            # No more conflicts for the same group
                            conflict_groups.append(conflict_group)
                            conflict_group = []

                    prev_quotient_matrix_string = quotient_matrix_string
                    prev_instance_id = instance_id
                    prev_state_id = state_id
                    prev_v_star = v_star

            for conflict_group in conflict_groups:
                for (instance_id_1, state_id_1, v_star_1), (instance_id_2, state_id_2, v_star_2) in combinations(conflict_group, 2):
                    # Blai: use canonical color refinement as approximation and correct false positives
                    wl1 = kwl.WeisfeilerLeman(1, self._ignore_counting)

                    wl_graph_1 = to_uvc_graph(
                        instances[instance_id_1].parser.get_factories(),
                        instances[instance_id_1].parser.get_problem(),
                        instances[instance_id_1].class_representatives_by_state_id[state_id_1],
                        self._coloring_function,
                        self._mark_true_goal_atoms)

                    wl_graph_2 = to_uvc_graph(
                        instances[instance_id_1].parser.get_factories(),
                        instances[instance_id_1].parser.get_problem(),
                        instances[instance_id_1].class_representatives_by_state_id[state_id_1],
                        self._coloring_function,
                        self._mark_true_goal_atoms)

                    coloring_1 = wl1.compute_coloring(wl_graph_1)
                    coloring_2 = wl1.compute_coloring(wl_graph_2)

                    if coloring_1 != coloring_2:
                        continue

                    print(wl_graph_1)
                    print(wl_graph_2)

                    # Report 1-WL conflict
                    total_conflicts[0] += 1
                    if instance_id_1 == instance_id_2:
                        total_conflicts_same_instance[0] += 1
                    if v_star_1 != v_star_2:
                        value_conflicts[0] += 1
                        if instance_id_1 == instance_id_2:
                            value_conflicts_same_instance[0] += 1
                        self._logger.info(f"[1-WL] Value conflict!")
                    else:
                        self._logger.info(f"[1-WL] Conflict!")

                    self._logger.info(f" > Instance 1: {instances[instance_id_1].problem_file_path}")
                    self._logger.info(f" > Instance 2: {instances[instance_id_2].problem_file_path}")
                    self._logger.info(f" > Cost: {v_star_1}; State 1: {instances[instance_id_1].class_representatives_by_state_id[state_id_1].to_string(instances[instance_id_1].parser.get_problem(), instances[instance_id_1].parser.get_factories())}")
                    self._logger.info(f" > Cost: {v_star_2}; State 2: {instances[instance_id_2].class_representatives_by_state_id[state_id_2].to_string(instances[instance_id_2].parser.get_problem(), instances[instance_id_2].parser.get_factories())}")

                    # Check 2-FWL conflict
                    fwl2 = kwl.WeisfeilerLeman(2, self._ignore_counting)

                    wl_graph_1 = to_uvc_graph(instances[instance_id_1].parser.get_factories(), instances[instance_id_1].parser.get_problem(), instances[instance_id_1].class_representatives_by_state_id[state_id_1], self._coloring_function, self._mark_true_goal_atoms)
                    wl_graph_2 = to_uvc_graph(instances[instance_id_2].parser.get_factories(), instances[instance_id_2].parser.get_problem(), instances[instance_id_2].class_representatives_by_state_id[state_id_2], self._coloring_function, self._mark_true_goal_atoms)

                    fwl2_coloring_1 = fwl2.compute_coloring(wl_graph_1)
                    fwl2_coloring_2 = fwl2.compute_coloring(wl_graph_2)

                    if fwl2_coloring_1 == fwl2_coloring_2:
                        if instance_id_1 == instance_id_2:
                            total_conflicts_same_instance[1] += 1
                        if v_star_1 != v_star_2:
                            value_conflicts[1] += 1
                            if instance_id_1 == instance_id_2:
                                value_conflicts_same_instance[1] += 1
                            self._logger.info(f"[2-FWL] Value conflict!")
                        else:
                            self._logger.info(f"[2-FWL] Conflict!")

                        self._logger.info(f" > Instance 1: {instances[instance_id_1].problem_file_path}")
                        self._logger.info(f" > Instance 2: {instances[instance_id_2].problem_file_path}")
                        self._logger.info(f" > Cost: {v_star_1}; State 1: {instances[instance_id_1].class_representatives_by_state_id[state_id_1].to_string(instances[instance_id_1].parser.get_problem(), instances[instance_id_1].parser.get_factories())}")
                        self._logger.info(f" > Cost: {v_star_2}; State 2: {instances[instance_id_2].class_representatives_by_state_id[state_id_2].to_string(instances[instance_id_2].parser.get_problem(), instances[instance_id_2].parser.get_factories())}")

                    exit(1)

        return total_conflicts, value_conflicts, total_conflicts_same_instance, value_conflicts_same_instance


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
        total_conflicts, value_conflicts, total_conflicts_same_instance, value_conflicts_same_instance = self._validate_wl_correctness(instances, partitioning_by_num_vertices)

        self._logger.info("[Results] Ran to completion.")
        self._logger.info(f"[Results] Domain: {self._domain_file_path}")
        self._logger.info(f"[Results] Configuration: [enable_pruning = {self._enable_pruning}, max_num_states = {self._max_num_states}, ignore_counting = {self._ignore_counting}, mark_true_goal_atoms = {self._mark_true_goal_atoms}]")
        self._logger.info(f"[Results] Table row: [# = {len(instances)}, #P = {final_number_of_states}, #S = {initial_number_of_states}, #C = {total_conflicts}, #V = {value_conflicts}, #C/same = {total_conflicts_same_instance}, #V/same = {value_conflicts_same_instance}]")
        self._logger.info(f"[Results] Peak memory usage: {int(memory_usage())} MiB.")
