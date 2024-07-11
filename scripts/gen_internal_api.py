"""Extract the first comment block from a Python module."""

import os
from pathlib import Path
from textwrap import dedent


def _comment_block(module: Path) -> str:
    lines = []
    with module.open() as file:
        for line in file:
            if line.startswith("#"):
                lines.append(line[1:])
            else:
                break
    return dedent("".join(lines))


def _render_internal_api(path: Path, heading_level: int = 4) -> None:
    for module in sorted(path.iterdir()):
        if module.name in ("__main__.py", "__init__.py"):
            continue
        if module.suffix == ".py":
            print(f"{'#' * heading_level} `{module.name}`\n")
            print(_comment_block(module))
        elif module.is_dir() and module.joinpath("__init__.py").exists():
            print(f"{'#' * heading_level} `{module.name}`\n")
            print(_comment_block(module / "__init__.py"))
            _render_internal_api(module, heading_level + 1)


def render_internal_api(heading_level: int = 4) -> None:
    """Render Griffe's internal API documentation.

    This function prints Markdown headings, and the contents of the first comment block of a module,
    for all modules in our internal API.

    Parameters:
        heading_level: The initial level of Markdown headings.
    """
    root = Path(os.environ["MKDOCS_CONFIG_DIR"])
    src = root / "src"
    internal_api = src / "_griffe"
    _render_internal_api(internal_api, heading_level)
