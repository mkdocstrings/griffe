# `griffe-runtime-objects`

[:octicons-heart-fill-24:{ .pulse } Sponsors only](../../insiders/index.md){ .insiders }

- **PyPI**: [`griffe-runtime-objects`](https://pypi.org/project/griffe-runtime-objects/)
- **GitHub**: [mkdocstrings/griffe-runtime-objects](https://github.com/mkdocstrings/griffe-runtime-objects)
- **Documentation:** [mkdocstrings.github.io/griffe-runtime-objects](https://mkdocstrings.github.io/griffe-runtime-objects)
- **Extension name:** `griffe_runtime_objects`

---

This extension stores runtime objects corresponding to each loaded Griffe object into its `extra` attribute, under the `runtime-objects` namespace.

```pycon
>>> import griffe
>>> griffe_data = griffe.load("griffe", extensions=griffe.load_extensions("griffe_runtime_objects"), resolve_aliases=True)
>>> griffe_data["parse"].extra
defaultdict(<class 'dict'>, {'runtime-objects': {'object': <function parse at 0x78685c951260>}})
>>> griffe_data["Module"].extra
defaultdict(<class 'dict'>, {'runtime-objects': {'object': <class '_griffe.models.Module'>}})
```

It can be useful in combination with mkdocstrings-python and custom templates, to iterate on object values or their attributes who couldn't be loaded by Griffe itself (for example objects built dynamically and loaded as attributes won't have "members" to iterate on).
