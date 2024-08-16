# `griffe-fieldz`

- **PyPI**: [`griffe-fieldz`](https://pypi.org/project/griffe-fieldz/)
- **GitHub**: [pyapp-kit/griffe-fieldz](https://github.com/pyapp-kit/griffe-fieldz)
- **Extension name:** `griffe_fieldz`

---

This extension adds support for data-class like things (pydantic, attrs, etc...). This extension will inject the fields of the data-class into the documentation, preventing you from duplicating field metadata in your docstrings.

It supports anything that [fieldz](https://github.com/pyapp-kit/fieldz) supports, which is currently:

- [`dataclasses.dataclass`](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass)
- [`pydantic.BaseModel`](https://docs.pydantic.dev/latest/)
- [`attrs.define`](https://www.attrs.org/en/stable/overview.html)
- [`msgspec.Struct`](https://jcristharif.com/msgspec/)
