# Alias

```
Alias(
    name: str,
    target: str | Object | Alias,
    *,
    lineno: int | None = None,
    endlineno: int | None = None,
    runtime: bool = True,
    parent: Module | Class | Alias | None = None,
    inherited: bool = False,
)

```

Bases: `ObjectAliasMixin`

```

              flowchart TD
              griffe.Alias[Alias]
              griffe._internal.mixins.ObjectAliasMixin[ObjectAliasMixin]
              griffe._internal.mixins.GetMembersMixin[GetMembersMixin]
              griffe._internal.mixins.SetMembersMixin[SetMembersMixin]
              griffe._internal.mixins.DelMembersMixin[DelMembersMixin]
              griffe._internal.mixins.SerializationMixin[SerializationMixin]

                              griffe._internal.mixins.ObjectAliasMixin --> griffe.Alias
                                griffe._internal.mixins.GetMembersMixin --> griffe._internal.mixins.ObjectAliasMixin
                
                griffe._internal.mixins.SetMembersMixin --> griffe._internal.mixins.ObjectAliasMixin
                
                griffe._internal.mixins.DelMembersMixin --> griffe._internal.mixins.ObjectAliasMixin
                
                griffe._internal.mixins.SerializationMixin --> griffe._internal.mixins.ObjectAliasMixin
                



              click griffe.Alias href "" "griffe.Alias"
              click griffe._internal.mixins.ObjectAliasMixin href "" "griffe._internal.mixins.ObjectAliasMixin"
              click griffe._internal.mixins.GetMembersMixin href "" "griffe._internal.mixins.GetMembersMixin"
              click griffe._internal.mixins.SetMembersMixin href "" "griffe._internal.mixins.SetMembersMixin"
              click griffe._internal.mixins.DelMembersMixin href "" "griffe._internal.mixins.DelMembersMixin"
              click griffe._internal.mixins.SerializationMixin href "" "griffe._internal.mixins.SerializationMixin"
            
```

This class represents an alias, or indirection, to an object declared in another module.

Aliases represent objects that are in the scope of a module or class, but were imported from another module.

They behave almost exactly like regular objects, to a few exceptions:

- line numbers are those of the alias, not the target
- the path is the alias path, not the canonical one
- the name can be different from the target's
- if the target can be resolved, the kind is the target's kind
- if the target cannot be resolved, the kind becomes Kind.ALIAS

Parameters:

- ## **`name`**

  (`str`) – The alias name.

- ## **`target`**

  (`str | Object | Alias`) – If it's a string, the target resolution is delayed until accessing the target property. If it's an object, or even another alias, the target is immediately set.

- ## **`lineno`**

  (`int | None`, default: `None` ) – The alias starting line number.

- ## **`endlineno`**

  (`int | None`, default: `None` ) – The alias ending line number.

- ## **`runtime`**

  (`bool`, default: `True` ) – Whether this alias is present at runtime or not.

- ## **`parent`**

  (`Module | Class | Alias | None`, default: `None` ) – The alias parent.

- ## **`inherited`**

  (`bool`, default: `False` ) – Whether this alias wraps an inherited member.

Methods:

- **`__bool__`** – An alias is always true-ish.
- **`__delitem__`** – Delete a member with its name or path.
- **`__getitem__`** – Get a member with its name or path.
- **`__len__`** – The length of an alias is always 1.
- **`__setitem__`** – Set a member with its name or path.
- **`as_dict`** – Return this alias' data as a dictionary.
- **`as_json`** – Return this target's data as a JSON string.
- **`del_member`** – Delete a member with its name or path.
- **`filter_members`** – Filter and return members based on predicates.
- **`from_json`** – Create an instance of this class from a JSON string.
- **`get_member`** – Get a member with its name or path.
- **`has_labels`** – Tell if this object has all the given labels.
- **`is_kind`** – Tell if this object is of the given kind.
- **`mro`** – Return a list of classes in order corresponding to Python's MRO.
- **`resolve`** – Resolve a name within this object's and parents' scope.
- **`resolve_target`** – Resolve the target.
- **`set_member`** – Set a member with its name or path.
- **`signature`** – Construct the class/function signature.

Attributes:

- **`alias_endlineno`** (`int | None`) – The ending line number of the alias.
- **`alias_lineno`** (`int | None`) – The starting line number of the alias.
- **`aliases`** (`dict[str, Alias]`) – The aliases pointing to this object.
- **`all_members`** (`dict[str, Object | Alias]`) – All members (declared and inherited).
- **`annotation`** (`str | Expr | None`) – The attribute type annotation.
- **`attributes`** (`dict[str, Attribute]`) – The attribute members.
- **`bases`** (`list[Expr | str]`) – The class bases.
- **`canonical_path`** (`str`) – The full dotted path of this object.
- **`classes`** (`dict[str, Class]`) – The class members.
- **`decorators`** (`list[Decorator]`) – The class/function decorators.
- **`deleter`** (`Function | None`) – The deleter linked to this function (property).
- **`deprecated`** (`str | bool | None`) – Whether this alias is deprecated (boolean or deprecation message).
- **`docstring`** (`Docstring | None`) – The target docstring.
- **`endlineno`** (`int | None`) – The ending line number of the target object.
- **`exports`** (`list[str | ExprName] | None`) – The names of the objects exported by this (module) object through the __all__ variable.
- **`extra`** (`dict`) – Namespaced dictionaries storing extra metadata for this object, used by extensions.
- **`filepath`** (`Path | list[Path]`) – The file path (or directory list for namespace packages) where this object was defined.
- **`final_target`** (`Object`) – The final, resolved target, if possible.
- **`functions`** (`dict[str, Function]`) – The function members.
- **`has_docstring`** (`bool`) – Whether this alias' target has a non-empty docstring.
- **`has_docstrings`** (`bool`) – Whether this alias' target or any of its members has a non-empty docstring.
- **`imports`** (`dict[str, str]`) – The other objects imported by this alias' target.
- **`imports_future_annotations`** (`bool`) – Whether this module import future annotations.
- **`inherited`** (`bool`) – Whether this alias represents an inherited member.
- **`inherited_members`** (`dict[str, Alias]`) – Members that are inherited from base classes.
- **`is_alias`** (`bool`) – Always true for aliases.
- **`is_attribute`** (`bool`) – Whether this object is an attribute.
- **`is_class`** (`bool`) – Whether this object is a class.
- **`is_class_private`** (`bool`) – Whether this object/alias is class-private (starts with \_\_ and is a class member).
- **`is_collection`** (`bool`) – Always false for aliases.
- **`is_deprecated`** (`bool`) – Whether this object is deprecated.
- **`is_exported`** (`bool`) – Whether this object/alias is exported (listed in __all__).
- **`is_function`** (`bool`) – Whether this object is a function.
- **`is_generic`** (`bool`) – Whether this object is generic.
- **`is_imported`** (`bool`) – Whether this object/alias was imported from another module.
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
- **`kind`** (`Kind`) – The target's kind, or Kind.ALIAS if the target cannot be resolved.
- **`labels`** (`set[str]`) – The target labels (property, dataclass, etc.).
- **`lineno`** (`int | None`) – The starting line number of the target object.
- **`lines`** (`list[str]`) – The lines containing the source of this object.
- **`lines_collection`** (`LinesCollection`) – The lines collection attached to this object or its parents.
- **`members`** (`dict[str, Object | Alias]`) – The target's members (modules, classes, functions, attributes, type aliases).
- **`module`** (`Module`) – The parent module of this object.
- **`modules`** (`dict[str, Module]`) – The module members.
- **`modules_collection`** (`ModulesCollection`) – The modules collection attached to the alias parents.
- **`name`** (`str`) – The alias name.
- **`overloads`** (`dict[str, list[Function]] | list[Function] | None`) – The overloaded signatures declared in this class/module or for this function.
- **`package`** (`Module`) – The absolute top module (the package) of this object.
- **`parameters`** (`Parameters`) – The parameters of the current function or __init__ method for classes.
- **`parent`** (`Module | Class | Alias | None`) – The parent of this alias.
- **`path`** (`str`) – The dotted path / import path of this object.
- **`public`** (`bool | None`) – Whether this alias is public.
- **`relative_filepath`** (`Path`) – The file path where this object was defined, relative to the current working directory.
- **`relative_package_filepath`** (`Path`) – The file path where this object was defined, relative to the top module path.
- **`resolved`** (`bool`) – Whether this alias' target is resolved.
- **`resolved_bases`** (`list[Object]`) – Resolved class bases.
- **`returns`** (`str | Expr | None`) – The function return type annotation.
- **`runtime`** (`bool`) – Whether this alias is available at runtime.
- **`setter`** (`Function | None`) – The setter linked to this function (property).
- **`source`** (`str`) – The source code of this object.
- **`target`** (`Object | Alias`) – The resolved target (actual object), if possible.
- **`target_path`** (`str`) – The path of this alias' target.
- **`type_aliases`** (`dict[str, TypeAlias]`) – The type alias members.
- **`type_parameters`** (`TypeParameters`) – The target type parameters.
- **`value`** (`str | Expr | None`) – The attribute or type alias value.
- **`wildcard`** (`str | None`) – The module on which the wildcard import is performed (if any).

## alias_endlineno

```
alias_endlineno: int | None = endlineno

```

The ending line number of the alias.

## alias_lineno

```
alias_lineno: int | None = lineno

```

The starting line number of the alias.

## aliases

```
aliases: dict[str, Alias]

```

The aliases pointing to this object.

## all_members

```
all_members: dict[str, Object | Alias]

```

All members (declared and inherited).

This method is part of the consumer API: do not use when producing Griffe trees!

## annotation

```
annotation: str | Expr | None

```

The attribute type annotation.

## attributes

```
attributes: dict[str, Attribute]

```

The attribute members.

This method is part of the consumer API: do not use when producing Griffe trees!

## bases

```
bases: list[Expr | str]

```

The class bases.

See also: Class, resolved_bases, mro.

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

## decorators

```
decorators: list[Decorator]

```

The class/function decorators.

See also: Function, Class.

## deleter

```
deleter: Function | None

```

The deleter linked to this function (property).

## deprecated

```
deprecated: str | bool | None = None

```

Whether this alias is deprecated (boolean or deprecation message).

## docstring

```
docstring: Docstring | None

```

The target docstring.

See also: has_docstring, has_docstrings.

## endlineno

```
endlineno: int | None

```

The ending line number of the target object.

See also: lineno.

## exports

```
exports: list[str | ExprName] | None

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
extra: dict

```

Namespaced dictionaries storing extra metadata for this object, used by extensions.

## filepath

```
filepath: Path | list[Path]

```

The file path (or directory list for namespace packages) where this object was defined.

See also: relative_filepath, relative_package_filepath.

## final_target

```
final_target: Object

```

The final, resolved target, if possible.

This will iterate through the targets until a non-alias object is found.

See also: target, resolve_target, resolved.

## functions

```
functions: dict[str, Function]

```

The function members.

This method is part of the consumer API: do not use when producing Griffe trees!

## has_docstring

```
has_docstring: bool

```

Whether this alias' target has a non-empty docstring.

See also: has_docstrings, docstring.

## has_docstrings

```
has_docstrings: bool

```

Whether this alias' target or any of its members has a non-empty docstring.

See also: has_docstring, docstring.

## imports

```
imports: dict[str, str]

```

The other objects imported by this alias' target.

Keys are the names within the object (`from ... import ... as AS_NAME`), while the values are the actual names of the objects (`from ... import REAL_NAME as ...`).

See also: is_imported.

## imports_future_annotations

```
imports_future_annotations: bool

```

Whether this module import future annotations.

## inherited

```
inherited: bool = inherited

```

Whether this alias represents an inherited member.

## inherited_members

```
inherited_members: dict[str, Alias]

```

Members that are inherited from base classes.

Each inherited member of the target will be wrapped in an alias, to preserve correct object access paths.

This method is part of the consumer API: do not use when producing Griffe trees!

See also: members.

## is_alias

```
is_alias: bool = True

```

Always true for aliases.

## is_attribute

```
is_attribute: bool

```

Whether this object is an attribute.

See also: is_module, is_class, is_function, is_type_alias, is_alias, is_kind.

## is_class

```
is_class: bool

```

Whether this object is a class.

See also: is_module, is_function, is_attribute, is_type_alias, is_alias, is_kind.

## is_class_private

```
is_class_private: bool

```

Whether this object/alias is class-private (starts with `__` and is a class member).

## is_collection

```
is_collection: bool = False

```

Always false for aliases.

See also: ModulesCollection.

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

See also: is_module, is_class, is_attribute, is_type_alias, is_alias, is_kind.

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

See also: is_module, is_class, is_function, is_attribute, is_alias, is_kind.

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
kind: Kind

```

The target's kind, or `Kind.ALIAS` if the target cannot be resolved.

See also: is_kind.

## labels

```
labels: set[str]

```

The target labels (`property`, `dataclass`, etc.).

See also: has_labels.

## lineno

```
lineno: int | None

```

The starting line number of the target object.

See also: endlineno.

## lines

```
lines: list[str]

```

The lines containing the source of this object.

See also: source, lines_collection.

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
members: dict[str, Object | Alias]

```

The target's members (modules, classes, functions, attributes, type aliases).

See also: inherited_members, get_member, set_member, filter_members.

## module

```
module: Module

```

The parent module of this object.

See also: package.

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

The modules collection attached to the alias parents.

## name

```
name: str = name

```

The alias name.

## overloads

```
overloads: dict[str, list[Function]] | list[Function] | None

```

The overloaded signatures declared in this class/module or for this function.

## package

```
package: Module

```

The absolute top module (the package) of this object.

See also: module.

## parameters

```
parameters: Parameters

```

The parameters of the current function or `__init__` method for classes.

This property can fetch inherited members, and therefore is part of the consumer API: do not use when producing Griffe trees!

## parent

```
parent: Module | Class | Alias | None

```

The parent of this alias.

## path

```
path: str

```

The dotted path / import path of this object.

See also: canonical_path.

## public

```
public: bool | None = None

```

Whether this alias is public.

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

## resolved

```
resolved: bool

```

Whether this alias' target is resolved.

## resolved_bases

```
resolved_bases: list[Object]

```

Resolved class bases.

This method is part of the consumer API: do not use when producing Griffe trees!

## returns

```
returns: str | Expr | None

```

The function return type annotation.

## runtime

```
runtime: bool = runtime

```

Whether this alias is available at runtime.

## setter

```
setter: Function | None

```

The setter linked to this function (property).

## source

```
source: str

```

The source code of this object.

See also: lines, lines_collection.

## target

```
target: Object | Alias

```

The resolved target (actual object), if possible.

Upon accessing this property, if the target is not already resolved, a lookup is done using the modules collection to find the target.

See also: final_target, resolve_target, resolved.

## target_path

```
target_path: str

```

The path of this alias' target.

## type_aliases

```
type_aliases: dict[str, TypeAlias]

```

The type alias members.

This method is part of the consumer API: do not use when producing Griffe trees!

## type_parameters

```
type_parameters: TypeParameters

```

The target type parameters.

## value

```
value: str | Expr | None

```

The attribute or type alias value.

## wildcard

```
wildcard: str | None

```

The module on which the wildcard import is performed (if any).

See also: GriffeLoader.expand_wildcards.

## __bool__

```
__bool__() -> bool

```

An alias is always true-ish.

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

## __len__

```
__len__() -> int

```

The length of an alias is always 1.

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

## as_dict

```
as_dict(
    *, full: bool = False, **kwargs: Any
) -> dict[str, Any]

```

Return this alias' data as a dictionary.

See also: as_json.

Parameters:

- ### **`full`**

  (`bool`, default: `False` ) – Whether to return full info, or just base info.

- ### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

## as_json

```
as_json(*, full: bool = False, **kwargs: Any) -> str

```

Return this target's data as a JSON string.

See also: as_dict.

Parameters:

- ### **`full`**

  (`bool`, default: `False` ) – Whether to return full info, or just base info.

- ### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options passed to encoder.

Returns:

- `str` – A JSON string.

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

## filter_members

```
filter_members(
    *predicates: Callable[[Object | Alias], bool],
) -> dict[str, Object | Alias]

```

Filter and return members based on predicates.

See also: members, get_member, set_member.

Parameters:

- ### **`*predicates`**

  (`Callable[[Object | Alias], bool]`, default: `()` ) – A list of predicates, i.e. callables accepting a member as argument and returning a boolean.

Returns:

- `dict[str, Object | Alias]` – A dictionary of members.

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

## mro

```
mro() -> list[Class]

```

Return a list of classes in order corresponding to Python's MRO.

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

## resolve_target

```
resolve_target() -> None

```

Resolve the target.

See also: target, final_target, resolved.

Raises:

- `AliasResolutionError` – When the target cannot be resolved. It happens when the target does not exist, or could not be loaded (unhandled dynamic object?), or when the target is from a module that was not loaded and added to the collection.
- `CyclicAliasError` – When the resolved target is the alias itself.

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

## signature

```
signature(
    *, return_type: bool = False, name: str | None = None
) -> str

```

Construct the class/function signature.

Parameters:

- ### **`return_type`**

  (`bool`, default: `False` ) – Whether to include the return type in the signature.

- ### **`name`**

  (`str | None`, default: `None` ) – The name of the class/function to use in the signature.

Returns:

- `str` – A string representation of the class/function signature.
