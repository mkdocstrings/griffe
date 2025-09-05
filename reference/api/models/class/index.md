# Class

```
Class(
    *args: Any,
    bases: Sequence[Expr | str] | None = None,
    decorators: list[Decorator] | None = None,
    **kwargs: Any,
)
```

Bases: `Object`

```
              flowchart TD
              griffe.Class[Class]
              griffe._internal.models.Object[Object]
              griffe._internal.mixins.ObjectAliasMixin[ObjectAliasMixin]
              griffe._internal.mixins.GetMembersMixin[GetMembersMixin]
              griffe._internal.mixins.SetMembersMixin[SetMembersMixin]
              griffe._internal.mixins.DelMembersMixin[DelMembersMixin]
              griffe._internal.mixins.SerializationMixin[SerializationMixin]

                              griffe._internal.models.Object --> griffe.Class
                                griffe._internal.mixins.ObjectAliasMixin --> griffe._internal.models.Object
                                griffe._internal.mixins.GetMembersMixin --> griffe._internal.mixins.ObjectAliasMixin
                
                griffe._internal.mixins.SetMembersMixin --> griffe._internal.mixins.ObjectAliasMixin
                
                griffe._internal.mixins.DelMembersMixin --> griffe._internal.mixins.ObjectAliasMixin
                
                griffe._internal.mixins.SerializationMixin --> griffe._internal.mixins.ObjectAliasMixin
                




              click griffe.Class href "" "griffe.Class"
              click griffe._internal.models.Object href "" "griffe._internal.models.Object"
              click griffe._internal.mixins.ObjectAliasMixin href "" "griffe._internal.mixins.ObjectAliasMixin"
              click griffe._internal.mixins.GetMembersMixin href "" "griffe._internal.mixins.GetMembersMixin"
              click griffe._internal.mixins.SetMembersMixin href "" "griffe._internal.mixins.SetMembersMixin"
              click griffe._internal.mixins.DelMembersMixin href "" "griffe._internal.mixins.DelMembersMixin"
              click griffe._internal.mixins.SerializationMixin href "" "griffe._internal.mixins.SerializationMixin"
```

The class representing a Python class.

Parameters:

- ## **`*args`**

  (`Any`, default: `()` ) – See griffe.Object.

- ## **`bases`**

  (`Sequence[Expr | str] | None`, default: `None` ) – The list of base classes, if any.

- ## **`decorators`**

  (`list[Decorator] | None`, default: `None` ) – The class decorators, if any.

- ## **`**kwargs`**

  (`Any`, default: `{}` ) – See griffe.Object.

Methods:

- **`__bool__`** – An object is always true-ish.
- **`__delitem__`** – Delete a member with its name or path.
- **`__getitem__`** – Get a member with its name or path.
- **`__len__`** – The number of members in this object, recursively.
- **`__setitem__`** – Set a member with its name or path.
- **`as_dict`** – Return this class' data as a dictionary.
- **`as_json`** – Return this object's data as a JSON string.
- **`del_member`** – Delete a member with its name or path.
- **`filter_members`** – Filter and return members based on predicates.
- **`from_json`** – Create an instance of this class from a JSON string.
- **`get_member`** – Get a member with its name or path.
- **`has_labels`** – Tell if this object has all the given labels.
- **`is_kind`** – Tell if this object is of the given kind.
- **`mro`** – Return a list of classes in order corresponding to Python's MRO.
- **`resolve`** – Resolve a name within this object's and parents' scope.
- **`set_member`** – Set a member with its name or path.
- **`signature`** – Construct the class signature.

Attributes:

- **`aliases`** (`dict[str, Alias]`) – The aliases pointing to this object.
- **`all_members`** (`dict[str, Object | Alias]`) – All members (declared and inherited).
- **`analysis`** (`Literal['static', 'dynamic'] | None`) – The type of analysis used to load this object.
- **`attributes`** (`dict[str, Attribute]`) – The attribute members.
- **`bases`** (`list[Expr | str]`) – The class bases.
- **`canonical_path`** (`str`) – The full dotted path of this object.
- **`classes`** (`dict[str, Class]`) – The class members.
- **`decorators`** (`list[Decorator]`) – The class decorators.
- **`deprecated`** (`bool | str | None`) – Whether this object is deprecated (boolean or deprecation message).
- **`docstring`** (`Docstring | None`) – The object docstring.
- **`endlineno`** (`int | None`) – The ending line number of the object.
- **`exports`** (`list[str | ExprName] | None`) – The names of the objects exported by this (module) object through the __all__ variable.
- **`extra`** (`dict[str, dict[str, Any]]`) – Namespaced dictionaries storing extra metadata for this object, used by extensions.
- **`filepath`** (`Path | list[Path]`) – The file path (or directory list for namespace packages) where this object was defined.
- **`functions`** (`dict[str, Function]`) – The function members.
- **`git_info`** (`GitInfo | None`) – Git information for this object, if available.
- **`has_docstring`** (`bool`) – Whether this object has a docstring (empty or not).
- **`has_docstrings`** (`bool`) – Whether this object or any of its members has a docstring (empty or not).
- **`imports`** (`dict[str, str]`) – The other objects imported by this object.
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
- **`is_init_module`** (`bool`) – Whether this object is an __init__.py module.
- **`is_module`** (`bool`) – Whether this object is a module.
- **`is_namespace_package`** (`bool`) – Whether this object is a namespace package (top folder, no __init__.py).
- **`is_namespace_subpackage`** (`bool`) – Whether this object is a namespace subpackage.
- **`is_package`** (`bool`) – Whether this object is a package (top module).
- **`is_private`** (`bool`) – Whether this object/alias is private (starts with \_) but not special.
- **`is_public`** (`bool`) – Whether this object is considered public.
- **`is_special`** (`bool`) – Whether this object/alias is special ("dunder" attribute/method, starts and end with \_\_).
- **`is_subpackage`** (`bool`) – Whether this object is a subpackage.
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
- **`overloads`** (`dict[str, list[Function]]`) – The overloaded signatures declared in this class.
- **`package`** (`Module`) – The absolute top module (the package) of this object.
- **`parameters`** (`Parameters`) – The parameters of this class' __init__ method, if any.
- **`parent`** (`Module | Class | None`) – The parent of the object (none if top module).
- **`path`** (`str`) – The dotted path of this object.
- **`public`** (`bool | None`) – Whether this object is public.
- **`relative_filepath`** (`Path`) – The file path where this object was defined, relative to the current working directory.
- **`relative_package_filepath`** (`Path`) – The file path where this object was defined, relative to the top module path.
- **`resolved_bases`** (`list[Object]`) – Resolved class bases.
- **`runtime`** (`bool`) – Whether this object is available at runtime.
- **`source`** (`str`) – The source code of this object.
- **`source_link`** (`str | None`) – Source link for this object, if available.
- **`type_aliases`** (`dict[str, TypeAlias]`) – The type alias members.
- **`type_parameters`** (`TypeParameters`) – The object type parameters.

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

## bases

```
bases: list[Expr | str] = list(bases) if bases else []
```

The class bases.

See also: resolved_bases, mro.

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
decorators: list[Decorator] = decorators or []
```

The class decorators.

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

The file path (or directory list for namespace packages) where this object was defined.

See also: relative_filepath, relative_package_filepath.

Examples:

```
>>> import griffe
>>> markdown = griffe.load("markdown")
>>> markdown.filepath
PosixPath('~/project/.venv/lib/python3.11/site-packages/markdown/__init__.py')
```

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

Whether this object is an `__init__.py` module.

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

Whether this object is a namespace package (top folder, no `__init__.py`).

See also: is_namespace_subpackage.

## is_namespace_subpackage

```
is_namespace_subpackage: bool
```

Whether this object is a namespace subpackage.

See also: is_namespace_package.

## is_package

```
is_package: bool
```

Whether this object is a package (top module).

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

Whether this object is a subpackage.

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
kind = CLASS
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

The overloaded signatures declared in this class.

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

## parameters

```
parameters: Parameters
```

The parameters of this class' `__init__` method, if any.

This property fetches inherited members, and therefore is part of the consumer API: do not use when producing Griffe trees!

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

## resolved_bases

```
resolved_bases: list[Object]
```

Resolved class bases.

This method is part of the consumer API: do not use when producing Griffe trees!

See also: bases, mro.

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

The number of members in this object, recursively.

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
as_dict(**kwargs: Any) -> dict[str, Any]
```

Return this class' data as a dictionary.

See also: as_json.

Parameters:

- ### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional serialization options.

Returns:

- `dict[str, Any]` – A dictionary.

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

See also: members.

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

See also: bases, resolved_bases.

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

Construct the class signature.

Parameters:

- ### **`return_type`**

  (`bool`, default: `False` ) – Whether to include the return type in the signature.

- ### **`name`**

  (`str | None`, default: `None` ) – The name of the class to use in the signature.

Returns:

- `str` – A string representation of the class signature.

## **Utilities**

## c3linear_merge

```
c3linear_merge(*lists: list[_T]) -> list[_T]
```

Merge lists of lists in the order defined by the C3Linear algorithm.

Parameters:

- ### **`*lists`**

  (`list[_T]`, default: `()` ) – Lists of items.

Returns:

- `list[_T]` – The merged list of items.
