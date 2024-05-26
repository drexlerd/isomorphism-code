#! /usr/bin/env python
import platform
import re
import sys

from pathlib import Path

from downward import suites
from downward.reports.absolute import AbsoluteReport
from lab.environments import TetralithEnvironment, LocalEnvironment
from lab.experiment import Experiment
from lab.reports import Attribute, geometric_mean
from pairwise_wl_parser import WLParser


# Create custom report class with suitable info and error attributes.
class BaseReport(AbsoluteReport):
    INFO_ATTRIBUTES = ["time_limit", "memory_limit"]
    ERROR_ATTRIBUTES = [
        #"domain",
        #"problem",
        #"algorithm",
        "unexplained_errors",
        "error",
        "node",
    ]

DIR = Path(__file__).resolve().parent
REPO = DIR.parent
BENCHMARKS_DIR = REPO / "data"

NODE = platform.node()
REMOTE = re.match(r"tetralith\d+.nsc.liu.se|n\d+", NODE)
if REMOTE:
    ENV = TetralithEnvironment(
        setup=TetralithEnvironment.DEFAULT_SETUP,
        memory_per_cpu="11600M",  # 11600M * 32 = 371.2G
        cpus_per_task=32,
        extra_options="#SBATCH -C fat --exclusive\n#SBATCH --account=naiss2023-5-314")
    SUITE = [
        "barman",
        "blocks_3",
        "blocks_4",
        "blocks_4_clear",
        "blocks_4_on",
        "childsnack",
        "delivery",
        "ferry",
        "grid",
        "gripper",
        "hiking",
        "logistics",
        "miconic",
        "reward",
        "rovers",
        "satellite",
        "spanner",
        "visitall",
    ]
    TIME_LIMIT = 60 * 60 * 24 * 1  # 2 days
else:
    ENV = LocalEnvironment(processes=12)
    SUITE = [
        "barman",
        "blocks_3",
        "blocks_4",
        "blocks_4_clear",
        "blocks_4_on",
        "childsnack",
        "delivery",
        "ferry",
        "grid",
        "gripper",
        "hiking",
        "logistics",
        "miconic",
        "reward",
        "rovers",
        "satellite",
        "spanner",
        "visitall",
    ]
    TIME_LIMIT = 10
ATTRIBUTES = [
    "run_dir",
    Attribute("coverage", absolute=True, min_wins=False, scale="linear"),
    Attribute("num_instances", absolute=True, min_wins=False, scale="linear"),
    Attribute("num_final_states", absolute=True, min_wins=False, scale="linear"),
    Attribute("num_total_states", absolute=True, min_wins=False, scale="linear"),
    Attribute("num_1fwl_iterations", absolute=True, min_wins=False, scale="linear"),
    Attribute("num_2fwl_iterations", absolute=True, min_wins=False, scale="linear"),
    Attribute("num_1fwl_total_conflicts", absolute=True, min_wins=False, scale="linear"),
    Attribute("num_2fwl_total_conflicts", absolute=True, min_wins=False, scale="linear"),
    Attribute("num_1fwl_total_value_conflicts", absolute=True, min_wins=True, scale="linear"),
    Attribute("num_2fwl_total_value_conflicts", absolute=True, min_wins=True, scale="linear"),
    Attribute("num_1fwl_total_conflicts_same", absolute=True, min_wins=True, scale="linear"),
    Attribute("num_2fwl_total_conflicts_same", absolute=True, min_wins=True, scale="linear"),
    Attribute("num_1fwl_total_value_conflicts_same", absolute=True, min_wins=True, scale="linear"),
    Attribute("num_2fwl_total_value_conflicts_same", absolute=True, min_wins=True, scale="linear"),
]

MEMORY_LIMIT = 380000

# Create a new experiment.
exp = Experiment(environment=ENV)
# Add custom parser for FF.
exp.add_parser(WLParser())

for domain_name in SUITE:
    ### Additional options:
    run = exp.add_run()
    # Create symbolic links and aliases. This is optional. We
    # could also use absolute paths in add_command().

    run.add_resource("data", BENCHMARKS_DIR / domain_name, symlink=True)
    run.add_resource("main_script", REPO / "main.py", symlink=True)
    # 'ff' binary has to be on the PATH.
    # We could also use exp.add_resource().
    run.add_command(
        "main_script_pairwise_wl",
        [sys.executable, "-u", "{main_script}", "pairwise-wl", "--data-path", f"{domain_name}", "--max-num-states", "1000000"],
        time_limit=TIME_LIMIT,
        memory_limit=MEMORY_LIMIT,
    )
    # AbsoluteReport needs the following properties:
    # 'domain', 'problem', 'algorithm', 'coverage'.
    run.set_property("domain", domain_name)
    run.set_property("problem", domain_name)
    run.set_property("algorithm", "pairwise-wl")
    # BaseReport needs the following properties:
    # 'time_limit', 'memory_limit'.
    run.set_property("time_limit", TIME_LIMIT)
    run.set_property("memory_limit", MEMORY_LIMIT)
    # Every run has to have a unique id in the form of a list.
    # The algorithm name is only really needed when there are
    # multiple algorithms.
    run.set_property("id", ["pairwise-wl", domain_name])

    ### Additional options: --mark-true-goal-atoms
    run = exp.add_run()
    # Create symbolic links and aliases. This is optional. We
    # could also use absolute paths in add_command().

    run.add_resource("data", BENCHMARKS_DIR / domain_name, symlink=True)
    run.add_resource("main_script", REPO / "main.py", symlink=True)
    # 'ff' binary has to be on the PATH.
    # We could also use exp.add_resource().
    run.add_command(
        "main_script_pairwise_wl",
        [sys.executable, "-u", "{main_script}", "pairwise-wl", "--data-path", f"{domain_name}", "--mark-true-goal-atoms", "--max-num-states", "1000000"],
        time_limit=TIME_LIMIT,
        memory_limit=MEMORY_LIMIT,
    )
    # AbsoluteReport needs the following properties:
    # 'domain', 'problem', 'algorithm', 'coverage'.
    run.set_property("domain", domain_name)
    run.set_property("problem", domain_name)
    run.set_property("algorithm", "pairwise-wl-mark-true-goal-atoms")
    # BaseReport needs the following properties:
    # 'time_limit', 'memory_limit'.
    run.set_property("time_limit", TIME_LIMIT)
    run.set_property("memory_limit", MEMORY_LIMIT)
    # Every run has to have a unique id in the form of a list.
    # The algorithm name is only really needed when there are
    # multiple algorithms.
    run.set_property("id", ["pairwise-wl-mark-true-goal-atoms", domain_name])


    ### Additional options: --ignore-counting
    run = exp.add_run()
    # Create symbolic links and aliases. This is optional. We
    # could also use absolute paths in add_command().

    run.add_resource("data", BENCHMARKS_DIR / domain_name, symlink=True)
    run.add_resource("main_script", REPO / "main.py", symlink=True)
    # 'ff' binary has to be on the PATH.
    # We could also use exp.add_resource().
    run.add_command(
        "main_script_pairwise_wl",
        [sys.executable, "-u", "{main_script}", "pairwise-wl", "--data-path", f"{domain_name}", "--ignore-counting", "--max-num-states", "1000000"],
        time_limit=TIME_LIMIT,
        memory_limit=MEMORY_LIMIT,
    )
    # AbsoluteReport needs the following properties:
    # 'domain', 'problem', 'algorithm', 'coverage'.
    run.set_property("domain", domain_name)
    run.set_property("problem", domain_name)
    run.set_property("algorithm", "pairwise-wl-ignore-counting")
    # BaseReport needs the following properties:
    # 'time_limit', 'memory_limit'.
    run.set_property("time_limit", TIME_LIMIT)
    run.set_property("memory_limit", MEMORY_LIMIT)
    # Every run has to have a unique id in the form of a list.
    # The algorithm name is only really needed when there are
    # multiple algorithms.
    run.set_property("id", ["pairwise-wl-ignore-counting", domain_name])

    ### Additional options: --mark-true-goal-atoms --ignore-counting
    run = exp.add_run()
    # Create symbolic links and aliases. This is optional. We
    # could also use absolute paths in add_command().

    run.add_resource("data", BENCHMARKS_DIR / domain_name, symlink=True)
    run.add_resource("main_script", REPO / "main.py", symlink=True)
    # 'ff' binary has to be on the PATH.
    # We could also use exp.add_resource().
    run.add_command(
        "main_script_pairwise_wl",
        [sys.executable, "-u", "{main_script}", "pairwise-wl", "--data-path", f"{domain_name}", "--mark-true-goal-atoms", "--ignore-counting", "--max-num-states", "1000000"],
        time_limit=TIME_LIMIT,
        memory_limit=MEMORY_LIMIT,
    )
    # AbsoluteReport needs the following properties:
    # 'domain', 'problem', 'algorithm', 'coverage'.
    run.set_property("domain", domain_name)
    run.set_property("problem", domain_name)
    run.set_property("algorithm", "pairwise-wl-mark-true-goal-atoms-ignore-counting")
    # BaseReport needs the following properties:
    # 'time_limit', 'memory_limit'.
    run.set_property("time_limit", TIME_LIMIT)
    run.set_property("memory_limit", MEMORY_LIMIT)
    # Every run has to have a unique id in the form of a list.
    # The algorithm name is only really needed when there are
    # multiple algorithms.
    run.set_property("id", ["pairwise-wl-mark-true-goal-atoms-ignore-counting", domain_name])

# Add step that writes experiment files to disk.
exp.add_step("build", exp.build)

# Add step that executes all runs.
exp.add_step("start", exp.start_runs)

exp.add_step("parse", exp.parse)

# Add step that collects properties from run directories and
# writes them to *-eval/properties.
exp.add_fetcher(name="fetch")

# Make a report.
exp.add_report(BaseReport(attributes=ATTRIBUTES), outfile="report.html")

# Parse the commandline and run the specified steps.
exp.run_steps()