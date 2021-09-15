# Why does this file exist, and why not put this in `__main__`?
#
# You might be tempted to import things from `__main__` later,
# but that will cause problems: the code will get executed twice:
#
# - When you run `python -m griffe` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `griffe.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `griffe.__main__` in `sys.modules`.

"""Module that contains the command line application."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from griffe.encoders import Encoder
from griffe.extended_ast import extend_ast
from griffe.extensions import Extensions
from griffe.loader import GriffeLoader
from griffe.logger import get_logger

logger = get_logger(__name__)


def _print_data(data, output_file):
    if output_file is sys.stdout:
        print(data)
    else:
        with open(output_file, "w") as fd:
            print(data, file=fd)


def get_parser() -> argparse.ArgumentParser:
    """
    Return the program argument parser.

    Returns:
        The argument parser for the program.
    """
    parser = argparse.ArgumentParser(prog="griffe")
    parser.add_argument(
        "-s",
        "--search",
        action="append",
        type=Path,
        help="Paths to search packages into.",
    )
    parser.add_argument(
        "-a",
        "--append-search",
        action="store_true",
        help="Whether to append sys.path to specified search paths.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=sys.stdout,
        help="Output file. Supports templating to output each package in its own file, with {{package}}.",
    )
    parser.add_argument("packages", metavar="PACKAGE", nargs="+", help="Packages to find and parse.")
    return parser


def main(args: list[str] | None = None) -> int:
    """
    Run the main program.

    This function is executed when you type `griffe` or `python -m griffe`.

    Arguments:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """
    parser = get_parser()
    opts: argparse.Namespace = parser.parse_args(args)  # type: ignore

    logging.basicConfig(format="%(levelname)-10s %(message)s", level=logging.DEBUG)  # noqa: WPS323

    output = opts.output

    per_package_output = False
    if isinstance(output, str) and output.format(package="package") != output:
        per_package_output = True

    search = opts.search
    if opts.append_search:
        search.extend(sys.path)

    extend_ast()

    extensions = Extensions()
    loader = GriffeLoader(extensions=extensions)
    packages = {}
    success = True

    for package in opts.packages:
        logger.info(f"Loading package {package}")
        try:
            module = loader.load_module(package, search_paths=search)
        except ModuleNotFoundError:
            logger.error(f"Could not find package {package}")
            success = False
        else:
            packages[module.name] = module

    if per_package_output:
        for package_name, data in packages.items():
            serialized = json.dumps(data, cls=Encoder, indent=2, full=True)
            _print_data(serialized, output.format(package=package_name))
    else:
        serialized = json.dumps(packages, cls=Encoder, indent=2, full=True)
        _print_data(serialized, output)

    return 0 if success else 1
