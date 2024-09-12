# Navigating APIs

Griffe loads API data into data models. These models provide various attributes and methods to access or update specific fields. The different models are:

- [`Module`][griffe.Module], representing Python modules;
- [`Class`][griffe.Class], representing Python classes;
- [`Function`][griffe.Function], representing Python functions and class methods;
- [`Attribute`][griffe.Attribute], representing object attributes that weren't identified as modules, classes or functions;
- [`Alias`][griffe.Alias], representing indirections such as imported objects or class members inherited from parent classes.

When [loading an object](loading.md), Griffe will give you back an instance of one of these models. A few examples:

```python
>>> import griffe
>>> type(griffe.load("markdown"))
<class '_griffe.models.Module'>
>>> type(griffe.load("markdown.core.Markdown"))
<class '_griffe.models.Class'>
>>> type(griffe.load("markdown.Markdown"))
<class '_griffe.models.Alias'>
>>> type(griffe.load("markdown.core.markdown"))
<class '_griffe.models.Function'>
>>> type(griffe.load("markdown.markdown"))
<class '_griffe.models.Alias'>
>>> type(griffe.load("markdown.Markdown.references"))
<class '_griffe.models.Attribute'>
```

However deep is the object, Griffe loads the entire package. It means that in all the cases above, Griffe loaded the whole `markdown` package. The model instance Griffe gives you back is therefore part of a tree that you can navigate.

## Moving up: parents

Each object holds a reference to its [`parent`][griffe.Object.parent] (except for the top-level module, for which the parent is `None`). Shortcuts are provided to climb up directly to the parent [`module`][griffe.Object.module], or the top-level [`package`][griffe.Object.package]. As we have seen in the [Loading chapter](loading.md), Griffe stores all loaded modules in a modules collection; this collection can be accessed too, through the [`modules_collection`][griffe.Object.modules_collection] attribute.

## Moving down: members

To access an object's members, there are a few options:

- Access to regular members through the [`members`][griffe.Object.members] attribute, which is a dictionary. The keys are member names, the values are Griffe models.

    ```pycon
    >>> import griffe
    >>> markdown = griffe.load("markdown")
    >>> markdown.members["Markdown"]
    Alias('Markdown', 'markdown.core.Markdown')
    >>> markdown.members["core"].members["Markdown"]
    Class('Markdown', 46, 451)
    ```

- Access to both regular and inherited members through the [`all_members`][griffe.Object.all_members] attribute, which is a dictionary again. See [Inherited members](#inherited-members).

- Convenient dictionary-like item access, thanks to the subscript syntax `[]`. With this syntax, you will not only be able to chain accesses, but also merge them into a single access by using dot-separated paths to objects:

    ```pycon
    >>> import griffe
    >>> markdown = griffe.load("markdown")
    >>> markdown["core"]["Markdown"]  # chained access
    Class('Markdown', 46, 451)
    >>> markdown["core.Markdown"]  # merged access
    Class('Markdown', 46, 451)
    ```

    The dictionary-like item access also accepts tuples of strings. So if for some reason you don't have a string equal to `"core.Markdown"` but a tuple equal to `("core", "Markdown")` (for example obtained from splitting another string), you can use it too:

    ```pycon
    >>> import griffe
    >>> markdown = griffe.load("markdown")
    >>> markdown[("core", "Markdown")]  # tuple access
    Class('Markdown', 46, 451)
    >>> # Due to the nature of the subscript syntax,
    >>> # you can even use implicit tuples.
    >>> markdown["core", "Markdown"]
    Class('Markdown', 46, 451)
    ```

- Less convenient, but safer access to members while the object tree is being built (while a package is still being loaded), using the [`get_member()`][griffe.GetMembersMixin.get_member] method.

    ```pycon
    >>> import griffe
    >>> markdown = griffe.load("markdown")
    >>> markdown.get_member("core.Markdown")
    Class('Markdown', 46, 451)
    ```

    In particular, Griffe extensions should always use `get_member` instead of the subscript syntax `[]`. The `get_member` method only looks into regular members, while the subscript syntax looks into inherited members too (for classes), which cannot be correctly computed until a package is fully loaded (which is generally not the case when an extension is running).

- In addition to this, models provide the [`attributes`][griffe.Object.attributes], [`functions`][griffe.Object.functions], [`classes`][griffe.Object.classes] or [`modules`][griffe.Object.modules] attributes, which return only members of the corresponding kind. These attributes are computed dynamically each time (they are Python properties).

The same way members are accessed, they can also be set:

- Dictionary-like item assignment: `markdown["thing"] = ...`, also supporting dotted-paths and string tuples. This will (re)assign both regular and inherited members for classes.
- Safer method for extensions: `markdown.set_member("thing", ...)`, also supporting dotted-paths and string tuples. This will not (re)assign inherited members for classes.
- Regular member assignment: `markdown.members["thing"] = ...`. **This is not recommended, as the assigned member's `parent` attribute will not be automatically updated.**

...and deleted:

- Dictionary-like item deletion: `del markdown["thing"]`, also supporting dotted-paths and string tuples. This will delete both regular and inherited members for classes.
- Safer method for extensions: `markdown.del_member("thing")`, also supporting dotted-paths and string tuples. This will not delete inherited members for classes.
- Regular member deletion: `del markdown.members["thing"]`. **This is not recommended, as the [`aliases`][griffe.Object.aliases] attribute of other objects in the tree will not be automatically updated.**

### Inherited members

Griffe supports class inheritance, both when visiting and inspecting modules.

To access members of a class that are inherited from base classes, use the [`inherited_members`][griffe.Object.inherited_members] attribute. If this is the first time you access inherited members, the base classes of the given class will be resolved and cached, then the MRO (Method Resolution Order) will be computed for these bases classes, and a dictionary of inherited members will be built and cached. Next times you access it, you'll get the cached dictionary. Make sure to only access `inherited_members` once everything is loaded by Griffe, to avoid computing things too early. Don't try to access inherited members in extensions, while visiting or inspecting modules.

Inherited members are aliases that point at the corresponding members in parent classes. These aliases will have their [`inherited`][griffe.Alias.inherited] attribute set to true.

**Important:** only classes from already loaded packages will be used when computing inherited members. This gives users control over how deep into inheritance to go, by pre-loading packages from which you want to inherit members. For example, if `package_c.ClassC` inherits from `package_b.ClassB`, itself inheriting from `package_a.ClassA`, and you want to load `ClassB` members only:

```python
import griffe

loader = griffe.GriffeLoader()
# note that we don't load package_a
loader.load("package_b")
loader.load("package_c")
```

If a base class cannot be resolved during computation of inherited members, Griffe logs a DEBUG message.

If you want to access all members at once (both declared and inherited), use the [`all_members`][griffe.Object.all_members] attribute. If you want to access only declared members, use the [`members`][griffe.Object] attribute.

Accessing the [`attributes`][griffe.Object.attributes], [`functions`][griffe.Object.functions], [`classes`][griffe.Object.classes] or [`modules`][griffe.Object.modules] attributes will trigger inheritance computation, so make sure to only access them once everything is loaded by Griffe. Don't try to access inherited members in extensions, while visiting or inspecting modules.

#### Limitations

Currently, there are three limitations to our class inheritance support:

1. when visiting (static analysis), some objects are not yet properly recognized as classes, for example named tuples. If you inherit from a named tuple, its members won't be added to the inherited members of the inheriting class.

    ```python
    MyTuple = namedtuple("MyTuple", "attr1 attr2")


    class MyClass(MyTuple):
        ...
    ```

2. when visiting (static analysis), subclasses using the same name as one of their parent class will prevent Griffe from computing the MRO and therefore the inherited members. To circumvent that, give a different name to your subclass:

    ```python
    from package import SomeClass


    # instead of
    class SomeClass(SomeClass):
        ...


    # do
    class SomeOtherClass(SomeClass):
        ...
    ```

3. when inspecting (dynamic analysis), ephemeral base classes won't be resolved, and therefore their members won't appear in child classes. To circumvent that, assign these dynamic classes to variables:

    ```python
    # instead of
    class MyClass(namedtuple("MyTuple", "attr1 attr2")):
        ...


    # do
    MyTuple = namedtuple("MyTuple", "attr1 attr2")


    class MyClass(MyTuple):
        ...
    ```

We will try to lift these limitations in the future.

## Aliases

Aliases represent indirections, such as objects imported from elsewhere, or attribute and methods inherited from parent classes. They are pointers to the object they represent. The path of the object they represent is stored in their [`target_path`][griffe.Alias.target_path] attribute. Once they are resolved, the target object can be accessed through their [`target`][griffe.Alias.target] attribute.

Aliases can be found in objects' members. Each object can also access its own aliases (the aliases pointing at it) through its [`aliases`][griffe.Object.aliases] attribute. This attribute is a dictionary whose keys are the aliases paths and values are the aliases themselves.

Most of the time, aliases simply act as proxies to their target objects. For example, accessing the `docstring` of an alias will simply return the docstring of the object it targets.

Accessing fields on aliases will trigger their resolution. If they are already resolved (their `target` attribute is set to the target object), the field is returned. If they are not resolved, their target path will be looked up in the modules collection, and if it is found, the object at this location will be assigned to the alias' `target` attribute. If it isn't found, an [`AliasResolutionError`][griffe.AliasResolutionError] exception will be raised.

Since merely accessing an alias field can raise an exception, it is often useful to check if an object is an alias before accessing its fields. There are multiple ways to check if an object is an alias:

- using the `is_alias` boolean ([`Object.is_alias`][griffe.Object.is_alias], [`Alias.is_alias`][griffe.Alias.is_alias]), which won't trigger resolution
- using `isinstance` to check if the object is an instance of [`Alias`][griffe.Alias]

```pycon
>>> import griffe
>>> load = griffe.load("griffe.load")
>>> load.is_alias
True
>>> isinstance(load, griffe.Alias)
True
```

The [`kind`][griffe.Alias.kind] of an alias will only return [`ALIAS`][griffe.Kind.ALIAS] if the alias is not resolved and cannot be resolved within the current modules collection.

You can of course also catch any raised exception with a regular try/except block:

```python
try:
    print(obj.source)
except griffe.AliasResolutionError:
    pass
```

To check if an alias is already resolved, you can use its [`resolved`][griffe.Alias.resolved] attribute.

### Alias chains

Aliases can be chained. For example, if module `a` imports `X` from module `b`, which itself imports `X` from module `c`, then `a.X` is an alias to `b.X` which is an alias to `c.X`: `a.X` -> `b.X` -> `c.X`. To access the final target directly, you can use the [`final_target`][griffe.Alias.final_target] attribute. Most alias properties that act like proxies actually fetch the final target rather than the next one to return the final field.

Sometimes, when a package makes use of complicated imports (wildcard imports from parents and submodules), or when runtime objects are hard to inspect, it is possible to end up with a cyclic chain of aliases. You could for example end up with a chain like `a.X` -> `b.X` -> `c.X` -> `a.X`. In this case, the alias *cannot* be resolved, since the chain goes in a loop. Griffe will raise a [`CyclicAliasError`][griffe.CyclicAliasError] when trying to resolve such cyclic chains.

Aliases chains are never partially resolved: either they are resolved down to their final target, or none of their links are resolved.

## Object kind

The kind of an object (module, class, function, attribute or alias) can be obtained in several ways.

- With the [`kind`][griffe.Object.kind] attribute and the [`Kind`][griffe.Kind] enumeration: `obj.kind is Kind.MODULE`.

- With the [`is_kind()`][griffe.Object.is_kind] method:

    - `obj.is_kind(Kind.MODULE)`
    - `obj.is_kind("class")`
    - `obj.is_kind({"function", Kind.ATTRIBUTE})`

    When given a set of kinds, the method returns true if the object is of one of the given kinds.

- With the [`is_module`][griffe.Object.is_module], [`is_class`][griffe.Object.is_class], [`is_function`][griffe.Object.is_function], [`is_attribute`][griffe.Object.is_attribute], and [`is_alias`][griffe.Object.is_alias] attributes.

Additionally, it is possible to check if an object is a sub-kind of module, with the following attributes:

- [`is_init_module`][griffe.Object.is_init_module], for `__init__.py` modules
- [`is_package`][griffe.Object.is_package], for top-level packages
- [`is_subpackage`][griffe.Object.is_subpackage], for non-top-level packages
- [`is_namespace_package`][griffe.Object.is_namespace_package], for top-level [namespace packages](https://packaging.python.org/en/latest/guides/packaging-namespace-packages/)
- [`is_namespace_subpackage`][griffe.Object.is_namespace_subpackage], for non-top-level namespace packages

Finally, additional [`labels`][griffe.Object.labels] are attached to objects to further specify their kind. The [`has_labels()`][griffe.Object.has_labels] method can be used to check if an object has several specific labels.

## Object location

An object is identified by its [`path`][griffe.Object.path], which is its location in the object tree. The path is composed of all the parent names and the object name, separated by dots, for example `mod.Class.meth`. This `path` is the [`canonical_path`][griffe.Object.canonical_path] on regular objects. For aliases however, the `path` is *where they are imported* while the canonical path is *where they come from*. Example:

```python
# pkg1.py
from pkg2 import A as B
```

```pycon
>>> import griffe
>>> B = griffe.load("pkg1.B")
>>> B.path
'pkg1.B'
>>> B.canonical_path
'pkg2.A'
```

### Source

Information on the actual source code of objects is available through the following attributes:

- [`filepath`][griffe.Object.filepath], the absolute path to the module the object appears in, for example `~/project/src/pkg/mod.py`
- [`relative_filepath`][griffe.Object.relative_filepath], the relative path to the module, compared to the current working directory, for example `src/pkg/mod.py`
- [`relative_package_filepath`][griffe.Object.relative_package_filepath], the relative path to the module, compared to the parent of the top-level package, for example `pkg/mod.py`
- [`lineno`][griffe.Object.lineno] and [`endlineno`][griffe.Object.endlineno], the starting and ending line numbers of the object in the source
- [`lines`][griffe.Object.lines], the lines of code defining the object (or importing the alias)
- [`source`][griffe.Object.source], the source lines concatenated as a single multiline string

Each object holds a reference to a [`lines_collection`][griffe.Object.lines_collection]. Similar to the modules collection, this lines collection is a dictionary whose keys are module file-paths and values are their contents as list of lines. The lines collection is populated by the loader.

## Object visibility

Each object has fields that are related to their visibility within the API.

- [`is_public`][griffe.Object.is_public]: whether this object is public (destined to be consumed by your users). For module-level objects, Griffe considers that the object is public if:

    - it is listed in its parent module's `__all__` attribute
    - or if its parent module does not declare `__all__`, and the object doesn't have a private name, and the object is not imported from elsewhere

    ```python
    # package1/__init__.py
    from package2 import A  # not public
    from package1 import submodule  # not public

    b = 0  # public
    _c = 1  # not public
    __d = 2  # not public

    def __getattr__(name: str):  # public
        ...
    ```

    For class-level objects, Griffe considers that the object is public if the object doesn't have a private name, and the object is not imported from elsewhere.

    ```python
    # package1/__init__.py
    class A:
        from package1.module import X  # not public
        from package2 import Y  # not public

        b = 0  # public
        _c = 1  # not public
        __d = 2  # not public

        def __eq__(self, other):  # public
            ...
    ```

- [`is_deprecated`][griffe.Object.is_deprecated]: whether this object is deprecated and shouldn't be used.

- [`is_special`][griffe.Object.is_special]: whether this object has a special name like `__special__`

- [`is_private`][griffe.Object.is_private]: whether this object has a private name like `_private` or `__private`, but not `__special__`

- [`is_class_private`][griffe.Object.is_class_private]: whether this object has a class-private name like `__private` and is a member of a class

Since `is_private` only check the name of the object, it is not mutually exclusive with `is_public`. It means an object can return true for both `is_public` and `is_private`. We invite Griffe users to mostly rely on `is_public` and `not is_public`.

It is possible to force `is_public` and `is_deprecated` to return true or false by setting the [`public`][griffe.Object.public] and [`deprecated`][griffe.Object.deprecated] fields respectively. These fields are typically set by extensions that support new ways of marking objects as public or deprecated.

## Imports/exports

Modules and classes populate their [`imports`][griffe.Object.imports] field with name that were imported from other modules. Similarly, modules populate their [`exports`][griffe.Object.exports] field with names that were exported by being listed into the module's `__all__` attribute. Each object then provides then [`is_imported`][griffe.Object.is_imported] and [`is_exported`][griffe.Object.is_exported] fields, which tell if an object was imported or exported respectively. Additionally, objects also provide an [`is_wildcard_exposed`][griffe.Object.is_wildcard_exposed] field that tells if an object is exposed to wildcard imports, i.e. will be imported when another module does `from this_module import *`.

## Docstrings

Each object has an optional [`docstring`][griffe.Object.docstring] attached to it. To check whether it has one without comparing against `None`, the two following fields can be used:

- [`has_docstring`][griffe.Object.has_docstring]: whether this object has a docstring (even empty)
- [`has_docstrings`][griffe.Object.has_docstrings]: same thing, but recursive; whether this object or any of its members has a docstring (even empty)

[Docstrings][griffe.Docstring] provide their cleaned-up [`value`][griffe.Docstring.value] (de-indented string, stripped from leading and trailing new lines), as well as their starting and ending line numbers with [`lineno`][griffe.Docstring.lineno] and [`endlineno`][griffe.Docstring.endlineno].

Docstrings can be parsed against several [docstring-styles](../../reference/docstrings.md), which are micro-formats that allow documenting things such as parameters, returned values, raised exceptions, etc..

When loading a package, it is possible to specify the docstring style to attach to every docstring (see the `docstring_parser` parameter of [`griffe.load`][griffe.load]). Accessing the [`parsed`][griffe.Docstring.parsed] field of a docstring will use this style to parse the docstring and return a list of [docstring sections][advanced-api-sections]. Each section has a `value` whose shape depends on the section kind. For example, parameter sections have a list of parameter representations as value, while a text section only has a string as value.

After a package is loaded, it is still possible to change the style used for specific docstrings by either overriding their [`parser`][griffe.Docstring.parser] and [`parser_options`][griffe.Docstring.parser_options] attributes, or by calling their [`parse()`][griffe.Docstring.parse] method with a different style:

```pycon
>>> import griffe
>>> markdown = griffe.load("markdown", docstring_parser="google")
>>> markdown["Markdown"].docstring.parse("numpy")
[...]
```

Do note, however, that the `parsed` attribute is cached, and won't be reset when overriding the `parser` or `parser_options` values.

Docstrings have a [`parent`][griffe.Docstring.parent] field too, that is a reference to their respective module, class, function or attribute.

## Model-specific fields

Models have most fields in common, but also have specific fields.

### Modules

- [`imports_future_annotations`][griffe.Module.imports_future_annotations]: Whether the module imports [future annotations](https://peps.python.org/pep-0563/), which changes the way we parse type annotations.
- [`overloads`][griffe.Module.overloads]: A dictionary to store overloads for module-level functions.

### Classes

- [`bases`][griffe.Class.bases]: A list of class bases in the form of [expressions][griffe.Expr].
- [`resolved_bases`][griffe.Class.resolved_bases]: A list of class bases, in the form of [Class][griffe.Class] objects. Only the bases that were loaded are returned, the others are discarded.
- [`mro()`][griffe.Class.mro]: A method to compute the Method Resolution Order in the form of a list of [Class][griffe.Class] objects.
- [`overloads`][griffe.Class.overloads]: A dictionary to store overloads for class-level methods.
- [`decorators`][griffe.Class.decorators]: The [decorators][griffe.Decorator] applied to the class.
- [`parameters`][griffe.Class.parameters]: The [parameters][griffe.Parameters] of the class' `__init__` method, if any.

### Functions

- [`decorators`][griffe.Function.decorators]: The [decorators][griffe.Decorator] applied to the function.
- [`overloads`][griffe.Function.overloads]: The overloaded signatures of the function.
- [`parameters`][griffe.Function.parameters]: The [parameters][griffe.Parameters] of the function.
- [`returns`][griffe.Function.returns]: The type annotation of the returned value, in the form of an [expression][griffe.Expr]. The `annotation` field can also be used, for compatibility with attributes.

### Attributes

- [`annotation`][griffe.Attribute.annotation]: The type annotation of the attribute, in the form of an [expression][griffe.Expr].
- [`value`][griffe.Attribute.value]: The value of the attribute, in the form of an [expression][griffe.Expr].
- [`deleter`][griffe.Attribute.deleter]: The property deleter.
- [`setter`][griffe.Attribute.setter]: The property setter.

### Alias

- [`alias_lineno`][griffe.Alias.alias_lineno]: The alias line number (where the object is imported).
- [`alias_endlineno`][griffe.Alias.alias_endlineno]: The alias ending line number (where the object is imported).
- [`target`][griffe.Alias.target]: The alias target (a module, class, function or attribute).
- [`target_path`][griffe.Alias.target_path]: The path of the alias target, as a string.
- [`wildcard`][griffe.Alias.wildcard]: Whether this alias represents a wildcard import, and if so from which module.
- [`resolve_target()`][griffe.Alias.resolve_target]: A method that resolves the target when called.

## Expressions

When parsing source code, Griffe builds enhanced ASTs for type annotations, decorators, parameter defaults, attribute values, etc.

These "expressions" are very similar to what Python's [ast][] module gives you back when parsing source code, with a few differences: attributes like `a.b.c.` are flattened, and names like `a` have a parent object attached to them, a Griffe object, allowing to resolve this name to its full path given the scope of its parent.

You can write some code below and print annotations or attribute values with [Rich]'s pretty printer to see how expressions look like.

```pyodide install="griffe,rich" theme="tomorrow,dracula"
from griffe import temporary_visited_module
from rich.pretty import pprint

code = """
    from dataclasses import dataclass
    from random import randint

    @dataclass
    class Bar:
        baz: int

    def get_some_baz() -> int:
        return randint(0, 10)

    foo: Bar = Bar(baz=get_some_baz())
"""        

with temporary_visited_module(code) as module:
    pprint(module["foo"].annotation)
    pprint(module["foo"].value)
```

Ultimately, these expressions are what allow downstream tools such as [mkdocstrings' Python handler][mkdocstrings-python] to render cross-references to every object it knows of, coming from the current code base or loaded from object inventories (objects.inv files).

During static analysis, these expressions also allow to analyze decorators, dataclass fields, and many more things in great details, and in a robust manner, to build third-party libraries support in the form of [Griffe extensions](extending.md).

To learn more about expressions, read their [API reference](../../reference/api/expressions.md).

### Modernization

[:octicons-heart-fill-24:{ .pulse } Sponsors only](../../insiders/index.md){ .insiders } — [:octicons-tag-24: Insiders 1.2.0](../../insiders/changelog.md#1.2.0)

The Python language keeps evolving, and often library developers must continue supporting a few minor versions of Python. Therefore they cannot use some features that were introduced in the latest versions.

Yet this doesn't mean they can't enjoy latest features in their own docs: Griffe allows to "modernize" expressions, for example by replacing `typing.Union` with PEP 604 type unions `|`. Thanks to this, downstream tools like [mkdocstrings][mkdocstrings-python] can automatically transform type annotations into their modern equivalent. This improves consistency in your docs, and shows users how to use your code with the latest features of the language.

To modernize an expression, simply call its [`modernize()`][griffe.Expr.modernize] method. It returns a new, modernized expression. Some parts of the expression might be left unchanged, so be careful if you decide to mutate them.

Modernizations applied:

- `typing.Dict[A, B]` becomes `dict[A, B]`
- `typing.List[A]` becomes `list[A]`
- `typing.Set[A]` becomes `set[A]`
- `typing.Tuple[A]` becomes `tuple[A]`
- `typing.Union[A, B]` becomes `A | B`
- `typing.Optional[A]` becomes `A | None`

## Next steps

In this chapter we saw many of the fields that compose our models, and how and why to use them. Now you might be interested in [extending](extending.md) or [serializing](serializing.md) the API data, or [checking for API breaking changes](checking.md).

[mkdocstrings-python]: https://mkdocstrings.github.io/python
[rich]: https://rich.readthedocs.io/en/stable/
