# `griffe-inherited-docstrings`

- **PyPI**: [`griffe-inherited-docstrings`](https://pypi.org/project/griffe-inherited-docstrings/)
- **GitHub**: [mkdocstrings/griffe-inherited-docstrings](https://github.com/mkdocstrings/griffe-inherited-docstrings)
- **Documentation:** [mkdocstrings.github.io/griffe-inherited-docstrings](https://mkdocstrings.github.io/griffe-inherited-docstrings)
- **Extension name:** `griffe_inherited_docstrings`

---

This extension, when enabled, iterates on the declared members of all classes found within a package, and if they don't have a docstring, but have a parent member with a docstring, sets their docstring to this parent docstring.

```python
class Base:
    attr = "hello"
    """Hello."""

    def hello(self):
        """Hello again."""
        ...

class Derived(Base):
    attr = "bye"

    def hello(self):
        ...
```

Following with example, *without* the extension `Derived.attr` and `Derived.hello` have no docstrings, while *with* the extension they will have the `Base.attr` and `Base.hello` docstrings attached, respectively.
