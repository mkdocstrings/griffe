# Public APIs

## What is a public API?

An API (Application Programming Interface) in the interface with which developers interact with your software. In the Python world, the API of your Python library is the set of modules, classes, functions and other attributes made available to your users. For example, users can do `from your_library import this_function`: `this_function` is part of the API of `your_library`.

Often times, when you develop a library, you create functions, classes, etc. that are only useful internally: they are not supposed to be used by your users. Python does not provide easy or standard ways to actually *prevent* users from using internal objects, so, to distinguish public objects from internal objects, we usually rely on conventions, such as prefixing internal objects' names with an underscore, for example `def _internal_function(): ...`, to mark them as "internal".

Prefixing an object's name with an underscore still does not prevent users from importing and using this object, but it *informs* them that they are not supposed to import and use it, and that this object might change or even disappear in the future, *without notice*.

On the other hand, public objects are supposed to stay compatible with previous versions of your library for at least a definite amount of time, to prevent downstream code from breaking. Any change that could break downstream code is supposed to be communicated *before* it is actually released. Maintainers of the library usually allow a period of time where the public object can still be used as before, but will emit deprecation warnings when doing so, hinting users that they should upgrade their use of the object (or use another object that will replace it). This period of time is usually called a deprecation period.

So, how do we mark an object as public? How do we inform our users which objects can safely be used, and which one are subject to unnotified changes? Usually, we rely again on the underscore prefix convention: if an object isn't prefixed with an underscore, it means that it is public. But essentially, your public API is what you say it is. If you clearly document that a single function of your package is public, and that all others are subject to unnotified changes and whose usage by users is not supported, then your public API is composed of this single function, and nothing else. **Public APIs are a matter of communication.** Concretely, it's about deciding what parts of your code base are public, and communicating that clearly.

Some components are obviously considered for the public API of a Python package:

- the module layout
- functions and their signature
- classes (their inheritance), their methods and signatures
- the rest of the module or class attributes, their types and values

Other components *should* be considered for the public API but are often forgotten:

- CLI options: see [The CLI is API too](#the-cli-is-api-too) section
- logger names: users might rely on them to filter logs (see [Logger names](#logger-names))
- exceptions raised: users definitely rely on them to catch errors

Other components *could* be considered for the public API, but usually require too much maintenance:

- logging messages: users might rely on them to grep the logs
- exception messages: users might rely on them for various things

Besides, logging and exception messages simply cannot allow deprecation periods where both old and new messages are emitted. Maintainers could however consider adding unique, short codes to message for more robust consumption.

> GRIFFE: **Our recommendation — Communicate your public API, verify what you can.**  
> Take the time to learn about and use ways to declare, communicate and deprecate your public API. Your users will have an easier time using your library. On the maintenance side, you won't get bug reports for uses that are not supported, or you will be able to quickly close them by pointing at the documentation explaining what your public API is, or why something was deprecated, for how long, and how to upgrade.
>
> Automate verifications around your public API with tools like Griffe. Currently Griffe doesn't support checking CLI configuration options, logger names or raised exceptions. If you have the capacity to, verify these manually before each release. [Griffe checks](../checking.md) and [API rules enforcement](#ensuring-api-rules) are a very good starting point.

## Conventions

Python does not provide any standard way to declare public APIs. However we do have official recommendations and a few conventions.

### Underscore prefix

In the Python ecosystem we very often prefix objects with an underscore to mark them as internal, or private. Objects that are not prefixed are then implicitly considered public. For example:

```python
def public_function():
    ...

def _internal_function():
    ...
```

The exception to this rule is that imported objects are not considered public. For example:

```python
from elsewhere import something
```

Even though `something` doesn't start with an underscore, it was imported so it is not considered public.

### `__all__` list

There is another convention that lets you do the opposite: explicitly mark objects as public. This convention uses the `__all__` module-level attribute, which is a list of strings containing the names of the public objects.

```python title="package/module.py"
__all__ [
    "this_function",
    "ThisClass",
]

def this_function():
    ...

def this_other_function():
    ...

class ThisClass:
    ...

class ThisOtherClass:
    ...
```

Here, even though `this_other_function` and `ThisOtherClass` are *not* prefixed with underscores, they are not considered public, because we explicitly and only marked `this_function` and `ThisClass` as public.

Declaring `__all__` has another beneficial effect: it affects wildcard imports. When your users use wildcard imports to import things from one of your module, Python will only import the objects that are listed in `__all__`. Without `__all__`, it would import all objects that are not prefixed with an underscore, *including objects already imported from elsewhere*. This can cause serious namespace pollution, and even slow down Python code when wildcard imports are chained. [We actually recommend avoiding wildcard imports](python-code.md#avoid-wildcard-imports).

By declaring `__all__`, your public API becomes explicit, and explicit is better than implicit. But `__all__` only works for module-level objects. Within classes, you will still have to rely on the underscore prefix convention to mark methods or attributes as internal/private.

```python
class Thing:
    def public_method(self):
        ...

    def _internal_method(self):
        ...
```

### Redundant aliases

When you expose your public API in `__init__` modules by importing most object from the underlying modules, it can be a bit tedious to import everything, and then list everything again in the `__all__` list attribute. For this reason, another convention emerged where objects imported and aliased with the same name are considered public.

```python title="my_package/__init__.py"
from elsewhere import something as something
from my_package._internal_module import Thing as Thing
```

Here `Thing` and `something` are considered public even though they were imported. If `__all__` was defined, it would take precedence and redundant aliases wouldn't apply.

### Wildcard imports

Same as for redundant aliases, this convention says that all objects imported thanks to wildcard imports are public. This can again be useful in `__init__` modules where you expose lots of objects declared in submodules.

```python title="my_package/__init__.py"
from my_package._internal_module1 import *
from my_package._internal_module2 import *
```

Note that the wildcard imports logic stays the same, and imports either all objects that do not start with an underscore (imported objects included!), or all objects listed in `__all__` if it is defined. It doesn't care about other conventions such as redundant aliases, or the wildcard imports convention itself.

---

> GRIFFE: **Our recommendation — Use the underscore prefix and `__all__` conventions.**  
> Use both the underscore prefix convention for consistent naming at module and class levels, and the `__all__` convention for declaring your public API. We do not recommend using the redundant aliases convention, because it doesn't provide any information at runtime. We do not recommend the wildcard import convention either, for the same reason and [for additional reasons mentioned here](python-code.md#avoid-wildcard-imports). We still provide the [`griffe-public-redundant-aliases`](https://mkdocstrings.github.io/griffe-public-redundant-aliases/) and [`griffe-public-wildcard-imports`](https://mkdocstrings.github.io/griffe-public-wildcard-imports/) extensions for those who would still like to rely on these conventions.
>
> Our recommendation matches [PEP 8](https://peps.python.org/pep-0008/#public-and-internal-interfaces):
>
> > To better support introspection, modules should explicitly declare the names in their public API using the `__all__` attribute. Setting `__all__` to an empty list indicates that the module has no public API.
>
> > Even with `__all__` set appropriately, internal interfaces (packages, modules, classes, functions, attributes or other names) should still be prefixed with a single leading underscore.

> TIP: **Concatenating `__all__` for easier maintenance of `__init__` modules.**  
> If you worry about maintenance of your `__init__` modules, know that you can very well concatenate `__all__` lists from submodules into the current one:
>
> ```tree
> my_package/
>     __init__.py
>     module.py
>     subpackage1/
>         __init__.py
>         _module1a.py
>     subpackage2/
>         __init__.py
>         _module2a.py
> ```
>
> ```python title="my_package/subpackage1/__init__.py"
> from my_package.subpackage1.module1a import this1a, that1a
>
> __all__ = ["this1a", "that1a"]
> ```
>
> ```python title="my_package/subpackage2/__init__.py"
> from my_package.subpackage2.module2a import this2a, that2a
>
> __all__ = ["this2a", "that2a"]
> ```
>
> ```python title="my_package/__init__.py"
> from my_package.module import this
> from my_package.subpackage1 import this1a, that1a, __all__ as subpackage1_all
> from my_package.subpackage2 import this2a, that2a, __all__ as subpackage2_all
>
> __all__ = ["this", *subpackage1_all, *subpackage2_all]
>
> # Griffe supports the `+` and `+=` operators too:
> # __all__ = ["this"] + subpackage1_all + subpackage2_all
> # __all__ = ["this"]; __all__ += subpackage1_all; __all__ += subpackage2_all 
> ```
>
> However we would argue that `this1a`, `that1a`, `this2a` and `that2a` should not be exposed publicly in more than one location. See our section on [unique names and public locations](#unique-names-and-public-locations).

## Module layout

We usually split the code of our packages into different modules. The code can be split according to domains, types of objects, logic, etc.: we don't have any recommendation on that. However, your package layout is part of your API, so it should be taken into account when deciding what you expose as your public API.

Most of the time, packages implicitly expose their module layout in their public API. Indeed, when you start a new project, you create new modules but don't immediately think about making them private. Then the project grows organically, you add more modules, and users start actually relying on their layout, importing specific objects from specific modules. Now when you want to move objects around, to reorganize your layout, you introduce breaking changes. So you have to create a deprecation period where objects that moved around are still importable in the old locations, but emit deprecation warnings. A module-level `__getattr__` function is commonly used for that.

```python title="package/old_module.py"
import warnings
from typing import Any

def __getattr__(name: str) -> Any:
    if name == "my_object":
        warnings.warn(
            "Importing `my_object` from `old_module` is deprecated, import it from `new_module` instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        from package.new_module import my_object

        return my_object

    raise AttributeError(f"module 'old_module' has no attribute '{name}'")
```

Such changes sometimes go unnoticed before the breaking change is released, because users don't enable deprecation warnings. These changes can also be confusing to users when they do notice the warnings: maybe they don't use the deprecated import themselves, and are not sure where to report the deprecated use. These changes also require time to upgrade, and time to maintain.

What if we could make this easier?

By hiding your module layout from your public API, you're removing all these pain points at once. Any object can freely move around without ever impacting users. Maintainers do not need to set deprecation periods where old and new uses are supported, or bump the major part of their semantic version when they stop supporting the old use. Hiding the module layout also removes the ambiguity of whether a submodule is considered public or not: [PEP 8](https://peps.python.org/pep-0008/#public-and-internal-interfaces) doesn't mention anything about it, and it doesn't look like the `__all__` convention expects developers to list their submodules too. In the end it looks like submodules are only subject to the underscore prefix convention.

So, how do we hide the module layout from the public API?

The most common way to hide the module layout is to make all your modules private, by prefixing their name with an underscore:

```tree
my_package/
    __init__.py
    _combat.py
    _exploration.py
    _sorcery.py
```

Then, you expose public objects in the top-level `__init__` module thanks to its `__all__` attribute:

```python title="my_package/__init__.py"
from my_package._combat import Combat
from my_package._exploration import navigate
from my_package._sorcery import cast_spell

__all__ [
    "Combat",
    "navigate",
    "cast_spell",
]
```

Now, if you want to move `cast_spell` into the `_combat` module, you can do so without impacting users. You can even rename your modules. All you have to do when doing so is update your top-level `__init__` module to import the objects from the right locations.

If you have more than one layer of submodules, you don't have to make the next layer private: only the first one is enough, as it informs users that they shouldn't import from this layer anyway:

```tree
my_package/
    __init__.py
    _combat.py
    _exploration.py
    _sorcery/
        __init__.py
        dark.py
        light.py
```

If you don't want to bother prefixing every module with an underscore, you could go one step further and do one of these two things:

- move everything into an `_internal` directory:

    ```tree
    my_package/
        __init__.py
        _internal/
            __init__.py
            combat.py
            exploration.py
            sorcery/
                __init__.py
                dark.py
                light.py
    ```

- or move everything into a private package:

    ```tree
    my_package/
        __init__.py
    _my_package/
        __init__.py
        combat.py
        exploration.py
        sorcery/
            __init__.py
            dark.py
            light.py
    ```

Whatever *hidden* layout you choose (private modules, internals, private package), it is not very important, as you will be able to switch from one to another easily. In Griffe we chose to experiment and go with the private package approach. This highlighted a few shortcomings that we were able to address in both Griffe and mkdocstrings-python, so we are happy with the result.

WARNING: **Top-level-only exposition doesn't play well with large packages.**  
The *fully* hidden layout plays well with small to medium projects. If you maintain a large project, it can become very impractical for both you and your users to expose every single object in the top-level `__init__` module. For large projects, it therefore makes sense to keep at least one or two additional public layers in your module layout. Sometimes packages also implement many variations of the same abstract class, using the same name in many different modules: in these cases, the modules are effective namespaces that could be kept in the public API.

GRIFFE: **Our recommendation — Hide your module layout early.**  
Start hiding your module layout early! It is much easier to (partially) expose the layout later than to hide it after your users started relying on it. It will also make code reorganizations much easier.

## Unique names and public locations

Whether or not you are planning to hide your module layout, as recommended in the previous section, one thing that will help both you and your users is making sure your object names are unique across your code base. Having unique names ensures that you can expose everything at the top-level module of your package without having to alias objects (using `from ... import x as y`). It will also ensure that your users don't end up importing multiple different objects with the same name, again having to alias them. Finally, it forces you to use meaningful names for your objects, names that don't need the context of the above namespaces (generally modules) to understand what they mean. For example, in Griffe we previously exposed `griffe.docstrings.utils.warning`. Exposing `warning` at the top-level made it very vague: what does it do? So we renamed it `docstring_warning`, which is much clearer.

Ensuring unique names across a code base is sometimes not feasible, or not desirable; in this case, try to use namespacing while still hiding the module layout the best you can.

In accordance with our recommendation on module layouts, it is also useful to ensure that a single public object is exposed in a single location. Ensuring unique public location for each object removes any ambiguity on the user side as to where to import the object from. It also helps documentation generators that try to cross-reference objects: with several locations, they cannot know for sure which one is the best to reference (which path is best to use and display in the generated documentation). With a fully hidden layout, all objects are *only* exposed in the top-level module, so there is no ambiguity. With partially hidden layouts, or completely public layouts, make sure to declare your public API so that each object is only exposed in a single location. Example:

```tree
my_package/
    __init__.py
    module.py
```

=== "Multiple locations, bad"
    Here the `Hello` class is exposed in both `my_package.module` and `my_package`.

    ```python title="my_package/module.py"
    __all__ ["Hello"]

    class Hello:
        ...
    ```

    ```python title="my_package/__init__"
    from my_package.module import Hello

    __all__ = ["Hello"]
    ```

=== "Single location, good"
    Here the `Hello` class is only exposed in `my_package.module`.

    ```python title="my_package/module.py"
    __all__ ["Hello"]

    class Hello:
        ...
    ```

    ```python title="my_package/__init__"
    # Nothing to see here.
    ```

    If you wanted to expose it in the top-level `__init__` module instead, then you should hide your module layout by making `module.py` private, renaming it `_module.py`, or using other hiding techniques such as described in the [Module layout](#module-layout) section.

=== "Single location (top-level), good"
    Here the `Hello` class is only exposed in `package`.

    ```python title="my_package/module.py"
    __all__ = []

    class Hello:
        ...
    ```

    ```python title="my_package/__init__"
    from my_package.module import Hello

    __all__ = ["Hello"]
    ```

    It feels weird to "unpublicize" the `Hello` class in `my_package.module` by declaring an empty `__all__`, so maybe the module should be made private instead: `my_package/_module.py`. See other hiding techniques in the [Module layout](#module-layout) section.

GRIFFE: **Our recommendation — Expose public objects in single locations, use meaningful names.**  
We recommend making sure that each public object is exposed in a single location. Ensuring unique names might be more tricky depending on the code base, so we recommend ensuring meaningful names at least, not requiring the context of modules above to understand what the objects are for.

## Logger names

The documentation of the standard `logging` library recommends to use `__name__` as logger name when obtaining a logger with `logging.getLogger()`, *unless we have a specific reason for not doing that*. Unfortunately, no examples of such specific reasons are given. So let us give one.

Using `__name__` as logger names means that your loggers have the same name as your module paths. For example, the module `package/module.py`, whose path and `__name__` value are `package.module`, will have a logger with the same name, i.e. `package.module`. If your module layout is public, that's fine: renaming the module or moving it around is already a breaking change that you must document.

However if your module layout is hidden, or if this particular module is private, then even though renaming it or moving it around is *not* breaking change, the change of name of its logger *is*. Indeed, by renaming your module (or moving it), you changed its `__name__` value, and therefore you changed its logger name.

Now, users that were relying on this name (for example to silence WARNING-level logs and below coming from this particular module) will see their logic break without any error and without any deprecation warning.

```python
# For example, the following would have zero effect if `_module` was renamed `_other_module`.
package_module_logger = logging.getLogger("package._module")
package_module_logger.setLevel(logging.ERROR)
```

Could we emit a deprecation warning when users obtain the logger with the old name? Unfortunately, there is no standard way to do that. This would require patching `logging.getLogger`, which means it would only work when users actually use this method, in a Python interpreter, and not for all the other ways logging can be configured (configuration files, configuration dicts, etc.).

Since it is essentially impossible to deprecate a logger name, we recommend to avoid using `__name__` as logger name, at the very least in private modules.

GRIFFE: **Our recommendation — Use a single logger.**  
Absolutely avoid using `__name__` as logger name in private modules. If your module layout is hidden, or does not matter for logging purposes, just use the same logger everywhere by using your package name as logger name. Example: `logger = logging.getLogger("griffe")`. Show your users how to temporarily alter your global logger (typically with context managers) so that altering subloggers becomes unnecessary. Maybe even provide the utilities to do that.

## Documentation

Obviously, your public API should be documented. Each object should have a docstring that explains why the object is useful and how it is used. More on that in our [docstrings recommendations](docstrings.md). Docstrings work well for offline documentation; we recommend exposing your public API online too, for example with [MkDocs](https://www.mkdocs.org/) and [mkdocstrings' Python handler](https://mkdocstrings.github.io/python/), or with other SSGs (Static Site Generators). Prefer a tool that is able to create a [Sphinx-like](https://sphobjinv.readthedocs.io/en/stable/syntax.html) inventory of objects (an `objects.inv` file) that will allow other projects to easily cross-reference your API from their own documentation. Make sure each and every object of your public API is documented in your web docs and therefore added to the objects inventory (and maybe that nothing else is added to this inventory as "public API").

> GRIFFE: **Our recommendation — Document your public API extensively.**  
> Write docstrings for each and every object of your public API. Deploy online documentation where each object is documented and added to an object inventory that can be consumed by third-party projects. If you find yourself reluctant to document a public object, it means that this object should maybe be internal instead.
>
> Our documentation framework of choice is of course [MkDocs](https://www.mkdocs.org) combined with our [mkdocstrings](https://mkdocstrings.github.io/) plugin.

## Ensuring API rules

If you already follow some of these recommendations, or if you decide to start following them, it might be a good idea to make sure that these recommendations keep being followed as your code base evolves. The intent of these recommendations, or "rules", can be captured in tests relatively easily thanks to Griffe.

We invite you to check out our own test file: [`test_internals.py`](https://github.com/mkdocstrings/griffe/blob/main/tests/test_internals.py). This test module asserts several things:

- all public objects are exposed in the top-level `griffe` module
- all public objects have unique names
- all public objects have single locations
- all public objects are added to the inventory (which means they are documented in our API docs)
- no private object is added to the inventory

GRIFFE: **Our recommendation — Test your API declaration early.**  
The sooner you test your API declaration, the better your code base will evolve. This will force you to really think about how your API is exposed to yours users. This will prevent mistakes like leaving a new object as public while you don't want users to start relying on it, or forgetting to expose a public object in your top-level module or to document it in your API docs.

## Linters

Depending on their configuration, many popular Python linters will warn you that you access or import private objects. This doesn't play well with hidden module layouts, where modules are private or moved under a private (sub-)package. Sometimes it doesn't even play well with private methods

> GRIFFE: **Our recommendation — Ignore "protected access" warnings for your own package, or make the warnings smarter.**  
> To users of linters, we recommend adding `# noqa` comments on the relevant code lines, or globally disabling warnings related to "private object access" if per-line exclusion requires too much maintenance.
>
> To authors of linters, we recommend (if possible) making these warnings smarter: they shouldn't be triggered when private objects are accessed from within the *same package*. Marking objects as private is meant to prevent downstream code to use them, not to prevent the developers of the current package themselves to use them: they know what they are doing and should be allowed to use their own private objects without warnings. At the same time, they don't want to disable these warnings *globally*, so the warnings should be derived in multiple versions, or made smarter.

## The CLI is API too

This section deserves an entire article, but we will try to stay succinct here.

Generally, we distinguish the API (Application Programming Interface) from the CLI (Command Line Interface), TUI (Textual User Interface) or GUI (Graphical User Interface). Contrary to TUIs or GUIs which are not likely to be controlled programmatically (they typically work with keyboard and mouse inputs), the CLI can easily be called by various scripts or programs, including from Python programs.

Even if a project was not designed to be used programmatically (doesn't expose a public API), it is *a certainty* that with enough popularity, it *will* be used programmatically. And the CLI will even more so be used programmatically if there is no API. Even if there is an API, sometimes it makes more sense to hook into the CLI rather than the API (cross-language integrations, wrappers, etc.).

Therefore, we urge everyone to consider their CLI as API too. We urge everyone to always design their project as library-first APIs rather than CLI-first tools.

The first user of your CLI as API is... you. When you declare your project's CLI entrypoint in pyproject.toml:

```toml
[project.scripts]
griffe = "griffe:main"
```

...this entrypoint ends up as a Python script in the `bin` directory of your virtual environment:

```python
#!/media/data/dev/griffe/.venv/bin/python
# -*- coding: utf-8 -*-
import re
import sys
from griffe import main
if __name__ == "__main__":
    sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
    sys.exit(main())
```

In this script, we find our entrypoint, `griffe.main`, used programmatically.

---

The second user of your CLI as API is... you again. When you write tests for your CLI, you import your entrypoints and call them by passing CLI options and arguments, maybe asserting the exit code raised with a `SystemExit` or the standard output/error thanks to [pytest's capture fixtures](https://docs.pytest.org/en/6.2.x/capture.html). Some simplified examples from our own test suite:

```python title="tests/test_cli.py"
import pytest
import griffe


def test_main() -> None:
    assert griffe.main(["dump", "griffe", "-s", "src", "-o/dev/null"]) == 0


def test_show_help(capsys: pytest.CaptureFixture) -> None:
    with pytest.raises(SystemExit):
        griffe.main(["-h"])
    captured = capsys.readouterr()
    assert "griffe" in captured.out


def test_show_version(capsys: pytest.CaptureFixture) -> None:
    with pytest.raises(SystemExit):
        griffe.main(["-V"])
    captured = capsys.readouterr()
    assert griffe.get_version() in captured.out
```

Now, when you start testing the logic of your CLI subcommands, such as our `dump` subcommand above, you might feel like passing again and again through the command-line arguments parser (here `argparse`) is wasteful and redundant. It is important to test that your arguments are parsed correctly (as you expect them to be parsed), but they shouldn't *have* to be parsed when you are testing the underlying logic.

It's a hint that your command-line arguments parsing (and command-line handling generally) should be *decoupled* from the logic below it: write functions with proper parameters! Then call these functions from your main CLI entrypoint, with the arguments obtained from parsing the command-line arguments and options. It will make testing and debugging much, much easier:

```python
import argparse
import sys


def dump(...):
    ...


def main(args: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(...)
    opts = parser.parse_args(args)
    if opts.subcommand == "dump":
        return dump(opts.arg1, opts.arg2, ...)
    elif ...

    print(f"Unknown subcommand {opts.subcommand}", file=sys.stderr)
    return 1
```

Now instead of having to call `main(["dump", "..."])` in your tests, you can directly call `dump(...)`, with all the benefits from static-typing and your IDE features, such as autocompletion, linting, etc..

---

The third and next users of your CLI as API are your users: just as you made your own life easier, you made their life easier for when they want to call some subcommands of your tool programmatically. No more messing with lists of strings without autocompletion or linting, no more patching of `sys.argv`, no more following the maze of transformations applied by this fancy CLI framework before finally reaching the crux of the subcommand you want to call, no more trying to replicate these transformations yourself with the CLI framework's API to avoid copy-pasting the dozens of lines you're only interested in.

> GRIFFE: **Our recommendation — Decouple command-line parsing from your CLI entrypoints.**  
> Do not tie the command parsing logic with your program's logic. Create functions early, make them accept arguments using basic types (`int`, `str`, `list`, etc.) so that your users can call your main command or subcommands with a single import and single statement. Do not encode all the logic in a single big `main` function. Decoupling the CLI-parsing logic from your entrypoints will make them much easier to test and use programmatically. Consider your entrypoints part of your API!
>
> Our CLI framework of choice is [Cappa](https://pypi.org/project/cappa/).

## Deprecations

With time, the code base of your project evolves. You add features, you fix bugs, and you generally reorganize code. Some of these changes might make your project's public API incompatible with previous versions. In that case, you usually have to "deprecate" previous usage in favor of the new usage. That means you have to support both, and emit deprecation warnings when old usage is detected.

There are many different ways of deprecating previous usage of code, which depend on the change itself. We invite you to read our [Checking APIs](../checking.md) chapter, which describes all the API changes Griffe is able to detect, and provides hint on how to allow deprecation periods for each kind of change.

In addition to emitting deprecation warnings, you should also update the docstrings and documentation for the old usage to point at the new usage, add "deprecated" labels where possible, and mark objects as deprecated when possible.

GRIFFE: **Our recommendation — Allow a deprecation periods, document deprecations.**  
Try allowing deprecation periods for every breaking change. Most changes can be made backward-compatible at the cost of writing legacy code. Use tools like [Yore](https://pawamoy.github.io/yore) to manage legacy code, and standard utilities like [`warnings.deprecated`][] to mark objects as deprecated. Griffe extensions such as [griffe-warnings-deprecated](https://mkdocstrings.github.io/griffe-warnings-deprecated/) can help you by dynamically augmenting docstrings for your API documentation.

## Third-party libraries

A few third-party libraries directly or indirectly related to public APIs deserve to be mentioned here.

[public](https://pypi.org/project/public/) lets you decorate objects with `@public.add` to dynamically add them to `__all__`, so that you don't have to build a list of strings yourself. The "public visibility" marker is closer to each object, and might help avoiding mistakes like forgetting to update `__all__` when an object is removed or renamed.

[modul](https://pypi.org/project/modul/), from Frost Ming, the author of [PDM](https://pdm-project.org/en/latest/), goes one step further and actually hides attributes that are not marked "exported" from users: they won't be able to access un-exported attributes, leaving *only* the public API visible.

[Deprecated](https://pypi.org/project/Deprecated/), which was probably a source of inspiration for [PEP 702](https://peps.python.org/pep-0702/), allows decorating objects with `@deprecated` to mark them as deprecated. Such decorated callables will emit deprecation warnings when called. PEP 702's `warnings.deprecated` could be seen as its successor, bringing the feature directly into the standard library so that type checkers and other static analysis tool can converge on this way to mark objects as deprecated.

[slothy](https://pypi.org/project/slothy/), which is less directly related to public APIs, but useful for the case where you are hiding your modules layout and exposing all your public API from the top-level `__init__` module. Depending on the size of your public API, and the time it takes to import everything (memory initializations, etc.), it might be interesting to make all these imports *lazy*. With a lazily imported public API, users who are only interested in a few objects of your public API won't have to pay the price of importing everything.
