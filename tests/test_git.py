"""Tests for creating a griffe Module from specific commits in a git repository."""

import shutil
from pathlib import Path
from subprocess import run  # noqa: S404

import pytest

from griffe.dataclasses import Module
from griffe.git import load_git
from tests import FIXTURES_DIR

REPO_NAME = "my-repo"
REPO_SOURCE = FIXTURES_DIR / "_repo"
MODULE_NAME = "my_module"


def _copy_contents(src: Path, dst: Path) -> None:
    """Copy *contents* of src into dst.

    Parameters:
        src: the folder whose contents will be copied to dst
        dst: the destination folder
    """
    dst.mkdir(exist_ok=True, parents=True)
    for src_path in src.iterdir():
        dst_path = dst / src_path.name
        if src_path.is_dir():
            _copy_contents(src_path, dst_path)
        else:
            shutil.copy(src_path, dst_path)


@pytest.fixture()
def git_repo(tmp_path: Path) -> Path:
    """Fixture that creates a git repo with multiple tagged versions.

    For each directory in `tests/test_git/_repo/`

        - the contents of the directory will be copied into the temporary repo
        - all files will be added and commited
        - the commit will be tagged with the name of the directory

    To add to these tests (i.e. to simulate change over time), either modify one of
    the files in the existing `v0.1.0`, `v0.2.0` folders, or continue adding new
    version folders following the same pattern.

    Parameters:
        tmp_path: temporary directory fixture

    Returns:
        Path: path to temporary repo.
    """
    repo_path = tmp_path / REPO_NAME
    repo_path.mkdir()
    run(["git", "-C", str(repo_path), "init"])  # noqa: S603,S607
    run(["git", "-C", str(repo_path), "config", "user.name", "Name"])  # noqa: S603,S607
    run(["git", "-C", str(repo_path), "config", "user.email", "my@email.com"])  # noqa: S603,S607
    for tagdir in REPO_SOURCE.iterdir():
        ver = tagdir.name
        _copy_contents(tagdir, repo_path)
        run(["git", "-C", str(repo_path), "add", "."])  # noqa: S603,S607
        run(["git", "-C", str(repo_path), "commit", "-m", f"feat: {ver} stuff"])  # noqa: S603,S607
        run(["git", "-C", str(repo_path), "tag", ver])  # noqa: S603,S607
    return repo_path


def test_load_git(git_repo: Path):  # noqa: WPS442
    """Test that we can load modules from different commits from a git repo.

    Parameters:
        git_repo: temporary git repo
    """
    v1 = load_git(MODULE_NAME, ref="v0.1.0", repo=git_repo)
    v2 = load_git(MODULE_NAME, ref="v0.2.0", repo=git_repo)
    assert isinstance(v1, Module)
    assert isinstance(v2, Module)
    assert v1.attributes["__version__"].value == "'0.1.0'"
    assert v2.attributes["__version__"].value == "'0.2.0'"


def test_load_git_errors(git_repo: Path):  # noqa: WPS442
    """Test that we get informative errors for various invalid inputs.

    Parameters:
        git_repo: temporary git repo
    """
    with pytest.raises(OSError, match="Not a git repository"):
        load_git(MODULE_NAME, ref="v0.2.0", repo="not-a-repo")

    with pytest.raises(RuntimeError, match="Could not create git worktre"):
        load_git(MODULE_NAME, ref="invalid-tag", repo=git_repo)

    with pytest.raises(ModuleNotFoundError, match="No module named 'not_a_real_module'"):
        load_git("not_a_real_module", ref="v0.2.0", repo=git_repo)
