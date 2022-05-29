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
