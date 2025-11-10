# Docstring models

## **Main API**

## Docstring

```
Docstring(
    value: str,
    *,
    lineno: int | None = None,
    endlineno: int | None = None,
    parent: Object | None = None,
    parser: DocstringStyle | Parser | None = None,
    parser_options: DocstringOptions | None = None,
)
```

This class represents docstrings.

Parameters:

- ### **`value`**

  (`str`) – The docstring value.

- ### **`lineno`**

  (`int | None`, default: `None` ) – The starting line number.

- ### **`endlineno`**

  (`int | None`, default: `None` ) – The ending line number.

- ### **`parent`**

  (`Object | None`, default: `None` ) – The parent object on which this docstring is attached.

- ### **`parser`**

  (`DocstringStyle | Parser | None`, default: `None` ) – The docstring parser to use. By default, no parsing is done.

- ### **`parser_options`**

  (`DocstringOptions | None`, default: `None` ) – Additional docstring parsing options.

Methods:

- **`as_dict`** – Return this docstring's data as a dictionary.
- **`parse`** – Parse the docstring into structured data.

Attributes:

- **`endlineno`** (`int | None`) – The ending line number of the docstring.
- **`lineno`** (`int | None`) – The starting line number of the docstring.
- **`lines`** (`list[str]`) – The lines of the docstring.
- **`parent`** (`Object | None`) – The object this docstring is attached to.
- **`parsed`** (`list[DocstringSection]`) – The docstring sections, parsed into structured data.
- **`parser`** (`DocstringStyle | Parser | None`) – The selected docstring parser.
- **`parser_options`** (`DocstringOptions`) – The configured parsing options.
- **`source`** (`str`) – The original, uncleaned value of the docstring as written in the source.
- **`value`** (`str`) – The original value of the docstring, cleaned by inspect.cleandoc.

Source code in `src/griffe/_internal/models.py`

```
def __init__(
    self,
    value: str,
    *,
    lineno: int | None = None,
    endlineno: int | None = None,
    parent: Object | None = None,
    parser: DocstringStyle | Parser | None = None,
    parser_options: DocstringOptions | None = None,
) -> None:
    """Initialize the docstring.

    Parameters:
        value: The docstring value.
        lineno: The starting line number.
        endlineno: The ending line number.
        parent: The parent object on which this docstring is attached.
        parser: The docstring parser to use. By default, no parsing is done.
        parser_options: Additional docstring parsing options.
    """
    self.value: str = inspect.cleandoc(value.rstrip())
    """The original value of the docstring, cleaned by `inspect.cleandoc`.

    See also: [`source`][griffe.Docstring.source].
    """

    self.lineno: int | None = lineno
    """The starting line number of the docstring.

    See also: [`endlineno`][griffe.Docstring.endlineno]."""

    self.endlineno: int | None = endlineno
    """The ending line number of the docstring.

    See also: [`lineno`][griffe.Docstring.lineno]."""

    self.parent: Object | None = parent
    """The object this docstring is attached to."""

    self.parser: DocstringStyle | Parser | None = parser
    """The selected docstring parser.

    See also: [`parser_options`][griffe.Docstring.parser_options],
    [`parse`][griffe.Docstring.parse].
    """

    self.parser_options: DocstringOptions = parser_options or {}
    """The configured parsing options.

    See also: [`parser`][griffe.Docstring.parser],
    [`parse`][griffe.Docstring.parse].
    """
```

### endlineno

```
endlineno: int | None = endlineno
```

The ending line number of the docstring.

See also: lineno.

### lineno

```
lineno: int | None = lineno
```

The starting line number of the docstring.

See also: endlineno.

### lines

```
lines: list[str]
```

The lines of the docstring.

See also: source.

### parent

```
parent: Object | None = parent
```

The object this docstring is attached to.

### parsed

```
parsed: list[DocstringSection]
```

The docstring sections, parsed into structured data.

### parser

```
parser: DocstringStyle | Parser | None = parser
```

The selected docstring parser.

See also: parser_options, parse.

### parser_options

```
parser_options: DocstringOptions = parser_options or {}
```

The configured parsing options.

See also: parser, parse.

### source

```
source: str
```

The original, uncleaned value of the docstring as written in the source.

It is a simple concatenation of the source lines. These source lines will include quotes (single/double/triple) and might include leading whitespace and indentation, as well as trailing comments.

Raises:

- `ValueError` – If the original docstring cannot be retrieved (no parent, no line numbers, or attached to namespace package).

See also: value.

### value

```
value: str = cleandoc(rstrip())
```

The original value of the docstring, cleaned by `inspect.cleandoc`.

See also: source.

### as_dict

```
as_dict(
    *, full: bool = False, **kwargs: Any
) -> dict[str, Any]
```

Return this docstring's data as a dictionary.

Parameters:

- #### **`full`**

  (`bool`, default: `False` ) – Whether to return full info, or just base info.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/models.py`

```
def as_dict(
    self,
    *,
    full: bool = False,
    **kwargs: Any,  # noqa: ARG002
) -> dict[str, Any]:
    """Return this docstring's data as a dictionary.

    Parameters:
        full: Whether to return full info, or just base info.
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    base: dict[str, Any] = {
        "value": self.value,
        "lineno": self.lineno,
        "endlineno": self.endlineno,
    }
    if full:
        base["parsed"] = self.parsed
    return base
```

### parse

```
parse(
    parser: DocstringStyle | Parser | None = None,
    **options: Any,
) -> list[DocstringSection]
```

Parse the docstring into structured data.

See also: parser, parser_options.

Parameters:

- #### **`parser`**

  (`DocstringStyle | Parser | None`, default: `None` ) – The docstring parser to use. In order: use the given parser, or the self parser, or no parser (return a single text section).

- #### **`**options`**

  (`Any`, default: `{}` ) – Additional docstring parsing options.

Returns:

- `list[DocstringSection]` – The parsed docstring as a list of sections.

Source code in `src/griffe/_internal/models.py`

```
def parse(
    self,
    parser: DocstringStyle | Parser | None = None,
    **options: Any,
) -> list[DocstringSection]:
    """Parse the docstring into structured data.

    See also: [`parser`][griffe.Docstring.parser],
    [`parser_options`][griffe.Docstring.parser_options].

    Parameters:
        parser: The docstring parser to use.
            In order: use the given parser, or the self parser, or no parser (return a single text section).
        **options: Additional docstring parsing options.

    Returns:
        The parsed docstring as a list of sections.
    """
    return parse(self, parser or self.parser, **(options or self.parser_options))
```

## **Advanced API: Sections**

## DocstringSectionKind

Bases: `str`, `Enum`

```
              flowchart TD
              griffe.DocstringSectionKind[DocstringSectionKind]

              

              click griffe.DocstringSectionKind href "" "griffe.DocstringSectionKind"
```

Enumeration of the possible docstring section kinds.

Attributes:

- **`admonition`** – Admonition block.
- **`attributes`** – Attributes section.
- **`classes`** – Classes section.
- **`deprecated`** – Deprecation section.
- **`examples`** – Examples section.
- **`functions`** – Functions section.
- **`modules`** – Modules section.
- **`other_parameters`** – Other parameters (keyword arguments) section.
- **`parameters`** – Parameters section.
- **`raises`** – Raises (exceptions) section.
- **`receives`** – Received value(s) (generators) section.
- **`returns`** – Returned value(s) section.
- **`text`** – Text section.
- **`type_aliases`** – Type aliases section.
- **`type_parameters`** – Type parameters section.
- **`warns`** – Warnings section.
- **`yields`** – Yielded value(s) (generators) section.

### admonition

```
admonition = 'admonition'
```

Admonition block.

### attributes

```
attributes = 'attributes'
```

Attributes section.

### classes

```
classes = 'classes'
```

Classes section.

### deprecated

```
deprecated = 'deprecated'
```

Deprecation section.

### examples

```
examples = 'examples'
```

Examples section.

### functions

```
functions = 'functions'
```

Functions section.

### modules

```
modules = 'modules'
```

Modules section.

### other_parameters

```
other_parameters = 'other parameters'
```

Other parameters (keyword arguments) section.

### parameters

```
parameters = 'parameters'
```

Parameters section.

### raises

```
raises = 'raises'
```

Raises (exceptions) section.

### receives

```
receives = 'receives'
```

Received value(s) (generators) section.

### returns

```
returns = 'returns'
```

Returned value(s) section.

### text

```
text = 'text'
```

Text section.

### type_aliases

```
type_aliases = 'type aliases'
```

Type aliases section.

### type_parameters

```
type_parameters = 'type parameters'
```

Type parameters section.

### warns

```
warns = 'warns'
```

Warnings section.

### yields

```
yields = 'yields'
```

Yielded value(s) (generators) section.

## DocstringSectionText

```
DocstringSectionText(value: str, title: str | None = None)
```

Bases: `DocstringSection`

```
              flowchart TD
              griffe.DocstringSectionText[DocstringSectionText]
              griffe._internal.docstrings.models.DocstringSection[DocstringSection]

                              griffe._internal.docstrings.models.DocstringSection --> griffe.DocstringSectionText
                


              click griffe.DocstringSectionText href "" "griffe.DocstringSectionText"
              click griffe._internal.docstrings.models.DocstringSection href "" "griffe._internal.docstrings.models.DocstringSection"
```

This class represents a text section.

Parameters:

- ### **`value`**

  (`str`) – The section text.

- ### **`title`**

  (`str | None`, default: `None` ) – An optional title.

Methods:

- **`__bool__`** – Whether this section has a true-ish value.
- **`as_dict`** – Return this section's data as a dictionary.

Attributes:

- **`kind`** (`DocstringSectionKind`) – The section kind.
- **`title`** (`str | None`) – The section title.
- **`value`** (`str`) – The section value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(self, value: str, title: str | None = None) -> None:
    """Initialize the section.

    Parameters:
        value: The section text.
        title: An optional title.
    """
    super().__init__(title)
    self.value: str = value
```

### kind

```
kind: DocstringSectionKind = text
```

The section kind.

### title

```
title: str | None = title
```

The section title.

### value

```
value: str = value
```

The section value.

### __bool__

```
__bool__() -> bool
```

Whether this section has a true-ish value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __bool__(self) -> bool:
    """Whether this section has a true-ish value."""
    return bool(self.value)
```

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this section's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this section's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    if hasattr(self.value, "as_dict"):  # noqa: SIM108
        serialized_value = self.value.as_dict(**kwargs)
    else:
        serialized_value = self.value
    base = {"kind": self.kind.value, "value": serialized_value}
    if self.title:
        base["title"] = self.title
    return base
```

## DocstringSectionParameters

```
DocstringSectionParameters(
    value: list[DocstringParameter],
    title: str | None = None,
)
```

Bases: `DocstringSection`

```
              flowchart TD
              griffe.DocstringSectionParameters[DocstringSectionParameters]
              griffe._internal.docstrings.models.DocstringSection[DocstringSection]

                              griffe._internal.docstrings.models.DocstringSection --> griffe.DocstringSectionParameters
                


              click griffe.DocstringSectionParameters href "" "griffe.DocstringSectionParameters"
              click griffe._internal.docstrings.models.DocstringSection href "" "griffe._internal.docstrings.models.DocstringSection"
```

This class represents a parameters section.

Parameters:

- ### **`value`**

  (`list[DocstringParameter]`) – The section parameters.

- ### **`title`**

  (`str | None`, default: `None` ) – An optional title.

Methods:

- **`__bool__`** – Whether this section has a true-ish value.
- **`as_dict`** – Return this section's data as a dictionary.

Attributes:

- **`kind`** (`DocstringSectionKind`) – The section kind.
- **`title`** (`str | None`) – The section title.
- **`value`** (`list[DocstringParameter]`) – The section value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(self, value: list[DocstringParameter], title: str | None = None) -> None:
    """Initialize the section.

    Parameters:
        value: The section parameters.
        title: An optional title.
    """
    super().__init__(title)
    self.value: list[DocstringParameter] = value
```

### kind

```
kind: DocstringSectionKind = parameters
```

The section kind.

### title

```
title: str | None = title
```

The section title.

### value

```
value: list[DocstringParameter] = value
```

The section value.

### __bool__

```
__bool__() -> bool
```

Whether this section has a true-ish value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __bool__(self) -> bool:
    """Whether this section has a true-ish value."""
    return bool(self.value)
```

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this section's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this section's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    if hasattr(self.value, "as_dict"):  # noqa: SIM108
        serialized_value = self.value.as_dict(**kwargs)
    else:
        serialized_value = self.value
    base = {"kind": self.kind.value, "value": serialized_value}
    if self.title:
        base["title"] = self.title
    return base
```

## DocstringSectionOtherParameters

```
DocstringSectionOtherParameters(
    value: list[DocstringParameter],
    title: str | None = None,
)
```

Bases: `DocstringSectionParameters`

```
              flowchart TD
              griffe.DocstringSectionOtherParameters[DocstringSectionOtherParameters]
              griffe._internal.docstrings.models.DocstringSectionParameters[DocstringSectionParameters]
              griffe._internal.docstrings.models.DocstringSection[DocstringSection]

                              griffe._internal.docstrings.models.DocstringSectionParameters --> griffe.DocstringSectionOtherParameters
                                griffe._internal.docstrings.models.DocstringSection --> griffe._internal.docstrings.models.DocstringSectionParameters
                



              click griffe.DocstringSectionOtherParameters href "" "griffe.DocstringSectionOtherParameters"
              click griffe._internal.docstrings.models.DocstringSectionParameters href "" "griffe._internal.docstrings.models.DocstringSectionParameters"
              click griffe._internal.docstrings.models.DocstringSection href "" "griffe._internal.docstrings.models.DocstringSection"
```

This class represents an other parameters section.

Parameters:

- ### **`value`**

  (`list[DocstringParameter]`) – The section parameters.

- ### **`title`**

  (`str | None`, default: `None` ) – An optional title.

Methods:

- **`__bool__`** – Whether this section has a true-ish value.
- **`as_dict`** – Return this section's data as a dictionary.

Attributes:

- **`kind`** (`DocstringSectionKind`) – The section kind.
- **`title`** (`str | None`) – The section title.
- **`value`** (`list[DocstringParameter]`) – The section value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(self, value: list[DocstringParameter], title: str | None = None) -> None:
    """Initialize the section.

    Parameters:
        value: The section parameters.
        title: An optional title.
    """
    super().__init__(title)
    self.value: list[DocstringParameter] = value
```

### kind

```
kind: DocstringSectionKind = other_parameters
```

The section kind.

### title

```
title: str | None = title
```

The section title.

### value

```
value: list[DocstringParameter] = value
```

The section value.

### __bool__

```
__bool__() -> bool
```

Whether this section has a true-ish value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __bool__(self) -> bool:
    """Whether this section has a true-ish value."""
    return bool(self.value)
```

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this section's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this section's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    if hasattr(self.value, "as_dict"):  # noqa: SIM108
        serialized_value = self.value.as_dict(**kwargs)
    else:
        serialized_value = self.value
    base = {"kind": self.kind.value, "value": serialized_value}
    if self.title:
        base["title"] = self.title
    return base
```

## DocstringSectionTypeParameters

```
DocstringSectionTypeParameters(
    value: list[DocstringTypeParameter],
    title: str | None = None,
)
```

Bases: `DocstringSection`

```
              flowchart TD
              griffe.DocstringSectionTypeParameters[DocstringSectionTypeParameters]
              griffe._internal.docstrings.models.DocstringSection[DocstringSection]

                              griffe._internal.docstrings.models.DocstringSection --> griffe.DocstringSectionTypeParameters
                


              click griffe.DocstringSectionTypeParameters href "" "griffe.DocstringSectionTypeParameters"
              click griffe._internal.docstrings.models.DocstringSection href "" "griffe._internal.docstrings.models.DocstringSection"
```

This class represents a type parameters section.

Parameters:

- ### **`value`**

  (`list[DocstringTypeParameter]`) – The section type parameters.

- ### **`title`**

  (`str | None`, default: `None` ) – An optional title.

Methods:

- **`__bool__`** – Whether this section has a true-ish value.
- **`as_dict`** – Return this section's data as a dictionary.

Attributes:

- **`kind`** (`DocstringSectionKind`) – The section kind.
- **`title`** (`str | None`) – The section title.
- **`value`** (`list[DocstringTypeParameter]`) – The section value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(self, value: list[DocstringTypeParameter], title: str | None = None) -> None:
    """Initialize the section.

    Parameters:
        value: The section type parameters.
        title: An optional title.
    """
    super().__init__(title)
    self.value: list[DocstringTypeParameter] = value
```

### kind

```
kind: DocstringSectionKind = type_parameters
```

The section kind.

### title

```
title: str | None = title
```

The section title.

### value

```
value: list[DocstringTypeParameter] = value
```

The section value.

### __bool__

```
__bool__() -> bool
```

Whether this section has a true-ish value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __bool__(self) -> bool:
    """Whether this section has a true-ish value."""
    return bool(self.value)
```

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this section's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this section's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    if hasattr(self.value, "as_dict"):  # noqa: SIM108
        serialized_value = self.value.as_dict(**kwargs)
    else:
        serialized_value = self.value
    base = {"kind": self.kind.value, "value": serialized_value}
    if self.title:
        base["title"] = self.title
    return base
```

## DocstringSectionRaises

```
DocstringSectionRaises(
    value: list[DocstringRaise], title: str | None = None
)
```

Bases: `DocstringSection`

```
              flowchart TD
              griffe.DocstringSectionRaises[DocstringSectionRaises]
              griffe._internal.docstrings.models.DocstringSection[DocstringSection]

                              griffe._internal.docstrings.models.DocstringSection --> griffe.DocstringSectionRaises
                


              click griffe.DocstringSectionRaises href "" "griffe.DocstringSectionRaises"
              click griffe._internal.docstrings.models.DocstringSection href "" "griffe._internal.docstrings.models.DocstringSection"
```

This class represents a raises section.

Parameters:

- ### **`value`**

  (`list[DocstringRaise]`) – The section exceptions.

- ### **`title`**

  (`str | None`, default: `None` ) – An optional title.

Methods:

- **`__bool__`** – Whether this section has a true-ish value.
- **`as_dict`** – Return this section's data as a dictionary.

Attributes:

- **`kind`** (`DocstringSectionKind`) – The section kind.
- **`title`** (`str | None`) – The section title.
- **`value`** (`list[DocstringRaise]`) – The section value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(self, value: list[DocstringRaise], title: str | None = None) -> None:
    """Initialize the section.

    Parameters:
        value: The section exceptions.
        title: An optional title.
    """
    super().__init__(title)
    self.value: list[DocstringRaise] = value
```

### kind

```
kind: DocstringSectionKind = raises
```

The section kind.

### title

```
title: str | None = title
```

The section title.

### value

```
value: list[DocstringRaise] = value
```

The section value.

### __bool__

```
__bool__() -> bool
```

Whether this section has a true-ish value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __bool__(self) -> bool:
    """Whether this section has a true-ish value."""
    return bool(self.value)
```

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this section's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this section's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    if hasattr(self.value, "as_dict"):  # noqa: SIM108
        serialized_value = self.value.as_dict(**kwargs)
    else:
        serialized_value = self.value
    base = {"kind": self.kind.value, "value": serialized_value}
    if self.title:
        base["title"] = self.title
    return base
```

## DocstringSectionWarns

```
DocstringSectionWarns(
    value: list[DocstringWarn], title: str | None = None
)
```

Bases: `DocstringSection`

```
              flowchart TD
              griffe.DocstringSectionWarns[DocstringSectionWarns]
              griffe._internal.docstrings.models.DocstringSection[DocstringSection]

                              griffe._internal.docstrings.models.DocstringSection --> griffe.DocstringSectionWarns
                


              click griffe.DocstringSectionWarns href "" "griffe.DocstringSectionWarns"
              click griffe._internal.docstrings.models.DocstringSection href "" "griffe._internal.docstrings.models.DocstringSection"
```

This class represents a warns section.

Parameters:

- ### **`value`**

  (`list[DocstringWarn]`) – The section warnings.

- ### **`title`**

  (`str | None`, default: `None` ) – An optional title.

Methods:

- **`__bool__`** – Whether this section has a true-ish value.
- **`as_dict`** – Return this section's data as a dictionary.

Attributes:

- **`kind`** (`DocstringSectionKind`) – The section kind.
- **`title`** (`str | None`) – The section title.
- **`value`** (`list[DocstringWarn]`) – The section value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(self, value: list[DocstringWarn], title: str | None = None) -> None:
    """Initialize the section.

    Parameters:
        value: The section warnings.
        title: An optional title.
    """
    super().__init__(title)
    self.value: list[DocstringWarn] = value
```

### kind

```
kind: DocstringSectionKind = warns
```

The section kind.

### title

```
title: str | None = title
```

The section title.

### value

```
value: list[DocstringWarn] = value
```

The section value.

### __bool__

```
__bool__() -> bool
```

Whether this section has a true-ish value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __bool__(self) -> bool:
    """Whether this section has a true-ish value."""
    return bool(self.value)
```

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this section's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this section's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    if hasattr(self.value, "as_dict"):  # noqa: SIM108
        serialized_value = self.value.as_dict(**kwargs)
    else:
        serialized_value = self.value
    base = {"kind": self.kind.value, "value": serialized_value}
    if self.title:
        base["title"] = self.title
    return base
```

## DocstringSectionReturns

```
DocstringSectionReturns(
    value: list[DocstringReturn], title: str | None = None
)
```

Bases: `DocstringSection`

```
              flowchart TD
              griffe.DocstringSectionReturns[DocstringSectionReturns]
              griffe._internal.docstrings.models.DocstringSection[DocstringSection]

                              griffe._internal.docstrings.models.DocstringSection --> griffe.DocstringSectionReturns
                


              click griffe.DocstringSectionReturns href "" "griffe.DocstringSectionReturns"
              click griffe._internal.docstrings.models.DocstringSection href "" "griffe._internal.docstrings.models.DocstringSection"
```

This class represents a returns section.

Parameters:

- ### **`value`**

  (`list[DocstringReturn]`) – The section returned items.

- ### **`title`**

  (`str | None`, default: `None` ) – An optional title.

Methods:

- **`__bool__`** – Whether this section has a true-ish value.
- **`as_dict`** – Return this section's data as a dictionary.

Attributes:

- **`kind`** (`DocstringSectionKind`) – The section kind.
- **`title`** (`str | None`) – The section title.
- **`value`** (`list[DocstringReturn]`) – The section value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(self, value: list[DocstringReturn], title: str | None = None) -> None:
    """Initialize the section.

    Parameters:
        value: The section returned items.
        title: An optional title.
    """
    super().__init__(title)
    self.value: list[DocstringReturn] = value
```

### kind

```
kind: DocstringSectionKind = returns
```

The section kind.

### title

```
title: str | None = title
```

The section title.

### value

```
value: list[DocstringReturn] = value
```

The section value.

### __bool__

```
__bool__() -> bool
```

Whether this section has a true-ish value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __bool__(self) -> bool:
    """Whether this section has a true-ish value."""
    return bool(self.value)
```

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this section's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this section's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    if hasattr(self.value, "as_dict"):  # noqa: SIM108
        serialized_value = self.value.as_dict(**kwargs)
    else:
        serialized_value = self.value
    base = {"kind": self.kind.value, "value": serialized_value}
    if self.title:
        base["title"] = self.title
    return base
```

## DocstringSectionYields

```
DocstringSectionYields(
    value: list[DocstringYield], title: str | None = None
)
```

Bases: `DocstringSection`

```
              flowchart TD
              griffe.DocstringSectionYields[DocstringSectionYields]
              griffe._internal.docstrings.models.DocstringSection[DocstringSection]

                              griffe._internal.docstrings.models.DocstringSection --> griffe.DocstringSectionYields
                


              click griffe.DocstringSectionYields href "" "griffe.DocstringSectionYields"
              click griffe._internal.docstrings.models.DocstringSection href "" "griffe._internal.docstrings.models.DocstringSection"
```

This class represents a yields section.

Parameters:

- ### **`value`**

  (`list[DocstringYield]`) – The section yielded items.

- ### **`title`**

  (`str | None`, default: `None` ) – An optional title.

Methods:

- **`__bool__`** – Whether this section has a true-ish value.
- **`as_dict`** – Return this section's data as a dictionary.

Attributes:

- **`kind`** (`DocstringSectionKind`) – The section kind.
- **`title`** (`str | None`) – The section title.
- **`value`** (`list[DocstringYield]`) – The section value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(self, value: list[DocstringYield], title: str | None = None) -> None:
    """Initialize the section.

    Parameters:
        value: The section yielded items.
        title: An optional title.
    """
    super().__init__(title)
    self.value: list[DocstringYield] = value
```

### kind

```
kind: DocstringSectionKind = yields
```

The section kind.

### title

```
title: str | None = title
```

The section title.

### value

```
value: list[DocstringYield] = value
```

The section value.

### __bool__

```
__bool__() -> bool
```

Whether this section has a true-ish value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __bool__(self) -> bool:
    """Whether this section has a true-ish value."""
    return bool(self.value)
```

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this section's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this section's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    if hasattr(self.value, "as_dict"):  # noqa: SIM108
        serialized_value = self.value.as_dict(**kwargs)
    else:
        serialized_value = self.value
    base = {"kind": self.kind.value, "value": serialized_value}
    if self.title:
        base["title"] = self.title
    return base
```

## DocstringSectionReceives

```
DocstringSectionReceives(
    value: list[DocstringReceive], title: str | None = None
)
```

Bases: `DocstringSection`

```
              flowchart TD
              griffe.DocstringSectionReceives[DocstringSectionReceives]
              griffe._internal.docstrings.models.DocstringSection[DocstringSection]

                              griffe._internal.docstrings.models.DocstringSection --> griffe.DocstringSectionReceives
                


              click griffe.DocstringSectionReceives href "" "griffe.DocstringSectionReceives"
              click griffe._internal.docstrings.models.DocstringSection href "" "griffe._internal.docstrings.models.DocstringSection"
```

This class represents a receives section.

Parameters:

- ### **`value`**

  (`list[DocstringReceive]`) – The section received items.

- ### **`title`**

  (`str | None`, default: `None` ) – An optional title.

Methods:

- **`__bool__`** – Whether this section has a true-ish value.
- **`as_dict`** – Return this section's data as a dictionary.

Attributes:

- **`kind`** (`DocstringSectionKind`) – The section kind.
- **`title`** (`str | None`) – The section title.
- **`value`** (`list[DocstringReceive]`) – The section value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(self, value: list[DocstringReceive], title: str | None = None) -> None:
    """Initialize the section.

    Parameters:
        value: The section received items.
        title: An optional title.
    """
    super().__init__(title)
    self.value: list[DocstringReceive] = value
```

### kind

```
kind: DocstringSectionKind = receives
```

The section kind.

### title

```
title: str | None = title
```

The section title.

### value

```
value: list[DocstringReceive] = value
```

The section value.

### __bool__

```
__bool__() -> bool
```

Whether this section has a true-ish value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __bool__(self) -> bool:
    """Whether this section has a true-ish value."""
    return bool(self.value)
```

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this section's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this section's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    if hasattr(self.value, "as_dict"):  # noqa: SIM108
        serialized_value = self.value.as_dict(**kwargs)
    else:
        serialized_value = self.value
    base = {"kind": self.kind.value, "value": serialized_value}
    if self.title:
        base["title"] = self.title
    return base
```

## DocstringSectionExamples

```
DocstringSectionExamples(
    value: list[tuple[Literal[text, examples], str]],
    title: str | None = None,
)
```

Bases: `DocstringSection`

```
              flowchart TD
              griffe.DocstringSectionExamples[DocstringSectionExamples]
              griffe._internal.docstrings.models.DocstringSection[DocstringSection]

                              griffe._internal.docstrings.models.DocstringSection --> griffe.DocstringSectionExamples
                


              click griffe.DocstringSectionExamples href "" "griffe.DocstringSectionExamples"
              click griffe._internal.docstrings.models.DocstringSection href "" "griffe._internal.docstrings.models.DocstringSection"
```

This class represents an examples section.

Parameters:

- ### **`value`**

  (`list[tuple[Literal[text, examples], str]]`) – The section examples.

- ### **`title`**

  (`str | None`, default: `None` ) – An optional title.

Methods:

- **`__bool__`** – Whether this section has a true-ish value.
- **`as_dict`** – Return this section's data as a dictionary.

Attributes:

- **`kind`** (`DocstringSectionKind`) – The section kind.
- **`title`** (`str | None`) – The section title.
- **`value`** (`list[tuple[Literal[text, examples], str]]`) – The section value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(
    self,
    value: list[tuple[Literal[DocstringSectionKind.text, DocstringSectionKind.examples], str]],
    title: str | None = None,
) -> None:
    """Initialize the section.

    Parameters:
        value: The section examples.
        title: An optional title.
    """
    super().__init__(title)
    self.value: list[tuple[Literal[DocstringSectionKind.text, DocstringSectionKind.examples], str]] = value
```

### kind

```
kind: DocstringSectionKind = examples
```

The section kind.

### title

```
title: str | None = title
```

The section title.

### value

```
value: list[tuple[Literal[text, examples], str]] = value
```

The section value.

### __bool__

```
__bool__() -> bool
```

Whether this section has a true-ish value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __bool__(self) -> bool:
    """Whether this section has a true-ish value."""
    return bool(self.value)
```

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this section's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this section's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    if hasattr(self.value, "as_dict"):  # noqa: SIM108
        serialized_value = self.value.as_dict(**kwargs)
    else:
        serialized_value = self.value
    base = {"kind": self.kind.value, "value": serialized_value}
    if self.title:
        base["title"] = self.title
    return base
```

## DocstringSectionAttributes

```
DocstringSectionAttributes(
    value: list[DocstringAttribute],
    title: str | None = None,
)
```

Bases: `DocstringSection`

```
              flowchart TD
              griffe.DocstringSectionAttributes[DocstringSectionAttributes]
              griffe._internal.docstrings.models.DocstringSection[DocstringSection]

                              griffe._internal.docstrings.models.DocstringSection --> griffe.DocstringSectionAttributes
                


              click griffe.DocstringSectionAttributes href "" "griffe.DocstringSectionAttributes"
              click griffe._internal.docstrings.models.DocstringSection href "" "griffe._internal.docstrings.models.DocstringSection"
```

This class represents an attributes section.

Parameters:

- ### **`value`**

  (`list[DocstringAttribute]`) – The section attributes.

- ### **`title`**

  (`str | None`, default: `None` ) – An optional title.

Methods:

- **`__bool__`** – Whether this section has a true-ish value.
- **`as_dict`** – Return this section's data as a dictionary.

Attributes:

- **`kind`** (`DocstringSectionKind`) – The section kind.
- **`title`** (`str | None`) – The section title.
- **`value`** (`list[DocstringAttribute]`) – The section value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(self, value: list[DocstringAttribute], title: str | None = None) -> None:
    """Initialize the section.

    Parameters:
        value: The section attributes.
        title: An optional title.
    """
    super().__init__(title)
    self.value: list[DocstringAttribute] = value
```

### kind

```
kind: DocstringSectionKind = attributes
```

The section kind.

### title

```
title: str | None = title
```

The section title.

### value

```
value: list[DocstringAttribute] = value
```

The section value.

### __bool__

```
__bool__() -> bool
```

Whether this section has a true-ish value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __bool__(self) -> bool:
    """Whether this section has a true-ish value."""
    return bool(self.value)
```

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this section's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this section's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    if hasattr(self.value, "as_dict"):  # noqa: SIM108
        serialized_value = self.value.as_dict(**kwargs)
    else:
        serialized_value = self.value
    base = {"kind": self.kind.value, "value": serialized_value}
    if self.title:
        base["title"] = self.title
    return base
```

## DocstringSectionFunctions

```
DocstringSectionFunctions(
    value: list[DocstringFunction], title: str | None = None
)
```

Bases: `DocstringSection`

```
              flowchart TD
              griffe.DocstringSectionFunctions[DocstringSectionFunctions]
              griffe._internal.docstrings.models.DocstringSection[DocstringSection]

                              griffe._internal.docstrings.models.DocstringSection --> griffe.DocstringSectionFunctions
                


              click griffe.DocstringSectionFunctions href "" "griffe.DocstringSectionFunctions"
              click griffe._internal.docstrings.models.DocstringSection href "" "griffe._internal.docstrings.models.DocstringSection"
```

This class represents a functions/methods section.

Parameters:

- ### **`value`**

  (`list[DocstringFunction]`) – The section functions.

- ### **`title`**

  (`str | None`, default: `None` ) – An optional title.

Methods:

- **`__bool__`** – Whether this section has a true-ish value.
- **`as_dict`** – Return this section's data as a dictionary.

Attributes:

- **`kind`** (`DocstringSectionKind`) – The section kind.
- **`title`** (`str | None`) – The section title.
- **`value`** (`list[DocstringFunction]`) – The section value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(self, value: list[DocstringFunction], title: str | None = None) -> None:
    """Initialize the section.

    Parameters:
        value: The section functions.
        title: An optional title.
    """
    super().__init__(title)
    self.value: list[DocstringFunction] = value
```

### kind

```
kind: DocstringSectionKind = functions
```

The section kind.

### title

```
title: str | None = title
```

The section title.

### value

```
value: list[DocstringFunction] = value
```

The section value.

### __bool__

```
__bool__() -> bool
```

Whether this section has a true-ish value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __bool__(self) -> bool:
    """Whether this section has a true-ish value."""
    return bool(self.value)
```

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this section's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this section's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    if hasattr(self.value, "as_dict"):  # noqa: SIM108
        serialized_value = self.value.as_dict(**kwargs)
    else:
        serialized_value = self.value
    base = {"kind": self.kind.value, "value": serialized_value}
    if self.title:
        base["title"] = self.title
    return base
```

## DocstringSectionClasses

```
DocstringSectionClasses(
    value: list[DocstringClass], title: str | None = None
)
```

Bases: `DocstringSection`

```
              flowchart TD
              griffe.DocstringSectionClasses[DocstringSectionClasses]
              griffe._internal.docstrings.models.DocstringSection[DocstringSection]

                              griffe._internal.docstrings.models.DocstringSection --> griffe.DocstringSectionClasses
                


              click griffe.DocstringSectionClasses href "" "griffe.DocstringSectionClasses"
              click griffe._internal.docstrings.models.DocstringSection href "" "griffe._internal.docstrings.models.DocstringSection"
```

This class represents a classes section.

Parameters:

- ### **`value`**

  (`list[DocstringClass]`) – The section classes.

- ### **`title`**

  (`str | None`, default: `None` ) – An optional title.

Methods:

- **`__bool__`** – Whether this section has a true-ish value.
- **`as_dict`** – Return this section's data as a dictionary.

Attributes:

- **`kind`** (`DocstringSectionKind`) – The section kind.
- **`title`** (`str | None`) – The section title.
- **`value`** (`list[DocstringClass]`) – The section value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(self, value: list[DocstringClass], title: str | None = None) -> None:
    """Initialize the section.

    Parameters:
        value: The section classes.
        title: An optional title.
    """
    super().__init__(title)
    self.value: list[DocstringClass] = value
```

### kind

```
kind: DocstringSectionKind = classes
```

The section kind.

### title

```
title: str | None = title
```

The section title.

### value

```
value: list[DocstringClass] = value
```

The section value.

### __bool__

```
__bool__() -> bool
```

Whether this section has a true-ish value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __bool__(self) -> bool:
    """Whether this section has a true-ish value."""
    return bool(self.value)
```

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this section's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this section's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    if hasattr(self.value, "as_dict"):  # noqa: SIM108
        serialized_value = self.value.as_dict(**kwargs)
    else:
        serialized_value = self.value
    base = {"kind": self.kind.value, "value": serialized_value}
    if self.title:
        base["title"] = self.title
    return base
```

## DocstringSectionTypeAliases

```
DocstringSectionTypeAliases(
    value: list[DocstringTypeAlias],
    title: str | None = None,
)
```

Bases: `DocstringSection`

```
              flowchart TD
              griffe.DocstringSectionTypeAliases[DocstringSectionTypeAliases]
              griffe._internal.docstrings.models.DocstringSection[DocstringSection]

                              griffe._internal.docstrings.models.DocstringSection --> griffe.DocstringSectionTypeAliases
                


              click griffe.DocstringSectionTypeAliases href "" "griffe.DocstringSectionTypeAliases"
              click griffe._internal.docstrings.models.DocstringSection href "" "griffe._internal.docstrings.models.DocstringSection"
```

This class represents a type aliases section.

Parameters:

- ### **`value`**

  (`list[DocstringTypeAlias]`) – The section classes.

- ### **`title`**

  (`str | None`, default: `None` ) – An optional title.

Methods:

- **`__bool__`** – Whether this section has a true-ish value.
- **`as_dict`** – Return this section's data as a dictionary.

Attributes:

- **`kind`** (`DocstringSectionKind`) – The section kind.
- **`title`** (`str | None`) – The section title.
- **`value`** (`list[DocstringTypeAlias]`) – The section value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(self, value: list[DocstringTypeAlias], title: str | None = None) -> None:
    """Initialize the section.

    Parameters:
        value: The section classes.
        title: An optional title.
    """
    super().__init__(title)
    self.value: list[DocstringTypeAlias] = value
```

### kind

```
kind: DocstringSectionKind = type_aliases
```

The section kind.

### title

```
title: str | None = title
```

The section title.

### value

```
value: list[DocstringTypeAlias] = value
```

The section value.

### __bool__

```
__bool__() -> bool
```

Whether this section has a true-ish value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __bool__(self) -> bool:
    """Whether this section has a true-ish value."""
    return bool(self.value)
```

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this section's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this section's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    if hasattr(self.value, "as_dict"):  # noqa: SIM108
        serialized_value = self.value.as_dict(**kwargs)
    else:
        serialized_value = self.value
    base = {"kind": self.kind.value, "value": serialized_value}
    if self.title:
        base["title"] = self.title
    return base
```

## DocstringSectionModules

```
DocstringSectionModules(
    value: list[DocstringModule], title: str | None = None
)
```

Bases: `DocstringSection`

```
              flowchart TD
              griffe.DocstringSectionModules[DocstringSectionModules]
              griffe._internal.docstrings.models.DocstringSection[DocstringSection]

                              griffe._internal.docstrings.models.DocstringSection --> griffe.DocstringSectionModules
                


              click griffe.DocstringSectionModules href "" "griffe.DocstringSectionModules"
              click griffe._internal.docstrings.models.DocstringSection href "" "griffe._internal.docstrings.models.DocstringSection"
```

This class represents a modules section.

Parameters:

- ### **`value`**

  (`list[DocstringModule]`) – The section modules.

- ### **`title`**

  (`str | None`, default: `None` ) – An optional title.

Methods:

- **`__bool__`** – Whether this section has a true-ish value.
- **`as_dict`** – Return this section's data as a dictionary.

Attributes:

- **`kind`** (`DocstringSectionKind`) – The section kind.
- **`title`** (`str | None`) – The section title.
- **`value`** (`list[DocstringModule]`) – The section value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(self, value: list[DocstringModule], title: str | None = None) -> None:
    """Initialize the section.

    Parameters:
        value: The section modules.
        title: An optional title.
    """
    super().__init__(title)
    self.value: list[DocstringModule] = value
```

### kind

```
kind: DocstringSectionKind = modules
```

The section kind.

### title

```
title: str | None = title
```

The section title.

### value

```
value: list[DocstringModule] = value
```

The section value.

### __bool__

```
__bool__() -> bool
```

Whether this section has a true-ish value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __bool__(self) -> bool:
    """Whether this section has a true-ish value."""
    return bool(self.value)
```

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this section's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this section's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    if hasattr(self.value, "as_dict"):  # noqa: SIM108
        serialized_value = self.value.as_dict(**kwargs)
    else:
        serialized_value = self.value
    base = {"kind": self.kind.value, "value": serialized_value}
    if self.title:
        base["title"] = self.title
    return base
```

## DocstringSectionDeprecated

```
DocstringSectionDeprecated(
    version: str, text: str, title: str | None = None
)
```

Bases: `DocstringSection`

```
              flowchart TD
              griffe.DocstringSectionDeprecated[DocstringSectionDeprecated]
              griffe._internal.docstrings.models.DocstringSection[DocstringSection]

                              griffe._internal.docstrings.models.DocstringSection --> griffe.DocstringSectionDeprecated
                


              click griffe.DocstringSectionDeprecated href "" "griffe.DocstringSectionDeprecated"
              click griffe._internal.docstrings.models.DocstringSection href "" "griffe._internal.docstrings.models.DocstringSection"
```

This class represents a deprecated section.

Parameters:

- ### **`version`**

  (`str`) – The deprecation version.

- ### **`text`**

  (`str`) – The deprecation text.

- ### **`title`**

  (`str | None`, default: `None` ) – An optional title.

Methods:

- **`__bool__`** – Whether this section has a true-ish value.
- **`as_dict`** – Return this section's data as a dictionary.

Attributes:

- **`kind`** (`DocstringSectionKind`) – The section kind.
- **`title`** (`str | None`) – The section title.
- **`value`** (`DocstringDeprecated`) – The section value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(self, version: str, text: str, title: str | None = None) -> None:
    """Initialize the section.

    Parameters:
        version: The deprecation version.
        text: The deprecation text.
        title: An optional title.
    """
    super().__init__(title)
    self.value: DocstringDeprecated = DocstringDeprecated(annotation=version, description=text)
```

### kind

```
kind: DocstringSectionKind = deprecated
```

The section kind.

### title

```
title: str | None = title
```

The section title.

### value

```
value: DocstringDeprecated = DocstringDeprecated(
    annotation=version, description=text
)
```

The section value.

### __bool__

```
__bool__() -> bool
```

Whether this section has a true-ish value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __bool__(self) -> bool:
    """Whether this section has a true-ish value."""
    return bool(self.value)
```

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this section's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this section's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    if hasattr(self.value, "as_dict"):  # noqa: SIM108
        serialized_value = self.value.as_dict(**kwargs)
    else:
        serialized_value = self.value
    base = {"kind": self.kind.value, "value": serialized_value}
    if self.title:
        base["title"] = self.title
    return base
```

## DocstringSectionAdmonition

```
DocstringSectionAdmonition(
    kind: str, text: str, title: str | None = None
)
```

Bases: `DocstringSection`

```
              flowchart TD
              griffe.DocstringSectionAdmonition[DocstringSectionAdmonition]
              griffe._internal.docstrings.models.DocstringSection[DocstringSection]

                              griffe._internal.docstrings.models.DocstringSection --> griffe.DocstringSectionAdmonition
                


              click griffe.DocstringSectionAdmonition href "" "griffe.DocstringSectionAdmonition"
              click griffe._internal.docstrings.models.DocstringSection href "" "griffe._internal.docstrings.models.DocstringSection"
```

This class represents an admonition section.

Parameters:

- ### **`kind`**

  (`str`) – The admonition kind.

- ### **`text`**

  (`str`) – The admonition text.

- ### **`title`**

  (`str | None`, default: `None` ) – An optional title.

Methods:

- **`__bool__`** – Whether this section has a true-ish value.
- **`as_dict`** – Return this section's data as a dictionary.

Attributes:

- **`kind`** (`DocstringSectionKind`) – The section kind.
- **`title`** (`str | None`) – The section title.
- **`value`** (`DocstringAdmonition`) – The section value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(self, kind: str, text: str, title: str | None = None) -> None:
    """Initialize the section.

    Parameters:
        kind: The admonition kind.
        text: The admonition text.
        title: An optional title.
    """
    super().__init__(title)
    self.value: DocstringAdmonition = DocstringAdmonition(annotation=kind, description=text)
```

### kind

```
kind: DocstringSectionKind = admonition
```

The section kind.

### title

```
title: str | None = title
```

The section title.

### value

```
value: DocstringAdmonition = DocstringAdmonition(
    annotation=kind, description=text
)
```

The section value.

### __bool__

```
__bool__() -> bool
```

Whether this section has a true-ish value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __bool__(self) -> bool:
    """Whether this section has a true-ish value."""
    return bool(self.value)
```

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this section's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this section's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    if hasattr(self.value, "as_dict"):  # noqa: SIM108
        serialized_value = self.value.as_dict(**kwargs)
    else:
        serialized_value = self.value
    base = {"kind": self.kind.value, "value": serialized_value}
    if self.title:
        base["title"] = self.title
    return base
```

## **Advanced API: Section items**

## DocstringAdmonition

```
DocstringAdmonition(
    *,
    description: str,
    annotation: str | Expr | None = None,
)
```

Bases: `DocstringElement`

```
              flowchart TD
              griffe.DocstringAdmonition[DocstringAdmonition]
              griffe._internal.docstrings.models.DocstringElement[DocstringElement]

                              griffe._internal.docstrings.models.DocstringElement --> griffe.DocstringAdmonition
                


              click griffe.DocstringAdmonition href "" "griffe.DocstringAdmonition"
              click griffe._internal.docstrings.models.DocstringElement href "" "griffe._internal.docstrings.models.DocstringElement"
```

This class represents an admonition.

Parameters:

- ### **`annotation`**

  (`str | Expr | None`, default: `None` ) – The element annotation, if any.

- ### **`description`**

  (`str`) – The element description.

Methods:

- **`as_dict`** – Return this element's data as a dictionary.

Attributes:

- **`annotation`** (`str | Expr | None`) – The element annotation.
- **`contents`** (`str`) – The contents of this admonition.
- **`description`** (`str`) – The element description.
- **`kind`** (`str | Expr | None`) – The kind of this admonition.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(self, *, description: str, annotation: str | Expr | None = None) -> None:
    """Initialize the element.

    Parameters:
        annotation: The element annotation, if any.
        description: The element description.
    """
    self.description: str = description
    """The element description."""
    self.annotation: str | Expr | None = annotation
    """The element annotation."""
```

### annotation

```
annotation: str | Expr | None = annotation
```

The element annotation.

### contents

```
contents: str
```

The contents of this admonition.

### description

```
description: str = description
```

The element description.

### kind

```
kind: str | Expr | None
```

The kind of this admonition.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this element's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
    """Return this element's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    return {
        "annotation": self.annotation,
        "description": self.description,
    }
```

## DocstringDeprecated

```
DocstringDeprecated(
    *,
    description: str,
    annotation: str | Expr | None = None,
)
```

Bases: `DocstringElement`

```
              flowchart TD
              griffe.DocstringDeprecated[DocstringDeprecated]
              griffe._internal.docstrings.models.DocstringElement[DocstringElement]

                              griffe._internal.docstrings.models.DocstringElement --> griffe.DocstringDeprecated
                


              click griffe.DocstringDeprecated href "" "griffe.DocstringDeprecated"
              click griffe._internal.docstrings.models.DocstringElement href "" "griffe._internal.docstrings.models.DocstringElement"
```

This class represents a documented deprecated item.

Parameters:

- ### **`annotation`**

  (`str | Expr | None`, default: `None` ) – The element annotation, if any.

- ### **`description`**

  (`str`) – The element description.

Methods:

- **`as_dict`** – Return this element's data as a dictionary.

Attributes:

- **`annotation`** (`str | Expr | None`) – The element annotation.
- **`description`** (`str`) – The element description.
- **`version`** (`str`) – The version of this deprecation.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(self, *, description: str, annotation: str | Expr | None = None) -> None:
    """Initialize the element.

    Parameters:
        annotation: The element annotation, if any.
        description: The element description.
    """
    self.description: str = description
    """The element description."""
    self.annotation: str | Expr | None = annotation
    """The element annotation."""
```

### annotation

```
annotation: str | Expr | None = annotation
```

The element annotation.

### description

```
description: str = description
```

The element description.

### version

```
version: str
```

The version of this deprecation.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this element's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
    """Return this element's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    return {
        "annotation": self.annotation,
        "description": self.description,
    }
```

## DocstringRaise

```
DocstringRaise(
    *,
    description: str,
    annotation: str | Expr | None = None,
)
```

Bases: `DocstringElement`

```
              flowchart TD
              griffe.DocstringRaise[DocstringRaise]
              griffe._internal.docstrings.models.DocstringElement[DocstringElement]

                              griffe._internal.docstrings.models.DocstringElement --> griffe.DocstringRaise
                


              click griffe.DocstringRaise href "" "griffe.DocstringRaise"
              click griffe._internal.docstrings.models.DocstringElement href "" "griffe._internal.docstrings.models.DocstringElement"
```

This class represents a documented raise value.

Parameters:

- ### **`annotation`**

  (`str | Expr | None`, default: `None` ) – The element annotation, if any.

- ### **`description`**

  (`str`) – The element description.

Methods:

- **`as_dict`** – Return this element's data as a dictionary.

Attributes:

- **`annotation`** (`str | Expr | None`) – The element annotation.
- **`description`** (`str`) – The element description.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(self, *, description: str, annotation: str | Expr | None = None) -> None:
    """Initialize the element.

    Parameters:
        annotation: The element annotation, if any.
        description: The element description.
    """
    self.description: str = description
    """The element description."""
    self.annotation: str | Expr | None = annotation
    """The element annotation."""
```

### annotation

```
annotation: str | Expr | None = annotation
```

The element annotation.

### description

```
description: str = description
```

The element description.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this element's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
    """Return this element's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    return {
        "annotation": self.annotation,
        "description": self.description,
    }
```

## DocstringWarn

```
DocstringWarn(
    *,
    description: str,
    annotation: str | Expr | None = None,
)
```

Bases: `DocstringElement`

```
              flowchart TD
              griffe.DocstringWarn[DocstringWarn]
              griffe._internal.docstrings.models.DocstringElement[DocstringElement]

                              griffe._internal.docstrings.models.DocstringElement --> griffe.DocstringWarn
                


              click griffe.DocstringWarn href "" "griffe.DocstringWarn"
              click griffe._internal.docstrings.models.DocstringElement href "" "griffe._internal.docstrings.models.DocstringElement"
```

This class represents a documented warn value.

Parameters:

- ### **`annotation`**

  (`str | Expr | None`, default: `None` ) – The element annotation, if any.

- ### **`description`**

  (`str`) – The element description.

Methods:

- **`as_dict`** – Return this element's data as a dictionary.

Attributes:

- **`annotation`** (`str | Expr | None`) – The element annotation.
- **`description`** (`str`) – The element description.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(self, *, description: str, annotation: str | Expr | None = None) -> None:
    """Initialize the element.

    Parameters:
        annotation: The element annotation, if any.
        description: The element description.
    """
    self.description: str = description
    """The element description."""
    self.annotation: str | Expr | None = annotation
    """The element annotation."""
```

### annotation

```
annotation: str | Expr | None = annotation
```

The element annotation.

### description

```
description: str = description
```

The element description.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this element's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
    """Return this element's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    return {
        "annotation": self.annotation,
        "description": self.description,
    }
```

## DocstringReturn

```
DocstringReturn(
    name: str,
    *,
    description: str,
    annotation: str | Expr | None = None,
    value: str | Expr | None = None,
)
```

Bases: `DocstringNamedElement`

```
              flowchart TD
              griffe.DocstringReturn[DocstringReturn]
              griffe._internal.docstrings.models.DocstringNamedElement[DocstringNamedElement]
              griffe._internal.docstrings.models.DocstringElement[DocstringElement]

                              griffe._internal.docstrings.models.DocstringNamedElement --> griffe.DocstringReturn
                                griffe._internal.docstrings.models.DocstringElement --> griffe._internal.docstrings.models.DocstringNamedElement
                



              click griffe.DocstringReturn href "" "griffe.DocstringReturn"
              click griffe._internal.docstrings.models.DocstringNamedElement href "" "griffe._internal.docstrings.models.DocstringNamedElement"
              click griffe._internal.docstrings.models.DocstringElement href "" "griffe._internal.docstrings.models.DocstringElement"
```

This class represents a documented return value.

Parameters:

- ### **`name`**

  (`str`) – The element name.

- ### **`description`**

  (`str`) – The element description.

- ### **`annotation`**

  (`str | Expr | None`, default: `None` ) – The element annotation, if any.

- ### **`value`**

  (`str | Expr | None`, default: `None` ) – The element value, as a string.

Methods:

- **`as_dict`** – Return this element's data as a dictionary.

Attributes:

- **`annotation`** (`str | Expr | None`) – The element annotation.
- **`description`** (`str`) – The element description.
- **`name`** (`str`) – The element name.
- **`value`** (`str | Expr | None`) – The element value, if any

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(
    self,
    name: str,
    *,
    description: str,
    annotation: str | Expr | None = None,
    value: str | Expr | None = None,
) -> None:
    """Initialize the element.

    Parameters:
        name: The element name.
        description: The element description.
        annotation: The element annotation, if any.
        value: The element value, as a string.
    """
    super().__init__(description=description, annotation=annotation)
    self.name: str = name
    """The element name."""
    self.value: str | Expr | None = value
    """The element value, if any"""
```

### annotation

```
annotation: str | Expr | None = annotation
```

The element annotation.

### description

```
description: str = description
```

The element description.

### name

```
name: str = name
```

The element name.

### value

```
value: str | Expr | None = value
```

The element value, if any

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this element's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this element's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    base = {"name": self.name, **super().as_dict(**kwargs)}
    if self.value is not None:
        base["value"] = self.value
    return base
```

## DocstringYield

```
DocstringYield(
    name: str,
    *,
    description: str,
    annotation: str | Expr | None = None,
    value: str | Expr | None = None,
)
```

Bases: `DocstringNamedElement`

```
              flowchart TD
              griffe.DocstringYield[DocstringYield]
              griffe._internal.docstrings.models.DocstringNamedElement[DocstringNamedElement]
              griffe._internal.docstrings.models.DocstringElement[DocstringElement]

                              griffe._internal.docstrings.models.DocstringNamedElement --> griffe.DocstringYield
                                griffe._internal.docstrings.models.DocstringElement --> griffe._internal.docstrings.models.DocstringNamedElement
                



              click griffe.DocstringYield href "" "griffe.DocstringYield"
              click griffe._internal.docstrings.models.DocstringNamedElement href "" "griffe._internal.docstrings.models.DocstringNamedElement"
              click griffe._internal.docstrings.models.DocstringElement href "" "griffe._internal.docstrings.models.DocstringElement"
```

This class represents a documented yield value.

Parameters:

- ### **`name`**

  (`str`) – The element name.

- ### **`description`**

  (`str`) – The element description.

- ### **`annotation`**

  (`str | Expr | None`, default: `None` ) – The element annotation, if any.

- ### **`value`**

  (`str | Expr | None`, default: `None` ) – The element value, as a string.

Methods:

- **`as_dict`** – Return this element's data as a dictionary.

Attributes:

- **`annotation`** (`str | Expr | None`) – The element annotation.
- **`description`** (`str`) – The element description.
- **`name`** (`str`) – The element name.
- **`value`** (`str | Expr | None`) – The element value, if any

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(
    self,
    name: str,
    *,
    description: str,
    annotation: str | Expr | None = None,
    value: str | Expr | None = None,
) -> None:
    """Initialize the element.

    Parameters:
        name: The element name.
        description: The element description.
        annotation: The element annotation, if any.
        value: The element value, as a string.
    """
    super().__init__(description=description, annotation=annotation)
    self.name: str = name
    """The element name."""
    self.value: str | Expr | None = value
    """The element value, if any"""
```

### annotation

```
annotation: str | Expr | None = annotation
```

The element annotation.

### description

```
description: str = description
```

The element description.

### name

```
name: str = name
```

The element name.

### value

```
value: str | Expr | None = value
```

The element value, if any

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this element's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this element's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    base = {"name": self.name, **super().as_dict(**kwargs)}
    if self.value is not None:
        base["value"] = self.value
    return base
```

## DocstringReceive

```
DocstringReceive(
    name: str,
    *,
    description: str,
    annotation: str | Expr | None = None,
    value: str | Expr | None = None,
)
```

Bases: `DocstringNamedElement`

```
              flowchart TD
              griffe.DocstringReceive[DocstringReceive]
              griffe._internal.docstrings.models.DocstringNamedElement[DocstringNamedElement]
              griffe._internal.docstrings.models.DocstringElement[DocstringElement]

                              griffe._internal.docstrings.models.DocstringNamedElement --> griffe.DocstringReceive
                                griffe._internal.docstrings.models.DocstringElement --> griffe._internal.docstrings.models.DocstringNamedElement
                



              click griffe.DocstringReceive href "" "griffe.DocstringReceive"
              click griffe._internal.docstrings.models.DocstringNamedElement href "" "griffe._internal.docstrings.models.DocstringNamedElement"
              click griffe._internal.docstrings.models.DocstringElement href "" "griffe._internal.docstrings.models.DocstringElement"
```

This class represents a documented receive value.

Parameters:

- ### **`name`**

  (`str`) – The element name.

- ### **`description`**

  (`str`) – The element description.

- ### **`annotation`**

  (`str | Expr | None`, default: `None` ) – The element annotation, if any.

- ### **`value`**

  (`str | Expr | None`, default: `None` ) – The element value, as a string.

Methods:

- **`as_dict`** – Return this element's data as a dictionary.

Attributes:

- **`annotation`** (`str | Expr | None`) – The element annotation.
- **`description`** (`str`) – The element description.
- **`name`** (`str`) – The element name.
- **`value`** (`str | Expr | None`) – The element value, if any

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(
    self,
    name: str,
    *,
    description: str,
    annotation: str | Expr | None = None,
    value: str | Expr | None = None,
) -> None:
    """Initialize the element.

    Parameters:
        name: The element name.
        description: The element description.
        annotation: The element annotation, if any.
        value: The element value, as a string.
    """
    super().__init__(description=description, annotation=annotation)
    self.name: str = name
    """The element name."""
    self.value: str | Expr | None = value
    """The element value, if any"""
```

### annotation

```
annotation: str | Expr | None = annotation
```

The element annotation.

### description

```
description: str = description
```

The element description.

### name

```
name: str = name
```

The element name.

### value

```
value: str | Expr | None = value
```

The element value, if any

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this element's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this element's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    base = {"name": self.name, **super().as_dict(**kwargs)}
    if self.value is not None:
        base["value"] = self.value
    return base
```

## DocstringParameter

```
DocstringParameter(
    name: str,
    *,
    description: str,
    annotation: str | Expr | None = None,
    value: str | Expr | None = None,
)
```

Bases: `DocstringNamedElement`

```
              flowchart TD
              griffe.DocstringParameter[DocstringParameter]
              griffe._internal.docstrings.models.DocstringNamedElement[DocstringNamedElement]
              griffe._internal.docstrings.models.DocstringElement[DocstringElement]

                              griffe._internal.docstrings.models.DocstringNamedElement --> griffe.DocstringParameter
                                griffe._internal.docstrings.models.DocstringElement --> griffe._internal.docstrings.models.DocstringNamedElement
                



              click griffe.DocstringParameter href "" "griffe.DocstringParameter"
              click griffe._internal.docstrings.models.DocstringNamedElement href "" "griffe._internal.docstrings.models.DocstringNamedElement"
              click griffe._internal.docstrings.models.DocstringElement href "" "griffe._internal.docstrings.models.DocstringElement"
```

This class represent a documented function parameter.

Parameters:

- ### **`name`**

  (`str`) – The element name.

- ### **`description`**

  (`str`) – The element description.

- ### **`annotation`**

  (`str | Expr | None`, default: `None` ) – The element annotation, if any.

- ### **`value`**

  (`str | Expr | None`, default: `None` ) – The element value, as a string.

Methods:

- **`as_dict`** – Return this element's data as a dictionary.

Attributes:

- **`annotation`** (`str | Expr | None`) – The element annotation.
- **`default`** (`str | Expr | None`) – The default value of this parameter.
- **`description`** (`str`) – The element description.
- **`name`** (`str`) – The element name.
- **`value`** (`str | Expr | None`) – The element value, if any

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(
    self,
    name: str,
    *,
    description: str,
    annotation: str | Expr | None = None,
    value: str | Expr | None = None,
) -> None:
    """Initialize the element.

    Parameters:
        name: The element name.
        description: The element description.
        annotation: The element annotation, if any.
        value: The element value, as a string.
    """
    super().__init__(description=description, annotation=annotation)
    self.name: str = name
    """The element name."""
    self.value: str | Expr | None = value
    """The element value, if any"""
```

### annotation

```
annotation: str | Expr | None = annotation
```

The element annotation.

### default

```
default: str | Expr | None
```

The default value of this parameter.

### description

```
description: str = description
```

The element description.

### name

```
name: str = name
```

The element name.

### value

```
value: str | Expr | None = value
```

The element value, if any

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this element's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this element's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    base = {"name": self.name, **super().as_dict(**kwargs)}
    if self.value is not None:
        base["value"] = self.value
    return base
```

## DocstringTypeParameter

```
DocstringTypeParameter(
    name: str,
    *,
    description: str,
    annotation: str | Expr | None = None,
    value: str | Expr | None = None,
)
```

Bases: `DocstringNamedElement`

```
              flowchart TD
              griffe.DocstringTypeParameter[DocstringTypeParameter]
              griffe._internal.docstrings.models.DocstringNamedElement[DocstringNamedElement]
              griffe._internal.docstrings.models.DocstringElement[DocstringElement]

                              griffe._internal.docstrings.models.DocstringNamedElement --> griffe.DocstringTypeParameter
                                griffe._internal.docstrings.models.DocstringElement --> griffe._internal.docstrings.models.DocstringNamedElement
                



              click griffe.DocstringTypeParameter href "" "griffe.DocstringTypeParameter"
              click griffe._internal.docstrings.models.DocstringNamedElement href "" "griffe._internal.docstrings.models.DocstringNamedElement"
              click griffe._internal.docstrings.models.DocstringElement href "" "griffe._internal.docstrings.models.DocstringElement"
```

This class represent a documented type parameter.

Parameters:

- ### **`name`**

  (`str`) – The element name.

- ### **`description`**

  (`str`) – The element description.

- ### **`annotation`**

  (`str | Expr | None`, default: `None` ) – The element annotation, if any.

- ### **`value`**

  (`str | Expr | None`, default: `None` ) – The element value, as a string.

Methods:

- **`as_dict`** – Return this element's data as a dictionary.

Attributes:

- **`annotation`** (`str | Expr | None`) – The element annotation.
- **`bound`** (`str | Expr | None`) – The bound of this type parameter.
- **`constraints`** (`tuple[str | Expr, ...] | None`) – The constraints of this type parameter.
- **`default`** (`str | Expr | None`) – The default value of this type parameter.
- **`description`** (`str`) – The element description.
- **`name`** (`str`) – The element name.
- **`value`** (`str | Expr | None`) – The element value, if any

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(
    self,
    name: str,
    *,
    description: str,
    annotation: str | Expr | None = None,
    value: str | Expr | None = None,
) -> None:
    """Initialize the element.

    Parameters:
        name: The element name.
        description: The element description.
        annotation: The element annotation, if any.
        value: The element value, as a string.
    """
    super().__init__(description=description, annotation=annotation)
    self.name: str = name
    """The element name."""
    self.value: str | Expr | None = value
    """The element value, if any"""
```

### annotation

```
annotation: str | Expr | None = annotation
```

The element annotation.

### bound

```
bound: str | Expr | None
```

The bound of this type parameter.

### constraints

```
constraints: tuple[str | Expr, ...] | None
```

The constraints of this type parameter.

### default

```
default: str | Expr | None
```

The default value of this type parameter.

### description

```
description: str = description
```

The element description.

### name

```
name: str = name
```

The element name.

### value

```
value: str | Expr | None = value
```

The element value, if any

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this element's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this element's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    base = {"name": self.name, **super().as_dict(**kwargs)}
    if self.value is not None:
        base["value"] = self.value
    return base
```

## DocstringAttribute

```
DocstringAttribute(
    name: str,
    *,
    description: str,
    annotation: str | Expr | None = None,
    value: str | Expr | None = None,
)
```

Bases: `DocstringNamedElement`

```
              flowchart TD
              griffe.DocstringAttribute[DocstringAttribute]
              griffe._internal.docstrings.models.DocstringNamedElement[DocstringNamedElement]
              griffe._internal.docstrings.models.DocstringElement[DocstringElement]

                              griffe._internal.docstrings.models.DocstringNamedElement --> griffe.DocstringAttribute
                                griffe._internal.docstrings.models.DocstringElement --> griffe._internal.docstrings.models.DocstringNamedElement
                



              click griffe.DocstringAttribute href "" "griffe.DocstringAttribute"
              click griffe._internal.docstrings.models.DocstringNamedElement href "" "griffe._internal.docstrings.models.DocstringNamedElement"
              click griffe._internal.docstrings.models.DocstringElement href "" "griffe._internal.docstrings.models.DocstringElement"
```

This class represents a documented module/class attribute.

Parameters:

- ### **`name`**

  (`str`) – The element name.

- ### **`description`**

  (`str`) – The element description.

- ### **`annotation`**

  (`str | Expr | None`, default: `None` ) – The element annotation, if any.

- ### **`value`**

  (`str | Expr | None`, default: `None` ) – The element value, as a string.

Methods:

- **`as_dict`** – Return this element's data as a dictionary.

Attributes:

- **`annotation`** (`str | Expr | None`) – The element annotation.
- **`description`** (`str`) – The element description.
- **`name`** (`str`) – The element name.
- **`value`** (`str | Expr | None`) – The element value, if any

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(
    self,
    name: str,
    *,
    description: str,
    annotation: str | Expr | None = None,
    value: str | Expr | None = None,
) -> None:
    """Initialize the element.

    Parameters:
        name: The element name.
        description: The element description.
        annotation: The element annotation, if any.
        value: The element value, as a string.
    """
    super().__init__(description=description, annotation=annotation)
    self.name: str = name
    """The element name."""
    self.value: str | Expr | None = value
    """The element value, if any"""
```

### annotation

```
annotation: str | Expr | None = annotation
```

The element annotation.

### description

```
description: str = description
```

The element description.

### name

```
name: str = name
```

The element name.

### value

```
value: str | Expr | None = value
```

The element value, if any

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this element's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this element's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    base = {"name": self.name, **super().as_dict(**kwargs)}
    if self.value is not None:
        base["value"] = self.value
    return base
```

## DocstringFunction

```
DocstringFunction(
    name: str,
    *,
    description: str,
    annotation: str | Expr | None = None,
    value: str | Expr | None = None,
)
```

Bases: `DocstringNamedElement`

```
              flowchart TD
              griffe.DocstringFunction[DocstringFunction]
              griffe._internal.docstrings.models.DocstringNamedElement[DocstringNamedElement]
              griffe._internal.docstrings.models.DocstringElement[DocstringElement]

                              griffe._internal.docstrings.models.DocstringNamedElement --> griffe.DocstringFunction
                                griffe._internal.docstrings.models.DocstringElement --> griffe._internal.docstrings.models.DocstringNamedElement
                



              click griffe.DocstringFunction href "" "griffe.DocstringFunction"
              click griffe._internal.docstrings.models.DocstringNamedElement href "" "griffe._internal.docstrings.models.DocstringNamedElement"
              click griffe._internal.docstrings.models.DocstringElement href "" "griffe._internal.docstrings.models.DocstringElement"
```

This class represents a documented function.

Parameters:

- ### **`name`**

  (`str`) – The element name.

- ### **`description`**

  (`str`) – The element description.

- ### **`annotation`**

  (`str | Expr | None`, default: `None` ) – The element annotation, if any.

- ### **`value`**

  (`str | Expr | None`, default: `None` ) – The element value, as a string.

Methods:

- **`as_dict`** – Return this element's data as a dictionary.

Attributes:

- **`annotation`** (`str | Expr | None`) – The element annotation.
- **`description`** (`str`) – The element description.
- **`name`** (`str`) – The element name.
- **`signature`** (`str | Expr | None`) – The function signature.
- **`value`** (`str | Expr | None`) – The element value, if any

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(
    self,
    name: str,
    *,
    description: str,
    annotation: str | Expr | None = None,
    value: str | Expr | None = None,
) -> None:
    """Initialize the element.

    Parameters:
        name: The element name.
        description: The element description.
        annotation: The element annotation, if any.
        value: The element value, as a string.
    """
    super().__init__(description=description, annotation=annotation)
    self.name: str = name
    """The element name."""
    self.value: str | Expr | None = value
    """The element value, if any"""
```

### annotation

```
annotation: str | Expr | None = annotation
```

The element annotation.

### description

```
description: str = description
```

The element description.

### name

```
name: str = name
```

The element name.

### signature

```
signature: str | Expr | None
```

The function signature.

### value

```
value: str | Expr | None = value
```

The element value, if any

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this element's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this element's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    base = {"name": self.name, **super().as_dict(**kwargs)}
    if self.value is not None:
        base["value"] = self.value
    return base
```

## DocstringClass

```
DocstringClass(
    name: str,
    *,
    description: str,
    annotation: str | Expr | None = None,
    value: str | Expr | None = None,
)
```

Bases: `DocstringNamedElement`

```
              flowchart TD
              griffe.DocstringClass[DocstringClass]
              griffe._internal.docstrings.models.DocstringNamedElement[DocstringNamedElement]
              griffe._internal.docstrings.models.DocstringElement[DocstringElement]

                              griffe._internal.docstrings.models.DocstringNamedElement --> griffe.DocstringClass
                                griffe._internal.docstrings.models.DocstringElement --> griffe._internal.docstrings.models.DocstringNamedElement
                



              click griffe.DocstringClass href "" "griffe.DocstringClass"
              click griffe._internal.docstrings.models.DocstringNamedElement href "" "griffe._internal.docstrings.models.DocstringNamedElement"
              click griffe._internal.docstrings.models.DocstringElement href "" "griffe._internal.docstrings.models.DocstringElement"
```

This class represents a documented class.

Parameters:

- ### **`name`**

  (`str`) – The element name.

- ### **`description`**

  (`str`) – The element description.

- ### **`annotation`**

  (`str | Expr | None`, default: `None` ) – The element annotation, if any.

- ### **`value`**

  (`str | Expr | None`, default: `None` ) – The element value, as a string.

Methods:

- **`as_dict`** – Return this element's data as a dictionary.

Attributes:

- **`annotation`** (`str | Expr | None`) – The element annotation.
- **`description`** (`str`) – The element description.
- **`name`** (`str`) – The element name.
- **`signature`** (`str | Expr | None`) – The class signature.
- **`value`** (`str | Expr | None`) – The element value, if any

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(
    self,
    name: str,
    *,
    description: str,
    annotation: str | Expr | None = None,
    value: str | Expr | None = None,
) -> None:
    """Initialize the element.

    Parameters:
        name: The element name.
        description: The element description.
        annotation: The element annotation, if any.
        value: The element value, as a string.
    """
    super().__init__(description=description, annotation=annotation)
    self.name: str = name
    """The element name."""
    self.value: str | Expr | None = value
    """The element value, if any"""
```

### annotation

```
annotation: str | Expr | None = annotation
```

The element annotation.

### description

```
description: str = description
```

The element description.

### name

```
name: str = name
```

The element name.

### signature

```
signature: str | Expr | None
```

The class signature.

### value

```
value: str | Expr | None = value
```

The element value, if any

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this element's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this element's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    base = {"name": self.name, **super().as_dict(**kwargs)}
    if self.value is not None:
        base["value"] = self.value
    return base
```

## DocstringTypeAlias

```
DocstringTypeAlias(
    name: str,
    *,
    description: str,
    annotation: str | Expr | None = None,
    value: str | Expr | None = None,
)
```

Bases: `DocstringNamedElement`

```
              flowchart TD
              griffe.DocstringTypeAlias[DocstringTypeAlias]
              griffe._internal.docstrings.models.DocstringNamedElement[DocstringNamedElement]
              griffe._internal.docstrings.models.DocstringElement[DocstringElement]

                              griffe._internal.docstrings.models.DocstringNamedElement --> griffe.DocstringTypeAlias
                                griffe._internal.docstrings.models.DocstringElement --> griffe._internal.docstrings.models.DocstringNamedElement
                



              click griffe.DocstringTypeAlias href "" "griffe.DocstringTypeAlias"
              click griffe._internal.docstrings.models.DocstringNamedElement href "" "griffe._internal.docstrings.models.DocstringNamedElement"
              click griffe._internal.docstrings.models.DocstringElement href "" "griffe._internal.docstrings.models.DocstringElement"
```

This class represents a documented type alias.

Parameters:

- ### **`name`**

  (`str`) – The element name.

- ### **`description`**

  (`str`) – The element description.

- ### **`annotation`**

  (`str | Expr | None`, default: `None` ) – The element annotation, if any.

- ### **`value`**

  (`str | Expr | None`, default: `None` ) – The element value, as a string.

Methods:

- **`as_dict`** – Return this element's data as a dictionary.

Attributes:

- **`annotation`** (`str | Expr | None`) – The element annotation.
- **`description`** (`str`) – The element description.
- **`name`** (`str`) – The element name.
- **`value`** (`str | Expr | None`) – The element value, if any

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(
    self,
    name: str,
    *,
    description: str,
    annotation: str | Expr | None = None,
    value: str | Expr | None = None,
) -> None:
    """Initialize the element.

    Parameters:
        name: The element name.
        description: The element description.
        annotation: The element annotation, if any.
        value: The element value, as a string.
    """
    super().__init__(description=description, annotation=annotation)
    self.name: str = name
    """The element name."""
    self.value: str | Expr | None = value
    """The element value, if any"""
```

### annotation

```
annotation: str | Expr | None = annotation
```

The element annotation.

### description

```
description: str = description
```

The element description.

### name

```
name: str = name
```

The element name.

### value

```
value: str | Expr | None = value
```

The element value, if any

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this element's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this element's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    base = {"name": self.name, **super().as_dict(**kwargs)}
    if self.value is not None:
        base["value"] = self.value
    return base
```

## DocstringModule

```
DocstringModule(
    name: str,
    *,
    description: str,
    annotation: str | Expr | None = None,
    value: str | Expr | None = None,
)
```

Bases: `DocstringNamedElement`

```
              flowchart TD
              griffe.DocstringModule[DocstringModule]
              griffe._internal.docstrings.models.DocstringNamedElement[DocstringNamedElement]
              griffe._internal.docstrings.models.DocstringElement[DocstringElement]

                              griffe._internal.docstrings.models.DocstringNamedElement --> griffe.DocstringModule
                                griffe._internal.docstrings.models.DocstringElement --> griffe._internal.docstrings.models.DocstringNamedElement
                



              click griffe.DocstringModule href "" "griffe.DocstringModule"
              click griffe._internal.docstrings.models.DocstringNamedElement href "" "griffe._internal.docstrings.models.DocstringNamedElement"
              click griffe._internal.docstrings.models.DocstringElement href "" "griffe._internal.docstrings.models.DocstringElement"
```

This class represents a documented module.

Parameters:

- ### **`name`**

  (`str`) – The element name.

- ### **`description`**

  (`str`) – The element description.

- ### **`annotation`**

  (`str | Expr | None`, default: `None` ) – The element annotation, if any.

- ### **`value`**

  (`str | Expr | None`, default: `None` ) – The element value, as a string.

Methods:

- **`as_dict`** – Return this element's data as a dictionary.

Attributes:

- **`annotation`** (`str | Expr | None`) – The element annotation.
- **`description`** (`str`) – The element description.
- **`name`** (`str`) – The element name.
- **`value`** (`str | Expr | None`) – The element value, if any

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(
    self,
    name: str,
    *,
    description: str,
    annotation: str | Expr | None = None,
    value: str | Expr | None = None,
) -> None:
    """Initialize the element.

    Parameters:
        name: The element name.
        description: The element description.
        annotation: The element annotation, if any.
        value: The element value, as a string.
    """
    super().__init__(description=description, annotation=annotation)
    self.name: str = name
    """The element name."""
    self.value: str | Expr | None = value
    """The element value, if any"""
```

### annotation

```
annotation: str | Expr | None = annotation
```

The element annotation.

### description

```
description: str = description
```

The element description.

### name

```
name: str = name
```

The element name.

### value

```
value: str | Expr | None = value
```

The element value, if any

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this element's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this element's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    base = {"name": self.name, **super().as_dict(**kwargs)}
    if self.value is not None:
        base["value"] = self.value
    return base
```

## **Models base classes**

## DocstringElement

```
DocstringElement(
    *,
    description: str,
    annotation: str | Expr | None = None,
)
```

This base class represents annotated, nameless elements.

Parameters:

- ### **`annotation`**

  (`str | Expr | None`, default: `None` ) – The element annotation, if any.

- ### **`description`**

  (`str`) – The element description.

Methods:

- **`as_dict`** – Return this element's data as a dictionary.

Attributes:

- **`annotation`** (`str | Expr | None`) – The element annotation.
- **`description`** (`str`) – The element description.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(self, *, description: str, annotation: str | Expr | None = None) -> None:
    """Initialize the element.

    Parameters:
        annotation: The element annotation, if any.
        description: The element description.
    """
    self.description: str = description
    """The element description."""
    self.annotation: str | Expr | None = annotation
    """The element annotation."""
```

### annotation

```
annotation: str | Expr | None = annotation
```

The element annotation.

### description

```
description: str = description
```

The element description.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this element's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
    """Return this element's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    return {
        "annotation": self.annotation,
        "description": self.description,
    }
```

## DocstringNamedElement

```
DocstringNamedElement(
    name: str,
    *,
    description: str,
    annotation: str | Expr | None = None,
    value: str | Expr | None = None,
)
```

Bases: `DocstringElement`

```
              flowchart TD
              griffe.DocstringNamedElement[DocstringNamedElement]
              griffe._internal.docstrings.models.DocstringElement[DocstringElement]

                              griffe._internal.docstrings.models.DocstringElement --> griffe.DocstringNamedElement
                


              click griffe.DocstringNamedElement href "" "griffe.DocstringNamedElement"
              click griffe._internal.docstrings.models.DocstringElement href "" "griffe._internal.docstrings.models.DocstringElement"
```

This base class represents annotated, named elements.

Parameters:

- ### **`name`**

  (`str`) – The element name.

- ### **`description`**

  (`str`) – The element description.

- ### **`annotation`**

  (`str | Expr | None`, default: `None` ) – The element annotation, if any.

- ### **`value`**

  (`str | Expr | None`, default: `None` ) – The element value, as a string.

Methods:

- **`as_dict`** – Return this element's data as a dictionary.

Attributes:

- **`annotation`** (`str | Expr | None`) – The element annotation.
- **`description`** (`str`) – The element description.
- **`name`** (`str`) – The element name.
- **`value`** (`str | Expr | None`) – The element value, if any

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(
    self,
    name: str,
    *,
    description: str,
    annotation: str | Expr | None = None,
    value: str | Expr | None = None,
) -> None:
    """Initialize the element.

    Parameters:
        name: The element name.
        description: The element description.
        annotation: The element annotation, if any.
        value: The element value, as a string.
    """
    super().__init__(description=description, annotation=annotation)
    self.name: str = name
    """The element name."""
    self.value: str | Expr | None = value
    """The element value, if any"""
```

### annotation

```
annotation: str | Expr | None = annotation
```

The element annotation.

### description

```
description: str = description
```

The element description.

### name

```
name: str = name
```

The element name.

### value

```
value: str | Expr | None = value
```

The element value, if any

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this element's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this element's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    base = {"name": self.name, **super().as_dict(**kwargs)}
    if self.value is not None:
        base["value"] = self.value
    return base
```

## DocstringSection

```
DocstringSection(title: str | None = None)
```

This class represents a docstring section.

Parameters:

- ### **`title`**

  (`str | None`, default: `None` ) – An optional title.

Methods:

- **`__bool__`** – Whether this section has a true-ish value.
- **`as_dict`** – Return this section's data as a dictionary.

Attributes:

- **`kind`** (`DocstringSectionKind`) – The section kind.
- **`title`** (`str | None`) – The section title.
- **`value`** (`Any`) – The section value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __init__(self, title: str | None = None) -> None:
    """Initialize the section.

    Parameters:
        title: An optional title.
    """
    self.title: str | None = title
    """The section title."""
    self.value: Any = None
    """The section value."""
```

### kind

```
kind: DocstringSectionKind
```

The section kind.

### title

```
title: str | None = title
```

The section title.

### value

```
value: Any = None
```

The section value.

### __bool__

```
__bool__() -> bool
```

Whether this section has a true-ish value.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def __bool__(self) -> bool:
    """Whether this section has a true-ish value."""
    return bool(self.value)
```

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this section's data as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/docstrings/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this section's data as a dictionary.

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    if hasattr(self.value, "as_dict"):  # noqa: SIM108
        serialized_value = self.value.as_dict(**kwargs)
    else:
        serialized_value = self.value
    base = {"kind": self.kind.value, "value": serialized_value}
    if self.title:
        base["title"] = self.title
    return base
```
