from pymimir import State

from typing import List, Union, Tuple

from .color_function import ColorFunction


class Vertex:
    def __init__(self):
        self._labels : List[Union[str, Tuple[str, int]]] = []
        # Outgoing neighbours
        self._V_out : List[Vertex] = []
        # Incoming neighbours
        self._V_in : List[Vertex] = []

    def get_canonical_labelling(self, color_function: ColorFunction) -> Tuple[Tuple[int], Tuple[int], Tuple[int]]:
        """ Recursively compute a canonical labelling of the vertex and its direct neighbourhood.
        """
        print((tuple(sorted(color_function.get_color_from_domain_label(label) for label in self._labels)),
                tuple(sorted(tuple(sorted(color_function.get_color_from_domain_label(label) for label in vertex._labels)) for vertex in self._V_out)),
                tuple(sorted(tuple(sorted(color_function.get_color_from_domain_label(label) for label in vertex._labels)) for vertex in self._V_in)),))
        return (tuple(sorted(color_function.get_color_from_domain_label(label) for label in self._labels)),
                tuple(sorted(tuple(sorted(color_function.get_color_from_domain_label(label) for label in vertex._labels)) for vertex in self._V_out)),
                tuple(sorted(tuple(sorted(color_function.get_color_from_domain_label(label) for label in vertex._labels)) for vertex in self._V_in)),)


class StateGraph:
    """
    In this version, we give all vertices the same color
    and encode type information using loop edges
    """
    def __init__(self, state : State, coloring_function: ColorFunction, mark_true_goal_atoms : bool = False):
        self._state = state
        self._coloring_function = coloring_function
        self._mark_true_goal_atoms = mark_true_goal_atoms

        ## 1. Initialize sufficiently many empty vertices and adjacency lists
        self._num_vertices = 0
        # One vertex for each object
        self._num_vertices += len(state.get_problem().objects)
        # N helper nodes for each atom of arity N
        for atom in state.get_atoms():
            self._num_vertices += len(atom.terms)
        # N helper nodes for each goal atom of arity N
        for literal in state.get_problem().goal:
            self._num_vertices += len(literal.atom.terms)
        self._vertices = [Vertex() for _ in range(self._num_vertices)]
        self._outgoing_vertices = [[] for _ in range(self._num_vertices)]
        self._ingoing_vertices = [[] for _ in range(self._num_vertices)]

        ## 2. We need to be able to access vertices by object
        object_name_to_vertex_index = dict()
        for i, obj in enumerate(state.get_problem().objects):
            object_name_to_vertex_index[obj.name] = i

        ## 3. Add vertex labels and edges
        i = 0
        for obj in state.get_problem().objects:
            # Label object node with its type
            self._vertices[i]._labels.append(obj.type.name)
            i += 1
        for atom in state.get_atoms():
            predicate_name = atom.predicate.name
            for pos, term in enumerate(atom.terms):
                object_id = object_name_to_vertex_index[term.name]
                helper_id = i
                self._vertices[helper_id]._labels.append((predicate_name, pos))
                self._outgoing_vertices[object_id].append(helper_id)
                self._ingoing_vertices[helper_id].append(object_id)
                i += 1
        for literal in state.get_problem().goal:
            predicate_name = literal.atom.predicate.name
            for pos, term in enumerate(literal.atom.terms):
                object_id = object_name_to_vertex_index[term.name]
                helper_id = i
                self._vertices[helper_id]._labels.append((predicate_name + "_g", pos))
                self._outgoing_vertices[object_id].append(helper_id)
                self._ingoing_vertices[helper_id].append(object_id)
                i += 1

        ## 4. Propagate neighbourhood information
        for vertex_id, vertex in enumerate(self._vertices):
            vertex._V_in = [self._vertices[i] for i in self._ingoing_vertices[vertex_id]]
            vertex._V_out = [self._vertices[i] for i in self._outgoing_vertices[vertex_id]]

    def compute_initial_coloring(self, color_function: ColorFunction) -> Tuple[int]:
        """ Return a canonical initial coloring of the graph
        taking into account the direct neighbourhood information.
        """
        return tuple(color_function.get_color_from_aggregate_label(vertex.get_canonical_labelling(color_function)) for vertex in self._vertices)
