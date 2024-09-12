# Docstrings

Griffe provides different docstring parsers allowing to extract even more structured data from source code.

The available parsers are:

- `google`, to parse Google-style docstrings, see [Napoleon's documentation][napoleon]
- `numpy`, to parse Numpydoc docstrings, see [Numpydoc's documentation][numpydoc]
- `sphinx`, to parse Sphinx-style docstrings, see [Sphinx's documentation][sphinx]
- `auto` (sponsors only), to automatically detect the docstring style, see [Auto-style](#auto-style)

Most of the time, the syntax specified in the aforementioned docs is supported. In some cases, the original syntax is not supported, or is supported but with subtle differences. We will try to document these differences in the following sections.

No assumption is made on the markup used in docstrings: it's retrieved as regular text. Tooling making use of Griffe can then choose to render the text as if it is Markdown, or AsciiDoc, or reStructuredText, etc..

## Google-style

Google-style docstrings, see [Napoleon's documentation][napoleon].

### Syntax {#google-syntax}

Sections are written like this:

```
section identifier: optional section title
    section contents
```

All sections identifiers are case-insensitive. All sections support multiple lines in descriptions, as well as blank lines. The first line must not be blank. Each section must be separated from contents above by a blank line.

❌ This is **invalid** and will be parsed as regular markup:

```python
Some text.
Note: # (1)!
    Some information.

    Blank lines allowed.
```

1. Missing blank line above.

❌ This is **invalid** and will be parsed as regular markup:

```python
Some text.

Note: # (1)!

    Some information.

    Blank lines allowed.
```

1. Extraneous blank line below.

✅ This is **valid** and will parsed as a text section followed by a note admonition:

```python
Some text.

Note:
    Some information.

    Blank lines allowed.
```

Find out possibly invalid section syntax by grepping for "reasons" in Griffe debug logs:

```bash
griffe dump -Ldebug -o/dev/null -fdgoogle your_package 2>&1 | grep reasons
```

Some sections support documenting multiple items (attributes, parameters, etc.). When multiple items are supported, each item description can use multiple lines, and continuation lines must be indented once more so that the parser is able to differentiate items.

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

It's possible to start a description with a newline if you find it less confusing:

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

### Admonitions {#google-admonitions}

When a section identifier does not match one of the [supported sections](#google-sections), the section is parsed as an "admonition" (or "callout").

Identifiers are case-insensitive, however singular and plural forms are distinct. For example, `Note:` is not the same as `Notes:`.

In particular, `Examples` is parsed as the [Examples section](#google-section-examples), while `Example` is parsed as an admonition whose kind is `example`.

The kind is obtained by lower-casing the identifier and replacing spaces with dashes. For example, an admonition whose identifier is `See also:` will have a kind equal to `see-also`.

Custom section titles are preserved in admonitions: `Tip: Check this out:` is parsed as a `tip` admonition with `Check this out:` as title.

It is up to any downstream documentation renderer to make use of these kinds and titles.

### Parser options {#google-options}

The parser accepts a few options:

- `ignore_init_summary`: Ignore the first line in `__init__` methods' docstrings. Useful when merging `__init__` docstring into class' docstrings with mkdocstrings-python's [`merge_init_into_class`][merge_init] option. Default: false.
- `returns_multiple_items`: Parse [Returns sections](#google-section-returns) and [Yields sections](#google-section-yields) as if they contain multiple items. It means that continuation lines must be indented. Default: true.
- `returns_named_value`: Whether to parse `thing: Description` in [Returns sections](#google-section-returns) and [Yields sections](#google-section-yields) as a name and description, rather than a type and description. When true, type must be wrapped in parentheses: `(int): Description.`. When false, parentheses are optional but the items cannot be named: `int: Description`. Default: true.
- `receives_multiple_items`: Parse [Receives sections](#google-section-receives) as if they contain multiple items. It means that continuation lines must be indented. Default: true.
- `receives_named_value`: Whether to parse `thing: Description` in [Receives sections](#google-section-receives) as a name and description, rather than a type and description. When true, type must be wrapped in parentheses: `(int): Description.`. When false, parentheses are optional but the items cannot be named: `int: Description`. Default: true.
- `returns_type_in_property_summary`: Whether to parse the return type of properties at the beginning of their summary: `str: Summary of the property`. Default: false.
- `trim_doctest_flags`: Remove the [doctest flags] written as comments in `pycon` snippets within a docstring. These flags are used to alter the behavior of [doctest] when testing docstrings, and should not be visible in your docs. Default: true.
- `warn_unknown_params`: Warn about parameters documented in docstrings that do not appear in the signature. Default: true.

### Sections {#google-sections}

The following sections are supported.

#### Attributes {#google-section-attributes}

- Multiple items allowed

Attributes sections allow to document attributes of a module, class, or class instance. They should be used in modules and classes docstrings only.

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

Type annotations are fetched from the related attributes definitions. You can override those by adding types between parentheses before the colon:

```python
"""My module.

Attributes:
    foo (Integer): Description for `foo`.
    bar (Boolean): Description for `bar`.
"""
```

TIP: **Types in docstrings are resolved using the docstrings' parent scope.**  
When documenting an attribute with `attr_name (attr_type): Attribute description`, `attr_type` will be resolved using the scope of the docstrings' parent object (class or module). For example, a type of `list[str]` will be parsed just as if it was an actual Python annotation. You can therefore use complex types (available in the current scope) in docstrings, for example `Optional[Union[int, Tuple[float, float]]]`.

#### Functions/Methods {#google-section-functions}

- Multiple items allowed

Functions or Methods sections allow to document functions of a module, or methods of a class. They should be used in modules and classes docstrings only.

```python
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

```python
"""
Functions:
    foo(): Description for `foo`.
    bar(baz=1): Description for `bar`.
"""
```

The signatures do not have to match the real ones: you can shorten them to only show the important parameters.

#### Classes {#google-section-classes}

- Multiple items allowed

Classes sections allow to document classes of a module or class. They should be used in modules and classes docstrings only.

```python
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

```python
"""
Functions:
    Foo(): Description for `Foo`.
    Bar(baz=1): Description for `Bar`.
"""
```

The signatures do not have to match the real ones: you can shorten them to only show the important initialization parameters.

#### Modules {#google-section-modules}

- Multiple items allowed

Modules sections allow to document submodules of a module. They should be used in modules docstrings only.

```tree
my_pkg/
    __init__.py
    foo.py
    bar.py
```

```python title="my_pkg/__init__.py"
"""My package.

Modules:
    foo: Description for `foo`.
    bar: Description for `bar`.
"""
```

#### Deprecated {#google-section-deprecated}

Deprecated sections allow to document a deprecation that happened at a particular version. They can be used in every docstring.

```python
"""My module.

Deprecated:
    1.2: The `foo` attribute is deprecated.
"""

foo: int = 0
```

#### Examples {#google-section-examples}

Examples sections allow to add examples of Python code without the use of markup code blocks. They are a mix of prose and interactive console snippets. They can be used in every docstring.

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
*Example* (singular) sections are parsed as admonitions. Console code blocks will only be understood in *Examples* (plural) sections.

#### Parameters {#google-section-parameters}

- Aliases: Args, Arguments, Params
- Multiple items allowed

Parameters sections allow to document parameters of a function. They are typically used in functions docstrings, but can also be used in dataclasses docstrings.

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

Type annotations are fetched from the related parameters definitions. You can override those by adding types between parentheses before the colon:

```python
"""My function.

Parameters:
    foo (Integer): Description for `foo`.
    bar (String): Description for `bar`.
"""
```

TIP: **Types in docstrings are resolved using the docstrings' parent scope.**  
When documenting a parameter with `param_name (param_type): Parameter description`, `param_type` will be resolved using the scope of the function (or class). For example, a type of `list[str]` will be parsed just as if it was an actual Python annotation. You can therefore use complex types (available in the current scope) in docstrings, for example `Optional[Union[int, Tuple[float, float]]]`.

#### Other Parameters {#google-section-other-parameters}

- Aliases: Keyword Args, Keyword Arguments, Other Args, Other Arguments, Other Params
- Multiple items allowed

Other parameters sections allow to document secondary parameters such as variadic keyword arguments, or parameters that should be of lesser interest to the user. They are used the same way Parameters sections are, but can also be useful in decorators / to document returned callables.

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

#### Raises {#google-section-raises}

- Aliases: Exceptions
- Multiple items allowed

Raises sections allow to document exceptions that are raised by a function. They are usually only used in functions docstrings.

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
`ValueError` and other built-in exceptions are resolved as such. You can document custom exception, using the names available in the current scope, for example `my_exceptions.MyCustomException` or `MyCustomException` directly, depending on what you imported/defined in the current module.

#### Warns {#google-section-warns}

- Aliases: Warnings
- Multiple items allowed

Warns sections allow to document warnings emitted by the following code. They are usually only used in functions docstrings.

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
`UserWarning` and other built-in warnings are resolved as such. You can document custom warnings, using the names available in the current scope, for example `my_warnings.MyCustomWarning` or `MyCustomWarning` directly, depending on what you imported/defined in the current module.

#### Yields {#google-section-yields}

- Multiple items allowed

Yields sections allow to document values that generator yield. They should be used only in generators docstrings. Documented items can be given a name when it makes sense.

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

Type annotations are fetched from the function return annotation when the annotation is `typing.Generator` or `typing.Iterator`. If your generator yields tuples, you can document each item of the tuple separately, and the type annotation will be fetched accordingly:

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

You have to indent each continuation line when documenting yielded values, even if there's only one value yielded:

```python
"""Foo.

Yields:
    partial_result: Some partial result.
        A longer description of details and other information
        for this partial result.
"""
```

If you don't want to indent continuation lines for the only yielded value, use the [`returns_multiple_items=False`](#google-options) parser option.

Type annotations can as usual be overridden using types in parentheses in the docstring itself:

```python
"""Foo.

Yields:
    x (int): Absissa.
    y (int): Ordinate.
    t (int): Timestamp.
"""
```

If you want to specify the type without a name, you still have to wrap the type in parentheses:

```python
"""Foo.

Yields:
    (int): Absissa.
    (int): Ordinate.
    (int): Timestamp.
"""
```

If you don't want to wrap the type in parentheses, use the [`returns_named_value=False`](#google-options) parser option. Setting it to false will disallow specifying a name.

TIP: **Types in docstrings are resolved using the docstrings' parent scope.**  
See previous tips for types in docstrings.

#### Receives {#google-section-receives}

- Multiple items allowed

Receives sections allow to document values that can be sent to generators using their `send` method. They should be used only in generators docstrings. Documented items can be given a name when it makes sense.

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

Type annotations are fetched from the function return annotation when the annotation is `typing.Generator`. If your generator is able to receive tuples, you can document each item of the tuple separately, and the type annotation will be fetched accordingly:

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

You have to indent each continuation line when documenting received values, even if there's only one value received:

```python
"""Foo.

Receives:
    data: Input data.
        A longer description of what this data actually is,
        and what it isn't.
"""
```

If you don't want to indent continuation lines for the only received value, use the [`receives_multiple_items=False`](#google-options) parser option.

Type annotations can as usual be overridden using types in parentheses in the docstring itself:

```python
"""Foo.

Receives:
    mode (ModeEnum): Some mode.
    flag (int): Some flag.
"""
```

If you want to specify the type without a name, you still have to wrap the type in parentheses:

```python
"""Foo.

Receives:
    (ModeEnum): Some mode.
    (int): Some flag.
"""
```

If you don't want to wrap the type in parentheses, use the [`receives_named_value=False`](#google-options) parser option. Setting it to false will disallow specifying a name.

TIP: **Types in docstrings are resolved using the docstrings' parent scope.**  
See previous tips for types in docstrings.

#### Returns {#google-section-returns}

- Multiple items allowed

Returns sections allow to document values returned by functions. They should be used only in functions docstrings. Documented items can be given a name when it makes sense.

```python
import random


def foo() -> int:
    """Foo.

    Returns:
        A random integer.
    """
    return random.randint(0, 100)
```

Type annotations are fetched from the function return annotation. If your function returns tuples of values, you can document each item of the tuple separately, and the type annotation will be fetched accordingly:

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

You have to indent each continuation line when documenting returned values, even if there's only one value returned:

```python
"""Foo.

Returns:
    success: Whether it succeeded.
        A longer description of what is considered success,
        and what is considered failure.
"""
```

If you don't want to indent continuation lines for the only returned value, use the [`returns_multiple_items=False`](#google-options) parser option.

Type annotations can as usual be overridden using types in parentheses in the docstring itself:

```python
"""Foo.

Returns:
    success (int): Whether it succeeded.
    precision (Decimal): Final precision.
"""
```

If you want to specify the type without a name, you still have to wrap the type in parentheses:

```python
"""Foo.

Returns:
    (int): Whether it succeeded.
    (Decimal): Final precision.
"""
```

If you don't want to wrap the type in parentheses, use the [`returns_named_value=False`](#google-options) parser option. Setting it to false will disallow specifying a name.

TIP: **Types in docstrings are resolved using the docstrings' function scope.**  
See previous tips for types in docstrings.

## Numpydoc-style

Numpydoc docstrings, see [Numpydoc's documentation][numpydoc]

### Syntax {#numpydoc-syntax}

Sections are written like this:

```
section identifier
------------------
section contents
```

All sections identifiers are case-insensitive. All sections support multiple lines in descriptions.

Some sections support documenting items items. Item descriptions start on a new, indented line. When multiple items are supported, each item description can use multiple lines.

```python
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

    ```python
    """
    name : type
        description
    """
    ```

- specifying just the name:

    ```python
    """
    name
        description
    """
    ```

    or

    ```python
    """
    name :
        description
    """
    ```

- specifying just the type:

    ```python
    """
    : type
        description
    """
    ```

- specifying neither the name nor type:

    ```python
    """
    :
        description
    """
    ```

### Admonitions {#numpydoc-admonitions}

When a section identifier does not match one of the [supported sections](#numpydoc-sections), the section is parsed as an "admonition" (or "callout").

Identifiers are case-insensitive, however singular and plural forms are distinct, except for notes and warnings. In particular, `Examples` is parsed as the [Examples section](#numpydoc-section-examples), while `Example` is parsed as an admonition whose kind is `example`.

The kind is obtained by lower-casing the identifier and replacing spaces with dashes. For example, an admonition whose identifier is `See also` will have a kind equal to `see-also`.

It is up to any downstream documentation renderer to make use of these kinds.

### Parser options {#numpydoc-options}

The parser accepts a few options:

- `ignore_init_summary`: Ignore the first line in `__init__` methods' docstrings. Useful when merging `__init__` docstring into class' docstrings with mkdocstrings-python's [`merge_init_into_class`][merge_init] option. Default: false.
- `trim_doctest_flags`: Remove the [doctest flags] written as comments in `pycon` snippets within a docstring. These flags are used to alter the behavior of [doctest] when testing docstrings, and should not be visible in your docs. Default: true.
- `warn_unknown_params`: Warn about parameters documented in docstrings that do not appear in the signature. Default: true.

### Sections {#numpydoc-sections}

The following sections are supported.

#### Attributes {#numpydoc-section-attributes}

- Multiple items allowed

Attributes sections allow to document attributes of a module, class, or class instance. They should be used in modules and classes docstrings only.

```python
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

```python
"""My module.

Attributes
----------
foo : Integer
    Description for `foo`.
bar : Boolean
    Description for `bar`.
"""
```

TIP: **Types in docstrings are resolved using the docstrings' parent scope.**  
When documenting an attribute with `attr_name : attr_type`, `attr_type` will be resolved using the scope of the docstrings' parent object (class or module). For example, a type of `list[str]` will be parsed just as if it was an actual Python annotation. You can therefore use complex types (available in the current scope) in docstrings, for example `Optional[Union[int, Tuple[float, float]]]`.

#### Functions/Methods {#numpydoc-section-functions}

- Multiple items allowed

Functions or Methods sections allow to document functions of a module, or methods of a class. They should be used in modules and classes docstrings only.

```python
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

```python
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

#### Classes {#numpydoc-section-classes}

- Multiple items allowed

Classes sections allow to document classes of a module or class. They should be used in modules and classes docstrings only.

```python
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

```python
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

#### Modules {#numpydoc-section-modules}

- Multiple items allowed

Modules sections allow to document submodules of a module. They should be used in modules docstrings only.

```tree
my_pkg/
    __init__.py
    foo.py
    bar.py
```

```python title="my_pkg/__init__.py"
"""My package.

Modules
-------
foo
    Description for `foo`.
bar
    Description for `bar`.
"""
```

#### Deprecated {#numpydoc-section-deprecated}

Deprecated sections allow to document a deprecation that happened at a particular version. They can be used in every docstring.

```python
"""My module.

Deprecated
----------
    1.2
        The `foo` attribute is deprecated.
"""

foo: int = 0
```

#### Examples {#numpydoc-section-examples}

Examples sections allow to add examples of Python code without the use of markup code blocks. They are a mix of prose and interactive console snippets. They can be used in every docstring.

```python
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

#### Parameters {#numpydoc-section-parameters}

- Aliases: Args, Arguments, Params
- Multiple items allowed

Parameters sections allow to document parameters of a function. They are typically used in functions docstrings, but can also be used in dataclasses docstrings.

```python
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

```python
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

```python
"""My function.

Parameters
----------
foo : Integer
    Description for `foo`.
bar : String
    Description for `bar`.
"""
```

TIP: **Types in docstrings are resolved using the docstrings' parent scope.**  
When documenting a parameter with `param_name : param_type`, `param_type` will be resolved using the scope of the function (or class). For example, a type of `list[str]` will be parsed just as if it was an actual Python annotation. You can therefore use complex types (available in the current scope) in docstrings, for example `Optional[Union[int, Tuple[float, float]]]`.

#### Other Parameters {#numpydoc-section-other-parameters}

- Aliases: Keyword Args, Keyword Arguments, Other Args, Other Arguments, Other Params
- Multiple items allowed

Other parameters sections allow to document secondary parameters such as variadic keyword arguments, or parameters that should be of lesser interest to the user. They are used the same way Parameters sections are.

```python
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

TIP: **Types in docstrings are resolved using the docstrings' parent scope.**  
See the same tip for parameters.

#### Raises {#numpydoc-section-raises}

- Aliases: Exceptions
- Multiple items allowed

Raises sections allow to document exceptions that are raised by a function. They are usually only used in functions docstrings.

```python
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

TIP: **Exceptions names are resolved using the function's scope.**  
`ValueError` and other built-in exceptions are resolved as such. You can document custom exception, using the names available in the current scope, for example `my_exceptions.MyCustomException` or `MyCustomException` directly, depending on what you imported/defined in the current module.

#### Warns {#numpydoc-section-warns}

- Multiple items allowed

Warns sections allow to document warnings emitted by the following code. They are usually only used in functions docstrings.

```python
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

TIP: **Warnings names are resolved using the function's scope.**  
`UserWarning` and other built-in warnings are resolved as such. You can document custom warnings, using the names available in the current scope, for example `my_warnings.MyCustomWarning` or `MyCustomWarning` directly, depending on what you imported/defined in the current module.

#### Yields {#numpydoc-section-yields}

- Multiple items allowed

Yields sections allow to document values that generator yield. They should be used only in generators docstrings. Documented items can be given a name when it makes sense.

```python
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

```python
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

```python
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

TIP: **Types in docstrings are resolved using the docstrings' parent scope.**  
See previous tips for types in docstrings.

#### Receives {#numpydoc-section-receives}

- Multiple items allowed

Receives sections allow to document values that can be sent to generators using their `send` method. They should be used only in generators docstrings. Documented items can be given a name when it makes sense.

```python
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

```python
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

```python
"""Foo.

Receives
--------
mode : ModeEnum
    Some mode.
flag : int
    Some flag.
"""
```

TIP: **Types in docstrings are resolved using the docstrings' parent scope.**  
See previous tips for types in docstrings.

#### Returns {#numpydoc-section-returns}

- Multiple items allowed

Returns sections allow to document values returned by functions. They should be used only in functions docstrings. Documented items can be given a name when it makes sense.

```python
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

```python
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

```python
"""Foo.

Returns
-------
success : int
    Whether it succeeded.
precision : Decimal
    Final precision.
"""
```

TIP: **Types in docstrings are resolved using the docstrings' function scope.**  
See previous tips for types in docstrings.

## Auto-style

[:octicons-heart-fill-24:{ .pulse } Sponsors only](../insiders/index.md){ .insiders } — [:octicons-tag-24: Insiders 1.3.0](../insiders/changelog.md#1.3.0).

Automatic style detection. This parser will first try to detect the style used in the docstring, and call the corresponding parser on it.

### Parser options {#auto-options}

The parser accepts a few options:

- `method`: The method to use to detect the style and infer the parser. Method 'heuristics' will use regular expressions, while method 'max_sections' will parse the docstring with all parsers specified in `style_order` and return the one who parsed the most sections. Default: `"heuristics"`.
- `style_order`: If multiple parsers parsed the same number of sections, `style_order` is used to decide which one to return. Default: `["sphinx", "google", "numpy"]`.
- `default`: If heuristics fail, the `default` parser is returned. The `default` parser is never used with the 'max_sections' method. Default: `None`.
- Any other option is passed down to the detected parser, if any.

For non-Insiders versions, `default` is returned if specified, else the first parser in `style_order` is returned. If `style_order` is not specified, `None` is returned.

## Parsers features

!!! tip "Want to contribute?"
    Each red cross is a link to an issue on the bugtracker. You will find some guidance on how to add support for the corresponding item.

    The sections are easier to deal in that order:

    - Deprecated (single item, version and text)
    - Raises, Warns (multiple items, no names, single type each)
    - Attributes, Other Parameters, Parameters (multiple items, one name and one optional type each)
    - Returns (multiple items, optional name and/or type each, annotation to split when multiple names)
    - Receives, Yields (multiple items, optional name and/or type each, several types of annotations to split when multiple names)

    "Examples" section are a bit different as they require to parse the examples. But you can probably reuse the code in the Google parser. We can probably even factorize the examples parsing into a single function.

    You can tackle several items at once in a single PR, as long as they relate to a single parser or a single section (a line or a column of the following tables).

### Sections

Section          | Google | Numpy | Sphinx
---------------- | ------ | ----- | ------
Attributes       | ✅     | ✅    | ✅
Functions        | ✅     | ✅    | ❌
Methods          | ✅     | ✅    | ❌
Classes          | ✅     | ✅    | ❌
Modules          | ✅     | ✅    | ❌
Deprecated       | ✅     | ✅[^1]| [❌][issue-section-sphinx-deprecated]
Examples         | ✅     | ✅    | [❌][issue-section-sphinx-examples]
Parameters       | ✅     | ✅    | ✅
Other Parameters | ✅     | ✅    | [❌][issue-section-sphinx-other-parameters]
Raises           | ✅     | ✅    | ✅
Warns            | ✅     | ✅    | [❌][issue-section-sphinx-warns]
Yields           | ✅     | ✅    | [❌][issue-section-sphinx-yields]
Receives         | ✅     | ✅    | [❌][issue-section-sphinx-receives]
Returns          | ✅     | ✅    | ✅

[^1]: Support for a regular section instead of the RST directive specified in the [Numpydoc styleguide](https://numpydoc.readthedocs.io/en/latest/format.html#deprecation-warning).

### Getting annotations/defaults from parent

Section          | Google | Numpy | Sphinx
---------------- | ------ | ----- | ------
Attributes       | ✅     | ✅    | [❌][issue-parent-sphinx-attributes]
Functions        | /      | /     | /
Methods          | /      | /     | /
Classes          | /      | /     | /
Modules          | /      | /     | /
Deprecated       | /      | /     | /
Examples         | /      | /     | /
Parameters       | ✅     | ✅    | ✅
Other Parameters | ✅     | ✅    | [❌][issue-parent-sphinx-other-parameters]
Raises           | /      | /     | /
Warns            | /      | /     | /
Yields           | ✅     | ✅    | [❌][issue-parent-sphinx-yields]
Receives         | ✅     | ✅    | [❌][issue-parent-sphinx-receives]
Returns          | ✅     | ✅    | ✅

### Cross-references for annotations in docstrings

Section          | Google | Numpy | Sphinx
---------------- | ------ | ----- | ------
Attributes       | ✅     | ✅    | [❌][issue-xref-sphinx-attributes]
Functions        | [❌][issue-xref-google-func-cls] | [❌][issue-xref-numpy-func-cls] | /
Methods          | [❌][issue-xref-google-func-cls] | [❌][issue-xref-numpy-func-cls] | /
Classes          | [❌][issue-xref-google-func-cls] | [❌][issue-xref-numpy-func-cls] | /
Modules          | /      | /     | /
Deprecated       | /      | /     | /
Examples         | /      | /     | /
Parameters       | ✅     | ✅    | [❌][issue-xref-sphinx-parameters]
Other Parameters | ✅     | ✅    | [❌][issue-xref-sphinx-other-parameters]
Raises           | ✅     | ✅    | [❌][issue-xref-sphinx-raises]
Warns            | ✅     | ✅    | [❌][issue-xref-sphinx-warns]
Yields           | ✅     | ✅    | [❌][issue-xref-sphinx-yields]
Receives         | ✅     | ✅    | [❌][issue-xref-sphinx-receives]
Returns          | ✅     | ✅    | [❌][issue-xref-sphinx-returns]

[doctest]: https://docs.python.org/3/library/doctest.html#module-doctest
[doctest flags]: https://docs.python.org/3/library/doctest.html#option-flags
[issue-parent-sphinx-attributes]: https://github.com/mkdocstrings/griffe/issues/33
[issue-parent-sphinx-other-parameters]: https://github.com/mkdocstrings/griffe/issues/34
[issue-parent-sphinx-receives]: https://github.com/mkdocstrings/griffe/issues/35
[issue-parent-sphinx-yields]: https://github.com/mkdocstrings/griffe/issues/36
[issue-section-sphinx-deprecated]: https://github.com/mkdocstrings/griffe/issues/6
[issue-section-sphinx-examples]: https://github.com/mkdocstrings/griffe/issues/7
[issue-section-sphinx-other-parameters]: https://github.com/mkdocstrings/griffe/issues/27
[issue-section-sphinx-receives]: https://github.com/mkdocstrings/griffe/issues/8
[issue-section-sphinx-warns]: https://github.com/mkdocstrings/griffe/issues/9
[issue-section-sphinx-yields]: https://github.com/mkdocstrings/griffe/issues/10
[issue-xref-google-func-cls]: https://github.com/mkdocstrings/griffe/issues/199
[issue-xref-numpy-func-cls]: https://github.com/mkdocstrings/griffe/issues/200
[issue-xref-sphinx-attributes]: https://github.com/mkdocstrings/griffe/issues/19
[issue-xref-sphinx-other-parameters]: https://github.com/mkdocstrings/griffe/issues/20
[issue-xref-sphinx-parameters]: https://github.com/mkdocstrings/griffe/issues/21
[issue-xref-sphinx-raises]: https://github.com/mkdocstrings/griffe/issues/22
[issue-xref-sphinx-receives]: https://github.com/mkdocstrings/griffe/issues/23
[issue-xref-sphinx-returns]: https://github.com/mkdocstrings/griffe/issues/24
[issue-xref-sphinx-warns]: https://github.com/mkdocstrings/griffe/issues/25
[issue-xref-sphinx-yields]: https://github.com/mkdocstrings/griffe/issues/26
[merge_init]: https://mkdocstrings.github.io/python/usage/configuration/docstrings/#merge_init_into_class
[napoleon]: https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
[numpydoc]: https://numpydoc.readthedocs.io/en/latest/format.html
[sphinx]: https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html
