#!/usr/bin/env python

import argparse

from pathlib import Path 

from src.exact.driver import Driver


def add_pddl_options(arg_parser: argparse.ArgumentParser):
    arg_parser.add_argument("--domain_file_path", required=True, help="The path to the domain file.")
    arg_parser.add_argument("--problem_file_path", required=True, help="The path to the problem file.")


def add_verbosity_option(arg_parser: argparse.ArgumentParser):
    log_levels = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]
    level_help = "Set log level for {0}. Allowed values: {1}".format
    arg_parser.add_argument("--verbosity", type=str, choices=log_levels, default="INFO", help=level_help("src", log_levels))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Abstraction generator.")

    # Root parser: type
    subparsers = parser.add_subparsers(dest="type", required=True, help="Abstraction type command help.")

    # Sub parser 1: exact
    exact_parser = subparsers.add_parser("exact", help="Exact abstraction generator.")
    add_pddl_options(exact_parser)
    add_verbosity_option(exact_parser)

    # Sub parser 2: wl
    wl_parser = subparsers.add_parser("wl", help="k-WL abstraction generator.")
    add_pddl_options(wl_parser)
    add_verbosity_option(wl_parser)
    wl_parser.add_argument("-k", "--dimension", type=int, help="Dimension of Weisfeiler-Leman", required=True)

    args = parser.parse_args()

    # Run the abstraction generator
    if args.type == "exact":
        driver = Driver(
            Path(args.domain_file_path).absolute(), 
            Path(args.problem_file_path).absolute(),
            args.verbosity) 
        driver.run()
    elif args.type == "wl":
        pass
