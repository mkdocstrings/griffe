# Extensions

## **Main API**

## load_extensions

```
load_extensions(*exts: LoadableExtensionType) -> Extensions
```

Load configured extensions.

Parameters:

- ### **`exts`**

  (`LoadableExtensionType`, default: `()` ) – Extensions with potential configuration options.

Returns:

- `Extensions` – An extensions container.

## Extension

Base class for Griffe extensions.

Methods:

- **`generic_inspect`** – Extend the base generic inspection with extensions.
- **`generic_visit`** – Visit children nodes.
- **`inspect`** – Inspect a node.
- **`on_alias`** – Run on aliases once the object tree has been fully constructed.
- **`on_alias_instance`** – Run when an Alias has been created.
- **`on_attribute`** – Run on attributes once the object tree has been fully constructed.
- **`on_attribute_instance`** – Run when an Attribute has been created.
- **`on_attribute_node`** – Run when visiting a new attribute node during static/dynamic analysis.
- **`on_class`** – Run on classes once the object tree has been fully constructed.
- **`on_class_instance`** – Run when a Class has been created.
- **`on_class_members`** – Run when members of a Class have been loaded.
- **`on_class_node`** – Run when visiting a new class node during static/dynamic analysis.
- **`on_function`** – Run on functions once the object tree has been fully constructed.
- **`on_function_instance`** – Run when a Function has been created.
- **`on_function_node`** – Run when visiting a new function node during static/dynamic analysis.
- **`on_instance`** – Run when an Object has been created.
- **`on_members`** – Run when members of an Object have been loaded.
- **`on_module`** – Run on modules once the object tree has been fully constructed.
- **`on_module_instance`** – Run when a Module has been created.
- **`on_module_members`** – Run when members of a Module have been loaded.
- **`on_module_node`** – Run when visiting a new module node during static/dynamic analysis.
- **`on_node`** – Run when visiting a new node during static/dynamic analysis.
- **`on_object`** – Run on objects (every kind) once the object tree has been fully constructed.
- **`on_package`** – Run when a package has been completely loaded.
- **`on_type_alias`** – Run on type aliases once the object tree has been fully constructed.
- **`on_type_alias_instance`** – Run when a TypeAlias has been created.
- **`on_type_alias_node`** – Run when visiting a new type alias node during static/dynamic analysis.
- **`visit`** – Visit a node.

### generic_inspect

```
generic_inspect(node: ObjectNode) -> None
```

Extend the base generic inspection with extensions.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

### generic_visit

```
generic_visit(node: AST) -> None
```

Visit children nodes.

Parameters:

- #### **`node`**

  (`AST`) – The node to visit the children of.

### inspect

```
inspect(node: ObjectNode) -> None
```

Inspect a node.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

### on_alias

```
on_alias(
    *, alias: Alias, loader: GriffeLoader, **kwargs: Any
) -> None
```

Run on aliases once the object tree has been fully constructed.

Note

This method runs once the object tree has been fully constructed: data is therefore complete and you can safely hook onto this event.

Parameters:

- #### **`alias`**

  (`Alias`) – The alias instance.

- #### **`loader`**

  (`GriffeLoader`) – The loader currently in use.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – For forward-compatibility.

### on_alias_instance

```
on_alias_instance(
    *,
    node: AST | ObjectNode,
    alias: Alias,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None
```

Run when an Alias has been created.

Warning

This method runs while the object tree is still being constructed: data might be incomplete (class inheritance, alias resolution, etc.). Only hook onto this event if you know what you're doing.

Parameters:

- #### **`node`**

  (`AST | ObjectNode`) – The currently visited node.

- #### **`alias`**

  (`Alias`) – The alias instance.

- #### **`agent`**

  (`Visitor | Inspector`) – The analysis agent currently running.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – For forward-compatibility.

### on_attribute

```
on_attribute(
    *, attr: Attribute, loader: GriffeLoader, **kwargs: Any
) -> None
```

Run on attributes once the object tree has been fully constructed.

Note

This method runs once the object tree has been fully constructed: data is therefore complete and you can safely hook onto this event.

Parameters:

- #### **`attr`**

  (`Attribute`) – The attribute instance.

- #### **`loader`**

  (`GriffeLoader`) – The loader currently in use.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – For forward-compatibility.

### on_attribute_instance

```
on_attribute_instance(
    *,
    node: AST | ObjectNode,
    attr: Attribute,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None
```

Run when an Attribute has been created.

Warning

This method runs while the object tree is still being constructed: data might be incomplete (class inheritance, alias resolution, etc.). Only hook onto this event if you know what you're doing.

Parameters:

- #### **`node`**

  (`AST | ObjectNode`) – The currently visited node.

- #### **`attr`**

  (`Attribute`) – The attribute instance.

- #### **`agent`**

  (`Visitor | Inspector`) – The analysis agent currently running.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – For forward-compatibility.

### on_attribute_node

```
on_attribute_node(
    *,
    node: AST | ObjectNode,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None
```

Run when visiting a new attribute node during static/dynamic analysis.

Parameters:

- #### **`node`**

  (`AST | ObjectNode`) – The currently visited node.

- #### **`agent`**

  (`Visitor | Inspector`) – The analysis agent currently running.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – For forward-compatibility.

### on_class

```
on_class(
    *, cls: Class, loader: GriffeLoader, **kwargs: Any
) -> None
```

Run on classes once the object tree has been fully constructed.

Note

This method runs once the object tree has been fully constructed: data is therefore complete and you can safely hook onto this event.

Parameters:

- #### **`cls`**

  (`Class`) – The class instance.

- #### **`loader`**

  (`GriffeLoader`) – The loader currently in use.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – For forward-compatibility.

### on_class_instance

```
on_class_instance(
    *,
    node: AST | ObjectNode,
    cls: Class,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None
```

Run when a Class has been created.

Warning

This method runs while the object tree is still being constructed: data might be incomplete (class inheritance, alias resolution, etc.). Only hook onto this event if you know what you're doing.

Parameters:

- #### **`node`**

  (`AST | ObjectNode`) – The currently visited node.

- #### **`cls`**

  (`Class`) – The class instance.

- #### **`agent`**

  (`Visitor | Inspector`) – The analysis agent currently running.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – For forward-compatibility.

### on_class_members

```
on_class_members(
    *,
    node: AST | ObjectNode,
    cls: Class,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None
```

Run when members of a Class have been loaded.

Warning

This method runs while the object tree is still being constructed: data might be incomplete (class inheritance, alias resolution, etc.). Only hook onto this event if you know what you're doing.

Parameters:

- #### **`node`**

  (`AST | ObjectNode`) – The currently visited node.

- #### **`cls`**

  (`Class`) – The class instance.

- #### **`agent`**

  (`Visitor | Inspector`) – The analysis agent currently running.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – For forward-compatibility.

### on_class_node

```
on_class_node(
    *,
    node: AST | ObjectNode,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None
```

Run when visiting a new class node during static/dynamic analysis.

Parameters:

- #### **`node`**

  (`AST | ObjectNode`) – The currently visited node.

- #### **`agent`**

  (`Visitor | Inspector`) – The analysis agent currently running.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – For forward-compatibility.

### on_function

```
on_function(
    *, func: Function, loader: GriffeLoader, **kwargs: Any
) -> None
```

Run on functions once the object tree has been fully constructed.

Note

This method runs once the object tree has been fully constructed: data is therefore complete and you can safely hook onto this event.

Parameters:

- #### **`func`**

  (`Function`) – The function instance.

- #### **`loader`**

  (`GriffeLoader`) – The loader currently in use.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – For forward-compatibility.

### on_function_instance

```
on_function_instance(
    *,
    node: AST | ObjectNode,
    func: Function,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None
```

Run when a Function has been created.

Warning

This method runs while the object tree is still being constructed: data might be incomplete (class inheritance, alias resolution, etc.). Only hook onto this event if you know what you're doing.

Parameters:

- #### **`node`**

  (`AST | ObjectNode`) – The currently visited node.

- #### **`func`**

  (`Function`) – The function instance.

- #### **`agent`**

  (`Visitor | Inspector`) – The analysis agent currently running.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – For forward-compatibility.

### on_function_node

```
on_function_node(
    *,
    node: AST | ObjectNode,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None
```

Run when visiting a new function node during static/dynamic analysis.

Parameters:

- #### **`node`**

  (`AST | ObjectNode`) – The currently visited node.

- #### **`agent`**

  (`Visitor | Inspector`) – The analysis agent currently running.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – For forward-compatibility.

### on_instance

```
on_instance(
    *,
    node: AST | ObjectNode,
    obj: Object,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None
```

Run when an Object has been created.

Warning

This method runs while the object tree is still being constructed: data might be incomplete (class inheritance, alias resolution, etc.). Only hook onto this event if you know what you're doing.

Parameters:

- #### **`node`**

  (`AST | ObjectNode`) – The currently visited node.

- #### **`obj`**

  (`Object`) – The object instance.

- #### **`agent`**

  (`Visitor | Inspector`) – The analysis agent currently running.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – For forward-compatibility.

### on_members

```
on_members(
    *,
    node: AST | ObjectNode,
    obj: Object,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None
```

Run when members of an Object have been loaded.

Warning

This method runs while the object tree is still being constructed: data might be incomplete (class inheritance, alias resolution, etc.). Only hook onto this event if you know what you're doing.

Parameters:

- #### **`node`**

  (`AST | ObjectNode`) – The currently visited node.

- #### **`obj`**

  (`Object`) – The object instance.

- #### **`agent`**

  (`Visitor | Inspector`) – The analysis agent currently running.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – For forward-compatibility.

### on_module

```
on_module(
    *, mod: Module, loader: GriffeLoader, **kwargs: Any
) -> None
```

Run on modules once the object tree has been fully constructed.

Note

This method runs once the object tree has been fully constructed: data is therefore complete and you can safely hook onto this event.

Parameters:

- #### **`mod`**

  (`Module`) – The module instance.

- #### **`loader`**

  (`GriffeLoader`) – The loader currently in use.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – For forward-compatibility.

### on_module_instance

```
on_module_instance(
    *,
    node: AST | ObjectNode,
    mod: Module,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None
```

Run when a Module has been created.

Warning

This method runs while the object tree is still being constructed: data might be incomplete (class inheritance, alias resolution, etc.). Only hook onto this event if you know what you're doing.

Parameters:

- #### **`node`**

  (`AST | ObjectNode`) – The currently visited node.

- #### **`mod`**

  (`Module`) – The module instance.

- #### **`agent`**

  (`Visitor | Inspector`) – The analysis agent currently running.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – For forward-compatibility.

### on_module_members

```
on_module_members(
    *,
    node: AST | ObjectNode,
    mod: Module,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None
```

Run when members of a Module have been loaded.

Warning

This method runs while the object tree is still being constructed: data might be incomplete (class inheritance, alias resolution, etc.). Only hook onto this event if you know what you're doing.

Parameters:

- #### **`node`**

  (`AST | ObjectNode`) – The currently visited node.

- #### **`mod`**

  (`Module`) – The module instance.

- #### **`agent`**

  (`Visitor | Inspector`) – The analysis agent currently running.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – For forward-compatibility.

### on_module_node

```
on_module_node(
    *,
    node: AST | ObjectNode,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None
```

Run when visiting a new module node during static/dynamic analysis.

Parameters:

- #### **`node`**

  (`AST | ObjectNode`) – The currently visited node.

- #### **`agent`**

  (`Visitor | Inspector`) – The analysis agent currently running.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – For forward-compatibility.

### on_node

```
on_node(
    *,
    node: AST | ObjectNode,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None
```

Run when visiting a new node during static/dynamic analysis.

Parameters:

- #### **`node`**

  (`AST | ObjectNode`) – The currently visited node.

### on_object

```
on_object(
    *, obj: Object, loader: GriffeLoader, **kwargs: Any
) -> None
```

Run on objects (every kind) once the object tree has been fully constructed.

Note

This method runs once the object tree has been fully constructed: data is therefore complete and you can safely hook onto this event.

Parameters:

- #### **`obj`**

  (`Object`) – The object instance.

- #### **`loader`**

  (`GriffeLoader`) – The loader currently in use.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – For forward-compatibility.

### on_package

```
on_package(
    *, pkg: Module, loader: GriffeLoader, **kwargs: Any
) -> None
```

Run when a package has been completely loaded.

Note

This method runs once the object tree has been fully constructed: data is therefore complete and you can safely hook onto this event.

Parameters:

- #### **`pkg`**

  (`Module`) – The package (Module) instance.

- #### **`loader`**

  (`GriffeLoader`) – The loader currently in use.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – For forward-compatibility.

### on_type_alias

```
on_type_alias(
    *,
    type_alias: TypeAlias,
    loader: GriffeLoader,
    **kwargs: Any,
) -> None
```

Run on type aliases once the object tree has been fully constructed.

Note

This method runs once the object tree has been fully constructed: data is therefore complete and you can safely hook onto this event.

Parameters:

- #### **`type_alias`**

  (`TypeAlias`) – The type alias instance.

- #### **`loader`**

  (`GriffeLoader`) – The loader currently in use.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – For forward-compatibility.

### on_type_alias_instance

```
on_type_alias_instance(
    *,
    node: AST | ObjectNode,
    type_alias: TypeAlias,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None
```

Run when a TypeAlias has been created.

Warning

This method runs while the object tree is still being constructed: data might be incomplete (class inheritance, alias resolution, etc.). Only hook onto this event if you know what you're doing.

Parameters:

- #### **`node`**

  (`AST | ObjectNode`) – The currently visited node.

- #### **`type_alias`**

  (`TypeAlias`) – The type alias instance.

- #### **`agent`**

  (`Visitor | Inspector`) – The analysis agent currently running.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – For forward-compatibility.

### on_type_alias_node

```
on_type_alias_node(
    *,
    node: AST | ObjectNode,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None
```

Run when visiting a new type alias node during static/dynamic analysis.

Parameters:

- #### **`node`**

  (`AST | ObjectNode`) – The currently visited node.

- #### **`agent`**

  (`Visitor | Inspector`) – The analysis agent currently running.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – For forward-compatibility.

### visit

```
visit(node: AST) -> None
```

Visit a node.

Parameters:

- #### **`node`**

  (`AST`) – The node to visit.

## **Advanced API**

## Extensions

```
Extensions(*extensions: Extension)
```

This class helps iterating on extensions that should run at different times.

Parameters:

- ### **`*extensions`**

  (`Extension`, default: `()` ) – The extensions to add.

Methods:

- **`add`** – Add extensions to this container.
- **`call`** – Call the extension hook for the given event.

### add

```
add(*extensions: Extension) -> None
```

Add extensions to this container.

Parameters:

- #### **`*extensions`**

  (`Extension`, default: `()` ) – The extensions to add.

### call

```
call(event: str, **kwargs: Any) -> None
```

Call the extension hook for the given event.

Parameters:

- #### **`event`**

  (`str`) – The triggered event.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Arguments passed to the hook.

## **Types**

## LoadableExtensionType

```
LoadableExtensionType = Union[
    str, dict[str, Any], Extension, type[Extension]
]
```

All the types that can be passed to `load_extensions`.

## **Builtin extensions**

## builtin_extensions

```
builtin_extensions: set[str] = {'dataclasses'}
```

The names of built-in Griffe extensions.

## DataclassesExtension

Bases: `Extension`

```
              flowchart TD
              griffe.DataclassesExtension[DataclassesExtension]
              griffe._internal.extensions.base.Extension[Extension]

                              griffe._internal.extensions.base.Extension --> griffe.DataclassesExtension
                


              click griffe.DataclassesExtension href "" "griffe.DataclassesExtension"
              click griffe._internal.extensions.base.Extension href "" "griffe._internal.extensions.base.Extension"
```

Built-in extension adding support for dataclasses.

This extension creates `__init__` methods of dataclasses if they don't already exist.

Methods:

- **`on_package`** – Hook for loaded packages.

### on_package

```
on_package(*, pkg: Module, **kwargs: Any) -> None
```

Hook for loaded packages.

Parameters:

- #### **`pkg`**

  (`Module`) – The loaded package.
