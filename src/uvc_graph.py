import sys

from graphviz import Graph as DotGraph

from typing import MutableSet, Dict

from pymimir import State

from .color import Color


class UVCVertex:
    def __init__(self, id: int, color : Color):
        self._id = id
        self._color = color

    def __eq__(self, other : "UVCVertex"):
        return self._id == other._id

    def __hash__(self):
        return hash(self._id)

    @property
    def id(self):
        return self._id

    @property
    def color(self):
        return self._color


class UVCEdge:
    def __init__(self, source_id: int, target_id: int):
        self._source_id = source_id
        self._target_id = target_id

    def __eq__(self, other : "UVCEdge"):
        return (self._source_id == other._source_id and self._target_id == other._target_id)

    def __hash__(self):
        return hash((self._source_id, self._target_id))

    @property
    def source_id(self):
        return self._source_id

    @property
    def target_id(self):
        return self._target_id


class UVCGraph:
    """ A directed vertex colored graph
    """
    def __init__(self, state : State):
        self._state = state
        self._vertices: Dict[int, UVCVertex] = dict()
        self._adj_list: Dict[int, MutableSet[UVCEdge]] = dict()

    def add_vertex(self, vertex : UVCVertex):
        """ Add a vertex *uniquely* to the graph.
        """
        if vertex.id in self._vertices:
            raise Exception("Vertex with same id already exists.")
        self._vertices[vertex.id] = vertex
        self._adj_list[vertex.id] = set()

    def add_edge(self, edge : UVCEdge):
        """ Add an edge *uniquely* to the graph.
        """
        if edge.source_id not in self._adj_list:
            raise Exception("Source node of edge does not exist.")
        if edge in self._adj_list[edge.source_id]:
            raise Exception("Edge with same source, target and color already exists.")
        self._adj_list[edge.source_id].add(edge)

    def test_is_undirected(self):
        """ Returns true iff the graph is undirected.
        """
        return all(all(UVCEdge(edge.target_id, edge.source_id) in self._adj_list[edge.target_id] for edge in edges) for edges in self._adj_list.values())

    def to_dot(self, output_file_path="output.gc"):
        """ Render a dot representation of the graph.
        """
        dot = DotGraph(comment='UndirectedVertexColoredGraph')
        for vertex in self._vertices.values():
            dot.node(str(vertex.id), f"{str(vertex.id)}: {str(vertex.color)}")
        for _, edges in self._adj_list.items():
            for edge in edges:
                if edge.source_id < edge.target_id:  # only print 1 edge
                    dot.edge(str(edge.source_id), str(edge.target_id))
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
