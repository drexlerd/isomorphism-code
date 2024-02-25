import json

from pathlib import Path
from typing import Dict, List

from dataclasses import asdict, is_dataclass, dataclass


def dataclass_to_dict(obj):
    """Convert a dataclass object to a dictionary, including nested dataclasses."""
    if is_dataclass(obj):
        return {key: dataclass_to_dict(value) for key, value in asdict(obj).items()}
    elif isinstance(obj, list):
        return [dataclass_to_dict(item) for item in obj]
    elif isinstance(obj, set):
        return [dataclass_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {dataclass_to_dict(key): dataclass_to_dict(value) for key, value in obj.items()}
    return obj


def dict_to_dataclass(cls, d):
    """Convert a dictionary back to a dataclass instance, including nested dataclasses."""
    try:
        field_types = {f.name: f.type for f in cls.__dataclass_fields__}
        return cls(**{f: dict_to_dataclass(field_types[f], d[f]) for f in d})
    except AttributeError:
        if isinstance(d, list):
            return [dict_to_dataclass(field_types.get(i), item) for i, item in enumerate(d)]
        return d


@dataclass
class Object:
    name: str


@dataclass
class Constant:
    name: str


@dataclass
class Predicate:
    name: str
    arity: int


@dataclass
class Atom:
    predicate: Predicate
    objects: List[Object]


@dataclass
class Literal:
    atom: Atom
    is_negated: bool


@dataclass
class Domain:
    constants: List[Constant]
    predicates: List[Predicate]
    static_predicates: List[Predicate]


@dataclass
class Problem:
    encountered_atoms: List[Atom]
    goal_literals: List[Literal]


@dataclass
class State:
    index: int
    static_atoms: List[Atom]
    fluent_atoms: List[Atom]
    equivalence_class_index: int


@dataclass
class Action:
    name: str
    arguments: List[Object]


@dataclass
class Transition:
    source_index: int
    target_index: int
    action: Action


class EquivalenceGraph:
    def __init__(self, domain: Domain, problem: Problem, states: Dict[int, State], transitions: Dict[int, List[Transition]]):
        self.domain = domain
        self.problem = problem
        self.states = states
        self.transitions = transitions

    def write(self, file_path: Path):
        """Write the state space to a file in JSON format."""
        with file_path.open('w') as f:
            json.dump({
                'domain': dataclass_to_dict(self.domain),
                'problem': dataclass_to_dict(self.problem),
                'states': dataclass_to_dict(self.states),
                'transitions': dataclass_to_dict(self.transitions)}, f, indent=4)

    def read(self, file_path: Path):
        """Read the state space from a file in JSON format and update the instance."""
        with file_path.open() as f:
            data = json.load(f)
            self.domain = dict_to_dataclass(Domain, data["domain"])
            self.problem = dict_to_dataclass(Problem, data["problem"])
            self.states = {int(k): dict_to_dataclass(State, v) for k, v in data['states'].items()}
            self.transitions = {int(k): list(v) for k, v in data['transitions'].items()}
