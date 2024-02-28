import logging

from dlplan.core import VocabularyInfo, SyntacticElementFactory
from dlplan.policy import PolicyFactory

from src.domain_data.domain_data import DomainData


def compute_domain_data(vocabulary_info: VocabularyInfo) -> DomainData:
    syntactic_element_factory = SyntacticElementFactory(vocabulary_info)
    policy_builder = PolicyFactory(syntactic_element_factory)
    return DomainData(vocabulary_info, policy_builder, syntactic_element_factory)