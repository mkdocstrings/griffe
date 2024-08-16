# `docstring-inheritance`

- **PyPI**: [`docstring-inheritance`](https://pypi.org/project/docstring-inheritance/)
- **GitHub**: [AntoineD/docstring-inheritance](https://github.com/AntoineD/docstring-inheritance)
- **Extension name:** `docstring_inheritance.griffe`

---

`docstring-inheritance` is a Python package that allows to avoid writing and maintaining duplicated Python docstrings. The typical usage is to enable the inheritance of the docstrings from a base class such that its derived classes fully or partially inherit the docstrings. It provides a Griffe extension and recommends to use it alongside the official [`inherited-docstrings`](../official/inherited-docstrings.md) extension in MkDocs:

```yaml
plugins:
- mkdocstrings:
    handlers:
      python:
        options:
          extensions:
          - griffe_inherited_docstrings
          - docstring_inheritance.griffe
```
