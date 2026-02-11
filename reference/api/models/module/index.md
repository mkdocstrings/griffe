# Module

```
Module(
    *args: Any,
    filepath: Path | list[Path] | None = None,
    **kwargs: Any,
)
```

Bases: `Object`

```
              flowchart TD
              griffe.Module[Module]
              griffe._internal.models.Object[Object]
              griffe._internal.mixins.ObjectAliasMixin[ObjectAliasMixin]
              griffe._internal.mixins.GetMembersMixin[GetMembersMixin]
              griffe._internal.mixins.SetMembersMixin[SetMembersMixin]
              griffe._internal.mixins.DelMembersMixin[DelMembersMixin]
              griffe._internal.mixins.SerializationMixin[SerializationMixin]

                              griffe._internal.models.Object --> griffe.Module
                                griffe._internal.mixins.ObjectAliasMixin --> griffe._internal.models.Object
                                griffe._internal.mixins.GetMembersMixin --> griffe._internal.mixins.ObjectAliasMixin
                
                griffe._internal.mixins.SetMembersMixin --> griffe._internal.mixins.ObjectAliasMixin
                
                griffe._internal.mixins.DelMembersMixin --> griffe._internal.mixins.ObjectAliasMixin
                
                griffe._internal.mixins.SerializationMixin --> griffe._internal.mixins.ObjectAliasMixin
                




              click griffe.Module href "" "griffe.Module"
              click griffe._internal.models.Object href "" "griffe._internal.models.Object"
              click griffe._internal.mixins.ObjectAliasMixin href "" "griffe._internal.mixins.ObjectAliasMixin"
              click griffe._internal.mixins.GetMembersMixin href "" "griffe._internal.mixins.GetMembersMixin"
              click griffe._internal.mixins.SetMembersMixin href "" "griffe._internal.mixins.SetMembersMixin"
              click griffe._internal.mixins.DelMembersMixin href "" "griffe._internal.mixins.DelMembersMixin"
              click griffe._internal.mixins.SerializationMixin href "" "griffe._internal.mixins.SerializationMixin"
```

The class representing a Python module.

Parameters:

- ## **`*args`**

  (`Any`, default: `()` ) – See griffe.Object.

- ## **`filepath`**

  (`Path | list[Path] | None`, default: `None` ) – The module file path (directory for namespace [sub]packages, none for builtin modules).

- ## **`**kwargs`**

  (`Any`, default: `{}` ) – See griffe.Object.

Methods:

- **`__bool__`** – An object is always true-ish.
- **`__delitem__`** – Delete a member with its name or path.
- **`__getitem__`** – Get a member with its name or path.
- **`__len__`** – The number of members in this object, recursively.
- **`__setitem__`** – Set a member with its name or path.
- **`as_dict`** – Return this module's data as a dictionary.
- **`as_json`** – Return this object's data as a JSON string.
- **`del_member`** – Delete a member with its name or path.
- **`filter_members`** – Filter and return members based on predicates.
- **`from_json`** – Create an instance of this class from a JSON string.
- **`get_member`** – Get a member with its name or path.
- **`has_labels`** – Tell if this object has all the given labels.
- **`is_kind`** – Tell if this object is of the given kind.
- **`resolve`** – Resolve a name within this object's and parents' scope.
- **`set_member`** – Set a member with its name or path.

Attributes:

- **`aliases`** (`dict[str, Alias]`) – The aliases pointing to this object.
- **`all_members`** (`dict[str, Object | Alias]`) – All members (declared and inherited).
- **`analysis`** (`Literal['static', 'dynamic'] | None`) – The type of analysis used to load this object.
- **`attributes`** (`dict[str, Attribute]`) – The attribute members.
- **`canonical_path`** (`str`) – The full dotted path of this object.
- **`classes`** (`dict[str, Class]`) – The class members.
- **`deprecated`** (`bool | str | None`) – Whether this object is deprecated (boolean or deprecation message).
- **`docstring`** (`Docstring | None`) – The object docstring.
- **`endlineno`** (`int | None`) – The ending line number of the object.
- **`exports`** (`list[str | ExprName] | None`) – The names of the objects exported by this (module) object through the __all__ variable.
- **`extra`** (`dict[str, dict[str, Any]]`) – Namespaced dictionaries storing extra metadata for this object, used by extensions.
- **`filepath`** (`Path | list[Path]`) – The file path of this module.
- **`functions`** (`dict[str, Function]`) – The function members.
- **`git_info`** (`GitInfo | None`) – Git information for this object, if available.
- **`has_docstring`** (`bool`) – Whether this object has a docstring (empty or not).
- **`has_docstrings`** (`bool`) – Whether this object or any of its members has a docstring (empty or not).
- **`imports`** (`dict[str, str]`) – The other objects imported by this object.
- **`imports_future_annotations`** (`bool`) – Whether this module import future annotations.
- **`inherited`** (`bool`) – Always false for objects.
- **`inherited_members`** (`dict[str, Alias]`) – Members that are inherited from base classes.
- **`is_alias`** (`bool`) – Always false for objects.
- **`is_attribute`** (`bool`) – Whether this object is an attribute.
- **`is_class`** (`bool`) – Whether this object is a class.
- **`is_class_private`** (`bool`) – Whether this object/alias is class-private (starts with \_\_ and is a class member).
- **`is_collection`** (`bool`) – Always false for objects.
- **`is_deprecated`** (`bool`) – Whether this object is deprecated.
- **`is_exported`** (`bool`) – Whether this object/alias is exported (listed in __all__).
- **`is_function`** (`bool`) – Whether this object is a function.
- **`is_generic`** (`bool`) – Whether this object is generic.
- **`is_imported`** (`bool`) – Whether this object/alias was imported from another module.
- **`is_init_method`** (`bool`) – Whether this function is an __init__ method.
- **`is_init_module`** (`bool`) – Whether this module is an __init__.py module.
- **`is_module`** (`bool`) – Whether this object is a module.
- **`is_namespace_package`** (`bool`) – Whether this module is a namespace package (top folder, no __init__.py).
- **`is_namespace_subpackage`** (`bool`) – Whether this module is a namespace subpackage.
- **`is_package`** (`bool`) – Whether this module is a package (top module).
- **`is_private`** (`bool`) – Whether this object/alias is private (starts with \_) but not special.
- **`is_public`** (`bool`) – Whether this object is considered public.
- **`is_special`** (`bool`) – Whether this object/alias is special ("dunder" attribute/method, starts and end with \_\_).
- **`is_subpackage`** (`bool`) – Whether this module is a subpackage.
- **`is_type_alias`** (`bool`) – Whether this object is a type alias.
- **`is_wildcard_exposed`** (`bool`) – Whether this object/alias is exposed to wildcard imports.
- **`kind`** – The object kind.
- **`labels`** (`set[str]`) – The object labels (property, dataclass, etc.).
- **`lineno`** (`int | None`) – The starting line number of the object.
- **`lines`** (`list[str]`) – The lines containing the source of this object.
- **`lines_collection`** (`LinesCollection`) – The lines collection attached to this object or its parents.
- **`members`** (`dict[str, Object | Alias]`) – The object members (modules, classes, functions, attributes, type aliases).
- **`module`** (`Module`) – The parent module of this object.
- **`modules`** (`dict[str, Module]`) – The module members.
- **`modules_collection`** (`ModulesCollection`) – The modules collection attached to this object or its parents.
- **`name`** (`str`) – The object name.
- **`overloads`** (`dict[str, list[Function]]`) – The overloaded signatures declared in this module.
- **`package`** (`Module`) – The absolute top module (the package) of this object.
- **`parent`** (`Module | Class | None`) – The parent of the object (none if top module).
- **`path`** (`str`) – The dotted path of this object.
- **`public`** (`bool | None`) – Whether this object is public.
- **`relative_filepath`** (`Path`) – The file path where this object was defined, relative to the current working directory.
- **`relative_package_filepath`** (`Path`) – The file path where this object was defined, relative to the top module path.
- **`runtime`** (`bool`) – Whether this object is available at runtime.
- **`source`** (`str`) – The source code of this object.
- **`source_link`** (`str | None`) – Source link for this object, if available.
- **`type_aliases`** (`dict[str, TypeAlias]`) – The type alias members.
- **`type_parameters`** (`TypeParameters`) – The object type parameters.

Source code in `packages/griffelib/src/griffe/_internal/models.py`

```
def __init__(self, *args: Any, filepath: Path | list[Path] | None = None, **kwargs: Any) -> None:
    """Initialize the module.

    Parameters:
        *args: See [`griffe.Object`][].
        filepath: The module file path (directory for namespace [sub]packages, none for builtin modules).
        **kwargs: See [`griffe.Object`][].
    """
    super().__init__(*args, **kwargs)
    self._filepath: Path | list[Path] | None = filepath
    self.overloads: dict[str, list[Function]] = defaultdict(list)
    """The overloaded signatures declared in this module."""
```

## aliases

```
aliases: dict[str, Alias] = {}
```

The aliases pointing to this object.

## all_members

```
all_members: dict[str, Object | Alias]
```

All members (declared and inherited).

This method is part of the consumer API: do not use when producing Griffe trees!

## analysis

```
analysis: Literal['static', 'dynamic'] | None = analysis
```

The type of analysis used to load this object.

None means the object was created manually.

## attributes

```
attributes: dict[str, Attribute]
```

The attribute members.

This method is part of the consumer API: do not use when producing Griffe trees!

## canonical_path

```
canonical_path: str
```

The full dotted path of this object.

The canonical path is the path where the object was defined (not imported).

See also: path.

## classes

```
classes: dict[str, Class]
```

The class members.

This method is part of the consumer API: do not use when producing Griffe trees!

## deprecated

```
deprecated: bool | str | None = None
```

Whether this object is deprecated (boolean or deprecation message).

## docstring

```
docstring: Docstring | None = docstring
```

The object docstring.

See also: has_docstring, has_docstrings.

## endlineno

```
endlineno: int | None = endlineno
```

The ending line number of the object.

See also: lineno.

## exports

```
exports: list[str | ExprName] | None = None
```

The names of the objects exported by this (module) object through the `__all__` variable.

Exports can contain string (object names) or resolvable names, like other lists of exports coming from submodules:

```
from .submodule import __all__ as submodule_all

__all__ = ["hello", *submodule_all]
```

Exports get expanded by the loader before it expands wildcards and resolves aliases.

See also: GriffeLoader.expand_exports.

## extra

```
extra: dict[str, dict[str, Any]] = defaultdict(dict)
```

Namespaced dictionaries storing extra metadata for this object, used by extensions.

## filepath

```
filepath: Path | list[Path]
```

The file path of this module.

Raises:

- `BuiltinModuleError` – When the instance filepath is None.

## functions

```
functions: dict[str, Function]
```

The function members.

This method is part of the consumer API: do not use when producing Griffe trees!

## git_info

```
git_info: GitInfo | None
```

Git information for this object, if available.

## has_docstring

```
has_docstring: bool
```

Whether this object has a docstring (empty or not).

See also: docstring, has_docstrings.

## has_docstrings

```
has_docstrings: bool
```

Whether this object or any of its members has a docstring (empty or not).

Inherited members are not considered. Imported members are not considered, unless they are also public.

See also: docstring, has_docstring.

## imports

```
imports: dict[str, str] = {}
```

The other objects imported by this object.

Keys are the names within the object (`from ... import ... as AS_NAME`), while the values are the actual names of the objects (`from ... import REAL_NAME as ...`).

## imports_future_annotations

```
imports_future_annotations: bool
```

Whether this module import future annotations.

## inherited

```
inherited: bool = False
```

Always false for objects.

Only aliases can be marked as inherited.

## inherited_members

```
inherited_members: dict[str, Alias]
```

Members that are inherited from base classes.

This method is part of the consumer API: do not use when producing Griffe trees!

See also: members.

## is_alias

```
is_alias: bool = False
```

Always false for objects.

## is_attribute

```
is_attribute: bool
```

Whether this object is an attribute.

See also: is_module. is_class, is_function, is_type_alias, is_alias, is_kind.

## is_class

```
is_class: bool
```

Whether this object is a class.

See also: is_module. is_function, is_attribute, is_type_alias, is_alias, is_kind.

## is_class_private

```
is_class_private: bool
```

Whether this object/alias is class-private (starts with `__` and is a class member).

## is_collection

```
is_collection: bool = False
```

Always false for objects.

## is_deprecated

```
is_deprecated: bool
```

Whether this object is deprecated.

## is_exported

```
is_exported: bool
```

Whether this object/alias is exported (listed in `__all__`).

## is_function

```
is_function: bool
```

Whether this object is a function.

See also: is_module. is_class, is_attribute, is_type_alias, is_alias, is_kind.

## is_generic

```
is_generic: bool
```

Whether this object is generic.

## is_imported

```
is_imported: bool
```

Whether this object/alias was imported from another module.

## is_init_method

```
is_init_method: bool
```

Whether this function is an `__init__` method.

## is_init_module

```
is_init_module: bool
```

Whether this module is an `__init__.py` module.

See also: is_module.

## is_module

```
is_module: bool
```

Whether this object is a module.

See also: is_init_module. is_class, is_function, is_attribute, is_type_alias, is_alias, is_kind.

## is_namespace_package

```
is_namespace_package: bool
```

Whether this module is a namespace package (top folder, no `__init__.py`).

See also: is_namespace_subpackage.

## is_namespace_subpackage

```
is_namespace_subpackage: bool
```

Whether this module is a namespace subpackage.

See also: is_namespace_package.

## is_package

```
is_package: bool
```

Whether this module is a package (top module).

See also: is_subpackage.

## is_private

```
is_private: bool
```

Whether this object/alias is private (starts with `_`) but not special.

## is_public

```
is_public: bool
```

Whether this object is considered public.

In modules, developers can mark objects as public thanks to the `__all__` variable. In classes however, there is no convention or standard to do so.

Therefore, to decide whether an object is public, we follow this algorithm:

- If the object's `public` attribute is set (boolean), return its value.
- If the object is listed in its parent's (a module) `__all__` attribute, it is public.
- If the parent (module) defines `__all__` and the object is not listed in, it is private.
- If the object has a private name, it is private.
- If the object was imported from another module, it is private.
- Otherwise, the object is public.

## is_special

```
is_special: bool
```

Whether this object/alias is special ("dunder" attribute/method, starts and end with `__`).

## is_subpackage

```
is_subpackage: bool
```

Whether this module is a subpackage.

See also: is_package.

## is_type_alias

```
is_type_alias: bool
```

Whether this object is a type alias.

See also: is_module. is_class, is_function, is_attribute, is_alias, is_kind.

## is_wildcard_exposed

```
is_wildcard_exposed: bool
```

Whether this object/alias is exposed to wildcard imports.

To be exposed to wildcard imports, an object/alias must:

- be available at runtime
- have a module as parent
- be listed in `__all__` if `__all__` is defined
- or not be private (having a name starting with an underscore)

Special case for Griffe trees: a submodule is only exposed if its parent imports it.

Returns:

- `bool` – True or False.

## kind

```
kind = MODULE
```

The object kind.

## labels

```
labels: set[str] = set()
```

The object labels (`property`, `dataclass`, etc.).

See also: has_labels.

## lineno

```
lineno: int | None = lineno
```

The starting line number of the object.

See also: endlineno.

## lines

```
lines: list[str]
```

The lines containing the source of this object.

See also: lines_collection, source.

## lines_collection

```
lines_collection: LinesCollection
```

The lines collection attached to this object or its parents.

See also: lines, source.

Raises:

- `ValueError` – When no modules collection can be found in the object or its parents.

## members

```
members: dict[str, Object | Alias] = {}
```

The object members (modules, classes, functions, attributes, type aliases).

See also: inherited_members, get_member, set_member, filter_members.

## module

```
module: Module
```

The parent module of this object.

See also: package.

Examples:

```
>>> import griffe
>>> markdown = griffe.load("markdown")
>>> markdown["core.Markdown.references"].module
Module(PosixPath('~/project/.venv/lib/python3.11/site-packages/markdown/core.py'))
>>> # The `module` of a module is itself.
>>> markdown["core"].module
Module(PosixPath('~/project/.venv/lib/python3.11/site-packages/markdown/core.py'))
```

Raises:

- `ValueError` – When the object is not a module and does not have a parent.

## modules

```
modules: dict[str, Module]
```

The module members.

This method is part of the consumer API: do not use when producing Griffe trees!

## modules_collection

```
modules_collection: ModulesCollection
```

The modules collection attached to this object or its parents.

Raises:

- `ValueError` – When no modules collection can be found in the object or its parents.

## name

```
name: str = name
```

The object name.

## overloads

```
overloads: dict[str, list[Function]] = defaultdict(list)
```

The overloaded signatures declared in this module.

## package

```
package: Module
```

The absolute top module (the package) of this object.

See also: module.

Examples:

```
>>> import griffe
>>> markdown = griffe.load("markdown")
>>> markdown["core.Markdown.references"].package
Module(PosixPath('~/project/.venv/lib/python3.11/site-packages/markdown/__init__.py'))
```

## parent

```
parent: Module | Class | None = parent
```

The parent of the object (none if top module).

## path

```
path: str
```

The dotted path of this object.

On regular objects (not aliases), the path is the canonical path.

See also: canonical_path.

Examples:

```
>>> import griffe
>>> markdown = griffe.load("markdown")
>>> markdown["core.Markdown.references"].path
'markdown.core.Markdown.references'
```

## public

```
public: bool | None = None
```

Whether this object is public.

## relative_filepath

```
relative_filepath: Path
```

The file path where this object was defined, relative to the current working directory.

If this object's file path is not relative to the current working directory, return its absolute path.

See also: filepath, relative_package_filepath.

Raises:

- `ValueError` – When the relative path could not be computed.

## relative_package_filepath

```
relative_package_filepath: Path
```

The file path where this object was defined, relative to the top module path.

See also: filepath, relative_filepath.

Raises:

- `ValueError` – When the relative path could not be computed.

## runtime

```
runtime: bool = runtime
```

Whether this object is available at runtime.

Typically, type-guarded objects (under an `if TYPE_CHECKING` condition) are not available at runtime.

## source

```
source: str
```

The source code of this object.

See also: lines, lines_collection.

## source_link

```
source_link: str | None
```

Source link for this object, if available.

## type_aliases

```
type_aliases: dict[str, TypeAlias]
```

The type alias members.

This method is part of the consumer API: do not use when producing Griffe trees!

## type_parameters

```
type_parameters: TypeParameters = (
    type_parameters or TypeParameters()
)
```

The object type parameters.

## __bool__

```
__bool__() -> bool
```

An object is always true-ish.

Source code in `packages/griffelib/src/griffe/_internal/models.py`

```
def __bool__(self) -> bool:
    """An object is always true-ish."""
    return True
```

## __delitem__

```
__delitem__(key: str | Sequence[str]) -> None
```

Delete a member with its name or path.

This method is part of the consumer API: do not use when producing Griffe trees!

Members will be looked up in both declared members and inherited ones, triggering computation of the latter.

Parameters:

- ### **`key`**

  (`str | Sequence[str]`) – The name or path of the member.

Examples:

```
>>> del griffe_object["foo"]
>>> del griffe_object["path.to.bar"]
>>> del griffe_object[("path", "to", "qux")]
```

Source code in `packages/griffelib/src/griffe/_internal/mixins.py`

```
def __delitem__(self, key: str | Sequence[str]) -> None:
    """Delete a member with its name or path.

    This method is part of the consumer API:
    do not use when producing Griffe trees!

    Members will be looked up in both declared members and inherited ones,
    triggering computation of the latter.

    Parameters:
        key: The name or path of the member.

    Examples:
        >>> del griffe_object["foo"]
        >>> del griffe_object["path.to.bar"]
        >>> del griffe_object[("path", "to", "qux")]
    """
    parts = _get_parts(key)
    if len(parts) == 1:
        name = parts[0]
        try:
            del self.members[name]  # ty:ignore[unresolved-attribute]
        except KeyError:
            del self.inherited_members[name]  # ty:ignore[unresolved-attribute]
    else:
        del self.all_members[parts[0]][parts[1:]]  # ty:ignore[unresolved-attribute]
```

## __getitem__

```
__getitem__(key: str | Sequence[str]) -> Any
```

Get a member with its name or path.

This method is part of the consumer API: do not use when producing Griffe trees!

Members will be looked up in both declared members and inherited ones, triggering computation of the latter.

Parameters:

- ### **`key`**

  (`str | Sequence[str]`) – The name or path of the member.

Examples:

```
>>> foo = griffe_object["foo"]
>>> bar = griffe_object["path.to.bar"]
>>> qux = griffe_object[("path", "to", "qux")]
```

Source code in `packages/griffelib/src/griffe/_internal/mixins.py`

```
def __getitem__(self, key: str | Sequence[str]) -> Any:
    """Get a member with its name or path.

    This method is part of the consumer API:
    do not use when producing Griffe trees!

    Members will be looked up in both declared members and inherited ones,
    triggering computation of the latter.

    Parameters:
        key: The name or path of the member.

    Examples:
        >>> foo = griffe_object["foo"]
        >>> bar = griffe_object["path.to.bar"]
        >>> qux = griffe_object[("path", "to", "qux")]
    """
    parts = _get_parts(key)
    if len(parts) == 1:
        return self.all_members[parts[0]]  # ty:ignore[unresolved-attribute]
    return self.all_members[parts[0]][parts[1:]]  # ty:ignore[unresolved-attribute]
```

## __len__

```
__len__() -> int
```

The number of members in this object, recursively.

Source code in `packages/griffelib/src/griffe/_internal/models.py`

```
def __len__(self) -> int:
    """The number of members in this object, recursively."""
    return len(self.members) + sum(len(member) for member in self.members.values())
```

## __setitem__

```
__setitem__(
    key: str | Sequence[str], value: Object | Alias
) -> None
```

Set a member with its name or path.

This method is part of the consumer API: do not use when producing Griffe trees!

Parameters:

- ### **`key`**

  (`str | Sequence[str]`) – The name or path of the member.

- ### **`value`**

  (`Object | Alias`) – The member.

Examples:

```
>>> griffe_object["foo"] = foo
>>> griffe_object["path.to.bar"] = bar
>>> griffe_object[("path", "to", "qux")] = qux
```

Source code in `packages/griffelib/src/griffe/_internal/mixins.py`

```
def __setitem__(self, key: str | Sequence[str], value: Object | Alias) -> None:
    """Set a member with its name or path.

    This method is part of the consumer API:
    do not use when producing Griffe trees!

    Parameters:
        key: The name or path of the member.
        value: The member.

    Examples:
        >>> griffe_object["foo"] = foo
        >>> griffe_object["path.to.bar"] = bar
        >>> griffe_object[("path", "to", "qux")] = qux
    """
    parts = _get_parts(key)
    if len(parts) == 1:
        name = parts[0]
        self.members[name] = value  # ty:ignore[unresolved-attribute]
        if self.is_collection:  # ty:ignore[unresolved-attribute]
            value._modules_collection = self  # ty:ignore[invalid-assignment]
        else:
            value.parent = self  # ty:ignore[invalid-assignment]
    else:
        self.members[parts[0]][parts[1:]] = value  # ty:ignore[unresolved-attribute]
```

## as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this module's data as a dictionary.

See also: as_json.

Parameters:

- ### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

Source code in `packages/griffelib/src/griffe/_internal/models.py`

```
def as_dict(self, **kwargs: Any) -> dict[str, Any]:
    """Return this module's data as a dictionary.

    See also: [`as_json`][griffe.Module.as_json].

    Parameters:
        **kwargs: Additional serialization options.

    Returns:
        A dictionary.
    """
    base = super().as_dict(**kwargs)
    if isinstance(self._filepath, list):
        base["filepath"] = [str(path) for path in self._filepath]
    elif self._filepath:
        base["filepath"] = str(self._filepath)
    else:
        base["filepath"] = None
    return base
```

## as_json

```
as_json(*, full: bool = False, **kwargs: Any) -> str
```

Return this object's data as a JSON string.

Parameters:

- ### **`full`**

  (`bool`, default: `False` ) – Whether to return full info, or just base info.

- ### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options passed to encoder.

Returns:

- `str` – A JSON string.

Source code in `packages/griffelib/src/griffe/_internal/mixins.py`

```
def as_json(self, *, full: bool = False, **kwargs: Any) -> str:
    """Return this object's data as a JSON string.

    Parameters:
        full: Whether to return full info, or just base info.
        **kwargs: Additional serialization options passed to encoder.

    Returns:
        A JSON string.
    """
    from griffe._internal.encoders import JSONEncoder  # Avoid circular import.  # noqa: PLC0415

    return json.dumps(self, cls=JSONEncoder, full=full, **kwargs)
```

## del_member

```
del_member(key: str | Sequence[str]) -> None
```

Delete a member with its name or path.

This method is part of the producer API: you can use it safely while building Griffe trees (for example in Griffe extensions).

Members will be looked up in declared members only, not inherited ones.

Parameters:

- ### **`key`**

  (`str | Sequence[str]`) – The name or path of the member.

Examples:

```
>>> griffe_object.del_member("foo")
>>> griffe_object.del_member("path.to.bar")
>>> griffe_object.del_member(("path", "to", "qux"))
```

Source code in `packages/griffelib/src/griffe/_internal/mixins.py`

```
def del_member(self, key: str | Sequence[str]) -> None:
    """Delete a member with its name or path.

    This method is part of the producer API:
    you can use it safely while building Griffe trees
    (for example in Griffe extensions).

    Members will be looked up in declared members only, not inherited ones.

    Parameters:
        key: The name or path of the member.

    Examples:
        >>> griffe_object.del_member("foo")
        >>> griffe_object.del_member("path.to.bar")
        >>> griffe_object.del_member(("path", "to", "qux"))
    """
    parts = _get_parts(key)
    if len(parts) == 1:
        name = parts[0]
        del self.members[name]  # ty:ignore[unresolved-attribute]
    else:
        self.members[parts[0]].del_member(parts[1:])  # ty:ignore[unresolved-attribute]
```

## filter_members

```
filter_members(
    *predicates: Callable[[Object | Alias], bool],
) -> dict[str, Object | Alias]
```

Filter and return members based on predicates.

See also: members.

Parameters:

- ### **`*predicates`**

  (`Callable[[Object | Alias], bool]`, default: `()` ) – A list of predicates, i.e. callables accepting a member as argument and returning a boolean.

Returns:

- `dict[str, Object | Alias]` – A dictionary of members.

Source code in `packages/griffelib/src/griffe/_internal/models.py`

```
def filter_members(self, *predicates: Callable[[Object | Alias], bool]) -> dict[str, Object | Alias]:
    """Filter and return members based on predicates.

    See also: [`members`][griffe.Object.members].

    Parameters:
        *predicates: A list of predicates, i.e. callables accepting a member as argument and returning a boolean.

    Returns:
        A dictionary of members.
    """
    if not predicates:
        return self.members
    members: dict[str, Object | Alias] = {
        name: member for name, member in self.members.items() if all(predicate(member) for predicate in predicates)
    }
    return members
```

## from_json

```
from_json(json_string: str, **kwargs: Any) -> _ObjType
```

Create an instance of this class from a JSON string.

Parameters:

- ### **`json_string`**

  (`str`) – JSON to decode into Object.

- ### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional options passed to decoder.

Returns:

- `_ObjType` – An Object instance.

Raises:

- `TypeError` – When the json_string does not represent and object of the class from which this classmethod has been called.

Source code in `packages/griffelib/src/griffe/_internal/mixins.py`

```
@classmethod
def from_json(cls: type[_ObjType], json_string: str, **kwargs: Any) -> _ObjType:  # noqa: PYI019
    """Create an instance of this class from a JSON string.

    Parameters:
        json_string: JSON to decode into Object.
        **kwargs: Additional options passed to decoder.

    Returns:
        An Object instance.

    Raises:
        TypeError: When the json_string does not represent and object
            of the class from which this classmethod has been called.
    """
    from griffe._internal.encoders import json_decoder  # Avoid circular import.  # noqa: PLC0415

    kwargs.setdefault("object_hook", json_decoder)
    obj = json.loads(json_string, **kwargs)
    if not isinstance(obj, cls):
        raise TypeError(f"provided JSON object is not of type {cls}")
    return obj
```

## get_member

```
get_member(key: str | Sequence[str]) -> Any
```

Get a member with its name or path.

This method is part of the producer API: you can use it safely while building Griffe trees (for example in Griffe extensions).

Members will be looked up in declared members only, not inherited ones.

Parameters:

- ### **`key`**

  (`str | Sequence[str]`) – The name or path of the member.

Examples:

```
>>> foo = griffe_object["foo"]
>>> bar = griffe_object["path.to.bar"]
>>> bar = griffe_object[("path", "to", "bar")]
```

Source code in `packages/griffelib/src/griffe/_internal/mixins.py`

```
def get_member(self, key: str | Sequence[str]) -> Any:
    """Get a member with its name or path.

    This method is part of the producer API:
    you can use it safely while building Griffe trees
    (for example in Griffe extensions).

    Members will be looked up in declared members only, not inherited ones.

    Parameters:
        key: The name or path of the member.

    Examples:
        >>> foo = griffe_object["foo"]
        >>> bar = griffe_object["path.to.bar"]
        >>> bar = griffe_object[("path", "to", "bar")]
    """
    parts = _get_parts(key)
    if len(parts) == 1:
        return self.members[parts[0]]  # ty:ignore[unresolved-attribute]
    return self.members[parts[0]].get_member(parts[1:])  # ty:ignore[unresolved-attribute]
```

## has_labels

```
has_labels(*labels: str) -> bool
```

Tell if this object has all the given labels.

See also: labels.

Parameters:

- ### **`*labels`**

  (`str`, default: `()` ) – Labels that must be present.

Returns:

- `bool` – True or False.

Source code in `packages/griffelib/src/griffe/_internal/models.py`

```
def has_labels(self, *labels: str) -> bool:
    """Tell if this object has all the given labels.

    See also: [`labels`][griffe.Object.labels].

    Parameters:
        *labels: Labels that must be present.

    Returns:
        True or False.
    """
    return set(labels).issubset(self.labels)
```

## is_kind

```
is_kind(kind: str | Kind | set[str | Kind]) -> bool
```

Tell if this object is of the given kind.

See also: is_module, is_class, is_function, is_attribute, is_type_alias, is_alias.

Parameters:

- ### **`kind`**

  (`str | Kind | set[str | Kind]`) – An instance or set of kinds (strings or enumerations).

Raises:

- `ValueError` – When an empty set is given as argument.

Returns:

- `bool` – True or False.

Source code in `packages/griffelib/src/griffe/_internal/models.py`

```
def is_kind(self, kind: str | Kind | set[str | Kind]) -> bool:
    """Tell if this object is of the given kind.

    See also: [`is_module`][griffe.Object.is_module],
    [`is_class`][griffe.Object.is_class],
    [`is_function`][griffe.Object.is_function],
    [`is_attribute`][griffe.Object.is_attribute],
    [`is_type_alias`][griffe.Object.is_type_alias],
    [`is_alias`][griffe.Object.is_alias].

    Parameters:
        kind: An instance or set of kinds (strings or enumerations).

    Raises:
        ValueError: When an empty set is given as argument.

    Returns:
        True or False.
    """
    if isinstance(kind, set):
        if not kind:
            raise ValueError("kind must not be an empty set")
        return self.kind in (knd if isinstance(knd, Kind) else Kind(knd) for knd in kind)
    if isinstance(kind, str):
        kind = Kind(kind)
    return self.kind is kind
```

## resolve

```
resolve(name: str) -> str
```

Resolve a name within this object's and parents' scope.

Parameters:

- ### **`name`**

  (`str`) – The name to resolve.

Raises:

- `NameResolutionError` – When the name could not be resolved.

Returns:

- `str` – The resolved name.

Source code in `packages/griffelib/src/griffe/_internal/models.py`

```
def resolve(self, name: str) -> str:
    """Resolve a name within this object's and parents' scope.

    Parameters:
        name: The name to resolve.

    Raises:
        NameResolutionError: When the name could not be resolved.

    Returns:
        The resolved name.
    """
    # TODO: Better match Python's own scoping rules?
    # Also, maybe return regular paths instead of canonical ones?

    # Name is a type parameter.
    if name in self.type_parameters:
        type_parameter = self.type_parameters[name]
        if type_parameter.kind is TypeParameterKind.type_var_tuple:
            prefix = "*"
        elif type_parameter.kind is TypeParameterKind.param_spec:
            prefix = "**"
        else:
            prefix = ""
        return f"{self.path}[{prefix}{name}]"

    # Name is a member of this object.
    if name in self.members:
        if self.members[name].is_alias:
            return self.members[name].target_path  # ty:ignore[possibly-missing-attribute]
        return self.members[name].path

    # Name unknown and no more parent scope, could be a built-in.
    if self.parent is None:
        raise NameResolutionError(f"{name} could not be resolved in the scope of {self.path}")

    # Name is parent, non-module object.
    if name == self.parent.name and not self.parent.is_module:
        return self.parent.path

    # Recurse in parent.
    return self.parent.resolve(name)
```

## set_member

```
set_member(
    key: str | Sequence[str], value: Object | Alias
) -> None
```

Set a member with its name or path.

This method is part of the producer API: you can use it safely while building Griffe trees (for example in Griffe extensions).

Parameters:

- ### **`key`**

  (`str | Sequence[str]`) – The name or path of the member.

- ### **`value`**

  (`Object | Alias`) – The member.

Examples:

```
>>> griffe_object.set_member("foo", foo)
>>> griffe_object.set_member("path.to.bar", bar)
>>> griffe_object.set_member(("path", "to", "qux"), qux)
```

Source code in `packages/griffelib/src/griffe/_internal/mixins.py`

```
def set_member(self, key: str | Sequence[str], value: Object | Alias) -> None:
    """Set a member with its name or path.

    This method is part of the producer API:
    you can use it safely while building Griffe trees
    (for example in Griffe extensions).

    Parameters:
        key: The name or path of the member.
        value: The member.

    Examples:
        >>> griffe_object.set_member("foo", foo)
        >>> griffe_object.set_member("path.to.bar", bar)
        >>> griffe_object.set_member(("path", "to", "qux"), qux)
    """
    parts = _get_parts(key)
    if len(parts) == 1:
        name = parts[0]
        if name in self.members:  # ty:ignore[unresolved-attribute]
            member = self.members[name]  # ty:ignore[unresolved-attribute]
            if not member.is_alias:
                # When reassigning a module to an existing one,
                # try to merge them as one regular and one stubs module
                # (implicit support for .pyi modules).
                if member.is_module and not (member.is_namespace_package or member.is_namespace_subpackage):
                    # Accessing attributes of the value or member can trigger alias errors.
                    # Accessing file paths can trigger a builtin module error.
                    with suppress(AliasResolutionError, CyclicAliasError, BuiltinModuleError):
                        if value.is_module and value.filepath != member.filepath:
                            with suppress(ValueError):
                                value = merge_stubs(member, value)  # ty:ignore[invalid-argument-type]
                for alias in member.aliases.values():
                    with suppress(CyclicAliasError):
                        alias.target = value
        self.members[name] = value  # ty:ignore[unresolved-attribute]
        if self.is_collection:  # ty:ignore[unresolved-attribute]
            value._modules_collection = self  # ty:ignore[invalid-assignment]
        else:
            value.parent = self  # ty:ignore[invalid-assignment]
    else:
        self.members[parts[0]].set_member(parts[1:], value)  # ty:ignore[unresolved-attribute]
```
