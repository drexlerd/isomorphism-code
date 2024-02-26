from dlplan.policy import PolicyBuilder

import math

from collections import defaultdict
from typing import List

from learner.src.domain_data.domain_data import DomainData
from learner.src.instance_data.instance_data import InstanceData
from learner.src.iteration_data.state_pair_equivalence import StatePairEquivalenceClasses, StatePairEquivalence, PerStateStatePairEquivalences
from learner.src.iteration_data.feature_pool import FeaturePool
from learner.src.iteration_data.feature_valuations import FeatureValuations



def make_conditions(policy_builder: PolicyBuilder,
    feature_pool: FeaturePool,
    feature_valuations: FeatureValuations):
    """ Create conditions over all features that are satisfied in source_idx """
    conditions = set()
    for b_idx, boolean in feature_pool.boolean_features.f_idx_to_feature.items():
        val = feature_valuations.b_idx_to_val[b_idx]
        if val:
            conditions.add(policy_builder.add_pos_condition(boolean.dlplan_feature))
        else:
            conditions.add(policy_builder.add_neg_condition(boolean.dlplan_feature))
    for n_idx, numerical in feature_pool.numerical_features.f_idx_to_feature.items():
        val = feature_valuations.n_idx_to_val[n_idx]
        if val > 0:
            conditions.add(policy_builder.add_gt_condition(numerical.dlplan_feature))
        else:
            conditions.add(policy_builder.add_eq_condition(numerical.dlplan_feature))
    return conditions

def make_effects(policy_builder: PolicyBuilder,
    feature_pool: FeaturePool,
    source_feature_valuations: FeatureValuations,
    target_feature_valuations: FeatureValuations):
    """ Create effects over all features that are satisfied in (source_idx,target_idx) """
    effects = set()
    for b_idx, boolean in feature_pool.boolean_features.f_idx_to_feature.items():
        source_val = source_feature_valuations.b_idx_to_val[b_idx]
        target_val = target_feature_valuations.b_idx_to_val[b_idx]
        if source_val and not target_val:
            effects.add(policy_builder.add_neg_effect(boolean.dlplan_feature))
        elif not source_val and target_val:
            effects.add(policy_builder.add_pos_effect(boolean.dlplan_feature))
        else:
            effects.add(policy_builder.add_bot_effect(boolean.dlplan_feature))
    for n_idx, numerical in feature_pool.numerical_features.f_idx_to_feature.items():
        source_val = source_feature_valuations.n_idx_to_val[n_idx]
        target_val = target_feature_valuations.n_idx_to_val[n_idx]
        if source_val > target_val:
            effects.add(policy_builder.add_dec_effect(numerical.dlplan_feature))
        elif source_val < target_val:
            effects.add(policy_builder.add_inc_effect(numerical.dlplan_feature))
        else:
            effects.add(policy_builder.add_bot_effect(numerical.dlplan_feature))
    return effects


def compute_state_pair_equivalences(domain_data: DomainData,
    instance_datas: List[InstanceData]):
    # We have to take a new policy_builder because our feature pool F uses indices 0,...,|F|
    policy_builder = domain_data.policy_builder
    rules = []
    rule_repr_to_idx = dict()
    for instance_data in instance_datas:
        per_state_state_pair_equivalences = PerStateStatePairEquivalences()
        for s_idx, tuple_graph in instance_data.per_state_tuple_graphs.s_idx_to_tuple_graph.items():
            if instance_data.is_deadend(s_idx):
                continue
            r_idx_to_distance = dict()
            r_idx_to_subgoal_states = defaultdict(set)
            subgoal_states_to_r_idx = dict()
            # add conditions
            conditions = make_conditions(policy_builder, domain_data.feature_pool, instance_data.per_state_feature_valuations.s_idx_to_feature_valuations[s_idx])
            for s_distance, s_prime_idxs in enumerate(tuple_graph.get_state_indices_by_distance()):
                for s_prime_idx in s_prime_idxs:
                    # add effects
                    effects = make_effects(policy_builder, domain_data.feature_pool, instance_data.per_state_feature_valuations.s_idx_to_feature_valuations[s_idx], instance_data.per_state_feature_valuations.s_idx_to_feature_valuations[s_prime_idx])
                    # add rule
                    rule = policy_builder.add_rule(conditions, effects)
                    rule_repr = repr(rule)
                    if rule_repr in rule_repr_to_idx:
                        r_idx = rule_repr_to_idx[rule_repr]
                    else:
                        r_idx = len(rules)
                        rule_repr_to_idx[rule_repr] = r_idx
                        rules.append(rule)
                    r_idx_to_distance[r_idx] = min(r_idx_to_distance.get(r_idx, math.inf), s_distance)
                    r_idx_to_subgoal_states[r_idx].add(s_prime_idx)
                    subgoal_states_to_r_idx[s_prime_idx] = r_idx
            per_state_state_pair_equivalences.s_idx_to_state_pair_equivalence[s_idx] = StatePairEquivalence(r_idx_to_subgoal_states, r_idx_to_distance, subgoal_states_to_r_idx)
        instance_data.set_per_state_state_pair_equivalences(per_state_state_pair_equivalences)
    domain_data.domain_state_pair_equivalence = StatePairEquivalenceClasses(rules)
