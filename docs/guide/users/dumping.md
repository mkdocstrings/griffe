# Dumping packages' signatures as JSON

Griffe can be used to load packages' signatures
and output them as JSON on the standard output
or in writable files.

Pass the names of packages to the `griffe dump` command:

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

It will output a JSON-serialized version of the packages' signatures.

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

To output in a file instead of standard output,
use the `--output` or `-o` option:

```console
$ griffe dump griffe -o griffe.json
```

If you load multiple packages' signatures,
you can dump each in its own file with a templated filepath:

```console
$ griffe dump griffe -o './dumps/{package}.json'
```

By default, Griffe will search in `sys.path`, so if you installed it through *pipx*,
there are few chances it will find your packages.
To explicitly specify search paths, use the `-s, --search <PATH>` option.
You can use it multiple times.
You can also add the search paths to the `PYTHONPATH` environment variable.
If Griffe can't find the packages, it will fail with a `ModuleNotFoundError`.

For an example of what real data looks like,
see [the full Griffe JSON dump](griffe.json). 
