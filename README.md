# griffe

[![ci](https://github.com/mkdocstrings/griffe/workflows/ci/badge.svg)](https://github.com/mkdocstrings/griffe/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://mkdocstrings.github.io/griffe/)
[![pypi version](https://img.shields.io/pypi/v/griffe.svg)](https://pypi.org/project/griffe/)
[![gitpod](https://img.shields.io/badge/gitpod-workspace-blue.svg?style=flat)](https://gitpod.io/#https://github.com/mkdocstrings/griffe)
[![gitter](https://badges.gitter.im/join%20chat.svg)](https://gitter.im/griffe/community)

Signatures for entire Python programs. Extract the structure, the frame, the skeleton of your project, to generate API documentation or find breaking changes in your API.

Griffe, pronounced "grif" (`/ɡʁif/`), is a french word that means "claw",
but also "signature" in a familiar way. "On reconnaît bien là sa griffe."

## Requirements

griffe requires Python 3.7 or above.

<details>
<summary>To install Python 3.7, I recommend using <a href="https://github.com/pyenv/pyenv"><code>pyenv</code></a>.</summary>

```bash
# install pyenv
git clone https://github.com/pyenv/pyenv ~/.pyenv

# setup pyenv (you should also put these three lines in .bashrc or similar)
export PATH="${HOME}/.pyenv/bin:${PATH}"
export PYENV_ROOT="${HOME}/.pyenv"
eval "$(pyenv init -)"

# install Python 3.7
pyenv install 3.7.12

# make it available globally
pyenv global system 3.7.12
```
</details>

## Installation

With `pip`:
```bash
pip install griffe
```

With [`pipx`](https://github.com/pipxproject/pipx):
```bash
python3.7 -m pip install --user pipx
pipx install griffe
```

## Usage

**On the command line**, pass the names of packages to the `griffe` command:

```console
$ griffe httpx fastapi
[
  {
    "name": "httpx",
    ...
  }
]
```

See [the Usage section](https://pawamoy.github.io/griffe/usage/#on-the-command-line) for more examples.

**With Python:**

```python
from griffe.loader import GriffeLoader

griffe = GriffeLoader()
fastapi = griffe.load_module("fastapi")
```

See [the Usage section](https://pawamoy.github.io/griffe/usage/#with-python) for more examples.

## Todo

- Visitor/Inspector:
    - Labels
        - Attribute: ?
        - Function: ?
        - Class: ?
        - Module: ?
    - Merging inherited members into class.
        Needs to be able to post-process classes,
        and to compute their MRO (C3Linearization, see docspec/pydocspec issues).
    - Merging `__init__` method's docstring into class' docstring (could be an extension)
    - Support for `typing.overload` decorator.
        We'll probably need to add an `overloads` attribute to `Function`,
        to store the list of `@overload`-decorated functions,
        because currently different members of a same object cannot have the same names.
- Extensions
    - Post-processing extensions
    - Third-party libraries we could provide support for:
        - Django support
        - Marshmallow support
        - Pydantic support
- Docstrings parsers
    - epydoc
    - New Markdown-based format? For graceful degradation
- Serializer:
    - Flat JSON
    - JSON schema
- API diff:
    - Mecanism to cache APIs? Should users version them, or store them somewhere (docs)?
    - Ability to return warnings (things that are not backward-compatibility-friendly)
    - List of things to consider for warnings
        - Multiple positional-or-keyword parameters
        - Public imports in public modules
        - Private things made public through imports/assignments
        - Too many public things? Generally annoying. Configuration?
    - Ability to compare two APIs to return breaking changes
    - List of things to consider for breaking changes
        - Changed position of positional only parameter
        - Changed position of positional or keyword parameter
        - Changed type of parameter
        - Changed type of public module attribute
        - Changed return type of a public function/method
        - Added parameter without a default value
        - Removed keyword-only parameter without a default value, without **kwargs to swallow it
        - Removed positional-only parameter without a default value, without *args to swallow it
        - Removed positional-or_keyword argument without a default value, without *args and **kwargs to swallow it
        - Removed public module/class/function/method/attribute
        - All of the previous even when parent is private (could be publicly imported or assigned somewhere),
            and later be smarter: public assign/import makes private things public!
        - Inheritance: removed base, or added/changed base that changes MRO
