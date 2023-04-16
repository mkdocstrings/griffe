# Docstrings

Griffe provides different docstring parsers allowing to extract
even more structured data from source code.

The available parsers are:

- `google`, to parse Google-style docstrings,
    see [Napoleon's documentation](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)
- `numpy`, to parse Numpydoc docstrings,
    see [Numpydoc's documentation](https://numpydoc.readthedocs.io/en/latest/format.html)
- `sphinx`, to parse Sphinx-style docstrings,
    see [Sphinx's documentation](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html)

## Syntax

Most of the time, the syntax specified in the aforementioned docs is supported.
In some cases, the original syntax is not supported, or is supported but with subtle differences.
We will try to document these differences in the following sections.

No assumption is made on the markup
used in docstrings: it's retrieved as regular text.
Tooling making use of Griffe can then choose to render
the text as if it is Markdown, or AsciiDoc, or reStructuredText, etc..

### Google-style

Sections are written like this:

```
section identifier: optional section title
    section contents
```

All sections identifiers are case-insensitive.
All sections support multiple lines in descriptions,
as well as blank lines.

Some sections also support documenting multiple items.
When multiple items are supported, each item description can
use multiple lines, and continuation lines must be indented once
more so that the parser is able to differentiate items.

```python
def foo(a, b):
    """Foo.

    Parameters:
        a: Here's a.
            Continuation line 1.

            Continuation line 2.
        b: Here's b.
    """
```

It's possible to start a description with a newline if you
find it less confusing:

```python
def foo(a, b):
    """Foo.

    Parameters:
        a:
            Here's a.
            Continuation line 1.

            Continuation line 2.
        b: Here's b.
    """
```

#### Attributes

- Multiple items allowed

Attributes sections allow to document attributes of a module, class, or class instance.
They should be used in modules and classes docstrings only.

```python
"""My module.

Attributes:
    foo: Description for `foo`.
    bar: Description for `bar`.
"""

foo: int = 0
bar: bool = True


class MyClass:
    """My class.

    Attributes:
        foofoo: Description for `foofoo`.
        barbar: Description for `barbar`.
    """

    foofoo: int = 0

    def __init__(self):
        self.barbar: bool = True
```

Type annotations are fetched from the related attributes definitions.
You can override those by adding types between parentheses before the colon:

```python
"""My module.

Attributes:
    foo (Integer): Description for `foo`.
    bar (Boolean): Description for `bar`.
"""
```

TIP: **Types in docstrings are resolved using the docstrings' parent scope.**  
When documenting an attribute with `attr_name (attr_type): Attribute description`, `attr_type`
will be resolved using the scope of the docstrings' parent object (class or module).
For example, a type of `list[str]` will be parsed just as if it was an actual Python annotation.
You can therefore use complex types (available in the current scope) in docstrings,
for example `Optional[Union[int, Tuple[float, float]]]`.

#### Deprecated

Deprecated sections allow to document a deprecation that happened at a particular version.
They can be used in every docstring.

```python
"""My module.

Deprecated:
    1.2: The `foo` attribute is deprecated.
"""

foo: int = 0
```

#### Examples

Examples sections allow to add examples of Python code without the use of markup code blocks.
They are a mix of prose and interactive console snippets.
They can be used in every docstring.

```python
"""My module.

Examples:
    Some explanation of what is possible.

    >>> print("hello!")
    hello!

    Blank lines delimit prose vs. console blocks.

    >>> a = 0
    >>> a += 1
    >>> a
    1
"""
```

WARNING: **Not the same as *Example* sections.**  
*Example* (singular) sections are parsed as admonitions.
Console code blocks will only be understood in *Examples* (plural) sections.

#### Parameters

- Aliases: Args, Arguments, Params
- Multiple items allowed

Parameters sections allow to document parameters of a function.
They are typically used in functions docstrings, but can also be used in dataclasses docstrings.

```python
def foo(a: int, b: str):
    """Foo.

    Parameters:
        a: Here's a.
        b: Here's b.
    """
```

```python
from dataclasses import dataclass


@dataclass
class Foo:
    """Foo.

    Parameters:
        a: Here's a.
        b: Here's b.
    """

    foo: int
    bar: str
```

Type annotations are fetched from the related parameters definitions.
You can override those by adding types between parentheses before the colon:

```python
"""My function.

Parameters:
    foo (Integer): Description for `foo`.
    bar (String): Description for `bar`.
"""
```

TIP: **Types in docstrings are resolved using the docstrings' parent scope.**  
When documenting a parameter with `param_name (param_type): Parameter description`, `param_type`
will be resolved using the scope of the function (or class).
For example, a type of `list[str]` will be parsed just as if it was an actual Python annotation.
You can therefore use complex types (available in the current scope) in docstrings,
for example `Optional[Union[int, Tuple[float, float]]]`.

#### Other Parameters

- Aliases: Keyword Args, Keyword Arguments, Other Params
- Multiple items allowed

Other parameters sections allow to document secondary parameters such as variadic keyword arguments,
or parameters that should be of lesser interest to the user.
They are used the same way Parameters sections are,
but can also be useful in decorators / to document returned callables.

```python
def foo(a, b, **kwargs):
    """Foo.

    Parameters:
        a: Here's a.
        b: Here's b.

    Other parameters:
        c (int): Here's c.
        d (bool): Here's d.
    """
```

```python
def foo(a, b):
    """Returns a callable.

    Parameters:
        a: Here's a.
        b: Here's b.

    Other parameters: Parameters of the returned callable:
        c (int): Here's c.
        d (bool): Here's d.
    """

    def inner(c, d):
        ...

    return inner
```

TIP: **Types in docstrings are resolved using the docstrings' parent scope.**  
See the same tip for parameters.

#### Raises

- Aliases: Exceptions
- Multiple items allowed

Raises sections allow to document exceptions that are raised by a function.
They are usually only used in functions docstrings.

```python
def foo(a: int):
    """Foo.

    Parameters:
        a: A value.

    Raises:
        ValueError: When `a` is less than 0.
    """
    if a < 0:
        raise ValueError("message")
```

TIP: **Exceptions names are resolved using the function's scope.**  
`ValueError` and other built-in exceptions are resolved as such.
You can document custom exception, using the names available in the current scope,
for example `my_exceptions.MyCustomException` or `MyCustomException` directly,
depending on what you imported/defined in the current module.

#### Receives

- Multiple items allowed

Receives sections allow to document values that can be sent to generators
using their `send` method.
They should be used only in generators docstrings.
Documented items can be given a name when it makes sense.

```python
from typing import Generator


def foo() -> Generator[int, str, None]:
    """Foo.

    Receives:
        reverse: Reverse the generator if `"reverse"` is received.

    Yields:
        Integers from 0 to 9.

    Examples:
        >>> gen = foo()
        >>> next(gen)
        0
        >>> next(gen)
        1
        >>> next(gen)
        2
        >>> gen.send("reverse")
        2
        >>> next(gen)
        1
        >>> next(gen)
        0
        >>> next(gen)
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        StopIteration
    """
    for i in range(10):
        received = yield i
        if received == "reverse":
            for j in range(i, -1, -1):
                yield j
            break
```

Type annotations are fetched from the function return annotation
when the annotation is `typing.Generator`. If your generator is able
to receive tuples, you can document each item of the tuple separately,
and the type annotation will be fetched accordingly:

```python
def foo() -> Generator[int, tuple[str, bool], None]:
    """Foo.

    Receives:
        mode: Some mode.
        flag: Some flag.

    ...
    """
    ...
```

Type annotations can as usual be overridden using types in parentheses
in the docstring itself:

```python
"""Foo.

Receives:
    mode (ModeEnum): Some mode.
    flag (int): Some flag.
"""
```

TIP: **Types in docstrings are resolved using the docstrings' parent scope.**  
See previous tips for types in docstrings.

#### Returns

- Multiple items allowed

Returns sections allow to document values returned by functions.
They should be used only in functions docstrings.
Documented items can be given a name when it makes sense.

```python
import random


def foo() -> int:
    """Foo.

    Returns:
        A random integer.
    """
    return random.randint(0, 100)
```

Type annotations are fetched from the function return annotation.
If your function returns tuples of values, you can document each item of the tuple separately,
and the type annotation will be fetched accordingly:

```python
def foo() -> tuple[bool, float]:
    """Foo.

    Returns:
        success: Whether it succeeded.
        precision: Final precision.

    ...
    """
    ...
```

Type annotations can as usual be overridden using types in parentheses
in the docstring itself:

```python
"""Foo.

Returns:
    success (int): Whether it succeeded.
    precision (Decimal): Final precision.
"""
```

TIP: **Types in docstrings are resolved using the docstrings' function scope.**  
See previous tips for types in docstrings.

WARNING: **Continuation lines for a single returned item must still be indented.**  
Even when your function returns a single value, you must indent continuation
lines of its description so that the parser does not think you are documenting
multiple items.

#### Warns

- Aliases: Warnings
- Multiple items allowed

Warns sections allow to document warnings emitted by the following code.
They are usually only used in functions docstrings.

```python
import warnings


def foo():
    """Foo.

    Warns:
        UserWarning: To annoy users.
    """
    warnings.warn("Just messing with you.", UserWarning)
```

TIP: **Warnings names are resolved using the function's scope.**  
`UserWarning` and other built-in warnings are resolved as such.
You can document custom warnings, using the names available in the current scope,
for example `my_warnings.MyCustomWarning` or `MyCustomWarning` directly,
depending on what you imported/defined in the current module.

#### Yields

- Multiple items allowed

Yields sections allow to document values that generator yield.
They should be used only in generators docstrings.
Documented items can be given a name when it makes sense.

```python
from typing import Iterator


def foo() -> Iterator[int]:
    """Foo.

    Yields:
        Integers from 0 to 9.
    """
    for i in range(10):
        yield i
```

Type annotations are fetched from the function return annotation
when the annotation is `typing.Generator` or `typing.Iterator`.
If your generator yields tuples, you can document each item of the tuple separately,
and the type annotation will be fetched accordingly:

```python
from datetime import datetime


def foo() -> Iterator[tuple[float, float, datetime]]:
    """Foo.

    Yields:
        x: Absissa.
        y: Ordinate.
        t: Time.

    ...
    """
    ...
```

Type annotations can as usual be overridden using types in parentheses
in the docstring itself:

```python
"""Foo.

Yields:
    x (int): Absissa.
    y (int): Ordinate.
    t (int): Timestamp.
"""
```

TIP: **Types in docstrings are resolved using the docstrings' parent scope.**  
See previous tips for types in docstrings.

## Parsers features

!!! tip "Want to contribute?"
    Each red cross is a link to an issue on the bugtracker.
    You will find some guidance on how to add support for the corresponding item.

    The sections are easier to deal in that order:

    - Deprecated (single item, version and text)
    - Raises, Warns (multiple items, no names, single type each)
    - Attributes, Other Parameters, Parameters (multiple items, one name and one optional type each)
    - Returns (multiple items, optional name and/or type each, annotation to split when multiple names)
    - Receives, Yields (multiple items, optional name and/or type each, several types of annotations to split when multiple names)

    "Examples" section are a bit different as they require to parse the examples.
    But you can probably reuse the code in the Google parser.
    We can probably even factorize the examples parsing into a single function.

    You can tackle several items at once in a single PR,
    as long as they relate to a single parser or a single section
    (a line or a column of the following tables).

### Sections

Section          | Google | Numpy | Sphinx
---------------- | ------ | ----- | ------
Attributes       | ✅     | ✅    | ✅
Deprecated       | ✅     | ✅[^1]| [❌][issue-section-sphinx-deprecated]
Examples         | ✅     | ✅    | [❌][issue-section-sphinx-examples]
Other Parameters | ✅     | ✅    | [❌][issue-section-sphinx-other-parameters]
Parameters       | ✅     | ✅    | ✅
Raises           | ✅     | ✅    | ✅
Receives         | ✅     | ✅    | [❌][issue-section-sphinx-receives]
Returns          | ✅     | ✅    | ✅
Warns            | ✅     | ✅    | [❌][issue-section-sphinx-warns]
Yields           | ✅     | ✅    | [❌][issue-section-sphinx-yields]

[^1]: Support for a regular section instead of the RST directive specified in the [Numpydoc styleguide](https://numpydoc.readthedocs.io/en/latest/format.html#deprecation-warning).


[issue-section-sphinx-deprecated]: https://github.com/mkdocstrings/griffe/issues/6
[issue-section-sphinx-examples]: https://github.com/mkdocstrings/griffe/issues/7
[issue-section-sphinx-other-parameters]: https://github.com/mkdocstrings/griffe/issues/27
[issue-section-sphinx-receives]: https://github.com/mkdocstrings/griffe/issues/8
[issue-section-sphinx-warns]: https://github.com/mkdocstrings/griffe/issues/9
[issue-section-sphinx-yields]: https://github.com/mkdocstrings/griffe/issues/10

### Getting annotations/defaults from parent

Section          | Google | Numpy | Sphinx
---------------- | ------ | ----- | ------
Attributes       | ✅     | ✅    | [❌][issue-parent-sphinx-attributes]
Deprecated       | /      | /     | /
Examples         | /      | /     | /
Other Parameters | ✅     | ✅    | [❌][issue-parent-sphinx-other-parameters]
Parameters       | ✅     | ✅    | ✅
Raises           | /      | /     | /
Receives         | ✅     | ✅    | [❌][issue-parent-sphinx-receives]
Returns          | ✅     | ✅    | ✅
Warns            | /      | /     | /
Yields           | ✅     | ✅    | [❌][issue-parent-sphinx-yields]

[issue-parent-sphinx-attributes]: https://github.com/mkdocstrings/griffe/issues/33
[issue-parent-sphinx-other-parameters]: https://github.com/mkdocstrings/griffe/issues/34
[issue-parent-sphinx-receives]: https://github.com/mkdocstrings/griffe/issues/35
[issue-parent-sphinx-yields]: https://github.com/mkdocstrings/griffe/issues/36

### Cross-references for annotations in docstrings

Section          | Google | Numpy | Sphinx
---------------- | ------ | ----- | ------
Attributes       | ✅     | ✅    | [❌][issue-xref-sphinx-attributes]
Deprecated       | /      | /     | /
Examples         | /      | /     | /
Other Parameters | ✅     | ✅    | [❌][issue-xref-sphinx-other-parameters]
Parameters       | ✅     | ✅    | [❌][issue-xref-sphinx-parameters]
Raises           | ✅     | ✅    | [❌][issue-xref-sphinx-raises]
Receives         | ✅     | ✅    | [❌][issue-xref-sphinx-receives]
Returns          | ✅     | ✅    | [❌][issue-xref-sphinx-returns]
Warns            | ✅     | ✅    | [❌][issue-xref-sphinx-warns]
Yields           | ✅     | ✅    | [❌][issue-xref-sphinx-yields]

[issue-xref-sphinx-attributes]: https://github.com/mkdocstrings/griffe/issues/19
[issue-xref-sphinx-other-parameters]: https://github.com/mkdocstrings/griffe/issues/20
[issue-xref-sphinx-parameters]: https://github.com/mkdocstrings/griffe/issues/21
[issue-xref-sphinx-raises]: https://github.com/mkdocstrings/griffe/issues/22
[issue-xref-sphinx-receives]: https://github.com/mkdocstrings/griffe/issues/23
[issue-xref-sphinx-returns]: https://github.com/mkdocstrings/griffe/issues/24
[issue-xref-sphinx-warns]: https://github.com/mkdocstrings/griffe/issues/25
[issue-xref-sphinx-yields]: https://github.com/mkdocstrings/griffe/issues/26

### Parsing options

Option                     | Google | Numpy | Sphinx
-------------------------- | ------ | ----- | ------
Ignore `__init__` summary  | ✅     | ✅    | [❌][issue-ignore-init-summary-sphinx]
Trim doctest flags         | ✅     | ✅    | [❌][issue-trim-doctest-flags-sphinx]
Warn about unknown params  | ✅     | ✅    | [❌][issue-warn-unknown-params-sphinx]

[issue-ignore-init-summary-sphinx]: https://github.com/mkdocstrings/griffe/issues/45
[issue-trim-doctest-flags-sphinx]: https://github.com/mkdocstrings/griffe/issues/49
[issue-warn-unknown-params-sphinx]: https://github.com/mkdocstrings/griffe/issues/64
