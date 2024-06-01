from pymimir import State

from graphviz import Graph as DotGraph
from typing import List, Union, Tuple

from .color_function import ColorFunction


class Vertex:
    def __init__(self):
        self._labels : List[Union[str, Tuple[str, int]]] = []

    def get_canonical_labelling(self, color_function: ColorFunction) -> Tuple[Tuple[int], Tuple[int], Tuple[int]]:
        """
        """
        #assert len(self._labels) == 1
        #return color_function.get_color_from_domain_label(self._labels[0])
        return color_function.get_color_from_aggregate_label(tuple(sorted(color_function.get_color_from_domain_label(label) for label in self._labels)))


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
        # N helper nodes for each atom of arity N > 0, 1 for each atom of arity 0
        for atom in state.get_atoms():
            self._num_vertices += len(atom.terms)
            if len(atom.terms) == 0:
                self._num_vertices += 1
        # N helper nodes for each goal atom of arity N
        for literal in state.get_problem().goal:
            self._num_vertices += len(literal.atom.terms)
            if len(literal.atom.terms) == 0:
                self._num_vertices += 1
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
            prev_helper_id = None
            for pos, term in enumerate(atom.terms):
                object_id = object_name_to_vertex_index[term.name]
                helper_id = i
                self._vertices[helper_id]._labels.append((predicate_name, pos))
                self._outgoing_vertices[object_id].append(helper_id)
                self._ingoing_vertices[helper_id].append(object_id)
                if prev_helper_id is not None:
                    self._outgoing_vertices[prev_helper_id].append(helper_id)
                    self._ingoing_vertices[helper_id].append(prev_helper_id)
                prev_helper_id = helper_id
                i += 1
            if len(atom.terms) == 0:
                self._vertices[i]._labels.append((predicate_name, -1))
                i += 1
        for literal in state.get_problem().goal:
            predicate_name = literal.atom.predicate.name
            prev_helper_id = None
            for pos, term in enumerate(literal.atom.terms):
                object_id = object_name_to_vertex_index[term.name]
                helper_id = i
                self._vertices[helper_id]._labels.append((predicate_name + "_g", pos))
                self._outgoing_vertices[object_id].append(helper_id)
                self._ingoing_vertices[helper_id].append(object_id)
                if prev_helper_id is not None:
                    self._outgoing_vertices[prev_helper_id].append(helper_id)
                    self._ingoing_vertices[helper_id].append(prev_helper_id)
                prev_helper_id = helper_id
                i += 1
            if len(literal.atom.terms) == 0:
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
