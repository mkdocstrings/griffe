# Inspecting specific objects

Griffe by default parses and visits your code (static analysis) instead of importing it and inspecting objects in memory (dynamic analysis). There are various reasons why static analysis is generally a better approach, but sometimes it is insufficient to handle particularly dynamic objects. When this happens and Griffe cannot handle specific objects, you have a few solutions:

1. enable dynamic analysis for the whole package
2. write a Griffe extension that dynamically handles just the problematic objects
3. write a Griffe extension that statically handles the objects

This document will help you achieve point 2.

<!-- TODO:
> NOTE: **Try static analysis first?**
> We always recommend to try and handle things statically, so if you're interested, please check out these other documents:
>
> - link to doc
> - link to doc
-->

Enabling dynamic analysis for whole packages is [not recommended][forcing-dynamic-analysis-not-recommended], but it can be useful to do it once and check the results, to see if our dynamic analysis agent is able to handle your code natively. Whether it is or not is not very important, you will be able to move onto creating an extension that will selectively inspect the relevant objects in any case. It could just be a bit more difficult in the latter case, and if you have trouble writing the extension we invite you to create a [Q&A discussion](https://github.com/mkdocstrings/griffe/discussions/categories/q-a) to get guidance.

---

Start by creating an extensions module (a simple Python file) somewhere in your repository, if you don't already have one. Within it, create an extension class:

```python
import griffe


class InspectSpecificObjects(griffe.Extension):
    """An extension to inspect just a few specific objects."""
```

Make it accept configuration options by declaring an `__init__` method:

```python hl_lines="7-8"
import griffe


class InspectSpecificObjects(griffe.Extension):
    """An extension to inspect just a few specific objects."""

    def __init__(self, objects: list[str]) -> None:
        self.objects = objects
```

Here we choose to store a list of strings, where each string is an object path, like `module.Class.method`. Feel free to store different values to help you filter objects according to your needs. For example, maybe you want to inspect all functions with a given label, in that case you could accept a single string which is the label name. Or you may want to inspect all functions decorated with a specific decorator, etc.

With this `__init__` method, users (or simply yourself) will be able to configure the extension by passing a list of object paths. You could also hard-code everything in the extension if you don't want or need to configure it.

Now that our extension accepts options, we implement its core functionality. We assume that the static analysis agent is able to see the objects we are interested in, and will actually create instances that represent them (Griffe objects). Therefore we hook onto the `on_instance` event, which runs each time a Griffe object is created.

```python hl_lines="10-11"
import griffe


class InspectSpecificObjects(griffe.Extension):
    """An extension to inspect just a few specific objects."""

    def __init__(self, objects: list[str]) -> None:
        self.objects = objects

    def on_instance(self, *, obj: griffe.Object, **kwargs) -> None:
        ...
```

Check out the [available hooks][griffe.Extension] to see if there more appropriate hooks for your needs.

Lets now use our configuration option to decide whether to do something or skip:

```python hl_lines="11-12"
import griffe


class InspectSpecificObjects(griffe.Extension):
    """An extension to inspect just a few specific objects."""

    def __init__(self, objects: list[str]) -> None:
        self.objects = objects

    def on_instance(self, *, obj: griffe.Object, **kwargs) -> None:
        if obj.path not in self.objects:
            return
```

Now we know that only the objects we're interested in will be handled, so lets handle them.

```python hl_lines="3 16-20"
import griffe

logger = griffe.get_logger("griffe_inspect_specific_objects")  # (1)!


class InspectSpecificObjects(griffe.Extension):
    """An extension to inspect just a few specific objects."""

    def __init__(self, objects: list[str]) -> None:
        self.objects = objects

    def on_instance(self, *, obj: griffe.Object, **kwargs) -> None:
        if obj.path not in self.objects:
            return

        try:
            runtime_obj = griffe.dynamic_import(obj.path)
        except ImportError as error:
            logger.warning(f"Could not import {obj.path}: {error}")  # (2)!
            return
```

1. We integrate with Griffe's logging (which also ensures integration with MkDocs' logging) by creating a logger. The name should look like a package name, with underscores.
2. We decide to log the exception as a warning (causing MkDocs builds to fail in `--strict` mode), but you could also log an error, or a debug message.

Now that we have a reference to our runtime object, we can use it to alter the Griffe object.

For example, we could use the runtime object's `__doc__` attribute, which could have been declared dynamically, to fix the Griffe object docstring:

```python hl_lines="22-25"
import griffe

logger = griffe.get_logger("griffe_inspect_specific_objects")


class InspectSpecificObjects(griffe.Extension):
    """An extension to inspect just a few specific objects."""

    def __init__(self, objects: list[str]) -> None:
        self.objects = objects

    def on_instance(self, *, obj: griffe.Object, **kwargs) -> None:
        if obj.path not in self.objects:
            return

        try:
            runtime_obj = griffe.dynamic_import(obj.path)
        except ImportError as error:
            logger.warning(f"Could not import {obj.path}: {error}")
            return

        if obj.docstring:
            obj.docstring.value = runtime_obj.__doc__
        else:
            obj.docstring = griffe.Docstring(runtime_obj.__doc__)
```

Or we could alter the Griffe object parameters in case of functions, which could have been modified by a signature-changing decorator:

```python hl_lines="1 23-27"
import inspect
import griffe

logger = griffe.get_logger("griffe_inspect_specific_objects")


class InspectSpecificObjects(griffe.Extension):
    """An extension to inspect just a few specific objects."""

    def __init__(self, objects: list[str]) -> None:
        self.objects = objects

    def on_instance(self, *, obj: griffe.Object, **kwargs) -> None:
        if obj.path not in self.objects:
            return

        try:
            runtime_obj = griffe.dynamic_import(obj.path)
        except ImportError as error:
            logger.warning(f"Could not import {obj.path}: {error}")
            return

        # Update default values modified by decorator.
        signature = inspect.signature(runtime_obj)
        for param in signature.parameters:
            if param.name in obj.parameters:
                obj.parameters[param.name].default = repr(param.default)
```

We could also entirely replace the Griffe object obtained from static analysis by the same one obtained from dynamic analysis:


```python hl_lines="14-25"
import griffe


class InspectSpecificObjects(griffe.Extension):
    """An extension to inspect just a few specific objects."""

    def __init__(self, objects: list[str]) -> None:
        self.objects = objects

    def on_instance(self, *, obj: griffe.Object, **kwargs) -> None:
        if obj.path not in self.objects:
            return

        inspected_module = griffe.inspect(obj.module.path, filepath=obj.filepath)
        obj.parent.set_member(obj.name, inspected_module[obj.name])  # (1)!
```

1. This assumes the object we're interested in is declared at the module level.
