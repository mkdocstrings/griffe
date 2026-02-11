# Third-party extensions

Third-party extensions are developed and maintained outside of the mkdocstrings organization, by various developers. They generally bring support for third-party libraries.

| Extension                                                                                                                        | Description                                                                                                                   |
| -------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| [`docstring-inheritance`](https://mkdocstrings.github.io/griffe/extensions/third-party/docstring-inheritance/index.md)           | A more advanced docstring inheritance utility that also provides a Griffe extension.                                          |
| [`fastapi`](https://github.com/fbraem/griffe-fastapi)                                                                            | Search for functions that are decorated with an APIRouter and adds the extra fields to a function.                            |
| [`fieldz`](https://mkdocstrings.github.io/griffe/extensions/third-party/fieldz/index.md)                                         | Support for data-class like objects (dataclasses, pydantic, attrs, etc.) using [fieldz](https://github.com/pyapp-kit/fieldz). |
| [`generics`](https://mkdocstrings.github.io/griffe/extensions/third-party/generics/index.md)                                     | Resolve generic type parameters as bound types in subclasses.                                                                 |
| [`inherited-method-crossrefs`](https://mkdocstrings.github.io/griffe/extensions/third-party/inherited-method-crossrefs/index.md) | Replace docstrings of inherited methods with cross-references to parents.                                                     |
| [`modernized-annotations`](https://mkdocstrings.github.io/griffe/extensions/third-party/modernized-annotations/index.md)         | Modernize type annotations by adopting PEP 585 and PEP 604.                                                                   |

You can find more third-party extensions by exploring the [`griffe-extension` topic on GitHub](https://github.com/topics/griffe-extension). You can also check out the "in-project" extensions (not published to PyPI) used in various projects on GitHub by [searching for "griffe extension" in code](https://github.com/search?q=griffe+Extension+language%3Apython&type=code).
