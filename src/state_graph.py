from pymimir import *

from typing import List

from .mimir_utils import flatten_types
from .color import Color
from .directed_edge_colored_graph import Vertex as DECVertex, Edge as DECEdge, DirectedEdgeColoredGraph as DECGraph
from .directed_vertex_colored_graph import Vertex as DVCVertex, Edge as DVCEdge, DirectedVertexColoredGraph as DVCGraph
from .graph_translator import dec_to_dvc_graph

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
        # Store the state for reference
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
            color_mapper.add(pred.name + "_g")


        ### Step 1: Create Directed Edge Colored Graph

        # Create empty directed edge colored graph
        self._dec_graph = DECGraph(state)

        # Add vertices
        for obj in problem.objects:
            v = DECVertex(id=vertex_mapper.str_to_int(obj.name), color=Color(0, obj.name))
            self._dec_graph.add_vertex(v)

        # Add type edges
        for obj in problem.objects:
            v = DECVertex(id=vertex_mapper.str_to_int(obj.name), color=Color(0, obj.name))
            for typ in flatten_types(obj.type):
                self._dec_graph.add_edge(DECEdge(v, v, Color(color_mapper.str_to_int(typ.name), typ.name)))

        # Add atom edges 
        for dynamic_atom in state.get_atoms():
            if dynamic_atom.predicate.arity > 2:
                raise Exception("Got predicate of arity 2! Implementation does not support this.")
            if dynamic_atom.predicate.arity == 1:
                v = DECVertex(id=vertex_mapper.str_to_int(dynamic_atom.terms[0].name), color=Color(0, dynamic_atom.terms[0].name))
                self._dec_graph.add_edge(DECEdge(v, v, Color(color_mapper.str_to_int(dynamic_atom.predicate.name), dynamic_atom.predicate.name)))
            if dynamic_atom.predicate.arity == 2:
                if dynamic_atom.predicate.name == "=":
                    # Skip equality
                    continue
                v = DECVertex(id=vertex_mapper.str_to_int(dynamic_atom.terms[0].name), color=Color(0, dynamic_atom.terms[0].name))
                v_prime = DECVertex(id=vertex_mapper.str_to_int(dynamic_atom.terms[1].name), color=Color(0, dynamic_atom.terms[1].name))
                self._dec_graph.add_edge(DECEdge(v, v_prime, Color(color_mapper.str_to_int(dynamic_atom.predicate.name), dynamic_atom.predicate.name)))

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
                v = DECVertex(id=vertex_mapper.str_to_int(goal_atom.terms[0].name), color=Color(0, goal_atom.terms[0].name))
                self._dec_graph.add_edge(DECEdge(v, v, Color(color_mapper.str_to_int(predicate_name), predicate_name)))
            if predicate_arity == 2:
                if predicate_name == "=":
                    # Skip equality
                    continue
                v = DECVertex(id=vertex_mapper.str_to_int(goal_atom.terms[0].name), color=Color(0, goal_atom.terms[0].name))
                v_prime = DECVertex(id=vertex_mapper.str_to_int(goal_atom.terms[1].name), color=Color(0, goal_atom.terms[1].name))
                self._dec_graph.add_edge(DECEdge(v, v_prime, Color(color_mapper.str_to_int(predicate_name), predicate_name)))


        ### Step 2: Create Directed Vertex Colored Graph

        # Create empty directed vertex colored graph
        self._dvc_graph = DVCGraph(state)
        for vertex in self._dec_graph.vertices:
            self._dvc_graph.add_vertex(DVCVertex(vertex.id, vertex.color))
        for _, edges in self._dec_graph.adj_list.items():
            for edge in edges:
                v = DVCVertex(edge.source.id, edge.source.color)
                v_middle = DVCVertex(len(self.dvc_graph.vertices), edge.color)
                v_prime = DVCVertex(edge.target.id, edge.target.color)
                self.dvc_graph.add_vertex(v_middle)
                self.dvc_graph.add_edge(DVCEdge(v, v_middle))
                self.dvc_graph.add_edge(DVCEdge(v_middle, v_prime))

    def __str__(self):
        return f"StateGraph({str(self._dec_graph)})"

    @property 
    def dec_graph(self):
        return self._dec_graph
    
    @property 
    def dvc_graph(self):
        return self._dvc_graph
