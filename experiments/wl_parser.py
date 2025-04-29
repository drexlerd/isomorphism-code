#! /usr/bin/env python

from lab.parser import Parser


def coverage(content, props):
    props["coverage"] = int("num_instances" in props)

class WLParser(Parser):
    """
    2025-04-26 13:51:38,400 - [Results] Ran to completion.
    2025-04-26 13:51:38,400 - [Results] Domain: /home/dominik-drexler/projects/code/isomorphism-code/data/blocks_3/domain.pddl
    2025-04-26 13:51:38,400 - [Results] Configuration: [enable_pruning = False, max_num_states = 10, weak = True]
    2025-04-26 13:51:38,400 - [Results] Table row: [# = 600, #S = 14, #S^2 = 196, #C = [1, 0], #C/#S^2 = [0.005, 0.000], #V = [0, 0], #V/#S^2 = [0.000, 0.000], #C/same = [0, 0], #V/same = [0, 0]]
    2025-04-26 13:51:38,400 - [Results] Peak memory usage: 76 MiB.
    """
    def __init__(self):
        super().__init__()
        self.add_pattern("num_instances", r".*\[Results\] Table row: \[# = (\d+), .*", type=int)
        self.add_pattern("num_equivalence_classes", r".*\[Results\] Table row: \[# = \d+, #S = (\d+), .*", type=int)
        self.add_pattern("num_pairs_of_equivalence_classes", r".*\[Results\] Table row: \[# = \d+, #S = \d+, #S\^2 = (\d+), .*", type=int)
        self.add_pattern("num_total_conflicts_1_wl", r".*\[Results\] Table row: \[# = \d+, #S = \d+, #S\^2 = \d+, #C = \[(\d+), \d+\], .*", type=int)
        self.add_pattern("num_total_conflicts_2_wl", r".*\[Results\] Table row: \[# = \d+, #S = \d+, #S\^2 = \d+, #C = \[\d+, (\d+)\], .*", type=int)
        self.add_pattern("ratio_total_conflicts_1_wl", r".*\[Results\] Table row: \[# = \d+, #S = \d+, #S\^2 = \d+, #C = \[\d+, \d+\], #C/#S\^2 = \[(.+?), .+?\], .*", type=float)
        self.add_pattern("ratio_total_conflicts_2_wl", r".*\[Results\] Table row: \[# = \d+, #S = \d+, #S\^2 = \d+, #C = \[\d+, \d+\], #C/#S\^2 = \[.+?, (.+?)\], .*", type=float)
        self.add_pattern("num_total_value_conflicts_1_wl", r".*\[Results\] Table row: \[# = \d+, #S = \d+, #S\^2 = \d+, #C = \[\d+, \d+\], #C/#S\^2 = \[.+?, .+?\], #V = \[(\d+), \d+\], .*", type=int)
        self.add_pattern("num_total_value_conflicts_2_wl", r".*\[Results\] Table row: \[# = \d+, #S = \d+, #S\^2 = \d+, #C = \[\d+, \d+\], #C/#S\^2 = \[.+?, .+?\], #V = \[\d+, (\d+)\], .*", type=int)
        self.add_pattern("ratio_total_value_conflicts_1_wl", r".*\[Results\] Table row: \[# = \d+, #S = \d+, #S\^2 = \d+, #C = \[\d+, \d+\], #C/#S\^2 = \[.+?, .+?\], #V = \[\d+, \d+\], #V/#S\^2 = \[(.+?), .+?\], .*", type=float)
        self.add_pattern("ratio_total_value_conflicts_2_wl", r".*\[Results\] Table row: \[# = \d+, #S = \d+, #S\^2 = \d+, #C = \[\d+, \d+\], #C/#S\^2 = \[.+?, .+?\], #V = \[\d+, \d+\], #V/#S\^2 = \[.+?, (.+?)\], .*", type=float)
        self.add_pattern("peak_memory_in_mib", r".*\[Results\] Peak memory usage: (\d+) MiB\.", type=int)

        self.add_function(coverage)
