# `apidiff`

The `apidiff` extension reads the consolidated history produced by [`griffe diff`](../../guide/users/checking.md#recording-api-history) and injects structured admonitions into parsed docstrings. Documentation renderers can then show notices such as **Added in version 2.0**, **Deprecated in version 3.0**, or **Changed in version 3.1** without adding this information to source docstrings by hand.

Enable it with its default history path, `.apidiff/diff.json`:

=== "CLI"
    ```console
    $ griffe dump -e apidiff my_package
    ```

=== "Python"
    ```python
    import griffe

    extensions = griffe.load_extensions("apidiff")
    my_package = griffe.load("my_package", extensions=extensions)
    ```

=== "mkdocstrings"
    ```yaml title="mkdocs.yml"
    plugins:
    - mkdocstrings:
        handlers:
          python:
            options:
              extensions:
              - apidiff
    ```

Configure another history path with an extension mapping:

```yaml
extensions:
- apidiff:
    path: build/api-history.json
```

The extension adds callouts for additions, deprecations, undeprecations, removals, and every other recorded change. Multiple changes to one object in the same version are grouped. A removed object has no current docstring, so its removal is attached to the nearest parent that still exists.

NOTE: Alias-specific callouts are not injected yet. Griffe aliases currently share their target's docstring, so changing an alias docstring would incorrectly affect the target and its other aliases.

The history file is optional. Enabling the extension before running `griffe diff` is a no-op.
