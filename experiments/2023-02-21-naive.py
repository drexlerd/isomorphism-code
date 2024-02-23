#! /usr/bin/env python
import platform
import re

from pathlib import Path

from downward import suites
from downward.reports.absolute import AbsoluteReport
from lab.environments import TetralithEnvironment, LocalEnvironment
from lab.experiment import Experiment
from lab.reports import Attribute, geometric_mean
from ismorphism_parser import IsomorphismParser


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

DIR = Path(__file__).resolve().parent
REPO = DIR.parent
BENCHMARKS_DIR = REPO / "data"

NODE = platform.node()
REMOTE = re.match(r"tetralith\d+.nsc.liu.se|n\d+", NODE)
if REMOTE:
    ENV = TetralithEnvironment(
        memory_per_cpu="3G",
        setup=TetralithEnvironment.DEFAULT_SETUP,
        extra_options="#SBATCH --account=naiss2023-5-314")
    SUITE = [
        "barman",
        "blocks_3",
        "blocks_4",
        "blocks_4_clear",
        "blocks_4_on",
        "childsnack",
        "delivery",
        "grid",
        "gripper",
        "logistics",
        "miconic",
        "reward",
        "spanner",
        "visitall",
    ]
    TIME_LIMIT = 900
else:
    ENV = LocalEnvironment(processes=4)
    SUITE = [
        "barman:p-2-2-2-0.pddl",
        "blocks_3:p-1-0.pddl",
        "blocks_4:p-1-0.pddl",
        "blocks_4_clear:p-1-0.pddl",
        "blocks_4_on:p-1-0.pddl",
        "childsnack:p-1-1.0-0.0-1-0.pddl",
        "delivery:instance_1_1_1_0.pddl",
        "grid:p-0-0-100-1-3-3-0.pddl",
        "gripper:p-1-0.pddl",
        "logistics:p-2-2-2-2-2-0.pddl",
        "miconic:p-2-1-0.pddl",
        "reward:instance_2x2_0.pddl",
        "spanner:p-1-1-1-0.pddl",
        "visitall:p-1-0.5-2-0.pddl",
    ]
    TIME_LIMIT = 10
ATTRIBUTES = [
    "run_dir",
    Attribute("num_states", absolute=True, min_wins=True, scale="linear"),
    Attribute("num_generated_states", absolute=True, min_wins=True, scale="linear"),
    Attribute("num_transitions", absolute=True, min_wins=True, scale="linear"),
    Attribute("num_deadends", absolute=True, min_wins=True, scale="linear"),
    Attribute("num_goals", absolute=True, min_wins=True, scale="linear"),
    Attribute("num_vertices_dec_graph", absolute=True, min_wins=True, scale="linear"),
    Attribute("num_vertices_dvc_graph", absolute=True, min_wins=True, scale="linear"),
    Attribute("max_num_edges_dec_graph", absolute=True, min_wins=True, scale="linear"),
    Attribute("max_num_edges_dvc_graph", absolute=True, min_wins=True, scale="linear"),
    Attribute("num_equivalence_classes", absolute=True, min_wins=True, scale="linear"),
    Attribute("time_total", absolute=True, min_wins=True, scale="linear"),
    Attribute("time_per_state", absolute=True, min_wins=True, scale="linear"),

]

MEMORY_LIMIT = 3000

# Create a new experiment.
exp = Experiment(environment=ENV)
# Add custom parser for FF.
exp.add_parser(IsomorphismParser())

#exp.add_resource("main_script", REPO / "main.py", symlink=True)

for task in suites.build_suite(BENCHMARKS_DIR, SUITE):
    run = exp.add_run()
    # Create symbolic links and aliases. This is optional. We
    # could also use absolute paths in add_command().
    run.add_resource("domain", task.domain_file, symlink=True)
    run.add_resource("problem", task.problem_file, symlink=True)
    run.add_resource("main_script", REPO / "main.py", symlink=True)
    # 'ff' binary has to be on the PATH.
    # We could also use exp.add_resource().
    run.add_command(
        "main_script_exact",
        ["python", "{main_script}", "exact", "--domain_file_path", "{domain}", "--problem_file_path", "{problem}", "--enable-pruning"],
        time_limit=TIME_LIMIT,
        memory_limit=MEMORY_LIMIT,
    )
    # AbsoluteReport needs the following properties:
    # 'domain', 'problem', 'algorithm', 'coverage'.
    run.set_property("domain", task.domain)
    run.set_property("problem", task.problem)
    run.set_property("algorithm", "exact")
    # BaseReport needs the following properties:
    # 'time_limit', 'memory_limit'.
    run.set_property("time_limit", TIME_LIMIT)
    run.set_property("memory_limit", MEMORY_LIMIT)
    # Every run has to have a unique id in the form of a list.
    # The algorithm name is only really needed when there are
    # multiple algorithms.
    run.set_property("id", ["exact", task.domain, task.problem])

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