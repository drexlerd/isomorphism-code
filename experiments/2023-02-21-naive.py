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
        partition="tetralith",
        email="",
        memory_per_cpu="3G",
        cpus_per_task=1,
        setup=TetralithEnvironment.DEFAULT_SETUP,
        extra_options="#SBATCH --account=snic2022-5-341")
    SUITE = ["gripper"]
    TIME_LIMIT = 3 * 3600
else:
    ENV = LocalEnvironment(processes=4)
    SUITE = ["gripper:p-1-0.pddl"]
    TIME_LIMIT = 180
ATTRIBUTES = [
    Attribute("num_states", absolute=True, min_wins=True, scale="linear"),
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

MEMORY_LIMIT = (16 * 3000) * 0.98

# Create a new experiment.
exp = Experiment(environment=ENV)
# Add custom parser for FF.
exp.add_parser(IsomorphismParser())

#exp.add_resource("main_script", REPO / "main.py", symlink=True)

for task in suites.build_suite(BENCHMARKS_DIR, SUITE):
    for complexity in [10]:
        run = exp.add_run()
        # Create symbolic links and aliases. This is optional. We
        # could also use absolute paths in add_command().
        run.add_resource("domain", task.domain_file, symlink=True)
        run.add_resource("problem", task.problem_file, symlink=True)
        # run.add_resource("main_script", REPO / "main.py", symlink=True)
        # 'ff' binary has to be on the PATH.
        # We could also use exp.add_resource().
        run.add_command(
            "main_script_exact",
            ["python3", REPO / "main.py", "exact", "--domain_file_path", "{domain}", "--problem_file_path", "{problem}"],
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