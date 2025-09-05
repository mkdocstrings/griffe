# Docstring parsers

## **Main API**

## parse

```
parse(
    docstring: Docstring,
    parser: DocstringStyle | Parser | None,
    **options: Any,
) -> list[DocstringSection]
```

Parse the docstring.

Parameters:

- ### **`docstring`**

  (`Docstring`) – The docstring to parse.

- ### **`parser`**

  (`DocstringStyle | Parser | None`) – The docstring parser to use. If None, return a single text section.

- ### **`**options`**

  (`Any`, default: `{}` ) – The options accepted by the parser.

Returns:

- `list[DocstringSection]` – A list of docstring sections.

## parse_auto

```
parse_auto(
    docstring: Docstring,
    *,
    method: DocstringDetectionMethod = "heuristics",
    style_order: list[Parser]
    | list[DocstringStyle]
    | None = None,
    default: Parser | DocstringStyle | None = None,
    per_style_options: PerStyleOptions | None = None,
    **options: Any,
) -> list[DocstringSection]
```

Parse a docstring by automatically detecting the style it uses.

[Sponsors only](../../../../insiders/) — [Insiders 1.3.0](../../../../insiders/changelog/#1.3.0).

See infer_docstring_style for more information on the available parameters.

Parameters:

- ### **`docstring`**

  (`Docstring`) – The docstring to parse.

- ### **`method`**

  (`DocstringDetectionMethod`, default: `'heuristics'` ) – The method to use to infer the parser.

- ### **`style_order`**

  (`list[Parser] | list[DocstringStyle] | None`, default: `None` ) – The order of the styles to try when inferring the parser.

- ### **`default`**

  (`Parser | DocstringStyle | None`, default: `None` ) – The default parser to use if the inference fails.

- ### **`per_style_options`**

  (`PerStyleOptions | None`, default: `None` ) – Additional parsing options per style.

- ### **`**options`**

  (`Any`, default: `{}` ) – Deprecated. Use per_style_options instead.

Returns:

- `list[DocstringSection]` – A list of docstring sections.

## parse_google

```
parse_google(
    docstring: Docstring,
    *,
    ignore_init_summary: bool = False,
    trim_doctest_flags: bool = True,
    returns_multiple_items: bool = True,
    returns_named_value: bool = True,
    returns_type_in_property_summary: bool = False,
    receives_multiple_items: bool = True,
    receives_named_value: bool = True,
    warn_unknown_params: bool = True,
    warn_missing_types: bool = True,
    warnings: bool = True,
    **options: Any,
) -> list[DocstringSection]
```

Parse a Google-style docstring.

This function iterates on lines of a docstring to build sections. It then returns this list of sections.

Parameters:

- ### **`docstring`**

  (`Docstring`) – The docstring to parse.

- ### **`ignore_init_summary`**

  (`bool`, default: `False` ) – Whether to ignore the summary in __init__ methods' docstrings.

- ### **`trim_doctest_flags`**

  (`bool`, default: `True` ) – Whether to remove doctest flags from Python example blocks.

- ### **`returns_multiple_items`**

  (`bool`, default: `True` ) – Whether to parse multiple items in Yields and Returns sections. When true, each item's continuation lines must be indented. When false (single item), no further indentation is required.

- ### **`returns_named_value`**

  (`bool`, default: `True` ) – Whether to parse Yields and Returns section items as name and description, rather than type and description. When true, type must be wrapped in parentheses: (int): Description.. Names are optional: name (int): Description.. When false, parentheses are optional but the items cannot be named: int: Description.

- ### **`receives_multiple_items`**

  (`bool`, default: `True` ) – Whether to parse multiple items in Receives sections. When true, each item's continuation lines must be indented. When false (single item), no further indentation is required.

- ### **`receives_named_value`**

  (`bool`, default: `True` ) – Whether to parse Receives section items as name and description, rather than type and description. When true, type must be wrapped in parentheses: (int): Description.. Names are optional: name (int): Description.. When false, parentheses are optional but the items cannot be named: int: Description.

- ### **`returns_type_in_property_summary`**

  (`bool`, default: `False` ) – Whether to parse the return type of properties at the beginning of their summary: str: Summary of the property.

- ### **`warn_unknown_params`**

  (`bool`, default: `True` ) – Warn about documented parameters not appearing in the signature.

- ### **`warn_missing_types`**

  (`bool`, default: `True` ) – Warn about missing types/annotations for parameters, return values, etc.

- ### **`warnings`**

  (`bool`, default: `True` ) – Whether to log warnings at all.

- ### **`**options`**

  (`Any`, default: `{}` ) – Swallowing keyword arguments for backward-compatibility.

Returns:

- `list[DocstringSection]` – A list of docstring sections.

## parse_numpy

```
parse_numpy(
    docstring: Docstring,
    *,
    ignore_init_summary: bool = False,
    trim_doctest_flags: bool = True,
    warn_unknown_params: bool = True,
    warn_missing_types: bool = True,
    warnings: bool = True,
    **options: Any,
) -> list[DocstringSection]
```

Parse a Numpydoc-style docstring.

This function iterates on lines of a docstring to build sections. It then returns this list of sections.

Parameters:

- ### **`docstring`**

  (`Docstring`) – The docstring to parse.

- ### **`ignore_init_summary`**

  (`bool`, default: `False` ) – Whether to ignore the summary in __init__ methods' docstrings.

- ### **`trim_doctest_flags`**

  (`bool`, default: `True` ) – Whether to remove doctest flags from Python example blocks.

- ### **`warn_unknown_params`**

  (`bool`, default: `True` ) – Warn about documented parameters not appearing in the signature.

- ### **`warn_missing_types`**

  (`bool`, default: `True` ) – Warn about missing types/annotations for parameters, return values, etc.

- ### **`warnings`**

  (`bool`, default: `True` ) – Whether to log warnings at all.

- ### **`**options`**

  (`Any`, default: `{}` ) – Swallowing keyword arguments for backward-compatibility.

Returns:

- `list[DocstringSection]` – A list of docstring sections.

## parse_sphinx

```
parse_sphinx(
    docstring: Docstring,
    *,
    warn_unknown_params: bool = True,
    warnings: bool = True,
    **options: Any,
) -> list[DocstringSection]
```

Parse a Sphinx-style docstring.

Parameters:

- ### **`docstring`**

  (`Docstring`) – The docstring to parse.

- ### **`warn_unknown_params`**

  (`bool`, default: `True` ) – Warn about documented parameters not appearing in the signature.

- ### **`warnings`**

  (`bool`, default: `True` ) – Whether to log warnings at all.

- ### **`**options`**

  (`Any`, default: `{}` ) – Swallowing keyword arguments for backward-compatibility.

Returns:

- `list[DocstringSection]` – A list of docstring sections.

## DocstringStyle

```
DocstringStyle = Literal[
    "google", "numpy", "sphinx", "auto"
]
```

The supported docstring styles (literal values of the Parser enumeration).

## **Parser options**

## DocstringOptions

```
DocstringOptions = Union[
    GoogleOptions, NumpyOptions, SphinxOptions, AutoOptions
]
```

The options for each docstring style.

## GoogleOptions

Bases: `TypedDict`

```
              flowchart TD
              griffe.GoogleOptions[GoogleOptions]

              

              click griffe.GoogleOptions href "" "griffe.GoogleOptions"
```

Options for parsing Google-style docstrings.

Attributes:

- **`ignore_init_summary`** (`bool`) – Whether to ignore the summary in __init__ methods' docstrings.
- **`receives_multiple_items`** (`bool`) – Whether to parse multiple items in Receives sections.
- **`receives_named_value`** (`bool`) – Whether to parse Receives section items as name and description, rather than type and description.
- **`returns_multiple_items`** (`bool`) – Whether to parse multiple items in Yields and Returns sections.
- **`returns_named_value`** (`bool`) – Whether to parse Yields and Returns section items as name and description, rather than type and description.
- **`returns_type_in_property_summary`** (`bool`) – Whether to parse the return type of properties at the beginning of their summary.
- **`trim_doctest_flags`** (`bool`) – Whether to remove doctest flags from Python example blocks.
- **`warn_missing_types`** (`bool`) – Whether to warn about missing types/annotations for parameters, return values, etc.
- **`warn_unknown_params`** (`bool`) – Whether to warn about unknown parameters.
- **`warnings`** (`bool`) – Whether to issue warnings for parsing issues.

### ignore_init_summary

```
ignore_init_summary: bool
```

Whether to ignore the summary in `__init__` methods' docstrings.

### receives_multiple_items

```
receives_multiple_items: bool
```

Whether to parse multiple items in `Receives` sections.

### receives_named_value

```
receives_named_value: bool
```

Whether to parse `Receives` section items as name and description, rather than type and description.

### returns_multiple_items

```
returns_multiple_items: bool
```

Whether to parse multiple items in `Yields` and `Returns` sections.

### returns_named_value

```
returns_named_value: bool
```

Whether to parse `Yields` and `Returns` section items as name and description, rather than type and description.

### returns_type_in_property_summary

```
returns_type_in_property_summary: bool
```

Whether to parse the return type of properties at the beginning of their summary.

### trim_doctest_flags

```
trim_doctest_flags: bool
```

Whether to remove doctest flags from Python example blocks.

### warn_missing_types

```
warn_missing_types: bool
```

Whether to warn about missing types/annotations for parameters, return values, etc.

### warn_unknown_params

```
warn_unknown_params: bool
```

Whether to warn about unknown parameters.

### warnings

```
warnings: bool
```

Whether to issue warnings for parsing issues.

## NumpyOptions

Bases: `TypedDict`

```
              flowchart TD
              griffe.NumpyOptions[NumpyOptions]

              

              click griffe.NumpyOptions href "" "griffe.NumpyOptions"
```

Options for parsing Numpydoc-style docstrings.

Attributes:

- **`ignore_init_summary`** (`bool`) – Whether to ignore the summary in __init__ methods' docstrings.
- **`trim_doctest_flags`** (`bool`) – Whether to remove doctest flags from Python example blocks.
- **`warn_missing_types`** (`bool`) – Whether to warn about missing types/annotations for parameters, return values, etc.
- **`warn_unknown_params`** (`bool`) – Whether to warn about unknown parameters.
- **`warnings`** (`bool`) – Whether to issue warnings for parsing issues.

### ignore_init_summary

```
ignore_init_summary: bool
```

Whether to ignore the summary in `__init__` methods' docstrings.

### trim_doctest_flags

```
trim_doctest_flags: bool
```

Whether to remove doctest flags from Python example blocks.

### warn_missing_types

```
warn_missing_types: bool
```

Whether to warn about missing types/annotations for parameters, return values, etc.

### warn_unknown_params

```
warn_unknown_params: bool
```

Whether to warn about unknown parameters.

### warnings

```
warnings: bool
```

Whether to issue warnings for parsing issues.

## SphinxOptions

Bases: `TypedDict`

```
              flowchart TD
              griffe.SphinxOptions[SphinxOptions]

              

              click griffe.SphinxOptions href "" "griffe.SphinxOptions"
```

Options for parsing Sphinx-style docstrings.

Attributes:

- **`warn_unknown_params`** (`bool`) – Whether to warn about unknown parameters.
- **`warnings`** (`bool`) – Whether to issue warnings for parsing issues.

### warn_unknown_params

```
warn_unknown_params: bool
```

Whether to warn about unknown parameters.

### warnings

```
warnings: bool
```

Whether to issue warnings for parsing issues.

## AutoOptions

Bases: `TypedDict`

```
              flowchart TD
              griffe.AutoOptions[AutoOptions]

              

              click griffe.AutoOptions href "" "griffe.AutoOptions"
```

Options for Auto-style docstrings.

Attributes:

- **`default`** (`Parser | DocstringStyle | None`) – The default parser to use if the inference fails.
- **`method`** (`DocstringDetectionMethod`) – The method to use to infer the parser.
- **`per_style_options`** (`PerStyleOptions | None`) – Additional parsing options per style.
- **`style_order`** (`list[Parser] | list[DocstringStyle] | None`) – The order of styles to try when inferring the parser.

### default

```
default: Parser | DocstringStyle | None
```

The default parser to use if the inference fails.

### method

```
method: DocstringDetectionMethod
```

The method to use to infer the parser.

### per_style_options

```
per_style_options: PerStyleOptions | None
```

Additional parsing options per style.

### style_order

```
style_order: list[Parser] | list[DocstringStyle] | None
```

The order of styles to try when inferring the parser.

## PerStyleOptions

Bases: `TypedDict`

```
              flowchart TD
              griffe.PerStyleOptions[PerStyleOptions]

              

              click griffe.PerStyleOptions href "" "griffe.PerStyleOptions"
```

Per-style options for docstring parsing.

Attributes:

- **`google`** (`GoogleOptions`) – Options for Google-style docstrings.
- **`numpy`** (`NumpyOptions`) – Options for Numpy-style docstrings.
- **`sphinx`** (`SphinxOptions`) – Options for Sphinx-style docstrings.

### google

```
google: GoogleOptions
```

Options for Google-style docstrings.

### numpy

```
numpy: NumpyOptions
```

Options for Numpy-style docstrings.

### sphinx

```
sphinx: SphinxOptions
```

Options for Sphinx-style docstrings.

## **Advanced API**

## Parser

Bases: `str`, `Enum`

```
              flowchart TD
              griffe.Parser[Parser]

              

              click griffe.Parser href "" "griffe.Parser"
```

Enumeration of the different docstring parsers.

Attributes:

- **`auto`** – Infer docstring parser.
- **`google`** – Google-style docstrings parser.
- **`numpy`** – Numpydoc-style docstrings parser.
- **`sphinx`** – Sphinx-style docstrings parser.

### auto

```
auto = 'auto'
```

Infer docstring parser.

[Sponsors only](../../../../insiders/) — [Insiders 1.3.0](../../../../insiders/changelog/#1.3.0).

### google

```
google = 'google'
```

Google-style docstrings parser.

### numpy

```
numpy = 'numpy'
```

Numpydoc-style docstrings parser.

### sphinx

```
sphinx = 'sphinx'
```

Sphinx-style docstrings parser.

## parsers

```
parsers: dict[
    Parser, Callable[[Docstring], list[DocstringSection]]
] = {
    auto: parse_auto,
    google: parse_google,
    sphinx: parse_sphinx,
    numpy: parse_numpy,
}
```

## parse_docstring_annotation

```
parse_docstring_annotation(
    annotation: str,
    docstring: Docstring,
    log_level: LogLevel = error,
) -> str | Expr
```

Parse a string into a true name or expression that can be resolved later.

Parameters:

- ### **`annotation`**

  (`str`) – The annotation to parse.

- ### **`docstring`**

  (`Docstring`) – The docstring in which the annotation appears. The docstring's parent is accessed to bind a resolver to the resulting name/expression.

- ### **`log_level`**

  (`LogLevel`, default: `error` ) – Log level to use to log a message.

Returns:

- `str | Expr` – The string unchanged, or a new name or expression.

## docstring_warning

```
docstring_warning(
    docstring: Docstring,
    offset: int,
    message: str,
    log_level: LogLevel = warning,
) -> None
```

Log a warning when parsing a docstring.

This function logs a warning message by prefixing it with the filepath and line number.

Parameters:

- ### **`docstring`**

  (`Docstring`) – The docstring object.

- ### **`offset`**

  (`int`) – The offset in the docstring lines.

- ### **`message`**

  (`str`) – The message to log.

Returns:

- `None` – A function used to log parsing warnings if name was passed, else none.

## DocstringDetectionMethod

```
DocstringDetectionMethod = Literal[
    "heuristics", "max_sections"
]
```

The supported methods to infer docstring styles.

## infer_docstring_style

```
infer_docstring_style(
    docstring: Docstring,
    *,
    method: DocstringDetectionMethod = "heuristics",
    style_order: list[Parser]
    | list[DocstringStyle]
    | None = None,
    default: Parser | DocstringStyle | None = None,
    per_style_options: PerStyleOptions | None = None,
    **options: Any,
) -> tuple[Parser | None, list[DocstringSection] | None]
```

Infer the parser to use for the docstring.

[Sponsors only](../../../../insiders/) — [Insiders 1.3.0](../../../../insiders/changelog/#1.3.0).

The 'heuristics' method uses regular expressions. The 'max_sections' method parses the docstring with all parsers specified in `style_order` and returns the one who parsed the most sections.

If heuristics fail, the `default` parser is returned. If multiple parsers parsed the same number of sections, `style_order` is used to decide which one to return. The `default` parser is never used with the 'max_sections' method.

For non-Insiders versions, `default` is returned if specified, else the first parser in `style_order` is returned. If `style_order` is not specified, `None` is returned.

Additional options are parsed to the detected parser, if any.

Parameters:

- ### **`docstring`**

  (`Docstring`) – The docstring to parse.

- ### **`method`**

  (`DocstringDetectionMethod`, default: `'heuristics'` ) – The method to use to infer the parser.

- ### **`style_order`**

  (`list[Parser] | list[DocstringStyle] | None`, default: `None` ) – The order of the styles to try when inferring the parser.

- ### **`default`**

  (`Parser | DocstringStyle | None`, default: `None` ) – The default parser to use if the inference fails.

- ### **`per_style_options`**

  (`PerStyleOptions | None`, default: `None` ) – Additional parsing options per style.

- ### **`**options`**

  (`Any`, default: `{}` ) – Deprecated. Use per_style_options instead.

Returns:

- `tuple[Parser | None, list[DocstringSection] | None]` – The inferred parser, and optionally parsed sections (when method is 'max_sections').
