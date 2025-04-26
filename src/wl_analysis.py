from collections import defaultdict
from pathlib import Path
import re

import pymimir.advanced.formalism as formalism
import pymimir.advanced.search as search
import pymimir.advanced.datasets as datasets
import pymimir.advanced.graphs as graphs

from typing import List, Tuple, Dict, Any, MutableSet
from itertools import combinations
from dataclasses import dataclass
import subprocess

from .performance import memory_usage
from .logger import initialize_logger, add_console_handler


@dataclass 
class StateInformation:
    state: search.State
    problem: formalism.Problem
    v_star: int


class Driver:
    def __init__(self, data_path : Path, verbosity: str, enable_pruning: bool, max_num_states: int, no_decoding_table: bool):
        self._domain_file_path = (data_path / "domain.pddl").resolve()
        self._problem_file_paths = [file.resolve() for file in data_path.iterdir() if file.is_file() and file.name != "domain.pddl"]
        self._coloring_function = None
        self._logger = initialize_logger("wl")
        self._logger.setLevel(verbosity)
        self._verbosity = verbosity.upper()
        self._enable_pruning = enable_pruning
        self._max_num_states = max_num_states
        self._no_decoding_table = no_decoding_table
        add_console_handler(self._logger)


    def _generate_data(self):
        # Create GeneralizedSearchContext
        search_context_options = search.SearchContextOptions()
        search_context_options.mode = search.SearchMode.GROUNDED
        generalized_search_context = search.GeneralizedSearchContext.create(self._domain_file_path, self._problem_file_paths, search_context_options)

        # Create KnowledgeBase
        state_space_options = datasets.StateSpaceOptions()
        state_space_options.symmetry_pruning = True 
        state_space_options.max_num_states = self._max_num_states
        generalized_state_space_options = datasets.GeneralizedStateSpaceOptions()
        knowledge_base_options = datasets.KnowledgeBaseOptions()
        knowledge_base_options.state_space_options = state_space_options
        knowledge_base_options.generalized_state_space_options = generalized_state_space_options
        knowledge_base = datasets.KnowledgeBase.create(generalized_search_context, knowledge_base_options)
        num_states = knowledge_base.get_generalized_state_space().get_graph().get_num_vertices()
        self._logger.info(f"[Generate data] Total number of gfa states: {num_states}")
        self._logger.info(f"[Generate data] Peak memory usage: {int(memory_usage())} MiB.")

        ### 5. Group gfa states by canonical initial coloring.
        grouped_states = defaultdict(list)
        for class_v in knowledge_base.get_generalized_state_space().get_graph().get_vertices():
            problem_v = knowledge_base.get_generalized_state_space().get_problem_vertex(class_v)
            state = datasets.get_state(problem_v)
            problem = datasets.get_problem(problem_v)
            object_graph = datasets.create_object_graph(state, problem)
            colors = tuple(sorted([colored_vertex.get_property_0() for colored_vertex in object_graph.get_vertices()]))
            grouped_states[colors].append(StateInformation(state, problem, datasets.get_unit_goal_distance(problem_v)))
        self._logger.info(f"[Generate data] Total number of gfa groups: {len(grouped_states)}")
        self._logger.info(f"[Generate data] Peak memory usage: {int(memory_usage())} MiB.")

        return knowledge_base, list(grouped_states.values()), num_states


    def _validate_wl_correctness(self, partitioning: List[List[StateInformation]]):
        total_conflicts = [0] * 2
        value_conflicts = [0] * 2
        total_conflicts_same_instance = [0] * 2
        value_conflicts_same_instance = [0] * 2

        for partition_idx, partition in enumerate(partitioning):
            partition_filename = f"partition_{partition_idx}.1qm"
            ### Dump certificate to a file:
            with open(partition_filename, "w") as file:
                for entry_idx, state_information in enumerate(partition):
                    state = state_information.state
                    problem = state_information.problem
                    v_star = state_information.v_star
                    object_graph = datasets.create_object_graph(state, problem)
                    certificate = graphs.compute_color_refinement_certificate(object_graph)
                    if self._no_decoding_table:
                        certificate = certificate.get_hash_to_color()

                    certificate = re.sub(r"\s+", "", str(certificate)) # remove white spaces in certificate
                    file.write(f"{str(certificate)} {partition_idx} {entry_idx} {v_star}\n")
            ### Use sort command as follows to sort by first column
            # sort -k 1,1 data.txt
            ### Call the sort command using subprocess
            sorted_partition_filename = f"partition_{partition_idx}.1qm"
            try:
                subprocess.run(['sort', '-k1,1', '-o', sorted_partition_filename, partition_filename], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error during sorting: {e}")
            ### Open the file for reading
            conflict_groups = []
            with open(sorted_partition_filename, "r") as file:
                prev_quotient_matrix_string = None
                prev_instance_id = None
                prev_state_id = None
                conflict_group = []
                for line in file:
                    quotient_matrix_string, instance_id, state_id, v_star = line.split()
                    instance_id = int(instance_id)
                    state_id = int(state_id)
                    v_star = float(v_star)
                    if prev_quotient_matrix_string is not None and prev_quotient_matrix_string == quotient_matrix_string:
                        ### Collect conflicts of a group
                        if not conflict_group:
                            conflict_group.append((prev_instance_id, prev_state_id, v_star))
                        conflict_group.append((instance_id, state_id, v_star))
                    else:
                        if conflict_group:
                            ### No more conflicts for the same group
                            conflict_groups.append(conflict_group)
                            conflict_group = []
                    prev_quotient_matrix_string = quotient_matrix_string
                    prev_instance_id = instance_id
                    prev_state_id = state_id
                conflict_groups.append(conflict_group)

            isomorphic_type_function = graphs.KFWLIsomorphismTypeCompressionFunction()
            for conflict_group in conflict_groups:
                for (partition_idx_1, entry_idx_1, v_star_1), (partition_idx_2, entry_idx_2, v_star_2) in combinations(conflict_group, 2):
                    state_information_1 : StateInformation = partitioning[partition_idx_1][entry_idx_1]
                    state_1 = state_information_1.state
                    problem_1 = state_information_1.problem
                    state_information_2 : StateInformation = partitioning[partition_idx_2][entry_idx_2]
                    state_2 = state_information_2.state
                    problem_2 = state_information_2.problem

                    object_graph_1 = datasets.create_object_graph(state_1, problem_1)
                    object_graph_2 = datasets.create_object_graph(state_2, problem_2)

                    certificate_1 = graphs.compute_color_refinement_certificate(object_graph_1)
                    certificate_2 = graphs.compute_color_refinement_certificate(object_graph_2) 
                    if self._no_decoding_table:
                        certificate_1 = certificate_1.get_hash_to_color()
                        certificate_2 = certificate_2.get_hash_to_color()
                    
                    # Report 1-WL conflict
                    assert(certificate_1 == certificate_2)
                    total_conflicts[0] += 1
                    if problem_1 == problem_2:
                        total_conflicts_same_instance[0] += 1
                    if v_star_1 != v_star_2:
                        value_conflicts[0] += 1
                        if problem_1 == problem_2:
                            value_conflicts_same_instance[0] += 1
                        self._logger.debug(f"[1-WL] Value conflict!")
                    else:
                        self._logger.debug(f"[1-WL] Conflict!")
                    self._logger.debug(f" > Instance 1: {problem_1.get_filepath()}")
                    self._logger.debug(f" > Instance 2: {problem_2.get_filepath()}")
                    self._logger.debug(f" > Cost: {v_star_1}; State 1: {state_1.to_string(problem_1)}")
                    self._logger.debug(f" > Cost: {v_star_2}; State 2: {state_2.to_string(problem_2)}")
                    self._logger.debug(f"Goal 1: fluent={[str(literal) for literal in problem_1.get_fluent_goal_condition()]}, derived={[str(literal) for literal in problem_1.get_derived_goal_condition()]}, static={[str(literal) for literal in problem_1.get_static_goal_condition()]}")
                    self._logger.debug(f"Goal 2: fluent={[str(literal) for literal in problem_2.get_fluent_goal_condition()]}, derived={[str(literal) for literal in problem_2.get_derived_goal_condition()]}, static={[str(literal) for literal in problem_2.get_static_goal_condition()]}")

                    # Check and report 2-FWL conflict
                    certificate_1 = graphs.compute_2fwl_certificate(object_graph_1, isomorphic_type_function)
                    certificate_2 = graphs.compute_2fwl_certificate(object_graph_2, isomorphic_type_function)
                    if self._no_decoding_table:
                        certificate_1 = certificate_1.get_hash_to_color()
                        certificate_2 = certificate_2.get_hash_to_color()

                    if certificate_1 == certificate_2:
                        total_conflicts[1] += 1
                        if problem_1 == problem_2:
                            total_conflicts_same_instance[1] += 1
                        if v_star_1 != v_star_2:
                            value_conflicts[1] += 1
                            if problem_1 == problem_2:
                                value_conflicts_same_instance[1] += 1
                            self._logger.debug(f"[2-FWL] Value conflict!")
                        else:
                            self._logger.debug(f"[2-FWL] Conflict!")
                        self._logger.debug(f" > Instance 1: {problem_1.get_filepath()}")
                        self._logger.debug(f" > Instance 2: {problem_2.get_filepath()}")
                        self._logger.debug(f" > Cost: {v_star_1}; State 1: {state_1.to_string(problem_1)}")
                        self._logger.debug(f" > Cost: {v_star_2}; State 2: {state_2.to_string(problem_2)}")
                        self._logger.debug(f"Goal 1: fluent={[str(literal) for literal in problem_1.get_fluent_goal_condition()]}, derived={[str(literal) for literal in problem_1.get_derived_goal_condition()]}, static={[str(literal) for literal in problem_1.get_static_goal_condition()]}")
                        self._logger.debug(f"Goal 2: fluent={[str(literal) for literal in problem_2.get_fluent_goal_condition()]}, derived={[str(literal) for literal in problem_2.get_derived_goal_condition()]}, static={[str(literal) for literal in problem_2.get_static_goal_condition()]}")
        
        return total_conflicts, value_conflicts, total_conflicts_same_instance, value_conflicts_same_instance


    def run(self):
        """ Main loop for computing k-WL and Aut(S(P)) for state space S(P).
        """
        self._logger.info(f"[Configuration] [enable_pruning = {self._enable_pruning}, max_num_states = {self._max_num_states}, no_decoding_table = {self._no_decoding_table}]")
        self._logger.debug("[Configuration] Domain file: {self._domain_file_path}")
        for i, problem_file_path in enumerate(self._problem_file_paths):
            self._logger.debug(f"[Configuration] Problem {i} file: {problem_file_path}")

        self._logger.info("[Pymimir] Generating pairwise non isomorphic states.")
        knowledge_base, partitioning, num_states = self._generate_data()
        self._logger.info(f"[Pymimir] Peak memory usage: {int(memory_usage())} MiB.")

        self._logger.info("[WL] Run validation...")
        total_conflicts, value_conflicts, total_conflicts_same_instance, value_conflicts_same_instance = self._validate_wl_correctness(partitioning)

        self._logger.info("[Results] Ran to completion.")
        self._logger.info(f"[Results] Domain: {self._domain_file_path}")
        self._logger.info(f"[Results] Configuration: [enable_pruning = {self._enable_pruning}, max_num_states = {self._max_num_states}, no_decoding_table = {self._no_decoding_table}]")
        total_conflicts_score = [num_conflict / (num_states * num_states) for num_conflict in total_conflicts]
        value_conflicts_score = [num_conflict / (num_states * num_states) for num_conflict in value_conflicts]
        self._logger.info(f"[Results] Table row: [# = {len(self._problem_file_paths)}, #S = {num_states}, #S^2 = {num_states * num_states}, #C = {total_conflicts}, #C/#S^2 = [{', '.join(f'{value:.5f}' for value in total_conflicts_score)}], #V = {value_conflicts}, #V/#S^2 = [{', '.join(f'{value:.5f}' for value in value_conflicts_score)}], #C/same = {total_conflicts_same_instance}, #V/same = {value_conflicts_same_instance}]")
        self._logger.info(f"[Results] Peak memory usage: {int(memory_usage())} MiB.")
