# `griffe-generics`

- **PyPI**: [`griffe-generics`](https://pypi.org/project/griffe-generics/)
- **GitHub**: [jonghwanhyeon/griffe-generics](https://github.com/jonghwanhyeon/griffe-generics)
- **Extension name:** `griffe_generics`

---

This extension resolves generic type parameters as bound types in subclasses. For example, if a parent class inherits from `Generics[L]`, and a subclass specifies `L` as `Hashable`, then all type annotations using `L` in the class methods or attributes inherited from the parent class will be transformed to use `Hashable` instead.
