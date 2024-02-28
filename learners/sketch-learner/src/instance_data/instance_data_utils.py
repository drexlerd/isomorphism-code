import logging
import os
import math

from dlplan.core import VocabularyInfo, InstanceInfo, DenotationsCaches, State
from dlplan.policy import Rule
from dlplan.state_space import StateSpace

from collections import defaultdict
from typing import  List, Dict, Tuple

from src.domain_data.domain_data import DomainData
from src.domain_data.domain_data_utils import compute_domain_data
from src.instance_data.instance_data import InstanceData
from src.instance_data.instance_information import InstanceInformation
from src.instance_data.tuple_graph_utils import compute_tuple_graphs
from src.instance_data.equivalence_graph import EquivalenceGraph, read_equivalence_graph
from src.iteration_data.sketch import Sketch
from src.util.command import create_experiment_workspace


def compute_instance_datas(config) -> Tuple[List[InstanceData], DomainData]:
    cwd = os.getcwd()
    vocabulary_info = None
    instance_datas = []
    for i, instance_information in enumerate(config.instance_informations):
        logging.info("Constructing InstanceData for filename %s", instance_information.filename)
        create_experiment_workspace(instance_information.workspace, False)
        # change working directory to put planner output files in correct directory
        os.chdir(instance_information.workspace)
        print(instance_information.workspace)
        # result = generate_state_space(str(config.domain_filename), str(instance_information.filename), vocabulary_info, len(instance_datas), config.max_time_per_instance)
        print(instance_information.filename)

        equivalence_graph = read_equivalence_graph(instance_information.filename)
        print(equivalence_graph)

        if vocabulary_info is None:
            # We obtain the parsed vocabulary from the first instance
            vocabulary_info = VocabularyInfo()
            for const in equivalence_graph.domain.constants:
                vocabulary_info.add_constant(const.name)
            static_predicate_names = set(pred.name for pred in equivalence_graph.domain.predicates)
            for pred in equivalence_graph.domain.predicates:
                if pred.name in static_predicate_names:
                    vocabulary_info.add_predicate(pred.name, pred.arity, True)
                else:
                    vocabulary_info.add_predicate(pred.name, pred.arity, False)

            domain_data = compute_domain_data(vocabulary_info)

        assert(vocabulary_info is not None)
        instance_info = InstanceInfo(i, vocabulary_info)
        for static_atom in equivalence_graph.problem.static_atoms:
            instance_info.add_static_atom(static_atom.predicate.name, [obj.name for obj in static_atom.objects])
        atom_to_dlplan_atom = dict()
        for atom in set(equivalence_graph.problem.encountered_atoms).difference(set(equivalence_graph.problem.static_atoms)):
            atom_to_dlplan_atom[atom] = instance_info.add_atom(atom.predicate.name, [obj.name for obj in atom.objects])

        states = dict()
        for state_id, state in equivalence_graph.states.items():
            states[state_id] = State(state_id, instance_info, [atom_to_dlplan_atom[atom] for atom in state.fluent_atoms])
        goal_states = equivalence_graph.goal_states

        forward_successors = defaultdict(set)
        for source_id, transitions in equivalence_graph.transitions.items():
            for transition in transitions:
                forward_successors[source_id].add(transition.target_index)
        state_space = StateSpace(instance_info, states, 0, forward_successors, goal_states)

        print(state_space.to_dot(1))


        if len(state_space.get_states()) > config.max_states_per_instance:
            continue
        goal_distances = state_space.compute_goal_distances()
        if goal_distances.get(state_space.get_initial_state_index(), None) is None:
            print("Unsolvable.")
            continue
        if set(state_space.get_states().keys()) == set(state_space.get_goal_state_indices()):
            print("Trivially solvable.")
            continue
        if not config.closed_Q and state_space.get_initial_state_index() in set(state_space.get_goal_state_indices()):
            print("Initial state is goal.")
            continue
        print("Num states:", len(state_space.get_states()))
        instance_data = InstanceData(len(instance_datas), domain_data, DenotationsCaches(), instance_information)
        instance_data.set_state_space(state_space, create_dump=True)
        instance_data.set_goal_distances(goal_distances)
        if config.closed_Q:
            instance_data.initial_s_idxs = [s_idx for s_idx in state_space.get_states().keys() if instance_data.is_alive(s_idx)]
        else:
            instance_data.initial_s_idxs = [state_space.get_initial_state_index(),]
        instance_datas.append(instance_data)
    # Sort the instances according to size and fix the indices afterwards
    instance_datas = sorted(instance_datas, key=lambda x : len(x.state_space.get_states()))
    for instance_idx, instance_data in enumerate(instance_datas):
        instance_data.id = instance_idx
    # change back working directory
    os.chdir(cwd)
    return instance_datas, domain_data


def compute_subproblems(config, instance_datas: List[InstanceData], sketch: Sketch, rule: Rule, r_idx: int, width: int) -> List[InstanceData]:
    features = list(sketch.dlplan_policy.get_booleans()) + list(sketch.dlplan_policy.get_numericals())
    subproblem_instance_datas = []
    for instance_data in instance_datas:
        state_space = instance_data.state_space
        covered_relevant_s_idxs = set()
        # 1. Group relevant states with same feature valuation together
        feature_valuation_to_relevant_s_idxs = defaultdict(set)
        for s_idx in sketch.compute_r_reachable_states(instance_data):
            if instance_data.is_goal(s_idx):
                # Definition of relevant states: state must be nongoal.
                continue
            if not rule.evaluate_conditions(state_space.get_states()[s_idx], instance_data.denotations_caches):
                # Definition of relevant states: state must satisfy condition of rule
                continue
            state = state_space.get_states()[s_idx]
            feature_valuation = tuple([feature.evaluate(state, instance_data.denotations_caches) for feature in features])
            feature_valuation_to_relevant_s_idxs[feature_valuation].add(s_idx)
        # 2. Group subgoal states with same feature valuation together
        feature_valuation_to_target_s_idxs = defaultdict(set)
        for s_idx, state in instance_data.state_space.get_states().items():
            feature_valuation = tuple([feature.evaluate(state, instance_data.denotations_caches) for feature in features])
            feature_valuation_to_target_s_idxs[feature_valuation].add(s_idx)
        # 3. Compute goals for each group.
        for _, relevant_s_idxs in feature_valuation_to_relevant_s_idxs.items():
            # 3.2. Compute set of goal states, i.e., all s' such that (f(s), f(s')) satisfies E.
            goal_s_idxs = set()
            for _, target_s_idxs in feature_valuation_to_target_s_idxs.items():
                if not rule.evaluate_effects(state_space.get_states()[next(iter(relevant_s_idxs))], state_space.get_states()[next(iter(target_s_idxs))], instance_data.denotations_caches):
                    continue
                goal_s_idxs.update(target_s_idxs)
            if not goal_s_idxs:
                continue

            # 4. Compute goal distances of all relevant states.
            old_goal_distances = instance_data.goal_distances
            old_goal_state_indices = instance_data.state_space.get_goal_state_indices()
            instance_data.state_space.set_goal_state_indices(goal_s_idxs)
            instance_data.goal_distances = instance_data.state_space.compute_goal_distances()
            # 4. Sort relevant states by distance and then instantiate the subproblem
            sorted_relevant_s_idxs = sorted(relevant_s_idxs, key=lambda x : -instance_data.goal_distances.get(x, math.inf))
            for initial_s_idx in sorted_relevant_s_idxs:
                if initial_s_idx in covered_relevant_s_idxs:
                    continue
                name = f"{instance_data.instance_information.name}-{initial_s_idx}"

                # 5. Compute states and initial states covered by these states.
                initial_state_distances = instance_data.state_space.compute_distances({initial_s_idx}, True, True)
                # All I-reachable states make it into the instance
                state_indices = set(initial_state_distances.keys())
                # Extend initial states by uncovered initial states
                subproblem_initial_s_idxs = {initial_s_idx,}
                covered_relevant_s_idxs.add(initial_s_idx)
                for initial_s_prime_idx in relevant_s_idxs:
                    if initial_s_prime_idx not in state_indices:
                        # State is not part of the subproblem
                        continue
                    elif initial_s_prime_idx in covered_relevant_s_idxs:
                        # Dont cover initial states multiple times
                        continue
                    subproblem_initial_s_idxs.add(initial_s_prime_idx)
                    covered_relevant_s_idxs.add(initial_s_prime_idx)

                # 6. Instantiate subproblem for initial state and subgoals.
                subproblem_state_space = StateSpace(
                    instance_data.state_space,
                    state_indices)
                subproblem_state_space.set_initial_state_index(initial_s_idx)
                # Goal states were overapproximated and must be restricted to those that are I-reachable
                subproblem_state_space.set_goal_state_indices(goal_s_idxs.intersection(state_indices))
                subproblem_goal_distances = subproblem_state_space.compute_goal_distances()
                subproblem_instance_information = InstanceInformation(
                    name,
                    instance_data.instance_information.filename,
                    instance_data.instance_information.workspace / f"rule_{r_idx}" / name)
                subproblem_instance_data = InstanceData(
                    len(subproblem_instance_datas),
                    instance_data.domain_data,
                    instance_data.denotations_caches,
                    subproblem_instance_information)
                subproblem_instance_data.set_state_space(subproblem_state_space)
                subproblem_instance_data.set_goal_distances(subproblem_goal_distances)
                subproblem_instance_data.initial_s_idxs = subproblem_initial_s_idxs
                if not subproblem_instance_data.is_alive(initial_s_idx):
                    continue
                assert all([subproblem_instance_data.is_alive(initial_s_idx) for initial_s_idx in subproblem_instance_data.initial_s_idxs])
                # 2.2.1. Recompute tuple graph for restricted state space
                compute_tuple_graphs(width, [subproblem_instance_data])
                subproblem_instance_datas.append(subproblem_instance_data)
            instance_data.state_space.set_goal_state_indices(old_goal_state_indices)
            instance_data.goal_distances = old_goal_distances
    subproblem_instance_datas = sorted(subproblem_instance_datas, key=lambda x : len(x.state_space.get_states()))
    for instance_idx, instance_data in enumerate(subproblem_instance_datas):
        instance_data.id = instance_idx
    print("Number of problems:", len(instance_datas))
    print("Number of subproblems:", len(subproblem_instance_datas))
    print("Highest number of states in problem:", max([len(instance_data.state_space.get_states()) for instance_data in instance_datas]))
    print("Highest number of states in subproblem:", max([len(instance_data.state_space.get_states()) for instance_data in subproblem_instance_datas]))
    return subproblem_instance_datas
