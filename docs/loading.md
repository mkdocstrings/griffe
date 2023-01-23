# Loading data with Python

Griffe provides a shortcut function for simple needs:

```python
import griffe

mkdocs = griffe.load("mkdocs")
```

The [`load`][griffe.loader.load] function accepts a number of parameters.

For more complex needs, create and use a loader:

```python
from griffe.loader import GriffeLoader

loader = GriffeLoader()
mkdocs = loader.load_module("mkdocs")
```

Similarly, the [`GriffeLoader`][griffe.loader.GriffeLoader] accepts
a number of parameters to configure how the modules are found and loaded.

If you don't want to recurse in the submodules:

```python
mkdocs = loader.load_module("mkdocs", submodules=False)
```

## Navigating into the loaded objects

Both the `load` function and the `GriffeLoader.load_module` method
return a [`Module`][griffe.dataclasses.Module] instance.
There are several ways to access members of an object:

- through its `members` attribute, which is a dictionary,
  with the usual `keys()`, `values()` and `items()` methods.
- thanks to its `__getitem__` method. For example `griffe["dataclasses"]`
  returns the `Module` instance representing Griffe's `dataclasses` module.
  Since this module also has members, you can chain calls: `griffe["dataclasses"]["Module"]`.
  Conveniently, you can chain the names with dots in a single call: `griffe["dataclasses.Module"]`.
  You can even pass a tuple instead of a string: `griffe[("dataclasses", "Module")]`.
- through the [`modules`][griffe.dataclasses.Object.modules],
  [`classes`][griffe.dataclasses.Object.classes],
  [`functions`][griffe.dataclasses.Object.functions] and
  [`attributes`][griffe.dataclasses.Object.attributes] properties,
  which take care of filtering members based on their kind, and return dictionaries.

Most of the time, you will only use classes from the [`griffe.dataclasses`][griffe.dataclasses]
and [`griffe.docstrings.dataclasses`][griffe.docstrings.dataclasses] modules.
