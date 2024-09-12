# Introduction

Griffe is able to read Python source code and inspect objects at runtime to extract information about the API of a Python package. This information is then stored into data models (Python classes), and these model instances together form a tree that statically represent the package's API: starting with the top-level module, then descending into submodules, classes, functions and attributes. From there, it's possible to explore and exploit this API representation in various ways.

## Command line tool

Griffe is both a command line tool and a Python library. The command line tool offers a few commands to, for example, serialize API data to JSON and check for API breaking changes between two versions of your project.

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

For a complete reference of the application programming interface, see [Reference / Python API](reference/api.md).
