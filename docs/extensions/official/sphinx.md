# `griffe-sphinx`

[:octicons-heart-fill-24:{ .pulse } Sponsors only](../../insiders/index.md){ .insiders }

- **PyPI**: [`griffe-sphinx`](https://pypi.org/project/griffe-sphinx/)
- **GitHub**: [mkdocstrings/griffe-sphinx](https://github.com/mkdocstrings/griffe-sphinx)
- **Documentation:** [mkdocstrings.github.io/griffe-sphinx](https://mkdocstrings.github.io/griffe-sphinx)
- **Extension name:** `griffe_sphinx`

---

This extension reads Sphinx-comments above attribute assignments to use them as docstrings.

```python
#: Summary of `module_attr`. 
module_attr = "hello"


class Hello:
    #: Summary of `class_attr`.
    #:
    #: Description of the class attribute.
    #: *Markup* and [cross-references][] are __supported__,
    #: just like in regular docstrings.
    class_attr = "hello"

    def __init__(self):
        #: Summary of `instance_attr`.
        self.instance_attr = "hello"
```

Comments are treated exactly like regular docstrings: they are "cleaned" (dedented, stripped of leading and trailing new lines) and contain any markup you want, be it Markdown, rST, AsciiDoc, etc.

Trailing comments are not supported:

```python
module_attr  #: This is not supported.
```
