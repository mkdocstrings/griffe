# API checks

## find_breaking_changes

```
find_breaking_changes(
    old_obj: Object | Alias, new_obj: Object | Alias
) -> Iterator[Breakage]
```

Find breaking changes between two versions of the same API.

The function will iterate recursively on all objects and yield breaking changes with detailed information.

Parameters:

- ### **`old_obj`**

  (`Object | Alias`) – The old version of an object.

- ### **`new_obj`**

  (`Object | Alias`) – The new version of an object.

Yields:

- `Breakage` – Breaking changes.

Examples:

```
>>> import sys, griffe
>>> new = griffe.load("pkg")
>>> old = griffe.load_git("pkg", "1.2.3")
>>> for breakage in griffe.find_breaking_changes(old, new)
...     print(breakage.explain(style=style), file=sys.stderr)
```

Source code in `src/griffe/_internal/diff.py`

```
def find_breaking_changes(
    old_obj: Object | Alias,
    new_obj: Object | Alias,
) -> Iterator[Breakage]:
    """Find breaking changes between two versions of the same API.

    The function will iterate recursively on all objects
    and yield breaking changes with detailed information.

    Parameters:
        old_obj: The old version of an object.
        new_obj: The new version of an object.

    Yields:
        Breaking changes.

    Examples:
        >>> import sys, griffe
        >>> new = griffe.load("pkg")
        >>> old = griffe.load_git("pkg", "1.2.3")
        >>> for breakage in griffe.find_breaking_changes(old, new)
        ...     print(breakage.explain(style=style), file=sys.stderr)
    """
    yield from _member_incompatibilities(old_obj, new_obj)
```

## ExplanationStyle

Bases: `str`, `Enum`

```
              flowchart TD
              griffe.ExplanationStyle[ExplanationStyle]

              

              click griffe.ExplanationStyle href "" "griffe.ExplanationStyle"
```

Enumeration of the possible styles for explanations.

Attributes:

- **`GITHUB`** – Explanation as GitHub workflow commands warnings, adapted to CI.
- **`MARKDOWN`** – Explanations in Markdown, adapted to changelogs.
- **`ONE_LINE`** – Explanations on one-line.
- **`VERBOSE`** – Explanations on multiple lines.

### GITHUB

```
GITHUB = 'github'
```

Explanation as GitHub workflow commands warnings, adapted to CI.

### MARKDOWN

```
MARKDOWN = 'markdown'
```

Explanations in Markdown, adapted to changelogs.

### ONE_LINE

```
ONE_LINE = 'oneline'
```

Explanations on one-line.

### VERBOSE

```
VERBOSE = 'verbose'
```

Explanations on multiple lines.

## Breakage

```
Breakage(
    obj: Object,
    old_value: Any,
    new_value: Any,
    details: str = "",
)
```

Breakages can explain what broke from a version to another.

Parameters:

- ### **`obj`**

  (`Object`) – The object related to the breakage.

- ### **`old_value`**

  (`Any`) – The old value.

- ### **`new_value`**

  (`Any`) – The new, incompatible value.

- ### **`details`**

  (`str`, default: `''` ) – Some details about the breakage.

Methods:

- **`as_dict`** – Return this object's data as a dictionary.
- **`explain`** – Explain the breakage by showing old and new value.

Attributes:

- **`details`** – Some details about the breakage.
- **`kind`** (`BreakageKind`) – The kind of breakage.
- **`new_value`** – The new, incompatible value.
- **`obj`** – The object related to the breakage.
- **`old_value`** – The old value.

Source code in `src/griffe/_internal/diff.py`

```
def __init__(self, obj: Object, old_value: Any, new_value: Any, details: str = "") -> None:
    """Initialize the breakage.

    Parameters:
        obj: The object related to the breakage.
        old_value: The old value.
        new_value: The new, incompatible value.
        details: Some details about the breakage.
    """
    self.obj = obj
    """The object related to the breakage."""
    self.old_value = old_value
    """The old value."""
    self.new_value = new_value
    """The new, incompatible value."""
    self.details = details
    """Some details about the breakage."""
```

### details

```
details = details
```

Some details about the breakage.

### kind

```
kind: BreakageKind
```

The kind of breakage.

### new_value

```
new_value = new_value
```

The new, incompatible value.

### obj

```
obj = obj
```

The object related to the breakage.

### old_value

```
old_value = old_value
```

The old value.

### as_dict

```
as_dict(
    *, full: bool = False, **kwargs: Any
) -> dict[str, Any]
```

Return this object's data as a dictionary.

Parameters:

- #### **`full`**

  (`bool`, default: `False` ) – Whether to return full info, or just base info.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/diff.py`

```
def as_dict(self, *, full: bool = False, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
    """Return this object's data as a dictionary.

    Parameters:
        full: Whether to return full info, or just base info.
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    return {
        "kind": self.kind,
        "object_path": self.obj.path,
        "old_value": self.old_value,
        "new_value": self.new_value,
    }
```

### explain

```
explain(style: ExplanationStyle = ONE_LINE) -> str
```

Explain the breakage by showing old and new value.

Parameters:

- #### **`style`**

  (`ExplanationStyle`, default: `ONE_LINE` ) – The explanation style to use.

Returns:

- `str` – An explanation.

Source code in `src/griffe/_internal/diff.py`

```
def explain(self, style: ExplanationStyle = ExplanationStyle.ONE_LINE) -> str:
    """Explain the breakage by showing old and new value.

    Parameters:
        style: The explanation style to use.

    Returns:
        An explanation.
    """
    return getattr(self, f"_explain_{style.value}")()
```

## BreakageKind

Bases: `str`, `Enum`

```
              flowchart TD
              griffe.BreakageKind[BreakageKind]

              

              click griffe.BreakageKind href "" "griffe.BreakageKind"
```

Enumeration of the possible API breakages.

Attributes:

- **`ATTRIBUTE_CHANGED_TYPE`** – Attribute types are incompatible
- **`ATTRIBUTE_CHANGED_VALUE`** – Attribute value was changed
- **`CLASS_REMOVED_BASE`** – Base class was removed
- **`OBJECT_CHANGED_KIND`** – Public object points to a different kind of object
- **`OBJECT_REMOVED`** – Public object was removed
- **`PARAMETER_ADDED_REQUIRED`** – Parameter was added as required
- **`PARAMETER_CHANGED_DEFAULT`** – Parameter default was changed
- **`PARAMETER_CHANGED_KIND`** – Parameter kind was changed
- **`PARAMETER_CHANGED_REQUIRED`** – Parameter is now required
- **`PARAMETER_MOVED`** – Positional parameter was moved
- **`PARAMETER_REMOVED`** – Parameter was removed
- **`RETURN_CHANGED_TYPE`** – Return types are incompatible

### ATTRIBUTE_CHANGED_TYPE

```
ATTRIBUTE_CHANGED_TYPE = 'Attribute types are incompatible'
```

Attribute types are incompatible

### ATTRIBUTE_CHANGED_VALUE

```
ATTRIBUTE_CHANGED_VALUE = 'Attribute value was changed'
```

Attribute value was changed

### CLASS_REMOVED_BASE

```
CLASS_REMOVED_BASE = 'Base class was removed'
```

Base class was removed

### OBJECT_CHANGED_KIND

```
OBJECT_CHANGED_KIND = (
    "Public object points to a different kind of object"
)
```

Public object points to a different kind of object

### OBJECT_REMOVED

```
OBJECT_REMOVED = 'Public object was removed'
```

Public object was removed

### PARAMETER_ADDED_REQUIRED

```
PARAMETER_ADDED_REQUIRED = "Parameter was added as required"
```

Parameter was added as required

### PARAMETER_CHANGED_DEFAULT

```
PARAMETER_CHANGED_DEFAULT = 'Parameter default was changed'
```

Parameter default was changed

### PARAMETER_CHANGED_KIND

```
PARAMETER_CHANGED_KIND = 'Parameter kind was changed'
```

Parameter kind was changed

### PARAMETER_CHANGED_REQUIRED

```
PARAMETER_CHANGED_REQUIRED = 'Parameter is now required'
```

Parameter is now required

### PARAMETER_MOVED

```
PARAMETER_MOVED = 'Positional parameter was moved'
```

Positional parameter was moved

### PARAMETER_REMOVED

```
PARAMETER_REMOVED = 'Parameter was removed'
```

Parameter was removed

### RETURN_CHANGED_TYPE

```
RETURN_CHANGED_TYPE = 'Return types are incompatible'
```

Return types are incompatible

## AttributeChangedTypeBreakage

```
AttributeChangedTypeBreakage(
    obj: Object,
    old_value: Any,
    new_value: Any,
    details: str = "",
)
```

Bases: `Breakage`

```
              flowchart TD
              griffe.AttributeChangedTypeBreakage[AttributeChangedTypeBreakage]
              griffe._internal.diff.Breakage[Breakage]

                              griffe._internal.diff.Breakage --> griffe.AttributeChangedTypeBreakage
                


              click griffe.AttributeChangedTypeBreakage href "" "griffe.AttributeChangedTypeBreakage"
              click griffe._internal.diff.Breakage href "" "griffe._internal.diff.Breakage"
```

Specific breakage class for attributes whose type changed.

Parameters:

- ### **`obj`**

  (`Object`) – The object related to the breakage.

- ### **`old_value`**

  (`Any`) – The old value.

- ### **`new_value`**

  (`Any`) – The new, incompatible value.

- ### **`details`**

  (`str`, default: `''` ) – Some details about the breakage.

Methods:

- **`as_dict`** – Return this object's data as a dictionary.
- **`explain`** – Explain the breakage by showing old and new value.

Attributes:

- **`details`** – Some details about the breakage.
- **`kind`** (`BreakageKind`) – The kind of breakage.
- **`new_value`** – The new, incompatible value.
- **`obj`** – The object related to the breakage.
- **`old_value`** – The old value.

Source code in `src/griffe/_internal/diff.py`

```
def __init__(self, obj: Object, old_value: Any, new_value: Any, details: str = "") -> None:
    """Initialize the breakage.

    Parameters:
        obj: The object related to the breakage.
        old_value: The old value.
        new_value: The new, incompatible value.
        details: Some details about the breakage.
    """
    self.obj = obj
    """The object related to the breakage."""
    self.old_value = old_value
    """The old value."""
    self.new_value = new_value
    """The new, incompatible value."""
    self.details = details
    """Some details about the breakage."""
```

### details

```
details = details
```

Some details about the breakage.

### kind

```
kind: BreakageKind = ATTRIBUTE_CHANGED_TYPE
```

The kind of breakage.

### new_value

```
new_value = new_value
```

The new, incompatible value.

### obj

```
obj = obj
```

The object related to the breakage.

### old_value

```
old_value = old_value
```

The old value.

### as_dict

```
as_dict(
    *, full: bool = False, **kwargs: Any
) -> dict[str, Any]
```

Return this object's data as a dictionary.

Parameters:

- #### **`full`**

  (`bool`, default: `False` ) – Whether to return full info, or just base info.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/diff.py`

```
def as_dict(self, *, full: bool = False, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
    """Return this object's data as a dictionary.

    Parameters:
        full: Whether to return full info, or just base info.
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    return {
        "kind": self.kind,
        "object_path": self.obj.path,
        "old_value": self.old_value,
        "new_value": self.new_value,
    }
```

### explain

```
explain(style: ExplanationStyle = ONE_LINE) -> str
```

Explain the breakage by showing old and new value.

Parameters:

- #### **`style`**

  (`ExplanationStyle`, default: `ONE_LINE` ) – The explanation style to use.

Returns:

- `str` – An explanation.

Source code in `src/griffe/_internal/diff.py`

```
def explain(self, style: ExplanationStyle = ExplanationStyle.ONE_LINE) -> str:
    """Explain the breakage by showing old and new value.

    Parameters:
        style: The explanation style to use.

    Returns:
        An explanation.
    """
    return getattr(self, f"_explain_{style.value}")()
```

## AttributeChangedValueBreakage

```
AttributeChangedValueBreakage(
    obj: Object,
    old_value: Any,
    new_value: Any,
    details: str = "",
)
```

Bases: `Breakage`

```
              flowchart TD
              griffe.AttributeChangedValueBreakage[AttributeChangedValueBreakage]
              griffe._internal.diff.Breakage[Breakage]

                              griffe._internal.diff.Breakage --> griffe.AttributeChangedValueBreakage
                


              click griffe.AttributeChangedValueBreakage href "" "griffe.AttributeChangedValueBreakage"
              click griffe._internal.diff.Breakage href "" "griffe._internal.diff.Breakage"
```

Specific breakage class for attributes whose value changed.

Parameters:

- ### **`obj`**

  (`Object`) – The object related to the breakage.

- ### **`old_value`**

  (`Any`) – The old value.

- ### **`new_value`**

  (`Any`) – The new, incompatible value.

- ### **`details`**

  (`str`, default: `''` ) – Some details about the breakage.

Methods:

- **`as_dict`** – Return this object's data as a dictionary.
- **`explain`** – Explain the breakage by showing old and new value.

Attributes:

- **`details`** – Some details about the breakage.
- **`kind`** (`BreakageKind`) – The kind of breakage.
- **`new_value`** – The new, incompatible value.
- **`obj`** – The object related to the breakage.
- **`old_value`** – The old value.

Source code in `src/griffe/_internal/diff.py`

```
def __init__(self, obj: Object, old_value: Any, new_value: Any, details: str = "") -> None:
    """Initialize the breakage.

    Parameters:
        obj: The object related to the breakage.
        old_value: The old value.
        new_value: The new, incompatible value.
        details: Some details about the breakage.
    """
    self.obj = obj
    """The object related to the breakage."""
    self.old_value = old_value
    """The old value."""
    self.new_value = new_value
    """The new, incompatible value."""
    self.details = details
    """Some details about the breakage."""
```

### details

```
details = details
```

Some details about the breakage.

### kind

```
kind: BreakageKind = ATTRIBUTE_CHANGED_VALUE
```

The kind of breakage.

### new_value

```
new_value = new_value
```

The new, incompatible value.

### obj

```
obj = obj
```

The object related to the breakage.

### old_value

```
old_value = old_value
```

The old value.

### as_dict

```
as_dict(
    *, full: bool = False, **kwargs: Any
) -> dict[str, Any]
```

Return this object's data as a dictionary.

Parameters:

- #### **`full`**

  (`bool`, default: `False` ) – Whether to return full info, or just base info.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/diff.py`

```
def as_dict(self, *, full: bool = False, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
    """Return this object's data as a dictionary.

    Parameters:
        full: Whether to return full info, or just base info.
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    return {
        "kind": self.kind,
        "object_path": self.obj.path,
        "old_value": self.old_value,
        "new_value": self.new_value,
    }
```

### explain

```
explain(style: ExplanationStyle = ONE_LINE) -> str
```

Explain the breakage by showing old and new value.

Parameters:

- #### **`style`**

  (`ExplanationStyle`, default: `ONE_LINE` ) – The explanation style to use.

Returns:

- `str` – An explanation.

Source code in `src/griffe/_internal/diff.py`

```
def explain(self, style: ExplanationStyle = ExplanationStyle.ONE_LINE) -> str:
    """Explain the breakage by showing old and new value.

    Parameters:
        style: The explanation style to use.

    Returns:
        An explanation.
    """
    return getattr(self, f"_explain_{style.value}")()
```

## ClassRemovedBaseBreakage

```
ClassRemovedBaseBreakage(
    obj: Object,
    old_value: Any,
    new_value: Any,
    details: str = "",
)
```

Bases: `Breakage`

```
              flowchart TD
              griffe.ClassRemovedBaseBreakage[ClassRemovedBaseBreakage]
              griffe._internal.diff.Breakage[Breakage]

                              griffe._internal.diff.Breakage --> griffe.ClassRemovedBaseBreakage
                


              click griffe.ClassRemovedBaseBreakage href "" "griffe.ClassRemovedBaseBreakage"
              click griffe._internal.diff.Breakage href "" "griffe._internal.diff.Breakage"
```

Specific breakage class for removed base classes.

Parameters:

- ### **`obj`**

  (`Object`) – The object related to the breakage.

- ### **`old_value`**

  (`Any`) – The old value.

- ### **`new_value`**

  (`Any`) – The new, incompatible value.

- ### **`details`**

  (`str`, default: `''` ) – Some details about the breakage.

Methods:

- **`as_dict`** – Return this object's data as a dictionary.
- **`explain`** – Explain the breakage by showing old and new value.

Attributes:

- **`details`** – Some details about the breakage.
- **`kind`** (`BreakageKind`) – The kind of breakage.
- **`new_value`** – The new, incompatible value.
- **`obj`** – The object related to the breakage.
- **`old_value`** – The old value.

Source code in `src/griffe/_internal/diff.py`

```
def __init__(self, obj: Object, old_value: Any, new_value: Any, details: str = "") -> None:
    """Initialize the breakage.

    Parameters:
        obj: The object related to the breakage.
        old_value: The old value.
        new_value: The new, incompatible value.
        details: Some details about the breakage.
    """
    self.obj = obj
    """The object related to the breakage."""
    self.old_value = old_value
    """The old value."""
    self.new_value = new_value
    """The new, incompatible value."""
    self.details = details
    """Some details about the breakage."""
```

### details

```
details = details
```

Some details about the breakage.

### kind

```
kind: BreakageKind = CLASS_REMOVED_BASE
```

The kind of breakage.

### new_value

```
new_value = new_value
```

The new, incompatible value.

### obj

```
obj = obj
```

The object related to the breakage.

### old_value

```
old_value = old_value
```

The old value.

### as_dict

```
as_dict(
    *, full: bool = False, **kwargs: Any
) -> dict[str, Any]
```

Return this object's data as a dictionary.

Parameters:

- #### **`full`**

  (`bool`, default: `False` ) – Whether to return full info, or just base info.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/diff.py`

```
def as_dict(self, *, full: bool = False, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
    """Return this object's data as a dictionary.

    Parameters:
        full: Whether to return full info, or just base info.
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    return {
        "kind": self.kind,
        "object_path": self.obj.path,
        "old_value": self.old_value,
        "new_value": self.new_value,
    }
```

### explain

```
explain(style: ExplanationStyle = ONE_LINE) -> str
```

Explain the breakage by showing old and new value.

Parameters:

- #### **`style`**

  (`ExplanationStyle`, default: `ONE_LINE` ) – The explanation style to use.

Returns:

- `str` – An explanation.

Source code in `src/griffe/_internal/diff.py`

```
def explain(self, style: ExplanationStyle = ExplanationStyle.ONE_LINE) -> str:
    """Explain the breakage by showing old and new value.

    Parameters:
        style: The explanation style to use.

    Returns:
        An explanation.
    """
    return getattr(self, f"_explain_{style.value}")()
```

## ObjectChangedKindBreakage

```
ObjectChangedKindBreakage(
    obj: Object,
    old_value: Any,
    new_value: Any,
    details: str = "",
)
```

Bases: `Breakage`

```
              flowchart TD
              griffe.ObjectChangedKindBreakage[ObjectChangedKindBreakage]
              griffe._internal.diff.Breakage[Breakage]

                              griffe._internal.diff.Breakage --> griffe.ObjectChangedKindBreakage
                


              click griffe.ObjectChangedKindBreakage href "" "griffe.ObjectChangedKindBreakage"
              click griffe._internal.diff.Breakage href "" "griffe._internal.diff.Breakage"
```

Specific breakage class for objects whose kind changed.

Parameters:

- ### **`obj`**

  (`Object`) – The object related to the breakage.

- ### **`old_value`**

  (`Any`) – The old value.

- ### **`new_value`**

  (`Any`) – The new, incompatible value.

- ### **`details`**

  (`str`, default: `''` ) – Some details about the breakage.

Methods:

- **`as_dict`** – Return this object's data as a dictionary.
- **`explain`** – Explain the breakage by showing old and new value.

Attributes:

- **`details`** – Some details about the breakage.
- **`kind`** (`BreakageKind`) – The kind of breakage.
- **`new_value`** – The new, incompatible value.
- **`obj`** – The object related to the breakage.
- **`old_value`** – The old value.

Source code in `src/griffe/_internal/diff.py`

```
def __init__(self, obj: Object, old_value: Any, new_value: Any, details: str = "") -> None:
    """Initialize the breakage.

    Parameters:
        obj: The object related to the breakage.
        old_value: The old value.
        new_value: The new, incompatible value.
        details: Some details about the breakage.
    """
    self.obj = obj
    """The object related to the breakage."""
    self.old_value = old_value
    """The old value."""
    self.new_value = new_value
    """The new, incompatible value."""
    self.details = details
    """Some details about the breakage."""
```

### details

```
details = details
```

Some details about the breakage.

### kind

```
kind: BreakageKind = OBJECT_CHANGED_KIND
```

The kind of breakage.

### new_value

```
new_value = new_value
```

The new, incompatible value.

### obj

```
obj = obj
```

The object related to the breakage.

### old_value

```
old_value = old_value
```

The old value.

### as_dict

```
as_dict(
    *, full: bool = False, **kwargs: Any
) -> dict[str, Any]
```

Return this object's data as a dictionary.

Parameters:

- #### **`full`**

  (`bool`, default: `False` ) – Whether to return full info, or just base info.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/diff.py`

```
def as_dict(self, *, full: bool = False, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
    """Return this object's data as a dictionary.

    Parameters:
        full: Whether to return full info, or just base info.
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    return {
        "kind": self.kind,
        "object_path": self.obj.path,
        "old_value": self.old_value,
        "new_value": self.new_value,
    }
```

### explain

```
explain(style: ExplanationStyle = ONE_LINE) -> str
```

Explain the breakage by showing old and new value.

Parameters:

- #### **`style`**

  (`ExplanationStyle`, default: `ONE_LINE` ) – The explanation style to use.

Returns:

- `str` – An explanation.

Source code in `src/griffe/_internal/diff.py`

```
def explain(self, style: ExplanationStyle = ExplanationStyle.ONE_LINE) -> str:
    """Explain the breakage by showing old and new value.

    Parameters:
        style: The explanation style to use.

    Returns:
        An explanation.
    """
    return getattr(self, f"_explain_{style.value}")()
```

## ObjectRemovedBreakage

```
ObjectRemovedBreakage(
    obj: Object,
    old_value: Any,
    new_value: Any,
    details: str = "",
)
```

Bases: `Breakage`

```
              flowchart TD
              griffe.ObjectRemovedBreakage[ObjectRemovedBreakage]
              griffe._internal.diff.Breakage[Breakage]

                              griffe._internal.diff.Breakage --> griffe.ObjectRemovedBreakage
                


              click griffe.ObjectRemovedBreakage href "" "griffe.ObjectRemovedBreakage"
              click griffe._internal.diff.Breakage href "" "griffe._internal.diff.Breakage"
```

Specific breakage class for removed objects.

Parameters:

- ### **`obj`**

  (`Object`) – The object related to the breakage.

- ### **`old_value`**

  (`Any`) – The old value.

- ### **`new_value`**

  (`Any`) – The new, incompatible value.

- ### **`details`**

  (`str`, default: `''` ) – Some details about the breakage.

Methods:

- **`as_dict`** – Return this object's data as a dictionary.
- **`explain`** – Explain the breakage by showing old and new value.

Attributes:

- **`details`** – Some details about the breakage.
- **`kind`** (`BreakageKind`) – The kind of breakage.
- **`new_value`** – The new, incompatible value.
- **`obj`** – The object related to the breakage.
- **`old_value`** – The old value.

Source code in `src/griffe/_internal/diff.py`

```
def __init__(self, obj: Object, old_value: Any, new_value: Any, details: str = "") -> None:
    """Initialize the breakage.

    Parameters:
        obj: The object related to the breakage.
        old_value: The old value.
        new_value: The new, incompatible value.
        details: Some details about the breakage.
    """
    self.obj = obj
    """The object related to the breakage."""
    self.old_value = old_value
    """The old value."""
    self.new_value = new_value
    """The new, incompatible value."""
    self.details = details
    """Some details about the breakage."""
```

### details

```
details = details
```

Some details about the breakage.

### kind

```
kind: BreakageKind = OBJECT_REMOVED
```

The kind of breakage.

### new_value

```
new_value = new_value
```

The new, incompatible value.

### obj

```
obj = obj
```

The object related to the breakage.

### old_value

```
old_value = old_value
```

The old value.

### as_dict

```
as_dict(
    *, full: bool = False, **kwargs: Any
) -> dict[str, Any]
```

Return this object's data as a dictionary.

Parameters:

- #### **`full`**

  (`bool`, default: `False` ) – Whether to return full info, or just base info.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/diff.py`

```
def as_dict(self, *, full: bool = False, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
    """Return this object's data as a dictionary.

    Parameters:
        full: Whether to return full info, or just base info.
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    return {
        "kind": self.kind,
        "object_path": self.obj.path,
        "old_value": self.old_value,
        "new_value": self.new_value,
    }
```

### explain

```
explain(style: ExplanationStyle = ONE_LINE) -> str
```

Explain the breakage by showing old and new value.

Parameters:

- #### **`style`**

  (`ExplanationStyle`, default: `ONE_LINE` ) – The explanation style to use.

Returns:

- `str` – An explanation.

Source code in `src/griffe/_internal/diff.py`

```
def explain(self, style: ExplanationStyle = ExplanationStyle.ONE_LINE) -> str:
    """Explain the breakage by showing old and new value.

    Parameters:
        style: The explanation style to use.

    Returns:
        An explanation.
    """
    return getattr(self, f"_explain_{style.value}")()
```

## ParameterAddedRequiredBreakage

```
ParameterAddedRequiredBreakage(
    obj: Object,
    old_value: Any,
    new_value: Any,
    details: str = "",
)
```

Bases: `Breakage`

```
              flowchart TD
              griffe.ParameterAddedRequiredBreakage[ParameterAddedRequiredBreakage]
              griffe._internal.diff.Breakage[Breakage]

                              griffe._internal.diff.Breakage --> griffe.ParameterAddedRequiredBreakage
                


              click griffe.ParameterAddedRequiredBreakage href "" "griffe.ParameterAddedRequiredBreakage"
              click griffe._internal.diff.Breakage href "" "griffe._internal.diff.Breakage"
```

Specific breakage class for new parameters added as required.

Parameters:

- ### **`obj`**

  (`Object`) – The object related to the breakage.

- ### **`old_value`**

  (`Any`) – The old value.

- ### **`new_value`**

  (`Any`) – The new, incompatible value.

- ### **`details`**

  (`str`, default: `''` ) – Some details about the breakage.

Methods:

- **`as_dict`** – Return this object's data as a dictionary.
- **`explain`** – Explain the breakage by showing old and new value.

Attributes:

- **`details`** – Some details about the breakage.
- **`kind`** (`BreakageKind`) – The kind of breakage.
- **`new_value`** – The new, incompatible value.
- **`obj`** – The object related to the breakage.
- **`old_value`** – The old value.

Source code in `src/griffe/_internal/diff.py`

```
def __init__(self, obj: Object, old_value: Any, new_value: Any, details: str = "") -> None:
    """Initialize the breakage.

    Parameters:
        obj: The object related to the breakage.
        old_value: The old value.
        new_value: The new, incompatible value.
        details: Some details about the breakage.
    """
    self.obj = obj
    """The object related to the breakage."""
    self.old_value = old_value
    """The old value."""
    self.new_value = new_value
    """The new, incompatible value."""
    self.details = details
    """Some details about the breakage."""
```

### details

```
details = details
```

Some details about the breakage.

### kind

```
kind: BreakageKind = PARAMETER_ADDED_REQUIRED
```

The kind of breakage.

### new_value

```
new_value = new_value
```

The new, incompatible value.

### obj

```
obj = obj
```

The object related to the breakage.

### old_value

```
old_value = old_value
```

The old value.

### as_dict

```
as_dict(
    *, full: bool = False, **kwargs: Any
) -> dict[str, Any]
```

Return this object's data as a dictionary.

Parameters:

- #### **`full`**

  (`bool`, default: `False` ) – Whether to return full info, or just base info.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/diff.py`

```
def as_dict(self, *, full: bool = False, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
    """Return this object's data as a dictionary.

    Parameters:
        full: Whether to return full info, or just base info.
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    return {
        "kind": self.kind,
        "object_path": self.obj.path,
        "old_value": self.old_value,
        "new_value": self.new_value,
    }
```

### explain

```
explain(style: ExplanationStyle = ONE_LINE) -> str
```

Explain the breakage by showing old and new value.

Parameters:

- #### **`style`**

  (`ExplanationStyle`, default: `ONE_LINE` ) – The explanation style to use.

Returns:

- `str` – An explanation.

Source code in `src/griffe/_internal/diff.py`

```
def explain(self, style: ExplanationStyle = ExplanationStyle.ONE_LINE) -> str:
    """Explain the breakage by showing old and new value.

    Parameters:
        style: The explanation style to use.

    Returns:
        An explanation.
    """
    return getattr(self, f"_explain_{style.value}")()
```

## ParameterChangedDefaultBreakage

```
ParameterChangedDefaultBreakage(
    obj: Object,
    old_value: Any,
    new_value: Any,
    details: str = "",
)
```

Bases: `Breakage`

```
              flowchart TD
              griffe.ParameterChangedDefaultBreakage[ParameterChangedDefaultBreakage]
              griffe._internal.diff.Breakage[Breakage]

                              griffe._internal.diff.Breakage --> griffe.ParameterChangedDefaultBreakage
                


              click griffe.ParameterChangedDefaultBreakage href "" "griffe.ParameterChangedDefaultBreakage"
              click griffe._internal.diff.Breakage href "" "griffe._internal.diff.Breakage"
```

Specific breakage class for parameters whose default value changed.

Parameters:

- ### **`obj`**

  (`Object`) – The object related to the breakage.

- ### **`old_value`**

  (`Any`) – The old value.

- ### **`new_value`**

  (`Any`) – The new, incompatible value.

- ### **`details`**

  (`str`, default: `''` ) – Some details about the breakage.

Methods:

- **`as_dict`** – Return this object's data as a dictionary.
- **`explain`** – Explain the breakage by showing old and new value.

Attributes:

- **`details`** – Some details about the breakage.
- **`kind`** (`BreakageKind`) – The kind of breakage.
- **`new_value`** – The new, incompatible value.
- **`obj`** – The object related to the breakage.
- **`old_value`** – The old value.

Source code in `src/griffe/_internal/diff.py`

```
def __init__(self, obj: Object, old_value: Any, new_value: Any, details: str = "") -> None:
    """Initialize the breakage.

    Parameters:
        obj: The object related to the breakage.
        old_value: The old value.
        new_value: The new, incompatible value.
        details: Some details about the breakage.
    """
    self.obj = obj
    """The object related to the breakage."""
    self.old_value = old_value
    """The old value."""
    self.new_value = new_value
    """The new, incompatible value."""
    self.details = details
    """Some details about the breakage."""
```

### details

```
details = details
```

Some details about the breakage.

### kind

```
kind: BreakageKind = PARAMETER_CHANGED_DEFAULT
```

The kind of breakage.

### new_value

```
new_value = new_value
```

The new, incompatible value.

### obj

```
obj = obj
```

The object related to the breakage.

### old_value

```
old_value = old_value
```

The old value.

### as_dict

```
as_dict(
    *, full: bool = False, **kwargs: Any
) -> dict[str, Any]
```

Return this object's data as a dictionary.

Parameters:

- #### **`full`**

  (`bool`, default: `False` ) – Whether to return full info, or just base info.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/diff.py`

```
def as_dict(self, *, full: bool = False, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
    """Return this object's data as a dictionary.

    Parameters:
        full: Whether to return full info, or just base info.
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    return {
        "kind": self.kind,
        "object_path": self.obj.path,
        "old_value": self.old_value,
        "new_value": self.new_value,
    }
```

### explain

```
explain(style: ExplanationStyle = ONE_LINE) -> str
```

Explain the breakage by showing old and new value.

Parameters:

- #### **`style`**

  (`ExplanationStyle`, default: `ONE_LINE` ) – The explanation style to use.

Returns:

- `str` – An explanation.

Source code in `src/griffe/_internal/diff.py`

```
def explain(self, style: ExplanationStyle = ExplanationStyle.ONE_LINE) -> str:
    """Explain the breakage by showing old and new value.

    Parameters:
        style: The explanation style to use.

    Returns:
        An explanation.
    """
    return getattr(self, f"_explain_{style.value}")()
```

## ParameterChangedKindBreakage

```
ParameterChangedKindBreakage(
    obj: Object,
    old_value: Any,
    new_value: Any,
    details: str = "",
)
```

Bases: `Breakage`

```
              flowchart TD
              griffe.ParameterChangedKindBreakage[ParameterChangedKindBreakage]
              griffe._internal.diff.Breakage[Breakage]

                              griffe._internal.diff.Breakage --> griffe.ParameterChangedKindBreakage
                


              click griffe.ParameterChangedKindBreakage href "" "griffe.ParameterChangedKindBreakage"
              click griffe._internal.diff.Breakage href "" "griffe._internal.diff.Breakage"
```

Specific breakage class for parameters whose kind changed.

Parameters:

- ### **`obj`**

  (`Object`) – The object related to the breakage.

- ### **`old_value`**

  (`Any`) – The old value.

- ### **`new_value`**

  (`Any`) – The new, incompatible value.

- ### **`details`**

  (`str`, default: `''` ) – Some details about the breakage.

Methods:

- **`as_dict`** – Return this object's data as a dictionary.
- **`explain`** – Explain the breakage by showing old and new value.

Attributes:

- **`details`** – Some details about the breakage.
- **`kind`** (`BreakageKind`) – The kind of breakage.
- **`new_value`** – The new, incompatible value.
- **`obj`** – The object related to the breakage.
- **`old_value`** – The old value.

Source code in `src/griffe/_internal/diff.py`

```
def __init__(self, obj: Object, old_value: Any, new_value: Any, details: str = "") -> None:
    """Initialize the breakage.

    Parameters:
        obj: The object related to the breakage.
        old_value: The old value.
        new_value: The new, incompatible value.
        details: Some details about the breakage.
    """
    self.obj = obj
    """The object related to the breakage."""
    self.old_value = old_value
    """The old value."""
    self.new_value = new_value
    """The new, incompatible value."""
    self.details = details
    """Some details about the breakage."""
```

### details

```
details = details
```

Some details about the breakage.

### kind

```
kind: BreakageKind = PARAMETER_CHANGED_KIND
```

The kind of breakage.

### new_value

```
new_value = new_value
```

The new, incompatible value.

### obj

```
obj = obj
```

The object related to the breakage.

### old_value

```
old_value = old_value
```

The old value.

### as_dict

```
as_dict(
    *, full: bool = False, **kwargs: Any
) -> dict[str, Any]
```

Return this object's data as a dictionary.

Parameters:

- #### **`full`**

  (`bool`, default: `False` ) – Whether to return full info, or just base info.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/diff.py`

```
def as_dict(self, *, full: bool = False, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
    """Return this object's data as a dictionary.

    Parameters:
        full: Whether to return full info, or just base info.
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    return {
        "kind": self.kind,
        "object_path": self.obj.path,
        "old_value": self.old_value,
        "new_value": self.new_value,
    }
```

### explain

```
explain(style: ExplanationStyle = ONE_LINE) -> str
```

Explain the breakage by showing old and new value.

Parameters:

- #### **`style`**

  (`ExplanationStyle`, default: `ONE_LINE` ) – The explanation style to use.

Returns:

- `str` – An explanation.

Source code in `src/griffe/_internal/diff.py`

```
def explain(self, style: ExplanationStyle = ExplanationStyle.ONE_LINE) -> str:
    """Explain the breakage by showing old and new value.

    Parameters:
        style: The explanation style to use.

    Returns:
        An explanation.
    """
    return getattr(self, f"_explain_{style.value}")()
```

## ParameterChangedRequiredBreakage

```
ParameterChangedRequiredBreakage(
    obj: Object,
    old_value: Any,
    new_value: Any,
    details: str = "",
)
```

Bases: `Breakage`

```
              flowchart TD
              griffe.ParameterChangedRequiredBreakage[ParameterChangedRequiredBreakage]
              griffe._internal.diff.Breakage[Breakage]

                              griffe._internal.diff.Breakage --> griffe.ParameterChangedRequiredBreakage
                


              click griffe.ParameterChangedRequiredBreakage href "" "griffe.ParameterChangedRequiredBreakage"
              click griffe._internal.diff.Breakage href "" "griffe._internal.diff.Breakage"
```

Specific breakage class for parameters which became required.

Parameters:

- ### **`obj`**

  (`Object`) – The object related to the breakage.

- ### **`old_value`**

  (`Any`) – The old value.

- ### **`new_value`**

  (`Any`) – The new, incompatible value.

- ### **`details`**

  (`str`, default: `''` ) – Some details about the breakage.

Methods:

- **`as_dict`** – Return this object's data as a dictionary.
- **`explain`** – Explain the breakage by showing old and new value.

Attributes:

- **`details`** – Some details about the breakage.
- **`kind`** (`BreakageKind`) – The kind of breakage.
- **`new_value`** – The new, incompatible value.
- **`obj`** – The object related to the breakage.
- **`old_value`** – The old value.

Source code in `src/griffe/_internal/diff.py`

```
def __init__(self, obj: Object, old_value: Any, new_value: Any, details: str = "") -> None:
    """Initialize the breakage.

    Parameters:
        obj: The object related to the breakage.
        old_value: The old value.
        new_value: The new, incompatible value.
        details: Some details about the breakage.
    """
    self.obj = obj
    """The object related to the breakage."""
    self.old_value = old_value
    """The old value."""
    self.new_value = new_value
    """The new, incompatible value."""
    self.details = details
    """Some details about the breakage."""
```

### details

```
details = details
```

Some details about the breakage.

### kind

```
kind: BreakageKind = PARAMETER_CHANGED_REQUIRED
```

The kind of breakage.

### new_value

```
new_value = new_value
```

The new, incompatible value.

### obj

```
obj = obj
```

The object related to the breakage.

### old_value

```
old_value = old_value
```

The old value.

### as_dict

```
as_dict(
    *, full: bool = False, **kwargs: Any
) -> dict[str, Any]
```

Return this object's data as a dictionary.

Parameters:

- #### **`full`**

  (`bool`, default: `False` ) – Whether to return full info, or just base info.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/diff.py`

```
def as_dict(self, *, full: bool = False, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
    """Return this object's data as a dictionary.

    Parameters:
        full: Whether to return full info, or just base info.
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    return {
        "kind": self.kind,
        "object_path": self.obj.path,
        "old_value": self.old_value,
        "new_value": self.new_value,
    }
```

### explain

```
explain(style: ExplanationStyle = ONE_LINE) -> str
```

Explain the breakage by showing old and new value.

Parameters:

- #### **`style`**

  (`ExplanationStyle`, default: `ONE_LINE` ) – The explanation style to use.

Returns:

- `str` – An explanation.

Source code in `src/griffe/_internal/diff.py`

```
def explain(self, style: ExplanationStyle = ExplanationStyle.ONE_LINE) -> str:
    """Explain the breakage by showing old and new value.

    Parameters:
        style: The explanation style to use.

    Returns:
        An explanation.
    """
    return getattr(self, f"_explain_{style.value}")()
```

## ParameterMovedBreakage

```
ParameterMovedBreakage(
    obj: Object,
    old_value: Any,
    new_value: Any,
    details: str = "",
)
```

Bases: `Breakage`

```
              flowchart TD
              griffe.ParameterMovedBreakage[ParameterMovedBreakage]
              griffe._internal.diff.Breakage[Breakage]

                              griffe._internal.diff.Breakage --> griffe.ParameterMovedBreakage
                


              click griffe.ParameterMovedBreakage href "" "griffe.ParameterMovedBreakage"
              click griffe._internal.diff.Breakage href "" "griffe._internal.diff.Breakage"
```

Specific breakage class for moved parameters.

Parameters:

- ### **`obj`**

  (`Object`) – The object related to the breakage.

- ### **`old_value`**

  (`Any`) – The old value.

- ### **`new_value`**

  (`Any`) – The new, incompatible value.

- ### **`details`**

  (`str`, default: `''` ) – Some details about the breakage.

Methods:

- **`as_dict`** – Return this object's data as a dictionary.
- **`explain`** – Explain the breakage by showing old and new value.

Attributes:

- **`details`** – Some details about the breakage.
- **`kind`** (`BreakageKind`) – The kind of breakage.
- **`new_value`** – The new, incompatible value.
- **`obj`** – The object related to the breakage.
- **`old_value`** – The old value.

Source code in `src/griffe/_internal/diff.py`

```
def __init__(self, obj: Object, old_value: Any, new_value: Any, details: str = "") -> None:
    """Initialize the breakage.

    Parameters:
        obj: The object related to the breakage.
        old_value: The old value.
        new_value: The new, incompatible value.
        details: Some details about the breakage.
    """
    self.obj = obj
    """The object related to the breakage."""
    self.old_value = old_value
    """The old value."""
    self.new_value = new_value
    """The new, incompatible value."""
    self.details = details
    """Some details about the breakage."""
```

### details

```
details = details
```

Some details about the breakage.

### kind

```
kind: BreakageKind = PARAMETER_MOVED
```

The kind of breakage.

### new_value

```
new_value = new_value
```

The new, incompatible value.

### obj

```
obj = obj
```

The object related to the breakage.

### old_value

```
old_value = old_value
```

The old value.

### as_dict

```
as_dict(
    *, full: bool = False, **kwargs: Any
) -> dict[str, Any]
```

Return this object's data as a dictionary.

Parameters:

- #### **`full`**

  (`bool`, default: `False` ) – Whether to return full info, or just base info.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/diff.py`

```
def as_dict(self, *, full: bool = False, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
    """Return this object's data as a dictionary.

    Parameters:
        full: Whether to return full info, or just base info.
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    return {
        "kind": self.kind,
        "object_path": self.obj.path,
        "old_value": self.old_value,
        "new_value": self.new_value,
    }
```

### explain

```
explain(style: ExplanationStyle = ONE_LINE) -> str
```

Explain the breakage by showing old and new value.

Parameters:

- #### **`style`**

  (`ExplanationStyle`, default: `ONE_LINE` ) – The explanation style to use.

Returns:

- `str` – An explanation.

Source code in `src/griffe/_internal/diff.py`

```
def explain(self, style: ExplanationStyle = ExplanationStyle.ONE_LINE) -> str:
    """Explain the breakage by showing old and new value.

    Parameters:
        style: The explanation style to use.

    Returns:
        An explanation.
    """
    return getattr(self, f"_explain_{style.value}")()
```

## ParameterRemovedBreakage

```
ParameterRemovedBreakage(
    obj: Object,
    old_value: Any,
    new_value: Any,
    details: str = "",
)
```

Bases: `Breakage`

```
              flowchart TD
              griffe.ParameterRemovedBreakage[ParameterRemovedBreakage]
              griffe._internal.diff.Breakage[Breakage]

                              griffe._internal.diff.Breakage --> griffe.ParameterRemovedBreakage
                


              click griffe.ParameterRemovedBreakage href "" "griffe.ParameterRemovedBreakage"
              click griffe._internal.diff.Breakage href "" "griffe._internal.diff.Breakage"
```

Specific breakage class for removed parameters.

Parameters:

- ### **`obj`**

  (`Object`) – The object related to the breakage.

- ### **`old_value`**

  (`Any`) – The old value.

- ### **`new_value`**

  (`Any`) – The new, incompatible value.

- ### **`details`**

  (`str`, default: `''` ) – Some details about the breakage.

Methods:

- **`as_dict`** – Return this object's data as a dictionary.
- **`explain`** – Explain the breakage by showing old and new value.

Attributes:

- **`details`** – Some details about the breakage.
- **`kind`** (`BreakageKind`) – The kind of breakage.
- **`new_value`** – The new, incompatible value.
- **`obj`** – The object related to the breakage.
- **`old_value`** – The old value.

Source code in `src/griffe/_internal/diff.py`

```
def __init__(self, obj: Object, old_value: Any, new_value: Any, details: str = "") -> None:
    """Initialize the breakage.

    Parameters:
        obj: The object related to the breakage.
        old_value: The old value.
        new_value: The new, incompatible value.
        details: Some details about the breakage.
    """
    self.obj = obj
    """The object related to the breakage."""
    self.old_value = old_value
    """The old value."""
    self.new_value = new_value
    """The new, incompatible value."""
    self.details = details
    """Some details about the breakage."""
```

### details

```
details = details
```

Some details about the breakage.

### kind

```
kind: BreakageKind = PARAMETER_REMOVED
```

The kind of breakage.

### new_value

```
new_value = new_value
```

The new, incompatible value.

### obj

```
obj = obj
```

The object related to the breakage.

### old_value

```
old_value = old_value
```

The old value.

### as_dict

```
as_dict(
    *, full: bool = False, **kwargs: Any
) -> dict[str, Any]
```

Return this object's data as a dictionary.

Parameters:

- #### **`full`**

  (`bool`, default: `False` ) – Whether to return full info, or just base info.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/diff.py`

```
def as_dict(self, *, full: bool = False, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
    """Return this object's data as a dictionary.

    Parameters:
        full: Whether to return full info, or just base info.
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    return {
        "kind": self.kind,
        "object_path": self.obj.path,
        "old_value": self.old_value,
        "new_value": self.new_value,
    }
```

### explain

```
explain(style: ExplanationStyle = ONE_LINE) -> str
```

Explain the breakage by showing old and new value.

Parameters:

- #### **`style`**

  (`ExplanationStyle`, default: `ONE_LINE` ) – The explanation style to use.

Returns:

- `str` – An explanation.

Source code in `src/griffe/_internal/diff.py`

```
def explain(self, style: ExplanationStyle = ExplanationStyle.ONE_LINE) -> str:
    """Explain the breakage by showing old and new value.

    Parameters:
        style: The explanation style to use.

    Returns:
        An explanation.
    """
    return getattr(self, f"_explain_{style.value}")()
```

## ReturnChangedTypeBreakage

```
ReturnChangedTypeBreakage(
    obj: Object,
    old_value: Any,
    new_value: Any,
    details: str = "",
)
```

Bases: `Breakage`

```
              flowchart TD
              griffe.ReturnChangedTypeBreakage[ReturnChangedTypeBreakage]
              griffe._internal.diff.Breakage[Breakage]

                              griffe._internal.diff.Breakage --> griffe.ReturnChangedTypeBreakage
                


              click griffe.ReturnChangedTypeBreakage href "" "griffe.ReturnChangedTypeBreakage"
              click griffe._internal.diff.Breakage href "" "griffe._internal.diff.Breakage"
```

Specific breakage class for return values which changed type.

Parameters:

- ### **`obj`**

  (`Object`) – The object related to the breakage.

- ### **`old_value`**

  (`Any`) – The old value.

- ### **`new_value`**

  (`Any`) – The new, incompatible value.

- ### **`details`**

  (`str`, default: `''` ) – Some details about the breakage.

Methods:

- **`as_dict`** – Return this object's data as a dictionary.
- **`explain`** – Explain the breakage by showing old and new value.

Attributes:

- **`details`** – Some details about the breakage.
- **`kind`** (`BreakageKind`) – The kind of breakage.
- **`new_value`** – The new, incompatible value.
- **`obj`** – The object related to the breakage.
- **`old_value`** – The old value.

Source code in `src/griffe/_internal/diff.py`

```
def __init__(self, obj: Object, old_value: Any, new_value: Any, details: str = "") -> None:
    """Initialize the breakage.

    Parameters:
        obj: The object related to the breakage.
        old_value: The old value.
        new_value: The new, incompatible value.
        details: Some details about the breakage.
    """
    self.obj = obj
    """The object related to the breakage."""
    self.old_value = old_value
    """The old value."""
    self.new_value = new_value
    """The new, incompatible value."""
    self.details = details
    """Some details about the breakage."""
```

### details

```
details = details
```

Some details about the breakage.

### kind

```
kind: BreakageKind = RETURN_CHANGED_TYPE
```

The kind of breakage.

### new_value

```
new_value = new_value
```

The new, incompatible value.

### obj

```
obj = obj
```

The object related to the breakage.

### old_value

```
old_value = old_value
```

The old value.

### as_dict

```
as_dict(
    *, full: bool = False, **kwargs: Any
) -> dict[str, Any]
```

Return this object's data as a dictionary.

Parameters:

- #### **`full`**

  (`bool`, default: `False` ) – Whether to return full info, or just base info.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `src/griffe/_internal/diff.py`

```
def as_dict(self, *, full: bool = False, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
    """Return this object's data as a dictionary.

    Parameters:
        full: Whether to return full info, or just base info.
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    return {
        "kind": self.kind,
        "object_path": self.obj.path,
        "old_value": self.old_value,
        "new_value": self.new_value,
    }
```

### explain

```
explain(style: ExplanationStyle = ONE_LINE) -> str
```

Explain the breakage by showing old and new value.

Parameters:

- #### **`style`**

  (`ExplanationStyle`, default: `ONE_LINE` ) – The explanation style to use.

Returns:

- `str` – An explanation.

Source code in `src/griffe/_internal/diff.py`

```
def explain(self, style: ExplanationStyle = ExplanationStyle.ONE_LINE) -> str:
    """Explain the breakage by showing old and new value.

    Parameters:
        style: The explanation style to use.

    Returns:
        An explanation.
    """
    return getattr(self, f"_explain_{style.value}")()
```
