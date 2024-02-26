#! /usr/bin/env python

from lab.parser import Parser


def error(content, props):
    if "num_equivalence_classes" in props:
        props["error"] = "success"
    else:
        props["error"] = "fail"


def coverage(content, props):
    props["coverage"] = int("num_equivalence_classes" in props)


class IsomorphismParser(Parser):
    def __init__(self):
        super().__init__()
        #self.add_pattern("num_states", r"Number of states: (.+)", type=int)
        self.add_pattern("num_generated_states", r"Number of generated states: (.+)", type=int)
        #self.add_pattern("num_transitions", r"Number of transitions: (.+)", type=int)
        #self.add_pattern("num_deadends", r"Number of deadend states: (.+)", type=int)
        #self.add_pattern("num_goals", r"Number of goal states: (.+)", type=int)
        self.add_pattern("num_equivalence_classes", r"Number of equivalence classes: (.+)", type=int)
        self.add_pattern("max_num_vertices_uvc_graph", r"Number of vertices in UVC graph: (.+)", type=int)
        self.add_pattern("time_total", r"Total time: (.+) seconds", type=float)
        self.add_pattern("average_time_per_state", r"Average time per state: (.+) seconds", type=float)
        self.add_function(error)
        self.add_function(coverage)
