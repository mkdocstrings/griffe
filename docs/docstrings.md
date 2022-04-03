# Docstrings

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

## Section support

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

## Getting annotations/defaults from parent

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

## Cross-references for annotations in docstrings

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

## Parsing options

Option                     | Google | Numpy | Sphinx
-------------------------- | ------ | ----- | ------
Ignore `__init__` summary  | ✅     | ✅    | [❌][issue-ignore-init-summary-sphinx]
Trim doctest flags         | ✅     | ✅    | [❌][issue-trim-doctest-flags-sphinx]

[issue-ignore-init-summary-sphinx]: https://github.com/mkdocstrings/griffe/issues/45
[issue-trim-doctest-flags-sphinx]: https://github.com/mkdocstrings/griffe/issues/49

