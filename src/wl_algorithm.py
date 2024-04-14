import numpy as np

from .wl_graph import Graph
from typing import Tuple


class WeisfeilerLeman:
    def __init__(self, k: int) -> None:
        if k < 1 or k > 2: raise Exception("k must be either 1 or 2")
        self._color_function = dict()
        self._k = k

    def _singleton_coloring(self, graph: Graph):
        edge_coloring = np.array(graph.get_edge_labels())
        current_coloring = np.array(graph.get_node_labels())
        color_offset = current_coloring.max() + 1

        num_iterations = 0
        while True:
            num_iterations += 1
            next_coloring = np.zeros_like(current_coloring)

            for node_id in range(0, graph.get_num_nodes()):
                # Get the ids of the in- and outgoing edges.
                ingoing_edge_ids = np.array(graph.get_inbound_edges(node_id))
                outgoing_edge_ids = np.array(graph.get_outbound_edges(node_id))
                # Get the ids of adjacent nodes.
                ingoing_node_ids = np.array([graph.get_source(edge_id) for edge_id in ingoing_edge_ids])
                outgoing_node_ids = np.array([graph.get_destination(edge_id) for edge_id in outgoing_edge_ids])
                # Get the colors of the in- and outgoing edges and nodes.
                ingoing_edge_colors = edge_coloring[ingoing_edge_ids]
                outgoing_edge_colors = edge_coloring[outgoing_edge_ids]
                ingoing_node_colors = current_coloring[ingoing_node_ids]
                outgoing_node_colors = current_coloring[outgoing_node_ids]
                # Sort the colors to make the color function invariant to the order. The edge colors are sorted according to the node colors.
                ingoing_sort = np.lexsort((ingoing_edge_colors, ingoing_node_colors))
                ingoing_edge_colors = ingoing_edge_colors[ingoing_sort]
                ingoing_node_colors = ingoing_node_colors[ingoing_sort]
                outgoing_sort = np.lexsort((outgoing_edge_colors, outgoing_node_colors))
                outgoing_edge_colors = outgoing_edge_colors[outgoing_sort]
                outgoing_node_colors = outgoing_node_colors[outgoing_sort]
                # Get and set the new color based on the current color and the color of adjacent nodes.
                node_color = current_coloring[node_id]
                color_key = (node_color, tuple(ingoing_node_colors), tuple(ingoing_edge_colors), tuple(outgoing_node_colors), tuple(outgoing_edge_colors))
                if color_key not in self._color_function: self._color_function[color_key] = len(self._color_function) + color_offset
                next_coloring[node_id] = self._color_function[color_key]

            # Check if we've reached a fixpoint.
            coloring_difference = next_coloring[0] - current_coloring[0]
            if ((current_coloring + coloring_difference) == next_coloring).all(): break
            else: current_coloring = next_coloring

        colors, counts = np.unique(current_coloring, return_counts=True)
        color_sort = np.lexsort((counts, colors))
        return num_iterations, tuple(colors[color_sort]), tuple(counts[color_sort])

    def _pair_coloring(self, graph: Graph):
        # Make these available for helper functions
        num_nodes = graph.get_num_nodes()
        edge_colors = graph.get_edge_labels()
        node_colors = graph.get_node_labels()

        def get_subgraph_color(src_vertex, dst_vertex):
            # Get the colors of the vertices in the pair
            src_color = node_colors[src_vertex]
            dst_color = node_colors[dst_vertex]
            # Get IDs of the edges between src and dst, but also self loops
            forward_edge_ids = graph.get_edges(src_vertex, dst_vertex)
            backward_edge_ids = graph.get_edges(dst_vertex, src_vertex)
            src_self_edge_ids = graph.get_edges(src_vertex, src_vertex)
            dst_self_edge_ids = graph.get_edges(dst_vertex, dst_vertex)
            # Get the colors of the edges mentioned earlier
            forward_edge_colors = [edge_colors[forward_edge_id] for forward_edge_id in forward_edge_ids]
            backward_edge_colors = [edge_colors[backward_edge_id] for backward_edge_id in backward_edge_ids]
            src_self_edge_colors = [edge_colors[src_self_edge_id] for src_self_edge_id in src_self_edge_ids]
            dst_self_edge_colors = [edge_colors[dst_self_edge_id] for dst_self_edge_id in dst_self_edge_ids]
            forward_edge_colors.sort()
            backward_edge_colors.sort()
            src_self_edge_colors.sort()
            dst_self_edge_colors.sort()
            # Get the color of the pair
            subgraph_key = (src_color, dst_color, tuple(forward_edge_colors), tuple(backward_edge_colors), tuple(src_self_edge_colors), tuple(dst_self_edge_colors))
            if subgraph_key not in self._color_function: self._color_function[subgraph_key] = len(self._color_function)
            return self._color_function[subgraph_key]

        def to_index(src_vertex, dst_vertex): return src_vertex * num_nodes + dst_vertex

        def get_neighboring_indices(src_vertex, dst_vertex):
            indices = np.zeros((num_nodes, 2), dtype=int)
            for middle_vertex in range(num_nodes):
                indices[middle_vertex, 0] = to_index(src_vertex, middle_vertex)
                indices[middle_vertex, 1] = to_index(middle_vertex, dst_vertex)
            return indices

        # TODO: Try to simplify the helper functions above, compute them directly with numpy.

        current_coloring = np.zeros(num_nodes * num_nodes, dtype=int)
        neighboring_indices = [None] * (num_nodes * num_nodes)

        for src_vertex in range(num_nodes):
            for dst_vertex in range(num_nodes):
                pair_index = to_index(src_vertex, dst_vertex)
                current_coloring[pair_index] = get_subgraph_color(src_vertex, dst_vertex)
                neighboring_indices[pair_index] = get_neighboring_indices(src_vertex, dst_vertex)

        num_iterations = 0
        while True:
            num_iterations += 1
            next_coloring = np.zeros_like(current_coloring)

            for src_vertex in range(num_nodes):
                for dst_vertex in range(num_nodes):
                    pair_index = to_index(src_vertex, dst_vertex)
                    neighboring_colors = list(map(tuple, current_coloring[neighboring_indices[pair_index]]))
                    neighboring_colors.sort()
                    color_key = (current_coloring[pair_index], *neighboring_colors)
                    if color_key not in self._color_function: self._color_function[color_key] = len(self._color_function)
                    next_coloring[pair_index] = self._color_function[color_key]

            # Check if we've reached a fixpoint.
            coloring_difference = next_coloring[0] - current_coloring[0]
            if ((current_coloring + coloring_difference) == next_coloring).all(): break
            else: current_coloring = next_coloring

        colors, counts = np.unique(current_coloring, return_counts=True)
        color_sort = np.lexsort((counts, colors))
        return num_iterations, tuple(colors[color_sort]), tuple(counts[color_sort])


    def compute_coloring(self, graph: Graph) -> Tuple[int, np.ndarray]:
        if self._k == 1: return self._singleton_coloring(graph)
        if self._k == 2: return self._pair_coloring(graph)
        else: raise Exception("k must be either 1 or 2")
