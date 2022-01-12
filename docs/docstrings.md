# Docstrings

## Section support

Section          | Google | Numpy | Sphinx
---------------- | ------ | ----- | ------
Attributes       | ✅     | ✅    | ✅
Deprecated       | ✅     | ✅[^1]| ❌
Examples         | ✅     | ✅    | ❌
Other Parameters | ✅     | ✅    | ❌
Parameters       | ✅     | ✅    | ✅
Raises           | ✅     | ✅    | ✅
Receives         | ✅     | ✅    | ❌
Returns          | ✅     | ✅    | ✅
Warns            | ✅     | ✅    | ❌
Yields           | ✅     | ✅    | ❌

[^1]: Support for a regular section instead of the RST directive specified in the [Numpydoc styleguide](https://numpydoc.readthedocs.io/en/latest/format.html#deprecation-warning).

## Getting annotations/defaults from parent

Section          | Google | Numpy | Sphinx
---------------- | ------ | ----- | ------
Attributes       | ✅     | ❌    | ❌
Deprecated       | /      | /     | /
Examples         | /      | /     | /
Other Parameters | ✅     | ✅    | ❌
Parameters       | ✅     | ✅    | ✅
Raises           | /      | /     | /
Receives         | ❌     | ❌    | ❌
Returns          | ✅     | ❌    | ✅
Warns            | /      | /     | /
Yields           | ✅     | ❌    | ❌

## Cross-references for annotations in docstrings

Section          | Google | Numpy | Sphinx
---------------- | ------ | ----- | ------
Attributes       | ✅     | ❌    | ❌
Deprecated       | /      | /     | /
Examples         | /      | /     | /
Other Parameters | ✅     | ❌    | ❌
Parameters       | ✅     | ❌    | ❌
Raises           | ✅     | ❌    | ❌
Receives         | ✅     | ❌    | ❌
Returns          | ✅     | ❌    | ❌
Warns            | ✅     | ❌    | ❌
Yields           | ✅     | ❌    | ❌
