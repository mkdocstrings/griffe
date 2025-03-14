# Setting the right docstring style for every docstring

Griffe attaches the specified docstring style and parsing options to each object in the tree of the package(s) you load. If your package(s) use several docstring styles, some of these objects will have the wrong style attached to them. This is problematic because other Griffe extensions rely on this attached style to parse docstrings and modify them. We plan to alleviate this limitation in the future (see [issue-340](https://github.com/mkdocstrings/griffe/issues/340)), but the most robust thing you can do is to make sure each object has the *right style* attached, as easly as possible, so that other extensions can work without issue.

There are currently two ways to make sure objects have the right docstring style attached as early as possible:

1. Use the [`auto` docstring style](https://mkdocstrings.github.io/griffe/reference/docstrings/#auto-style) (currently only available to sponsors). Griffe will use regular expressions to infer the docstring style used. 100% accuracy is impossible to achieve, so it's possible that you get incorrect styles for some objects.
2. Write and use a custom Griffe extension.

This how-to provides a few extension-based solutions to correctly set docstring styles in your packages. **Just make sure to enable these extensions in first position.**

## Markup comment

Depending on the markup you use in docstrings, you can add a comment that tells Griffe which docstring style to use.

=== "Markdown"

    ```python
    def function():
        """Summary.

        Body.

        <!-- style: google -->
        """
    ```

=== "reStructuredText"

    ```python
    def function():
        """Summary.

        Body.

        .. style: google
        """
    ```

Your Griffe extension can then use regular expressions to search for such comments. For example with Markdown (HTML) comments: 

```python
import re
import griffe


class ApplyDocstringStyle(griffe.Extension):
    def __init__(self, regex: str = "<!-- style: (google|numpy|sphinx) -->") -> None:
         self.regex = re.compile(regex)

    def on_instance(self, *, obj: griffe.Object, **kwargs) -> None:
        if obj.docstring:
            if match := self.regex.search(obj.docstring.value):
                obj.docstring.parser = match.group(1)
```

## Python comment

You could also decide to add a trailing comment to your docstrings to indicate which style to use.

```python
def function():
    """Summary.

    Body.
    """  # style: google
```

Your extension can then pick up this comment to assign the right style:

```python
import re
import griffe


class ApplyDocstringStyle(griffe.Extension):
    def __init__(self, regex: str = ".*# style: (google|numpy|sphinx)$") -> None:
         self.regex = re.compile(regex)

    def on_instance(self, *, obj: griffe.Object, **kwargs) -> None:
        if obj.docstring:
            if match := self.regex.search(obj.docstring.source):
                obj.docstring.parser = match.group(1)
```

## Explicit configuration

Finally, you could decide to map a list of objects to the docstring style they should use. Your extension can either accept options, or it could hard-code that list:

```python
import griffe
from fnmatch import fnmatch

class ApplyDocstringStyle(griffe.Extension):
    def __init__(self, config: dict[str, str]):
        self.instances = {}
        self.globs = {}
        for key, value in config.items():
            if "*" in key:
                self.globs[key] = value
            else:
                self.instances[key] = value

    def on_instance(self, *, obj: griffe.Object, **kwargs) -> None:
        if obj.path in self.instances:
            if obj.docstring:
                obj.docsring.parser = self.instances[obj.path]
         else:
             for pattern, style in self.globs:
                 if fnmatch(obj.path, pattern):
                     if obj.docstring:
                         obj.docstring.parser = style
```

Example configuration in MkDocs:

```yaml
plugins:
- mkdocstrings:
    handlers:
      python:
        options:
          extensions:
          - your_griffe_extension.py:
              config:                
                path.to.obj1: google
                path.to.obj2: numpy
                path.to.obj3.*: sphinx
                path.to.obj4*: google
```

The benefit of this last solution is that it works for code you don't have control over. An alternative solution is to use the [griffe-autodocstringstyle extension](https://mkdocstrings.github.io/griffe/extensions/official/autodocstringstyle/) (sponsors only), which automatically assigns the `auto` style to all objects coming from sources found in a virtual environment.
