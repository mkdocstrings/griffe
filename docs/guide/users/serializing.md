# Serializing APIs

Griffe can be used to load API data and output it as JSON on standard output or in writable files. An example of what real data looks like can be found here: [Griffe's full JSON dump](../../griffe.json). We also provide a [JSON schema](../../schema.json).

## Command-line

The easiest way to load and serialize API data is to use the command-line tool:

```console
$ griffe dump httpx fastapi
{
  "httpx": {
    "name": "httpx",
    ...
  },
  "fastapi": {
    "name": "fastapi",
    ...
  }
}
```

It will output a JSON-serialized version of the packages API data.

Try it out on Griffe itself:

```console
$ griffe dump griffe
{
  "griffe": {
    "name": "griffe",
    ...
  }
}
```

To output in a file instead of standard output, use the `-o`, `--output` option:

```console
$ griffe dump griffe -o griffe.json
```

If you load multiple packages' signatures, you can dump each in its own file with a templated filepath:

```console
$ griffe dump griffe -o './dumps/{package}.json'
```

By default, Griffe will search in `sys.path`, so if you installed it through *pipx*, there are few chances it will find your packages. To explicitly specify search paths, use the `-s, --search <PATH>` option. You can use it multiple times. You can also add the search paths to the `PYTHONPATH` environment variable. If Griffe can't find the packages, it will fail with a `ModuleNotFoundError`.

See all the options for the `dump` command in the [CLI reference](../../reference/cli.md).

## Python API

If you have read through the [Navigating](navigating.md) chapter, you know about our five data models for modules, classes, functions, attributes and aliases. Each one of these model provide the two following methods:

- [`as_json`][griffe.Object.as_json], which allows to serialize an object into JSON,
- [`from_json`][griffe.Object.from_json], which allows to load JSON back into a model instance.

These two methods are convenient wrappers around our [JSON encoder][griffe.JSONEncoder] and [JSON decoder][griffe.json_decoder]. The JSON encoder and decoder will give you finer-grain control over what you serialize or load, as the methods above are only available on data models, and not on sub-structures like decorators or parameters.

Under the hood, `as_json` just calls [`as_dict`][griffe.Object.as_dict], which converts the model instance into a dictionary, and then serialize this dictionary to JSON.

When serializing an object, by default the JSON will only contain the fields required to load it back to a Griffe model instance. If you are not planning on loading back the data into our data models, or if you want to load them in a different implementation which is not able to infer back all the other fields, you can choose to serialize every possible field. We call this a full dump, and it is enabled with the `full` option of the [encoder][griffe.JSONEncoder] or the [`as_json`][griffe.Object.as_json] method.

## Schema

For anything automated, we suggest relying on our [JSON schema](../../schema.json).

When serializing multiple packages with the `dump` command, you get a map with package names as keys. Map values are the serialized objects (modules, classes, functions, etc.). They are maps too, with field names and values as key-value pairs.

For example:

```json
{
  "kind": "class",
  "name": "Expr",
  "lineno": 82,
  "endlineno": 171,
  "docstring": {
    "value": "Base class for expressions.",
    "lineno": 84,
    "endlineno": 84
  },
  "labels": [
    "dataclass"
  ],
  "members": [
    ...
  ],
  "bases": [],
  "decorators": [
    {
      "value": {
        "name": "dataclass",
        "cls": "ExprName"
      },
      "lineno": 82,
      "endlineno": 82
    }
  ]
}
```

The `members` value, truncated here, just repeats the pattern: it's an array of maps. We use an array for members instead of a map to preserve order, which could be important to downstream tools.

The other fields do not require explanations, except maybe for expressions. You will sometimes notice deeply nested structures with `cls` keys. These are serialized Griffe [expressions](../../reference/api/expressions.md). They represent actual code.

## Next steps

That's it! There is not much to say about serialization. We are interested in getting your feedback regarding serialization as we didn't see it being used a lot. Next you might be interested in learning how to [check](checking.md) or [extend](extending.md) your API data.
