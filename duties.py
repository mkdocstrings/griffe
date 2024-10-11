"""Development tasks."""

from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from functools import partial
from importlib.metadata import version as pkgversion
from pathlib import Path
from typing import TYPE_CHECKING

from duty import duty, tools

if TYPE_CHECKING:
    from collections.abc import Iterator

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

    ```bash
    make changelog [bump=VERSION]
    ```

    Update the changelog in-place. The changelog task uses [git-changelog](https://pawamoy.github.io/git-changelog/)
    to read Git commits and parse their messages to infer the new version based
    on our [commit message convention][commit-message-convention].

    The new version will be based on the types of the latest commits,
    unless a specific version is provided with the `bump` parameter.

    If the group of commits contains only bug fixes (`fix:`)
    and/or commits that are not interesting for users (`chore:`, `style:`, etc.),
    the changelog will gain a new **patch** entry.
    It means that the new suggested version will be a patch bump
    of the previous one: `0.1.1` becomes `0.1.2`.

    If the group of commits contains at least one feature (`feat:`),
    the changelog will gain a new **minor** entry.
    It means that the new suggested version will be a minor bump
    of the previous one: `0.1.1` becomes `0.2.0`.

    If there is, in the group of commits, a commit whose body contains something like `Breaking change`,
    the changelog will gain a new **major** entry, unless the version is still an "alpha" version (starting with 0),
    in which case it gains a **minor** entry.
    It means that the new suggested version will be a major bump
    of the previous one: `1.2.1` becomes `2.0.0`, but `0.2.1` is only bumped up to `0.3.0`.
    Moving from "alpha" status to "beta" or "stable" status is a choice left to the developers,
    when they consider the package is ready for it.

    The configuration for git-changelog is located at `config/git-changelog.toml`.

    Parameters:
        bump: Bump option passed to git-changelog.
    """
    ctx.run(tools.git_changelog(bump=bump or None), title="Updating changelog")


@duty(pre=["check-quality", "check-types", "check-docs", "check-api"])
def check(ctx: Context) -> None:
    """Check it all!

    ```bash
    make check
    ```

    Composite command to run all the check commands:

    - [`check-quality`][], to check the code quality on all Python versions
    - [`check-types`][], to type-check the code on all Python versions
    - [`check-docs`][], to check the docs on all Python versions
    - [`check-api`][], to check for API breaking changes
    """


@duty
def check_quality(ctx: Context) -> None:
    """Check the code quality.

    ```bash
    make check-quality
    ```

    Check the code quality using [Ruff](https://astral.sh/ruff).

    The configuration for Ruff is located at `config/ruff.toml`.
    In this file, you can deactivate rules or activate others to customize your analysis.
    Rule identifiers always start with one or more capital letters, like `D`, `S` or `BLK`,
    then followed by a number.

    You can ignore a rule on a specific code line by appending
    a `noqa` comment ("no quality analysis/assurance"):

    ```python title="src/your_package/module.py"
    print("a code line that triggers a Ruff warning")  # noqa: ID
    ```

    ...where ID is the identifier of the rule you want to ignore for this line.

    Example:
        ```python title="src/your_package/module.py"
        import subprocess
        ```

        ```console
        $ make check-quality
        ✗ Checking code quality (1)
        > ruff check --config=config/ruff.toml src/ tests/ scripts/
        src/your_package/module.py:2:1: S404 Consider possible security implications associated with subprocess module.
        ```

        Now add a comment to ignore this warning.

        ```python title="src/your_package/module.py"
        import subprocess  # noqa: S404
        ```

        ```console
        $ make check-quality
        ✓ Checking code quality
        ```

        You can disable multiple different warnings on a single line
        by separating them with commas, for example `# noqa: D300,D301`.

    You can disable a warning globally by adding its ID
    into the list in `config/ruff.toml`.

    You can also disable warnings per file, like so:

    ```toml title="config/ruff.toml"
    [per-file-ignores]
    "src/your_package/your_module.py" = [
        "T201",  # Print statement
    ]
    ```
    """
    ctx.run(
        tools.ruff.check(*PY_SRC_LIST, config="config/ruff.toml"),
        title=pyprefix("Checking code quality"),
    )


@duty
def check_docs(ctx: Context) -> None:
    """Check if the documentation builds correctly.

    ```bash
    make check-docs
    ```

    Build the docs with [MkDocs](https://www.mkdocs.org/) in strict mode.

    The configuration for MkDocs is located at `mkdocs.yml`.

    This task builds the documentation with strict behavior:
    any warning will be considered an error and the command will fail.
    The warnings/errors can be about incorrect docstring format,
    or invalid cross-references.
    """
    Path("htmlcov").mkdir(parents=True, exist_ok=True)
    Path("htmlcov/index.html").touch(exist_ok=True)
    with material_insiders():
        ctx.run(
            tools.mkdocs.build(strict=True, verbose=True),
            title=pyprefix("Building documentation"),
        )


@duty
def check_types(ctx: Context) -> None:
    """Check that the code is correctly typed.

    ```bash
    make check-types
    ```

    Run type-checking on the code with [Mypy](https://mypy.readthedocs.io/).

    The configuration for Mypy is located at `config/mypy.ini`.

    If you cannot or don't know how to fix a typing error in your code,
    as a last resort you can ignore this specific error with a comment:

    ```python title="src/your_package/module.py"
    print("a code line that triggers a Mypy warning")  # type: ignore[ID]
    ```

    ...where ID is the name of the warning.

    Example:
        ```python title="src/your_package/module.py"
        result = data_dict.get(key, None).value
        ```

        ```console
        $ make check-types
        ✗ Checking types (1)
        > mypy --config-file=config/mypy.ini src/ tests/ scripts/
        src/your_package/module.py:2:1: Item "None" of "Data | None" has no attribute "value" [union-attr]
        ```

        Now add a comment to ignore this warning.

        ```python title="src/your_package/module.py"
        result = data_dict.get(key, None).value  # type: ignore[union-attr]
        ```

        ```console
        $ make check-types
        ✓ Checking types
        ```
    """
    ctx.run(
        tools.mypy(*PY_SRC_LIST, config_file="config/mypy.ini"),
        title=pyprefix("Type-checking"),
    )


@duty
def check_api(ctx: Context, *cli_args: str) -> None:
    """Check for API breaking changes.

    ```bash
    make check-api
    ```

    Compare the current code to the latest version (Git tag)
    using [Griffe](https://mkdocstrings.github.io/griffe/),
    to search for API breaking changes since latest version.
    It is set to allow failures, and is more about providing information
    than preventing CI to pass.

    Parameters:
        *cli_args: Additional Griffe CLI arguments.
    """
    ctx.run(
        tools.griffe.check("griffe", search=["src"], color=True).add_args(*cli_args),
        title="Checking for API breaking changes",
        nofail=True,
    )


@duty
def docs(ctx: Context, *cli_args: str, host: str = "127.0.0.1", port: int = 8000) -> None:
    """Serve the documentation (localhost:8000).

    ```bash
    make docs
    ```

    This task uses [MkDocs](https://www.mkdocs.org/) to serve the documentation locally.

    Parameters:
        *cli_args: Additional MkDocs CLI arguments.
        host: The host to serve the docs from.
        port: The port to serve the docs on.
    """
    with material_insiders():
        ctx.run(
            tools.mkdocs.serve(dev_addr=f"{host}:{port}").add_args(*cli_args),
            title="Serving documentation",
            capture=False,
        )


@duty
def docs_deploy(ctx: Context) -> None:
    """Deploy the documentation to GitHub pages.

    ```bash
    make docs-deploy
    ```

    Use [MkDocs](https://www.mkdocs.org/) to build and deploy the documentation to GitHub pages.
    """
    os.environ["DEPLOY"] = "true"
    with material_insiders() as insiders:
        if not insiders:
            ctx.run(lambda: False, title="Not deploying docs without Material for MkDocs Insiders!")
        origin = ctx.run("git config --get remote.origin.url", silent=True, allow_overrides=False)
        if "pawamoy-insiders/griffe" in origin:
            ctx.run(
                "git remote add upstream git@github.com:mkdocstrings/griffe",
                silent=True,
                nofail=True,
                allow_overrides=False,
            )
            ctx.run(
                tools.mkdocs.gh_deploy(remote_name="upstream", force=True),
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
    """Run formatting tools on the code.

    ```bash
    make format
    ```

    Format the code with [Ruff](https://astral.sh/ruff).
    This command will also automatically fix some coding issues when possible.
    """
    ctx.run(
        tools.ruff.check(*PY_SRC_LIST, config="config/ruff.toml", fix_only=True, exit_zero=True),
        title="Auto-fixing code",
    )
    ctx.run(tools.ruff.format(*PY_SRC_LIST, config="config/ruff.toml"), title="Formatting code")


@duty
def build(ctx: Context) -> None:
    """Build source and wheel distributions.

    ```bash
    make build
    ```

    Build distributions of your project for the current version.
    The build task uses the [`build` tool](https://build.pypa.io/en/stable/)
    to build `.tar.gz` (Gzipped sources archive) and `.whl` (wheel) distributions
    of your project in the `dist` directory.
    """
    ctx.run(
        tools.build(),
        title="Building source and wheel distributions",
        pty=PTY,
    )


@duty
def publish(ctx: Context) -> None:
    """Publish source and wheel distributions to PyPI.

    ```bash
    make publish
    ```

    Publish the source and wheel distributions of your project to PyPI
    using [Twine](https://twine.readthedocs.io/).
    """
    if not Path("dist").exists():
        ctx.run("false", title="No distribution files found")
    dists = [str(dist) for dist in Path("dist").iterdir()]
    ctx.run(
        tools.twine.upload(*dists, skip_existing=True),
        title="Publishing source and wheel distributions to PyPI",
        pty=PTY,
    )


@duty(post=["build", "publish", "docs-deploy"])
def release(ctx: Context, version: str = "") -> None:
    """Release a new version of the project.

    ```bash
    make release [version=VERSION]
    ```

    This task will:

    - Stage changes to `pyproject.toml` and `CHANGELOG.md`
    - Commit the changes with a message like `chore: Prepare release 1.0.0`
    - Tag the commit with the new version number
    - Push the commit and the tag to the remote repository
    - Build source and wheel distributions
    - Publish the distributions to PyPI
    - Deploy the documentation to GitHub pages

    Parameters:
        version: The new version number to use. If not provided, you will be prompted for it.
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


@duty(silent=True, aliases=["cov"])
def coverage(ctx: Context) -> None:
    """Report coverage as text and HTML.

    ```bash
    make coverage
    ```

    Combine coverage data from multiple test runs with [Coverage.py](https://coverage.readthedocs.io/),
    then generate an HTML report into the `htmlcov` directory,
    and print a text report in the console.
    """
    ctx.run(tools.coverage.combine(), nofail=True)
    ctx.run(tools.coverage.report(rcfile="config/coverage.ini"), capture=False)
    ctx.run(tools.coverage.html(rcfile="config/coverage.ini"))


@duty
def test(ctx: Context, *cli_args: str, match: str = "") -> None:
    """Run the test suite.

    ```bash
    make test [match=EXPR]
    ```

    Run the test suite with [Pytest](https://docs.pytest.org/) and plugins.
    Code source coverage is computed thanks to
    [coveragepy](https://coverage.readthedocs.io/en/coverage-5.1/).

    Parameters:
        *cli_args: Additional Pytest CLI arguments.
        match: A pytest expression to filter selected tests.
    """
    py_version = f"{sys.version_info.major}{sys.version_info.minor}"
    os.environ["COVERAGE_FILE"] = f".coverage.{py_version}"
    ctx.run(
        tools.pytest(
            "tests",
            config_file="config/pytest.ini",
            select=match,
            color="yes",
        ).add_args("-n", "auto", *cli_args),
        title=pyprefix("Running tests"),
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

    from griffe import visit

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
