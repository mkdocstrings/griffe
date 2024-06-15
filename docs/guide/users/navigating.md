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
<class '_griffe.dataclasses.Module'>
>>> type(griffe.load("markdown.core.Markdown"))
<class '_griffe.dataclasses.Class'>
>>> type(griffe.load("markdown.Markdown"))
<class '_griffe.dataclasses.Alias'>
>>> type(griffe.load("markdown.core.markdown"))
<class '_griffe.dataclasses.Function'>
>>> type(griffe.load("markdown.markdown"))
<class '_griffe.dataclasses.Alias'>
>>> type(griffe.load("markdown.Markdown.references"))
<class '_griffe.dataclasses.Attribute'>
```

However deep is the object, Griffe loads the entire package. It means that in all the cases above, Griffe loaded the whole `markdown` package. The model instance Griffe gives you back is therefore part of a tree that you can navigate.

## Members

To access members, there are more options:

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

## Inherited members

Griffe supports class inheritance, both when visiting and inspecting modules.

To access members of a class that are inherited from base classes, use the [`inherited_members`][griffe.Object.inherited_members] attribute. If this is the first time you access inherited members, the base classes of the given class will be resolved and cached, then the MRO (Method Resolution Order) will be computed for these bases classes, and a dictionary of inherited members will be built and cached. Next times you access it, you'll get the cached dictionary. Make sure to only access `inherited_members` once everything is loaded by Griffe, to avoid computing things too early. Don't try to access inherited members in extensions, while visiting or inspecting modules.

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

### Limitations

Currently, there are three limitations to our class inheritance support:

1. when visiting (static analysis), some objects are not yet properly recognized as classes,
    for example named tuples. If you inherit from a named tuple,
    its members won't be added to the inherited members of the inheriting class.

    ```python
    MyTuple = namedtuple("MyTuple", "attr1 attr2")


    class MyClass(MyTuple):
        ...
    ```

2. when visiting (static analysis), subclasses using the same name
    as one of their parent class will prevent Griffe from computing the MRO
    and therefore the inherited members. To circumvent that, give a
    different name to your subclass:

    ```python
    from package import SomeClass
    
    
    # instead of
    class SomeClass(SomeClass):
        ...

    
    # do
    class SomeOtherClass(SomeClass):
        ...
    ```

3. when inspecting (dynamic analysis), ephemeral base classes won't be resolved,
    and therefore their members won't appear in child classes. To circumvent that,
    assign these dynamic classes to variables:

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

## Data fields

Each object holds a reference to its parent (except for the top-level module, for which the parent is `None`). Accessing the parent is as easy as doing `obj.parent`.

Many of the available data fields are computed thanks to this parent, allowing us to climb the tree up to its root, the top-level module. Some of the fields taking advantage of [`parent`](griffe.Object.parent) are:

- [`module`][griffe.Object.module], which is the parent module of any object nested within it:

    ```pycon
    >>> import griffe
    >>> markdown = griffe.load("markdown")
    >>> markdown["core.Markdown.references"].module
    Module(PosixPath('.venv/lib/python3.11/site-packages/markdown/core.py'))
    >>> # The `module` of a module is itself.
    >>> markdown["core"].module
    Module(PosixPath('.venv/lib/python3.11/site-packages/markdown/core.py'))
    ```

- [`package`][griffe.Object.package], which is the top-level module, or package, of any object:

    ```pycon
    >>> import griffe
    >>> markdown = griffe.load("markdown")
    >>> markdown["core.Markdown.references"].package
    Module(PosixPath('.venv/lib/python3.11/site-packages/markdown/__init__.py'))
    ```

- [`path`][griffe.Object.path], which is the "Python path" of an object. This path is the chain of names in the tree down to the current object, separated by dots.

    ```pycon
    >>> import griffe
    >>> markdown = griffe.load("markdown")
    >>> markdown["core.Markdown.references"].path
    'markdown.core.Markdown.references'
    ```

    The `path` of an object therefore depends on its location in the object tree. 

- [`filepath`][griffe.Object.filepath], which is the filepath the object exists in.

    ```pycon
    >>> import griffe
    >>> markdown = griffe.load("markdown")
    >>> markdown.filepath
    PosixPath('.venv/lib/python3.11/site-packages/markdown/__init__.py')
    ```


