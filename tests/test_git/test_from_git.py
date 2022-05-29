import os
import shutil
from pathlib import Path

import pytest

from griffe.dataclasses import Module
from griffe.git import git_load


@pytest.fixture
def test_repo(tmp_path: Path):
    PKG = Path(__file__).parent / "test_repo"
    new_dir = shutil.copytree(PKG, tmp_path / "test_repo")
    os.rename(new_dir / "_git", new_dir / ".git")
    return new_dir


def test_git_load(test_repo):
    v1 = git_load("test_module", commit="v0.1.0", repo=test_repo)
    v2 = git_load("test_module", commit="v0.2.0", repo=test_repo)
    assert isinstance(v1, Module)
    assert isinstance(v2, Module)
    assert v1["__version__"].value == "'0.1.0'"
    assert v2["__version__"].value == "'0.2.0'"


def test_git_load_not_a_repo():
    with pytest.raises(ValueError) as e:
        git_load("test_module", commit="v0.2.0", repo="not-a-repo")
    assert "Not a git repository" in str(e.value)  # noqa: WPS441


def test_git_load_not_a_commit(test_repo):
    with pytest.raises(RuntimeError) as e:
        git_load("test_module", commit="invalid-tag", repo=test_repo)
    assert "Could not create git worktre" in str(e.value)  # noqa: WPS441


def test_git_load_not_a_module(test_repo):
    with pytest.raises(ModuleNotFoundError) as e:
        git_load("not_a_real_module", commit="v0.2.0", repo=test_repo)
    assert "No module named 'not_a_real_module'" in str(e.value)  # noqa: WPS441
