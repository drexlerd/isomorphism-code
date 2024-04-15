from collections import defaultdict


class Graph:
    def __init__(self, directed: bool):
        self._directed = directed
        self._outgoing_edges = []
        self._ingoing_edges = []
        self._outgoing_adjacent = []
        self._ingoing_adjacent = []
        self._edge_sources = []
        self._edge_destinations = []
        self._vertex_labels = []
        self._edge_labels = []

    def add_vertex(self, label = 0):
        vertex = self.get_num_vertices()
        self._outgoing_edges.append([])
        self._ingoing_edges.append([])
        self._outgoing_adjacent.append(defaultdict(list))
        self._ingoing_adjacent.append(defaultdict(list))
        self._vertex_labels.append(label)
        return vertex

    def add_edge(self, v, w, label = 0):
        n = self.get_num_edges()
        self._outgoing_edges[v].append(n)
        self._ingoing_edges[w].append(n)
        self._outgoing_adjacent[v][w].append(n)
        self._ingoing_adjacent[w][v].append(n)
        self._edge_sources.append(v)
        self._edge_destinations.append(w)
        self._edge_labels.append(label)
        if not self._directed:
            n = self.get_num_edges()
            self._outgoing_edges[w].append(n)
            self._ingoing_edges[v].append(n)
            self._outgoing_adjacent[w][v].append(n)
            self._ingoing_adjacent[v][w].append(n)
            self._edge_sources.append(w)
            self._edge_destinations.append(v)
            self._edge_labels.append(label)

    def get_source(self, edge):
        return self._edge_sources[edge]

    def get_destination(self, edge):
        return self._edge_destinations[edge]

    def get_outbound_edges(self, vertex):
        return self._outgoing_edges[vertex]

    def get_inbound_edges(self, vertex):
        return self._ingoing_edges[vertex]

    def get_num_vertices(self):
        return len(self._vertex_labels)

    def get_num_edges(self):
        return len(self._edge_sources)

    def get_vertex_label(self, vertex):
        return self._vertex_labels[vertex]

    def get_vertex_labels(self):
        return self._vertex_labels

    def get_edge_labels(self):
        return self._edge_labels

    def get_edges(self, src_vertex, dst_vertex):
        return self._outgoing_adjacent[src_vertex][dst_vertex]

    def is_directed(self):
        return self._directed

    def is_undirected(self):
        return not self._directed
