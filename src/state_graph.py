from pymimir import State, Problem
from pynauty import Graph as NautyGraph, certificate as nauty_certificate

from typing import List, MutableSet
from collections import defaultdict

from .color import Color
from .dec_graph import DECVertex, DECEdge, DECGraph
from .dvc_graph import DVCVertex, DVCEdge, DVCGraph


class NameToIndexMapper:
    """
    Perfect has function to map a list of types to a color
    """
    def __init__(self):
        self._str_to_int = dict()
        self._int_to_str = dict()

    def add(self, string : str):
        assert string not in self._str_to_int
        number = len(self._str_to_int)
        self._str_to_int[string] = number
        self._int_to_str[number] = string

    def str_to_int(self, string : str):
        assert string in self._str_to_int
        return self._str_to_int[string]

    def int_to_str(self, number : int):
        assert number in self._int_to_str
        return self._int_to_str[number]

    def strs_to_int(self, strings: MutableSet[str]):
        """ Compute a perfect hash value for a given non-empty set of labels.
        """
        assert(strings)
        number = 0
        factor = 1
        for string in sorted(list(strings)):
            number += factor * self._str_to_int[string]
            factor *= len(self._str_to_int)
        return number


class StateGraph:
    """
    In this version, we give all vertices the same color
    and encode type information using loop edges
    """
    def __init__(self, state : State):
        self._state = state
        # Bookkeeping: create mappings from names to integers
        vertex_mapper, color_mapper = self._create_name_to_index_mapping(state)

        ### Step 1: Create Directed Edge Colored Graph (DECGraph)
        self._dec_graph = self._create_directed_edge_colored_graph(state, vertex_mapper, color_mapper)

        ### Step 2: Create Directed Vertex Colored Graph (DVCGraph)
        self._dvc_graph = self._create_directed_vertex_colored_graph(self._dec_graph)

        ### Step 3: Translate to pynauty graph
        self._nauty_graph = self._create_pynauty_graph(self._dvc_graph)

        ### Step 4: Compute the graph certificate
        self._nauty_certificate = nauty_certificate(self._nauty_graph)

    def _create_name_to_index_mapping(self, state: State):
        problem = state.get_problem()
        vertex_mapper = NameToIndexMapper()
        for obj in problem.objects:
            vertex_mapper.add(obj.name)
        color_mapper = NameToIndexMapper()
        for typ in problem.domain.types:
            color_mapper.add(typ.name)
        for pred in problem.domain.predicates:
            color_mapper.add(pred.name)
            color_mapper.add(pred.name + "_g")
        for const in problem.domain.constants:
            color_mapper.add(const.name)
        return vertex_mapper, color_mapper

    def _create_directed_edge_colored_graph(self, state, vertex_mapper, color_mapper):
        problem = state.get_problem()

        # Create empty directed edge colored graph
        graph = DECGraph(state)

        # Add vertices
        for obj in problem.objects:
            # Create color based on the type
            # Note: we currently assume that each object has a single parent type
            # To support "either" types, we must compute an aggregate
            v = DECVertex(
                id=vertex_mapper.str_to_int(obj.name),
                color=Color(
                    value=color_mapper.str_to_int(obj.type.name),
                    labels={obj.type.name},
                    info=obj.name))
            graph.add_vertex(v)

        # Add atom edges
        for dynamic_atom in state.get_atoms():
            if dynamic_atom.predicate.arity > 2:
                raise Exception("Got predicate of arity 2! Implementation does not support this.")
            if dynamic_atom.predicate.arity == 1:
                v_id = vertex_mapper.str_to_int(dynamic_atom.terms[0].name)
                graph.add_edge(
                    DECEdge(v_id, v_id,
                        Color(
                            value=color_mapper.str_to_int(dynamic_atom.predicate.name),
                            labels={dynamic_atom.predicate.name})))
            if dynamic_atom.predicate.arity == 2:
                if dynamic_atom.predicate.name == "=":
                    # Skip equality
                    continue
                v_id = vertex_mapper.str_to_int(dynamic_atom.terms[0].name)
                v_prime_id = vertex_mapper.str_to_int(dynamic_atom.terms[1].name)
                graph.add_edge(
                    DECEdge(v_id, v_prime_id,
                        Color(
                            value=color_mapper.str_to_int(dynamic_atom.predicate.name),
                            labels={dynamic_atom.predicate.name})))

        # Add goal atom edges
        for goal_literal in problem.goal:
            if goal_literal.negated:
                raise Exception("Negated goal atoms currently not supported.")
            goal_atom = goal_literal.atom
            predicate_arity = goal_atom.predicate.arity
            predicate_name = goal_atom.predicate.name + "_g"
            if predicate_arity > 2:
                raise Exception("Got predicate of arity 2! Implementation does not support this.")
            if predicate_arity == 1:
                v_id = vertex_mapper.str_to_int(goal_atom.terms[0].name)
                graph.add_edge(
                    DECEdge(v_id, v_id,
                        Color(
                            value=color_mapper.str_to_int(predicate_name),
                            labels={predicate_name})))
            if predicate_arity == 2:
                if predicate_name == "=":
                    # Skip equality
                    continue
                v_id = vertex_mapper.str_to_int(goal_atom.terms[0].name)
                v_prime_id = vertex_mapper.str_to_int(goal_atom.terms[1].name)
                graph.add_edge(
                    DECEdge(v_id, v_prime_id,
                        Color(
                            value=color_mapper.str_to_int(predicate_name),
                            labels={predicate_name})))

        # Add constant edges
        for const in problem.domain.constants:
            const_name = const.name
            v_id = vertex_mapper.str_to_int(const_name)
            graph.add_edge(
                DECEdge(v_id, v_id,
                    Color(
                        value=color_mapper.str_to_int(const_name),
                        labels={const_name})))
        return graph

    def _create_directed_vertex_colored_graph(self, dec_graph: DECGraph):
        ### More compact encoding with loops integrated into vertex colors
        graph = DVCGraph(dec_graph.state)
        for vertex in dec_graph.vertices.values():
            graph.add_vertex(DVCVertex(
                id=vertex.id,
                color=vertex.color))
        for source_id, edges in dec_graph.adj_list.items():
            # For each transition, encode the label in a helper vertex
            for edge in edges:
                assert edge.source_id == source_id
                v = dec_graph.vertices[source_id]
                v_prime = dec_graph.vertices[edge.target_id]
                v_middle = DVCVertex(len(graph.vertices), edge.color)
                graph.add_vertex(v_middle)
                graph.add_edge(DVCEdge(v.id, v_middle.id))
                graph.add_edge(DVCEdge(v_middle.id, v_prime.id))
        return graph

    def _create_pynauty_graph(self, dvc_graph: DVCGraph):
        color_to_vertices = defaultdict(set)
        for vertex in dvc_graph.vertices.values():
            color_to_vertices[vertex.color.value].add(vertex.id)
        color_to_vertices = dict(sorted(color_to_vertices.items()))
        vertex_partitioning = list(color_to_vertices.values())
        graph = NautyGraph(
            number_of_vertices=len(dvc_graph.vertices),
            directed=True,
            adjacency_dict={source_id: [edge.target_id for edge in edges]
                            for source_id, edges in dvc_graph.adj_list.items()},
            vertex_coloring=vertex_partitioning)
        return graph

    def __str__(self):
        return f"StateGraph({str(self._dec_graph)})"

    @property
    def state(self):
        return self._state

    @property
    def dec_graph(self):
        return self._dec_graph

    @property
    def dvc_graph(self):
        return self._dvc_graph

    @property
    def nauty_certificate(self):
        return self._nauty_certificate
