# Loading APIs

Griffe can load API data from both source code (static analysis) and objects at runtime through introspection (dynamic analysis). Both static and dynamic analysis can be used at the same time: Griffe will first try to find sources, and will fall back to introspection if it cannot find any. When Griffe finds compiled modules within a packages, it uses introspection again to extract API information. There are various options to configure how Griffe loads data, for example to force or disallow dynamic analysis, but first let see the interface.

## The `load` function

The main interface to load API data is Griffe's [`load`][griffe.load] function:

```python
import griffe

my_package = griffe.load("my_package")
```

You can ask to load a specific object rather than a package:

```python
import griffe

my_method = griffe.load("my_package.MyClass.my_method")
```

Griffe will load the whole package anyway, but return the specified object directly, so that you don't have to access it manually. To manually access the object representing the method called `my_method`, you would have used the `my_package` variable instantiated before, like this:

```python
my_method = my_package["MyClass.my_method"]
```

The [Navigating](navigating.md) topic will show you all the ways Griffe objects can be navigated.

Finally, you can even load packages or modules by passing absolute or relative file paths. This is useful when the module or package is not installed within the current Python environment and therefore cannot be found in the default search paths (see [Search paths](#search-paths) below).

```python
import griffe

griffe.load("src/my_package")
griffe.load("some_script.py")
```

In case of ambiguity, you can instruct Griffe to ignore existing relative file paths with `try_relative_paths=False`. For example, when using [the flat layout (in contrast to the src-layout)](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/), your Python package is in the root of the repository.

```tree
./
    my_package/
        __init__.py
    pyproject.toml
```

Here if you ask Griffe to load `my_package`, it will find it as a relative path, in `./my_package`. If you want Griffe to use the version installed in your environment's site packages instead, set `try_relative_path` to false:

```python
import griffe

my_installed_package = griffe.load("my_package", try_relative_path=False)
```

## The `GriffeLoader` class

The [`load`][griffe.load] function is a shortcut for instantiating the [`GriffeLoader`][griffe.GriffeLoader] class and calling its [`load`][griffe.GriffeLoader.load] method. Calling the [`load`][griffe.load] function multiple times will instantiate a new Griffe loader each time. If you care about efficiency, it is better to instantiate the loader yourself and use its `load` method:

```python
import griffe

loader = GriffeLoader()
my_package = loader.load("my_package")
my_other_package = loader.load("my_other_package")
```

Keeping a reference to the loader will reduce the number of IO operations on the file-system, as the contents of the directories that the loader searches into will be cached (only the lists of files and directories will be cached, not the file contents).

Reusing the same loader will also help resolving aliases across different packages. See [Alias resolution](#alias-resolution) below.

## Search paths

To specify in which directories Griffe should search for packages and modules, you can use the `search_paths` parameter on both the [`load` function][griffe.load] and the [`GriffeLoader` class][griffe.GriffeLoader].

=== "`load`"
    ```python
    import griffe

    my_package = griffe.load("my_package", search_paths=["src"])
    ```

=== "`GriffeLoader`"
    ```python
    import griffe

    loader = GriffeLoader(search_paths=["src"])
    my_package = loader.load("my_package")
    ```

By default it will search in the paths found in [`sys.path`][sys.path], which can be influenced through the [`PYTHONPATH`][PYTHONPATH] environment variable.

If Griffe cannot find sources for the specified object in the given search paths, it will try to import the specified object and use dynamic analysis on it (introspection). See [Forcing dynamic analysis](#forcing-dynamic-analysis) and [Disallowing dynamic analysis](#disallowing-dynamic-analysis).

## Forcing dynamic analysis

Griffe always tries first to find sources for the specified object. Then, unless told otherwise, it uses static analysis to load API data, i.e. it parses the sources and visits the AST (Abstract Syntax Tree) to extract information. If for some reason you want Griffe to use dynamic analysis instead (importing and inspecting runtime objects), you can pass the `force_inspection=True` argument:

```python
import griffe

my_package = griffe.load("my_package", force_inspection=True)
```

Forcing inspection can be useful when your code is highly dynamic, and static analysis has trouble keeping up.

**However we don't recommend forcing inspection**, for a few reasons:

- dynamic analysis requires that you either mock your dependencies, or install them
- dynamic analysis will **execute code**, possibly ***arbitrary code*** if you import third-party dependencies, putting you at risk
- dynamic analysis will potentially consume more resources (CPU, RAM) since it executes code
- dynamic analysis will sometimes give you less precise or incomplete information
- it's possible to write Griffe extensions that will *statically handle* the highly dynamic parts of your code (like custom decorators) that Griffe doesn't understand by default
- if really needed, it's possible to handle only a subset of objects with dynamic analysis, while the rest is loaded with static analysis, again thanks to Griffe extensions

The [Extending](extending.md) topic will explain how to write and use extensions for Griffe.

## Disallowing dynamic analysis

If you want to be careful about what gets executed in the current Python process, you can choose to disallow dynamic analysis by passing the `allow_inspection=False` argument. If Griffe cannot find sources for a package, it will not try to import it and will instead fail with a `ModuleNotFoundError` directly.

```python
import griffe

# Here Griffe will fall back on dynamic analysis and import `itertools`.
griffe.load("itertools")

# While here it will raise `ModuleNotFoundError`.
griffe.load("itertools", allow_inspection=False)
```

## Alias resolution

>? QUESTION: **What's that?**  
> In Griffe, indirections to objects are called *aliases*. These indirections, or aliases, represent two kinds of objects: imported objects and inherited objects. Indeed, an imported object is "aliased" in the module that imports it, while its true location is in the module it was imported from. Similarly, a method inherited from a parent class is "aliased" in the subclass, while its true location is in the parent class.
>
> The name "alias" comes from the fact that imported objects can be aliased under a different name: `from X import A as B`. In the case of inherited members, this doesn't really apply, but we reuse the concept for conciseness.
>
> An [`Alias`][griffe.Alias] instance is therefore a pointer to another object. It has its own name, parent, line numbers, and stores the path to the target object. Thanks to this path, we can access the actual target object and all its metadata, such as name, parent, line numbers, docstring, etc.. Obtaining a reference to the target object is what we call "alias resolution".
>
> **To summarize, alias resolution is a post-process task that resolves imports after loading everything.**

To resolve an alias, i.e. obtain a reference to the object it targets, we have to wait for this object to be loaded. Indeed, during analysis, objects are loaded in breadth-first order (in the object hierarchy, highest objects are loaded first, deepest ones are loaded last), so when we encounter an imported object, we often haven't loaded this object yet.

Once a whole package is loaded, we are ready to try and resolve all aliases. But we don't *have* to resolve them. First, because the user might not need aliases to be resolved, and second, because each alias can be resolved individually and transparently when accessing its target object properties.

Therefore, alias resolution is optional and enabled with the `resolve_aliases` parameter.

Lets take an example.

```tree title="File layout"
./
    my_package/
        __init__.py
        my_module.py
```

```python title="my_package/__init__.py"
from my_package.my_module import my_function
```

```python title="my_package/my_module.py"
def my_function():
    print("hello")
```

When loading this package, `my_package.my_function` will be an alias pointing at `my_package.my_module.my_function`:

```python
import griffe

my_package = griffe.load("my_package")
my_package["my_function"].resolved  # False
```

```python
import griffe

my_package = griffe.load("my_package", resolve_aliases=True)
my_package["my_function"].resolved  # True
my_package["my_function"].target is my_package["my_module.my_function"]  # True
```

The [Navigating](navigating.md) topic will tell you more about aliases and how they behave.

### Modules collection

In the first section of this page, we briefly mentioned that Griffe always loads the entire package containing the object you requested. One of the reason it always load entire packages and not just single, isolated objects, is that alias resolution requires all objects of a package to be loaded. Which means that if an alias points to an object that is part of *another* package, it can only be resolved if the *other* package is *also loaded*. For example:

```tree title="File layout"
./
    package1/
        __init__.py
    package2/
        __init__.py
```

```python title="package1/__init__.py"
X = 0
```

```python title="package2/__init__.py"
from package1 import X
```

```pycon
>>> import griffe
>>> package2 = griffe.load("package2", resolve_aliases=True)
>>> package2["X"].target_path
'package1.X'
>>> package2["X"].resolved
False
>>> package2["X"].target
Traceback (most recent call last):
  File "_griffe/dataclasses.py", line 1375, in _resolve_target
    resolved = self.modules_collection.get_member(self.target_path)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "_griffe/mixins.py", line 84, in get_member
    return self.members[parts[0]].get_member(parts[1:])  # type: ignore[attr-defined]
           ~~~~~~~~~~~~^^^^^^^^^^
KeyError: 'package1'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "_griffe/dataclasses.py", line 1310, in target
    self.resolve_target()
  File "_griffe/dataclasses.py", line 1369, in resolve_target
    self._resolve_target()
  File "_griffe/dataclasses.py", line 1377, in _resolve_target
    raise AliasResolutionError(self) from error
_griffe.exceptions.AliasResolutionError: Could not resolve alias package2.X pointing at package1.X (in package2/__init__.py:1)
```

As you can see in the interpreter session above, Griffe did not resolve the `X` alias. When we tried to access its target object anyway, it failed with a `KeyError`, which was raised again as an [`AliasResolutionError`][griffe.AliasResolutionError].

Lets try again, but this time by loading both packages.

```pycon
>>> import griffe
>>> package1 = griffe.load("package1")  # nothing to resolve
>>> package2 = griffe.load("package2", resolve_aliases=True)
>>> package2["X"].target_path
'package1.X'
>>> package2["X"].resolved
False  # Hmm?
>>> package2["X"].target
Traceback (most recent call last):
...
_griffe.exceptions.AliasResolutionError: Could not resolve alias package2.X pointing at package1.X (in package2/__init__.py:1)
```

The same exception again? What happened here? We loaded both packages, but Griffe still failed to resolve the alias. That is expected; here is the explanation.

If you look closely at the first exception traceback, you will see that Griffe searched the target path in `self.modules_collection`. So what is this modules collection?

Each instance of [`GriffeLoader`][griffe.GriffeLoader] holds a reference to an instance of [`ModulesCollection`][griffe.ModulesCollection]. If you don't create such a collection manually to pass it to the loader, it will instantiate one itself. All objects loaded with this loader are added to this very modules collection, and gain a reference to it.

Since the [`load` function][griffe.load] is just a shortcut for creating a loader and calling its [`load` method][griffe.GriffeLoader.load], when we called `griffe.load(...)` twice, it actually created two distinct collections of modules. When Griffe tried to resolve aliases of `package2`, it looked for `package1` in `package2`'s collection, and couldn't find it. Indeed, `package1` was in another modules collection.

Therefore, to resolve aliases *across different packages*, these packages must be loaded within the same modules collection. In order to do that, you have a few options:

- instantiate a single loader, and use it to load both packages
- create your own modules collection, and pass it to the [`load` function][griffe.load] each time you call it
- create your own modules collection, and pass it to the different instances of [`GriffeLoader`][griffe.GriffeLoader] you create

=== "Same loader"
    ```pycon
    >>> import griffe
    >>> loader = griffe.GriffeLoader()
    >>> package1 = loader.load("package1")
    >>> package2 = loader.load("package2")
    >>> loader.resolve_aliases()
    >>> package2["X"].resolved
    True
    >>> package2["X"].target
    Attribute('X', lineno=1, endlineno=1)
    ```

=== "Same collection with `load`"
    ```pycon
    >>> import griffe
    >>> collection = griffe.ModulesCollection()
    >>> package1 = griffe.load("package1", modules_collection=collection)
    >>> package2 = griffe.load("package2", modules_collection=collection, resolve_aliases=True)
    >>> package2["X"].resolved
    True
    >>> package2["X"].target
    Attribute('X', lineno=1, endlineno=1)
    ```

=== "Same collection, different loaders"
    ```pycon
    >>> import griffe
    >>> collection = griffe.ModulesCollection()
    >>> loader1 = griffe.GriffeLoader(modules_collection=collection, ...)
    >>> package1 = loader1.load("package1")
    >>> loader2 = griffe.GriffeLoader(modules_collection=collection, ...)  # different parameters
    >>> package2 = loader2.load("package2")
    >>> package2["X"].resolved
    True
    >>> package2["X"].target
    Attribute('X', lineno=1, endlineno=1)
    ```

There is no preferred way, it depends on whether you need to instantiate different loaders with different parameters (search paths for example) while keeping every loaded module in the same collection, or if a single loader is enough, or if you explicitly need a reference to the collection, etc..

### Loading external packages automatically

By default, when resolving aliases, Griffe loaders will not be able to resolve aliases pointing at objects from "external" packages. By external, we mean that these packages are external to the current modules collection: they are not loaded. But sometimes users don't know in advance which packages need to be loaded in order to resolve aliases (and compute class inheritance). For these cases, Griffe loaders can be instructed to automatically load external packages. If we take the previous example again:

```python
import griffe

package2 = griffe.load("package2", resolve_aliases=True, resolve_external=True)
print(package2["X"].target.name)  # X
```

Here Griffe automatically loaded `package1` while resolving aliases, even though we didn't explicitly load it ourselves.

While automatically resolving aliases pointing at external packages can be convenient, we advise cautiousness: this can trigger the loading of *a lot* of external packages, *recursively*.

One special case that we must mention is that Griffe will by default automatically load *private sibling packages*. For example, when resolving aliases for the `ast` module, Griffe will automatically try and load `_ast` too (if dynamic analysis is allowed, since this is a builtin module), even without `resolve_external=True`. If you want to prevent this behavior, you can pass `resolve_external=False` (it is `None` by default).

## Next steps

Now that the API is loaded, you can start [navigating it](navigating.md), [serializing it](serializing.md) or [checking for API breaking changes](checking.md). If you find out that the API data is incorrect or incomplete, you might want to learn how to [extend it](extending.md).
