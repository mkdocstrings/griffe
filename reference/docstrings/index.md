# Docstrings

Griffe provides different docstring parsers allowing to extract even more structured data from source code.

The available parsers are:

- `google`, to parse Google-style docstrings, see [Napoleon's documentation](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)
- `numpy`, to parse Numpydoc docstrings, see [Numpydoc's documentation](https://numpydoc.readthedocs.io/en/latest/format.html)
- `sphinx`, to parse Sphinx-style docstrings, see [Sphinx's documentation](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html)
- `auto`, to automatically detect the docstring style, see [Auto-style](#auto-style)

Most of the time, the syntax specified in the aforementioned docs is supported. In some cases, the original syntax is not supported, or is supported but with subtle differences. We will try to document these differences in the following sections.

No assumption is made on the markup used in docstrings: it's retrieved as regular text. Tooling making use of Griffe can then choose to render the text as if it is Markdown, or AsciiDoc, or reStructuredText, etc..

## Google-style

Google-style docstrings, see [Napoleon's documentation](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).

### Syntax

Sections are written like this:

```
section identifier: optional section title
    section contents
```

All sections identifiers are case-insensitive. All sections support multiple lines in descriptions, as well as blank lines. The first line must not be blank. Each section must be separated from contents above by a blank line.

❌ This is **invalid** and will be parsed as regular markup:

```
Some text.
Note: # (1)!
    Some information.

    Blank lines allowed.
```

1. Missing blank line above.

❌ This is **invalid** and will be parsed as regular markup:

```
Some text.

Note: # (1)!

    Some information.

    Blank lines allowed.
```

1. Extraneous blank line below.

✅ This is **valid** and will parsed as a text section followed by a note admonition:

```
Some text.

Note:
    Some information.

    Blank lines allowed.
```

Find out possibly invalid section syntax by grepping for "reasons" in Griffe debug logs:

```
griffe dump -Ldebug -o/dev/null -fdgoogle your_package 2>&1 | grep reasons
```

Some sections support documenting multiple items (attributes, parameters, etc.). When multiple items are supported, each item description can use multiple lines, and continuation lines must be indented once more so that the parser is able to differentiate items.

```
def foo(a, b):
    """Foo.

    Parameters:
        a: Here's a.
            Continuation line 1.

            Continuation line 2.
        b: Here's b.
    """
```

It's possible to start a description with a newline if you find it less confusing:

```
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

### Admonitions

When a section identifier does not match one of the [supported sections](#google-sections), the section is parsed as an "admonition" (or "callout").

Identifiers are case-insensitive, however singular and plural forms are distinct. For example, `Note:` is not the same as `Notes:`.

In particular, `Examples` is parsed as the [Examples section](#google-section-examples), while `Example` is parsed as an admonition whose kind is `example`.

The kind is obtained by lower-casing the identifier and replacing spaces with dashes. For example, an admonition whose identifier is `See also:` will have a kind equal to `see-also`.

Custom section titles are preserved in admonitions: `Tip: Check this out:` is parsed as a `tip` admonition with `Check this out:` as title.

It is up to any downstream documentation renderer to make use of these kinds and titles.

### Parser options

The parser accepts a few options:

- `ignore_init_summary`: Ignore the first line in `__init__` methods' docstrings. Useful when merging `__init__` docstring into class' docstrings with mkdocstrings-python's [`merge_init_into_class`](https://mkdocstrings.github.io/python/usage/configuration/docstrings/#merge_init_into_class) option. Default: false.
- `returns_multiple_items`: Parse [Returns sections](#google-section-returns) and [Yields sections](#google-section-yields) as if they contain multiple items. It means that continuation lines must be indented. Default: true.
- `returns_named_value`: Whether to parse `thing: Description` in [Returns sections](#google-section-returns) and [Yields sections](#google-section-yields) as a name and description, rather than a type and description. When true, type must be wrapped in parentheses: `(int): Description.`. When false, parentheses are optional but the items cannot be named: `int: Description`. Default: true.
- `receives_multiple_items`: Parse [Receives sections](#google-section-receives) as if they contain multiple items. It means that continuation lines must be indented. Default: true.
- `receives_named_value`: Whether to parse `thing: Description` in [Receives sections](#google-section-receives) as a name and description, rather than a type and description. When true, type must be wrapped in parentheses: `(int): Description.`. When false, parentheses are optional but the items cannot be named: `int: Description`. Default: true.
- `returns_type_in_property_summary`: Whether to parse the return type of properties at the beginning of their summary: `str: Summary of the property`. Default: false.
- `trim_doctest_flags`: Remove the [doctest flags](https://docs.python.org/3/library/doctest.html#option-flags) written as comments in `pycon` snippets within a docstring. These flags are used to alter the behavior of [doctest](https://docs.python.org/3/library/doctest.html#module-doctest) when testing docstrings, and should not be visible in your docs. Default: true.
- `warn_unknown_params`: Warn about parameters documented in docstrings that do not appear in the signature. Default: true.
- `warn_missing_types`: Warn about missing type or annotation for parameters, return values, etc. Default: true.
- `warnings`: Generally enable/disable warnings when parsing docstrings. Default: true.

### Sections

The following sections are supported.

#### Attributes

- Multiple items allowed

Attributes sections allow to document attributes of a module, class, or class instance. They should be used in modules and classes docstrings only.

```
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

Type annotations are fetched from the related attributes definitions. You can override those by adding types between parentheses before the colon:

```
"""My module.

Attributes:
    foo (Integer): Description for `foo`.
    bar (Boolean): Description for `bar`.
"""
```

Types in docstrings are resolved using the docstrings' parent scope.

When documenting an attribute with `attr_name (attr_type): Attribute description`, `attr_type` will be resolved using the scope of the docstrings' parent object (class or module). For example, a type of `list[str]` will be parsed just as if it was an actual Python annotation. You can therefore use complex types (available in the current scope) in docstrings, for example `Optional[Union[int, Tuple[float, float]]]`.

#### Functions/Methods

- Multiple items allowed

Functions or Methods sections allow to document functions of a module, or methods of a class. They should be used in modules and classes docstrings only.

```
"""My module.

Functions:
    foo: Description for `foo`.
    bar: Description for `bar`.
"""


def foo():
    return "foo"


def bar(baz: int) -> int:
    return baz * 2


class MyClass:
    """My class.

    Methods:
        foofoo: Description for `foofoo`.
        barbar: Description for `barbar`.
    """

    def foofoo(self):
        return "foofoo"

    @staticmethod
    def barbar():
        return "barbar"
```

It's possible to write the function/method signature as well as its name:

```
"""
Functions:
    foo(): Description for `foo`.
    bar(baz=1): Description for `bar`.
"""
```

The signatures do not have to match the real ones: you can shorten them to only show the important parameters.

#### Classes

- Multiple items allowed

Classes sections allow to document classes of a module or class. They should be used in modules and classes docstrings only.

```
"""My module.

Classes:
    Foo: Description for `foo`.
    Bar: Description for `bar`.
"""


class Foo:
    ...


class Bar:
    def __init__(self, baz: int) -> int:
        return baz * 2


class MyClass:
    """My class.

    Classes:
        FooFoo: Description for `foofoo`.
        BarBar: Description for `barbar`.
    """

    class FooFoo:
        ...

    class BarBar:
        ...
```

It's possible to write the class signature as well as its name:

```
"""
Functions:
    Foo(): Description for `Foo`.
    Bar(baz=1): Description for `Bar`.
"""
```

The signatures do not have to match the real ones: you can shorten them to only show the important initialization parameters.

#### Modules

- Multiple items allowed

Modules sections allow to document submodules of a module. They should be used in modules docstrings only.

```
📁 my_pkg/
├──  __init__.py
├──  foo.py
└──  bar.py
```

my_pkg/__init__.py

```
"""My package.

Modules:
    foo: Description for `foo`.
    bar: Description for `bar`.
"""
```

#### Examples

Examples sections allow to add examples of Python code without the use of markup code blocks. They are a mix of prose and interactive console snippets. They can be used in every docstring.

```
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

Not the same as *Example* sections.

*Example* (singular) sections are parsed as admonitions. Console code blocks will only be understood in *Examples* (plural) sections.

#### Parameters

- Aliases: Args, Arguments, Params
- Multiple items allowed

Parameters sections allow to document parameters of a function. They are typically used in functions docstrings, but can also be used in dataclasses docstrings.

```
def foo(a: int, b: str):
    """Foo.

    Parameters:
        a: Here's a.
        b: Here's b.
    """
```

```
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

Type annotations are fetched from the related parameters definitions. You can override those by adding types between parentheses before the colon:

```
"""My function.

Parameters:
    foo (Integer): Description for `foo`.
    bar (String): Description for `bar`.
"""
```

Types in docstrings are resolved using the docstrings' parent scope.

When documenting a parameter with `param_name (param_type): Parameter description`, `param_type` will be resolved using the scope of the function (or class). For example, a type of `list[str]` will be parsed just as if it was an actual Python annotation. You can therefore use complex types (available in the current scope) in docstrings, for example `Optional[Union[int, Tuple[float, float]]]`.

#### Other Parameters

- Aliases: Keyword Args, Keyword Arguments, Other Args, Other Arguments, Other Params
- Multiple items allowed

Other parameters sections allow to document secondary parameters such as variadic keyword arguments, or parameters that should be of lesser interest to the user. They are used the same way Parameters sections are, but can also be useful in decorators / to document returned callables.

```
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

```
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

Types in docstrings are resolved using the docstrings' parent scope.

See the same tip for parameters.

#### Raises

- Aliases: Exceptions
- Multiple items allowed

Raises sections allow to document exceptions that are raised by a function. They are usually only used in functions docstrings.

```
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

Exceptions names are resolved using the function's scope.

`ValueError` and other built-in exceptions are resolved as such. You can document custom exception, using the names available in the current scope, for example `my_exceptions.MyCustomException` or `MyCustomException` directly, depending on what you imported/defined in the current module.

#### Warns

- Aliases: Warnings
- Multiple items allowed

Warns sections allow to document warnings emitted by the following code. They are usually only used in functions docstrings.

```
import warnings


def foo():
    """Foo.

    Warns:
        UserWarning: To annoy users.
    """
    warnings.warn("Just messing with you.", UserWarning)
```

Warnings names are resolved using the function's scope.

`UserWarning` and other built-in warnings are resolved as such. You can document custom warnings, using the names available in the current scope, for example `my_warnings.MyCustomWarning` or `MyCustomWarning` directly, depending on what you imported/defined in the current module.

#### Yields

- Multiple items allowed

Yields sections allow to document values that generator yield. They should be used only in generators docstrings. Documented items can be given a name when it makes sense.

```
from typing import Iterator


def foo() -> Iterator[int]:
    """Foo.

    Yields:
        Integers from 0 to 9.
    """
    for i in range(10):
        yield i
```

Type annotations are fetched from the function return annotation when the annotation is `typing.Generator` or `typing.Iterator`. If your generator yields tuples, you can document each item of the tuple separately, and the type annotation will be fetched accordingly:

```
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

You have to indent each continuation line when documenting yielded values, even if there's only one value yielded:

```
"""Foo.

Yields:
    partial_result: Some partial result.
        A longer description of details and other information
        for this partial result.
"""
```

If you don't want to indent continuation lines for the only yielded value, use the [`returns_multiple_items=False`](#google-options) parser option.

Type annotations can as usual be overridden using types in parentheses in the docstring itself:

```
"""Foo.

Yields:
    x (int): Absissa.
    y (int): Ordinate.
    t (int): Timestamp.
"""
```

If you want to specify the type without a name, you still have to wrap the type in parentheses:

```
"""Foo.

Yields:
    (int): Absissa.
    (int): Ordinate.
    (int): Timestamp.
"""
```

If you don't want to wrap the type in parentheses, use the [`returns_named_value=False`](#google-options) parser option. Setting it to false will disallow specifying a name.

Types in docstrings are resolved using the docstrings' parent scope.

See previous tips for types in docstrings.

#### Receives

- Multiple items allowed

Receives sections allow to document values that can be sent to generators using their `send` method. They should be used only in generators docstrings. Documented items can be given a name when it makes sense.

```
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

Type annotations are fetched from the function return annotation when the annotation is `typing.Generator`. If your generator is able to receive tuples, you can document each item of the tuple separately, and the type annotation will be fetched accordingly:

```
def foo() -> Generator[int, tuple[str, bool], None]:
    """Foo.

    Receives:
        mode: Some mode.
        flag: Some flag.

    ...
    """
    ...
```

You have to indent each continuation line when documenting received values, even if there's only one value received:

```
"""Foo.

Receives:
    data: Input data.
        A longer description of what this data actually is,
        and what it isn't.
"""
```

If you don't want to indent continuation lines for the only received value, use the [`receives_multiple_items=False`](#google-options) parser option.

Type annotations can as usual be overridden using types in parentheses in the docstring itself:

```
"""Foo.

Receives:
    mode (ModeEnum): Some mode.
    flag (int): Some flag.
"""
```

If you want to specify the type without a name, you still have to wrap the type in parentheses:

```
"""Foo.

Receives:
    (ModeEnum): Some mode.
    (int): Some flag.
"""
```

If you don't want to wrap the type in parentheses, use the [`receives_named_value=False`](#google-options) parser option. Setting it to false will disallow specifying a name.

Types in docstrings are resolved using the docstrings' parent scope.

See previous tips for types in docstrings.

#### Returns

- Multiple items allowed

Returns sections allow to document values returned by functions. They should be used only in functions docstrings. Documented items can be given a name when it makes sense.

```
import random


def foo() -> int:
    """Foo.

    Returns:
        A random integer.
    """
    return random.randint(0, 100)
```

Type annotations are fetched from the function return annotation. If your function returns tuples of values, you can document each item of the tuple separately, and the type annotation will be fetched accordingly:

```
def foo() -> tuple[bool, float]:
    """Foo.

    Returns:
        success: Whether it succeeded.
        precision: Final precision.

    ...
    """
    ...
```

You have to indent each continuation line when documenting returned values, even if there's only one value returned:

```
"""Foo.

Returns:
    success: Whether it succeeded.
        A longer description of what is considered success,
        and what is considered failure.
"""
```

If you don't want to indent continuation lines for the only returned value, use the [`returns_multiple_items=False`](#google-options) parser option.

Type annotations can as usual be overridden using types in parentheses in the docstring itself:

```
"""Foo.

Returns:
    success (int): Whether it succeeded.
    precision (Decimal): Final precision.
"""
```

If you want to specify the type without a name, you still have to wrap the type in parentheses:

```
"""Foo.

Returns:
    (int): Whether it succeeded.
    (Decimal): Final precision.
"""
```

If you don't want to wrap the type in parentheses, use the [`returns_named_value=False`](#google-options) parser option. Setting it to false will disallow specifying a name.

Types in docstrings are resolved using the docstrings' function scope.

See previous tips for types in docstrings.

## Numpydoc-style

Numpydoc docstrings, see [Numpydoc's documentation](https://numpydoc.readthedocs.io/en/latest/format.html)

### Syntax

Sections are written like this:

```
section identifier
------------------
section contents
```

All sections identifiers are case-insensitive. All sections support multiple lines in descriptions.

Some sections support documenting items items. Item descriptions start on a new, indented line. When multiple items are supported, each item description can use multiple lines.

```
def foo(a, b):
    """Foo.

    Parameters
    ----------
    a
        Here's a.
        Continuation line 1.

        Continuation line 2.
    b
        Here's b.
    """
```

For items that have an optional name and type, several syntaxes are supported:

- specifying both the name and type:

  ```
  """
  name : type
      description
  """
  ```

- specifying just the name:

  ```
  """
  name
      description
  """
  ```

  or

  ```
  """
  name :
      description
  """
  ```

- specifying just the type:

  ```
  """
  : type
      description
  """
  ```

- specifying neither the name nor type:

  ```
  """
  :
      description
  """
  ```

### Admonitions

When a section identifier does not match one of the [supported sections](#numpydoc-sections), the section is parsed as an "admonition" (or "callout").

Identifiers are case-insensitive, however singular and plural forms are distinct, except for notes and warnings. In particular, `Examples` is parsed as the [Examples section](#numpydoc-section-examples), while `Example` is parsed as an admonition whose kind is `example`.

The kind is obtained by lower-casing the identifier and replacing spaces with dashes. For example, an admonition whose identifier is `See also` will have a kind equal to `see-also`.

It is up to any downstream documentation renderer to make use of these kinds.

### Parser options

The parser accepts a few options:

- `ignore_init_summary`: Ignore the first line in `__init__` methods' docstrings. Useful when merging `__init__` docstring into class' docstrings with mkdocstrings-python's [`merge_init_into_class`](https://mkdocstrings.github.io/python/usage/configuration/docstrings/#merge_init_into_class) option. Default: false.
- `trim_doctest_flags`: Remove the [doctest flags](https://docs.python.org/3/library/doctest.html#option-flags) written as comments in `pycon` snippets within a docstring. These flags are used to alter the behavior of [doctest](https://docs.python.org/3/library/doctest.html#module-doctest) when testing docstrings, and should not be visible in your docs. Default: true.
- `warn_unknown_params`: Warn about parameters documented in docstrings that do not appear in the signature. Default: true.
- `warn_missing_types`: Warn about missing type or annotation for parameters, return values, etc. Default: true.
- `warnings`: Generally enable/disable warnings when parsing docstrings. Default: true.

### Sections

The following sections are supported.

#### Attributes

- Multiple items allowed

Attributes sections allow to document attributes of a module, class, or class instance. They should be used in modules and classes docstrings only.

```
"""My module.

Attributes
----------
foo
    Description for `foo`.
bar
    Description for `bar`.
"""

foo: int = 0
bar: bool = True


class MyClass:
    """My class.

    Attributes
    ----------
    foofoo
        Description for `foofoo`.
    barbar
        Description for `barbar`.
    """

    foofoo: int = 0

    def __init__(self):
        self.barbar: bool = True
```

Type annotations are fetched from the related attributes definitions. You can override those by adding types between parentheses before the colon:

```
"""My module.

Attributes
----------
foo : Integer
    Description for `foo`.
bar : Boolean
    Description for `bar`.
"""
```

Types in docstrings are resolved using the docstrings' parent scope.

When documenting an attribute with `attr_name : attr_type`, `attr_type` will be resolved using the scope of the docstrings' parent object (class or module). For example, a type of `list[str]` will be parsed just as if it was an actual Python annotation. You can therefore use complex types (available in the current scope) in docstrings, for example `Optional[Union[int, Tuple[float, float]]]`.

#### Functions/Methods

- Multiple items allowed

Functions or Methods sections allow to document functions of a module, or methods of a class. They should be used in modules and classes docstrings only.

```
"""My module.

Functions
---------
foo
    Description for `foo`.
bar
    Description for `bar`.
"""


def foo():
    return "foo"


def bar(baz: int) -> int:
    return baz * 2


class MyClass:
    """My class.

    Methods
    -------
    foofoo
        Description for `foofoo`.
    barbar
        Description for `barbar`.
    """

    def foofoo(self):
        return "foofoo"

    @staticmethod
    def barbar():
        return "barbar"
```

It's possible to write the function/method signature as well as its name:

```
"""
Functions
---------
foo()
    Description for `foo`.
bar(baz=1)
    Description for `bar`.
"""
```

The signatures do not have to match the real ones: you can shorten them to only show the important parameters.

#### Classes

- Multiple items allowed

Classes sections allow to document classes of a module or class. They should be used in modules and classes docstrings only.

```
"""My module.

Classes
-------
Foo
    Description for `foo`.
Bar
    Description for `bar`.
"""


class Foo:
    ...


class Bar:
    def __init__(self, baz: int) -> int:
        return baz * 2


class MyClass:
    """My class.

    Classes
    -------
    FooFoo
        Description for `foofoo`.
    BarBar
        Description for `barbar`.
    """

    class FooFoo:
        ...

    class BarBar:
        ...
```

It's possible to write the class signature as well as its name:

```
"""
Functions
---------
Foo()
    Description for `Foo`.
Bar(baz=1)
    Description for `Bar`.
"""
```

The signatures do not have to match the real ones: you can shorten them to only show the important initialization parameters.

#### Modules

- Multiple items allowed

Modules sections allow to document submodules of a module. They should be used in modules docstrings only.

```
📁 my_pkg/
├──  __init__.py
├──  foo.py
└──  bar.py
```

my_pkg/__init__.py

```
"""My package.

Modules
-------
foo
    Description for `foo`.
bar
    Description for `bar`.
"""
```

#### Examples

Examples sections allow to add examples of Python code without the use of markup code blocks. They are a mix of prose and interactive console snippets. They can be used in every docstring.

```
"""My module.

Examples
--------
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

#### Parameters

- Aliases: Args, Arguments, Params
- Multiple items allowed

Parameters sections allow to document parameters of a function. They are typically used in functions docstrings, but can also be used in dataclasses docstrings.

```
def foo(a: int, b: str):
    """Foo.

    Parameters
    ----------
    a
        Here's a.
    b
        Here's b.
    """
```

```
from dataclasses import dataclass


@dataclass
class Foo:
    """Foo.

    Parameters
    ----------
    a
        Here's a.
    b
        Here's b.
    """

    foo: int
    bar: str
```

Type annotations are fetched from the related parameters definitions. You can override those by adding types between parentheses before the colon:

```
"""My function.

Parameters
----------
foo : Integer
    Description for `foo`.
bar : String
    Description for `bar`.
"""
```

Types in docstrings are resolved using the docstrings' parent scope.

When documenting a parameter with `param_name : param_type`, `param_type` will be resolved using the scope of the function (or class). For example, a type of `list[str]` will be parsed just as if it was an actual Python annotation. You can therefore use complex types (available in the current scope) in docstrings, for example `Optional[Union[int, Tuple[float, float]]]`.

#### Other Parameters

- Aliases: Keyword Args, Keyword Arguments, Other Args, Other Arguments, Other Params
- Multiple items allowed

Other parameters sections allow to document secondary parameters such as variadic keyword arguments, or parameters that should be of lesser interest to the user. They are used the same way Parameters sections are.

```
def foo(a, b, **kwargs):
    """Foo.

    Parameters
    ----------
    a
        Here's a.
    b
        Here's b.

    Other parameters
    ----------------
    c : int
        Here's c.
    d : bool
        Here's d.
    """
```

Types in docstrings are resolved using the docstrings' parent scope.

See the same tip for parameters.

#### Raises

- Aliases: Exceptions
- Multiple items allowed

Raises sections allow to document exceptions that are raised by a function. They are usually only used in functions docstrings.

```
def foo(a: int):
    """Foo.

    Parameters
    ----------
    a
        A value.

    Raises
    ------
    ValueError
        When `a` is less than 0.
    """
    if a < 0:
        raise ValueError("message")
```

Exceptions names are resolved using the function's scope.

`ValueError` and other built-in exceptions are resolved as such. You can document custom exception, using the names available in the current scope, for example `my_exceptions.MyCustomException` or `MyCustomException` directly, depending on what you imported/defined in the current module.

#### Warns

- Multiple items allowed

Warns sections allow to document warnings emitted by the following code. They are usually only used in functions docstrings.

```
import warnings


def foo():
    """Foo.

    Warns
    -----
    UserWarning
        To annoy users.
    """
    warnings.warn("Just messing with you.", UserWarning)
```

Warnings names are resolved using the function's scope.

`UserWarning` and other built-in warnings are resolved as such. You can document custom warnings, using the names available in the current scope, for example `my_warnings.MyCustomWarning` or `MyCustomWarning` directly, depending on what you imported/defined in the current module.

#### Yields

- Multiple items allowed

Yields sections allow to document values that generator yield. They should be used only in generators docstrings. Documented items can be given a name when it makes sense.

```
from typing import Iterator


def foo() -> Iterator[int]:
    """Foo.

    Yields
    ------
    :
        Integers from 0 to 9.
    """
    for i in range(10):
        yield i
```

Type annotations are fetched from the function return annotation when the annotation is `typing.Generator` or `typing.Iterator`. If your generator yields tuples, you can document each item of the tuple separately, and the type annotation will be fetched accordingly:

```
from datetime import datetime


def foo() -> Iterator[tuple[float, float, datetime]]:
    """Foo.

    Yields
    ------
    x
        Absissa.
    y
        Ordinate.
    t
        Time.
    """
    ...
```

Type annotations can as usual be overridden using types in parentheses in the docstring itself:

```
"""Foo.

Yields
------
x : int
    Absissa.
y : int
    Ordinate.
t : int
    Timestamp.
"""
```

Types in docstrings are resolved using the docstrings' parent scope.

See previous tips for types in docstrings.

#### Receives

- Multiple items allowed

Receives sections allow to document values that can be sent to generators using their `send` method. They should be used only in generators docstrings. Documented items can be given a name when it makes sense.

```
from typing import Generator


def foo() -> Generator[int, str, None]:
    """Foo.

    Receives
    --------
    reverse
        Reverse the generator if `"reverse"` is received.

    Yields
    ------
    :
        Integers from 0 to 9.

    Examples
    --------
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

Type annotations are fetched from the function return annotation when the annotation is `typing.Generator`. If your generator is able to receive tuples, you can document each item of the tuple separately, and the type annotation will be fetched accordingly:

```
def foo() -> Generator[int, tuple[str, bool], None]:
    """Foo.

    Receives
    --------
    mode
        Some mode.
    flag
        Some flag.
    """
    ...
```

Type annotations can as usual be overridden using types in parentheses in the docstring itself:

```
"""Foo.

Receives
--------
mode : ModeEnum
    Some mode.
flag : int
    Some flag.
"""
```

Types in docstrings are resolved using the docstrings' parent scope.

See previous tips for types in docstrings.

#### Returns

- Multiple items allowed

Returns sections allow to document values returned by functions. They should be used only in functions docstrings. Documented items can be given a name when it makes sense.

```
import random


def foo() -> int:
    """Foo.

    Returns
    -------
    :
        A random integer.
    """
    return random.randint(0, 100)
```

Type annotations are fetched from the function return annotation. If your function returns tuples of values, you can document each item of the tuple separately, and the type annotation will be fetched accordingly:

```
def foo() -> tuple[bool, float]:
    """Foo.

    Returns
    -------
    success
        Whether it succeeded.
    precision
        Final precision.
    """
    ...
```

Type annotations can as usual be overridden using types in parentheses in the docstring itself:

```
"""Foo.

Returns
-------
success : int
    Whether it succeeded.
precision : Decimal
    Final precision.
"""
```

Types in docstrings are resolved using the docstrings' function scope.

See previous tips for types in docstrings.

## Auto-style

Automatic style detection. This parser will first try to detect the style used in the docstring, and call the corresponding parser on it.

### Parser options

The parser accepts a few options:

- `method`: The method to use to detect the style and infer the parser. Method 'heuristics' will use regular expressions, while method 'max_sections' will parse the docstring with all parsers specified in `style_order` and return the one who parsed the most sections. Default: `"heuristics"`.
- `style_order`: If multiple parsers parsed the same number of sections, `style_order` is used to decide which one to return. Default: `["sphinx", "google", "numpy"]`.
- `default`: If heuristics fail, the `default` parser is returned. The `default` parser is never used with the 'max_sections' method. Default: `None`.
- Any other option is passed down to the detected parser, if any.

## Parsers features

Want to contribute?

Each red cross is a link to an issue on the bugtracker. You will find some guidance on how to add support for the corresponding item.

The sections are easier to deal in that order:

- Raises, Warns (multiple items, no names, single type each)
- Attributes, Other Parameters, Parameters (multiple items, one name and one optional type each)
- Returns (multiple items, optional name and/or type each, annotation to split when multiple names)
- Receives, Yields (multiple items, optional name and/or type each, several types of annotations to split when multiple names)

"Examples" section are a bit different as they require to parse the examples. But you can probably reuse the code in the Google parser. We can probably even factorize the examples parsing into a single function.

You can tackle several items at once in a single PR, as long as they relate to a single parser or a single section (a line or a column of the following tables).

### Sections

| Section          | Google | Numpy | Sphinx                                                 |
| ---------------- | ------ | ----- | ------------------------------------------------------ |
| Attributes       | ✅     | ✅    | ✅                                                     |
| Functions        | ✅     | ✅    | ❌                                                     |
| Methods          | ✅     | ✅    | ❌                                                     |
| Classes          | ✅     | ✅    | ❌                                                     |
| Modules          | ✅     | ✅    | ❌                                                     |
| Examples         | ✅     | ✅    | [❌](https://github.com/mkdocstrings/griffe/issues/7)  |
| Parameters       | ✅     | ✅    | ✅                                                     |
| Other Parameters | ✅     | ✅    | [❌](https://github.com/mkdocstrings/griffe/issues/27) |
| Raises           | ✅     | ✅    | ✅                                                     |
| Warns            | ✅     | ✅    | [❌](https://github.com/mkdocstrings/griffe/issues/9)  |
| Yields           | ✅     | ✅    | [❌](https://github.com/mkdocstrings/griffe/issues/10) |
| Receives         | ✅     | ✅    | [❌](https://github.com/mkdocstrings/griffe/issues/8)  |
| Returns          | ✅     | ✅    | ✅                                                     |

### Getting annotations/defaults from parent

| Section          | Google | Numpy | Sphinx                                                 |
| ---------------- | ------ | ----- | ------------------------------------------------------ |
| Attributes       | ✅     | ✅    | [❌](https://github.com/mkdocstrings/griffe/issues/33) |
| Functions        | /      | /     | /                                                      |
| Methods          | /      | /     | /                                                      |
| Classes          | /      | /     | /                                                      |
| Modules          | /      | /     | /                                                      |
| Examples         | /      | /     | /                                                      |
| Parameters       | ✅     | ✅    | ✅                                                     |
| Other Parameters | ✅     | ✅    | [❌](https://github.com/mkdocstrings/griffe/issues/34) |
| Raises           | /      | /     | /                                                      |
| Warns            | /      | /     | /                                                      |
| Yields           | ✅     | ✅    | [❌](https://github.com/mkdocstrings/griffe/issues/36) |
| Receives         | ✅     | ✅    | [❌](https://github.com/mkdocstrings/griffe/issues/35) |
| Returns          | ✅     | ✅    | ✅                                                     |

### Cross-references for annotations in docstrings

| Section          | Google                                                  | Numpy                                                   | Sphinx                                                 |
| ---------------- | ------------------------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------ |
| Attributes       | ✅                                                      | ✅                                                      | [❌](https://github.com/mkdocstrings/griffe/issues/19) |
| Functions        | [❌](https://github.com/mkdocstrings/griffe/issues/199) | [❌](https://github.com/mkdocstrings/griffe/issues/200) | /                                                      |
| Methods          | [❌](https://github.com/mkdocstrings/griffe/issues/199) | [❌](https://github.com/mkdocstrings/griffe/issues/200) | /                                                      |
| Classes          | [❌](https://github.com/mkdocstrings/griffe/issues/199) | [❌](https://github.com/mkdocstrings/griffe/issues/200) | /                                                      |
| Modules          | /                                                       | /                                                       | /                                                      |
| Examples         | /                                                       | /                                                       | /                                                      |
| Parameters       | ✅                                                      | ✅                                                      | [❌](https://github.com/mkdocstrings/griffe/issues/21) |
| Other Parameters | ✅                                                      | ✅                                                      | [❌](https://github.com/mkdocstrings/griffe/issues/20) |
| Raises           | ✅                                                      | ✅                                                      | [❌](https://github.com/mkdocstrings/griffe/issues/22) |
| Warns            | ✅                                                      | ✅                                                      | [❌](https://github.com/mkdocstrings/griffe/issues/25) |
| Yields           | ✅                                                      | ✅                                                      | [❌](https://github.com/mkdocstrings/griffe/issues/26) |
| Receives         | ✅                                                      | ✅                                                      | [❌](https://github.com/mkdocstrings/griffe/issues/23) |
| Returns          | ✅                                                      | ✅                                                      | [❌](https://github.com/mkdocstrings/griffe/issues/24) |
