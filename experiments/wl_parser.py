#! /usr/bin/env python

from lab.parser import Parser


def coverage(content, props):
    num_1fwl_conflicts = props.get("num_1fwl_total_conflicts", None)
    num_2fwl_conflicts = props.get("num_2fwl_total_conflicts", None)

    props["coverage"] = int((num_1fwl_conflicts is not None and num_1fwl_conflicts == 0) or \
        (num_1fwl_conflicts is not None and num_1fwl_conflicts > 0 and num_2fwl_conflicts is not None))

def adapt_booleans(content, props):
    num_1fwl_conflicts = props.get("num_1fwl_total_conflicts", None)
    num_2fwl_conflicts = props.get("num_2fwl_total_conflicts", None)

    if num_1fwl_conflicts is not None:
        if num_1fwl_conflicts == 0:
            props["is_1fwl_valid"] = 1
        else:
            props["is_1fwl_valid"] = 0

    if "is_1fwl_valid" in props and props["is_1fwl_valid"] == 0 and num_2fwl_conflicts is not None:
        if num_2fwl_conflicts == 0:
            props["is_2fwl_valid"] = 1
        else:
            props["is_2fwl_valid"] = 0


class WLParser(Parser):
    """
    2024-05-05 17:12:33,265 - [Preprocessing] Generating state space...
    2024-05-05 17:12:33,265 - [Preprocessing] States: 5
    2024-05-05 17:12:33,265 - [Nauty] Computing...
    2024-05-05 17:12:33,270 - [Nauty] Partitions: 5
    2024-05-05 17:12:33,271 - [1-FWL, UVC] Valid: True; Total Conflicts: 0; Value Conflicts: 0
    2024-05-05 17:12:33,271 - Ran to completion.


    2024-05-05 17:12:34,425 - [Preprocessing] Generating state space...
    2024-05-05 17:12:34,469 - [Preprocessing] States: 12025
    2024-05-05 17:12:34,470 - [Nauty] Computing...
    2024-05-05 17:12:43,987 - [Nauty] Partitions: 3272
    2024-05-05 17:12:44,182 - [1-FWL] Conflict!
    2024-04-18 15:39:39,036 - [1-FWL] Conflict: <State '10723806440305811923'> and <State '14482522608517870975'>
    ...
    2024-04-18 15:39:46,868 - [1-FWL] Conflict: <State '16025430313133900862'> and <State '17353597119015167139'>
    2024-04-18 15:39:47,981 - [1-FWL, UVC] Valid: False; Conflicts: 30
    2024-04-18 15:39:47,982 - [2-FWL, UVC] Validating...
    2024-04-18 15:40:44,013 - [2-FWL, UVC] Valid: True; Conflicts: 0

    2024-07-16 14:36:31,946 - [Results] Table row: [#P = 18, #S = 88, #I = [1, 0], #C = [0, 0], #V = [0, 0]]
    """
    def __init__(self):
        super().__init__()
        self.add_pattern("num_final_states", r".*\[Results\] Table row: \[#P = (\d+).*", type=int)
        self.add_pattern("num_total_states", r".*\[Results\] Table row: \[#P = \d+, #S = (\d+).*", type=int)
        self.add_pattern("num_1fwl_total_conflicts", r".*\[Results\] Table row: \[#P = \d+, #S = \d+, #I = \[\d+, \d+\], #C = \[(\d+), \d+\].*", type=int)
        self.add_pattern("num_2fwl_total_conflicts", r".*\[Results\] Table row: \[ #P = \d+, #S = \d+, #I = \[\d+, \d+\], #C = \[\d+, (\d+)\].*", type=int)
        self.add_pattern("num_1fwl_total_value_conflicts", r".*\[Results\] Table row: \[#P = \d+, #S = \d+, #I = \[\d+, \d+\], #C = \[\d+, \d+\], #V = \[(\d+), \d+\].*", type=int)
        self.add_pattern("num_2fwl_total_value_conflicts", r".*\[Results\] Table row: \[#P = \d+, #S = \d+, #I = \[\d+, \d+\], #C = \[\d+, \d+\], #V = \[\d+, (\d+)\].*", type=int)

        self.add_function(coverage)
        self.add_function(adapt_booleans)
