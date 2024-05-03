"""Development tasks."""

from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from functools import partial
from importlib.metadata import version as pkgversion
from pathlib import Path
from typing import TYPE_CHECKING, Iterator

from duty import duty
from duty.callables import coverage, lazy, mkdocs, mypy, pytest, ruff, safety

if TYPE_CHECKING:
    from duty.context import Context


PY_SRC_PATHS = (Path(_) for _ in ("src", "tests", "duties.py", "scripts"))
PY_SRC_LIST = tuple(str(_) for _ in PY_SRC_PATHS)
PY_SRC = " ".join(PY_SRC_LIST)
CI = os.environ.get("CI", "0") in {"1", "true", "yes", ""}
WINDOWS = os.name == "nt"
PTY = not WINDOWS and not CI
MULTIRUN = os.environ.get("MULTIRUN", "0") == "1"


def pyprefix(title: str) -> str:  # noqa: D103
    if MULTIRUN:
        prefix = f"(python{sys.version_info.major}.{sys.version_info.minor})"
        return f"{prefix:14}{title}"
    return title


@contextmanager
def material_insiders() -> Iterator[bool]:  # noqa: D103
    if "+insiders" in pkgversion("mkdocs-material"):
        os.environ["MATERIAL_INSIDERS"] = "true"
        try:
            yield True
        finally:
            os.environ.pop("MATERIAL_INSIDERS")
    else:
        yield False


@duty
def changelog(ctx: Context, bump: str = "") -> None:
    """Update the changelog in-place with latest commits.

    Parameters:
        bump: Bump option passed to git-changelog.
    """
    from git_changelog.cli import main as git_changelog

    args = [f"--bump={bump}"] if bump else []
    ctx.run(git_changelog, args=[args], title="Updating changelog", command="git-changelog")


@duty(pre=["check_quality", "check_types", "check_docs", "check_dependencies", "check-api"])
def check(ctx: Context) -> None:  # noqa: ARG001
    """Check it all!"""


@duty
def check_quality(ctx: Context) -> None:
    """Check the code quality."""
    ctx.run(
        ruff.check(*PY_SRC_LIST, config="config/ruff.toml"),
        title=pyprefix("Checking code quality"),
        command=f"ruff check --config config/ruff.toml {PY_SRC}",
    )


@duty
def check_dependencies(ctx: Context) -> None:
    """Check for vulnerabilities in dependencies."""
    # retrieve the list of dependencies
    requirements = ctx.run(
        ["uv", "pip", "freeze"],
        silent=True,
        allow_overrides=False,
    )

    ctx.run(
        safety.check(requirements),
        title="Checking dependencies",
        command="uv pip freeze | safety check --stdin",
    )


@duty
def check_docs(ctx: Context) -> None:
    """Check if the documentation builds correctly."""
    Path("htmlcov").mkdir(parents=True, exist_ok=True)
    Path("htmlcov/index.html").touch(exist_ok=True)
    with material_insiders():
        ctx.run(
            mkdocs.build(strict=True, verbose=True),
            title=pyprefix("Building documentation"),
            command="mkdocs build -vs",
        )


@duty
def check_types(ctx: Context) -> None:
    """Check that the code is correctly typed."""
    ctx.run(
        mypy.run(*PY_SRC_LIST, config_file="config/mypy.ini"),
        title=pyprefix("Type-checking"),
        command=f"mypy --config-file config/mypy.ini {PY_SRC}",
    )


@duty
def check_api(ctx: Context) -> None:
    """Check for API breaking changes."""
    from griffe.cli import check as g_check

    griffe_check = lazy(g_check, name="griffe.check")
    ctx.run(
        griffe_check("griffe", search_paths=["src"], color=True),
        title="Checking for API breaking changes",
        command="griffe check -ssrc griffe",
        nofail=True,
    )


@duty
def docs(ctx: Context, host: str = "127.0.0.1", port: int = 8000) -> None:
    """Serve the documentation (localhost:8000).

    Parameters:
        host: The host to serve the docs from.
        port: The port to serve the docs on.
    """
    with material_insiders():
        ctx.run(
            mkdocs.serve(dev_addr=f"{host}:{port}"),
            title="Serving documentation",
            capture=False,
        )


@duty
def docs_deploy(ctx: Context) -> None:
    """Deploy the documentation on GitHub pages."""
    os.environ["DEPLOY"] = "true"
    with material_insiders() as insiders:
        if not insiders:
            ctx.run(lambda: False, title="Not deploying docs without Material for MkDocs Insiders!")
        origin = ctx.run("git config --get remote.origin.url", silent=True)
        if "pawamoy-insiders/griffe" in origin:
            ctx.run("git remote add upstream git@github.com:mkdocstrings/griffe", silent=True, nofail=True)
            ctx.run(
                mkdocs.gh_deploy(remote_name="upstream", force=True),
                title="Deploying documentation",
            )
        else:
            ctx.run(
                lambda: False,
                title="Not deploying docs from public repository (do that from insiders instead!)",
                nofail=True,
            )


@duty
def format(ctx: Context) -> None:
    """Run formatting tools on the code."""
    ctx.run(
        ruff.check(*PY_SRC_LIST, config="config/ruff.toml", fix_only=True, exit_zero=True),
        title="Auto-fixing code",
    )
    ctx.run(ruff.format(*PY_SRC_LIST, config="config/ruff.toml"), title="Formatting code")


@duty
def build(ctx: Context) -> None:
    """Build source and wheel distributions."""
    from build.__main__ import main as pyproject_build

    ctx.run(
        pyproject_build,
        args=[()],
        title="Building source and wheel distributions",
        command="pyproject-build",
        pty=PTY,
    )


@duty
def publish(ctx: Context) -> None:
    """Publish source and wheel distributions to PyPI."""
    from twine.cli import dispatch as twine_upload

    if not Path("dist").exists():
        ctx.run("false", title="No distribution files found")
    dists = [str(dist) for dist in Path("dist").iterdir()]
    ctx.run(
        twine_upload,
        args=[["upload", "-r", "pypi", "--skip-existing", *dists]],
        title="Publish source and wheel distributions to PyPI",
        command="twine upload -r pypi --skip-existing dist/*",
        pty=PTY,
    )


@duty(post=["build", "publish", "docs-deploy"])
def release(ctx: Context, version: str = "") -> None:
    """Release a new Python package.

    Parameters:
        version: The new version number to use.
    """
    origin = ctx.run("git config --get remote.origin.url", silent=True)
    if "pawamoy-insiders/griffe" in origin:
        ctx.run(
            lambda: False,
            title="Not releasing from insiders repository (do that from public repo instead!)",
        )
    if not (version := (version or input("> Version to release: ")).strip()):
        ctx.run("false", title="A version must be provided")
    ctx.run("git add pyproject.toml CHANGELOG.md", title="Staging files", pty=PTY)
    ctx.run(["git", "commit", "-m", f"chore: Prepare release {version}"], title="Committing changes", pty=PTY)
    ctx.run(f"git tag {version}", title="Tagging commit", pty=PTY)
    ctx.run("git push", title="Pushing commits", pty=False)
    ctx.run("git push --tags", title="Pushing tags", pty=False)


@duty(silent=True, aliases=["coverage"])
def cov(ctx: Context) -> None:
    """Report coverage as text and HTML."""
    ctx.run(coverage.combine, nofail=True)
    ctx.run(coverage.report(rcfile="config/coverage.ini"), capture=False)
    ctx.run(coverage.html(rcfile="config/coverage.ini"))


@duty
def test(ctx: Context, match: str = "") -> None:
    """Run the test suite.

    Parameters:
        match: A pytest expression to filter selected tests.
    """
    py_version = f"{sys.version_info.major}{sys.version_info.minor}"
    os.environ["COVERAGE_FILE"] = f".coverage.{py_version}"
    ctx.run(
        pytest.run("-n", "auto", "tests", config_file="config/pytest.ini", select=match, color="yes", verbosity=10),
        title=pyprefix("Running tests"),
        command=f"pytest -c config/pytest.ini -n auto -k{match!r} --color=yes tests",
    )


class Seeds(list):  # noqa: D101
    def __init__(self, cli_value: str = "") -> None:  # noqa: D107
        if cli_value:
            self.extend(int(seed) for seed in cli_value.split(","))


@duty
def fuzz(
    ctx: Context,
    *,
    size: int = 20,
    min_seed: int = 0,
    max_seed: int = 1_000_000,
    seeds: Seeds = Seeds(),  # noqa: B008
) -> None:
    """Fuzz Griffe against generated Python code.

    Parameters:
        ctx: The context instance (passed automatically).
        size: The size of the case set (number of cases to test).
        seeds: Seeds to test or exclude.
        min_seed: Minimum value for the seeds range.
        max_seed: Maximum value for the seeds range.
    """
    import warnings
    from random import sample
    from tempfile import gettempdir

    from pysource_codegen import generate
    from pysource_minimize import minimize

    from griffe.agents.visitor import visit

    warnings.simplefilter("ignore", SyntaxWarning)

    def fails(code: str, filepath: Path) -> bool:
        try:
            visit(filepath.stem, filepath=filepath, code=code)
        except Exception:  # noqa: BLE001
            return True
        return False

    def test_seed(seed: int, revisit: bool = False) -> bool:  # noqa: FBT001,FBT002
        filepath = Path(gettempdir(), f"fuzz_{seed}_{sys.version_info.minor}.py")
        if filepath.exists():
            if revisit:
                code = filepath.read_text()
            else:
                return True
        else:
            code = generate(seed)
            filepath.write_text(code)

        if fails(code, filepath):
            new_code = minimize(code, partial(fails, filepath=filepath))
            if code != new_code:
                filepath.write_text(new_code)
            return False
        return True

    revisit = bool(seeds)
    seeds = seeds or sample(range(min_seed, max_seed + 1), size)  # type: ignore[assignment]
    for seed in seeds:
        ctx.run(test_seed, args=[seed, revisit], title=f"Visiting code generated with seed {seed}")
