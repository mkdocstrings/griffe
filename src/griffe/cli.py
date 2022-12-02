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
    """Return the program argument parser.

    Returns:
        The argument parser for the program.
    """
    usage = "%(prog)s [GLOBAL_OPTS...] COMMAND [COMMAND_OPTS...]"  # noqa: WPS323 (%-formatting)
    description = "Signatures for entire Python programs. "
    "Extract the structure, the frame, the skeleton of your project, "
    "to generate API documentation or find breaking changes in your API."
    parser = argparse.ArgumentParser(add_help=False, usage=usage, description=description, prog="griffe")

    main_help = "Show this help message and exit. Commands also accept the -h/--help option."
    subcommand_help = "Show this help message and exit."

    global_options = parser.add_argument_group(title="Global options")
    global_options.add_argument("-h", "--help", action="help", help=main_help)

    def add_common_options(subparser):  # noqa: WPS430
        common_options = subparser.add_argument_group(title="Common options")
        common_options.add_argument("-h", "--help", action="help", help=subcommand_help)
        search_options = subparser.add_argument_group(title="Search options")
        search_options.add_argument(
            "-s",
            "--search",
            dest="search_paths",
            action="append",
            type=Path,
            help="Paths to search packages into.",
        )
        loading_options = subparser.add_argument_group(title="Loading options")
        loading_options.add_argument(
            "-e",
            "--extensions",
            default={},
            type=json.loads,
            help="A list of extensions to use.",
        )
        loading_options.add_argument(
            "-X",
            "--no-inspection",
            dest="allow_inspection",
            action="store_false",
            default=True,
            help="Disallow inspection of builtin/compiled/not found modules.",
        )
        debug_options = subparser.add_argument_group(title="Debugging options")
        debug_options.add_argument(
            "-L",
            "--log-level",
            metavar="LEVEL",
            default=DEFAULT_LOG_LEVEL,
            choices=_level_choices,
            type=str.upper,
            help="Set the log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.",
        )

    # ========= SUBPARSERS ========= #
    subparsers = parser.add_subparsers(
        dest="subcommand", title="Commands", metavar="COMMAND", prog="griffe", required=True
    )

    def add_subparser(command: str, text: str, **kwargs) -> argparse.ArgumentParser:  # noqa: WPS430 (nested function)
        return subparsers.add_parser(command, add_help=False, help=text, description=text, **kwargs)

    # ========= DUMP PARSER ========= #
    dump_parser = add_subparser("dump", "Load package-signatures and dump them as JSON.")
    dump_options = dump_parser.add_argument_group(title="Dump options")
    dump_options.add_argument("packages", metavar="PACKAGE", nargs="+", help="Packages to find, load and dump.")
    dump_options.add_argument(
        "-f",
        "--full",
        action="store_true",
        default=False,
        help="Whether to dump full data in JSON.",
    )
    dump_options.add_argument(
        "-o",
        "--output",
        default=sys.stdout,
        help="Output file. Supports templating to output each package in its own file, with `{package}`.",
    )
    dump_options.add_argument(
        "-d",
        "--docstyle",
        dest="docstring_parser",
        default=None,
        type=Parser,
        help="The docstring style to parse.",
    )
    dump_options.add_argument(
        "-D",
        "--docopts",
        dest="docstring_options",
        default={},
        type=json.loads,
        help="The options for the docstring parser.",
    )
    dump_options.add_argument(
        "-y",
        "--sys-path",
        dest="append_sys_path",
        action="store_true",
        help="Whether to append `sys.path` to search paths specified with `-s`.",
    )
    dump_options.add_argument(
        "-r",
        "--resolve-aliases",
        action="store_true",
        help="Whether to resolve aliases.",
    )
    dump_options.add_argument(
        "-I",
        "--resolve-implicit",
        action="store_true",
        help="Whether to resolve implicitely exported aliases as well. "
        "Aliases are explicitely exported when defined in `__all__`.",
    )
    dump_options.add_argument(
        "-U",
        "--resolve-external",
        action="store_true",
        help="Whether to resolve aliases pointing to external/unknown modules (not loaded directly).",
    )
    dump_options.add_argument(
        "-S",
        "--stats",
        action="store_true",
        help="Show statistics at the end.",
    )
    add_common_options(dump_parser)

    # ========= CHECK PARSER ========= #
    check_parser = add_subparser("check", "Check for API breakages or possible improvements.")
    check_options = check_parser.add_argument_group(title="Check options")
    check_options.add_argument("package", metavar="PACKAGE", help="Package to find, load and check, as path.")
    check_options.add_argument(
        "-a",
        "--against",
        metavar="REF",
        help="Older Git reference (commit, branch, tag) to check against. Default: load latest tag.",
    )
    check_options.add_argument(
        "-b",
        "--base-ref",
        metavar="BASE_REF",
        help="Git reference (commit, branch, tag) to check. Default: load current code.",
    )
    check_options.add_argument("-v", "--verbose", action="store_true", help="Verbose output.")
    add_common_options(check_parser)

    return parser


def dump(
    packages: Sequence[str],
    *,
    output: str | IO | None = None,
    full: bool = False,
    docstring_parser: Parser | None = None,
    docstring_options: dict[str, Any] | None = None,
    extensions: Sequence[str | dict[str, Any] | Extension | Type[Extension]] | None = None,
    resolve_aliases: bool = False,
    resolve_implicit: bool = False,
    resolve_external: bool = False,
    search_paths: Sequence[str | Path] | None = None,
    append_sys_path: bool = False,
    allow_inspection: bool = True,
    stats: bool = False,
) -> int:
    """Load packages data and dump it as JSON.

    Parameters:
        packages: The packages to load and dump.
        output: Where to output the JSON-serialized data.
        full: Whether to output full or minimal data.
        docstring_parser: The docstring parser to use. By default, no parsing is done.
        docstring_options: Additional docstring parsing options.
        resolve_aliases: Whether to resolve aliases (indirect objects references).
        resolve_implicit: Whether to resolve every alias or only the explicitly exported ones.
        resolve_external: Whether to load additional, unspecified modules to resolve aliases.
        extensions: The extensions to use.
        search_paths: The paths to search into.
        append_sys_path: Whether to append the contents of `sys.path` to the search paths.
        allow_inspection: Whether to allow inspecting modules when visiting them is not possible.
        stats: Whether to compute and log stats about loading.

    Returns:
        `0` for success, `1` for failure.
    """
    per_package_output = False
    if isinstance(output, str) and output.format(package="package") != output:
        per_package_output = True

    search_paths = list(search_paths) if search_paths else []
    if append_sys_path:
        search_paths.extend(sys.path)

    try:
        loaded_extensions = load_extensions(extensions or ())
    except ExtensionError as error:
        logger.error(error)
        return 1

    loader = _load_packages(
        packages,
        extensions=loaded_extensions,
        search_paths=search_paths,
        docstring_parser=docstring_parser,
        docstring_options=docstring_options,
        resolve_aliases=resolve_aliases,
        resolve_implicit=resolve_implicit,
        resolve_external=resolve_external,
        allow_inspection=allow_inspection,
    )
    data_packages = loader.modules_collection.members

    started = datetime.now()
    if per_package_output:
        for package_name, data in data_packages.items():
            serialized = data.as_json(indent=2, full=full)
            _print_data(serialized, output.format(package=package_name))  # type: ignore[union-attr]
    else:
        serialized = json.dumps(data_packages, cls=JSONEncoder, indent=2, full=full)
        _print_data(serialized, output)
    elapsed = datetime.now() - started

    if stats:
        logger.info(_stats({"time_spent_serializing": elapsed.microseconds, **loader.stats()}))

    return 0 if len(data_packages) == len(packages) else 1


def check(
    package: str | Path,
    against: str | None = None,
    against_path: str | Path | None = None,
    *,
    base_ref: str | None = None,
    extensions: Sequence[str | dict[str, Any] | Extension | Type[Extension]] | None = None,
    search_paths: Sequence[str | Path] | None = None,
    allow_inspection: bool = True,
    verbose: bool = False,
) -> int:
    """Load packages data and dump it as JSON.

    Parameters:
        package: The package to load and check.
        against: Older Git reference (commit, branch, tag) to check against.
        against_path: Path when the "against" reference is checked out.
        base_ref: Git reference (commit, branch, tag) to check.
        extensions: The extensions to use.
        search_paths: The paths to search into.
        allow_inspection: Whether to allow inspecting modules when visiting them is not possible.
        verbose: Use a verbose output.

    Returns:
        `0` for success, `1` for failure.
    """
    colorama.deinit()
    colorama.init()

    search_paths = list(search_paths) if search_paths else []

    against = against or _get_latest_tag(package)
    against_path = against_path or package
    repository = _get_repo_root(against_path)

    try:
        loaded_extensions = load_extensions(extensions or ())
    except ExtensionError as error:
        logger.error(error)
        return 1

    old_package = load_git(
        against_path,
        ref=against,
        repo=repository,
        extensions=loaded_extensions,
        search_paths=search_paths,
        allow_inspection=allow_inspection,
    )
    if base_ref:
        new_package = load_git(
            package,
            ref=base_ref,
            repo=repository,
            extensions=loaded_extensions,
            search_paths=search_paths,
            allow_inspection=allow_inspection,
        )
    else:
        new_package = load(
            package,
            try_relative_path=True,
            extensions=loaded_extensions,
            search_paths=search_paths,
            allow_inspection=allow_inspection,
        )

    if verbose:
        style = ExplanationStyle.VERBOSE
    else:
        style = ExplanationStyle.ONE_LINE
    breakages = list(find_breaking_changes(old_package, new_package))
    for breakage in breakages:
        print(breakage.explain(style=style), file=sys.stderr)
    if breakages:
        return 1
    return 0


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
