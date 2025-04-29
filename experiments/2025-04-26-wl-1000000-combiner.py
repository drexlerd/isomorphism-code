#! /usr/bin/env python

from lab.experiment import Experiment
from lab.reports import Attribute, geometric_mean
from downward.reports.absolute import AbsoluteReport

# Create custom report class with suitable info and error attributes.
class BaseReport(AbsoluteReport):
    INFO_ATTRIBUTES = ["time_limit", "memory_limit"]
    ERROR_ATTRIBUTES = [
        "domain",
        "problem",
        "algorithm",
        "unexplained_errors",
        "error",
        "node",
    ]

ATTRIBUTES = [
    "run_dir",
    Attribute("coverage", absolute=True, min_wins=False, scale="linear"),
    Attribute("num_instances", absolute=True, min_wins=False, scale="linear"),
    Attribute("num_equivalence_classes", absolute=True, min_wins=False, scale="linear"),
    Attribute("num_pairs_of_equivalence_classes", absolute=True, min_wins=False, scale="linear"),
    Attribute("num_total_conflicts_1_wl", absolute=True, min_wins=False, scale="linear"),
    Attribute("num_total_conflicts_2_wl", absolute=True, min_wins=False, scale="linear"),
    Attribute("ratio_total_conflicts_1_wl", absolute=True, min_wins=False, scale="linear", digits=5),
    Attribute("ratio_total_conflicts_2_wl", absolute=True, min_wins=False, scale="linear", digits=5),
    Attribute("num_total_value_conflicts_1_wl", absolute=True, min_wins=False, scale="linear"),
    Attribute("num_total_value_conflicts_2_wl", absolute=True, min_wins=False, scale="linear"),
    Attribute("ratio_total_value_conflicts_1_wl", absolute=True, min_wins=False, scale="linear", digits=5),
    Attribute("ratio_total_value_conflicts_2_wl", absolute=True, min_wins=False, scale="linear", digits=5),
    Attribute("peak_memory_in_mib", absolute=True, min_wins=True, scale="linear"),
]


exp = Experiment("2025-04-26-wl-1000000-combined")

exp.add_fetcher("2025-04-26-wl-1000000-eval")
exp.add_fetcher("2025-04-26-wl-weak-1000000-eval")

exp.add_report(BaseReport(attributes=ATTRIBUTES, filter_algorithm=["wl", "wl-no-decoding-table"]))

exp.run_steps()
