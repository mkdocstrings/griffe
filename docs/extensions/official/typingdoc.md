# `griffe-typingdoc`

- **PyPI**: [`griffe-typingdoc`](https://pypi.org/project/griffe-typingdoc/)
- **GitHub**: [mkdocstrings/griffe-typingdoc](https://github.com/mkdocstrings/griffe-typingdoc)
- **Documentation:** [mkdocstrings.github.io/griffe-typingdoc](https://mkdocstrings.github.io/griffe-typingdoc)
- **Extension name:** `griffe_typingdoc`

---

This extension reads docstrings for parameters, return values and more from type annotation using [`Annotated`][typing.Annotated] and the [`Doc`][typing_extensions.Doc] class suggested in [PEP 727](https://peps.python.org/pep-0727/). Documenting parameters and return values this way makes it possible to completely avoid relying on a particular "docstring style" (Google, Numpydoc, Sphinx, etc.) and just use plain markup in module/classes/function docstrings. Docstrings therefore do not have to be parsed at all.

```python
from typing import Annotated as An
from typing_extensions import Doc


def function(
    param1: An[int, Doc("Some integer value.")],
    param2: An[
        str,
        Doc(
            """
            Summary of the parameter.

            Multi-line docstrings can be used, as usual.
            Any **markup** is supported, as usual.
            """
        )
    ]
) -> An[bool, Doc("Whether you like PEP 727.")]:
    """Summary of the function.

    No more "Args", "Parameters" or "Returns" sections.
    Just plain markup.
    """
    ...
```

PEP 727 is likely to be withdrawn or rejected, but the `Doc` class will remain in `typing_extensions`, [as told by Jelle Zijlstra](https://discuss.python.org/t/pep-727-documentation-metadata-in-typing/32566/183):

> We’ll probably keep it in `typing_extensions` indefinitely even if the PEP gets withdrawn or rejected, for backwards compatibility reasons.
>
> You are free to use it in your own code using the typing-extensions version. If usage of `typing_extensions.Doc` becomes widespread, that will be a good argument for accepting the PEP and putting it in the standard library.
