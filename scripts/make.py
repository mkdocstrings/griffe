#!/usr/bin/env python3
"""Management commands."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator

PYTHON_VERSIONS = os.getenv("PYTHON_VERSIONS", "3.8 3.9 3.10 3.11 3.12 3.13").split()

_exe = ""
_prefix = ""
_commands = []


# -----------------------------------------------------------------------------
# Helper functions ------------------------------------------------------------
# -----------------------------------------------------------------------------
def _shell(cmd: str, *, capture_output: bool = False, **kwargs: Any) -> str | None:
    if capture_output:
        return subprocess.check_output(cmd, shell=True, text=True, **kwargs)  # noqa: S602
    subprocess.run(cmd, shell=True, check=True, stderr=subprocess.STDOUT, **kwargs)  # noqa: S602
    return None


@contextmanager
def _environ(**kwargs: str) -> Iterator[None]:
    original = dict(os.environ)
    os.environ.update(kwargs)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(original)


def _uv_install() -> None:
    uv_opts = ""
    if "UV_RESOLUTION" in os.environ:
        uv_opts = f"--resolution={os.getenv('UV_RESOLUTION')}"
    requirements = _shell(f"uv pip compile {uv_opts} pyproject.toml devdeps.txt", capture_output=True)
    _shell("uv pip install -r -", input=requirements, text=True)
    if "CI" not in os.environ:
        _shell("uv pip install --no-deps -e .")
    else:
        _shell("uv pip install --no-deps .")


def _activate(path: str) -> None:
    global _exe, _prefix  # noqa: PLW0603

    if (bin := Path(path, "bin")).exists():
        activate_script = bin / "activate_this.py"
    elif (scripts := Path(path, "Scripts")).exists():
        activate_script = scripts / "activate_this.py"
        _exe = ".exe"
        _prefix = f"{path}/Scripts/"
    else:
        raise ValueError(f"make: activate: Cannot find activation script in {path}")

    if not activate_script.exists():
        raise ValueError(f"make: activate: Cannot find activation script in {path}")

    exec(activate_script.read_text(), {"__file__": str(activate_script)})  # noqa: S102


def _run(version: str, cmd: str, *args: str, **kwargs: Any) -> None:
    kwargs = {"check": True, **kwargs}
    if version == "default":
        _activate(".venv")
        subprocess.run([f"{_prefix}{cmd}{_exe}", *args], **kwargs)  # noqa: S603, PLW1510
    else:
        _activate(f".venvs/{version}")
        os.environ["MULTIRUN"] = "1"
        subprocess.run([f"{_prefix}{cmd}{_exe}", *args], **kwargs)  # noqa: S603, PLW1510


def _command(name: str) -> Callable[[Callable[..., None]], Callable[..., None]]:
    def wrapper(func: Callable[..., None]) -> Callable[..., None]:
        func.__cmdname__ = name  # type: ignore[attr-defined]
        _commands.append(func)
        return func

    return wrapper


# -----------------------------------------------------------------------------
# Commands --------------------------------------------------------------------
# -----------------------------------------------------------------------------
@_command("help")
def help(*args: str) -> None:
    """Print this help. Add task name to print help.

    ```bash
    make help [TASK]
    ```

    When the Python dependencies are not installed,
    this command just print the available commands.
    When the Python dependencies are installed,
    [duty](https://github.com/pawamoy/duty) is available
    so the command can also print the available tasks.

    If you add a task name after the command, it will print help for this specific task.
    """
    if len(args) > 1:
        _run("default", "duty", "--help", args[1])
    else:
        print("Available commands")
        for cmd in _commands:
            print(f"  {cmd.__cmdname__:21} {cmd.__doc__.splitlines()[0]}")  # type: ignore[attr-defined,union-attr]
        try:
            _run("default", "python", "-V", capture_output=True)
        except (subprocess.CalledProcessError, ValueError):
            pass
        else:
            print("\nAvailable tasks", flush=True)
            run("duty", "--list")


@_command("setup")
def setup() -> None:
    """Setup all virtual environments (install dependencies).

    ```bash
    make setup
    ```

    The `setup` command installs all the Python dependencies required to work on the project.
    Virtual environments and dependencies are managed by [uv](https://github.com/astral-sh/uv).
    Development dependencies are listed in the `devdeps.txt` file.

    The command will create a virtual environment in the `.venv` folder,
    as well as one virtual environment per supported Python version in the `.venvs/3.x` folders.
    Supported Python versions are listed in the `scripts/make` file, and can be overridden
    by setting the `PYTHON_VERSIONS` environment variable.

    If you cloned the repository on the same file-system as uv's cache,
    everything will be hard linked from the cache, so don't worry about wasting disk space.

    Once dependencies are installed, try running `make` or `make help` again, to show additional tasks.

    ```console exec="1" source="console"
    $ alias make="$PWD/scripts/make"  # markdown-exec: hide
    $ make
    ```

    These tasks are written using [duty](https://github.com/pawamoy/duty) (a task runner),
    and located in the `duties.py` module in the repository root.

    Some of these tasks will run in the default virtual environment (`.venv`),
    while others will run in all the supported Python version environments (`.venvs/3.x`).
    """
    if not shutil.which("uv"):
        raise ValueError("make: setup: uv must be installed, see https://github.com/astral-sh/uv")

    print("Installing dependencies (default environment)")
    default_venv = Path(".venv")
    if not default_venv.exists():
        _shell("uv venv --python python")
    _uv_install()

    if PYTHON_VERSIONS:
        for version in PYTHON_VERSIONS:
            print(f"\nInstalling dependencies (python{version})")
            venv_path = Path(f".venvs/{version}")
            if not venv_path.exists():
                _shell(f"uv venv --python {version} {venv_path}")
            with _environ(VIRTUAL_ENV=str(venv_path.resolve())):
                _uv_install()


@_command("run")
def run(cmd: str, *args: str, **kwargs: Any) -> None:
    """Run a command in the default virtual environment.

    ```bash
    make run <CMD> [ARG...]
    ```

    This command runs an arbitrary command inside the default virtual environment (`.venv`).
    It is especially useful to start a Python interpreter without having to first activate
    the virtual environment: `make run python`.
    """
    _run("default", cmd, *args, **kwargs)


@_command("multirun")
def multirun(cmd: str, *args: str, **kwargs: Any) -> None:
    """Run a command for all configured Python versions.

    ```bash
    make multirun <CMD> [ARG...]
    ```

    This command runs an arbitrary command inside the environments
    for all supported Python versions. It is especially useful for running tests.
    """
    if PYTHON_VERSIONS:
        for version in PYTHON_VERSIONS:
            run3x(version, cmd, *args, **kwargs)
    else:
        run(cmd, *args, **kwargs)


@_command("allrun")
def allrun(cmd: str, *args: str, **kwargs: Any) -> None:
    """Run a command in all virtual environments.

    ```bash
    make multirun <CMD> [ARG...]
    ```

    This command runs an arbitrary command inside the default environment,
    as well as the environments for all supported Python versions.

    This command is especially useful to install, remove or update dependencies
    in all environments at once. For example, if you want to install a dependency
    in editable mode, from a local source:

    ```bash
    make allrun uv pip install -e ../other-project
    ```
    """
    run(cmd, *args, **kwargs)
    if PYTHON_VERSIONS:
        multirun(cmd, *args, **kwargs)


@_command("3.x")
def run3x(version: str, cmd: str, *args: str, **kwargs: Any) -> None:
    """Run a command in the virtual environment for Python 3.x.

    ```bash
    make 3.x <CMD> [ARG...]
    ```

    This command runs an arbitrary command inside the environment of the selected Python version.
    It can be useful if you want to run a task that usually runs in the default environment
    with a different Python version.
    """
    _run(version, cmd, *args, **kwargs)


@_command("clean")
def clean() -> None:
    """Delete build artifacts and cache files.

    ```bash
    make clean
    ```

    This command simply deletes build artifacts and cache files and folders
    such as `build/`, `.cache/`, etc.. The virtual environments (`.venv` and `.venvs/*`)
    are not removed by this command.
    """
    paths_to_clean = ["build", "dist", "htmlcov", "site", ".coverage*", ".pdm-build"]
    for path in paths_to_clean:
        _shell(f"rm -rf {path}")

    cache_dirs = [".cache", ".pytest_cache", ".mypy_cache", ".ruff_cache", "__pycache__"]
    for dirpath in Path().rglob("*"):
        if any(dirpath.match(pattern) for pattern in cache_dirs) and not (
            dirpath.match(".venv") or dirpath.match(".venvs")
        ):
            shutil.rmtree(path, ignore_errors=True)


@_command("vscode")
def vscode() -> None:
    """Configure VSCode to work on this project.

    ```bash
    make vscode
    ```

    This command configures the [VSCode editor](https://code.visualstudio.com/)
    by copying the following files into the `.vscode` directory:

    - `launch.json`, for run configurations (to run debug sessions)
    - `settings.json`, for various editor settings like linting tools and their configuration
    - `tasks.json`, for running tasks directly from VSCode's interface

    Warning:
        These files will be overwritten every time the command is run.
    """
    Path(".vscode").mkdir(parents=True, exist_ok=True)
    _shell("cp -v config/vscode/* .vscode")


# -----------------------------------------------------------------------------
# Main ------------------------------------------------------------------------
# -----------------------------------------------------------------------------
def main(args: list[str]) -> int:
    """Main entry point."""
    if not args or args[0] == "help":
        help(*args)
        return 0

    while args:
        cmd = args.pop(0)

        if cmd == "run":
            run(*args)
            return 0

        if cmd == "multirun":
            multirun(*args)
            return 0

        if cmd == "allrun":
            allrun(*args)
            return 0

        if cmd.startswith("3."):
            run3x(cmd, *args)
            return 0

        opts = []
        while args and (args[0].startswith("-") or "=" in args[0]):
            opts.append(args.pop(0))

        if cmd == "clean":
            clean()
        elif cmd == "setup":
            setup()
        elif cmd == "vscode":
            vscode()
        elif cmd == "check":
            multirun("duty", "check-quality", "check-types", "check-docs")
            run("duty", "check-api")
        elif cmd in {"check-quality", "check-docs", "check-types", "test"}:
            multirun("duty", cmd, *opts)
        else:
            run("duty", cmd, *opts)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except subprocess.CalledProcessError as process:
        if process.output:
            print(process.output, file=sys.stderr)
        sys.exit(process.returncode)
