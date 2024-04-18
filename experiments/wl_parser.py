#! /usr/bin/env python

from lab.parser import Parser


def error(content, props):
    if "num_equivalence_classes" in props:
        props["error"] = "success"
    else:
        props["error"] = "fail"


def coverage(content, props):
    num_1fwl_conflicts = props.get("num_1fwl_conflicts", None)
    num_2fwl_conflicts = props.get("num_2fwl_conflicts", None)

    props["coverage"] = int((num_1fwl_conflicts is not None and num_1fwl_conflicts == 0) or \
        (num_1fwl_conflicts is not None and num_1fwl_conflicts > 0 and num_2fwl_conflicts is not None))


class WLParser(Parser):
    """
    2024-04-18 14:49:46,258 - [Preprocessing] Generating state space...
    2024-04-18 14:49:46,260 - [Preprocessing] States: 704
    2024-04-18 14:49:46,260 - [Nauty] Computing...
    2024-04-18 14:49:46,544 - [Nauty] Partitions: 30
    2024-04-18 14:49:46,544 - [1-FWL, UVC] Validating...
    2024-04-18 14:49:46,574 - [1-FWL, UVC] Valid: True; Conflicts: 0


    2024-04-18 15:39:28,641 - [Preprocessing] Generating state space...
    2024-04-18 15:39:28,738 - [Preprocessing] States: 12025
    2024-04-18 15:39:28,739 - [Nauty] Computing...
    2024-04-18 15:39:38,848 - [Nauty] Partitions: 3272
    2024-04-18 15:39:38,849 - [1-FWL, UVC] Validating...
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
        self.add_pattern("is_1fwl_valid", r".*\[1-FWL, UVC\] Valid: (.+); Conflicts: .+", type=bool)
        self.add_pattern("num_1fwl_conflicts", r".*\[1-FWL, UVC\] Valid: .+; Conflicts: (.+)", type=int)
        self.add_pattern("is_2fwl_valid", r".*\[2-FWL, UVC\] Valid: (.+); Conflicts: .+", type=bool)
        self.add_pattern("num_2fwl_conflicts", r".*\[2-FWL, UVC\] Valid: .+; Conflicts: (.+)", type=int)

        self.add_function(coverage)
