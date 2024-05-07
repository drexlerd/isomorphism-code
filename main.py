#! /usr/bin/env python

import argparse
import sys

from pathlib import Path


print(sys.executable)


def add_pddl_options(arg_parser: argparse.ArgumentParser):
    arg_parser.add_argument("--domain_file_path", required=True, help="The path to the domain file.")
    arg_parser.add_argument("--problem_file_path", required=True, help="The path to the problem file.")


def add_verbosity_option(arg_parser: argparse.ArgumentParser):
    log_levels = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]
    level_help = "Set log level for {0}. Allowed values: {1}".format
    arg_parser.add_argument("--verbosity", type=str, choices=log_levels, default="INFO", help=level_help("src", log_levels))


def add_dump_dot_option(arg_parser: argparse.ArgumentParser):
    arg_parser.add_argument("--dump-dot", action="store_true", help="If specified, the graph dot representations will be written to files.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Abstraction generator.")

    # Root parser: type
    subparsers = parser.add_subparsers(dest="type", required=True, help="Abstraction type command help.")

    # Sub parser 1: exact
    exact_parser = subparsers.add_parser("exact", help="Exact abstraction generator.")
    add_pddl_options(exact_parser)
    add_verbosity_option(exact_parser)
    add_dump_dot_option(exact_parser)
    exact_parser.add_argument("--enable-pruning", action="store_true", help="If specified, only a single representative for each equivalence is kept in a breadth-first-search.")

    # Sub parser 2: wl
    wl_parser = subparsers.add_parser("wl", help="k-WL abstraction generator.")
    add_pddl_options(wl_parser)
    add_verbosity_option(wl_parser)
    add_dump_dot_option(wl_parser)
    wl_parser.add_argument("--ignore-counting", action="store_true", help="Disallow counting quantifiers.")
    wl_parser.add_argument("--mark-true-goal-atoms", action="store_true", help="If specified, mark true and false goal atoms.")
    wl_parser.add_argument("--terminate-early", action="store_true", help="If specified, terminate if colors distinguish partitions.")

    # Sub parser 3: gnn
    gnn_parser = subparsers.add_parser("gnn", help="GNN trainer.")
    add_pddl_options(gnn_parser)
    add_verbosity_option(gnn_parser)

    args = parser.parse_args()

    # Run the abstraction generator
    if args.type == "exact":
        from src.exact import Driver
        driver = Driver(
            Path(args.domain_file_path).absolute(),
            Path(args.problem_file_path).absolute(),
            args.verbosity,
            args.dump_dot,
            args.enable_pruning)
    elif args.type == "wl":
        from src.wl_analysis import Driver
        driver = Driver(
            Path(args.domain_file_path).absolute(),
            Path(args.problem_file_path).absolute(),
            args.verbosity,
            args.ignore_counting,
            args.mark_true_goal_atoms)
    elif args.type == "gnn":
        from src.gnn import Driver
        driver = Driver(
            Path(args.domain_file_path).absolute(),
            Path(args.problem_file_path).absolute(),
            args.verbosity)

    # Run the configuration
    driver.run()
