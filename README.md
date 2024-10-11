# Griffe

[![ci](https://github.com/mkdocstrings/griffe/workflows/ci/badge.svg)](https://github.com/mkdocstrings/griffe/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs-708FCC.svg?style=flat)](https://mkdocstrings.github.io/griffe/)
[![pypi version](https://img.shields.io/pypi/v/griffe.svg)](https://pypi.org/project/griffe/)
[![gitpod](https://img.shields.io/badge/gitpod-workspace-708FCC.svg?style=flat)](https://gitpod.io/#https://github.com/mkdocstrings/griffe)
[![gitter](https://badges.gitter.im/join%20chat.svg)](https://app.gitter.im/#/room/#mkdocstrings_griffe:gitter.im)

<img src="logo.svg" alt="Griffe logo, created by François Rozet &lt;francois.rozet@outlook.com&gt;" style="float: right; max-width: 200px; margin: 0 15px;">

Signatures for entire Python programs. Extract the structure, the frame, the skeleton of your project, to generate API documentation or find breaking changes in your API.

Griffe, pronounced "grif" (`/ɡʁif/`), is a french word that means "claw",
but also "signature" in a familiar way. "On reconnaît bien là sa griffe."

- [User guide](https://mkdocstrings.github.io/griffe/guide/users/)
- [Contributor guide](https://mkdocstrings.github.io/griffe/guide/contributors/)
- [API reference](https://mkdocstrings.github.io/griffe/reference/api/)

## Installation

```bash
pip install griffe
```

With [`uv`](https://docs.astral.sh/uv/):

```bash
uv tool install griffe
```

## Usage

### Dump JSON-serialized API

**On the command line**, pass the names of packages to the `griffe dump` command:

```console
$ griffe dump httpx fastapi
{
  "httpx": {
    "name": "httpx",
    ...
  },
  "fastapi": {
    "name": "fastapi",
    ...
  }
}
```

See the [Serializing chapter](https://mkdocstrings.github.io/griffe/guide/users/serializing/) for more examples.

### Check for API breaking changes

Pass a relative path to the `griffe check` command:

```console
$ griffe check mypackage --verbose
mypackage/mymodule.py:10: MyClass.mymethod(myparam):
Parameter kind was changed:
  Old: positional or keyword
  New: keyword-only
```

For `src` layouts:

```console
$ griffe check --search src mypackage --verbose
src/mypackage/mymodule.py:10: MyClass.mymethod(myparam):
Parameter kind was changed:
  Old: positional or keyword
  New: keyword-only
```

It's also possible to directly **check packages from PyPI.org**
(or other indexes configured through `PIP_INDEX_URL`). 
This feature is [available to sponsors only](https://mkdocstrings.github.io/griffe/insiders/)
and requires that you install Griffe with the `pypi` extra:

```bash
pip install griffe[pypi]
```

The command syntax is:

```bash
griffe check package_name -b project-name==2.0 -a project-name==1.0
```

See the [Checking chapter](https://mkdocstrings.github.io/griffe/guide/users/checking/) for more examples.

### Load and navigate data with Python

**With Python**, loading a package:

```python
import griffe

fastapi = griffe.load("fastapi")
```

Finding breaking changes:

```python
import griffe

previous = griffe.load_git("mypackage", ref="0.2.0")
current = griffe.load("mypackage")

for breakage in griffe.find_breaking_changes(previous, current):
    ...
```

See the [Loading chapter](https://mkdocstrings.github.io/griffe/guide/users/loading/) for more examples.
