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

from griffe.encoders import Encoder
from griffe.extensions.base import Extensions
from griffe.loader import GriffeLoader


def get_parser() -> argparse.ArgumentParser:
    """
    Return the program argument parser.

    Returns:
        The argument parser for the program.
    """
    parser = argparse.ArgumentParser(prog="griffe")
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

    extensions = Extensions()
    loader = GriffeLoader(extensions=extensions)
    modules = []
    for package in opts.packages:
        modules.append(loader.load_module(package))
    serialized = json.dumps(modules, cls=Encoder, indent=2, full=True)
    print(serialized)
    return 0
