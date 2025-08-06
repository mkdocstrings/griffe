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
