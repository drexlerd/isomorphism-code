import sys

from graphviz import Digraph

from typing import MutableSet, Dict

from pymimir import State

from .color import Color


class DVCVertex:
    def __init__(self, id: int, color : Color):
        self._id = id
        self._color = color

    def __eq__(self, other : "DVCVertex"):
        return self._id == other._id

    def __hash__(self):
        return hash(self._id)

    @property
    def id(self):
        return self._id
  
    @property 
    def color(self):
        return self._color

    
class DVCEdge:
    def __init__(self, source: DVCVertex, target: DVCVertex):
        self._source = source
        self._target = target

    def __eq__(self, other : "DVCEdge"):
        return (self._source == other._source and self._target == other._target)

    def __hash__(self):
        return hash((self._source, self._target))

    @property 
    def source(self):
        return self._source
    
    @property 
    def target(self):
        return self._target
    

class DVCGraph:
    def __init__(self, state : State):
        self._state = state
        self._vertices: MutableSet[DVCVertex] = set()
        self._adj_list: Dict[DVCVertex, MutableSet[DVCEdge]] = dict()

    def add_vertex(self, vertex : DVCVertex):
        """ Add a vertex *uniquely* to the graph.
        """
        if vertex in self._vertices:
            raise Exception("Vertex with same id already exists.")
        self._vertices.add(vertex)
        self._adj_list[vertex] = set()

    def add_edge(self, edge : DVCEdge):
        """ Add an edge *uniquely* to the graph.
        """
        if edge.source not in self._adj_list:
            raise Exception("Source node of edge does not exist.")
        if edge in self._adj_list[edge.source]:
            raise Exception("Edge with same source, target and color already exists.")
        self._adj_list[edge.source].add(edge)

    def to_dot(self, output_file_path="output.gc"):
        """ Render a dot representation of the graph.
        """
        dot = Digraph(comment='DirectedVertexColoredGraph')
        for vertex in self._vertices:
            dot.node(str(vertex.id), str(vertex.color))
        for _, edges in self._adj_list.items():
            for edge in edges:
                dot.edge(str(edge.source.id), str(edge.target.id))
        dot.render(output_file_path, view=False, quiet=True)

    @property
    def state(self):
        return self._state

    @property
    def vertices(self):
        return self._vertices
    
    @property
    def adj_list(self):
        return self._adj_list
