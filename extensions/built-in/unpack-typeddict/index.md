# `unpack_typeddict`

The `unpack_typeddict` extension adds support for Unpack and TypedDict from the standard library. When enabled, it will add an `__init__` method to typed dictionaries, and expand `**kwargs: Unpack[...]` (the ellipsis being a typed dict class) in function signatures to the relevant parameters, using the typed dict attributes or added signature. The extension will also update any Parameters section in the function docstring, to reflect the signature update.

Example:

```
from typing import TypedDict, Unpack


class GreetKwargs(TypedDict):
    name: str
    """The name of a person to greet."""
    shout: bool
    """Whether to shout."""


def greet(**kwargs: Unpack[GreetKwargs]) -> str:
    """Greet someone.

    Parameters:
        **kwargs: Greet parameters.

    Returns:
        A message.
    """
    message = f"Hello {kwargs['name']}!"
    if kwargs["shout"]:
        return message.upper() + "!!"
    return message
```

With the `unpack_typeddict` extension enabled, the data loaded by Griffe will be updated as follows:

```
class GreetKwargs(TypedDict):
    # Attributes removed from Griffe data.

    # Added by the extension to Griffe data (not to the runtime class):
    def __init__(self, *, name: str, shout: bool) -> None:
        """
        Parameters:
            name: The name of a person to greet.
            shout: Whether to shout.
        """


def greet(*, name: str, shout: bool) -> str:
    """Greet someone.

    Parameters:
        name: The name of a person to greet.
        shout: Whether to shout.

    Returns:
        A message.
    """
```

Thanks to this `__init__` method now appearing in the typed dictionary, tools like mkdocstrings can now render a proper signature for `GreetKwargs`.

Note

Our example shows a Google-style docstring, but we actually insert a structured docstring section into the parsed data, which is style-agnostic, so it works with any docstring style.

To enable the extension:

```
$ griffe dump -e unpack_typeddict my_package
```

```
import griffe

my_package = griffe.load("my_package", extensions=griffe.load_extensions("unpack_typeddict"))
```

mkdocs.yml

```
plugins:
- mkdocstrings:
    handlers:
      python:
        options:
          extensions:
          - unpack_typeddict
```
