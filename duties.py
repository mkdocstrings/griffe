"""Development tasks."""

import importlib
import os
import re
import sys
import tempfile
from contextlib import suppress
from io import StringIO
from pathlib import Path
from typing import List, Optional, Pattern
from urllib.request import urlopen

from duty import duty

PY_SRC_PATHS = (Path(_) for _ in ("src", "tests", "duties.py", "docs"))
PY_SRC_LIST = tuple(str(_) for _ in PY_SRC_PATHS)
PY_SRC = " ".join(PY_SRC_LIST)
TESTING = os.environ.get("TESTING", "0") in {"1", "true"}
CI = os.environ.get("CI", "0") in {"1", "true", "yes", ""}
WINDOWS = os.name == "nt"
PTY = not WINDOWS and not CI


def _latest(lines: List[str], regex: Pattern) -> Optional[str]:
    for line in lines:
        match = regex.search(line)
        if match:
            return match.groupdict()["version"]
    return None


def _unreleased(versions, last_release):
    for index, version in enumerate(versions):
        if version.tag == last_release:
            return versions[:index]
    return versions


def update_changelog(
    inplace_file: str,
    marker: str,
    version_regex: str,
    template_url: str,
) -> None:
    """
    Update the given changelog file in place.

    Parameters:
        inplace_file: The file to update in-place.
        marker: The line after which to insert new contents.
        version_regex: A regular expression to find currently documented versions in the file.
        template_url: The URL to the Jinja template used to render contents.
    """
    from git_changelog.build import Changelog
    from git_changelog.commit import AngularStyle
    from jinja2.sandbox import SandboxedEnvironment

    AngularStyle.DEFAULT_RENDER.insert(0, AngularStyle.TYPES["build"])
    env = SandboxedEnvironment(autoescape=False)
    template_text = urlopen(template_url).read().decode("utf8")  # noqa: S310
    template = env.from_string(template_text)
    changelog = Changelog(".", style="angular")

    if len(changelog.versions_list) == 1:
        last_version = changelog.versions_list[0]
        if last_version.planned_tag is None:
            planned_tag = "0.1.0"
            last_version.tag = planned_tag
            last_version.url += planned_tag
            last_version.compare_url = last_version.compare_url.replace("HEAD", planned_tag)

    with open(inplace_file, "r") as changelog_file:
        lines = changelog_file.read().splitlines()

    last_released = _latest(lines, re.compile(version_regex))
    if last_released:
        changelog.versions_list = _unreleased(changelog.versions_list, last_released)
    rendered = template.render(changelog=changelog, inplace=True)
    lines[lines.index(marker)] = rendered

    with open(inplace_file, "w") as changelog_file:  # noqa: WPS440
        changelog_file.write("\n".join(lines).rstrip("\n") + "\n")


@duty
def changelog(ctx):
    """
    Update the changelog in-place with latest commits.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    commit = "166758a98d5e544aaa94fda698128e00733497f4"
    template_url = f"https://raw.githubusercontent.com/pawamoy/jinja-templates/{commit}/keepachangelog.md"
    ctx.run(
        update_changelog,
        kwargs={
            "inplace_file": "CHANGELOG.md",
            "marker": "<!-- insertion marker -->",
            "version_regex": r"^## \[v?(?P<version>[^\]]+)",
            "template_url": template_url,
        },
        title="Updating changelog",
        pty=PTY,
    )


@duty(pre=["check_quality", "check_types", "check_docs", "check_dependencies"])
def check(ctx):
    """
    Check it all!

    Parameters:
        ctx: The context instance (passed automatically).
    """


@duty
def check_quality(ctx, files=PY_SRC):
    """
    Check the code quality.

    Parameters:
        ctx: The context instance (passed automatically).
        files: The files to check.
    """
    ctx.run(f"flake8 --config=config/flake8.ini {files}", title="Checking code quality", pty=PTY)


@duty
def check_dependencies(ctx):
    """
    Check for vulnerabilities in dependencies.

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
    from safety.formatter import report
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
        vulns = safety_check(packages=packages, ignore_ids="", key="", db_mirror="", cached=False, proxy={})
        output_report = report(vulns=vulns, full=True, checked_packages=len(packages))
        if vulns:
            print(output_report)

    ctx.run(safety, title="Checking dependencies")


@duty
def check_docs(ctx):
    """
    Check if the documentation builds correctly.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    Path("htmlcov").mkdir(parents=True, exist_ok=True)
    Path("htmlcov/index.html").touch(exist_ok=True)
    ctx.run("mkdocs build -s", title="Building documentation", pty=PTY)


@duty  # noqa: WPS231
def check_types(ctx):  # noqa: WPS231
    """
    Check that the code is correctly typed.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    # NOTE: the following code works around this issue:
    # https://github.com/python/mypy/issues/10633

    # compute packages directory path
    py = f"{sys.version_info.major}.{sys.version_info.minor}"
    pkgs_dir = Path("__pypackages__", py, "lib").resolve()

    # build the list of available packages
    packages = {}
    for package in pkgs_dir.glob("*"):
        if package.suffix not in {".dist-info", ".pth"} and package.name != "__pycache__":
            packages[package.name] = package

    # handle .pth files
    for pth in pkgs_dir.glob("*.pth"):
        with suppress(OSError):
            for package in Path(pth.read_text(encoding="utf8").splitlines()[0]).glob("*"):  # noqa: WPS440
                if package.suffix != ".dist-info":
                    packages[package.name] = package

    # create a temporary directory to assign to MYPYPATH
    with tempfile.TemporaryDirectory() as tmpdir:

        # symlink the stubs
        ignore = set()
        for stubs in (path for name, path in packages.items() if name.endswith("-stubs")):  # noqa: WPS335
            Path(tmpdir, stubs.name).symlink_to(stubs, target_is_directory=True)
            # try to symlink the corresponding package
            # see https://www.python.org/dev/peps/pep-0561/#stub-only-packages
            pkg_name = stubs.name.replace("-stubs", "")
            if pkg_name in packages:
                ignore.add(pkg_name)
                Path(tmpdir, pkg_name).symlink_to(packages[pkg_name], target_is_directory=True)

        # create temporary mypy config to ignore stubbed packages
        newconfig = Path("config", "mypy.ini").read_text(encoding="utf8")
        newconfig += "\n" + "\n\n".join(f"[mypy-{pkg}.*]\nignore_errors=true" for pkg in ignore)
        tmpconfig = Path(tmpdir, "mypy.ini")
        tmpconfig.write_text(newconfig)

        # set MYPYPATH and run mypy
        os.environ["MYPYPATH"] = tmpdir
        ctx.run(f"mypy --config-file {tmpconfig} {PY_SRC}", title="Type-checking", pty=PTY)


@duty(silent=True)
def clean(ctx):
    """
    Delete temporary files.

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
    """
    Build the documentation locally.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    ctx.run("mkdocs build", title="Building documentation")


@duty
def docs_serve(ctx, host="127.0.0.1", port=8000):
    """
    Serve the documentation (localhost:8000).

    Parameters:
        ctx: The context instance (passed automatically).
        host: The host to serve the docs from.
        port: The port to serve the docs on.
    """
    ctx.run(f"mkdocs serve -a {host}:{port}", title="Serving documentation", capture=False)


@duty
def docs_deploy(ctx):
    """
    Deploy the documentation on GitHub pages.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    ctx.run("mkdocs gh-deploy", title="Deploying documentation")


@duty
def format(ctx):
    """
    Run formatting tools on the code.

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
    """
    Release a new Python package.

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
    """
    Report coverage as text and HTML.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    ctx.run("coverage combine", nofail=True)
    ctx.run("coverage report --rcfile=config/coverage.ini", capture=False)
    ctx.run("coverage html --rcfile=config/coverage.ini")


@duty
def test(ctx, match: str = ""):
    """
    Run the test suite.

    Parameters:
        ctx: The context instance (passed automatically).
        match: A pytest expression to filter selected tests.
    """
    py_version = f"{sys.version_info.major}{sys.version_info.minor}"
    os.environ["COVERAGE_FILE"] = f".coverage.{py_version}"
    ctx.run(
        ["pytest", "-c", "config/pytest.ini", "-n", "auto", "-k", match, "tests"],
        title="Running tests",
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
