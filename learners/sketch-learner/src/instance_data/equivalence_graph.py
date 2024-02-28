import json

from pathlib import Path
from typing import Dict, List

from dataclasses import dataclass, asdict, is_dataclass


def to_serializable(obj):
    """Convert a custom object to a serializable dictionary."""
    if is_dataclass(obj):
        return {k: to_serializable(v) for k, v in asdict(obj).items()}
    elif isinstance(obj, list):
        return [to_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    else:
        return obj


@dataclass
class Object:
    name: str

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return to_serializable({"name": self.name})


@dataclass
class Constant:
    name: str

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return to_serializable({"name": self.name})


@dataclass
class Predicate:
    name: str
    arity: int

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return to_serializable({"name": self.name, "arity": self.arity})


@dataclass
class Atom:
    predicate: Predicate
    objects: List[Object]

    @classmethod
    def from_dict(cls, data):
        predicate = Predicate.from_dict(data["predicate"])
        objects = [Object.from_dict(obj) for obj in data["objects"]]
        return cls(predicate, objects)

    def to_dict(self):
        return to_serializable({"predicate": self.predicate, "objects": self.objects})


@dataclass
class Literal:
    atom: Atom
    is_negated: bool

    @classmethod
    def from_dict(cls, data):
        atom = Atom.from_dict(data["atom"])
        is_negated = bool(data["is_negated"])
        return cls(atom, is_negated)

    def to_dict(self):
        return to_serializable({"atom": self.atom, "is_negated": self.is_negated})


@dataclass
class Domain:
    constants: List[Constant]
    predicates: List[Predicate]
    static_predicates: List[Predicate]

    @classmethod
    def from_dict(cls, data):
        constants = [Constant.from_dict(obj) for obj in data["constants"]]
        predicates = [Predicate.from_dict(obj) for obj in data["predicates"]]
        static_predicates = [Predicate.from_dict(obj) for obj in data["static_predicates"]]
        return cls(constants, predicates, static_predicates)

    def to_dict(self):
        return to_serializable({"constants": self.constants, "predicates": self.predicates, "static_predicates": self.static_predicates})


@dataclass
class Problem:
    encountered_atoms: List[Atom]
    static_atoms: List[Atom]
    goal_literals: List[Literal]

    @classmethod
    def from_dict(cls, data):
        encountered_atoms = [Atom.from_dict(obj) for obj in data["encountered_atoms"]]
        static_atoms = [Atom.from_dict(obj) for obj in data["static_atoms"]]
        goal_literals = [Literal.from_dict(obj) for obj in data["goal_literals"]]
        return cls(encountered_atoms, static_atoms, goal_literals)

    def to_dict(self):
        return to_serializable({"encountered_atoms": self.encountered_atoms, "static_atoms": self.static_atoms, "goal_literals": self.goal_literals})


@dataclass
class State:
    index: int
    static_atoms: List[Atom]
    fluent_atoms: List[Atom]
    equivalence_class_index: int

    @classmethod
    def from_dict(cls, data):
        index = int(data["index"])
        static_atoms = [Atom.from_dict(obj) for obj in data["static_atoms"]]
        fluent_atoms = [Atom.from_dict(obj) for obj in data["fluent_atoms"]]
        equivalence_class_index = data["index"]
        return cls(index, static_atoms, fluent_atoms, equivalence_class_index)

    def to_dict(self):
        return to_serializable({"index": self.index, "static_atoms": self.static_atoms, "fluent_atoms": self.fluent_atoms, "equivalence_class_index": self.equivalence_class_index})


@dataclass
class Action:
    name: str
    arguments: List[Object]

    @classmethod
    def from_dict(cls, data):
        name = data["name"]
        arguments = [Object.from_dict(obj) for obj in data["arguments"]]
        return cls(name, arguments)

    def to_dict(self):
        return to_serializable({"name": self.name, "arguments": self.arguments})


@dataclass
class Transition:
    source_index: int
    target_index: int
    action: Action

    @classmethod
    def from_dict(cls, data):
        source_index = int(data["source_index"])
        target_index = int(data["target_index"])
        action = Action.from_dict(data["action"])
        return cls(source_index, target_index, action)

    def to_dict(self):
        return to_serializable({"source_index": self.source_index, "target_index": self.target_index, "action": self.action})


class EquivalenceGraph:
    def __init__(self, domain: Domain, problem: Problem, states: Dict[int, State], transitions: Dict[int, List[Transition]]):
        self.domain = domain
        self.problem = problem
        self.states = states
        self.transitions = transitions

    @classmethod
    def from_dict(cls, data):
        domain = Domain.from_dict(data["domain"])
        problem = Problem.from_dict(data["problem"])
        states = {int(k): State.from_dict(v) for k, v in data["states"].items()}
        transitions = {int(k): [Transition.from_dict(t) for t in v] for k, v in data["transitions"].items()}
        return cls(domain, problem, states, transitions)

    def to_dict(self):
        return to_serializable({
            "domain": self.domain,
            "problem": self.problem,
            "states": self.states,
            "transitions": self.transitions
        })


def write_equivalence_graph(equivalence_graph: EquivalenceGraph, file_path: Path) -> None:
    """Write the state space to a file in JSON format."""
    with file_path.open('w') as f:
        json_dict = equivalence_graph.to_dict()
        f.write(json.dumps(json_dict, indent=4))


def read_equivalence_graph(file_path: Path) -> EquivalenceGraph:
    """Read the state space from a file in JSON format and update the instance."""
    with file_path.open() as f:
        data = json.load(f)
        return EquivalenceGraph.from_dict(data)
