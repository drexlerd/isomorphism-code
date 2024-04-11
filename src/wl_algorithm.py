import numpy as np

from .wl_graph import Graph
from typing import Tuple


class WeisfeilerLeman:
    def __init__(self) -> None:
        self._color_function = dict()

    def compute_coloring(self, graph: Graph) -> Tuple[int, np.ndarray]:
        edge_coloring = np.array(graph.get_edge_labels())
        current_coloring = np.array(graph.get_node_labels())
        current_histogram = np.unique(current_coloring, return_counts=True)[1]
        current_histogram.sort()
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

            next_histogram = np.unique(next_coloring, return_counts=True)[1]
            next_histogram.sort()

            if (next_histogram.shape == current_histogram.shape) and (next_histogram == current_histogram).all():
                break

            current_coloring = next_coloring
            current_histogram = next_histogram

        colors, counts = np.unique(current_coloring, return_counts=True)
        return num_iterations, tuple(colors), tuple(counts)
