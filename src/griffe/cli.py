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
import subprocess  # noqa: S404
import sys
from datetime import datetime
from pathlib import Path
from typing import IO, Any, Callable, Sequence, Type

import colorama

from griffe.agents.extensions import Extension, Extensions
from griffe.agents.extensions.base import load_extensions
from griffe.diff import ExplanationStyle, find_breaking_changes
from griffe.docstrings.parsers import Parser
from griffe.encoders import JSONEncoder
from griffe.exceptions import ExtensionError
from griffe.git import load_git
from griffe.loader import GriffeLoader, load  # noqa: WPS347
from griffe.logger import get_logger

DEFAULT_LOG_LEVEL = os.getenv("GRIFFE_LOG_LEVEL", "INFO").upper()
logger = get_logger(__name__)


def _print_data(data: str, output_file: str | IO | None):
    if isinstance(output_file, str):
        with open(output_file, "w") as fd:
            print(data, file=fd)
    else:
        if output_file is None:
            output_file = sys.stdout
        print(data, file=output_file)


def _get_latest_tag(path: str | Path) -> str:
    if isinstance(path, str):
        path = Path(path)
    if not path.is_dir():
        path = path.parent
    output = subprocess.check_output(  # noqa: S603,S607
        ["git", "describe", "--tags", "--abbrev=0"],
        cwd=path,
    )
    return output.decode().strip()


def _get_repo_root(path: str | Path) -> str:
    if isinstance(path, str):
        path = Path(path)
    if not path.is_dir():
        path = path.parent
    output = subprocess.check_output(  # noqa: S603,S607
        ["git", "rev-parse", "--show-toplevel"],
        cwd=path,
    )
    return output.decode().strip()


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
    stubs = per_ext[".pyi"]
    compiled = modules - builtin - regular - stubs
    lines.append("")
    lines.append(f"Total number of lines: {stats['lines']}")
    lines.append("")
    lines.append("Modules")
    lines.append(f"  Builtin: {builtin}")
    lines.append(f"  Compiled: {compiled}")
    lines.append(f"  Regular: {regular}")
    lines.append(f"  Stubs: {stubs}")
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
    *,
    extensions: Extensions | None,
    search_paths: Sequence[str | Path],
    docstring_parser: Parser | None,
    docstring_options: dict[str, Any] | None,
    resolve_aliases: bool = True,
    resolve_implicit: bool = False,
    resolve_external: bool = False,
    allow_inspection: bool = True,
) -> GriffeLoader:
    loader = GriffeLoader(
        extensions=extensions,
        search_paths=search_paths,
        docstring_parser=docstring_parser,
        docstring_options=docstring_options,
        allow_inspection=allow_inspection,
    )
    for package in packages:
        if not package:
            logger.debug("Empty package name, continuing")
            continue
        logger.info(f"Loading package {package}")
        try:
            loader.load_module(package)
        except ModuleNotFoundError as error:
            logger.error(f"Could not find package {package}: {error}")
        except ImportError as error:
            logger.error(f"Tried but could not import package {package}: {error}")
    logger.info("Finished loading packages")
    if resolve_aliases:
        logger.info("Starting alias resolution")
        unresolved, iterations = loader.resolve_aliases(implicit=resolve_implicit, external=resolve_external)
        if unresolved:
            logger.info(f"{len(unresolved)} aliases were still unresolved after {iterations} iterations")
        else:
            logger.info(f"All aliases were resolved after {iterations} iterations")
    return loader


_level_choices = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def get_parser() -> argparse.ArgumentParser:
    """Return the CLI argument parser.

    Returns:
        An argparse parser.
    """
    return argparse.ArgumentParser(prog="griffe")


def main(args: Optional[List[str]] = None) -> int:
    """Run the main program.

    This function is executed when you type `griffe` or `python -m griffe`.

    Parameters:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """
    parser = get_parser()
    opts: argparse.Namespace = parser.parse_args(args)
    opts_dict = opts.__dict__
    subcommand = opts_dict.pop("subcommand")

    log_level = opts_dict.pop("log_level", DEFAULT_LOG_LEVEL)
    try:
        level = getattr(logging, log_level)
    except AttributeError:
        choices = "', '".join(_level_choices)
        print(
            f"griffe: error: invalid log level '{log_level}' (choose from '{choices}')",
            file=sys.stderr,
        )
        return 1
    else:
        logging.basicConfig(format="%(levelname)-10s %(message)s", level=level)  # noqa: WPS323

    commands: dict[str, Callable[..., int]] = {"check": check, "dump": dump}
    return commands[subcommand](**opts_dict)
