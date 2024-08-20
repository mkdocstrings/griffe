"""Render docs for our program structure."""

import os
import subprocess
from io import StringIO
from pathlib import Path
from textwrap import dedent
from unittest.mock import MagicMock

from code2flow import code2flow, engine, model

engine.logging = MagicMock()


model.TRUNK_COLOR = "#fca311"
model.LEAF_COLOR = "#98c1d9"
model.EDGE_COLORS = ["#b8b8ff"] * 8
model.NODE_COLOR = "#e5e5e5"


def _render_call_graph(module: Path) -> None:
    buffer = StringIO()
    code2flow(str(module), buffer)
    try:
        svg = subprocess.check_output(["dot", "-Tsvg"], input=buffer.getvalue(), text=True)  # noqa: S603, S607
    except subprocess.CalledProcessError:
        # The subprocess dies with SIGSEGV in GHA...
        return
    if 'class="node"' not in svg:
        print()
    else:
        print(f'<div class="interactiveSVG code2flow">{svg}</div>')


def _comment_block(module: Path) -> str:
    lines = []
    with module.open() as file:
        for line in file:
            if line.startswith("#"):
                lines.append(line[1:])
            else:
                break
    return dedent("".join(lines))


def _render_api(path: Path, root: Path, heading_level: int = 4) -> None:
    for module in sorted(path.iterdir()):
        if module.name in ("__main__.py", "__init__.py"):
            continue
        rel_path = str(module.relative_to(root).with_suffix("")).replace("/", "-")
        if module.suffix == ".py":
            print(f"{'#' * heading_level} `{module.name}` {{#{rel_path}}}\n")
            print(_comment_block(module))
            _render_call_graph(module)
        elif module.is_dir() and module.joinpath("__init__.py").exists():
            print(f"{'#' * heading_level} `{module.name}` {{#{rel_path}}}\n")
            print(_comment_block(module / "__init__.py"))
            _render_api(module, root, heading_level + 1)


def render_internal_api(heading_level: int = 4) -> None:
    """Render Griffe's internal API's structure docs.

    This function prints Markdown headings, and the contents of the first comment block of a module,
    for all modules in our internal API.

    Parameters:
        heading_level: The initial level of Markdown headings.
    """
    root = Path(os.environ["MKDOCS_CONFIG_DIR"])
    src = root / "src"
    internal_api = src / "_griffe"
    print(_comment_block(internal_api / "__init__.py"))
    _render_api(internal_api, internal_api, heading_level)


def render_public_api(heading_level: int = 4) -> None:
    """Render Griffe's main module's docs.

    Parameters:
        heading_level: The initial level of Markdown headings.
    """
    root = Path(os.environ["MKDOCS_CONFIG_DIR"])
    src = root / "src"
    public_api = src / "griffe"
    print(f"{'#' * heading_level} `griffe`\n")
    print(_comment_block(public_api / "__init__.py"))


def render_entrypoint(heading_level: int = 4) -> None:
    """Render Griffe's main entrypoint's docs.

    Parameters:
        heading_level: The initial level of Markdown headings.
    """
    root = Path(os.environ["MKDOCS_CONFIG_DIR"])
    src = root / "src"
    public_api = src / "griffe"
    print(f"{'#' * heading_level} `griffe.__main__`\n")
    print(_comment_block(public_api / "__main__.py"))
