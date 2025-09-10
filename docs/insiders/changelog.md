# Changelog

## Griffe Insiders

[](){#insiders-1.3.1}
### 1.3.1 <small>December 31, 2024</small> { id="1.3.1" }

- Accept per-style docstring options instead of generic options when docstring style is set to `auto`.
    In MkDocs, apply the following change:

    ```diff
     docstring_style: auto
     docstring_options:
    -  ignore_init_summary: true
    +  per_style_options:
    +    google:
    +      ignore_init_summary: true
    ```

[](){#insiders-1.3.0}

### 1.3.0 <small>August 09, 2024</small> { id="1.3.0" }

- [Automatic docstring style detection](../reference/docstrings.md#auto-style)

[](){#insiders-1.2.0}

### 1.2.0 <small>March 11, 2024</small> { id="1.2.0" }

- [Expressions modernization](../guide/users/navigating.md#modernization)

[](){#insiders-1.1.0}

### 1.1.0 <small>March 02, 2024</small> { id="1.1.0" }

- Check API of Python packages by [downloading them from PyPI](../guide/users/checking.md#using-pypi)

[](){#insiders-1.0.0}

### 1.0.0 <small>January 16, 2024</small> { id="1.0.0" }

- Add [Markdown][markdown] and [GitHub][github] output formats to the check command
