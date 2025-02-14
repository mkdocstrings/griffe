# `griffe-inherited-docstrings`

- **PyPI**: [`griffe-inherited-docstrings`](https://pypi.org/project/griffe-inherited-docstrings/)
- **GitHub**: [mkdocstrings/griffe-inherited-docstrings](https://github.com/mkdocstrings/griffe-inherited-docstrings)
- **Documentation:** [mkdocstrings.github.io/griffe-inherited-docstrings](https://mkdocstrings.github.io/griffe-inherited-docstrings)
- **Extension name:** `griffe_inherited_docstrings`

---

This extension, when enabled, iterates over the declared members of all classes found within a package, and if they don't have a docstring, but do have a parent member with a docstring, sets their docstring to that parent's docstring.

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

In the example above, *without* the extension `Derived.attr` and `Derived.hello` have no docstrings, while *with* the extension they will have the `Base.attr` and `Base.hello` docstrings attached, respectively.
