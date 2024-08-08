import pykwl as kwl

from pymimir import StaticVertexColoredDigraph, compute_vertex_colors


def to_uvc_graph(object_graph: StaticVertexColoredDigraph) -> kwl.EdgeColoredGraph:
    wl_graph = kwl.EdgeColoredGraph(False)

    vertex_colors = compute_vertex_colors(object_graph)
    sorted_vertex_colors = sorted(vertex_colors)
    color_remap = dict()
    for color in sorted_vertex_colors:
        if color not in color_remap:
            color_remap[color] = len(color_remap)

    # Copy vertices and edges. The indices remain identical.
    for vertex_id in range(object_graph.get_num_vertices()):
        wl_graph.add_node(color_remap[vertex_colors[vertex_id]] + 1)  # coloring must start at 1

    for source_vertex_id in range(object_graph.get_num_vertices()):
        for target_vertex_index in object_graph.get_forward_adjacent_vertex_indices(source_vertex_id):
            if (source_vertex_id < target_vertex_index):
                # Antiparallel edges are added automatically in an undirected graph of pykwl.
                wl_graph.add_edge(source_vertex_id, target_vertex_index)
    return wl_graph
