from pymimir import *

from typing import List

from .mimir_utils import flatten_types
from .color import Color
from .directed_edge_colored_graph import Vertex, Edge, DirectedEdgeColoredGraph


class ColorMapper:
    """
    Perfect has function to map a list of types to a color
    """
    def __init__(self, domain: Domain):
        self._type_to_value = {t: Color(i, t.name) for i, t in enumerate(domain.types)}
        self._predicate_to_value = {p: Color(i + len(domain.types), p.name) for i, p in enumerate(domain.predicates)}

    def get_color_of_type(self, type : Type):
        return self._type_to_value[type]
    
    def get_color_of_predicate(self, predicate : Predicate):
        return self._predicate_to_value[predicate]


class StateGraph:
    """
    In this version, we give all vertices the same color 
    and encode type information using loop edges
    """
    def __init__(self, state : State):
        self._state = state 

        # Create empty edge colored graph
        self._graph = DirectedEdgeColoredGraph()

        color_mapper = ColorMapper(state.get_problem().domain)

        # Add vertices
        problem = state.get_problem()
        for i, object in enumerate(problem.objects):
            v = Vertex(id=i, color=Color(0, object.name))
            self._graph.add_vertex(v)

        # Add type edges
        for i, object in enumerate(problem.objects):
            v = Vertex(id=i, color=Color(0, object.name))
            for type in flatten_types(object.type):
                self._graph.add_edge(Edge(v, v, color_mapper.get_color_of_type(type)))
        


    def __str__(self):
        return f"StateGraph({str(self._graph)})"
