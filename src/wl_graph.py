class Graph:
    def __init__(self, directed: bool):
        self._directed = directed
        self._outgoing_edges = []
        self._ingoing_edges = []
        self._edge_sources = []
        self._edge_destinations = []
        self._unique_node_labels = set()
        self._unique_edge_labels = set()
        self._node_labels = []
        self._edge_labels = []

    # add node/edge
    def add_node(self, label = 0):
        n = self.get_num_nodes()
        self._outgoing_edges.append([])
        self._ingoing_edges.append([])
        self._node_labels.append(label)
        self._unique_node_labels.add(label)
        return n

    def add_edge(self, v, w, label = 0):
        n = self.get_num_edges()
        self._outgoing_edges[v].append(n)
        self._ingoing_edges[w].append(n)
        self._edge_sources.append(v)
        self._edge_destinations.append(w)
        self._edge_labels.append(label)
        self._unique_edge_labels.add(label)
        # Add opposing edge if not directed
        if not self._directed:
            n = self.get_num_edges()
            self._outgoing_edges[w].append(n)
            self._ingoing_edges[v].append(n)
            self._edge_sources.append(w)
            self._edge_destinations.append(v)
            self._edge_labels.append(label)

    def get_source(self, e):
        return self._edge_sources[e]

    def get_destination(self, e):
        return self._edge_destinations[e]

    def get_outbound_edges(self, v):
        return self._outgoing_edges[v]

    def get_inbound_edges(self, v):
        return self._ingoing_edges[v]

    def get_num_nodes(self):
        return len(self._node_labels)

    def get_num_edges(self):
        return len(self._edge_sources)

    def get_set_node_labels(self):
        return self._unique_node_labels

    def get_node_labels(self):
        return self._node_labels

    def get_set_edge_labels(self):
        return self._unique_edge_labels

    def get_edge_labels(self):
        return self._edge_labels

    def directed(self):
        return self._directed

    def undirected(self):
        return not self._directed
