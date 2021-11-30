# griffe

[![ci](https://github.com/pawamoy/griffe/workflows/ci/badge.svg)](https://github.com/pawamoy/griffe/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://pawamoy.github.io/griffe/)
[![pypi version](https://img.shields.io/pypi/v/griffe.svg)](https://pypi.org/project/griffe/)
[![gitpod](https://img.shields.io/badge/gitpod-workspace-blue.svg?style=flat)](https://gitpod.io/#https://github.com/pawamoy/griffe)
[![gitter](https://badges.gitter.im/join%20chat.svg)](https://gitter.im/griffe/community)

Signatures for entire Python programs. Extract the structure, the frame, the skeleton of your project, to generate API documentation or find breaking changes in your API.

:warning: Work in progress!

## Requirements

Griffe requires Python 3.8 or above.

<details>
<summary>To install Python 3.8, I recommend using <a href="https://github.com/pyenv/pyenv"><code>pyenv</code></a>.</summary>

```bash
# install pyenv
git clone https://github.com/pyenv/pyenv ~/.pyenv

# setup pyenv (you should also put these three lines in .bashrc or similar)
export PATH="${HOME}/.pyenv/bin:${PATH}"
export PYENV_ROOT="${HOME}/.pyenv"
eval "$(pyenv init - bash)"

# install Python 3.8
pyenv install 3.8.12

# make it available globally
pyenv global system 3.8.12
```
</details>

## Installation

With `pip`:
```bash
python3.8 -m pip install griffe
```

With [`pipx`](https://github.com/pipxproject/pipx):
```bash
python3.8 -m pip install --user pipx

pipx install --python python3.8 griffe
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

- [ ] Design:
    - [x] Navigable trees (nodes and data)
    - [x] Extension system
    - [x] Performance
- [ ] Loader/Visitor:
    - [x] Docstrings
        - [x] Line numbers
        - [x] Parsing: see below
    - [ ] Labels
        - [ ] Attribute: ?
        - [ ] Function: ?
        - [ ] Class: ?
        - [ ] Module: ?
    - [x] Modules
    - [x] Classes
        - [x] Bases (parent classes)
        - [ ] Merging inherited members into class.
              Needs to be able to post-process classes,
              and to compute their MRO (C3Linearization, see docspec/pydocspec issues).
        - [ ] Merging `__init__` method's docstring into class' docstring
        - [x] Decorators
    - [x] Functions
        - [x] Parameters
        - [x] Return annotation (names, constants, attributes)
        - [x] Decorators
        - [ ] Support for `typing.overload` decorator.
              We'll probably need to add an `overloads` attribute to `Function`,
              to store the list of `@overload`-decorated functions,
              because currently different members of a same object cannot have the same names.
    - [x] Attributes (variables/constants)
        - [x] Docstrings
        - [x] Value
    - [x] Name resolution
        - [x] Per-object scope
        - [x] Load external packages resursively (indirections/aliases)
        - [x] Resolve everything that is an `ast.Name`
        - [x] Resolve names inside more complex expressions? Calls, exprs, etc.
    - [x] Lines collection (lines for each module)
- [x] Extension system
    - [x] Node-visiting extensions
    - [ ] Post-processing extensions
- [x] Docstrings parsers
    - [x] Structured format
    - [x] Styles
        - [x] Google
        - [x] RST
        - [x] Numpy
        - [ ] epydoc
        - [ ] New Markdown-based format? For graceful degradation
- [ ] Serializer:
    - [x] JSON
        - [x] Nested
        - [ ] Flat
- [ ] API diff:
    - [ ] Mecanism to cache APIs? Should users version them, or store them somewhere (docs)?
    - [ ] Ability to return warnings (things that are not backward-compatibility-friendly)
    - [ ] List of things to consider for warnings
        - [ ] Multiple positional-or-keyword parameters
        - [ ] Public imports in public modules
        - [ ] Private things made public through imports/assignments
        - [ ] Too many public things? Generally annoying. Configuration?
    - [ ] Ability to compare two APIs to return breaking changes
    - [ ] List of things to consider for breaking changes
        - [ ] Changed position of positional only parameter
        - [ ] Changed position of positional or keyword parameter
        - [ ] Changed type of parameter
        - [ ] Changed type of public module attribute
        - [ ] Changed return type of a public function/method
        - [ ] Added parameter without a default value
        - [ ] Removed keyword-only parameter without a default value, without **kwargs to swallow it
        - [ ] Removed positional-only parameter without a default value, without *args to swallow it
        - [ ] Removed positional-or_keyword argument without a default value, without *args and **kwargs to swallow it
        - [ ] Removed public module/class/function/method/attribute
        - [ ] All of the previous even when parent is private (could be publicly imported or assigned somewhere),
              and later be smarter: public assign/import makes private things public!
        - [ ] Inheritance: removed base, or added/changed base that changes MRO
