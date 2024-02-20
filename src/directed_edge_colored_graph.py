from graphviz import Digraph

from typing import MutableSet, Dict

from pymimir import State

from .color import Color


class Vertex:
    def __init__(self, id: int, color : Color):
        self._id = id
        self._color = color

    def __eq__(self, other : "Vertex"):
        return self._id == other._id

    def __hash__(self):
        return hash(self._id)

    def __str__(self):
        return f"({str(self._id)},{str(self._color)})"

    @property
    def id(self):
        return self._id
  
    @property 
    def color(self):
        return self._color

    
class Edge:
    def __init__(self, source: Vertex, target: Vertex, color: Color):
        self._source = source
        self._target = target
        self._color = color

    def __eq__(self, other : "Edge"):
        return (self._source == other._source and self._target == other._target and self._color == other._color)

    def __hash__(self):
        return hash((self._source, self._target, self._color))
    
    def __str__(self):
        return f"({str(self._source)},{str(self._color)},{str(self._target)})"
    
    @property 
    def source(self):
        return self._source
    
    @property 
    def target(self):
        return self._target
    
    @property
    def color(self):
        return self._color


class DirectedEdgeColoredGraph:
    def __init__(self, state : State):
        self._state = state
        self._vertices: MutableSet[Vertex] = set()
        self._adj_list: Dict[Vertex, MutableSet[Edge]] = dict()

    def add_vertex(self, vertex : Vertex):
        if vertex in self._vertices:
            raise Exception("Vertex with same id already exists.")
        self._vertices.add(vertex)
        self._adj_list[vertex] = set()

    def add_edge(self, edge : Edge):
        if edge.source not in self._adj_list:
            raise Exception("Source node of edge does not exist.")
        if edge in self._adj_list[edge.source]:
            raise Exception("Edge with same source, target and color already exists.")
        self._adj_list[edge.source].add(edge)

    def __str__(self):
        vertices = [str(v) for v in self._vertices]
        edges = {str(v) : [str(e) for e in edges_from_v] for v, edges_from_v in self._adj_list.items()}
        return f"DirectedEdgeColoredGraph(Vertices({vertices}),AdjList({edges}))"
    
    def to_dot(self):
        """
        Return a dot representation of the graph.
        """
        dot = Digraph(comment='DirectedEdgeColoredGraph')
        for vertex in self._vertices:
            dot.node(str(vertex.id), str(vertex.color.concrete))
        for _, edges in self._adj_list.items():
            for edge in edges:
                dot.edge(str(edge.source.id), str(edge.target.id), str(edge.color.concrete))
        dot.render("output.gc", view=True)
    
    @property
    def state(self):
        return self._state

    @property
    def vertices(self):
        return self._vertices
    
    @property
    def adj_list(self):
        return self._adj_list

