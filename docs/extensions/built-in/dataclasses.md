# `dataclasses`

The `dataclasses` extension adds support for [dataclasses][] from the standard library. It works both statically and dynamically. When used statically, it re-creates the `__init__` methods and their signatures (as Griffe objects), that would otherwise be created at runtime. When used dynamically, it does nothing since `__init__` methods are created by the library and can be inspected normally.

Example:

```python
from dataclasses import dataclass


@dataclass
class Room:
    uid: int
    name: str
    capacity: int = 10
    available: bool = True
```

With the `dataclasses` extension enabled, the Griffe object for the `Room` class will get an `__init__` method with the following signature:

```python
def __init__(self, uid: int, name: str, capacity: int = 10, available: bool = True) -> None:
    ...
```

Additional metadata like `ClassVar`, the `init` and `kw_only` parameters, or the `KW_ONLY` sentinel are also recognized and will update the `__init__` method signature accordingly.

**This extension is enabled by default.** It is always added last. If you need to give it a higher priority, you can explictly enable it to change its position in the list of extensions (it will run only once):

=== "CLI"
    ```console
    $ griffecli dump -e dataclasses,other my_package
    ```

=== "Python"
    ```python
    import griffe

    my_package = griffelib.load("my_package", extensions=griffelib.load_extensions("dataclasses", "other"))
    ```

=== "mkdocstrings"
    ```yaml title="mkdocs.yml"
    plugins:
    - mkdocstrings:
        handlers:
          python:
            options:
              extensions:
              - dataclasses
              - other
    ```

