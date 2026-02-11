# Installation

Griffe is a Python package, so you can install it with your favorite Python package installer or dependency manager.

## Install as a tool & library

```
pip install griffe
```

[pip](https://pip.pypa.io/en/stable/) is the main package installer for Python.

```
pdm add griffe
```

[PDM](https://pdm-project.org/en/latest/) is an all-in-one solution for Python project management.

```
poetry add griffe
```

[Poetry](https://python-poetry.org/) is an all-in-one solution for Python project management.

```
rye add griffe
```

[Rye](https://rye.astral.sh/) is an all-in-one solution for Python project management, written in Rust.

```
uv add griffe
```

[uv](https://docs.astral.sh/uv/) is an extremely fast Python package and project manager, written in Rust.

## Install as a library only

If you only need the library for API introspection and analysis without the CLI tool, you can install `griffelib`:

```
pip install griffelib
```

[pip](https://pip.pypa.io/en/stable/) is the main package installer for Python.

```
pdm add griffelib
```

[PDM](https://pdm-project.org/en/latest/) is an all-in-one solution for Python project management.

```
poetry add griffelib
```

[Poetry](https://python-poetry.org/) is an all-in-one solution for Python project management.

```
rye add griffelib
```

[Rye](https://rye.astral.sh/) is an all-in-one solution for Python project management, written in Rust.

```
uv add griffelib
```

[uv](https://docs.astral.sh/uv/) is an extremely fast Python package and project manager, written in Rust.

This installs the `griffe` package as usual, but without the CLI program and its dependencies.

## Install as a tool only

```
pip install --user griffe
```

[pip](https://pip.pypa.io/en/stable/) is the main package installer for Python.

```
pipx install griffe
```

[pipx](https://pipx.pypa.io/stable/) allows to install and run Python applications in isolated environments.

```
rye install griffe
```

[Rye](https://rye.astral.sh/) is an all-in-one solution for Python project management, written in Rust.

```
uv tool install griffe
```

[uv](https://docs.astral.sh/uv/) is an extremely fast Python package and project manager, written in Rust.

## Running Griffe

Once installed, you can run Griffe using the `griffe` command:

```
$ griffe check mypackage
```

Or as a Python module:

```
$ python -m griffe check mypackage
```
