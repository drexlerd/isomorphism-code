from dataclasses import dataclass


@dataclass
class SearchNode:
    state_id: int
    parent_state_id: int
    creating_action_name: str
