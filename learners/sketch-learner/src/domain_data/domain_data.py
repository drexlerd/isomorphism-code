from dataclasses import dataclass

from dlplan.core import VocabularyInfo, SyntacticElementFactory
from dlplan.generator import FeatureGenerator
from dlplan.policy import PolicyFactory

from src.iteration_data.state_pair_equivalence import PerStateStatePairEquivalences
from src.iteration_data.feature_pool import FeaturePool


@dataclass
class DomainData:
    """ Store data related to a domain. """
    vocabulary_info: VocabularyInfo
    policy_builder: PolicyFactory
    syntactic_element_factory: SyntacticElementFactory
    domain_feature_data: FeaturePool = None
    domain_state_pair_equivalence: PerStateStatePairEquivalences = None
