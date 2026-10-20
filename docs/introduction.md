# Introduction

Griffe is able to read Python source code and inspect objects at runtime to extract information about the API of a Python package. This information is then stored into data models (Python classes), and these model instances together form a tree that statically represent the package's API: starting with the top-level module, then descending into submodules, classes, functions, attributes and type aliases. From there, it's possible to explore and exploit this API representation in various ways.

This tour shows how to export API data with the CLI and explore it with Python. [Install Griffe](installation.md) before running the examples.

Create an `example.py` file in your working directory:

```python title="example.py"
def greet(name: str) -> str:
    """Return a greeting for the given name."""
    return f"Hello, {name}!"
```

## Command line tool

Griffe is both a command line tool and a Python library. The command line tool offers a few commands to, for example, serialize API data to JSON and check for API breaking changes between two versions of your project.

From the directory containing `example.py`, export its API:

```bash
griffe dump example --output api.json
```

This writes `api.json` with an `example` entry containing the module's members, signatures, and docstrings. It does not call `greet`.

For your own package, replace `my_package` in the following commands with its import name:

```bash
# Load API of `my_package`, serialize it to JSON,
# print it to standard output.
griffe dump my_package
```

```bash
# Check for API breaking changes
# between current version and version 1.0 (Git reference).
griffe check my_package --against 1.0
```

Both commands accept a `-h`, `--help` argument to show all the available options. For a complete reference of the command line interface, see [Reference / Command line interface](reference/cli.md).

## Python library

As a library, Griffe exposes all its public API directly in the top-level module. It means you can simply import `griffe` to access all its API.

From the same directory, run this Python example:

```python
import griffe

module = griffe.load("example")
function = module["greet"]

print(function.path)
print(function.parameters["name"].annotation)
print(function.returns)
print(function.docstring.value)
```

Expected output:

```text
example.greet
str
str
Return a greeting for the given name.
```

The function is represented by a Griffe data model. You can inspect its signature and docstring without executing its body.

Other public entrypoints include:

```python
import griffe

griffe.load(...)
griffe.find_breaking_changes(...)
griffe.main(...)
griffe.visit(...)
griffe.inspect(...)
```

To start exploring your API within Griffe data models, use the [`load`][griffe.load] function to load your package and access its various objects:

```python
import griffe

my_package = griffe.load("my_package")

some_method = my_package["some_module.SomeClass.some_method"]
print(some_method.docstring.value)
print(f"Is `some_method` public? {'yes' if some_method.is_public else 'no'}")
```

Use the [`load_git`][griffe.load_git] function to load your API at a particular moment in time, specified with a Git reference (commit hash, branch name, tag name):

```python
import griffe

my_package_v2_1 = griffe.load_git("my_package", ref="2.1")
```

For more advanced usage, see our guide on [loading and navigating data](guide/users/loading.md).

For a complete reference of the application programming interface, see [Reference / Python API](reference/api/index.md).

## Next steps

- [Loading APIs](guide/users/loading.md): configure how Griffe finds and analyzes your package.
- [Navigating APIs](guide/users/navigating.md): explore members, aliases, and inheritance.
- [Checking APIs](guide/users/checking.md): compare versions and handle breaking changes.
