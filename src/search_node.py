from pymimir import State, Action
from dataclasses import dataclass


@dataclass
class SearchNode:
    parent_state: State
    creating_action: Action
