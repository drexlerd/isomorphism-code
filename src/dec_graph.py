from graphviz import Digraph

from typing import MutableSet, Dict

from pymimir import State

from .color import Color


class DECVertex:
    def __init__(self, id: int, color : Color):
        self._id = id
        self._color = color

    def __eq__(self, other : "DECVertex"):
        return self._id == other._id

    def __hash__(self):
        return hash(self._id)

    @property
    def id(self):
        return self._id
  
    @property 
    def color(self):
        return self._color

    
class DECEdge:
    def __init__(self, source: DECVertex, target: DECVertex, color: Color):
        self._source = source
        self._target = target
        self._color = color

    def __eq__(self, other : "DECEdge"):
        return (self._source == other._source and self._target == other._target and self._color == other._color)

    def __hash__(self):
        return hash((self._source, self._target, self._color))
    
    @property 
    def source(self):
        return self._source
    
    @property 
    def target(self):
        return self._target
    
    @property
    def color(self):
        return self._color


class DECGraph:
    def __init__(self, state : State):
        self._state = state
        self._vertices: MutableSet[DECVertex] = set()
        self._adj_list: Dict[DECVertex, MutableSet[DECEdge]] = dict()

    def add_vertex(self, vertex : DECVertex):
        """ Add a vertex *uniquely* to the graph.
        """
        if vertex in self._vertices:
            raise Exception("Vertex with same id already exists.")
        self._vertices.add(vertex)
        self._adj_list[vertex] = set()

    def add_edge(self, edge : DECEdge):
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
        dot = Digraph(comment='DirectedEdgeColoredGraph')
        for vertex in self._vertices:
            dot.node(str(vertex.id), str(vertex.color))
        for _, edges in self._adj_list.items():
            for edge in edges:
                dot.edge(str(edge.source.id), str(edge.target.id), str(edge.color))
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

