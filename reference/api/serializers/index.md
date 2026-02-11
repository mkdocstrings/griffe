# Serializers

## **Main API**

See the as_json() and from_json() methods of objects.

## **Advanced API**

## JSONEncoder

```
JSONEncoder(*args: Any, full: bool = False, **kwargs: Any)
```

Bases: `JSONEncoder`

```
              flowchart TD
              griffe.JSONEncoder[JSONEncoder]

              

              click griffe.JSONEncoder href "" "griffe.JSONEncoder"
```

JSON encoder.

JSON encoders can be used directly, or through the json.dump or json.dumps methods.

Examples:

```
>>> from griffe import JSONEncoder
>>> JSONEncoder(full=True).encode(..., **kwargs)
```

```
>>> import json
>>> from griffe import JSONEncoder
>>> json.dumps(..., cls=JSONEncoder, full=True, **kwargs)
```

Parameters:

- ### **`*args`**

  (`Any`, default: `()` ) – See json.JSONEncoder.

- ### **`full`**

  (`bool`, default: `False` ) – Whether to dump full data or base data. If you plan to reload the data in Python memory using the json_decoder, you don't need the full data as it can be inferred again using the base data. If you want to feed a non-Python tool instead, dump the full data.

- ### **`**kwargs`**

  (`Any`, default: `{}` ) – See json.JSONEncoder.

Methods:

- **`default`** – Return a serializable representation of the given object.

Attributes:

- **`full`** (`bool`) – Whether to dump full data or base data.

Source code in `packages/griffelib/src/griffe/_internal/encoders.py`

```
def __init__(
    self,
    *args: Any,
    full: bool = False,
    **kwargs: Any,
) -> None:
    """Initialize the encoder.

    Parameters:
        *args: See [`json.JSONEncoder`][].
        full: Whether to dump full data or base data.
            If you plan to reload the data in Python memory
            using the [`json_decoder`][griffe.json_decoder],
            you don't need the full data as it can be inferred again
            using the base data. If you want to feed a non-Python
            tool instead, dump the full data.
        **kwargs: See [`json.JSONEncoder`][].
    """
    super().__init__(*args, **kwargs)
    self.full: bool = full
    """Whether to dump full data or base data."""
```

### full

```
full: bool = full
```

Whether to dump full data or base data.

### default

```
default(obj: Any) -> Any
```

Return a serializable representation of the given object.

Parameters:

- #### **`obj`**

  (`Any`) – The object to serialize.

Returns:

- `Any` – A serializable representation.

Source code in `packages/griffelib/src/griffe/_internal/encoders.py`

```
def default(self, obj: Any) -> Any:  # ty:ignore[invalid-method-override]
    """Return a serializable representation of the given object.

    Parameters:
        obj: The object to serialize.

    Returns:
        A serializable representation.
    """
    try:
        return obj.as_dict(full=self.full)
    except AttributeError:
        return _json_encoder_map.get(type(obj), super().default)(obj)
```

## json_decoder

```
json_decoder(
    obj_dict: dict[str, Any],
) -> (
    dict[str, Any]
    | Object
    | Alias
    | Parameter
    | TypeParameter
    | str
    | Expr
)
```

Decode dictionaries as data classes.

The json.loads method walks the tree from bottom to top.

Examples:

```
>>> import json
>>> from griffe import json_decoder
>>> json.loads(..., object_hook=json_decoder)
```

Parameters:

- ### **`obj_dict`**

  (`dict[str, Any]`) – The dictionary to decode.

Returns:

- `dict[str, Any] | Object | Alias | Parameter | TypeParameter | str | Expr` – An instance of a data class.

Source code in `packages/griffelib/src/griffe/_internal/encoders.py`

```
def json_decoder(
    obj_dict: dict[str, Any],
) -> dict[str, Any] | Object | Alias | Parameter | TypeParameter | str | expressions.Expr:
    """Decode dictionaries as data classes.

    The [`json.loads`][] method walks the tree from bottom to top.

    Examples:
        >>> import json
        >>> from griffe import json_decoder
        >>> json.loads(..., object_hook=json_decoder)

    Parameters:
        obj_dict: The dictionary to decode.

    Returns:
        An instance of a data class.
    """
    # Load expressions.
    if "cls" in obj_dict:
        return _load_expression(obj_dict)

    # Load objects and parameters.
    if "kind" in obj_dict:
        kind = obj_dict["kind"]
        if kind in _loader_map:
            return _loader_map[kind](obj_dict)
        # YORE: EOL 3.11: Replace `.__members__.values()` with `` within line.
        if kind in ParameterKind.__members__.values():
            return _load_parameter(obj_dict)
        # YORE: EOL 3.11: Replace `.__members__.values()` with `` within line.
        if kind in TypeParameterKind.__members__.values():
            return _load_type_parameter(obj_dict)

    # Return dict as is.
    return obj_dict
```
