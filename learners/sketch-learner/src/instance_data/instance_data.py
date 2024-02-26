from dlplan.core import DenotationsCaches
from dlplan.novelty import TupleGraph
from dlplan.state_space import StateSpace

from dataclasses import dataclass
from typing import List, Dict

from learner.src.domain_data.domain_data import DomainData
from learner.src.instance_data.instance_information import InstanceInformation
from learner.src.instance_data.tuple_graph import PerStateTupleGraphs
from learner.src.iteration_data.feature_valuations import PerStateFeatureValuations
from learner.src.iteration_data.state_pair_equivalence import PerStateStatePairEquivalences
from learner.src.iteration_data.tuple_graph_equivalence import PerStateTupleGraphEquivalences
from learner.src.util.command import write_file
from learner.src.util.command import create_experiment_workspace


@dataclass
class InstanceData:
    id: int
    domain_data: DomainData
    denotations_caches: DenotationsCaches  # We use a cache for each instance such that we can ignore the instance index.
    instance_information: InstanceInformation
    state_space: StateSpace = None
    goal_distances: Dict[int, int] = None
    per_state_tuple_graphs: PerStateTupleGraphs = None

    initial_s_idxs: List[int] = None  # in cases we need multiple initial states
    per_state_feature_valuations: PerStateFeatureValuations = None
    per_state_state_pair_equivalences: PerStateStatePairEquivalences = None
    per_state_tuple_graph_equivalences: PerStateTupleGraphEquivalences = None

    def set_state_space(self, state_space: StateSpace, create_dump: bool = False):
        self.state_space = state_space
        if create_dump:
            create_experiment_workspace(self.instance_information.workspace, False)
            write_file(self.instance_information.workspace / f"{self.instance_information.name}.dot", state_space.to_dot(1))

    def set_per_state_tuple_graphs(self, per_state_tuple_graphs: PerStateTupleGraphs, create_dump: bool = False):
        self.per_state_tuple_graphs = per_state_tuple_graphs
        if create_dump:
            for tuple_graph in per_state_tuple_graphs.s_idx_to_tuple_graph.values():
                create_experiment_workspace(self.instance_information.workspace / "tuple_graphs", False)
                write_file(self.instance_information.workspace / "tuple_graphs" / f"{tuple_graph.get_root_state_index()}.dot", tuple_graph.to_dot(1))

    def set_per_state_feature_valuations(self, per_state_feature_valuations: PerStateFeatureValuations, create_dump=False):
        self.per_state_feature_valuations = per_state_feature_valuations
        if create_dump:
            create_experiment_workspace(self.instance_information.workspace, False)
            write_file(self.instance_information.workspace / self.instance_information.name / "per_state_feature_valuations.txt", str(self.per_state_feature_valuations))

    def set_per_state_state_pair_equivalences(self, per_state_state_pair_equivalences: PerStateStatePairEquivalences):
        self.per_state_state_pair_equivalences = per_state_state_pair_equivalences

    def set_per_state_tuple_graph_equivalences(self, per_state_tuple_graph_equivalence: PerStateTupleGraphEquivalences):
        self.per_state_tuple_graph_equivalences = per_state_tuple_graph_equivalence

    def set_goal_distances(self, goal_distances: Dict[int, int]):
        self.goal_distances =  goal_distances

    def is_deadend(self, s_idx: int):
        return self.goal_distances.get(s_idx, None) is None

    def is_goal(self, s_idx: int):
        return s_idx in self.state_space.get_goal_state_indices()

    def is_alive(self, s_idx: int):
        return not self.is_goal(s_idx) and not self.is_deadend(s_idx)
