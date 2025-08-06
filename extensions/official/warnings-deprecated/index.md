# `griffe-warnings-deprecated`

- **PyPI**: [`griffe-warnings-deprecated`](https://pypi.org/project/griffe-warnings-deprecated/)
- **GitHub**: [mkdocstrings/griffe-warnings-deprecated](https://github.com/mkdocstrings/griffe-warnings-deprecated)
- **Documentation:** [mkdocstrings.github.io/griffe-warnings-deprecated](https://mkdocstrings.github.io/griffe-warnings-deprecated)
- **Extension name:** `griffe_warnings_deprecated`

______________________________________________________________________

This extension adds support for functions and classes decorated with @warnings.deprecated(...), as implemented thanks to [PEP 702](https://peps.python.org/pep-0702/). The message provided in the decorator call will be stored in the corresponding Griffe object's deprecated attribute (usable by downstream rendering templates), and will also add an admonition to the object's docstring with the provided message as text.

```
from warnings import deprecated

@deprecated("This function is **deprecated**. Use [another one][package.another_func] instead.")
def deprecated_func():
    ...


def another_func():
    ...

```
