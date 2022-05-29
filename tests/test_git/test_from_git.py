import os
import shutil
from pathlib import Path
from subprocess import run


import pytest

from griffe.dataclasses import Module
from griffe.git import git_load

REPO_NAME = "my-repo"
REPO_SOURCE = Path(__file__).parent / "_repo"
MODULE_NAME = "my_module"


def _copy_contents(src: Path, dst: Path):
    dst.mkdir(exist_ok=True, parents=True)
    for src_path in src.iterdir():
        dst_path = dst / src_path.name
        if src_path.is_dir():
            _copy_contents(src_path, dst_path)
        else:
            shutil.copy(src_path, dst_path)


@pytest.fixture
def git_repo(tmp_path: Path):
    repo_path = tmp_path / REPO_NAME
    repo_path.mkdir()
    run(["git", "-C", str(repo_path), "init"])
    run(["git", "-C", str(repo_path), "config", "user.name", "Name"])
    run(["git", "-C", str(repo_path), "config", "user.email", "my@email.com"])
    for tagdir in REPO_SOURCE.glob("v*"):
        ver = tagdir.name
        _copy_contents(tagdir, repo_path)
        run(["git", "-C", str(repo_path), "add", "."])
        run(["git", "-C", str(repo_path), "commit", "-m", f"feat: {ver} stuff"])
        run(["git", "-C", str(repo_path), "tag", ver])
    return repo_path


def test_git_load(git_repo):
    v1 = git_load(MODULE_NAME, commit="v0.1.0", repo=git_repo)
    v2 = git_load(MODULE_NAME, commit="v0.2.0", repo=git_repo)
    assert isinstance(v1, Module)
    assert isinstance(v2, Module)
    assert v1.attributes["__version__"].value == "'0.1.0'"
    assert v2.attributes["__version__"].value == "'0.2.0'"


def test_git_load_not_a_repo():
    with pytest.raises(ValueError) as e:
        git_load(MODULE_NAME, commit="v0.2.0", repo="not-a-repo")
    assert "Not a git repository" in str(e.value)  # noqa: WPS441


def test_git_load_not_a_commit(git_repo):
    with pytest.raises(RuntimeError) as e:
        git_load(MODULE_NAME, commit="invalid-tag", repo=git_repo)
    assert "Could not create git worktre" in str(e.value)  # noqa: WPS441


def test_git_load_not_a_module(git_repo):
    with pytest.raises(ModuleNotFoundError) as e:
        git_load("not_a_real_module", commit="v0.2.0", repo=git_repo)
    assert "No module named 'not_a_real_module'" in str(e.value)  # noqa: WPS441
