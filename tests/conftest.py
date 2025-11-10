"""Configuration for the pytest test suite."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pytest_gitconfig import GitConfig


@pytest.fixture(name="gitconfig", scope="session")
def _default_gitconfig(default_gitconfig: GitConfig) -> GitConfig:
    default_gitconfig.set({"user.name": "My Name"})
    default_gitconfig.set({"user.email": "my@email.com"})
    return default_gitconfig
