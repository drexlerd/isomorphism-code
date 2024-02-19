#!/usr/bin/env python

import argparse

from pynauty import *


def create_graph(num_packages : int, grid_size: int):
    num_vertices = num_packages + grid_size ** 2 + 1 + 3 + 4
    # objects
    o_packages = list(range(0, num_packages))
    o_cells = list(range(0 + num_packages, grid_size ** 2 + num_packages))
    o_truck = grid_size ** 2 + num_packages
    # predicates
    p_connected = o_truck + 1
    p_at = p_connected + 1
    p_at_g = p_at + 1
    # types
    t_object = p_at_g + 1
    t_package = t_object + 1
    t_truck = t_package + 1
    t_cell = t_truck + 1

    

    g = Graph(num_vertices, True)

    # Add vertical cell connections
    for col in range(grid_size - 1): 
        for row in range(grid_size):
            cell = o_cells[col * grid_size + row]
            cell_up = o_cells[(col + 1) * grid_size + row]
            g.connect_vertex(cell, [cell_up])
            g.connect_vertex(cell_up, [cell])
    # Add horizontal cell connections
    for col in range(grid_size): 
        for row in range(grid_size - 1):
            cell = o_cells[col * grid_size + row]
            cell_right = o_cells[col * grid_size + row + 1]
            g.connect_vertex(cell, [cell_right])
            g.connect_vertex(cell, [cell_right])
            g.connect_vertex(cell_right, [cell])
            g.connect_vertex(cell, [cell_right])

    return g

    


if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser(description="Process number of packages and size of grid.")

    # Add arguments
    parser.add_argument("-p", "--packages", type=int, help="Number of packages", required=True)
    parser.add_argument("-s", "--grid_size", type=int, help="Size of the squared grid", required=True)
    args = parser.parse_args()

    g = create_graph(args.packages, args.grid_size)
    print(g)


# Define the first graph
#g1 = Graph(9, directed=True)  # [0,...,3] packages (4), [4,...,19] locations (4), 1 truck
#g1.connect_vertex(0, [1, 2, 3])
#g1.connect_vertex(2, [1, 3, 4])
#g1.connect_vertex(4, [3])
#g1.set_vertex_coloring([{0,1},{2,3,4}])
#print(g1)
#
## Define a second graph, which should be tested for isomorphism with g1
#g2 = Graph(5, directed=True)
## Connect vertices in g2 in a way that represents an isomorphic graph
## to g1 or a non-isomorphic graph, depending on what you're testing
#g2.connect_vertex(0, [1, 2, 3])
#g2.connect_vertex(2, [1, 3, 4])
#g2.connect_vertex(4, [3])
#g2.set_vertex_coloring([{0},{1,2,3,4}])
#print(g2)
#
## Generate canonical labels for both graphs
## Note: The actual function to use might differ based on your pynauty version
## This is a conceptual example; you may need to use graph_autgrp or another function
#canonical_label_g1 = autgrp(g1)
#canonical_label_g2 = autgrp(g2)
#print(canonical_label_g1)
#print(canonical_label_g2)
#
#if isomorphic(g1, g2):
#    print("The graphs are isomorphic")
#else:
#    print("The graphs are non-isomorphic")
