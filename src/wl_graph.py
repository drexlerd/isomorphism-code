class Graph:
    def __init__(self, directed: bool):
        self._directed = directed
        self._adjacency_lists_outbound = []
        self._adjacency_lists_inbound = []
        self._edges_src = []
        self._edges_dst = []
        self._set_node_labels = set()
        self._set_edge_labels = set()
        self._node_labels = []
        self._edge_labels = []
        self._num_nodes = 0

    # add node/edge
    def add_node(self, label = 0):
        self._adjacency_lists_outbound.append([])
        self._adjacency_lists_inbound.append([])
        self._node_labels.append(label)
        self._set_node_labels.add(label)
        self._num_nodes += 1
        return self._num_nodes - 1

    def add_edge(self, v, w, label = 0):
        n = self.get_num_edges()
        self._adjacency_lists_outbound[v].append(n)
        self._adjacency_lists_inbound[w].append(n)
        self._edges_src.append(v)
        self._edges_dst.append(w)
        self._edge_labels.append(label)
        self._set_edge_labels.add(label)
        # Add opposing edge if not directed
        if not self._directed:
            n = self.get_num_edges()
            self._adjacency_lists_outbound[w].append(n)
            self._adjacency_lists_inbound[v].append(n)
            self._edges_src.append(w)
            self._edges_dst.append(v)
            self._edge_labels.append(label)

    def get_src(self, e):
        return self._edges_src[e]

    def get_dst(self, e):
        return self._edges_dst[e]

    def get_degree(self, v):
        return self.get_in_degree(v) + self.get_out_degree(v) if self._directed else self.get_out_degree(v)

    def get_in_degree(self, v):
        return len(self._adjacency_lists_outbound[v])

    def get_out_degree(self, v):
        return len(self._adjacency_lists_inbound[v])

    def get_outbound_edges(self, v):
        return self._adjacency_lists_outbound[v]

    def get_inbound_edges(self, v):
        return self._adjacency_lists_inbound[v]

    def get_incident_edges(self, v):
        return self.get_outbound_edges(v) + self.get_inbound_edges(v) if self._directed else self.get_outbound_edges(v)

    def get_num_nodes(self):
        return self._num_nodes

    def get_num_edges(self):
        return len(self._edges_src)

    def get_set_node_labels(self):
        return self._set_node_labels

    def get_node_labels(self):
        return self._node_labels

    def get_set_edge_labels(self):
        return self._set_edge_labels

    def get_edge_labels(self):
        return self._edge_labels

    def has_edge(self, v, w):
        for e in self._adjacency_lists_outbound[v]:
            if self.get_src(e) == v and self.get_dst(e) == w:
                return True
        return False

    def directed(self):
        return self._directed

    def undirected(self):
        return not self._directed
