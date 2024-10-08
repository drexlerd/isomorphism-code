from collections import defaultdict
from pathlib import Path
from pymimir import PDDLParser, IApplicableActionGenerator, StateRepository, Problem, State, StateSpacesOptions, StateSpace, FaithfulAbstractState, FaithfulAbstractionsOptions, FaithfulAbstraction, GlobalFaithfulAbstractState, GlobalFaithfulAbstraction, Certificate, SparseNautyGraph, StaticVertexColoredDigraph, ProblemColorFunction, create_object_graph
from typing import List, Tuple, Dict, Any, MutableSet
from itertools import combinations
from dataclasses import dataclass
import subprocess

from .performance import memory_usage
from .logger import initialize_logger, add_console_handler
from .pykwl_utils import to_uvc_graph

import pykwl as kwl


@dataclass
class InstanceData:
    id: int
    parser: PDDLParser
    applicable_action_generator: IApplicableActionGenerator
    state_repository: StateRepository
    problem: Problem
    problem_file_path: str
    goal_distances: Dict[State, int]
    class_representatives: Dict[Any, State]
    class_representatives_by_state_id: Dict[int, State]
    num_total_states: int

@dataclass
class StateInformation:
    gfa_state: GlobalFaithfulAbstractState
    v_star: int

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
        self._mark_true_goal_literals = mark_true_goal_atoms
        add_console_handler(self._logger)


    def _generate_data(self) -> MutableSet[GlobalFaithfulAbstractState]:
        ### 1. Create state spaces to obtain the total number of states.
        state_spaces_options = StateSpacesOptions()
        state_spaces_options.state_space_options.use_unit_cost_one = True
        state_spaces_options.state_space_options.remove_if_unsolvable = True
        state_spaces_options.state_space_options.max_num_states = self._max_num_states
        state_spaces_options.sort_ascending_by_num_states = True
        state_spaces = StateSpace.create(
            str(self._domain_file_path),
            [str(problem_file_path) for problem_file_path in self._problem_file_paths],
            state_spaces_options)
        num_states = sum(state_space.get_num_states() for state_space in state_spaces)
        self._logger.info(f"[Generate data] Total number of states: {num_states}")
        self._logger.info(f"[Generate data] Peak memory usage: {int(memory_usage())} MiB.")

        ### 2. Fetch memory from state spaces to create gfas using the same factories, aag, and ssg.
        memories = []
        for state_space in state_spaces:
            memories.append((state_space.get_problem(), state_space.get_pddl_factories(), state_space.get_aag(), state_space.get_ssg()))

        ### 3. Perform pairwise isomorphism reduction across instances.
        faithful_abstractions_options = FaithfulAbstractionsOptions()
        faithful_abstractions_options.fa_options.mark_true_goal_literals = self._mark_true_goal_literals
        faithful_abstractions_options.fa_options.use_unit_cost_one = True
        faithful_abstractions_options.fa_options.remove_if_unsolvable = True
        faithful_abstractions_options.fa_options.max_num_concrete_states = self._max_num_states
        faithful_abstractions_options.fa_options.max_num_abstract_states = self._max_num_states
        faithful_abstractions_options.sort_ascending_by_num_states = True
        gfas = GlobalFaithfulAbstraction.create(
            memories,
            faithful_abstractions_options)

        ### 4. Create combined data set where each state is non-isomorphic to all other states.
        gfa_states: MutableSet[GlobalFaithfulAbstractState] = set()
        for gfa in gfas:
            gfa_states.update(set(gfa.get_states()))
        num_gfa_states = len(gfa_states)
        self._logger.info(f"[Generate data] Total number of gfa states: {num_gfa_states}")
        self._logger.info(f"[Generate data] Peak memory usage: {int(memory_usage())} MiB.")

        ### 5. Group gfa states by canonical initial coloring.
        # Assumption: if two object graphs have same canonical initial coloring
        # then they also have same number of vertices and edges.
        grouped_gfa_states: Dict[Tuple[int], StateInformation] = defaultdict(list)
        ### Fetch underlying fas to access the representative abstract state.
        fas = gfas[0].get_abstractions()
        for gfa_state in gfa_states:
            fa_index = gfa_state.get_faithful_abstraction_index()
            fa = fas[fa_index]
            fa_state = fa.get_states()[gfa_state.get_faithful_abstract_state_index()]
            v_star = int(fa.get_goal_distances()[fa_state.get_index()])
            isomorphism_certificate = fa_state.get_certificate()
            grouped_gfa_states[tuple(isomorphism_certificate.get_canonical_initial_coloring())].append(StateInformation(gfa_state, v_star))
        self._logger.info(f"[Generate data] Total number of gfa groups: {len(grouped_gfa_states)}")
        self._logger.info(f"[Generate data] Peak memory usage: {int(memory_usage())} MiB.")

        ### Important: return gfas since they own the memory to all data.
        return gfas, grouped_gfa_states, num_states, num_gfa_states

    def _validate_wl_correctness(self, gfas: List[GlobalFaithfulAbstraction], grouped_gfa_states: Dict[Tuple[int], StateInformation]):
        total_conflicts = [0] * 2
        value_conflicts = [0] * 2
        total_conflicts_same_instance = [0] * 2
        value_conflicts_same_instance = [0] * 2

        wl = kwl.CanonicalColorRefinement(False)

        ### Fetch fas to access data underlying of gfa_states
        fas = gfas[0].get_abstractions()

        color_functions: List[ProblemColorFunction] = []
        for fa in fas:
            color_functions.append(ProblemColorFunction(fa.get_problem()))

        for partition_id, gfa_states_group in enumerate(grouped_gfa_states.values()):

            partition_filename = f"partition_{partition_id}.1qm"

            ### Dump quotient matrices to a file with format:
            # repr(quotient_matrix) instance_id state_id
            with open(partition_filename, "w") as file:
                for state_information in gfa_states_group:
                    gfa_state: GlobalFaithfulAbstractState = state_information.gfa_state
                    v_star: int = state_information.v_star
                    # fa_index can also be seen as gfa_index
                    fa_index = gfa_state.get_faithful_abstraction_index()
                    fa_state_index = gfa_state.get_faithful_abstract_state_index()
                    fa = fas[fa_index]
                    problem = fa.get_problem()
                    factories = fa.get_pddl_factories()
                    fa_state = fa.get_states()[fa_state_index]
                    representative_state = fa_state.get_representative_state()
                    color_function = color_functions[fa_index]
                    object_graph = create_object_graph(color_function, factories, problem, representative_state, self._mark_true_goal_literals)

                    ### How to print the representative concrete state
                    # print(representative_state.to_string(problem, factories))

                    ### How to print object graph to dot
                    # print(object_graph)

                    ### Unfortunately, the WL code is not integrated into pymimir.
                    # Hence, we have to translate the graph.
                    # @Blai, interested in integrating coloring related code into pymimir?
                    wl_graph = to_uvc_graph(object_graph)

                    wl.calculate(wl_graph, True)

                    quotient_matrix = wl.get_quotient_matrix_string()

                    file.write(f"{quotient_matrix} {fa_index} {gfa_state.get_index()} {v_star}\n")

            ### Use sort command as follows to sort by first column
            # sort -k 1,1 data.txt

            ### Call the sort command using subprocess
            sorted_partition_filename = f"partition_{partition_id}.1qm"
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
                prev_v_star = None
                conflict_group = []
                for line in file:
                    quotient_matrix_string, instance_id, state_id, v_star = line.split()
                    instance_id = int(instance_id)
                    state_id = int(state_id)
                    v_star = int(v_star)

                    if prev_quotient_matrix_string is not None and prev_quotient_matrix_string == quotient_matrix_string:
                        ### Collect conflicts of a group
                        if not conflict_group:
                            conflict_group.append((prev_instance_id, prev_state_id, prev_v_star))
                        conflict_group.append((instance_id, state_id, v_star))
                    else:
                        if conflict_group:
                            ### No more conflicts for the same group
                            conflict_groups.append(conflict_group)
                            conflict_group = []

                    prev_quotient_matrix_string = quotient_matrix_string
                    prev_instance_id = instance_id
                    prev_state_id = state_id
                    prev_v_star = v_star

            for conflict_group in conflict_groups:
                for (fa_index_1, fa_state_index_1, v_star_1), (fa_index_2, fa_state_index_2, v_star_2) in combinations(conflict_group, 2):
                    ### Use canonical color refinement as approximation and correct false positives
                    wl1 = kwl.WeisfeilerLeman(1, self._ignore_counting)

                    fa_1: FaithfulAbstraction = fas[fa_index_1]
                    problem_1 = fa_1.get_problem()
                    factories_1 = fa_1.get_pddl_factories()
                    problem_filepath_1 = fa_1.get_problem().get_filepath()
                    fa_state_1: FaithfulAbstractState = fa_1.get_states()[fa_state_index_1]
                    representative_state_1 = fa_state_1.get_representative_state()
                    color_function_1 = color_functions[fa_index_1]
                    object_graph_1 = create_object_graph(color_function_1, factories_1, problem_1, representative_state_1, self._mark_true_goal_literals)

                    fa_2: FaithfulAbstraction = fas[fa_index_2]
                    problem_2 = fa_2.get_problem()
                    factories_2 = fa_2.get_pddl_factories()
                    problem_filepath_2 = fa_1.get_problem().get_filepath()
                    fa_state_2: FaithfulAbstractState = fa_2.get_states()[fa_state_index_2]
                    representative_state_2 = fa_state_2.get_representative_state()
                    color_function_2 = color_functions[fa_index_2]
                    object_graph_2 = create_object_graph(color_function_2, factories_2, problem_2, representative_state_2, self._mark_true_goal_literals)


                    wl_graph_1 = to_uvc_graph(object_graph_1)
                    wl_graph_2 = to_uvc_graph(object_graph_2)

                    coloring_1 = wl1.compute_coloring(wl_graph_1)
                    coloring_2 = wl1.compute_coloring(wl_graph_2)

                    if coloring_1 != coloring_2:
                        continue

                    # Report 1-WL conflict
                    total_conflicts[0] += 1
                    if fa_index_1 == fa_index_2:
                        total_conflicts_same_instance[0] += 1
                    if v_star_1 != v_star_2:
                        value_conflicts[0] += 1
                        if fa_index_1 == fa_index_2:
                            value_conflicts_same_instance[0] += 1
                        self._logger.info(f"[1-WL] Value conflict!")
                    else:
                        self._logger.info(f"[1-WL] Conflict!")

                    self._logger.info(f" > Instance 1: {problem_filepath_1}")
                    self._logger.info(f" > Instance 2: {problem_filepath_2}")
                    self._logger.info(f" > Cost: {v_star_1}; State 1: {representative_state_1.to_string(problem_1, factories_1)}")
                    self._logger.info(f" > Cost: {v_star_2}; State 2: {representative_state_2.to_string(problem_2, factories_2)}")
                    self._logger.info(f"Goal 1: fluent={[str(literal) for literal in problem_1.get_fluent_goal_condition()]}, derived={[str(literal) for literal in problem_1.get_derived_goal_condition()]}, static={[str(literal) for literal in problem_1.get_static_goal_condition()]}")
                    self._logger.info(f"Goal 2: fluent={[str(literal) for literal in problem_2.get_fluent_goal_condition()]}, derived={[str(literal) for literal in problem_2.get_derived_goal_condition()]}, static={[str(literal) for literal in problem_2.get_static_goal_condition()]}")

                    # Check 2-FWL conflict
                    fwl2 = kwl.WeisfeilerLeman(2, self._ignore_counting)

                    fwl2_coloring_1 = fwl2.compute_coloring(wl_graph_1)
                    fwl2_coloring_2 = fwl2.compute_coloring(wl_graph_2)

                    if fwl2_coloring_1 == fwl2_coloring_2:
                        if fa_index_1 == fa_index_2:
                            total_conflicts_same_instance[1] += 1
                        if v_star_1 != v_star_2:
                            value_conflicts[1] += 1
                            if fa_index_1 == fa_index_2:
                                value_conflicts_same_instance[1] += 1
                            self._logger.info(f"[2-FWL] Value conflict!")
                        else:
                            self._logger.info(f"[2-FWL] Conflict!")

                        self._logger.info(f" > Instance 1: {problem_filepath_1}")
                        self._logger.info(f" > Instance 2: {problem_filepath_2}")
                        self._logger.info(f" > Cost: {v_star_1}; State 1: {representative_state_1.to_string(problem_1, factories_1)}")
                        self._logger.info(f" > Cost: {v_star_2}; State 2: {representative_state_2.to_string(problem_2, factories_2)}")
                        self._logger.info(f"Goal 1: fluent={[str(literal) for literal in problem_1.get_fluent_goal_condition()]}, derived={[str(literal) for literal in problem_1.get_derived_goal_condition()]}, static={[str(literal) for literal in problem_1.get_static_goal_condition()]}")
                        self._logger.info(f"Goal 2: fluent={[str(literal) for literal in problem_2.get_fluent_goal_condition()]}, derived={[str(literal) for literal in problem_2.get_derived_goal_condition()]}, static={[str(literal) for literal in problem_2.get_static_goal_condition()]}")


        return total_conflicts, value_conflicts, total_conflicts_same_instance, value_conflicts_same_instance


    def run(self):
        """ Main loop for computing k-WL and Aut(S(P)) for state space S(P).
        """
        self._logger.info(f"[Configuration] [enable_pruning = {self._enable_pruning}, max_num_states = {self._max_num_states}, ignore_counting = {self._ignore_counting}, mark_true_goal_atoms = {self._mark_true_goal_literals}]")
        self._logger.info("[Configuration] Domain file: {self._domain_file_path}")
        for i, problem_file_path in enumerate(self._problem_file_paths):
            self._logger.info(f"[Configuration] Problem {i} file: {problem_file_path}")

        self._logger.info("[Pymimir] Generating pairwise non isomorphic states.")
        gfas, grouped_gfa_states, num_states, num_gfa_states = self._generate_data()
        self._logger.info(f"[Pymimir] Peak memory usage: {int(memory_usage())} MiB.")
        if not gfas:
            self._logger.info(f"[Pymimir] Got empty set of gfas. Aborting.")
            return

        # Dominik (13-07-2024): Commented out the code to see memory consumption of just the data generation
        self._logger.info("[WL] Run validation...")
        total_conflicts, value_conflicts, total_conflicts_same_instance, value_conflicts_same_instance = self._validate_wl_correctness(gfas, grouped_gfa_states)

        self._logger.info("[Results] Ran to completion.")
        self._logger.info(f"[Results] Domain: {self._domain_file_path}")
        self._logger.info(f"[Results] Configuration: [enable_pruning = {self._enable_pruning}, max_num_states = {self._max_num_states}, ignore_counting = {self._ignore_counting}, mark_true_goal_atoms = {self._mark_true_goal_literals}]")
        self._logger.info(f"[Results] Table row: [# = {len(self._problem_file_paths)}, #P = {num_gfa_states}, #S = {num_states}, #C = {total_conflicts}, #V = {value_conflicts}, #C/same = {total_conflicts_same_instance}, #V/same = {value_conflicts_same_instance}]")
        self._logger.info(f"[Results] Peak memory usage: {int(memory_usage())} MiB.")
