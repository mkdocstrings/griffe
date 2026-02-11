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
    docstring_options: DocstringOptions | None = None,
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

  (`DocstringOptions | None`, default: `None` ) – Docstring parsing options.

- ### **`lines_collection`**

  (`LinesCollection | None`, default: `None` ) – A collection of source code lines.

- ### **`modules_collection`**

  (`ModulesCollection | None`, default: `None` ) – A collection of modules.

Returns:

- `Module` – The module, with its members populated.

Source code in `packages/griffelib/src/griffe/_internal/agents/visitor.py`

```
def visit(
    module_name: str,
    filepath: Path,
    code: str,
    *,
    extensions: Extensions | None = None,
    parent: Module | None = None,
    docstring_parser: DocstringStyle | Parser | None = None,
    docstring_options: DocstringOptions | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
) -> Module:
    """Parse and visit a module file.

    We provide this function for static analysis. It uses a [`NodeVisitor`][ast.NodeVisitor]-like class,
    the [`Visitor`][griffe.Visitor], to compile and parse code (using [`compile`][])
    then visit the resulting AST (Abstract Syntax Tree).

    Important:
        This function is generally not used directly.
        In most cases, users can rely on the [`GriffeLoader`][griffe.GriffeLoader]
        and its accompanying [`load`][griffe.load] shortcut and their respective options
        to load modules using static analysis.

    Parameters:
        module_name: The module name (as when importing [from] it).
        filepath: The module file path.
        code: The module contents.
        extensions: The extensions to use when visiting the AST.
        parent: The optional parent of this module.
        docstring_parser: The docstring parser to use. By default, no parsing is done.
        docstring_options: Docstring parsing options.
        lines_collection: A collection of source code lines.
        modules_collection: A collection of modules.

    Returns:
        The module, with its members populated.
    """
    return Visitor(
        module_name,
        filepath,
        code,
        extensions or load_extensions(),
        parent,
        docstring_parser=docstring_parser,
        docstring_options=docstring_options,
        lines_collection=lines_collection,
        modules_collection=modules_collection,
    ).get_module()
```

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
    docstring_options: DocstringOptions | None = None,
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

  (`DocstringOptions | None`, default: `None` ) – Docstring parsing options.

- ### **`lines_collection`**

  (`LinesCollection | None`, default: `None` ) – A collection of source code lines.

- ### **`modules_collection`**

  (`ModulesCollection | None`, default: `None` ) – A collection of modules.

Returns:

- `Module` – The module, with its members populated.

Source code in `packages/griffelib/src/griffe/_internal/agents/inspector.py`

```
def inspect(
    module_name: str,
    *,
    filepath: Path | None = None,
    import_paths: Sequence[str | Path] | None = None,
    extensions: Extensions | None = None,
    parent: Module | None = None,
    docstring_parser: DocstringStyle | Parser | None = None,
    docstring_options: DocstringOptions | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
) -> Module:
    """Inspect a module.

    Sometimes we cannot get the source code of a module or an object,
    typically built-in modules like `itertools`.
    The only way to know what they are made of is to actually import them and inspect their contents.

    Sometimes, even if the source code is available,
    loading the object is desired because it was created or modified dynamically,
    and our static agent is not powerful enough to infer all these dynamic modifications.
    In this case, we load the module using introspection.

    Griffe therefore provides this function for dynamic analysis.
    It uses a [`NodeVisitor`][ast.NodeVisitor]-like class, the [`Inspector`][griffe.Inspector],
    to inspect the module with [`inspect.getmembers()`][inspect.getmembers].

    The inspection agent works similarly to the regular [`Visitor`][griffe.Visitor] agent,
    in that it maintains a state with the current object being handled, and recursively handle its members.

    Important:
        This function is generally not used directly.
        In most cases, users can rely on the [`GriffeLoader`][griffe.GriffeLoader]
        and its accompanying [`load`][griffe.load] shortcut and their respective options
        to load modules using dynamic analysis.

    Parameters:
        module_name: The module name (as when importing [from] it).
        filepath: The module file path.
        import_paths: Paths to import the module from.
        extensions: The extensions to use when inspecting the module.
        parent: The optional parent of this module.
        docstring_parser: The docstring parser to use. By default, no parsing is done.
        docstring_options: Docstring parsing options.
        lines_collection: A collection of source code lines.
        modules_collection: A collection of modules.

    Returns:
        The module, with its members populated.
    """
    return Inspector(
        module_name,
        filepath,
        extensions or load_extensions(),
        parent,
        docstring_parser=docstring_parser,
        docstring_options=docstring_options,
        lines_collection=lines_collection,
        modules_collection=modules_collection,
    ).get_module(import_paths)
```

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
    docstring_options: DocstringOptions | None = None,
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

  (`DocstringOptions | None`, default: `None` ) – Docstring parsing options.

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
- **`docstring_options`** (`DocstringOptions`) – The docstring parsing options.
- **`docstring_parser`** (`DocstringStyle | Parser | None`) – The docstring parser to use.
- **`extensions`** (`Extensions`) – The extensions to use when visiting the AST.
- **`filepath`** (`Path`) – The module filepath.
- **`lines_collection`** (`LinesCollection`) – A collection of source code lines.
- **`module_name`** (`str`) – The module name.
- **`modules_collection`** (`ModulesCollection`) – A collection of modules.
- **`parent`** (`Module | None`) – An optional parent for the final module object.
- **`type_guarded`** (`bool`) – Whether the current code branch is type-guarded.

Source code in `packages/griffelib/src/griffe/_internal/agents/visitor.py`

```
def __init__(
    self,
    module_name: str,
    filepath: Path,
    code: str,
    extensions: Extensions,
    parent: Module | None = None,
    docstring_parser: DocstringStyle | Parser | None = None,
    docstring_options: DocstringOptions | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
) -> None:
    """Initialize the visitor.

    Parameters:
        module_name: The module name.
        filepath: The module filepath.
        code: The module source code.
        extensions: The extensions to use when visiting.
        parent: An optional parent for the final module object.
        docstring_parser: The docstring parser to use.
        docstring_options: Docstring parsing options.
        lines_collection: A collection of source code lines.
        modules_collection: A collection of modules.
    """
    super().__init__()

    self.module_name: str = module_name
    """The module name."""

    self.filepath: Path = filepath
    """The module filepath."""

    self.code: str = code
    """The module source code."""

    self.extensions: Extensions = extensions
    """The extensions to use when visiting the AST."""

    self.parent: Module | None = parent
    """An optional parent for the final module object."""

    self.current: Module | Class = None
    """The current object being visited."""

    self.docstring_parser: DocstringStyle | Parser | None = docstring_parser
    """The docstring parser to use."""

    self.docstring_options: DocstringOptions = docstring_options or {}
    """The docstring parsing options."""

    self.lines_collection: LinesCollection = lines_collection or LinesCollection()
    """A collection of source code lines."""

    self.modules_collection: ModulesCollection = modules_collection or ModulesCollection()
    """A collection of modules."""

    self.type_guarded: bool = False
    """Whether the current code branch is type-guarded."""
```

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
docstring_options: DocstringOptions = (
    docstring_options or {}
)
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

Source code in `packages/griffelib/src/griffe/_internal/agents/visitor.py`

```
def decorators_to_labels(self, decorators: list[Decorator]) -> set[str]:
    """Build and return a set of labels based on decorators.

    Parameters:
        decorators: The decorators to check.

    Returns:
        A set of labels.
    """
    labels = set()
    for decorator in decorators:
        callable_path = decorator.callable_path
        if callable_path in builtin_decorators:
            labels.add(builtin_decorators[callable_path])
        elif callable_path in stdlib_decorators:
            labels |= stdlib_decorators[callable_path]
    return labels
```

### generic_visit

```
generic_visit(node: AST) -> None
```

Extend the base generic visit with extensions.

Parameters:

- #### **`node`**

  (`AST`) – The node to visit.

Source code in `packages/griffelib/src/griffe/_internal/agents/visitor.py`

```
def generic_visit(self, node: ast.AST) -> None:
    """Extend the base generic visit with extensions.

    Parameters:
        node: The node to visit.
    """
    for child in ast_children(node):
        self.visit(child)
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/visitor.py`

```
def get_base_property(self, decorators: list[Decorator], function: Function) -> str | None:
    """Check decorators to return the base property in case of setters and deleters.

    Parameters:
        decorators: The decorators to check.

    Returns:
        base_property: The property for which the setter/deleted is set.
        property_function: Either `"setter"` or `"deleter"`.
    """
    for decorator in decorators:
        try:
            path, prop_function = decorator.callable_path.rsplit(".", 1)
        except ValueError:
            continue
        property_setter_or_deleter = (
            prop_function in {"setter", "deleter"}
            and path == function.path
            and self.current.get_member(function.name).has_labels("property")
        )
        if property_setter_or_deleter:
            return prop_function
    return None
```

### get_module

```
get_module() -> Module
```

Build and return the object representing the module attached to this visitor.

This method triggers a complete visit of the module nodes.

Returns:

- `Module` – A module instance.

Source code in `packages/griffelib/src/griffe/_internal/agents/visitor.py`

```
def get_module(self) -> Module:
    """Build and return the object representing the module attached to this visitor.

    This method triggers a complete visit of the module nodes.

    Returns:
        A module instance.
    """
    # Optimization: equivalent to `ast.parse`, but with `optimize=1` to remove assert statements.
    # TODO: With options, could use `optimize=2` to remove docstrings.
    top_node = compile(self.code, mode="exec", filename=str(self.filepath), flags=ast.PyCF_ONLY_AST, optimize=1)
    self.visit(top_node)
    return self.current.module
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/visitor.py`

```
def handle_attribute(
    self,
    node: ast.Assign | ast.AnnAssign,
    annotation: str | Expr | None = None,
) -> None:
    """Handle an attribute (assignment) node.

    Parameters:
        node: The node to visit.
        annotation: A potential annotation.
    """
    self.extensions.call("on_node", node=node, agent=self)
    self.extensions.call("on_attribute_node", node=node, agent=self)
    parent = self.current
    labels = set()
    names = None

    if parent.kind is Kind.MODULE:
        try:
            names = get_names(node)
        except KeyError:  # Unsupported nodes, like subscript.
            return
        labels.add("module-attribute")
    elif parent.kind is Kind.CLASS:
        try:
            names = get_names(node)
        except KeyError:  # Unsupported nodes, like subscript.
            return

        if isinstance(annotation, Expr) and annotation.is_classvar:
            # Explicit `ClassVar`: class attribute only.
            annotation = annotation.slice  # ty:ignore[unresolved-attribute]
            labels.add("class-attribute")
        elif node.value:
            # Attribute assigned at class-level: available in instances as well.
            labels.add("class-attribute")
            labels.add("instance-attribute")
        else:
            # Annotated attribute only: not available at class-level.
            labels.add("instance-attribute")

    elif parent.kind is Kind.FUNCTION:
        if parent.name != "__init__":
            return
        try:
            names = get_instance_names(node)
        except KeyError:  # Unsupported nodes, like subscript.
            return
        parent = parent.parent
        if parent is None:
            return
        labels.add("instance-attribute")

    if not names:
        return

    value = safe_get_expression(node.value, parent=self.current, parse_strings=False)

    try:
        docstring = self._get_docstring(ast_next(node), strict=True)
    except (LastNodeError, AttributeError):
        docstring = None

    for name in names:
        # TODO: Handle assigns like `x.y = z`.
        # We need to resolve `x.y` and add `z` in its members.
        if "." in name:
            continue

        if name in parent.members:
            # Assigning multiple times.
            # TODO: Might be better to inspect.
            if isinstance(node.parent, (ast.If, ast.ExceptHandler)):  # ty:ignore[unresolved-attribute]
                continue  # Prefer "no-exception" case.

            existing_member = parent.members[name]
            with suppress(AliasResolutionError, CyclicAliasError):
                labels |= existing_member.labels
                # Forward previous docstring and annotation instead of erasing them.
                if existing_member.docstring and not docstring:
                    docstring = existing_member.docstring
                with suppress(AttributeError):
                    if existing_member.annotation and not annotation:  # ty:ignore[possibly-missing-attribute]
                        annotation = existing_member.annotation  # ty:ignore[possibly-missing-attribute]

        attribute = Attribute(
            name=name,
            value=value,
            annotation=annotation,
            lineno=node.lineno,
            endlineno=node.end_lineno,
            docstring=docstring,
            runtime=not self.type_guarded,
            analysis="static",
        )
        attribute.labels |= labels
        parent.set_member(name, attribute)

        if name == "__all__":
            with suppress(AttributeError):
                parent.exports = [
                    name if isinstance(name, str) else ExprName(name.name, parent=name.parent)
                    for name in safe_get__all__(node, self.current)  # ty:ignore[invalid-argument-type]
                ]
        self.extensions.call("on_instance", node=node, obj=attribute, agent=self)
        self.extensions.call("on_attribute_instance", node=node, attr=attribute, agent=self)
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/visitor.py`

```
def handle_function(self, node: ast.AsyncFunctionDef | ast.FunctionDef, labels: set | None = None) -> None:
    """Handle a function definition node.

    Parameters:
        node: The node to visit.
        labels: Labels to add to the data object.
    """
    self.extensions.call("on_node", node=node, agent=self)
    self.extensions.call("on_function_node", node=node, agent=self)

    labels = labels or set()

    # Handle decorators.
    decorators = []
    overload = False
    if node.decorator_list:
        lineno = node.decorator_list[0].lineno
        for decorator_node in node.decorator_list:
            decorator_value = safe_get_expression(decorator_node, parent=self.current, parse_strings=False)
            if decorator_value is None:
                continue
            decorator = Decorator(
                decorator_value,
                lineno=decorator_node.lineno,
                endlineno=decorator_node.end_lineno,
            )
            decorators.append(decorator)
            overload |= decorator.callable_path in typing_overload
    else:
        lineno = node.lineno

    labels |= self.decorators_to_labels(decorators)

    if "property" in labels:
        attribute = Attribute(
            name=node.name,
            value=None,
            annotation=safe_get_annotation(node.returns, parent=self.current, member=node.name),
            lineno=node.lineno,
            endlineno=node.end_lineno,
            docstring=self._get_docstring(node),
            runtime=not self.type_guarded,
            analysis="static",
        )
        attribute.labels |= labels
        self.current.set_member(node.name, attribute)
        self.extensions.call("on_instance", node=node, obj=attribute, agent=self)
        self.extensions.call("on_attribute_instance", node=node, attr=attribute, agent=self)
        return

    # Handle parameters.
    parameters = Parameters(
        *[
            Parameter(
                name,
                kind=kind,
                annotation=safe_get_annotation(annotation, parent=self.current, member=node.name),
                default=default
                if isinstance(default, str)
                else safe_get_expression(default, parent=self.current, parse_strings=False),
            )
            for name, annotation, kind, default in get_parameters(node.args)
        ],
    )

    function = Function(
        name=node.name,
        lineno=lineno,
        endlineno=node.end_lineno,
        parameters=parameters,
        returns=safe_get_annotation(node.returns, parent=self.current, member=node.name),
        decorators=decorators,
        type_parameters=TypeParameters(*self._get_type_parameters(node, scope=node.name)),
        docstring=self._get_docstring(node),
        runtime=not self.type_guarded,
        parent=self.current,
        analysis="static",
    )

    property_function = self.get_base_property(decorators, function)

    if overload:
        self.current.overloads[function.name].append(function)
    elif property_function:
        base_property: Attribute = self.current.members[node.name]  # ty:ignore[invalid-assignment]
        if property_function == "setter":
            base_property.setter = function
            base_property.labels.add("writable")
        elif property_function == "deleter":
            base_property.deleter = function
            base_property.labels.add("deletable")
    else:
        self.current.set_member(node.name, function)
        if self.current.kind in {Kind.MODULE, Kind.CLASS} and self.current.overloads[function.name]:
            function.overloads = self.current.overloads[function.name]
            del self.current.overloads[function.name]

    function.labels |= labels

    self.extensions.call("on_instance", node=node, obj=function, agent=self)
    self.extensions.call("on_function_instance", node=node, func=function, agent=self)
    if self.current.kind is Kind.CLASS and function.name == "__init__":
        self.current = function  # ty:ignore[invalid-assignment]
        self.generic_visit(node)
        self.current = self.current.parent  # ty:ignore[invalid-assignment]
```

### visit

```
visit(node: AST) -> None
```

Extend the base visit with extensions.

Parameters:

- #### **`node`**

  (`AST`) – The node to visit.

Source code in `packages/griffelib/src/griffe/_internal/agents/visitor.py`

```
def visit(self, node: ast.AST) -> None:
    """Extend the base visit with extensions.

    Parameters:
        node: The node to visit.
    """
    getattr(self, f"visit_{ast_kind(node)}", self.generic_visit)(node)
```

### visit_annassign

```
visit_annassign(node: AnnAssign) -> None
```

Visit an annotated assignment node.

Parameters:

- #### **`node`**

  (`AnnAssign`) – The node to visit.

Source code in `packages/griffelib/src/griffe/_internal/agents/visitor.py`

```
def visit_annassign(self, node: ast.AnnAssign) -> None:
    """Visit an annotated assignment node.

    Parameters:
        node: The node to visit.
    """
    self.handle_attribute(node, safe_get_annotation(node.annotation, parent=self.current))
```

### visit_assign

```
visit_assign(node: Assign) -> None
```

Visit an assignment node.

Parameters:

- #### **`node`**

  (`Assign`) – The node to visit.

Source code in `packages/griffelib/src/griffe/_internal/agents/visitor.py`

```
def visit_assign(self, node: ast.Assign) -> None:
    """Visit an assignment node.

    Parameters:
        node: The node to visit.
    """
    self.handle_attribute(node)
```

### visit_asyncfunctiondef

```
visit_asyncfunctiondef(node: AsyncFunctionDef) -> None
```

Visit an async function definition node.

Parameters:

- #### **`node`**

  (`AsyncFunctionDef`) – The node to visit.

Source code in `packages/griffelib/src/griffe/_internal/agents/visitor.py`

```
def visit_asyncfunctiondef(self, node: ast.AsyncFunctionDef) -> None:
    """Visit an async function definition node.

    Parameters:
        node: The node to visit.
    """
    self.handle_function(node, labels={"async"})
```

### visit_augassign

```
visit_augassign(node: AugAssign) -> None
```

Visit an augmented assignment node.

Parameters:

- #### **`node`**

  (`AugAssign`) – The node to visit.

Source code in `packages/griffelib/src/griffe/_internal/agents/visitor.py`

```
def visit_augassign(self, node: ast.AugAssign) -> None:
    """Visit an augmented assignment node.

    Parameters:
        node: The node to visit.
    """
    with suppress(AttributeError):
        all_augment = (
            node.target.id == "__all__"  # ty:ignore[possibly-missing-attribute]
            and self.current.is_module
            and isinstance(node.op, ast.Add)
        )
        if all_augment:
            # We assume `exports` is not `None` at this point.
            self.current.exports.extend(  # ty:ignore[possibly-missing-attribute]
                [
                    name if isinstance(name, str) else ExprName(name.name, parent=name.parent)
                    for name in safe_get__all__(node, self.current)  # ty:ignore[invalid-argument-type]
                ],
            )
```

### visit_classdef

```
visit_classdef(node: ClassDef) -> None
```

Visit a class definition node.

Parameters:

- #### **`node`**

  (`ClassDef`) – The node to visit.

Source code in `packages/griffelib/src/griffe/_internal/agents/visitor.py`

```
def visit_classdef(self, node: ast.ClassDef) -> None:
    """Visit a class definition node.

    Parameters:
        node: The node to visit.
    """
    self.extensions.call("on_node", node=node, agent=self)
    self.extensions.call("on_class_node", node=node, agent=self)

    # Handle decorators.
    decorators: list[Decorator] = []
    if node.decorator_list:
        lineno = node.decorator_list[0].lineno
        decorators.extend(
            Decorator(
                safe_get_expression(decorator_node, parent=self.current, parse_strings=False),  # ty:ignore[invalid-argument-type]
                lineno=decorator_node.lineno,
                endlineno=decorator_node.end_lineno,
            )
            for decorator_node in node.decorator_list
        )
    else:
        lineno = node.lineno

    # Handle base classes and keywords.
    bases = [safe_get_base_class(base, parent=self.current, member=node.name) for base in node.bases]
    keywords = {
        kw.arg: safe_get_class_keyword(kw.value, parent=self.current) for kw in node.keywords if kw.arg is not None
    }

    class_ = Class(
        name=node.name,
        lineno=lineno,
        endlineno=node.end_lineno,
        docstring=self._get_docstring(node),
        decorators=decorators,
        type_parameters=TypeParameters(*self._get_type_parameters(node, scope=node.name)),
        bases=bases,  # ty:ignore[invalid-argument-type]
        keywords=keywords,
        runtime=not self.type_guarded,
        analysis="static",
    )
    class_.labels |= self.decorators_to_labels(decorators)

    self.current.set_member(node.name, class_)
    self.current = class_
    self.extensions.call("on_instance", node=node, obj=class_, agent=self)
    self.extensions.call("on_class_instance", node=node, cls=class_, agent=self)
    self.generic_visit(node)
    self.extensions.call("on_members", node=node, obj=class_, agent=self)
    self.extensions.call("on_class_members", node=node, cls=class_, agent=self)
    self.current = self.current.parent  # ty:ignore[invalid-assignment]
```

### visit_functiondef

```
visit_functiondef(node: FunctionDef) -> None
```

Visit a function definition node.

Parameters:

- #### **`node`**

  (`FunctionDef`) – The node to visit.

Source code in `packages/griffelib/src/griffe/_internal/agents/visitor.py`

```
def visit_functiondef(self, node: ast.FunctionDef) -> None:
    """Visit a function definition node.

    Parameters:
        node: The node to visit.
    """
    self.handle_function(node)
```

### visit_if

```
visit_if(node: If) -> None
```

Visit an "if" node.

Parameters:

- #### **`node`**

  (`If`) – The node to visit.

Source code in `packages/griffelib/src/griffe/_internal/agents/visitor.py`

```
def visit_if(self, node: ast.If) -> None:
    """Visit an "if" node.

    Parameters:
        node: The node to visit.
    """
    if isinstance(node.parent, (ast.Module, ast.ClassDef)):  # ty:ignore[unresolved-attribute]
        condition = safe_get_condition(node.test, parent=self.current, log_level=None)
        if str(condition) in {"typing.TYPE_CHECKING", "TYPE_CHECKING"}:
            self.type_guarded = True
    self.generic_visit(node)
    self.type_guarded = False
```

### visit_import

```
visit_import(node: Import) -> None
```

Visit an import node.

Parameters:

- #### **`node`**

  (`Import`) – The node to visit.

Source code in `packages/griffelib/src/griffe/_internal/agents/visitor.py`

```
def visit_import(self, node: ast.Import) -> None:
    """Visit an import node.

    Parameters:
        node: The node to visit.
    """
    for name in node.names:
        alias_path = name.name if name.asname else name.name.split(".", 1)[0]
        alias_name = name.asname or alias_path.split(".", 1)[0]
        self.current.imports[alias_name] = alias_path
        alias = Alias(
            alias_name,
            alias_path,
            lineno=node.lineno,
            endlineno=node.end_lineno,
            runtime=not self.type_guarded,
            analysis="static",
        )
        self.current.set_member(alias_name, alias)
        self.extensions.call("on_alias_instance", alias=alias, node=node, agent=self)
```

### visit_importfrom

```
visit_importfrom(node: ImportFrom) -> None
```

Visit an "import from" node.

Parameters:

- #### **`node`**

  (`ImportFrom`) – The node to visit.

Source code in `packages/griffelib/src/griffe/_internal/agents/visitor.py`

```
def visit_importfrom(self, node: ast.ImportFrom) -> None:
    """Visit an "import from" node.

    Parameters:
        node: The node to visit.
    """
    for name in node.names:
        if not node.module and node.level == 1 and not name.asname and self.current.module.is_init_module:
            # Special case: when being in `a/__init__.py` and doing `from . import b`,
            # we are effectively creating a member `b` in `a` that is pointing to `a.b`
            # -> cyclic alias! In that case, we just skip it, as both the member and module
            # have the same name and can be accessed the same way.
            continue

        alias_path = relative_to_absolute(node, name, self.current.module)
        if name.name == "*":
            alias_name = alias_path.replace(".", "/")
            alias_path = alias_path.replace(".*", "")
        else:
            alias_name = name.asname or name.name
            self.current.imports[alias_name] = alias_path
        # Do not create aliases pointing to themselves (it happens with
        # `from package.current_module import Thing as Thing` or
        # `from . import thing as thing`).
        if alias_path != f"{self.current.path}.{alias_name}":
            alias = Alias(
                alias_name,
                alias_path,
                lineno=node.lineno,
                endlineno=node.end_lineno,
                runtime=not self.type_guarded,
                analysis="static",
            )
            self.current.set_member(alias_name, alias)
            self.extensions.call("on_alias_instance", alias=alias, node=node, agent=self)
```

### visit_module

```
visit_module(node: Module) -> None
```

Visit a module node.

Parameters:

- #### **`node`**

  (`Module`) – The node to visit.

Source code in `packages/griffelib/src/griffe/_internal/agents/visitor.py`

```
def visit_module(self, node: ast.Module) -> None:
    """Visit a module node.

    Parameters:
        node: The node to visit.
    """
    self.extensions.call("on_node", node=node, agent=self)
    self.extensions.call("on_module_node", node=node, agent=self)
    self.current = module = Module(
        name=self.module_name,
        filepath=self.filepath,
        parent=self.parent,
        docstring=self._get_docstring(node),
        lines_collection=self.lines_collection,
        modules_collection=self.modules_collection,
        analysis="static",
    )
    self.extensions.call("on_instance", node=node, obj=module, agent=self)
    self.extensions.call("on_module_instance", node=node, mod=module, agent=self)
    self.generic_visit(node)
    self.extensions.call("on_members", node=node, obj=module, agent=self)
    self.extensions.call("on_module_members", node=node, mod=module, agent=self)
```

### visit_typealias

```
visit_typealias(node: TypeAlias) -> None
```

Visit a type alias node.

Parameters:

- #### **`node`**

  (`TypeAlias`) – The node to visit.

Source code in `packages/griffelib/src/griffe/_internal/agents/visitor.py`

```
def visit_typealias(self, node: ast.TypeAlias) -> None:
    """Visit a type alias node.

    Parameters:
        node: The node to visit.
    """
    self.extensions.call("on_node", node=node, agent=self)
    self.extensions.call("on_type_alias_node", node=node, agent=self)

    # A type alias's name attribute is syntactically a single NAME,
    # but represented as an expression in the AST.
    # https://jellezijlstra.github.io/pep695#ast

    name = node.name.id

    value = safe_get_expression(node.value, parent=self.current, member=name)

    try:
        docstring = self._get_docstring(ast_next(node), strict=True)
    except (LastNodeError, AttributeError):
        docstring = None

    type_alias = TypeAlias(
        name=name,
        value=value,
        lineno=node.lineno,
        endlineno=node.end_lineno,
        type_parameters=TypeParameters(*self._get_type_parameters(node, scope=name)),
        docstring=docstring,
        parent=self.current,
        analysis="static",
    )
    self.current.set_member(name, type_alias)
    self.extensions.call("on_instance", node=node, obj=type_alias, agent=self)
    self.extensions.call("on_type_alias_instance", node=node, type_alias=type_alias, agent=self)
```

## Inspector

```
Inspector(
    module_name: str,
    filepath: Path | None,
    extensions: Extensions,
    parent: Module | None = None,
    docstring_parser: DocstringStyle | Parser | None = None,
    docstring_options: DocstringOptions | None = None,
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

  (`DocstringOptions | None`, default: `None` ) – Docstring parsing options.

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
- **`docstring_options`** (`DocstringOptions`) – The docstring parsing options.
- **`docstring_parser`** (`DocstringStyle | Parser | None`) – The docstring parser to use.
- **`extensions`** (`Extensions`) – The extensions to use when inspecting.
- **`filepath`** (`Path | None`) – The module file path.
- **`lines_collection`** (`LinesCollection`) – A collection of source code lines.
- **`module_name`** (`str`) – The module name.
- **`modules_collection`** (`ModulesCollection`) – A collection of modules.
- **`parent`** (`Module | None`) – An optional parent for the final module object.

Source code in `packages/griffelib/src/griffe/_internal/agents/inspector.py`

```
def __init__(
    self,
    module_name: str,
    filepath: Path | None,
    extensions: Extensions,
    parent: Module | None = None,
    docstring_parser: DocstringStyle | Parser | None = None,
    docstring_options: DocstringOptions | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
) -> None:
    """Initialize the inspector.

    Parameters:
        module_name: The module name.
        filepath: The optional filepath.
        extensions: Extensions to use when inspecting.
        parent: The module parent.
        docstring_parser: The docstring parser to use.
        docstring_options: Docstring parsing options.
        lines_collection: A collection of source code lines.
        modules_collection: A collection of modules.
    """
    super().__init__()

    self.module_name: str = module_name
    """The module name."""

    self.filepath: Path | None = filepath
    """The module file path."""

    self.extensions: Extensions = extensions
    """The extensions to use when inspecting."""

    self.parent: Module | None = parent
    """An optional parent for the final module object."""

    self.current: Module | Class = None
    """The current object being inspected."""

    self.docstring_parser: DocstringStyle | Parser | None = docstring_parser
    """The docstring parser to use."""

    self.docstring_options: DocstringOptions = docstring_options or {}
    """The docstring parsing options."""

    self.lines_collection: LinesCollection = lines_collection or LinesCollection()
    """A collection of source code lines."""

    self.modules_collection: ModulesCollection = modules_collection or ModulesCollection()
    """A collection of modules."""
```

### current

```
current: Module | Class = None
```

The current object being inspected.

### docstring_options

```
docstring_options: DocstringOptions = (
    docstring_options or {}
)
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

Source code in `packages/griffelib/src/griffe/_internal/agents/inspector.py`

```
def generic_inspect(self, node: ObjectNode) -> None:
    """Extend the base generic inspection with extensions.

    Parameters:
        node: The node to inspect.
    """
    for child in node.children:
        if target_path := child.alias_target_path:
            # If the child is an actual submodule of the current module,
            # and has no `__file__` set, we won't find it on the disk so we must inspect it now.
            # For that we instantiate a new inspector and use it to inspect the submodule,
            # then assign the submodule as member of the current module.
            # If the submodule has a `__file__` set, the loader should find it on the disk,
            # so we skip it here (no member, no alias, just skip it).
            if child.is_module and target_path == f"{self.current.path}.{child.name}":
                if not hasattr(child.obj, "__file__"):
                    logger.debug("Module %s is not discoverable on disk, inspecting right now", target_path)
                    inspector = Inspector(
                        child.name,
                        filepath=None,
                        parent=self.current.module,
                        extensions=self.extensions,
                        docstring_parser=self.docstring_parser,
                        docstring_options=self.docstring_options,
                        lines_collection=self.lines_collection,
                        modules_collection=self.modules_collection,
                    )
                    inspector.inspect_module(child)
                    self.current.set_member(child.name, inspector.current.module)
            # Otherwise, alias the object.
            else:
                alias = Alias(child.name, target_path, analysis="dynamic")
                self.current.set_member(child.name, alias)
                self.extensions.call("on_alias_instance", alias=alias, node=node, agent=self)
        else:
            self.inspect(child)
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/inspector.py`

```
def get_module(self, import_paths: Sequence[str | Path] | None = None) -> Module:
    """Build and return the object representing the module attached to this inspector.

    This method triggers a complete inspection of the module members.

    Parameters:
        import_paths: Paths replacing `sys.path` to import the module.

    Returns:
        A module instance.
    """
    import_path = self.module_name
    if self.parent is not None:
        import_path = f"{self.parent.path}.{import_path}"

    # Make sure `import_paths` is a list, in case we want to `insert` into it.
    import_paths = list(import_paths or ())

    # If the thing we want to import has a filepath,
    # we make sure to insert the right parent directory
    # at the front of our list of import paths.
    # We do this by counting the number of dots `.` in the import path,
    # corresponding to slashes `/` in the filesystem,
    # and go up in the file tree the same number of times.
    if self.filepath:
        parent_path = self.filepath.parent
        for _ in range(import_path.count(".")):
            parent_path = parent_path.parent
        # Climb up one more time for `__init__` modules.
        if self.filepath.stem == "__init__":
            parent_path = parent_path.parent
        if parent_path not in import_paths:
            import_paths.insert(0, parent_path)

    value = dynamic_import(import_path, import_paths)

    # We successfully imported the given object,
    # and we now create the object tree with all the necessary nodes,
    # from the root of the package to this leaf object.
    parent_node = None
    if self.parent is not None:
        for part in self.parent.path.split("."):
            parent_node = ObjectNode(None, name=part, parent=parent_node)
    module_node = ObjectNode(value, self.module_name, parent=parent_node)

    self.inspect(module_node)
    return self.current.module
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/inspector.py`

```
def handle_attribute(self, node: ObjectNode, annotation: str | Expr | None = None) -> None:
    """Handle an attribute.

    Parameters:
        node: The node to inspect.
        annotation: A potential annotation.
    """
    self.extensions.call("on_node", node=node, agent=self)
    self.extensions.call("on_attribute_node", node=node, agent=self)

    # TODO: To improve.
    parent = self.current
    labels: set[str] = set()

    if parent.kind is Kind.MODULE:
        labels.add("module-attribute")
    elif parent.kind is Kind.CLASS:
        labels.add("class-attribute")
    elif parent.kind is Kind.FUNCTION:
        if parent.name != "__init__":
            return
        parent = parent.parent
        labels.add("instance-attribute")

    try:
        value = repr(node.obj)
    except Exception:  # noqa: BLE001
        value = None
    try:
        docstring = self._get_docstring(node)
    except Exception:  # noqa: BLE001
        docstring = None

    attribute = Attribute(
        name=node.name,
        value=value,
        annotation=annotation,
        docstring=docstring,
        analysis="dynamic",
    )
    attribute.labels |= labels
    parent.set_member(node.name, attribute)  # ty:ignore[possibly-missing-attribute]

    if node.name == "__all__":
        parent.exports = list(node.obj)  # ty:ignore[invalid-assignment]
    self.extensions.call("on_instance", node=node, obj=attribute, agent=self)
    self.extensions.call("on_attribute_instance", node=node, attr=attribute, agent=self)
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/inspector.py`

```
def handle_function(self, node: ObjectNode, labels: set | None = None) -> None:
    """Handle a function.

    Parameters:
        node: The node to inspect.
        labels: Labels to add to the data object.
    """
    self.extensions.call("on_node", node=node, agent=self)
    self.extensions.call("on_function_node", node=node, agent=self)

    try:
        signature = getsignature(node.obj)
    except Exception:  # noqa: BLE001
        # So many exceptions can be raised here:
        # AttributeError, NameError, RuntimeError, ValueError, TokenError, TypeError...
        parameters = None
        returns = None
    else:
        parameters = Parameters(
            *[
                _convert_parameter(parameter, parent=self.current, member=node.name)
                for parameter in signature.parameters.values()
            ],
        )
        return_annotation = signature.return_annotation
        returns = (
            None
            if return_annotation is _empty
            else _convert_object_to_annotation(return_annotation, parent=self.current, member=node.name)
        )

    lineno, endlineno = self._get_linenos(node)

    obj: Attribute | Function
    labels = labels or set()
    if "property" in labels:
        obj = Attribute(
            name=node.name,
            value=None,
            annotation=returns,
            docstring=self._get_docstring(node),
            lineno=lineno,
            endlineno=endlineno,
            analysis="dynamic",
        )
    else:
        obj = Function(
            name=node.name,
            parameters=parameters,
            returns=returns,
            type_parameters=TypeParameters(
                *_convert_type_parameters(node.obj, parent=self.current, member=node.name),
            ),
            docstring=self._get_docstring(node),
            lineno=lineno,
            endlineno=endlineno,
            analysis="dynamic",
        )
    obj.labels |= labels
    self.current.set_member(node.name, obj)
    self.extensions.call("on_instance", node=node, obj=obj, agent=self)
    if obj.is_attribute:
        self.extensions.call("on_attribute_instance", node=node, attr=obj, agent=self)
    else:
        self.extensions.call("on_function_instance", node=node, func=obj, agent=self)
```

### inspect

```
inspect(node: ObjectNode) -> None
```

Extend the base inspection with extensions.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

Source code in `packages/griffelib/src/griffe/_internal/agents/inspector.py`

```
def inspect(self, node: ObjectNode) -> None:
    """Extend the base inspection with extensions.

    Parameters:
        node: The node to inspect.
    """
    getattr(self, f"inspect_{node.kind}", self.generic_inspect)(node)
```

### inspect_attribute

```
inspect_attribute(node: ObjectNode) -> None
```

Inspect an attribute.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

Source code in `packages/griffelib/src/griffe/_internal/agents/inspector.py`

```
def inspect_attribute(self, node: ObjectNode) -> None:
    """Inspect an attribute.

    Parameters:
        node: The node to inspect.
    """
    self.handle_attribute(node)
```

### inspect_builtin_function

```
inspect_builtin_function(node: ObjectNode) -> None
```

Inspect a builtin function.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

Source code in `packages/griffelib/src/griffe/_internal/agents/inspector.py`

```
def inspect_builtin_function(self, node: ObjectNode) -> None:
    """Inspect a builtin function.

    Parameters:
        node: The node to inspect.
    """
    self.handle_function(node, {"builtin"})
```

### inspect_builtin_method

```
inspect_builtin_method(node: ObjectNode) -> None
```

Inspect a builtin method.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

Source code in `packages/griffelib/src/griffe/_internal/agents/inspector.py`

```
def inspect_builtin_method(self, node: ObjectNode) -> None:
    """Inspect a builtin method.

    Parameters:
        node: The node to inspect.
    """
    self.handle_function(node, {"builtin"})
```

### inspect_cached_property

```
inspect_cached_property(node: ObjectNode) -> None
```

Inspect a cached property.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

Source code in `packages/griffelib/src/griffe/_internal/agents/inspector.py`

```
def inspect_cached_property(self, node: ObjectNode) -> None:
    """Inspect a cached property.

    Parameters:
        node: The node to inspect.
    """
    self.handle_function(node, {"cached", "property"})
```

### inspect_class

```
inspect_class(node: ObjectNode) -> None
```

Inspect a class.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

Source code in `packages/griffelib/src/griffe/_internal/agents/inspector.py`

```
def inspect_class(self, node: ObjectNode) -> None:
    """Inspect a class.

    Parameters:
        node: The node to inspect.
    """
    self.extensions.call("on_node", node=node, agent=self)
    self.extensions.call("on_class_node", node=node, agent=self)

    bases = []
    for base in node.obj.__bases__:
        if base is object:
            continue
        bases.append(f"{base.__module__}.{base.__qualname__}")

    lineno, endlineno = self._get_linenos(node)
    class_ = Class(
        name=node.name,
        docstring=self._get_docstring(node),
        bases=bases,
        type_parameters=TypeParameters(*_convert_type_parameters(node.obj, parent=self.current, member=node.name)),
        lineno=lineno,
        endlineno=endlineno,
        analysis="dynamic",
    )
    self.current.set_member(node.name, class_)
    self.current = class_
    self.extensions.call("on_instance", node=node, obj=class_, agent=self)
    self.extensions.call("on_class_instance", node=node, cls=class_, agent=self)
    self.generic_inspect(node)
    self.extensions.call("on_members", node=node, obj=class_, agent=self)
    self.extensions.call("on_class_members", node=node, cls=class_, agent=self)
    self.current = self.current.parent  # ty:ignore[invalid-assignment]
```

### inspect_classmethod

```
inspect_classmethod(node: ObjectNode) -> None
```

Inspect a class method.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

Source code in `packages/griffelib/src/griffe/_internal/agents/inspector.py`

```
def inspect_classmethod(self, node: ObjectNode) -> None:
    """Inspect a class method.

    Parameters:
        node: The node to inspect.
    """
    self.handle_function(node, {"classmethod"})
```

### inspect_coroutine

```
inspect_coroutine(node: ObjectNode) -> None
```

Inspect a coroutine.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

Source code in `packages/griffelib/src/griffe/_internal/agents/inspector.py`

```
def inspect_coroutine(self, node: ObjectNode) -> None:
    """Inspect a coroutine.

    Parameters:
        node: The node to inspect.
    """
    self.handle_function(node, {"async"})
```

### inspect_function

```
inspect_function(node: ObjectNode) -> None
```

Inspect a function.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

Source code in `packages/griffelib/src/griffe/_internal/agents/inspector.py`

```
def inspect_function(self, node: ObjectNode) -> None:
    """Inspect a function.

    Parameters:
        node: The node to inspect.
    """
    self.handle_function(node)
```

### inspect_getset_descriptor

```
inspect_getset_descriptor(node: ObjectNode) -> None
```

Inspect a get/set descriptor.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

Source code in `packages/griffelib/src/griffe/_internal/agents/inspector.py`

```
def inspect_getset_descriptor(self, node: ObjectNode) -> None:
    """Inspect a get/set descriptor.

    Parameters:
        node: The node to inspect.
    """
    self.handle_function(node, {"property"})
```

### inspect_method

```
inspect_method(node: ObjectNode) -> None
```

Inspect a method.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

Source code in `packages/griffelib/src/griffe/_internal/agents/inspector.py`

```
def inspect_method(self, node: ObjectNode) -> None:
    """Inspect a method.

    Parameters:
        node: The node to inspect.
    """
    self.handle_function(node)
```

### inspect_method_descriptor

```
inspect_method_descriptor(node: ObjectNode) -> None
```

Inspect a method descriptor.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

Source code in `packages/griffelib/src/griffe/_internal/agents/inspector.py`

```
def inspect_method_descriptor(self, node: ObjectNode) -> None:
    """Inspect a method descriptor.

    Parameters:
        node: The node to inspect.
    """
    self.handle_function(node, {"method descriptor"})
```

### inspect_module

```
inspect_module(node: ObjectNode) -> None
```

Inspect a module.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

Source code in `packages/griffelib/src/griffe/_internal/agents/inspector.py`

```
def inspect_module(self, node: ObjectNode) -> None:
    """Inspect a module.

    Parameters:
        node: The node to inspect.
    """
    self.extensions.call("on_node", node=node, agent=self)
    self.extensions.call("on_module_node", node=node, agent=self)
    self.current = module = Module(
        name=self.module_name,
        filepath=self.filepath,
        parent=self.parent,
        docstring=self._get_docstring(node),
        lines_collection=self.lines_collection,
        modules_collection=self.modules_collection,
        analysis="dynamic",
    )
    self.extensions.call("on_instance", node=node, obj=module, agent=self)
    self.extensions.call("on_module_instance", node=node, mod=module, agent=self)
    self.generic_inspect(node)
    self.extensions.call("on_members", node=node, obj=module, agent=self)
    self.extensions.call("on_module_members", node=node, mod=module, agent=self)
```

### inspect_property

```
inspect_property(node: ObjectNode) -> None
```

Inspect a property.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

Source code in `packages/griffelib/src/griffe/_internal/agents/inspector.py`

```
def inspect_property(self, node: ObjectNode) -> None:
    """Inspect a property.

    Parameters:
        node: The node to inspect.
    """
    self.handle_function(node, {"property"})
```

### inspect_staticmethod

```
inspect_staticmethod(node: ObjectNode) -> None
```

Inspect a static method.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

Source code in `packages/griffelib/src/griffe/_internal/agents/inspector.py`

```
def inspect_staticmethod(self, node: ObjectNode) -> None:
    """Inspect a static method.

    Parameters:
        node: The node to inspect.
    """
    self.handle_function(node, {"staticmethod"})
```

### inspect_type_alias

```
inspect_type_alias(node: ObjectNode) -> None
```

Inspect a type alias.

Parameters:

- #### **`node`**

  (`ObjectNode`) – The node to inspect.

Source code in `packages/griffelib/src/griffe/_internal/agents/inspector.py`

```
def inspect_type_alias(self, node: ObjectNode) -> None:
    """Inspect a type alias.

    Parameters:
        node: The node to inspect.
    """
    self.extensions.call("on_node", node=node, agent=self)
    self.extensions.call("on_type_alias_node", node=node, agent=self)

    lineno, endlineno = self._get_linenos(node)

    type_alias = TypeAlias(
        name=node.name,
        value=_convert_type_to_annotation(node.obj.__value__, parent=self.current, member=node.name),
        lineno=lineno,
        endlineno=endlineno,
        type_parameters=TypeParameters(*_convert_type_parameters(node.obj, parent=self.current, member=node.name)),
        docstring=self._get_docstring(node),
        parent=self.current,
        analysis="dynamic",
    )
    self.current.set_member(node.name, type_alias)
    self.extensions.call("on_instance", node=node, obj=type_alias, agent=self)
    self.extensions.call("on_type_alias_instance", node=node, type_alias=type_alias, agent=self)
```

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

Source code in `packages/griffelib/src/griffe/_internal/importer.py`

```
@contextmanager
def sys_path(*paths: str | Path) -> Iterator[None]:
    """Redefine `sys.path` temporarily.

    Parameters:
        *paths: The paths to use when importing modules.
            If no paths are given, keep `sys.path` untouched.

    Yields:
        Nothing.
    """
    if not paths:
        yield
        return
    old_path = sys.path
    sys.path = [str(path) for path in paths]
    try:
        yield
    finally:
        sys.path = old_path
```

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

Source code in `packages/griffelib/src/griffe/_internal/importer.py`

```
def dynamic_import(import_path: str, import_paths: Sequence[str | Path] | None = None) -> Any:
    """Dynamically import the specified object.

    It can be a module, class, method, function, attribute, type alias,
    nested arbitrarily.

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

    Since the function potentially tries multiple things before succeeding,
    all errors happening along the way are recorded, and re-emitted with
    an `ImportError` when it fails, to let users know what was tried.

    IMPORTANT: The paths given through the `import_paths` parameter are used
    to temporarily patch `sys.path`: this function is therefore not thread-safe.

    IMPORTANT: The paths given as `import_paths` must be *correct*.
    The contents of `sys.path` must be consistent to what a user of the imported code
    would expect. Given a set of paths, if the import fails for a user, it will fail here too,
    with potentially unintuitive errors. If we wanted to make this function more robust,
    we could add a loop to "roll the window" of given paths, shifting them to the left
    (for example: `("/a/a", "/a/b", "/a/c/")`, then `("/a/b", "/a/c", "/a/a/")`,
    then `("/a/c", "/a/a", "/a/b/")`), to make sure each entry is given highest priority
    at least once, maintaining relative order, but we deem this unnecessary for now.

    Parameters:
        import_path: The path of the object to import.
        import_paths: The (sys) paths to import the object from.

    Raises:
        ModuleNotFoundError: When the object's module could not be found.
        ImportError: When there was an import error or when couldn't get the attribute.

    Returns:
        The imported object.
    """
    module_parts: list[str] = import_path.split(".")
    object_parts: list[str] = []
    errors = []

    with sys_path(*(import_paths or ())):
        while module_parts:
            module_path = ".".join(module_parts)
            try:
                module = import_module(module_path)
            except BaseException as error:  # noqa: BLE001
                # pyo3's PanicException can only be caught with BaseException.
                # We do want to catch base exceptions anyway (exit, interrupt, etc.).
                errors.append(_error_details(error, module_path))
                object_parts.insert(0, module_parts.pop(-1))
            else:
                break
        else:
            raise ImportError("; ".join(errors))

        # Sometimes extra dependencies are not installed,
        # so importing the leaf module fails with a ModuleNotFoundError,
        # or later `getattr` triggers additional code that fails.
        # In these cases, and for consistency, we always re-raise an ImportError
        # instead of an any other exception (it's called "dynamic import" after all).
        # See https://github.com/mkdocstrings/mkdocstrings/issues/380.
        value = module
        for part in object_parts:
            try:
                value = getattr(value, part)
            except BaseException as error:  # noqa: BLE001
                errors.append(_error_details(error, module_path + ":" + ".".join(object_parts)))
                raise ImportError("; ".join(errors))  # noqa: B904

    return value
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/nodes/runtime.py`

```
def __init__(self, obj: Any, name: str, parent: ObjectNode | None = None) -> None:
    """Initialize the object.

    Parameters:
        obj: A Python object.
        name: The object's name.
        parent: The object's parent node.
    """
    # Unwrap object.
    try:
        obj = inspect.unwrap(obj)
    except Exception as error:  # noqa: BLE001
        # `inspect.unwrap` at some point runs `hasattr(obj, "__wrapped__")`,
        # which triggers the `__getattr__` method of the object, which in
        # turn can raise various exceptions. Probably not just `__getattr__`.
        # See https://github.com/pawamoy/pytkdocs/issues/45.
        logger.debug("Could not unwrap %s: %r", name, error)

    # Unwrap cached properties (`inspect.unwrap` doesn't do that).
    if isinstance(obj, cached_property):
        is_cached_property = True
        obj = obj.func
    else:
        is_cached_property = False

    self.obj: Any = obj
    """The actual Python object."""
    self.name: str = name
    """The Python object's name."""
    self.parent: ObjectNode | None = parent
    """The parent node."""
    self.is_cached_property: bool = is_cached_property
    """Whether this node's object is a cached property."""
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/nodes/ast.py`

```
def ast_kind(node: AST) -> str:
    """Return the kind of an AST node.

    Parameters:
        node: The AST node.

    Returns:
        The node kind.
    """
    return node.__class__.__name__.lower()
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/nodes/ast.py`

```
def ast_children(node: AST) -> Iterator[AST]:
    """Return the children of an AST node.

    Parameters:
        node: The AST node.

    Yields:
        The node children.
    """
    for field_name in node._fields:
        try:
            field = getattr(node, field_name)
        except AttributeError:
            continue
        if isinstance(field, AST):
            field.parent = node
            yield field
        elif isinstance(field, list):
            for child in field:
                if isinstance(child, AST):
                    child.parent = node
                    yield child
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/nodes/ast.py`

```
def ast_previous_siblings(node: AST) -> Iterator[AST]:
    """Return the previous siblings of this node, starting from the closest.

    Parameters:
        node: The AST node.

    Yields:
        The previous siblings.
    """
    for sibling in ast_children(node.parent):  # ty:ignore[unresolved-attribute]
        if sibling is not node:
            yield sibling
        else:
            return
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/nodes/ast.py`

```
def ast_next_siblings(node: AST) -> Iterator[AST]:
    """Return the next siblings of this node, starting from the closest.

    Parameters:
        node: The AST node.

    Yields:
        The next siblings.
    """
    siblings = ast_children(node.parent)  # ty:ignore[unresolved-attribute]
    for sibling in siblings:
        if sibling is node:
            break
    yield from siblings
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/nodes/ast.py`

```
def ast_siblings(node: AST) -> Iterator[AST]:
    """Return the siblings of this node.

    Parameters:
        node: The AST node.

    Yields:
        The siblings.
    """
    siblings = ast_children(node.parent)  # ty:ignore[unresolved-attribute]
    for sibling in siblings:
        if sibling is not node:
            yield sibling
        else:
            break
    yield from siblings
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/nodes/ast.py`

```
def ast_previous(node: AST) -> AST:
    """Return the previous sibling of this node.

    Parameters:
        node: The AST node.

    Raises:
        LastNodeError: When the node does not have previous siblings.

    Returns:
        The sibling.
    """
    try:
        *_, last = ast_previous_siblings(node)
    except ValueError:
        raise LastNodeError("there is no previous node") from None
    return last
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/nodes/ast.py`

```
def ast_next(node: AST) -> AST:
    """Return the next sibling of this node.

    Parameters:
        node: The AST node.

    Raises:
        LastNodeError: When the node does not have next siblings.

    Returns:
        The sibling.
    """
    try:
        return next(ast_next_siblings(node))
    except StopIteration:
        raise LastNodeError("there is no next node") from None
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/nodes/ast.py`

```
def ast_first_child(node: AST) -> AST:
    """Return the first child of this node.

    Parameters:
        node: The AST node.

    Raises:
        LastNodeError: When the node does not have children.

    Returns:
        The child.
    """
    try:
        return next(ast_children(node))
    except StopIteration as error:
        raise LastNodeError("there are no children node") from error
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/nodes/ast.py`

```
def ast_last_child(node: AST) -> AST:
    """Return the lasts child of this node.

    Parameters:
        node: The AST node.

    Raises:
        LastNodeError: When the node does not have children.

    Returns:
        The child.
    """
    try:
        *_, last = ast_children(node)
    except ValueError as error:
        raise LastNodeError("there are no children node") from error
    return last
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/nodes/docstrings.py`

```
def get_docstring(
    node: ast.AST,
    *,
    strict: bool = False,
) -> tuple[str | None, int | None, int | None]:
    """Extract a docstring.

    Parameters:
        node: The node to extract the docstring from.
        strict: Whether to skip searching the body (functions).

    Returns:
        A tuple with the value and line numbers of the docstring.
    """
    # TODO: Possible optimization using a type map.
    if isinstance(node, ast.Expr):
        doc = node.value
    elif not strict and node.body and isinstance(node.body, list) and isinstance(node.body[0], ast.Expr):  # ty:ignore[unresolved-attribute]
        doc = node.body[0].value  # ty:ignore[unresolved-attribute]
    else:
        return None, None, None
    if isinstance(doc, ast.Constant) and isinstance(doc.value, str):
        return doc.value, doc.lineno, doc.end_lineno
    return None, None, None
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/nodes/assignments.py`

```
def get_name(node: ast.AST) -> str:
    """Extract name from an assignment node.

    Parameters:
        node: The node to extract names from.

    Returns:
        A list of names.
    """
    return _node_name_map[type(node)](node)
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/nodes/assignments.py`

```
def get_names(node: ast.AST) -> list[str]:
    """Extract names from an assignment node.

    Parameters:
        node: The node to extract names from.

    Returns:
        A list of names.
    """
    return _node_names_map[type(node)](node)
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/nodes/assignments.py`

```
def get_instance_names(node: ast.AST) -> list[str]:
    """Extract names from an assignment node, only for instance attributes.

    Parameters:
        node: The node to extract names from.

    Returns:
        A list of names.
    """
    return [name.split(".", 1)[1] for name in get_names(node) if name.startswith("self.")]
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/nodes/exports.py`

```
def get__all__(node: ast.Assign | ast.AnnAssign | ast.AugAssign, parent: Module) -> list[str | ExprName]:
    """Get the values declared in `__all__`.

    Parameters:
        node: The assignment node.
        parent: The parent module.

    Returns:
        A set of names.
    """
    if node.value is None:
        return []
    return _extract(node.value, parent)
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/nodes/exports.py`

```
def safe_get__all__(
    node: ast.Assign | ast.AnnAssign | ast.AugAssign,
    parent: Module,
    log_level: LogLevel = LogLevel.debug,  # TODO: Set to error when we handle more things?
) -> list[str | ExprName]:
    """Safely (no exception) extract values in `__all__`.

    Parameters:
        node: The `__all__` assignment node.
        parent: The parent used to resolve the names.
        log_level: Log level to use to log a message.

    Returns:
        A list of strings or resolvable names.
    """
    try:
        return get__all__(node, parent)
    except Exception as error:  # noqa: BLE001
        message = f"Failed to extract `__all__` value: {get_value(node.value)}"
        with suppress(Exception):
            message += f" at {parent.relative_filepath}:{node.lineno}"
        if isinstance(error, KeyError):
            message += f": unsupported node {error}"
        else:
            message += f": {error}"
        getattr(logger, log_level.value)(message)
        return []
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/nodes/imports.py`

```
def relative_to_absolute(node: ast.ImportFrom, name: ast.alias, current_module: Module) -> str:
    """Convert a relative import path to an absolute one.

    Parameters:
        node: The "from ... import ..." AST node.
        name: The imported name.
        current_module: The module in which the import happens.

    Returns:
        The absolute import path.
    """
    level = node.level
    if (level > 0 and current_module.is_package) or current_module.is_subpackage:
        level -= 1
    while level > 0 and current_module.parent is not None:
        current_module = current_module.parent  # ty:ignore[invalid-assignment]
        level -= 1
    base = current_module.path + "." if node.level > 0 else ""
    node_module = node.module + "." if node.module else ""
    return base + node_module + name.name
```

## get_parameters

```
get_parameters(node: arguments) -> ParametersType
```

Source code in `packages/griffelib/src/griffe/_internal/agents/nodes/parameters.py`

```
def get_parameters(node: ast.arguments) -> ParametersType:
    parameters: ParametersType = []

    # TODO: Probably some optimizations to do here.
    args_kinds_defaults: Iterable = reversed(
        (
            *zip_longest(
                reversed(
                    (
                        *zip_longest(
                            node.posonlyargs,
                            [],
                            fillvalue=ParameterKind.positional_only,
                        ),
                        *zip_longest(node.args, [], fillvalue=ParameterKind.positional_or_keyword),
                    ),
                ),
                reversed(node.defaults),
                fillvalue=None,
            ),
        ),
    )
    arg: ast.arg
    kind: ParameterKind
    arg_default: ast.AST | None
    for (arg, kind), arg_default in args_kinds_defaults:
        parameters.append((arg.arg, arg.annotation, kind, arg_default))

    if node.vararg:
        parameters.append(
            (
                node.vararg.arg,
                node.vararg.annotation,
                ParameterKind.var_positional,
                "()",
            ),
        )

    # TODO: Probably some optimizations to do here.
    kwargs_defaults: Iterable = reversed(
        (
            *zip_longest(
                reversed(node.kwonlyargs),
                reversed(node.kw_defaults),
                fillvalue=None,
            ),
        ),
    )
    kwarg: ast.arg
    kwarg_default: ast.AST | None
    for kwarg, kwarg_default in kwargs_defaults:
        parameters.append(
            (kwarg.arg, kwarg.annotation, ParameterKind.keyword_only, kwarg_default),
        )

    if node.kwarg:
        parameters.append(
            (
                node.kwarg.arg,
                node.kwarg.annotation,
                ParameterKind.var_keyword,
                "{}",
            ),
        )

    return parameters
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

Source code in `packages/griffelib/src/griffe/_internal/agents/nodes/values.py`

```
def get_value(node: ast.AST | None) -> str | None:
    """Get the string representation of a node.

    Parameters:
        node: The node to represent.

    Returns:
        The representing code for the node.
    """
    if node is None:
        return None
    return unparse(node)
```

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

Source code in `packages/griffelib/src/griffe/_internal/agents/nodes/values.py`

```
def safe_get_value(node: ast.AST | None, filepath: str | Path | None = None) -> str | None:
    """Safely (no exception) get the string representation of a node.

    Parameters:
        node: The node to represent.
        filepath: An optional filepath from where the node comes.

    Returns:
        The representing code for the node.
    """
    try:
        return get_value(node)
    except Exception as error:  # noqa: BLE001
        message = f"Failed to represent node {node}"
        if filepath:
            message += f" at {filepath}:{node.lineno}"  # ty:ignore[unresolved-attribute]
        message += f": {error}"
        logger.exception(message)
        return None
```
