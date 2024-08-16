# `dataclasses`

The `dataclasses` extension adds support for [dataclasses][] from the standard library. It works both statically and dynamically. When used statically, it re-creates the `__init__` methods and their signatures (as Griffe objects), that would otherwise be created at runtime. When used dynamically, it does nothing since `__init__` methods are created by the library and can be inspected normally.

**This extension is enabled by default.**
