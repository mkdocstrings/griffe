"""Development tasks."""

import importlib
import os
import sys
from io import StringIO
from pathlib import Path

from duty import duty

PY_SRC_PATHS = (Path(_) for _ in ("src", "tests", "duties.py", "scripts"))
PY_SRC_LIST = tuple(str(_) for _ in PY_SRC_PATHS)
PY_SRC = " ".join(PY_SRC_LIST)
TESTING = os.environ.get("TESTING", "0") in {"1", "true"}
CI = os.environ.get("CI", "0") in {"1", "true", "yes", ""}
WINDOWS = os.name == "nt"
PTY = not WINDOWS and not CI
MULTIRUN = os.environ.get("PDM_MULTIRUN", "0") == "1"


def pyprefix(title: str) -> str:  # noqa: D103
    if MULTIRUN:
        prefix = f"(python{sys.version_info.major}.{sys.version_info.minor})"
        return f"{prefix:14}{title}"
    return title


@duty
def changelog(ctx):
    """Update the changelog in-place with latest commits.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    from git_changelog.cli import build_and_render as git_changelog

    ctx.run(
        git_changelog,
        kwargs={
            "repository": ".",
            "output": "CHANGELOG.md",
            "convention": "angular",
            "template": "keepachangelog",
            "parse_trailers": True,
            "parse_refs": False,
            "sections": ("build", "deps", "feat", "fix", "refactor"),
            "bump_latest": True,
            "in_place": True,
        },
        title="Updating changelog",
    )


@duty(pre=["check_quality", "check_types", "check_docs", "check_dependencies"])
def check(ctx):
    """Check it all!

    Parameters:
        ctx: The context instance (passed automatically).
    """


@duty
def check_quality(ctx, files=PY_SRC):
    """Check the code quality.

    Parameters:
        ctx: The context instance (passed automatically).
        files: The files to check.
    """
    ctx.run(f"flake8 --config=config/flake8.ini {files}", title=pyprefix("Checking code quality"), pty=PTY)


@duty
def check_dependencies(ctx):
    """Check for vulnerabilities in dependencies.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    # undo possible patching
    # see https://github.com/pyupio/safety/issues/348
    for module in sys.modules:  # noqa: WPS528
        if module.startswith("safety.") or module == "safety":
            del sys.modules[module]  # noqa: WPS420

    importlib.invalidate_caches()

    # reload original, unpatched safety
    from safety.formatter import SafetyFormatter
    from safety.safety import calculate_remediations
    from safety.safety import check as safety_check
    from safety.util import read_requirements

    # retrieve the list of dependencies
    requirements = ctx.run(
        ["pdm", "export", "-f", "requirements", "--without-hashes"],
        title="Exporting dependencies as requirements",
        allow_overrides=False,
    )

    # check using safety as a library
    def safety():  # noqa: WPS430
        packages = list(read_requirements(StringIO(requirements)))
        vulns, db_full = safety_check(packages=packages, ignore_vulns="")
        remediations = calculate_remediations(vulns, db_full)
        output_report = SafetyFormatter("text").render_vulnerabilities(
            announcements=[],
            vulnerabilities=vulns,
            remediations=remediations,
            full=True,
            packages=packages,
        )
        if vulns:
            print(output_report)
            return False
        return True

    ctx.run(safety, title="Checking dependencies")


@duty
def check_docs(ctx):
    """Check if the documentation builds correctly.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    Path("htmlcov").mkdir(parents=True, exist_ok=True)
    Path("htmlcov/index.html").touch(exist_ok=True)
    ctx.run("mkdocs build -s", title=pyprefix("Building documentation"), pty=PTY)


@duty  # noqa: WPS231
def check_types(ctx):  # noqa: WPS231
    """
    Check that the code is correctly typed.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    ctx.run(f"mypy --config-file config/mypy.ini {PY_SRC}", title=pyprefix("Type-checking"), pty=PTY)


@duty(silent=True)
def clean(ctx):
    """Delete temporary files.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    ctx.run("rm -rf .coverage*")
    ctx.run("rm -rf .mypy_cache")
    ctx.run("rm -rf .pytest_cache")
    ctx.run("rm -rf tests/.pytest_cache")
    ctx.run("rm -rf build")
    ctx.run("rm -rf dist")
    ctx.run("rm -rf htmlcov")
    ctx.run("rm -rf pip-wheel-metadata")
    ctx.run("rm -rf site")
    ctx.run("find . -type d -name __pycache__ | xargs rm -rf")
    ctx.run("find . -name '*.rej' -delete")


@duty
def docs(ctx):
    """Build the documentation locally.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    ctx.run("mkdocs build", title="Building documentation")


@duty
def docs_serve(ctx, host="127.0.0.1", port=8000):
    """Serve the documentation (localhost:8000).

    Parameters:
        ctx: The context instance (passed automatically).
        host: The host to serve the docs from.
        port: The port to serve the docs on.
    """
    ctx.run(f"mkdocs serve -a {host}:{port}", title="Serving documentation", capture=False)


@duty
def docs_deploy(ctx):
    """Deploy the documentation on GitHub pages.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    ctx.run("mkdocs gh-deploy", title="Deploying documentation")


@duty
def format(ctx):
    """Run formatting tools on the code.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    ctx.run(
        f"autoflake -ir --exclude tests/fixtures --remove-all-unused-imports {PY_SRC}",
        title="Removing unused imports",
        pty=PTY,
    )
    ctx.run(f"isort {PY_SRC}", title="Ordering imports", pty=PTY)
    ctx.run(f"black {PY_SRC}", title="Formatting code", pty=PTY)


@duty
def release(ctx, version):
    """Release a new Python package.

    Parameters:
        ctx: The context instance (passed automatically).
        version: The new version number to use.
    """
    ctx.run("git add pyproject.toml CHANGELOG.md", title="Staging files", pty=PTY)
    ctx.run(["git", "commit", "-m", f"chore: Prepare release {version}"], title="Committing changes", pty=PTY)
    ctx.run(f"git tag {version}", title="Tagging commit", pty=PTY)
    if not TESTING:
        ctx.run("git push", title="Pushing commits", pty=False)
        ctx.run("git push --tags", title="Pushing tags", pty=False)
        ctx.run("pdm build", title="Building dist/wheel", pty=PTY)
        ctx.run("twine upload --skip-existing dist/*", title="Publishing version", pty=PTY)
        docs_deploy.run()


@duty(silent=True)
def coverage(ctx):
    """Report coverage as text and HTML.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    ctx.run("coverage combine", nofail=True)
    ctx.run("coverage report --rcfile=config/coverage.ini", capture=False)
    ctx.run("coverage html --rcfile=config/coverage.ini")


@duty
def test(ctx, match: str = ""):
    """Run the test suite.

    Parameters:
        ctx: The context instance (passed automatically).
        match: A pytest expression to filter selected tests.
    """
    py_version = f"{sys.version_info.major}{sys.version_info.minor}"
    os.environ["COVERAGE_FILE"] = f".coverage.{py_version}"
    ctx.run(
        ["pytest", "-c", "config/pytest.ini", "-n", "auto", "-k", match, "tests"],
        title=pyprefix("Running tests"),
        pty=PTY,
        nofail=py_version == "311",
    )


@duty
def profile(ctx, browser: bool = False, **opts):
    """
    Run the test suite.

    Parameters:
        ctx: The context instance (passed automatically).
        browser: Whether to open the SVG file in the browser at the end.
        **opts: Additional options: async.
    """
    async_loader = opts.pop("async", False)
    griffe_opts = ["-A"] if async_loader else []
    packages = ctx.run(
        "find ~/.cache/pdm/packages -maxdepth 4 -type f -name __init__.py -exec dirname {} +",  # noqa: P103
        title="Finding packages",
    ).split("\n")
    ctx.run(
        [
            sys.executable,
            "-mcProfile",
            "-oprofile.pstats",
            "-m",
            "griffe",
            "-o/dev/null",
            "-LDEBUG",
            *griffe_opts,
            *packages,
        ],
        title=f"Profiling in {'async' if async_loader else 'sync'} mode on {len(packages)} packages",
        pty=False,
    )
    ctx.run("gprof2dot profile.pstats | dot -Tsvg -o profile.svg", title="Converting to SVG")
    if browser:
        os.system("/usr/bin/firefox profile.svg 2>/dev/null &")  # noqa: S605
