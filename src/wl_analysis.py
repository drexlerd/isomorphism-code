from collections import defaultdict, deque
from pathlib import Path
from pymimir import State, StateSpace, FaithfulAbstraction, ProblemColorFunction, create_object_graph
from typing import List, Tuple, Union, Deque, Dict
from itertools import combinations
from dataclasses import dataclass

from .performance import memory_usage
from .logger import initialize_logger, add_console_handler
from .pykwl_utils import to_uvc_graph

import pykwl as kwl


class Driver:
    def __init__(self, domain_file_path : Path, problem_file_path : Path, verbosity: str, enable_pruning: bool, max_num_states: int, ignore_counting: bool, mark_true_goal_atoms: bool):
        self._domain_file_path = domain_file_path
        self._problem_file_path = problem_file_path
        self._logger = initialize_logger("wl")
        self._logger.setLevel(verbosity)
        self._verbosity = verbosity.upper()
        self._enable_pruning = enable_pruning
        self._max_num_states = max_num_states
        self._ignore_counting = ignore_counting
        self._mark_true_goal_atoms = mark_true_goal_atoms
        add_console_handler(self._logger)

    def _generate_data(self) -> Tuple[StateSpace, FaithfulAbstraction]:
        state_space = StateSpace.create(
            str(self._domain_file_path),
            str(self._problem_file_path),
            use_unit_cost_one=True,
            remove_if_unsolvable=True,
            max_num_states=self._max_num_states)

        if state_space is None:
            return None

        faithful_abstraction = FaithfulAbstraction.create(
            state_space.get_problem(),
            state_space.get_pddl_factories(),
            state_space.get_aag(),
            state_space.get_ssg(),
            self._mark_true_goal_atoms,
            use_unit_cost_one=True,
            remove_if_unsolvable=True,
            compute_complete_abstraction_mapping=False)

        if faithful_abstraction is None:
            return None

        return (state_space, faithful_abstraction)

    def _validate_wl_correctness_iteratively(self, k: int, state_space: StateSpace, fa: FaithfulAbstraction, partition: List[Tuple[State, int, kwl.EdgeColoredGraph]]):
        """ The idea of the iterative solution is to run a standard DFS.
            Each node gets it own instantiation of WL because the colors in such a partition are identical.
        """

        total_conflicts = 0
        value_conflicts = 0
        max_num_iterations = 0

        @dataclass
        class SearchNode:
            wl : kwl.WeisfeilerLeman
            partition: List[Tuple[int, State, int, kwl.EdgeColoredGraph, kwl.GraphColoring, kwl.GraphColoring]]
            num_previous_iterations: int

        partition_ext = []
        wl = kwl.WeisfeilerLeman(k, self._ignore_counting)
        for state, v_star, kwl_graph in partition:
            current_coloring = wl.compute_initial_coloring(kwl_graph)
            # We only care data compatibility between current and next coloring, so we can call compute_initial_coloring again.
            next_coloring = wl.compute_initial_coloring(kwl_graph)
            partition_ext.append((state, v_star, kwl_graph, current_coloring, next_coloring))

        queue : Deque[SearchNode] = deque()
        queue.append(SearchNode(wl, partition_ext, 0))

        while queue:
            cur_node = queue.pop()
            cur_wl = cur_node.wl
            cur_partition = cur_node.partition
            cur_num_prev_iterations = cur_node.num_previous_iterations

            # 1.1 Run 1-WL until colors start divering
            is_stable_state = dict()
            for state, v_star, kwl_graph, current_coloring, next_coloring in cur_partition:
                is_stable_state[state] = False

            num_iterations = cur_num_prev_iterations

            colorings = set()

            colorings_by_state = dict()

            while True:
                all_stable = True

                num_iterations += 1
                max_num_iterations = max(max_num_iterations, num_iterations)

                next_partition = []
                for element in cur_partition:
                    state, v_star, kwl_graph, current_coloring, next_coloring = element

                    if is_stable_state[state]:
                        next_partition.append(element)
                        continue

                    is_stable = cur_wl.compute_next_coloring(kwl_graph, current_coloring, next_coloring)

                    if is_stable:
                        is_stable_state[state] = True
                    else:
                        all_stable = False

                    colors, counts = next_coloring.get_frequencies()
                    coloring = (num_iterations, tuple(colors), tuple(counts))
                    colorings.add(coloring)
                    colorings_by_state[state] = coloring

                    # swap current and next coloring
                    next_partition.append((state, v_star, kwl_graph, next_coloring, current_coloring))

                cur_partition = next_partition

                if len(colorings) > 1:
                    # Detected diverging state colorings
                    break

                if all_stable:
                    # All are stable
                    break

            # 1.2 Compute the new partitioning
            partitioning = defaultdict(list)
            for (state, v_star, wl_graph, current_coloring, next_coloring) in cur_partition:
                coloring = colorings_by_state[state]

                partitioning[coloring].append((state, v_star, wl_graph, current_coloring, next_coloring))

            # 2. Recursively refine new partitioning
            for coloring, sub_partition in partitioning.items():
                if len(sub_partition) == 1:
                    # Base case 1: partition is singleton set. There cannot be any conflicts.
                    pass
                elif all(is_stable_state[state] for state, _, _, _, _ in sub_partition):
                    # Base case 2: all colors in the partition are stable

                    if len(sub_partition) > 1:

                        for (state_1, v_star_1, _, _, _), (state_2, v_star_2, _, _, _) in combinations(sub_partition, 2):

                            if v_star_1 != v_star_2:
                                value_conflicts += 1
                                self._logger.info(f"[{k}-FWL] Value conflict!")
                            else:
                                self._logger.info(f"[{k}-FWL] Conflict!")
                            total_conflicts += 1


                            self._logger.info(f" > Cost: {v_star_1}; State 1: {state_1.to_string(fa.get_problem(), fa.get_pddl_factories())}")
                            self._logger.info(f" > Cost: {v_star_2}; State 2: {state_2.to_string(fa.get_problem(), fa.get_pddl_factories())}")
                            self._logger.info(f"Goal 1: fluent={[str(literal) for literal in fa.get_problem().get_fluent_goal_condition()]}, derived={[str(literal) for literal in fa.get_problem().get_derived_goal_condition()]}, static={[str(literal) for literal in fa.get_problem().get_static_goal_condition()]}")
                            self._logger.info(f"Goal 2: fluent={[str(literal) for literal in fa.get_problem().get_fluent_goal_condition()]}, derived={[str(literal) for literal in fa.get_problem().get_derived_goal_condition()]}, static={[str(literal) for literal in fa.get_problem().get_static_goal_condition()]}")


                else:
                    # Inductive case:

                    queue.append(SearchNode(kwl.WeisfeilerLeman(k, self._ignore_counting), sub_partition, num_iterations))

            # self._logger.info(f"Finished partition with color function size {wl.get_coloring_function_size()}")

        return total_conflicts, value_conflicts, max_num_iterations


    def _validate_wl_correctness(self, k: int, state_space: StateSpace, faithful_abstraction: FaithfulAbstraction) -> Tuple[int, int, int]:
        # Test representatives from each partition to see if two are mapped to the same class.

        total_conflicts = 0
        value_conflicts = 0
        max_num_iterations = 0

        initial_partitionings: Dict[Tuple[int], List[Tuple[int, State, kwl.EdgeColoredGraph]]] = defaultdict(list)
        color_function = ProblemColorFunction(state_space.get_problem())
        goal_distances = faithful_abstraction.get_goal_distances()
        for abstract_state in faithful_abstraction.get_states():
            certificate = abstract_state.get_certificate()
            v_star = goal_distances[abstract_state.get_index()]
            state = abstract_state.get_representative_state()
            object_graph = create_object_graph(color_function, state_space.get_pddl_factories(), state_space.get_problem(), state, self._mark_true_goal_atoms)
            kwl_graph = to_uvc_graph(object_graph)

            initial_partitionings[tuple(certificate.get_canonical_initial_coloring())].append((state, v_star, kwl_graph))

        for canonical_initial_coloring, initial_partition in initial_partitionings.items():

            self._logger.info(f"Processing partitioning with canonical initial coloring {canonical_initial_coloring}")

            total_conflicts_i, value_conflicts_i, max_num_iterations_i = self._validate_wl_correctness_iteratively(k, state_space, faithful_abstraction, initial_partition)
            total_conflicts += total_conflicts_i
            value_conflicts += value_conflicts_i
            max_num_iterations = max(max_num_iterations, max_num_iterations_i)

        return total_conflicts, value_conflicts, max_num_iterations


    def run(self):
        """ Main loop for computing k-WL and Aut(S(P)) for state space S(P).
        """
        """ Main loop for computing k-WL and Aut(S(P)) for state space S(P).
        """
        self._logger.info(f"[Configuration] [enable_pruning = {self._enable_pruning}, max_num_states = {self._max_num_states}, ignore_counting = {self._ignore_counting}, mark_true_goal_atoms = {self._mark_true_goal_atoms}]")
        self._logger.info(f"[Configuration] Domain file: {self._domain_file_path}")
        self._logger.info(f"[Configuration] Problem file: {self._problem_file_path}")

        self._logger.info("[Pymimir] Generating pairwise non isomorphic states.")
        data = self._generate_data()
        self._logger.info(f"[Pymimir] Peak memory usage: {int(memory_usage())} MiB.")
        if data is None:
            self._logger.info(f"[Pymimir] Got empty set of gfas. Aborting.")
            return

        state_space, faithful_abstraction = data

        total_conflicts = [0, 0]
        value_conflicts = [0, 0]
        max_num_iterations = [0, 0]
        self._logger.info("[1-WL] Run validation...")
        total_conflicts[0], value_conflicts[0], max_num_iterations[0] = self._validate_wl_correctness(1, state_space, faithful_abstraction)
        if total_conflicts[0] > 0:
            self._logger.info("[2-FWL] Run validation...")
            total_conflicts[1], value_conflicts[1], max_num_iterations[1] = self._validate_wl_correctness(2, state_space, faithful_abstraction)

        self._logger.info("[Results] Ran to completion.")
        self._logger.info(f"[Results] Domain: {self._domain_file_path}")
        self._logger.info(f"[Results] Table row: [#P = {faithful_abstraction.get_num_states()}, #S = {state_space.get_num_states()}, #I = {max_num_iterations}, #C = {total_conflicts}, #V = {value_conflicts}]")
