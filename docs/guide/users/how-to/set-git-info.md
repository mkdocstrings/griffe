# Set Git information and source link on objects

Griffe tries to set [source information][source-information] on each package it loads. Sometimes it won't be able to find such information, or to find the correct information. In this case, you can programmatically set the right information with a Griffe extension. This will let you fix or customize the source links for many objects at once or for specific objects.

## Git information on whole packages

In this example we see how to set the Git information for whole packages. This will affect every object in these packages, and therefore the source link for each object.

Start by creating an extensions module (a simple Python file) somewhere in your repository, if you don't already have one. Within it, create an extension class:

```python
import griffe


class GitInfo(griffe.Extension):
    """An extension to set the right Git information."""
```

Next we hook onto the `on_package` event to override the `git_info` attribute of the packages we are interested into.

```python
from pathlib import Path
from typing import Any

import griffe


class GitInfo(griffe.Extension):
    """An extension to set the right Git information."""

    def on_package(self, *, pkg: griffe.Module, **kwargs: Any) -> None:
        if pkg.name == "my_package_name":
            pkg.git_info = griffe.GitInfo(
                repository=Path("/path/to/this/package/local/repository"),
                service="forgejo",
                remote_url="https://myhostedforge.mydomain.com/myaccount/myproject",
                commit_hash="77f928aeab857cb45564462a4f849c2df2cca99a",
            )
```

Here we hardcode the commit hash, but ideally we would obtain it by running a Git command in a subprocess, or any other way that gives a relevant commit hash.

```python
import subprocess

process = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"], text=True, capture_output=True)
commit_hash = process.stdout.strip()
```

We could also reuse properties that Griffe found:

```python
# Here we reuse `repository` and `commit_hash` while overriding only `service` and `remote_url`.
pkg.git_info = griffe.GitInfo(
    repository=pkg.git_info.repository,
    service="forgejo",
    remote_url="https://myhostedforge.mydomain.com/myaccount/myproject",
    commit_hash=pkg.git_info.commit_hash,
)

# We could also mutate the original `GitInfo` object:
pkg.git_info.service = "forgejo"
```

Now, with this extension enabled (see [Using extensions][using-extensions]), every object source link in our `my_package_name` package will be based on this Git information. For example, the source link for `my_package_name.my_function` would be something like `https://myhostedforge.mydomain.com/myaccount/myproject/src/commit/77f928aeab857cb45564462a4f849c2df2cca99a/src/my_package_name/__init__.py#L35-L48`.

## Source links on specific objects

Let say you expose Python objects in your API that are compiled from other sources (C extension, Pyo3 code, etc.). Let say you also know the filepath and line numbers for each of these compiled objects. With this information, you could fix the source link for these compiled objects so that they point to the actual sources, and not to the final modules, where the line numbers would be incorrect (or to nowhere since we wouldn't have line numbers in the first place).

Start by creating an extensions module (a simple Python file) somewhere in your repository, if you don't already have one. Within it, create an extension class:

```python
import griffe


class SourceLinks(griffe.Extension):
    """An extension to set the right source links."""
```

Next we hook onto the `on_object` event to override the `source_link` attribute of the objects we are interested into.

```python
from pathlib import Path
from typing import Any

import griffe


class SourceLinks(griffe.Extension):
    """An extension to set the right source links."""

    def on_object(self, *, obj: griffe.Object, **kwargs: Any) -> None:
        if obj.path == "my_package_name.my_function":
            obj.source_link = "https://myhostedforge.mydomain.com/myaccount/myproject/src/commit/77f928aeab857cb45564462a4f849c2df2cca99a/src/lib.rs#L35-L48"
        # Handle any other object you want.
        elif ...:
            ...
```

Here we hardcode the link, but we can also reuse the Git information of the package to just correct the filepath and line numbers:

```python
from pathlib import Path
from typing import Any

import griffe


class SourceLinks(griffe.Extension):
    """An extension to set the right source links."""

    def on_object(self, *, obj: griffe.Object, **kwargs: Any) -> None:
        if obj.path == "my_package_name.my_function":
            obj.source_link = obj.git_info.get_source_link(
                filepath="src/lib.rs",
                lineno=35,
                endlineno=48,
            )
        # Handle any other object you want.
        elif ...:
            ...
```
