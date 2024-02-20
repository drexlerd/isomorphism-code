from pymimir import *

from typing import List

from .mimir_utils import flatten_types
from .color import Color
from .directed_edge_colored_graph import Vertex, Edge, DirectedEdgeColoredGraph


class StringToIntMapper:
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
        return self._str_to_int[string]

    def int_to_str(self, number : int):
        return self._int_to_str[number]



class StateGraph:
    """
    In this version, we give all vertices the same color 
    and encode type information using loop edges
    """
    def __init__(self, state : State):
        self._state = state

        # Bookkeeping
        problem = state.get_problem()
        vertex_mapper = StringToIntMapper()
        for obj in problem.objects:
            vertex_mapper.add(obj.name)
        color_mapper = StringToIntMapper()
        for typ in problem.domain.types:
            color_mapper.add(typ.name)
        for pred in problem.domain.predicates:
            color_mapper.add(pred.name)

        # Create empty edge colored graph
        self._graph = DirectedEdgeColoredGraph()

        # Add vertices
        for obj in problem.objects:
            v = Vertex(id=vertex_mapper.str_to_int(obj.name), color=Color(0, obj.name))
            self._graph.add_vertex(v)

        # Add type edges
        for obj in problem.objects:
            v = Vertex(id=vertex_mapper.str_to_int(obj.name), color=Color(0, obj.name))
            for typ in flatten_types(obj.type):
                self._graph.add_edge(Edge(v, v, Color(color_mapper.str_to_int(typ.name), typ.name)))

        # Add atom edges 
        for dynamic_atom in state.get_atoms():
            if dynamic_atom.predicate.arity > 2:
                raise Exception("Got predicate of arity 2! Implementation does not support this.")
            if dynamic_atom.predicate.arity == 1:
                v = Vertex(id=vertex_mapper.str_to_int(dynamic_atom.terms[0].name), color=Color(0, dynamic_atom.terms[0].name))
                self._graph.add_edge(Edge(v, v, Color(color_mapper.str_to_int(dynamic_atom.predicate.name), dynamic_atom.predicate.name)))
            if dynamic_atom.predicate.arity == 2:
                if dynamic_atom.predicate.name == "=": 
                    # Skip equality
                    continue
                v = Vertex(id=vertex_mapper.str_to_int(dynamic_atom.terms[0].name), color=Color(0, dynamic_atom.terms[0].name))
                v_prime = Vertex(id=vertex_mapper.str_to_int(dynamic_atom.terms[1].name), color=Color(0, dynamic_atom.terms[1].name))
                self._graph.add_edge(Edge(v, v_prime, Color(color_mapper.str_to_int(dynamic_atom.predicate.name), dynamic_atom.predicate.name)))

    @property 
    def graph(self):
        return self._graph
            
        

    def __str__(self):
        return f"StateGraph({str(self._graph)})"
