#! /usr/bin/env python

import argparse
import sys

from pathlib import Path

print(sys.executable)

def add_max_num_states_options(arg_parser: argparse.ArgumentParser):
    arg_parser.add_argument("--max-num-states", default=100_000, help="The maximum number of states.", type=int)

def add_verbosity_option(arg_parser: argparse.ArgumentParser):
    log_levels = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]
    level_help = "Set log level for {0}. Allowed values: {1}".format
    arg_parser.add_argument("--verbosity", type=str, choices=log_levels, default="INFO", help=level_help("src", log_levels))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Abstraction generator.")

    # Root parser: type
    subparsers = parser.add_subparsers(dest="type", required=True, help="Abstraction type command help.")

    # Sub parser 1: pairwise-wl
    wl_parser = subparsers.add_parser("wl", help="k-WL abstraction generator.")
    wl_parser.add_argument("--data-path", required=True, help="The path to the domain file.")
    wl_parser.add_argument("--no-decoding-table", action="store_true", help="Certificate comparison without decoding table")
    add_verbosity_option(wl_parser)
    add_max_num_states_options(wl_parser)

    args = parser.parse_args()

    # Run the abstraction generator
    driver = None
    if args.type == "wl":
        from src.wl_analysis import Driver
        driver = Driver(
            Path(args.data_path).absolute(),
            args.verbosity,
            args.max_num_states,
            args.no_decoding_table)

    # Run the configuration
    driver.run()
