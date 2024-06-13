
## Navigating into the loaded objects

Both the `load` function and the `GriffeLoader.load` method
return an [`Object`][griffe.Object] instance.
There are several ways to access members of an object:

- through its `members` attribute, which is a dictionary,
  with the usual `keys()`, `values()` and `items()` methods.
- thanks to its `__getitem__` method. For example `griffe["dataclasses"]`
  returns the `Module` instance representing Griffe's `dataclasses` module.
  Since this module also has members, you can chain calls: `griffe["dataclasses"]["Module"]`.
  Conveniently, you can chain the names with dots in a single call: `griffe["dataclasses.Module"]`.
  You can even pass a tuple instead of a string: `griffe[("dataclasses", "Module")]`.
- through the [`modules`][griffe.Object.modules],
  [`classes`][griffe.Object.classes],
  [`functions`][griffe.Object.functions] and
  [`attributes`][griffe.Object.attributes] properties,
  which take care of filtering members based on their kind, and return dictionaries.
