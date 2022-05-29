from __future__ import annotations

import os
import shutil
from contextlib import contextmanager
from pathlib import Path
from subprocess import DEVNULL, CalledProcessError, check_output, run
from tempfile import TemporaryDirectory
from typing import Any, Iterator, Sequence
from uuid import uuid1

from griffe.agents.extensions import Extensions
from griffe.collections import LinesCollection, ModulesCollection
from griffe.dataclasses import Module
from griffe.docstrings.parsers import Parser
from griffe.loader import load


def _assert_git_repo(repo: str) -> None:
    if not shutil.which("git"):
        raise RuntimeError("Could not find git executable. Please install git.")

    try:
        check_output(["git", "-C", repo, "rev-parse", "--is-inside-work-tree"], stderr=DEVNULL)
    except CalledProcessError as e:
        raise ValueError(f"Not a git repository: {repo!r}") from e


@contextmanager
def tmp_worktree(commit: str = "HEAD", repo: str | Path = ".") -> Iterator[str]:
    repo = str(repo)
    _assert_git_repo(repo)
    with TemporaryDirectory() as td:
        _name = str(uuid1())
        target = os.path.join(td, _name)
        run(
            ["git", "-C", repo, "worktree", "add", "-b", _name, target, commit],
            stdout=DEVNULL,
            stderr=DEVNULL,
        )
        try:
            yield target
        finally:
            run(["git", "-C", repo, "worktree", "remove", _name], stdout=DEVNULL)
            run(["git", "-C", repo, "worktree", "prune"], stdout=DEVNULL)
            run(["git", "-C", repo, "branch", "-d", _name], stdout=DEVNULL)


def git_load(
    module: str | Path,
    commit: str = "HEAD",
    repo: str | Path = ".",
    submodules: bool = True,
    try_relative_path: bool = True,
    extensions: Extensions | None = None,
    search_paths: Sequence[str | Path] | None = None,
    docstring_parser: Parser | None = None,
    docstring_options: dict[str, Any] | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
    allow_inspection: bool = True,
) -> Module:
    """Load and return a module from a specific git commit."""
    kwargs = {k: v for k, v in locals().items() if k not in {"commit", "repo"}}
    with tmp_worktree(commit, repo) as worktree:
        search_paths = list(search_paths) if search_paths else []
        kwargs["search_paths"] = [worktree] + search_paths
        return load(**kwargs)
