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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def load_extensions(*exts: LoadableExtensionType) -> Extensions:
    """Load configured extensions.

    Parameters:
        exts: Extensions with potential configuration options.

    Returns:
        An extensions container.
    """
    extensions = Extensions()

    for extension in exts:
        ext = _load_extension(extension)
        if isinstance(ext, list):
            extensions.add(*ext)  # ty:ignore[invalid-argument-type]
        else:
            extensions.add(ext)

    # TODO: Deprecate and remove at some point?
    # Always add our built-in dataclasses extension.
    from griffe._internal.extensions.dataclasses import DataclassesExtension  # noqa: PLC0415

    for ext in extensions._extensions:
        if type(ext) is DataclassesExtension:
            break
    else:
        extensions.add(*_load_extension("dataclasses"))  # ty:ignore[not-iterable]

    return extensions
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def generic_inspect(self, node: ObjectNode) -> None:
    """Extend the base generic inspection with extensions.

    Parameters:
        node: The node to inspect.
    """
    for child in node.children:
        if not child.alias_target_path:
            self.inspect(child)
```

### generic_visit

```
generic_visit(node: AST) -> None
```

Visit children nodes.

Parameters:

- #### **`node`**

  (`AST`) – The node to visit the children of.

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def generic_visit(self, node: ast.AST) -> None:
    """Visit children nodes.

    Parameters:
        node: The node to visit the children of.
    """
    for child in ast_children(node):
        self.visit(child)
```

### inspect

```
inspect(node: ObjectNode) -> None
```

Inspect a node.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def inspect(self, node: ObjectNode) -> None:
    """Inspect a node.

    Parameters:
        node: The node to inspect.
    """
    getattr(self, f"inspect_{node.kind}", lambda _: None)(node)
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_alias(self, *, alias: Alias, loader: GriffeLoader, **kwargs: Any) -> None:
    """Run on aliases once the object tree has been fully constructed.

    Note:
        This method runs once the object tree has been fully constructed:
        data is therefore complete and you can safely hook onto this event.

    Parameters:
        alias: The alias instance.
        loader: The loader currently in use.
        **kwargs: For forward-compatibility.
    """
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_alias_instance(
    self,
    *,
    node: ast.AST | ObjectNode,
    alias: Alias,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None:
    """Run when an Alias has been created.

    Warning:
        This method runs while the object tree is still being constructed:
        data might be incomplete (class inheritance, alias resolution, etc.).
        Only hook onto this event if you know what you're doing.

    Parameters:
        node: The currently visited node.
        alias: The alias instance.
        agent: The analysis agent currently running.
        **kwargs: For forward-compatibility.
    """
    if getattr(self, "__old_on_alias", False):
        self.on_alias(node=node, alias=alias, agent=agent, **kwargs)
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_attribute(self, *, attr: Attribute, loader: GriffeLoader, **kwargs: Any) -> None:
    """Run on attributes once the object tree has been fully constructed.

    Note:
        This method runs once the object tree has been fully constructed:
        data is therefore complete and you can safely hook onto this event.

    Parameters:
        attr: The attribute instance.
        loader: The loader currently in use.
        **kwargs: For forward-compatibility.
    """
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_attribute_instance(
    self,
    *,
    node: ast.AST | ObjectNode,
    attr: Attribute,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None:
    """Run when an Attribute has been created.

    Warning:
        This method runs while the object tree is still being constructed:
        data might be incomplete (class inheritance, alias resolution, etc.).
        Only hook onto this event if you know what you're doing.

    Parameters:
        node: The currently visited node.
        attr: The attribute instance.
        agent: The analysis agent currently running.
        **kwargs: For forward-compatibility.
    """
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_attribute_node(self, *, node: ast.AST | ObjectNode, agent: Visitor | Inspector, **kwargs: Any) -> None:
    """Run when visiting a new attribute node during static/dynamic analysis.

    Parameters:
        node: The currently visited node.
        agent: The analysis agent currently running.
        **kwargs: For forward-compatibility.
    """
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_class(self, *, cls: Class, loader: GriffeLoader, **kwargs: Any) -> None:
    """Run on classes once the object tree has been fully constructed.

    Note:
        This method runs once the object tree has been fully constructed:
        data is therefore complete and you can safely hook onto this event.

    Parameters:
        cls: The class instance.
        loader: The loader currently in use.
        **kwargs: For forward-compatibility.
    """
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_class_instance(
    self,
    *,
    node: ast.AST | ObjectNode,
    cls: Class,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None:
    """Run when a Class has been created.

    Warning:
        This method runs while the object tree is still being constructed:
        data might be incomplete (class inheritance, alias resolution, etc.).
        Only hook onto this event if you know what you're doing.

    Parameters:
        node: The currently visited node.
        cls: The class instance.
        agent: The analysis agent currently running.
        **kwargs: For forward-compatibility.
    """
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_class_members(
    self,
    *,
    node: ast.AST | ObjectNode,
    cls: Class,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None:
    """Run when members of a Class have been loaded.

    Warning:
        This method runs while the object tree is still being constructed:
        data might be incomplete (class inheritance, alias resolution, etc.).
        Only hook onto this event if you know what you're doing.

    Parameters:
        node: The currently visited node.
        cls: The class instance.
        agent: The analysis agent currently running.
        **kwargs: For forward-compatibility.
    """
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_class_node(self, *, node: ast.AST | ObjectNode, agent: Visitor | Inspector, **kwargs: Any) -> None:
    """Run when visiting a new class node during static/dynamic analysis.

    Parameters:
        node: The currently visited node.
        agent: The analysis agent currently running.
        **kwargs: For forward-compatibility.
    """
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_function(self, *, func: Function, loader: GriffeLoader, **kwargs: Any) -> None:
    """Run on functions once the object tree has been fully constructed.

    Note:
        This method runs once the object tree has been fully constructed:
        data is therefore complete and you can safely hook onto this event.

    Parameters:
        func: The function instance.
        loader: The loader currently in use.
        **kwargs: For forward-compatibility.
    """
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_function_instance(
    self,
    *,
    node: ast.AST | ObjectNode,
    func: Function,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None:
    """Run when a Function has been created.

    Warning:
        This method runs while the object tree is still being constructed:
        data might be incomplete (class inheritance, alias resolution, etc.).
        Only hook onto this event if you know what you're doing.

    Parameters:
        node: The currently visited node.
        func: The function instance.
        agent: The analysis agent currently running.
        **kwargs: For forward-compatibility.
    """
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_function_node(self, *, node: ast.AST | ObjectNode, agent: Visitor | Inspector, **kwargs: Any) -> None:
    """Run when visiting a new function node during static/dynamic analysis.

    Parameters:
        node: The currently visited node.
        agent: The analysis agent currently running.
        **kwargs: For forward-compatibility.
    """
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_instance(
    self,
    *,
    node: ast.AST | ObjectNode,
    obj: Object,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None:
    """Run when an Object has been created.

    Warning:
        This method runs while the object tree is still being constructed:
        data might be incomplete (class inheritance, alias resolution, etc.).
        Only hook onto this event if you know what you're doing.

    Parameters:
        node: The currently visited node.
        obj: The object instance.
        agent: The analysis agent currently running.
        **kwargs: For forward-compatibility.
    """
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_members(self, *, node: ast.AST | ObjectNode, obj: Object, agent: Visitor | Inspector, **kwargs: Any) -> None:
    """Run when members of an Object have been loaded.

    Warning:
        This method runs while the object tree is still being constructed:
        data might be incomplete (class inheritance, alias resolution, etc.).
        Only hook onto this event if you know what you're doing.

    Parameters:
        node: The currently visited node.
        obj: The object instance.
        agent: The analysis agent currently running.
        **kwargs: For forward-compatibility.
    """
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_module(self, *, mod: Module, loader: GriffeLoader, **kwargs: Any) -> None:
    """Run on modules once the object tree has been fully constructed.

    Note:
        This method runs once the object tree has been fully constructed:
        data is therefore complete and you can safely hook onto this event.

    Parameters:
        mod: The module instance.
        loader: The loader currently in use.
        **kwargs: For forward-compatibility.
    """
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_module_instance(
    self,
    *,
    node: ast.AST | ObjectNode,
    mod: Module,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None:
    """Run when a Module has been created.

    Warning:
        This method runs while the object tree is still being constructed:
        data might be incomplete (class inheritance, alias resolution, etc.).
        Only hook onto this event if you know what you're doing.

    Parameters:
        node: The currently visited node.
        mod: The module instance.
        agent: The analysis agent currently running.
        **kwargs: For forward-compatibility.
    """
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_module_members(
    self,
    *,
    node: ast.AST | ObjectNode,
    mod: Module,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None:
    """Run when members of a Module have been loaded.

    Warning:
        This method runs while the object tree is still being constructed:
        data might be incomplete (class inheritance, alias resolution, etc.).
        Only hook onto this event if you know what you're doing.

    Parameters:
        node: The currently visited node.
        mod: The module instance.
        agent: The analysis agent currently running.
        **kwargs: For forward-compatibility.
    """
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_module_node(self, *, node: ast.AST | ObjectNode, agent: Visitor | Inspector, **kwargs: Any) -> None:
    """Run when visiting a new module node during static/dynamic analysis.

    Parameters:
        node: The currently visited node.
        agent: The analysis agent currently running.
        **kwargs: For forward-compatibility.
    """
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_node(self, *, node: ast.AST | ObjectNode, agent: Visitor | Inspector, **kwargs: Any) -> None:
    """Run when visiting a new node during static/dynamic analysis.

    Parameters:
        node: The currently visited node.
    """
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_object(self, *, obj: Object, loader: GriffeLoader, **kwargs: Any) -> None:
    """Run on objects (every kind) once the object tree has been fully constructed.

    Note:
        This method runs once the object tree has been fully constructed:
        data is therefore complete and you can safely hook onto this event.

    Parameters:
        obj: The object instance.
        loader: The loader currently in use.
        **kwargs: For forward-compatibility.
    """
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_package(self, *, pkg: Module, loader: GriffeLoader, **kwargs: Any) -> None:
    """Run when a package has been completely loaded.

    Note:
        This method runs once the object tree has been fully constructed:
        data is therefore complete and you can safely hook onto this event.

    Parameters:
        pkg: The package (Module) instance.
        loader: The loader currently in use.
        **kwargs: For forward-compatibility.
    """
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_type_alias(self, *, type_alias: TypeAlias, loader: GriffeLoader, **kwargs: Any) -> None:
    """Run on type aliases once the object tree has been fully constructed.

    Note:
        This method runs once the object tree has been fully constructed:
        data is therefore complete and you can safely hook onto this event.

    Parameters:
        type_alias: The type alias instance.
        loader: The loader currently in use.
        **kwargs: For forward-compatibility.
    """
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_type_alias_instance(
    self,
    *,
    node: ast.AST | ObjectNode,
    type_alias: TypeAlias,
    agent: Visitor | Inspector,
    **kwargs: Any,
) -> None:
    """Run when a TypeAlias has been created.

    Warning:
        This method runs while the object tree is still being constructed:
        data might be incomplete (class inheritance, alias resolution, etc.).
        Only hook onto this event if you know what you're doing.

    Parameters:
        node: The currently visited node.
        type_alias: The type alias instance.
        agent: The analysis agent currently running.
        **kwargs: For forward-compatibility.
    """
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def on_type_alias_node(self, *, node: ast.AST | ObjectNode, agent: Visitor | Inspector, **kwargs: Any) -> None:
    """Run when visiting a new type alias node during static/dynamic analysis.

    Parameters:
        node: The currently visited node.
        agent: The analysis agent currently running.
        **kwargs: For forward-compatibility.
    """
```

### visit

```
visit(node: AST) -> None
```

Visit a node.

Parameters:

- #### **`node`**

  (`AST`) – The node to visit.

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def visit(self, node: ast.AST) -> None:
    """Visit a node.

    Parameters:
        node: The node to visit.
    """
    getattr(self, f"visit_{ast_kind(node)}", lambda _: None)(node)
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def __init__(self, *extensions: Extension) -> None:
    """Initialize the extensions container.

    Parameters:
        *extensions: The extensions to add.
    """
    self._extensions: list[Extension] = []
    self.add(*extensions)
```

### add

```
add(*extensions: Extension) -> None
```

Add extensions to this container.

Parameters:

- #### **`*extensions`**

  (`Extension`, default: `()` ) – The extensions to add.

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def add(self, *extensions: Extension) -> None:
    """Add extensions to this container.

    Parameters:
        *extensions: The extensions to add.
    """
    for extension in extensions:
        self._extensions.append(extension)
```

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

Source code in `packages/griffelib/src/griffe/_internal/extensions/base.py`

```
def call(self, event: str, **kwargs: Any) -> None:
    """Call the extension hook for the given event.

    Parameters:
        event: The triggered event.
        **kwargs: Arguments passed to the hook.
    """
    for extension in self._extensions:
        getattr(extension, event, self._noop)(**kwargs)
```

## **Types**

## LoadableExtensionType

```
LoadableExtensionType = (
    str | dict[str, Any] | Extension | type[Extension]
)
```

All the types that can be passed to `load_extensions`.

## **Builtin extensions**

## builtin_extensions

```
builtin_extensions: set[str] = {
    "dataclasses",
    "unpack_typeddict",
}
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

Source code in `packages/griffelib/src/griffe/_internal/extensions/dataclasses.py`

```
def on_package(self, *, pkg: Module, **kwargs: Any) -> None:  # noqa: ARG002
    """Hook for loaded packages.

    Parameters:
        pkg: The loaded package.
    """
    _apply_recursively(pkg, set())
```

## UnpackTypedDictExtension

Bases: `Extension`

```
              flowchart TD
              griffe.UnpackTypedDictExtension[UnpackTypedDictExtension]
              griffe._internal.extensions.base.Extension[Extension]

                              griffe._internal.extensions.base.Extension --> griffe.UnpackTypedDictExtension
                


              click griffe.UnpackTypedDictExtension href "" "griffe.UnpackTypedDictExtension"
              click griffe._internal.extensions.base.Extension href "" "griffe._internal.extensions.base.Extension"
```

An extension to handle `Unpack[TypeDict]`.

Methods:

- **`on_class`** – Add an __init__ method to TypedDict classes if missing.
- **`on_function`** – Expand \*\*kwargs: Unpack[TypedDict] in function signatures.

### on_class

```
on_class(*, cls: Class, **kwargs: Any) -> None
```

Add an `__init__` method to `TypedDict` classes if missing.

Source code in `packages/griffelib/src/griffe/_internal/extensions/unpack_typeddict.py`

```
def on_class(self, *, cls: Class, **kwargs: Any) -> None:  # noqa: ARG002
    """Add an `__init__` method to `TypedDict` classes if missing."""
    for base in cls.bases:
        if isinstance(base, Expr) and base.canonical_path in {"typing.TypedDict", "typing_extensions.TypedDict"}:
            cls.labels.add("typed-dict")
            break
    else:
        return

    required, optional = _get_or_set_attrs(cls)

    if "__init__" not in cls.members:
        # Build the `__init__` method and add it to the class.
        parameters = Parameters(
            Parameter(name="self", kind=ParameterKind.positional_or_keyword),
            *_params_from_attrs(required, optional),
        )
        # TODO: Add `**kwargs` parameter if extra items are allowed.
        init = Function(name="__init__", parameters=parameters, returns="None")
        cls.set_member("__init__", init)
        # Update the `__init__` docstring.
        _update_docstring(init, required, optional)

    # Remove attributes from the class, as they are now in the `__init__` method.
    for attr in chain(required, optional):
        cls.del_member(attr["name"])
```

### on_function

```
on_function(*, func: Function, **kwargs: Any) -> None
```

Expand `**kwargs: Unpack[TypedDict]` in function signatures.

Source code in `packages/griffelib/src/griffe/_internal/extensions/unpack_typeddict.py`

```
def on_function(self, *, func: Function, **kwargs: Any) -> None:  # noqa: ARG002
    """Expand `**kwargs: Unpack[TypedDict]` in function signatures."""
    # Find any `**kwargs: Unpack[TypedDict]` parameter.
    for parameter in func.parameters:
        if parameter.kind is ParameterKind.var_keyword:
            annotation = parameter.annotation
            if isinstance(annotation, ExprSubscript) and annotation.canonical_path in {
                "typing.Annotated",
                "typing_extensions.Annotated",
            }:
                annotation = annotation.slice.elements[0]
            if isinstance(annotation, ExprSubscript) and annotation.canonical_path in {
                "typing.Unpack",
                "typing_extensions.Unpack",
            }:
                slice_path = annotation.slice.canonical_path
                typed_dict = func.modules_collection[slice_path]
                break
    else:
        return

    required, optional = _get_or_set_attrs(typed_dict)

    # Update any parameter section in the docstring.
    # We do this before updating the signature so that
    # parsing the docstring doesn't emit warnings.
    _update_docstring(func, required, optional, parameter)

    # Update the function parameters.
    del func.parameters[parameter.name]
    for param in _params_from_attrs(required, optional):
        func.parameters[param.name] = Parameter(
            name=param.name,
            annotation=param.annotation,
            kind=ParameterKind.keyword_only,
            default=param.default,
            docstring=param.docstring,
        )
```
