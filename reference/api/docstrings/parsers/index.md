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

Source code in `src/griffe/_internal/docstrings/parsers.py`

```
def parse(
    docstring: Docstring,
    parser: DocstringStyle | Parser | None,
    **options: Any,
) -> list[DocstringSection]:
    """Parse the docstring.

    Parameters:
        docstring: The docstring to parse.
        parser: The docstring parser to use. If None, return a single text section.
        **options: The options accepted by the parser.

    Returns:
        A list of docstring sections.
    """
    if parser:
        if not isinstance(parser, Parser):
            parser = Parser(parser)
        return parsers[parser](docstring, **options)
    return [DocstringSectionText(docstring.value)] if docstring.value else []
```

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

Source code in `src/griffe/_internal/docstrings/auto.py`

```
def parse_auto(
    docstring: Docstring,
    *,
    method: DocstringDetectionMethod = "heuristics",
    style_order: list[Parser] | list[DocstringStyle] | None = None,
    default: Parser | DocstringStyle | None = None,
    per_style_options: PerStyleOptions | None = None,
    # YORE: Bump 2: Remove line.
    **options: Any,
) -> list[DocstringSection]:
    """Parse a docstring by automatically detecting the style it uses.

    See [`infer_docstring_style`][griffe.infer_docstring_style] for more information
    on the available parameters.

    Parameters:
        docstring: The docstring to parse.
        method: The method to use to infer the parser.
        style_order: The order of the styles to try when inferring the parser.
        default: The default parser to use if the inference fails.
        per_style_options: Additional parsing options per style.
        **options: Deprecated. Use `per_style_options` instead.

    Returns:
        A list of docstring sections.
    """
    from griffe._internal.docstrings.parsers import parse  # noqa: PLC0415

    # YORE: Bump 2: Replace block with `per_style_options = per_style_options or {}`.
    if options:
        if per_style_options:
            raise ValueError("Cannot use both `options` and `per_style_options`.")
        warn("`**options` are deprecated. Use `per_style_options` instead.", DeprecationWarning, stacklevel=2)
        per_style_options = {"google": options, "numpy": options, "sphinx": options}  # type: ignore[assignment]
    elif not per_style_options:
        per_style_options = {}

    style, sections = infer_docstring_style(
        docstring,
        method=method,
        style_order=style_order,
        default=default,
        per_style_options=per_style_options,
    )
    if sections is None:
        return parse(docstring, style, **per_style_options.get(style, {}))  # type: ignore[arg-type,typeddict-item,union-attr]
    return sections
```

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

Source code in `src/griffe/_internal/docstrings/google.py`

````
def parse_google(
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
    # YORE: Bump 2: Remove line.
    **options: Any,
) -> list[DocstringSection]:
    """Parse a Google-style docstring.

    This function iterates on lines of a docstring to build sections.
    It then returns this list of sections.

    Parameters:
        docstring: The docstring to parse.
        ignore_init_summary: Whether to ignore the summary in `__init__` methods' docstrings.
        trim_doctest_flags: Whether to remove doctest flags from Python example blocks.
        returns_multiple_items: Whether to parse multiple items in `Yields` and `Returns` sections.
            When true, each item's continuation lines must be indented.
            When false (single item), no further indentation is required.
        returns_named_value: Whether to parse `Yields` and `Returns` section items as name and description, rather than type and description.
            When true, type must be wrapped in parentheses: `(int): Description.`. Names are optional: `name (int): Description.`.
            When false, parentheses are optional but the items cannot be named: `int: Description`.
        receives_multiple_items: Whether to parse multiple items in `Receives` sections.
            When true, each item's continuation lines must be indented.
            When false (single item), no further indentation is required.
        receives_named_value: Whether to parse `Receives` section items as name and description, rather than type and description.
            When true, type must be wrapped in parentheses: `(int): Description.`. Names are optional: `name (int): Description.`.
            When false, parentheses are optional but the items cannot be named: `int: Description`.
        returns_type_in_property_summary: Whether to parse the return type of properties
            at the beginning of their summary: `str: Summary of the property`.
        warn_unknown_params: Warn about documented parameters not appearing in the signature.
        warn_missing_types: Warn about missing types/annotations for parameters, return values, etc.
        warnings: Whether to log warnings at all.
        **options: Swallowing keyword arguments for backward-compatibility.

    Returns:
        A list of docstring sections.
    """
    sections: list[DocstringSection] = []
    current_section = []

    in_code_block = False
    lines = docstring.lines

    # YORE: Bump 2: Remove block.
    if options:
        warn("Passing additional options is deprecated, these options are ignored.", DeprecationWarning, stacklevel=2)

    options = {
        "ignore_init_summary": ignore_init_summary,
        "trim_doctest_flags": trim_doctest_flags,
        "returns_multiple_items": returns_multiple_items,
        "returns_named_value": returns_named_value,
        "returns_type_in_property_summary": returns_type_in_property_summary,
        "receives_multiple_items": receives_multiple_items,
        "receives_named_value": receives_named_value,
        "warn_unknown_params": warn_unknown_params,
        "warn_missing_types": warn_missing_types,
        "warnings": warnings,
    }

    ignore_summary = (
        options["ignore_init_summary"]
        and docstring.parent is not None
        and docstring.parent.name == "__init__"
        and docstring.parent.is_function
        and docstring.parent.parent is not None
        and docstring.parent.parent.is_class
    )

    offset = 2 if ignore_summary else 0

    while offset < len(lines):
        line_lower = lines[offset].lower()

        if in_code_block:
            if line_lower.lstrip(" ").startswith("```"):
                in_code_block = False
            current_section.append(lines[offset])

        elif line_lower.lstrip(" ").startswith("```"):
            in_code_block = True
            current_section.append(lines[offset])

        elif match := _RE_ADMONITION.match(lines[offset]):
            groups = match.groupdict()
            title = groups["title"]
            admonition_type = groups["type"]
            is_section = admonition_type.lower() in _section_kind

            has_previous_line = offset > 0
            blank_line_above = not has_previous_line or _is_empty_line(lines[offset - 1])
            has_next_line = offset < len(lines) - 1
            has_next_lines = offset < len(lines) - 2
            blank_line_below = has_next_line and _is_empty_line(lines[offset + 1])
            blank_lines_below = has_next_lines and _is_empty_line(lines[offset + 2])
            indented_line_below = has_next_line and not blank_line_below and lines[offset + 1].startswith(" ")
            indented_lines_below = has_next_lines and not blank_lines_below and lines[offset + 2].startswith(" ")
            if not (indented_line_below or indented_lines_below):
                # Do not warn when there are no contents,
                # this is most probably not a section or admonition.
                current_section.append(lines[offset])
                offset += 1
                continue
            reasons = []
            kind = "section" if is_section else "admonition"
            if (indented_line_below or indented_lines_below) and not blank_line_above:
                reasons.append(f"Missing blank line above {kind}")
            if indented_lines_below and blank_line_below:
                reasons.append(f"Extraneous blank line below {kind} title")
            if reasons:
                if warnings:
                    reasons_string = "; ".join(reasons)
                    docstring_warning(
                        docstring,
                        offset,
                        f"Possible {kind} skipped, reasons: {reasons_string}",
                        LogLevel.debug,
                    )
                current_section.append(lines[offset])
                offset += 1
                continue

            if is_section:
                if current_section:
                    if any(current_section):
                        sections.append(DocstringSectionText("\n".join(current_section).rstrip("\n")))
                    current_section = []
                reader = _section_reader[_section_kind[admonition_type.lower()]]
                section, offset = reader(docstring, offset=offset + 1, **options)  # type: ignore[operator]
                if section:
                    section.title = title
                    sections.append(section)

            else:
                contents, offset = _read_block(docstring, offset=offset + 1)
                if contents:
                    if current_section:
                        if any(current_section):
                            sections.append(DocstringSectionText("\n".join(current_section).rstrip("\n")))
                        current_section = []
                    if title is None:
                        title = admonition_type
                    admonition_type = admonition_type.lower().replace(" ", "-")
                    sections.append(DocstringSectionAdmonition(kind=admonition_type, text=contents, title=title))
                else:
                    with suppress(IndexError):
                        current_section.append(lines[offset])
        else:
            current_section.append(lines[offset])

        offset += 1

    if current_section and any(current_section):
        sections.append(DocstringSectionText("\n".join(current_section).rstrip("\n")))

    if (
        returns_type_in_property_summary
        and sections
        and docstring.parent
        and docstring.parent.is_attribute
        and "property" in docstring.parent.labels
    ):
        lines = sections[0].value.lstrip().split("\n")
        if ":" in lines[0]:
            annotation, line = lines[0].split(":", 1)
            lines = [line, *lines[1:]]
            sections[0].value = "\n".join(lines)
            sections.append(
                DocstringSectionReturns(
                    [DocstringReturn("", description="", annotation=parse_docstring_annotation(annotation, docstring))],
                ),
            )

    return sections
````

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

Source code in `src/griffe/_internal/docstrings/numpy.py`

````
def parse_numpy(
    docstring: Docstring,
    *,
    ignore_init_summary: bool = False,
    trim_doctest_flags: bool = True,
    warn_unknown_params: bool = True,
    warn_missing_types: bool = True,
    warnings: bool = True,
    # YORE: Bump 2: Remove line.
    **options: Any,
) -> list[DocstringSection]:
    """Parse a Numpydoc-style docstring.

    This function iterates on lines of a docstring to build sections.
    It then returns this list of sections.

    Parameters:
        docstring: The docstring to parse.
        ignore_init_summary: Whether to ignore the summary in `__init__` methods' docstrings.
        trim_doctest_flags: Whether to remove doctest flags from Python example blocks.
        warn_unknown_params: Warn about documented parameters not appearing in the signature.
        warn_missing_types: Warn about missing types/annotations for parameters, return values, etc.
        warnings: Whether to log warnings at all.
        **options: Swallowing keyword arguments for backward-compatibility.

    Returns:
        A list of docstring sections.
    """
    sections: list[DocstringSection] = []
    current_section = []
    admonition_title = ""

    in_code_block = False
    lines = docstring.lines

    # YORE: Bump 2: Remove block.
    if options:
        warn("Passing additional options is deprecated, these options are ignored.", DeprecationWarning, stacklevel=2)

    options = {
        "trim_doctest_flags": trim_doctest_flags,
        "ignore_init_summary": ignore_init_summary,
        "warn_unknown_params": warn_unknown_params,
        "warn_missing_types": warn_missing_types,
        "warnings": warnings,
    }

    ignore_summary = (
        options["ignore_init_summary"]
        and docstring.parent is not None
        and docstring.parent.name == "__init__"
        and docstring.parent.is_function
        and docstring.parent.parent is not None
        and docstring.parent.parent.is_class
    )

    offset = 2 if ignore_summary else 0

    while offset < len(lines):
        line_lower = lines[offset].lower()

        # Code blocks can contain dash lines that we must not interpret.
        if in_code_block:
            # End of code block.
            if line_lower.lstrip(" ").startswith("```"):
                in_code_block = False
            # Lines in code block must not be interpreted in any way.
            current_section.append(lines[offset])

        # Start of code block.
        elif line_lower.lstrip(" ").startswith("```"):
            in_code_block = True
            current_section.append(lines[offset])

        # Dash lines after empty lines lose their meaning.
        elif _is_empty_line(lines[offset]):
            current_section.append("")

        # End of the docstring, wrap up.
        elif offset == len(lines) - 1:
            current_section.append(lines[offset])
            _append_section(sections, current_section, admonition_title)
            admonition_title = ""
            current_section = []

        # Dash line after regular, non-empty line.
        elif _is_dash_line(lines[offset + 1]):
            # Finish reading current section.
            _append_section(sections, current_section, admonition_title)
            current_section = []

            # Start parsing new (known) section.
            if line_lower in _section_kind:
                admonition_title = ""
                reader = _section_reader[_section_kind[line_lower]]
                section, offset = reader(docstring, offset=offset + 2, **options)  # type: ignore[operator]
                if section:
                    sections.append(section)

            # Start parsing admonition.
            else:
                admonition_title = lines[offset]
                offset += 1  # Skip next dash line.

        # Regular line.
        else:
            current_section.append(lines[offset])

        offset += 1

    # Finish current section.
    _append_section(sections, current_section, admonition_title)

    return sections
````

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

Source code in `src/griffe/_internal/docstrings/sphinx.py`

```
def parse_sphinx(
    docstring: Docstring,
    *,
    warn_unknown_params: bool = True,
    warnings: bool = True,
    # YORE: Bump 2: Remove line.
    **options: Any,
) -> list[DocstringSection]:
    """Parse a Sphinx-style docstring.

    Parameters:
        docstring: The docstring to parse.
        warn_unknown_params: Warn about documented parameters not appearing in the signature.
        warnings: Whether to log warnings at all.
        **options: Swallowing keyword arguments for backward-compatibility.

    Returns:
        A list of docstring sections.
    """
    parsed_values = _ParsedValues()

    # YORE: Bump 2: Remove block.
    if options:
        warn("Passing additional options is deprecated, these options are ignored.", DeprecationWarning, stacklevel=2)

    options = {
        "warn_unknown_params": warn_unknown_params,
        "warnings": warnings,
    }

    lines = docstring.lines
    curr_line_index = 0

    while curr_line_index < len(lines):
        line = lines[curr_line_index]
        for field_type in _field_types:
            if field_type.matches(line):
                # https://github.com/python/mypy/issues/5485
                curr_line_index = field_type.reader(docstring, curr_line_index, parsed_values, **options)
                break
        else:
            parsed_values.description.append(line)

        curr_line_index += 1

    return _parsed_values_to_sections(parsed_values)
```

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

```
GoogleOptions(
    *,
    ignore_init_summary: bool = ...,
    trim_doctest_flags: bool = ...,
    returns_multiple_items: bool = ...,
    returns_named_value: bool = ...,
    returns_type_in_property_summary: bool = ...,
    receives_multiple_items: bool = ...,
    receives_named_value: bool = ...,
    warn_unknown_params: bool = ...,
    warn_missing_types: bool = ...,
    warnings: bool = ...,
)
```

Bases: `TypedDict`

```
              flowchart TD
              griffe.GoogleOptions[GoogleOptions]

              

              click griffe.GoogleOptions href "" "griffe.GoogleOptions"
```

Options for parsing Google-style docstrings.

Parameters:

- ### **`ignore_init_summary`**

  (`bool`, default: `...` ) – Whether to ignore the summary in __init__ methods' docstrings.

- ### **`trim_doctest_flags`**

  (`bool`, default: `...` ) – Whether to remove doctest flags from Python example blocks.

- ### **`returns_multiple_items`**

  (`bool`, default: `...` ) – Whether to parse multiple items in Yields and Returns sections.

- ### **`returns_named_value`**

  (`bool`, default: `...` ) – Whether to parse Yields and Returns section items as name and description, rather than type and description.

- ### **`returns_type_in_property_summary`**

  (`bool`, default: `...` ) – Whether to parse the return type of properties at the beginning of their summary.

- ### **`receives_multiple_items`**

  (`bool`, default: `...` ) – Whether to parse multiple items in Receives sections.

- ### **`receives_named_value`**

  (`bool`, default: `...` ) – Whether to parse Receives section items as name and description, rather than type and description.

- ### **`warn_unknown_params`**

  (`bool`, default: `...` ) – Whether to warn about unknown parameters.

- ### **`warn_missing_types`**

  (`bool`, default: `...` ) – Whether to warn about missing types/annotations for parameters, return values, etc.

- ### **`warnings`**

  (`bool`, default: `...` ) – Whether to issue warnings for parsing issues.

## NumpyOptions

```
NumpyOptions(
    *,
    ignore_init_summary: bool = ...,
    trim_doctest_flags: bool = ...,
    warn_unknown_params: bool = ...,
    warn_missing_types: bool = ...,
    warnings: bool = ...,
)
```

Bases: `TypedDict`

```
              flowchart TD
              griffe.NumpyOptions[NumpyOptions]

              

              click griffe.NumpyOptions href "" "griffe.NumpyOptions"
```

Options for parsing Numpydoc-style docstrings.

Parameters:

- ### **`ignore_init_summary`**

  (`bool`, default: `...` ) – Whether to ignore the summary in __init__ methods' docstrings.

- ### **`trim_doctest_flags`**

  (`bool`, default: `...` ) – Whether to remove doctest flags from Python example blocks.

- ### **`warn_unknown_params`**

  (`bool`, default: `...` ) – Whether to warn about unknown parameters.

- ### **`warn_missing_types`**

  (`bool`, default: `...` ) – Whether to warn about missing types/annotations for parameters, return values, etc.

- ### **`warnings`**

  (`bool`, default: `...` ) – Whether to issue warnings for parsing issues.

## SphinxOptions

```
SphinxOptions(
    *, warn_unknown_params: bool = ..., warnings: bool = ...
)
```

Bases: `TypedDict`

```
              flowchart TD
              griffe.SphinxOptions[SphinxOptions]

              

              click griffe.SphinxOptions href "" "griffe.SphinxOptions"
```

Options for parsing Sphinx-style docstrings.

Parameters:

- ### **`warn_unknown_params`**

  (`bool`, default: `...` ) – Whether to warn about unknown parameters.

- ### **`warnings`**

  (`bool`, default: `...` ) – Whether to issue warnings for parsing issues.

## AutoOptions

```
AutoOptions(
    *,
    method: DocstringDetectionMethod = ...,
    style_order: list[Parser]
    | list[DocstringStyle]
    | None = ...,
    default: Parser | DocstringStyle | None = ...,
    per_style_options: PerStyleOptions | None = ...,
)
```

Bases: `TypedDict`

```
              flowchart TD
              griffe.AutoOptions[AutoOptions]

              

              click griffe.AutoOptions href "" "griffe.AutoOptions"
```

Options for Auto-style docstrings.

Parameters:

- ### **`method`**

  (`DocstringDetectionMethod`, default: `...` ) – The method to use to infer the parser.

- ### **`style_order`**

  (`list[Parser] | list[DocstringStyle] | None`, default: `...` ) – The order of styles to try when inferring the parser.

- ### **`default`**

  (`Parser | DocstringStyle | None`, default: `...` ) – The default parser to use if the inference fails.

- ### **`per_style_options`**

  (`PerStyleOptions | None`, default: `...` ) – Additional parsing options per style.

## PerStyleOptions

```
PerStyleOptions(
    *,
    google: GoogleOptions = ...,
    numpy: NumpyOptions = ...,
    sphinx: SphinxOptions = ...,
)
```

Bases: `TypedDict`

```
              flowchart TD
              griffe.PerStyleOptions[PerStyleOptions]

              

              click griffe.PerStyleOptions href "" "griffe.PerStyleOptions"
```

Per-style options for docstring parsing.

Parameters:

- ### **`google`**

  (`GoogleOptions`, default: `...` ) – Options for Google-style docstrings.

- ### **`numpy`**

  (`NumpyOptions`, default: `...` ) – Options for Numpy-style docstrings.

- ### **`sphinx`**

  (`SphinxOptions`, default: `...` ) – Options for Sphinx-style docstrings.

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

Source code in `src/griffe/_internal/docstrings/utils.py`

```
def parse_docstring_annotation(
    annotation: str,
    docstring: Docstring,
    log_level: LogLevel = LogLevel.error,
) -> str | Expr:
    """Parse a string into a true name or expression that can be resolved later.

    Parameters:
        annotation: The annotation to parse.
        docstring: The docstring in which the annotation appears.
            The docstring's parent is accessed to bind a resolver to the resulting name/expression.
        log_level: Log level to use to log a message.

    Returns:
        The string unchanged, or a new name or expression.
    """
    with suppress(
        AttributeError,  # Docstring has no parent that can be used to resolve names.
        SyntaxError,  # Annotation contains syntax errors.
    ):
        code = compile(annotation, mode="eval", filename="", flags=PyCF_ONLY_AST, optimize=2)
        if code.body:  # type: ignore[attr-defined]
            name_or_expr = safe_get_annotation(
                code.body,  # type: ignore[attr-defined]
                parent=docstring.parent,  # type: ignore[arg-type]
                log_level=log_level,
            )
            return name_or_expr or annotation
    return annotation
```

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

Source code in `src/griffe/_internal/docstrings/utils.py`

```
def docstring_warning(
    docstring: Docstring,
    offset: int,
    message: str,
    log_level: LogLevel = LogLevel.warning,
) -> None:
    """Log a warning when parsing a docstring.

    This function logs a warning message by prefixing it with the filepath and line number.

    Parameters:
        docstring: The docstring object.
        offset: The offset in the docstring lines.
        message: The message to log.

    Returns:
        A function used to log parsing warnings if `name` was passed, else none.
    """

    def warn(docstring: Docstring, offset: int, message: str, log_level: LogLevel = LogLevel.warning) -> None:
        try:
            prefix = docstring.parent.relative_filepath  # type: ignore[union-attr]
        except (AttributeError, ValueError):
            prefix = "<module>"
        except BuiltinModuleError:
            prefix = f"<module: {docstring.parent.module.name}>"  # type: ignore[union-attr]
        log = getattr(logger, log_level.value)
        log(f"{prefix}:{(docstring.lineno or 0) + offset}: {message}")

    warn(docstring, offset, message, log_level)
```

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

The 'heuristics' method uses regular expressions. The 'max_sections' method parses the docstring with all parsers specified in `style_order` and returns the one who parsed the most sections.

If heuristics fail, the `default` parser is returned. If multiple parsers parsed the same number of sections, `style_order` is used to decide which one to return. The `default` parser is never used with the 'max_sections' method.

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

Source code in `src/griffe/_internal/docstrings/auto.py`

```
def infer_docstring_style(
    docstring: Docstring,
    *,
    method: DocstringDetectionMethod = "heuristics",
    style_order: list[Parser] | list[DocstringStyle] | None = None,
    default: Parser | DocstringStyle | None = None,
    per_style_options: PerStyleOptions | None = None,
    # YORE: Bump 2: Remove line.
    **options: Any,
) -> tuple[Parser | None, list[DocstringSection] | None]:
    """Infer the parser to use for the docstring.

    The 'heuristics' method uses regular expressions. The 'max_sections' method
    parses the docstring with all parsers specified in `style_order` and returns
    the one who parsed the most sections.

    If heuristics fail, the `default` parser is returned. If multiple parsers
    parsed the same number of sections, `style_order` is used to decide which
    one to return. The `default` parser is never used with the 'max_sections' method.

    Additional options are parsed to the detected parser, if any.

    Parameters:
        docstring: The docstring to parse.
        method: The method to use to infer the parser.
        style_order: The order of the styles to try when inferring the parser.
        default: The default parser to use if the inference fails.
        per_style_options: Additional parsing options per style.
        **options: Deprecated. Use `per_style_options` instead.

    Returns:
        The inferred parser, and optionally parsed sections (when method is 'max_sections').
    """
    from griffe._internal.docstrings.parsers import parsers  # noqa: PLC0415

    # YORE: Bump 2: Replace block with `per_style_options = per_style_options or {}`.
    if options:
        if per_style_options:
            raise ValueError("Cannot use both `options` and `per_style_options`.")
        warn("`**options` is deprecated. Use `per_style_options` instead.", DeprecationWarning, stacklevel=2)
        per_style_options = {"google": options, "numpy": options, "sphinx": options}  # type: ignore[assignment]
    elif not per_style_options:
        per_style_options = {}

    style_order = [Parser(style) if isinstance(style, str) else style for style in style_order or _default_style_order]

    if method == "heuristics":
        for style in style_order:
            pattern, replacements = _patterns[style]
            patterns = [
                re.compile(pattern.format(replacement), re.IGNORECASE | re.MULTILINE) for replacement in replacements
            ]
            if any(pattern.search(docstring.value) for pattern in patterns):
                return style, None
        return default if default is None or isinstance(default, Parser) else Parser(default), None

    if method == "max_sections":
        style_sections = {}
        for style in style_order:
            style_sections[style] = parsers[style](docstring, **per_style_options.get(style, {}))  # type: ignore[arg-type,union-attr]
        style_lengths = {style: len(section) for style, section in style_sections.items()}
        max_sections = max(style_lengths.values())
        for style in style_order:
            if style_lengths[style] == max_sections:
                return style, style_sections[style]

    raise ValueError(f"Invalid method '{method}'.")
```
