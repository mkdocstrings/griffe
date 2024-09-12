# `griffe-autodocstringstyle`

[:octicons-heart-fill-24:{ .pulse } Sponsors only](../../insiders/index.md){ .insiders }

- **PyPI**: [`griffe-autodocstringstyle`](https://pypi.org/project/griffe-autodocstringstyle/)
- **GitHub**: [mkdocstrings/griffe-autodocstringstyle](https://github.com/mkdocstrings/griffe-autodocstringstyle)
- **Documentation:** [mkdocstrings.github.io/griffe-autodocstringstyle](https://mkdocstrings.github.io/griffe-autodocstringstyle)
- **Extension name:** `griffe_autodocstringstyle`

---

This extension sets the docstring parser to `auto` for all the docstrings of external packages. Packages are considered "external" when their sources are found in a virtual environment instead of a folder under the current working directory. Setting their docstring style to `auto` is useful if you plan on rendering the docstring of these objects in your own documentation.
