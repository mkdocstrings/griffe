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
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

from griffe.agents.extensions import Extensions
from griffe.agents.extensions.base import load_extensions
from griffe.docstrings.parsers import Parser
from griffe.encoders import JSONEncoder
from griffe.exceptions import ExtensionError
from griffe.loader import GriffeLoader
from griffe.logger import get_logger

logger = get_logger(__name__)


def _print_data(data: str, output_file: str):
    if output_file is sys.stdout:
        print(data)
    else:
        with open(output_file, "w") as fd:
            print(data, file=fd)


def _stats(stats):
    lines = []
    packages = stats["packages"]
    modules = stats["modules"]
    classes = stats["classes"]
    functions = stats["functions"]
    attributes = stats["attributes"]
    objects = sum((modules, classes, functions, attributes))
    lines.append("Statistics")
    lines.append("---------------------")
    lines.append("Number of loaded objects")
    lines.append(f"  Modules: {modules}")
    lines.append(f"  Classes: {classes}")
    lines.append(f"  Functions: {functions}")
    lines.append(f"  Attributes: {attributes}")
    lines.append(f"  Total: {objects} across {packages} packages")
    per_ext = stats["modules_by_extension"]
    builtin = per_ext[""]
    regular = per_ext[".py"]
    compiled = modules - builtin - regular
    lines.append("")
    lines.append(f"Total number of lines: {stats['lines']}")
    lines.append("")
    lines.append("Modules")
    lines.append(f"  Builtin: {builtin}")
    lines.append(f"  Compiled: {compiled}")
    lines.append(f"  Regular: {regular}")
    lines.append("  Per extension:")
    for ext, number in sorted(per_ext.items()):
        if ext:
            lines.append(f"    {ext}: {number}")
    visit_time = stats["time_spent_visiting"] / 1000
    inspect_time = stats["time_spent_inspecting"] / 1000
    total_time = visit_time + inspect_time
    visit_percent = visit_time / total_time * 100
    inspect_percent = inspect_time / total_time * 100
    try:
        visit_time_per_module = visit_time / regular
    except ZeroDivisionError:
        visit_time_per_module = 0
    inspected_modules = builtin + compiled
    try:
        inspect_time_per_module = visit_time / inspected_modules
    except ZeroDivisionError:
        inspect_time_per_module = 0
    lines.append("")
    lines.append(
        f"Time spent visiting modules ({regular}): "
        f"{visit_time}ms, {visit_time_per_module:.02f}ms/module ({visit_percent:.02f}%)"
    )
    lines.append(
        f"Time spent inspecting modules ({inspected_modules}): "
        f"{inspect_time}ms, {inspect_time_per_module:.02f}ms/module ({inspect_percent:.02f}%)"
    )
    serialize_time = stats["time_spent_serializing"] / 1000
    serialize_time_per_module = serialize_time / modules
    lines.append(f"Time spent serializing: " f"{serialize_time}ms, {serialize_time_per_module:.02f}ms/module")
    return "\n".join(lines)


def _load_packages(
    packages: Sequence[str],
    extensions: Extensions | None,
    search_paths: Sequence[str],
    docstring_parser: Parser | None,
    docstring_options: dict[str, Any],
    resolve_aliases: bool = True,
    only_exported: bool = True,
    only_known_modules: bool = True,
):
    loader = GriffeLoader(
        extensions=extensions,
        search_paths=search_paths,
        docstring_parser=docstring_parser,
        docstring_options=docstring_options,
    )
    for package in packages:
        logger.info(f"Loading package {package}")
        try:
            loader.load_module(package)
        except ModuleNotFoundError as error:
            logger.error(f"Could not find package {package}: {error}")
        except ImportError as error:
            logger.error(f"Tried but could not import package {package}: {error}")
    logger.info("Finished loading packages, starting alias resolution")
    if resolve_aliases:
        unresolved, iterations = loader.resolve_aliases(only_exported, only_known_modules)
        if unresolved:
            logger.info(f"{len(unresolved)} aliases were still unresolved after {iterations} iterations")
        else:
            logger.info(f"All aliases were resolved after {iterations} iterations")
    return loader


_level_choices = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def get_parser() -> argparse.ArgumentParser:
    """Return the program argument parser.

    Returns:
        The argument parser for the program.
    """
    parser = argparse.ArgumentParser(prog="griffe", add_help=False)
    parser.add_argument(
        "-A",
        "--async",
        action="store_true",
        help="Whether to read files on disk asynchronously. "
        "Very large projects with many files will be processed faster. "
        "Small projects with a few files will not see any speed up.",
    )
    parser.add_argument(
        "-y",
        "--sys-path",
        action="store_true",
        help="Whether to append sys.path to search paths specified with -s.",
    )
    parser.add_argument(
        "-d",
        "--docstyle",
        default=None,
        type=Parser,
        help="The docstring style to parse.",
    )
    parser.add_argument(
        "-D",
        "--docopts",
        default={},
        type=json.loads,
        help="The options for the docstring parser.",
    )
    parser.add_argument(
        "-e",
        "--extensions",
        default={},
        type=json.loads,
        help="A list of extensions to use.",
    )
    parser.add_argument(
        "-f",
        "--full",
        action="store_true",
        default=False,
        help="Whether to dump full data in JSON.",
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        help="Show this help message and exit.",
    )
    parser.add_argument(
        "-L",
        "--log-level",
        metavar="LEVEL",
        default=os.getenv("GRIFFE_LOG_LEVEL", "INFO").upper(),
        choices=_level_choices,
        type=str.upper,
        help="Set the log level: DEBUG, INFO, WARNING, ERROR, CRITICAL.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=sys.stdout,
        help="Output file. Supports templating to output each package in its own file, with {package}.",
    )
    parser.add_argument(
        "-r",
        "--resolve-aliases",
        action="store_true",
        help="Whether to resolve aliases.",
    )
    parser.add_argument(
        "-I",
        "--resolve-implicit",
        action="store_true",
        help="Whether to resolve implicitely exported aliases as well. "
        "Aliases are explicitely exported when defined in '__all__'.",
    )
    parser.add_argument(
        "-U",
        "--resolve-external",
        action="store_true",
        help="Whether to resolve aliases pointing to external/unknown modules (not loaded directly).",
    )
    parser.add_argument(
        "-s",
        "--search",
        action="append",
        type=Path,
        help="Paths to search packages into.",
    )
    parser.add_argument(
        "-S",
        "--stats",
        action="store_true",
        help="Show statistics at the end.",
    )

    parser.add_argument("packages", metavar="PACKAGE", nargs="+", help="Packages to find and parse.")
    return parser


def main(args: list[str] | None = None) -> int:  # noqa: WPS231
    """Run the main program.

    This function is executed when you type `griffe` or `python -m griffe`.

    Parameters:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """
    parser = get_parser()
    opts: argparse.Namespace = parser.parse_args(args)

    try:
        level = getattr(logging, opts.log_level)
    except AttributeError:
        choices = "', '".join(_level_choices)
        print(
            f"griffe: error: env var GRIFFE_LOG_LEVEL: invalid level '{opts.log_level}' (choose from '{choices}')",
            file=sys.stderr,
        )
        sys.exit(1)

    logging.basicConfig(format="%(levelname)-10s %(message)s", level=level)  # noqa: WPS323

    output = opts.output

    per_package_output = False
    if isinstance(output, str) and output.format(package="package") != output:
        per_package_output = True

    search = opts.search
    if opts.sys_path:
        search.extend(sys.path)

    try:
        extensions = load_extensions(opts.extensions)
    except ExtensionError as error:
        print(f"griffe: error: {error}", file=sys.stderr)
        return 1

    loader = _load_packages(
        opts.packages,
        extensions,
        search,
        opts.docstyle,
        opts.docopts,
        opts.resolve_aliases,
        not opts.resolve_implicit,
        not opts.resolve_external,
    )
    packages = loader.modules_collection.members

    started = datetime.now()
    if per_package_output:
        for package_name, data in packages.items():
            serialized = json.dumps(data, cls=JSONEncoder, indent=2, full=opts.full)
            _print_data(serialized, output.format(package=package_name))
    else:
        serialized = json.dumps(packages, cls=JSONEncoder, indent=2, full=opts.full)
        _print_data(serialized, output)
    elapsed = datetime.now() - started

    if opts.stats:
        logger.info(_stats({"time_spent_serializing": elapsed.microseconds, **loader.stats()}))

    return 0 if len(packages) == len(opts.packages) else 1
