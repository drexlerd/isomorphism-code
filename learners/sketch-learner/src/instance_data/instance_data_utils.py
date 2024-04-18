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
        print(instance_information.filename)

        equivalence_graph = read_equivalence_graph(instance_information.filename)

        if vocabulary_info is None:
            # We obtain the parsed vocabulary from the first instance
            vocabulary_info = VocabularyInfo()
            for const in equivalence_graph.domain.constants:
                vocabulary_info.add_constant(const.name)
            static_predicate_names = set(pred.name for pred in equivalence_graph.domain.static_predicates)
            for pred in equivalence_graph.domain.predicates:
                if pred.name in static_predicate_names:
                    vocabulary_info.add_predicate(pred.name, pred.arity, True)
                else:
                    vocabulary_info.add_predicate(pred.name, pred.arity, False)
                    vocabulary_info.add_predicate(pred.name + "_g", pred.arity, False)

            domain_data = compute_domain_data(vocabulary_info)

        assert(vocabulary_info is not None)
        instance_info = InstanceInfo(i, vocabulary_info)
        for static_atom in equivalence_graph.problem.static_atoms:
            instance_info.add_static_atom(static_atom.predicate.name, [obj.name for obj in static_atom.objects])
        atom_to_dlplan_atom = dict()
        for atom in set(equivalence_graph.problem.encountered_atoms).difference(set(equivalence_graph.problem.static_atoms)):
            atom_to_dlplan_atom[atom] = instance_info.add_atom(atom.predicate.name, [obj.name for obj in atom.objects])
        for literal in equivalence_graph.problem.goal_literals:
            assert not literal.is_negated
            instance_info.add_static_atom(literal.atom.predicate.name + "_g", [obj.name for obj in literal.atom.objects])

        states = dict()
        for state_id, state in equivalence_graph.states.items():
            states[state_id] = State(state_id, instance_info, [atom_to_dlplan_atom[atom] for atom in state.fluent_atoms])
        goal_states = equivalence_graph.goal_states

        forward_successors = defaultdict(set)
        for source_id, transitions in equivalence_graph.transitions.items():
            for transition in transitions:
                forward_successors[source_id].add(transition.target_index)
        state_space = StateSpace(instance_info, states, 0, forward_successors, goal_states)

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
