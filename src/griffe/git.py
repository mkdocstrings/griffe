"""This module contains the code allowing to load modules from specific git commits.

```python
from griffe.git import load_git

# where `repo` is the folder *containing* `.git`
old_api = load_git("my_module", commit="v0.1.0", repo="path/to/repo")
```
"""
from __future__ import annotations

import os
import shutil
from contextlib import contextmanager
from pathlib import Path
from subprocess import DEVNULL, PIPE, CalledProcessError, check_output, run  # noqa: S404
from tempfile import TemporaryDirectory
from typing import Any, Iterator, Sequence
from uuid import uuid1

from griffe import loader
from griffe.agents.extensions import Extensions
from griffe.collections import LinesCollection, ModulesCollection
from griffe.dataclasses import Module
from griffe.docstrings.parsers import Parser


def _assert_git_repo(repo: str) -> None:
    if not shutil.which("git"):
        raise RuntimeError("Could not find git executable. Please install git.")

    try:
        check_output(["git", "-C", repo, "rev-parse", "--is-inside-work-tree"], stderr=DEVNULL)  # noqa: S603,S607
    except CalledProcessError as err:
        raise OSError(f"Not a git repository: {repo!r}") from err


@contextmanager
def tmp_worktree(commit: str = "HEAD", repo: str | Path = ".") -> Iterator[str]:
    """Context manager that checks out `commit` in `repo` to a temporary worktree.

    Parameters:
        commit: A "commit-ish" - such as a hash or tag.
        repo: Path to the repository (i.e. the directory *containing* the `.git` directory)

    Yields:
        The path to the temporary worktree.

    Raises:
        OSError: If `repo` is not a valid `.git` repository
        RuntimeError: If the `git` executable is unavailable, or if it cannot create a worktree
    """
    repo = str(repo)
    _assert_git_repo(repo)
    with TemporaryDirectory() as td:
        uid = str(uuid1())
        target = os.path.join(td, uid)
        retval = run(  # noqa: S603,S607
            ["git", "-C", repo, "worktree", "add", "-b", uid, target, commit],
            stderr=PIPE,
            stdout=PIPE,
        )
        if retval.returncode:
            raise RuntimeError(f"Could not create git worktree: {retval.stderr.decode()}")

        try:
            yield target
        finally:
            run(["git", "-C", repo, "worktree", "remove", uid], stdout=DEVNULL)  # noqa: S603,S607
            run(["git", "-C", repo, "worktree", "prune"], stdout=DEVNULL)  # noqa: S603,S607
            run(["git", "-C", repo, "branch", "-d", uid], stdout=DEVNULL)  # noqa: S603,S607


def load_git(
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
    """Load and return a module from a specific git commit in `repo`.

    This function will create a temporary
    [git worktree](https://git-scm.com/docs/git-worktree) at the requested `commit`,
    before loading `module` with [`griffe.load`][griffe.loader.load].
    
    This function requires that the `git` executable be installed.

    Parameters:
        module: The module name or path.
        commit: A "commit-ish" - such as a hash or tag.
        repo: Path to the repository (i.e. the directory *containing* the `.git` directory)
        submodules: Whether to recurse on the submodules.
        try_relative_path: Whether to try finding the module as a relative path.
        extensions: The extensions to use.
        search_paths: The paths to search into.
        docstring_parser: The docstring parser to use. By default, no parsing is done.
        docstring_options: Additional docstring parsing options.
        lines_collection: A collection of source code lines.
        modules_collection: A collection of modules.
        allow_inspection: Whether to allow inspecting modules when visiting them is not possible.

    Returns:
        A loaded module.
    """
    kwargs = locals().copy()
    kwargs.pop("commit")
    kwargs.pop("repo")
    with tmp_worktree(commit, repo) as worktree:
        search_paths = list(search_paths) if search_paths else []
        kwargs["search_paths"] = [worktree] + search_paths
        return loader.load(**kwargs)
