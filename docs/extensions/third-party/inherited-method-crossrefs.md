# `griffe-inherited-method-crossrefs`

- **PyPI**: [`griffe-inherited-method-crossrefs`](https://pypi.org/project/griffe-inherited-method-crossrefs/)
- **GitHub**: [mlprt/griffe-inherited-method-crossrefs](https://github.com/mlprt/griffe-inherited-method-crossrefs)
- **Extension name:** `griffe_inherited_method_crossrefs`

---

This extension replaces docstrings of inherited methods with cross-references to parent methods. For example, if a class `foo.Child` inherits the method `do_something` from `bar.Parent`, then in the generated documentation, the docstring of `Child.do_something` will appear similar to

> Inherited from [bar.Parent](https://example.com/link/to/bar.Parent.do_something)

whereas the docstring of `bar.Parent.do_something` will be unaffected.

This is contrast to the official [`inherited-docstrings`](../official/inherited-docstrings.md) extension which simply attaches the docstring of the parent method to the subclass method, which means that modifying the subclass method docstring also modifies the parent method docstring (it's the same object).
