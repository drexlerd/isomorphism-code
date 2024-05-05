#! /usr/bin/env python

from lab.parser import Parser


def coverage(content, props):
    num_1fwl_conflicts = props.get("num_1fwl_total_conflicts", None)
    num_2fwl_conflicts = props.get("num_2fwl_total_conflicts", None)

    props["coverage"] = int((num_1fwl_conflicts is not None and num_1fwl_conflicts == 0) or \
        (num_1fwl_conflicts is not None and num_1fwl_conflicts > 0 and num_2fwl_conflicts is not None))

def adapt_booleans(content, props):
    is_1fwl_valid = props.get("is_1fwl_valid", None)
    if is_1fwl_valid is not None:
        if is_1fwl_valid == "True":
            props["is_1fwl_valid"] = 1
        elif is_1fwl_valid == "False":
            props["is_1fwl_valid"] = 0
        else:
            raise RuntimeError("Unexpected string in is_1fwl_valid: ", is_1fwl_valid)

    is_2fwl_valid = props.get("is_2fwl_valid", None)
    if is_2fwl_valid:
        if is_2fwl_valid == "True":
            props["is_2fwl_valid"] = 1
        elif is_2fwl_valid == "False":
            props["is_2fwl_valid"] = 0
        else:
            raise RuntimeError("Unexpected string in is_2fwl_valid: ", is_2fwl_valid)

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
    """
    def __init__(self):
        super().__init__()
        self.add_pattern("num_states", r".*\[Preprocessing\] States: (.+)", type=int)
        self.add_pattern("num_partitions", r".*\[Nauty\] Partitions: (.+)", type=int)
        self.add_pattern("is_1fwl_valid", r".*\[1-FWL, UVC\] Valid: (.+); Total Conflicts: .+; Value Conflicts: .+", type=str)
        self.add_pattern("num_1fwl_total_conflicts", r".*\[1-FWL, UVC\] Valid: .+; Total Conflicts: (.+); Value Conflicts: .+", type=int)
        self.add_pattern("num_1fwl_value_conflicts", r".*\[1-FWL, UVC\] Valid: .+; Total Conflicts: .+; Value Conflicts: (.+)", type=int)
        self.add_pattern("is_2fwl_valid", r".*\[2-FWL, UVC\] Valid: (.+); Total Conflicts: .+; Value Conflicts: .+", type=str)
        self.add_pattern("num_2fwl_total_conflicts", r".*\[2-FWL, UVC\] Valid: .+; Total Conflicts: (.+); Value Conflicts: .+", type=int)
        self.add_pattern("num_2fwl_value_conflicts", r".*\[2-FWL, UVC\] Valid: .+; Total Conflicts: .+; Value Conflicts: (.+)", type=int)

        self.add_function(coverage)
        self.add_function(adapt_booleans)
