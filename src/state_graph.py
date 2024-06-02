from pymimir import PDDLFactories, Problem, State

from graphviz import Graph as DotGraph
from typing import List, Union, Tuple

from .color_function import ColorFunction


class Vertex:
    def __init__(self):
        self._labels : List[Union[str, Tuple[str, int]]] = []

    def get_canonical_labelling(self, color_function: ColorFunction) -> Tuple[Tuple[int], Tuple[int], Tuple[int]]:
        """
        """
        return color_function.get_color_from_aggregate_label(tuple(sorted(color_function.get_color_from_domain_label(label) for label in self._labels)))


class StateGraph:
    """
    In this version, we give all vertices the same color
    and encode type information using loop edges
    """
    def __init__(self, pddl_factories: PDDLFactories, problem: Problem, state : State, coloring_function: ColorFunction, mark_true_goal_atoms : bool = False):
        self._state = state
        self._coloring_function = coloring_function
        self._mark_true_goal_atoms = mark_true_goal_atoms

        ## 1. Initialize sufficiently many empty vertices and adjacency lists
        self._num_vertices = 0
        # One vertex for each object
        self._num_vertices += len(problem.get_objects())
        # N helper nodes for each atom of arity N > 0, 1 for each atom of arity 0
        for atom in pddl_factories.get_static_ground_atoms_from_ids(state.get_static_ground_atom_ids(problem)) \
            + pddl_factories.get_fluent_ground_atoms_from_ids(state.get_fluent_ground_atom_ids(problem)) \
            + pddl_factories.get_derived_ground_atoms_from_ids(state.get_derived_ground_atom_ids(problem)):
            self._num_vertices += len(atom.get_objects())
            if atom.get_arity() == 0:
                self._num_vertices += 1
        # N helper nodes for each goal atom of arity N
        for literal in problem.get_static_goal_condition() + problem.get_fluent_goal_condition() + problem.get_derived_goal_condition():
            self._num_vertices += len(literal.get_atom().get_objects())
            if literal.get_atom().get_arity() == 0:
                self._num_vertices += 1
        self._vertices = [Vertex() for _ in range(self._num_vertices)]
        self._outgoing_vertices = [[] for _ in range(self._num_vertices)]
        self._ingoing_vertices = [[] for _ in range(self._num_vertices)]

        ## 2. We need to be able to access vertices by object
        object_name_to_vertex_index = dict()
        for i, obj in enumerate(problem.get_objects()):
            object_name_to_vertex_index[obj.get_name()] = i

        ## 3. Add vertex labels and edges
        i = 0
        for obj in problem.get_objects():
            # Mimir v2 translates types into predicates
            i += 1
        for atom in pddl_factories.get_static_ground_atoms_from_ids(state.get_static_ground_atom_ids(problem)) \
            + pddl_factories.get_fluent_ground_atoms_from_ids(state.get_fluent_ground_atom_ids(problem)) \
            + pddl_factories.get_derived_ground_atoms_from_ids(state.get_derived_ground_atom_ids(problem)):
            predicate_name = atom.get_predicate().get_name()
            prev_helper_id = None
            for pos, obj in enumerate(atom.get_objects()):
                object_id = object_name_to_vertex_index[obj.get_name()]
                helper_id = i
                self._vertices[helper_id]._labels.append((predicate_name, pos))
                self._outgoing_vertices[object_id].append(helper_id)
                self._ingoing_vertices[helper_id].append(object_id)
                if prev_helper_id is not None:
                    self._outgoing_vertices[prev_helper_id].append(helper_id)
                    self._ingoing_vertices[helper_id].append(prev_helper_id)
                prev_helper_id = helper_id
                i += 1
            if atom.get_arity() == 0:
                self._vertices[i]._labels.append((predicate_name, -1))
                i += 1
        for literal in problem.get_static_goal_condition() + problem.get_fluent_goal_condition() + problem.get_derived_goal_condition():
            atom = literal.get_atom()
            predicate = atom.get_predicate()
            predicate_name = predicate.get_name()
            prev_helper_id = None
            for pos, obj in enumerate(atom.get_objects()):
                object_id = object_name_to_vertex_index[obj.get_name()]
                helper_id = i
                self._vertices[helper_id]._labels.append((predicate_name + "_g", pos))
                self._outgoing_vertices[object_id].append(helper_id)
                self._ingoing_vertices[helper_id].append(object_id)
                if prev_helper_id is not None:
                    self._outgoing_vertices[prev_helper_id].append(helper_id)
                    self._ingoing_vertices[helper_id].append(prev_helper_id)
                prev_helper_id = helper_id
                i += 1
            if atom.get_arity() == 0:
                self._vertices[i]._labels.append((predicate_name + "_g", -1))
                i += 1

    def compute_initial_coloring(self, color_function: ColorFunction) -> Tuple[int]:
        """ Return a canonical initial coloring of the graph.
        """
        return tuple(vertex.get_canonical_labelling(color_function) for vertex in self._vertices)

    def to_dot(self, output_file_path="output.gc"):
        dot = DotGraph(comment='UndirectedVertexColoredGraph')
        for vertex_id, vertex in enumerate(self._vertices):
            dot.node(str(vertex_id), f"{str(vertex_id)}: {str(vertex._labels)}")
        for source_id, target_ids in enumerate(self._outgoing_vertices):
            for target_id in target_ids:
                dot.edge(str(source_id), str(target_id))
        dot.render(output_file_path, view=False, quiet=True)
