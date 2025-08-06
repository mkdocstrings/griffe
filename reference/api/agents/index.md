# Agents

Griffe is able to analyze code both statically and dynamically.

## **Main API**

## visit

```
visit(
    module_name: str,
    filepath: Path,
    code: str,
    *,
    extensions: Extensions | None = None,
    parent: Module | None = None,
    docstring_parser: DocstringStyle | Parser | None = None,
    docstring_options: dict[str, Any] | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
) -> Module

```

Parse and visit a module file.

We provide this function for static analysis. It uses a NodeVisitor-like class, the Visitor, to compile and parse code (using compile) then visit the resulting AST (Abstract Syntax Tree).

Important

This function is generally not used directly. In most cases, users can rely on the GriffeLoader and its accompanying load shortcut and their respective options to load modules using static analysis.

Parameters:

- ### **`module_name`**

  (`str`) – The module name (as when importing [from] it).

- ### **`filepath`**

  (`Path`) – The module file path.

- ### **`code`**

  (`str`) – The module contents.

- ### **`extensions`**

  (`Extensions | None`, default: `None` ) – The extensions to use when visiting the AST.

- ### **`parent`**

  (`Module | None`, default: `None` ) – The optional parent of this module.

- ### **`docstring_parser`**

  (`DocstringStyle | Parser | None`, default: `None` ) – The docstring parser to use. By default, no parsing is done.

- ### **`docstring_options`**

  (`dict[str, Any] | None`, default: `None` ) – Additional docstring parsing options.

- ### **`lines_collection`**

  (`LinesCollection | None`, default: `None` ) – A collection of source code lines.

- ### **`modules_collection`**

  (`ModulesCollection | None`, default: `None` ) – A collection of modules.

Returns:

- `Module` – The module, with its members populated.

## inspect

```
inspect(
    module_name: str,
    *,
    filepath: Path | None = None,
    import_paths: Sequence[str | Path] | None = None,
    extensions: Extensions | None = None,
    parent: Module | None = None,
    docstring_parser: DocstringStyle | Parser | None = None,
    docstring_options: dict[str, Any] | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
) -> Module

```

Inspect a module.

Sometimes we cannot get the source code of a module or an object, typically built-in modules like `itertools`. The only way to know what they are made of is to actually import them and inspect their contents.

Sometimes, even if the source code is available, loading the object is desired because it was created or modified dynamically, and our static agent is not powerful enough to infer all these dynamic modifications. In this case, we load the module using introspection.

Griffe therefore provides this function for dynamic analysis. It uses a NodeVisitor-like class, the Inspector, to inspect the module with inspect.getmembers().

The inspection agent works similarly to the regular Visitor agent, in that it maintains a state with the current object being handled, and recursively handle its members.

Important

This function is generally not used directly. In most cases, users can rely on the GriffeLoader and its accompanying load shortcut and their respective options to load modules using dynamic analysis.

Parameters:

- ### **`module_name`**

  (`str`) – The module name (as when importing [from] it).

- ### **`filepath`**

  (`Path | None`, default: `None` ) – The module file path.

- ### **`import_paths`**

  (`Sequence[str | Path] | None`, default: `None` ) – Paths to import the module from.

- ### **`extensions`**

  (`Extensions | None`, default: `None` ) – The extensions to use when inspecting the module.

- ### **`parent`**

  (`Module | None`, default: `None` ) – The optional parent of this module.

- ### **`docstring_parser`**

  (`DocstringStyle | Parser | None`, default: `None` ) – The docstring parser to use. By default, no parsing is done.

- ### **`docstring_options`**

  (`dict[str, Any] | None`, default: `None` ) – Additional docstring parsing options.

- ### **`lines_collection`**

  (`LinesCollection | None`, default: `None` ) – A collection of source code lines.

- ### **`modules_collection`**

  (`ModulesCollection | None`, default: `None` ) – A collection of modules.

Returns:

- `Module` – The module, with its members populated.

## **Advanced API**

## Visitor

```
Visitor(
    module_name: str,
    filepath: Path,
    code: str,
    extensions: Extensions,
    parent: Module | None = None,
    docstring_parser: DocstringStyle | Parser | None = None,
    docstring_options: dict[str, Any] | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
)

```

This class is used to instantiate a visitor.

Visitors iterate on AST nodes to extract data from them.

Parameters:

- ### **`module_name`**

  (`str`) – The module name.

- ### **`filepath`**

  (`Path`) – The module filepath.

- ### **`code`**

  (`str`) – The module source code.

- ### **`extensions`**

  (`Extensions`) – The extensions to use when visiting.

- ### **`parent`**

  (`Module | None`, default: `None` ) – An optional parent for the final module object.

- ### **`docstring_parser`**

  (`DocstringStyle | Parser | None`, default: `None` ) – The docstring parser to use.

- ### **`docstring_options`**

  (`dict[str, Any] | None`, default: `None` ) – The docstring parsing options.

- ### **`lines_collection`**

  (`LinesCollection | None`, default: `None` ) – A collection of source code lines.

- ### **`modules_collection`**

  (`ModulesCollection | None`, default: `None` ) – A collection of modules.

Methods:

- **`decorators_to_labels`** – Build and return a set of labels based on decorators.
- **`generic_visit`** – Extend the base generic visit with extensions.
- **`get_base_property`** – Check decorators to return the base property in case of setters and deleters.
- **`get_module`** – Build and return the object representing the module attached to this visitor.
- **`handle_attribute`** – Handle an attribute (assignment) node.
- **`handle_function`** – Handle a function definition node.
- **`visit`** – Extend the base visit with extensions.
- **`visit_annassign`** – Visit an annotated assignment node.
- **`visit_assign`** – Visit an assignment node.
- **`visit_asyncfunctiondef`** – Visit an async function definition node.
- **`visit_augassign`** – Visit an augmented assignment node.
- **`visit_classdef`** – Visit a class definition node.
- **`visit_functiondef`** – Visit a function definition node.
- **`visit_if`** – Visit an "if" node.
- **`visit_import`** – Visit an import node.
- **`visit_importfrom`** – Visit an "import from" node.
- **`visit_module`** – Visit a module node.
- **`visit_typealias`** – Visit a type alias node.

Attributes:

- **`code`** (`str`) – The module source code.
- **`current`** (`Module | Class`) – The current object being visited.
- **`docstring_options`** (`dict[str, Any]`) – The docstring parsing options.
- **`docstring_parser`** (`DocstringStyle | Parser | None`) – The docstring parser to use.
- **`extensions`** (`Extensions`) – The extensions to use when visiting the AST.
- **`filepath`** (`Path`) – The module filepath.
- **`lines_collection`** (`LinesCollection`) – A collection of source code lines.
- **`module_name`** (`str`) – The module name.
- **`modules_collection`** (`ModulesCollection`) – A collection of modules.
- **`parent`** (`Module | None`) – An optional parent for the final module object.
- **`type_guarded`** (`bool`) – Whether the current code branch is type-guarded.

### code

```
code: str = code

```

The module source code.

### current

```
current: Module | Class = None

```

The current object being visited.

### docstring_options

```
docstring_options: dict[str, Any] = docstring_options or {}

```

The docstring parsing options.

### docstring_parser

```
docstring_parser: DocstringStyle | Parser | None = (
    docstring_parser
)

```

The docstring parser to use.

### extensions

```
extensions: Extensions = extensions

```

The extensions to use when visiting the AST.

### filepath

```
filepath: Path = filepath

```

The module filepath.

### lines_collection

```
lines_collection: LinesCollection = (
    lines_collection or LinesCollection()
)

```

A collection of source code lines.

### module_name

```
module_name: str = module_name

```

The module name.

### modules_collection

```
modules_collection: ModulesCollection = (
    modules_collection or ModulesCollection()
)

```

A collection of modules.

### parent

```
parent: Module | None = parent

```

An optional parent for the final module object.

### type_guarded

```
type_guarded: bool = False

```

Whether the current code branch is type-guarded.

### decorators_to_labels

```
decorators_to_labels(
    decorators: list[Decorator],
) -> set[str]

```

Build and return a set of labels based on decorators.

Parameters:

- #### **`decorators`**

  (`list[Decorator]`) – The decorators to check.

Returns:

- `set[str]` – A set of labels.

### generic_visit

```
generic_visit(node: AST) -> None

```

Extend the base generic visit with extensions.

Parameters:

- #### **`node`**

  (`AST`) – The node to visit.

### get_base_property

```
get_base_property(
    decorators: list[Decorator], function: Function
) -> str | None

```

Check decorators to return the base property in case of setters and deleters.

Parameters:

- #### **`decorators`**

  (`list[Decorator]`) – The decorators to check.

Returns:

- **`base_property`** ( `str | None` ) – The property for which the setter/deleted is set.
- **`property_function`** ( `str | None` ) – Either "setter" or "deleter".

### get_module

```
get_module() -> Module

```

Build and return the object representing the module attached to this visitor.

This method triggers a complete visit of the module nodes.

Returns:

- `Module` – A module instance.

### handle_attribute

```
handle_attribute(
    node: Assign | AnnAssign,
    annotation: str | Expr | None = None,
) -> None

```

Handle an attribute (assignment) node.

Parameters:

- #### **`node`**

  (`Assign | AnnAssign`) – The node to visit.

- #### **`annotation`**

  (`str | Expr | None`, default: `None` ) – A potential annotation.

### handle_function

```
handle_function(
    node: AsyncFunctionDef | FunctionDef,
    labels: set | None = None,
) -> None

```

Handle a function definition node.

Parameters:

- #### **`node`**

  (`AsyncFunctionDef | FunctionDef`) – The node to visit.

- #### **`labels`**

  (`set | None`, default: `None` ) – Labels to add to the data object.

### visit

```
visit(node: AST) -> None

```

Extend the base visit with extensions.

Parameters:

- #### **`node`**

  (`AST`) – The node to visit.

### visit_annassign

```
visit_annassign(node: AnnAssign) -> None

```

Visit an annotated assignment node.

Parameters:

- #### **`node`**

  (`AnnAssign`) – The node to visit.

### visit_assign

```
visit_assign(node: Assign) -> None

```

Visit an assignment node.

Parameters:

- #### **`node`**

  (`Assign`) – The node to visit.

### visit_asyncfunctiondef

```
visit_asyncfunctiondef(node: AsyncFunctionDef) -> None

```

Visit an async function definition node.

Parameters:

- #### **`node`**

  (`AsyncFunctionDef`) – The node to visit.

### visit_augassign

```
visit_augassign(node: AugAssign) -> None

```

Visit an augmented assignment node.

Parameters:

- #### **`node`**

  (`AugAssign`) – The node to visit.

### visit_classdef

```
visit_classdef(node: ClassDef) -> None

```

Visit a class definition node.

Parameters:

- #### **`node`**

  (`ClassDef`) – The node to visit.

### visit_functiondef

```
visit_functiondef(node: FunctionDef) -> None

```

Visit a function definition node.

Parameters:

- #### **`node`**

  (`FunctionDef`) – The node to visit.

### visit_if

```
visit_if(node: If) -> None

```

Visit an "if" node.

Parameters:

- #### **`node`**

  (`If`) – The node to visit.

### visit_import

```
visit_import(node: Import) -> None

```

Visit an import node.

Parameters:

- #### **`node`**

  (`Import`) – The node to visit.

### visit_importfrom

```
visit_importfrom(node: ImportFrom) -> None

```

Visit an "import from" node.

Parameters:

- #### **`node`**

  (`ImportFrom`) – The node to visit.

### visit_module

```
visit_module(node: Module) -> None

```

Visit a module node.

Parameters:

- #### **`node`**

  (`Module`) – The node to visit.

### visit_typealias

```
visit_typealias(node: TypeAlias) -> None

```

Visit a type alias node.

Parameters:

- #### **`node`**

  (`TypeAlias`) – The node to visit.

## Inspector

```
Inspector(
    module_name: str,
    filepath: Path | None,
    extensions: Extensions,
    parent: Module | None = None,
    docstring_parser: DocstringStyle | Parser | None = None,
    docstring_options: dict[str, Any] | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
)

```

This class is used to instantiate an inspector.

Inspectors iterate on objects members to extract data from them.

Parameters:

- ### **`module_name`**

  (`str`) – The module name.

- ### **`filepath`**

  (`Path | None`) – The optional filepath.

- ### **`extensions`**

  (`Extensions`) – Extensions to use when inspecting.

- ### **`parent`**

  (`Module | None`, default: `None` ) – The module parent.

- ### **`docstring_parser`**

  (`DocstringStyle | Parser | None`, default: `None` ) – The docstring parser to use.

- ### **`docstring_options`**

  (`dict[str, Any] | None`, default: `None` ) – The docstring parsing options.

- ### **`lines_collection`**

  (`LinesCollection | None`, default: `None` ) – A collection of source code lines.

- ### **`modules_collection`**

  (`ModulesCollection | None`, default: `None` ) – A collection of modules.

Methods:

- **`generic_inspect`** – Extend the base generic inspection with extensions.
- **`get_module`** – Build and return the object representing the module attached to this inspector.
- **`handle_attribute`** – Handle an attribute.
- **`handle_function`** – Handle a function.
- **`inspect`** – Extend the base inspection with extensions.
- **`inspect_attribute`** – Inspect an attribute.
- **`inspect_builtin_function`** – Inspect a builtin function.
- **`inspect_builtin_method`** – Inspect a builtin method.
- **`inspect_cached_property`** – Inspect a cached property.
- **`inspect_class`** – Inspect a class.
- **`inspect_classmethod`** – Inspect a class method.
- **`inspect_coroutine`** – Inspect a coroutine.
- **`inspect_function`** – Inspect a function.
- **`inspect_getset_descriptor`** – Inspect a get/set descriptor.
- **`inspect_method`** – Inspect a method.
- **`inspect_method_descriptor`** – Inspect a method descriptor.
- **`inspect_module`** – Inspect a module.
- **`inspect_property`** – Inspect a property.
- **`inspect_staticmethod`** – Inspect a static method.
- **`inspect_type_alias`** – Inspect a type alias.

Attributes:

- **`current`** (`Module | Class`) – The current object being inspected.
- **`docstring_options`** (`dict[str, Any]`) – The docstring parsing options.
- **`docstring_parser`** (`DocstringStyle | Parser | None`) – The docstring parser to use.
- **`extensions`** (`Extensions`) – The extensions to use when inspecting.
- **`filepath`** (`Path | None`) – The module file path.
- **`lines_collection`** (`LinesCollection`) – A collection of source code lines.
- **`module_name`** (`str`) – The module name.
- **`modules_collection`** (`ModulesCollection`) – A collection of modules.
- **`parent`** (`Module | None`) – An optional parent for the final module object.

### current

```
current: Module | Class = None

```

The current object being inspected.

### docstring_options

```
docstring_options: dict[str, Any] = docstring_options or {}

```

The docstring parsing options.

### docstring_parser

```
docstring_parser: DocstringStyle | Parser | None = (
    docstring_parser
)

```

The docstring parser to use.

### extensions

```
extensions: Extensions = extensions

```

The extensions to use when inspecting.

### filepath

```
filepath: Path | None = filepath

```

The module file path.

### lines_collection

```
lines_collection: LinesCollection = (
    lines_collection or LinesCollection()
)

```

A collection of source code lines.

### module_name

```
module_name: str = module_name

```

The module name.

### modules_collection

```
modules_collection: ModulesCollection = (
    modules_collection or ModulesCollection()
)

```

A collection of modules.

### parent

```
parent: Module | None = parent

```

An optional parent for the final module object.

### generic_inspect

```
generic_inspect(node: ObjectNode) -> None

```

Extend the base generic inspection with extensions.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

### get_module

```
get_module(
    import_paths: Sequence[str | Path] | None = None,
) -> Module

```

Build and return the object representing the module attached to this inspector.

This method triggers a complete inspection of the module members.

Parameters:

- #### **`import_paths`**

  (`Sequence[str | Path] | None`, default: `None` ) – Paths replacing sys.path to import the module.

Returns:

- `Module` – A module instance.

### handle_attribute

```
handle_attribute(
    node: ObjectNode, annotation: str | Expr | None = None
) -> None

```

Handle an attribute.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

- #### **`annotation`**

  (`str | Expr | None`, default: `None` ) – A potential annotation.

### handle_function

```
handle_function(
    node: ObjectNode, labels: set | None = None
) -> None

```

Handle a function.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

- #### **`labels`**

  (`set | None`, default: `None` ) – Labels to add to the data object.

### inspect

```
inspect(node: ObjectNode) -> None

```

Extend the base inspection with extensions.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

### inspect_attribute

```
inspect_attribute(node: ObjectNode) -> None

```

Inspect an attribute.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

### inspect_builtin_function

```
inspect_builtin_function(node: ObjectNode) -> None

```

Inspect a builtin function.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

### inspect_builtin_method

```
inspect_builtin_method(node: ObjectNode) -> None

```

Inspect a builtin method.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

### inspect_cached_property

```
inspect_cached_property(node: ObjectNode) -> None

```

Inspect a cached property.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

### inspect_class

```
inspect_class(node: ObjectNode) -> None

```

Inspect a class.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

### inspect_classmethod

```
inspect_classmethod(node: ObjectNode) -> None

```

Inspect a class method.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

### inspect_coroutine

```
inspect_coroutine(node: ObjectNode) -> None

```

Inspect a coroutine.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

### inspect_function

```
inspect_function(node: ObjectNode) -> None

```

Inspect a function.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

### inspect_getset_descriptor

```
inspect_getset_descriptor(node: ObjectNode) -> None

```

Inspect a get/set descriptor.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

### inspect_method

```
inspect_method(node: ObjectNode) -> None

```

Inspect a method.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

### inspect_method_descriptor

```
inspect_method_descriptor(node: ObjectNode) -> None

```

Inspect a method descriptor.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

### inspect_module

```
inspect_module(node: ObjectNode) -> None

```

Inspect a module.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

### inspect_property

```
inspect_property(node: ObjectNode) -> None

```

Inspect a property.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

### inspect_staticmethod

```
inspect_staticmethod(node: ObjectNode) -> None

```

Inspect a static method.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

### inspect_type_alias

```
inspect_type_alias(node: ObjectNode) -> None

```

Inspect a type alias.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

## **Dynamic analysis helpers**

## sys_path

```
sys_path(*paths: str | Path) -> Iterator[None]

```

Redefine `sys.path` temporarily.

Parameters:

- ### **`*paths`**

  (`str | Path`, default: `()` ) – The paths to use when importing modules. If no paths are given, keep sys.path untouched.

Yields:

- `None` – Nothing.

## dynamic_import

```
dynamic_import(
    import_path: str,
    import_paths: Sequence[str | Path] | None = None,
) -> Any

```

Dynamically import the specified object.

It can be a module, class, method, function, attribute, type alias, nested arbitrarily.

It works like this:

- for a given object path `a.b.x.y`
- it tries to import `a.b.x.y` as a module (with `importlib.import_module`)
- if it fails, it tries again with `a.b.x`, storing `y`
- then `a.b`, storing `x.y`
- then `a`, storing `b.x.y`
- if nothing worked, it raises an error
- if one of the iteration worked, it moves on, and...
- it tries to get the remaining (stored) parts with `getattr`
- for example it gets `b` from `a`, then `x` from `b`, etc.
- if a single attribute access fails, it raises an error
- if everything worked, it returns the last obtained attribute

Since the function potentially tries multiple things before succeeding, all errors happening along the way are recorded, and re-emitted with an `ImportError` when it fails, to let users know what was tried.

Important

The paths given through the `import_paths` parameter are used to temporarily patch `sys.path`: this function is therefore not thread-safe.

Important

The paths given as `import_paths` must be *correct*. The contents of `sys.path` must be consistent to what a user of the imported code would expect. Given a set of paths, if the import fails for a user, it will fail here too, with potentially unintuitive errors. If we wanted to make this function more robust, we could add a loop to "roll the window" of given paths, shifting them to the left (for example: `("/a/a", "/a/b", "/a/c/")`, then `("/a/b", "/a/c", "/a/a/")`, then `("/a/c", "/a/a", "/a/b/")`), to make sure each entry is given highest priority at least once, maintaining relative order, but we deem this unnecessary for now.

Parameters:

- ### **`import_path`**

  (`str`) – The path of the object to import.

- ### **`import_paths`**

  (`Sequence[str | Path] | None`, default: `None` ) – The (sys) paths to import the object from.

Raises:

- `ModuleNotFoundError` – When the object's module could not be found.
- `ImportError` – When there was an import error or when couldn't get the attribute.

Returns:

- `Any` – The imported object.

## ObjectNode

```
ObjectNode(
    obj: Any, name: str, parent: ObjectNode | None = None
)

```

Helper class to represent an object tree.

It's not really a tree but more a backward-linked list: each node has a reference to its parent, but not to its child (for simplicity purposes and to avoid bugs).

Each node stores an object, its name, and a reference to its parent node.

Parameters:

- ### **`obj`**

  (`Any`) – A Python object.

- ### **`name`**

  (`str`) – The object's name.

- ### **`parent`**

  (`ObjectNode | None`, default: `None` ) – The object's parent node.

Attributes:

- **`alias_target_path`** (`str | None`) – Alias target path of this node, if the node should be an alias.
- **`children`** (`Sequence[ObjectNode]`) – The children of this node.
- **`exclude_specials`** (`set[str]`) – Low level attributes known to cause issues when resolving aliases.
- **`is_attribute`** (`bool`) – Whether this node's object is an attribute.
- **`is_builtin_function`** (`bool`) – Whether this node's object is a builtin function.
- **`is_builtin_method`** (`bool`) – Whether this node's object is a builtin method.
- **`is_cached_property`** (`bool`) – Whether this node's object is a cached property.
- **`is_class`** (`bool`) – Whether this node's object is a class.
- **`is_classmethod`** (`bool`) – Whether this node's object is a classmethod.
- **`is_coroutine`** (`bool`) – Whether this node's object is a coroutine.
- **`is_function`** (`bool`) – Whether this node's object is a function.
- **`is_getset_descriptor`** (`bool`) – Whether this node's object is a get/set descriptor.
- **`is_method`** (`bool`) – Whether this node's object is a method.
- **`is_method_descriptor`** (`bool`) – Whether this node's object is a method descriptor.
- **`is_module`** (`bool`) – Whether this node's object is a module.
- **`is_property`** (`bool`) – Whether this node's object is a property.
- **`is_staticmethod`** (`bool`) – Whether this node's object is a staticmethod.
- **`is_type_alias`** (`bool`) – Whether this node's object is a type alias.
- **`kind`** (`ObjectKind`) – The kind of this node.
- **`module`** (`ObjectNode`) – The object's module, fetched from the node tree.
- **`module_path`** (`str | None`) – The object's module path.
- **`name`** (`str`) – The Python object's name.
- **`obj`** (`Any`) – The actual Python object.
- **`parent`** (`ObjectNode | None`) – The parent node.
- **`parent_is_class`** (`bool`) – Whether the object of this node's parent is a class.
- **`path`** (`str`) – The object's (Python) path.

### alias_target_path

```
alias_target_path: str | None

```

Alias target path of this node, if the node should be an alias.

### children

```
children: Sequence[ObjectNode]

```

The children of this node.

### exclude_specials

```
exclude_specials: set[str] = {
    "__builtins__",
    "__loader__",
    "__spec__",
}

```

Low level attributes known to cause issues when resolving aliases.

### is_attribute

```
is_attribute: bool

```

Whether this node's object is an attribute.

### is_builtin_function

```
is_builtin_function: bool

```

Whether this node's object is a builtin function.

### is_builtin_method

```
is_builtin_method: bool

```

Whether this node's object is a builtin method.

### is_cached_property

```
is_cached_property: bool = is_cached_property

```

Whether this node's object is a cached property.

### is_class

```
is_class: bool

```

Whether this node's object is a class.

### is_classmethod

```
is_classmethod: bool

```

Whether this node's object is a classmethod.

### is_coroutine

```
is_coroutine: bool

```

Whether this node's object is a coroutine.

### is_function

```
is_function: bool

```

Whether this node's object is a function.

### is_getset_descriptor

```
is_getset_descriptor: bool

```

Whether this node's object is a get/set descriptor.

### is_method

```
is_method: bool

```

Whether this node's object is a method.

### is_method_descriptor

```
is_method_descriptor: bool

```

Whether this node's object is a method descriptor.

Built-in methods (e.g. those implemented in C/Rust) are often method descriptors, rather than normal methods.

### is_module

```
is_module: bool

```

Whether this node's object is a module.

### is_property

```
is_property: bool

```

Whether this node's object is a property.

### is_staticmethod

```
is_staticmethod: bool

```

Whether this node's object is a staticmethod.

### is_type_alias

```
is_type_alias: bool

```

Whether this node's object is a type alias.

### kind

```
kind: ObjectKind

```

The kind of this node.

### module

```
module: ObjectNode

```

The object's module, fetched from the node tree.

### module_path

```
module_path: str | None

```

The object's module path.

### name

```
name: str = name

```

The Python object's name.

### obj

```
obj: Any = obj

```

The actual Python object.

### parent

```
parent: ObjectNode | None = parent

```

The parent node.

### parent_is_class

```
parent_is_class: bool

```

Whether the object of this node's parent is a class.

### path

```
path: str

```

The object's (Python) path.

## ObjectKind

Bases: `str`, `Enum`

```

              flowchart TD
              griffe.ObjectKind[ObjectKind]

              

              click griffe.ObjectKind href "" "griffe.ObjectKind"
            
```

Enumeration of the different runtime object kinds.

Attributes:

- **`ATTRIBUTE`** – Attributes.
- **`BUILTIN_FUNCTION`** – Built-in functions.
- **`BUILTIN_METHOD`** – Built-in methods.
- **`CACHED_PROPERTY`** – Cached properties.
- **`CLASS`** – Classes.
- **`CLASSMETHOD`** – Class methods.
- **`COROUTINE`** – Coroutines
- **`FUNCTION`** – Functions.
- **`GETSET_DESCRIPTOR`** – Get/set descriptors.
- **`METHOD`** – Methods.
- **`METHOD_DESCRIPTOR`** – Method descriptors.
- **`MODULE`** – Modules.
- **`PROPERTY`** – Properties.
- **`STATICMETHOD`** – Static methods.
- **`TYPE_ALIAS`** – Type aliases.

### ATTRIBUTE

```
ATTRIBUTE = 'attribute'

```

Attributes.

### BUILTIN_FUNCTION

```
BUILTIN_FUNCTION = 'builtin_function'

```

Built-in functions.

### BUILTIN_METHOD

```
BUILTIN_METHOD = 'builtin_method'

```

Built-in methods.

### CACHED_PROPERTY

```
CACHED_PROPERTY = 'cached_property'

```

Cached properties.

### CLASS

```
CLASS = 'class'

```

Classes.

### CLASSMETHOD

```
CLASSMETHOD = 'classmethod'

```

Class methods.

### COROUTINE

```
COROUTINE = 'coroutine'

```

Coroutines

### FUNCTION

```
FUNCTION = 'function'

```

Functions.

### GETSET_DESCRIPTOR

```
GETSET_DESCRIPTOR = 'getset_descriptor'

```

Get/set descriptors.

### METHOD

```
METHOD = 'method'

```

Methods.

### METHOD_DESCRIPTOR

```
METHOD_DESCRIPTOR = 'method_descriptor'

```

Method descriptors.

### MODULE

```
MODULE = 'module'

```

Modules.

### PROPERTY

```
PROPERTY = 'property'

```

Properties.

### STATICMETHOD

```
STATICMETHOD = 'staticmethod'

```

Static methods.

### TYPE_ALIAS

```
TYPE_ALIAS = 'type_alias'

```

Type aliases.

## **Static analysis helpers**

## builtin_decorators

```
builtin_decorators = {
    "property": "property",
    "staticmethod": "staticmethod",
    "classmethod": "classmethod",
}

```

Mapping of builtin decorators to labels.

## stdlib_decorators

```
stdlib_decorators = {
    "abc.abstractmethod": {"abstractmethod"},
    "functools.cache": {"cached"},
    "functools.cached_property": {"cached", "property"},
    "cached_property.cached_property": {
        "cached",
        "property",
    },
    "functools.lru_cache": {"cached"},
    "dataclasses.dataclass": {"dataclass"},
}

```

Mapping of standard library decorators to labels.

## typing_overload

```
typing_overload = {
    "typing.overload",
    "typing_extensions.overload",
}

```

Set of recognized typing overload decorators.

When such a decorator is found, the decorated function becomes an overload.

## ast_kind

```
ast_kind(node: AST) -> str

```

Return the kind of an AST node.

Parameters:

- ### **`node`**

  (`AST`) – The AST node.

Returns:

- `str` – The node kind.

## ast_children

```
ast_children(node: AST) -> Iterator[AST]

```

Return the children of an AST node.

Parameters:

- ### **`node`**

  (`AST`) – The AST node.

Yields:

- `AST` – The node children.

## ast_previous_siblings

```
ast_previous_siblings(node: AST) -> Iterator[AST]

```

Return the previous siblings of this node, starting from the closest.

Parameters:

- ### **`node`**

  (`AST`) – The AST node.

Yields:

- `AST` – The previous siblings.

## ast_next_siblings

```
ast_next_siblings(node: AST) -> Iterator[AST]

```

Return the next siblings of this node, starting from the closest.

Parameters:

- ### **`node`**

  (`AST`) – The AST node.

Yields:

- `AST` – The next siblings.

## ast_siblings

```
ast_siblings(node: AST) -> Iterator[AST]

```

Return the siblings of this node.

Parameters:

- ### **`node`**

  (`AST`) – The AST node.

Yields:

- `AST` – The siblings.

## ast_previous

```
ast_previous(node: AST) -> AST

```

Return the previous sibling of this node.

Parameters:

- ### **`node`**

  (`AST`) – The AST node.

Raises:

- `LastNodeError` – When the node does not have previous siblings.

Returns:

- `AST` – The sibling.

## ast_next

```
ast_next(node: AST) -> AST

```

Return the next sibling of this node.

Parameters:

- ### **`node`**

  (`AST`) – The AST node.

Raises:

- `LastNodeError` – When the node does not have next siblings.

Returns:

- `AST` – The sibling.

## ast_first_child

```
ast_first_child(node: AST) -> AST

```

Return the first child of this node.

Parameters:

- ### **`node`**

  (`AST`) – The AST node.

Raises:

- `LastNodeError` – When the node does not have children.

Returns:

- `AST` – The child.

## ast_last_child

```
ast_last_child(node: AST) -> AST

```

Return the lasts child of this node.

Parameters:

- ### **`node`**

  (`AST`) – The AST node.

Raises:

- `LastNodeError` – When the node does not have children.

Returns:

- `AST` – The child.

## get_docstring

```
get_docstring(
    node: AST, *, strict: bool = False
) -> tuple[str | None, int | None, int | None]

```

Extract a docstring.

Parameters:

- ### **`node`**

  (`AST`) – The node to extract the docstring from.

- ### **`strict`**

  (`bool`, default: `False` ) – Whether to skip searching the body (functions).

Returns:

- `tuple[str | None, int | None, int | None]` – A tuple with the value and line numbers of the docstring.

## get_name

```
get_name(node: AST) -> str

```

Extract name from an assignment node.

Parameters:

- ### **`node`**

  (`AST`) – The node to extract names from.

Returns:

- `str` – A list of names.

## get_names

```
get_names(node: AST) -> list[str]

```

Extract names from an assignment node.

Parameters:

- ### **`node`**

  (`AST`) – The node to extract names from.

Returns:

- `list[str]` – A list of names.

## get_instance_names

```
get_instance_names(node: AST) -> list[str]

```

Extract names from an assignment node, only for instance attributes.

Parameters:

- ### **`node`**

  (`AST`) – The node to extract names from.

Returns:

- `list[str]` – A list of names.

## get\_\_all\_\_

```
get__all__(
    node: Assign | AnnAssign | AugAssign, parent: Module
) -> list[str | ExprName]

```

Get the values declared in `__all__`.

Parameters:

- ### **`node`**

  (`Assign | AnnAssign | AugAssign`) – The assignment node.

- ### **`parent`**

  (`Module`) – The parent module.

Returns:

- `list[str | ExprName]` – A set of names.

## safe_get\_\_all\_\_

```
safe_get__all__(
    node: Assign | AnnAssign | AugAssign,
    parent: Module,
    log_level: LogLevel = debug,
) -> list[str | ExprName]

```

Safely (no exception) extract values in `__all__`.

Parameters:

- ### **`node`**

  (`Assign | AnnAssign | AugAssign`) – The __all__ assignment node.

- ### **`parent`**

  (`Module`) – The parent used to resolve the names.

- ### **`log_level`**

  (`LogLevel`, default: `debug` ) – Log level to use to log a message.

Returns:

- `list[str | ExprName]` – A list of strings or resolvable names.

## relative_to_absolute

```
relative_to_absolute(
    node: ImportFrom, name: alias, current_module: Module
) -> str

```

Convert a relative import path to an absolute one.

Parameters:

- ### **`node`**

  (`ImportFrom`) – The "from ... import ..." AST node.

- ### **`name`**

  (`alias`) – The imported name.

- ### **`current_module`**

  (`Module`) – The module in which the import happens.

Returns:

- `str` – The absolute import path.

## get_parameters

```
get_parameters(node: arguments) -> ParametersType

```

## get_value

```
get_value(node: AST | None) -> str | None

```

Get the string representation of a node.

Parameters:

- ### **`node`**

  (`AST | None`) – The node to represent.

Returns:

- `str | None` – The representing code for the node.

## safe_get_value

```
safe_get_value(
    node: AST | None, filepath: str | Path | None = None
) -> str | None

```

Safely (no exception) get the string representation of a node.

Parameters:

- ### **`node`**

  (`AST | None`) – The node to represent.

- ### **`filepath`**

  (`str | Path | None`, default: `None` ) – An optional filepath from where the node comes.

Returns:

- `str | None` – The representing code for the node.

## **Deprecated API**

## ExportedName

```
ExportedName(name: str, parent: Module)

```

Deprecated. An intermediate class to store names.

The get\_\_all\_\_ function now returns instances of ExprName instead.

Attributes:

- **`name`** (`str`) – The exported name.
- **`parent`** (`Module`) – The parent module.

### name

```
name: str

```

The exported name.

### parent

```
parent: Module

```

The parent module.
