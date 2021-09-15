# griffe

[![ci](https://github.com/pawamoy/griffe/workflows/ci/badge.svg)](https://github.com/pawamoy/griffe/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://pawamoy.github.io/griffe/)
[![pypi version](https://img.shields.io/pypi/v/griffe.svg)](https://pypi.org/project/griffe/)
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

- Design:
    - [x] Navigable trees (nodes and data)
    - [x] Extension system
    - [x] Initial optimisations (~65KLoC/s)
- Loader/Visitor:
    - [x] Docstrings
        - [x] Line numbers
    - [x] Modules
    - [x] Classes
        - [ ] `__init__` data merged into parent class
    - [x] Functions
        - [x] Arguments
            - [x] Annotation (names, constants, attributes)
            - [x] Kind
            - [x] Default (constants, names, calls)
        - [ ] Positional only arguments
            - [ ] Annotation
            - [ ] Kind
            - [ ] Default
        - [ ] Keyword only arguments
            - [ ] Annotation
            - [ ] Kind
            - [ ] Default
        - [x] Return annotation (names, constants, attributes)
    - [ ] Data (variables/attributes)
        - [ ] Docstrings
        - [ ] Value
    - [ ] Name resolution
        - [ ] Per-object scope
        - [ ] Load external packages resursively (inheritance)
        - [ ] Resolve everything that is an `ast.Name`
        - [ ] Resolve names inside more complex expressions? Calls, exprs, etc.
    - [x] Lines collection (lines for each module)
- [ ] Docstrings parsers
    - [ ] Structured format
    - [ ] Styles
        - [ ] Google
        - [ ] RST
        - [ ] Numpy
        - [ ] New Markdown-based format? For graceful degradation
- Serializer:
    - [x] JSON
        - [x] Nested
        - [ ] Flat