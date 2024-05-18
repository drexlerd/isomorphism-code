#! /usr/bin/env python

from lab.parser import Parser


def coverage(content, props):
    props["coverage"] = int("num_instances" in props)

class WLParser(Parser):
    """
    2024-05-09 15:31:15,117 - [Results] Ran to completion.
    2024-05-09 15:31:15,118 - [Results] Domain: /home/dominik/projects/code/weifeiler-lehman-code/data/ferry/domain.pddl
    2024-05-09 15:31:15,118 - [Results] Configuration: [enable_pruning = False, max_num_states = 1000000, ignore_counting = False, mark_true_goal_atoms = False]
    2024-05-09 15:31:15,118 - [Results] Table row: [# = 180, #P = 265, #S = 8430, #C = [3, 0], #V = [3, 0], #C/same = [3, 0], #V/same = [3, 0]]
    """
    def __init__(self):
        super().__init__()
        self.add_pattern("num_instances", r".*\[Results\] Table row: \[# = (\d+), .*", type=int)
        self.add_pattern("num_final_states", r".*\[Results\] Table row: \[# = \d+, #P = (\d+), .*", type=int)
        self.add_pattern("num_total_states", r".*\[Results\] Table row: \[# = \d+, #P = \d+, #S = (\d+), .*", type=int)
        self.add_pattern("num_1fwl_iterations", r".*\[Results\] Table row: \[# = \d+, #P = \d+, #S = \d+, #I = \[(\d+), \d+\], .*", type=int)
        self.add_pattern("num_2fwl_iterations", r".*\[Results\] Table row: \[# = \d+, #P = \d+, #S = \d+, #I = \[\d+, (\d+)\], .*", type=int)
        self.add_pattern("num_1fwl_total_conflicts", r".*\[Results\] Table row: \[# = \d+, #P = \d+, #S = \d+, #I = \[\d+, \d+\], #C = \[(\d+), \d+\], .*", type=int)
        self.add_pattern("num_2fwl_total_conflicts", r".*\[Results\] Table row: \[# = \d+, #P = \d+, #S = \d+, #I = \[\d+, \d+\], #C = \[\d+, (\d+)\], .*", type=int)
        self.add_pattern("num_1fwl_total_value_conflicts", r".*\[Results\] Table row: \[# = \d+, #P = \d+, #S = \d+, #I = \[\d+, \d+\], #C = \[\d+, \d+\], #V = \[(\d+), \d+\], .*", type=int)
        self.add_pattern("num_2fwl_total_value_conflicts", r".*\[Results\] Table row: \[# = \d+, #P = \d+, #S = \d+, #I = \[\d+, \d+\], #C = \[\d+, \d+\], #V = \[\d+, (\d+)\], .*", type=int)
        self.add_pattern("num_1fwl_total_conflicts_same", r".*\[Results\] Table row: \[# = \d+, #P = \d+, #S = \d+, #I = \[\d+, \d+\], #C = \[\d+, \d+\], #V = \[\d+, \d+\], #C/same = \[(\d+), \d+\], .*", type=int)
        self.add_pattern("num_2fwl_total_conflicts_same", r".*\[Results\] Table row: \[# = \d+, #P = \d+, #S = \d+, #I = \[\d+, \d+\], #C = \[\d+, \d+\], #V = \[\d+, \d+\], #C/same = \[\d+, (\d+)\], .*", type=int)
        self.add_pattern("num_1fwl_total_value_conflicts_same", r".*\[Results\] Table row: \[# = \d+, #P = \d+, #S = \d+, #I = \[\d+, \d+\], #C = \[\d+, \d+\], #V = \[\d+, \d+\], #C/same = \[\d+, \d+\], #V/same = \[(\d+), \d+\]\]", type=int)
        self.add_pattern("num_2fwl_total_value_conflicts_same", r".*\[Results\] Table row: \[# = \d+, #P = \d+, #S = \d+, #I = \[\d+, \d+\], #C = \[\d+, \d+\], #V = \[\d+, \d+\], #C/same = \[\d+, \d+\], #V/same = \[\d+, (\d+)\]\]", type=int)

        self.add_function(coverage)
