# Official extensions

Official extensions are developed and maintained within the mkdocstrings organization on GitHub, in separate repositories. They generally bring support for various third-party libraries or other documentation-related features that are part of Python's standard library.

Extension | Description
--------- | -----------
[`autodocstringstyle`](autodocstringstyle.md) | Set docstring style to `auto` for external packages.
 [`inherited-docstrings`](inherited-docstrings.md) | Inherit docstrings from parent classes.
[`public-redundant-aliases`](public-redundant-aliases.md) | Mark objects imported with redundant aliases as public.
[`public-wildcard-imports`](public-wildcard-imports.md) | Mark wildcard imported objects as public.
 [`pydantic`](pydantic.md) | Support for [Pydantic](https://docs.pydantic.dev/latest/) models.
[`runtime-objects`](runtime-objects.md) | Access runtime objects corresponding to each loaded Griffe object through their `extra` attribute.
[`sphinx`](sphinx.md) | Parse [Sphinx](https://www.sphinx-doc.org/)-comments above attributes (`#:`) as docstrings.
 [`typing-doc`](typingdoc.md) | Support for [PEP 727](https://peps.python.org/pep-0727/)'s [`typing.Doc`][typing_extensions.Doc], "Documentation in Annotated Metadata".
 [`warnings-deprecated`](warnings-deprecated.md) | Support for [PEP 702](https://peps.python.org/pep-0702/)'s [`warnings.deprecated`][], "Marking deprecations using the type system".
