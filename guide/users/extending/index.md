# Extending APIs

Griffe has an extension system that can be used to enhance or customize the data that Griffe collects. Extensions are written in Python.

## Using extensions

Extensions can be specified both on the command-line (in the terminal), and programmatically (in Python).

### On the command-line

On the command-line, you can specify extensions to use with the `-e`, `--extensions` option. This option accepts a single positional argument which can take two forms:

- a comma-separated list of extensions
- a JSON list of extensions

Extensions can accept options: the comma-separated list does not allow to specify options, while the JSON list does. See examples below.

With both forms, each extension refers to one of these three things:

- the name of a built-in extension's module, for example `dynamic_docstrings` (this is just an example, this built-in extension does not exist)
- the Python dotted-path to a module containing one or more extensions, or to an extension directly, for example `package.module` and `package.module.ThisExtension`
- the file path to a Python script, and an optional extension name, separated by a colon, for example `scripts/griffe_exts.py` and `scripts/griffe_exts.py:ThisExtension`

The specified extension modules can contain more than one extension: Griffe will pick up and load every extension declared or imported within the modules. If options are specified for a module that contains multiple extensions, the same options will be passed to all the extensions, so extension writers must make sure that all extensions within a single module accept the same options. If they don't, Griffe will abort with an error.

To specify options in the JSON form, use a dictionary instead of a string: the dictionary's only key is the extension identifier (built-in name, Python path, file path) and its value is a dictionary of options.

Some examples:

```
griffe dump griffe -e pydantic,scripts/exts.py:DynamicDocstrings,griffe_attrs
```

```
griffe check --search src griffe -e '[
  {"pydantic": {"schema": true}},
  {
    "scripts/exts.py:DynamicDocstrings": {
      "paths": ["mypkg.mymod.myobj"]
    }
  },
  "griffe_attrs"
]'
```

In the above two examples, `pydantic` would be a built-in extension, `scripts/exts.py:DynamicDocstrings` the file path plus name of a local extension, and `griffe_attrs` the name of a third-party package that exposes one or more extensions.

### Programmatically

Within Python code, extensions can be specified with the `extensions` parameter of the GriffeLoader class or load function.

The parameter accepts an instance of the Extensions class. Such an instance is created with the help of the load_extensions function, which itself accepts a list of strings, dictionaries, extension classes and extension instances.

Strings and dictionaries are used the same way as [on the command-line](#on-the-command-line). Extension instances are used as such, and extension classes are instantiated without any options.

Example:

```
import griffe

from mypackage.extensions import ThisExtension, ThisOtherExtension

extensions = griffe.load_extensions(
    {"pydantic": {"schema": true}},
    {"scripts/exts.py:DynamicDocstrings": {"paths": ["mypkg.mymod.myobj"]}},
    "griffe_attrs",
    ThisExtension(option="value"),
    ThisOtherExtension,
)

data = griffe.load("mypackage", extensions=extensions)
```

### In MkDocs

MkDocs and its mkdocstrings plugin can be configured to use Griffe extensions:

mkdocs.yml

```
plugins:
- mkdocstrings:
    handlers:
      python:
        options:
          extensions:
          - pydantic: {schema: true}
          - scripts/exts.py:DynamicDocstrings:
              paths: [mypkg.mymod.myobj]
          - griffe_attrs
```

The `extensions` key accepts a list that is passed to the load_extensions function. See [how to use extensions programmatically](#programmatically) to learn more.

## Writing extensions

In the next section we give a bit of context on how Griffe works, to show how extensions can integrate into the data collection process. Feel free to skip to the [Events and hooks](#events-and-hooks) section or the [Full example](#full-example) section if you'd prefer to see concrete examples first.

### How it works

To extract information from your Python sources, Griffe tries to build Abstract Syntax Trees by parsing the sources with ast utilities.

If the source code is not available (the modules are built-in or compiled), Griffe imports the modules and builds object trees instead.

Griffe then follows the [Visitor pattern](https://www.wikiwand.com/en/Visitor_pattern) to walk the tree and extract information. For ASTs, Griffe uses its Visitor agent and for object trees, it uses its Inspector agent.

Sometimes during the walk through the source or runtime objects, both the visitor and inspector agents will trigger events, called **analysis events**. These events can be hooked on by extensions to alter or enhance Griffe's behavior. Some hooks will be passed just the current node being visited, others will be passed both the node and an instance of an Object subclass, such as a Module, a Class, a Function, an Attribute, or a Type Alias. Extensions will therefore be able to modify these instances.

Once the Griffe tree for a given package has been fully constructed, Griffe will trigger a second set of events, called **load events**, by walking the tree again. **It is safer to use load events as they are triggered only once data is complete for a given package**, contrary to the analysis events which are triggered *while the Griffe tree is still being built*.

The following flow chart shows an example of an AST visit. The tree is simplified: actual trees have a lot more nodes like `if/elif/else` nodes, `try/except/else/finally` nodes, and many more.

```
flowchart TB
M(Module definition) --- C(Class definition) & F(Function definition)
C --- m(Function definition) & A(Variable assignment)
```

The following flow chart shows an example of an object tree inspection. The tree is simplified as well: many more types of objects are handled.

```
flowchart TB
M(Module) --- C(Class) & F(Function)
C --- m(Method) & A(Attribute)
```

For a more concrete example, let say that we visit (or inspect) an AST (or object tree) for a given module, and that this module contains a single class, which itself contains a single method:

- the agent (visitor or inspector) will walk through the tree by starting with the module node
- it will instantiate a Module, then walk through its members, continuing with the class node
- it will instantiate a Class, then walk through its members, continuing with the function node
- it will instantiate a Function
- then it will go back up and finish walking since there are no more nodes to walk through

Every time the agent enters a node, creates an object instance, or finishes handling members of an object, it will trigger an event.

The flow of events is drawn in the following flowchart:

```
flowchart TB
visit_mod{{enter module node}}
event_mod_node{{"<a href='/griffe/reference/griffe/extensions/#griffe.Extension.on_node'><b><code style='color: var(--md-accent-fg-color)'>on_node</code></b></a> event<br><a href='/griffe/reference/griffe/extensions/#griffe.Extension.on_module_node'><b><code style='color: var(--md-accent-fg-color)'>on_module_node</code></b></a> event"}}
create_mod{{create module instance}}
event_mod_instance{{"<a href='/griffe/reference/griffe/extensions/#griffe.Extension.on_instance'><b><code style='color: var(--md-accent-fg-color)'>on_instance</code></b></a> event<br><a href='/griffe/reference/griffe/extensions/#griffe.Extension.on_module_instance'><b><code style='color: var(--md-accent-fg-color)'>on_module_instance</code></b></a> event"}}
visit_mod_members{{visit module members}}
visit_cls{{enter class node}}
event_cls_node{{"<a href='/griffe/reference/griffe/extensions/#griffe.Extension.on_node'><b><code style='color: var(--md-accent-fg-color)'>on_node</code></b></a> event<br><a href='/griffe/reference/griffe/extensions/#griffe.Extension.on_class_node'><b><code style='color: var(--md-accent-fg-color)'>on_class_node</code></b></a> event"}}
create_cls{{create class instance}}
event_cls_instance{{"<a href='/griffe/reference/griffe/extensions/#griffe.Extension.on_instance'><b><code style='color: var(--md-accent-fg-color)'>on_instance</code></b></a> event<br><a href='/griffe/reference/griffe/extensions/#griffe.Extension.on_class_instance'><b><code style='color: var(--md-accent-fg-color)'>on_class_instance</code></b></a> event"}}
visit_cls_members{{visit class members}}
visit_func{{enter func node}}
event_func_node{{"<a href='/griffe/reference/griffe/extensions/#griffe.Extension.on_node'><b><code style='color: var(--md-accent-fg-color)'>on_node</code></b></a> event<br><a href='/griffe/reference/griffe/extensions/#griffe.Extension.on_function_node'><b><code style='color: var(--md-accent-fg-color)'>on_function_node</code></b></a> event"}}
create_func{{create function instance}}
event_func_instance{{"<a href='/griffe/reference/griffe/extensions/#griffe.Extension.on_instance'><b><code style='color: var(--md-accent-fg-color)'>on_instance</code></b></a> event<br><a href='/griffe/reference/griffe/extensions/#griffe.Extension.on_function_instance'><b><code style='color: var(--md-accent-fg-color)'>on_function_instance</code></b></a> event"}}
event_cls_members{{"<a href='/griffe/reference/griffe/extensions/#griffe.Extension.on_members'><b><code style='color: var(--md-accent-fg-color)'>on_members</code></b></a> event<br><a href='/griffe/reference/griffe/extensions/#griffe.Extension.on_class_members'><b><code style='color: var(--md-accent-fg-color)'>on_class_members</code></b></a> event"}}
event_mod_members{{"<a href='/griffe/reference/griffe/extensions/#griffe.Extension.on_members'><b><code style='color: var(--md-accent-fg-color)'>on_members</code></b></a> event<br><a href='/griffe/reference/griffe/extensions/#griffe.Extension.on_module_members'><b><code style='color: var(--md-accent-fg-color)'>on_module_members</code></b></a> event"}}

start{start} --> visit_mod
visit_mod --> event_mod_node
event_mod_node --> create_mod
create_mod --> event_mod_instance
event_mod_instance --> visit_mod_members
visit_mod_members --1--> visit_cls
visit_cls --> event_cls_node
event_cls_node --> create_cls
create_cls --> event_cls_instance
event_cls_instance --> visit_cls_members
visit_cls_members --1--> visit_func
visit_func --> event_func_node
event_func_node --> create_func
create_func --> event_func_instance
event_func_instance --> visit_cls_members
visit_cls_members --2--> event_cls_members
event_cls_members --> visit_mod_members
visit_mod_members --2--> event_mod_members
event_mod_members --> finish{finish}

class event_mod_node event
class event_mod_instance event
class event_cls_node event
class event_cls_instance event
class event_func_node event
class event_func_instance event
class event_cls_members event
class event_mod_members event
classDef event stroke:#3cc,stroke-width:2
```

Hopefully this flowchart gives you a pretty good idea of what happens when Griffe collects data from a Python module. The next section will explain in more details the different events that are triggered, and how to hook onto them in your extensions.

### Events and hooks

There are two kinds of events in Griffe: [**load events**](#load-events) and [**analysis events**](#analysis-events). Load events are scoped to the Griffe loader (triggered once a package is fully loaded). Analysis events are scoped to the visitor and inspector agents (triggered during static and dynamic analysis).

**Hooks** are methods that are called when a particular event is triggered. To target a specific event, the hook must be named after it. See [Extensions and hooks](#extensions-and-hooks).

#### Load events

**Load events** are triggered once the tree for a given package has been fully constructed.

There is 1 generic **load event**:

- on_object: The "on object" event is triggered on any kind of object (except for aliases and packages, so modules, classes, functions, attributes and type aliases), once the tree for the object's package has been fully constructed.

There are also specific **load events** for each object kind:

- on_module: The "on module" event is triggered on modules.
- on_class: The "on class" event is triggered on classes.
- on_function: The "on function" event is triggered on functions.
- on_attribute: The "on attribute" event is triggered on attributes.
- on_type_alias: The "on type alias" event is triggered on type aliases.
- on_alias: The "on alias" event is triggered on aliases (imported/inherited objects).
- on_package: The "on package" event is triggered on top-level modules (packages) only.

#### Analysis events

**Analysis events** are triggered while modules are being scanned (with static or dynamic analysis). Data is incomplete when these events are triggered, so we recommend only hooking onto these events if you know what you are doing. In doubt, prefer using **load events** above.

There are 3 generic **analysis events**:

- on_node: The "on node" events are triggered when the agent (visitor or inspector) starts handling a node in the tree (AST or object tree).
- on_instance: The "on instance" events are triggered when the agent just created an instance of Module, Class, Function, Attribute, or Type Alias, and added it as a member of its parent. The "on instance" event is **not** triggered when an Alias is created.
- on_members: The "on members" events are triggered when the agent just finished handling all the members of an object. Functions, attributes and type aliases do not have members, so there are no "on members" events for these kinds.

There are also specific **analysis events** for each object kind:

- on_module_node
- on_module_instance
- on_module_members
- on_class_node
- on_class_instance
- on_class_members
- on_function_node
- on_function_instance
- on_attribute_node
- on_attribute_instance
- on_type_alias_node
- on_type_alias_instance
- on_alias_instance

#### Extensions and hooks

**Extensions** are classes that inherit from Griffe's Extension base class and define some hooks as methods:

```
import griffe


class MyExtension(griffe.Extension):
    def on_object(
        self,
        *,
        obj: griffe.Object,
        loader: griffe.GriffeLoader,
        **kwargs,
    ) -> None:
        """Do something with `obj`."""
```

Hooks are always defined as methods of a class inheriting from Extension, never as standalone functions. IDEs should autocomplete the signature when you start typing `def` followed by a hook name.

Since hooks are declared in a class, feel free to also declare state variables (or any other variable) in the `__init__` method:

```
import ast
from griffe import Extension, Object, ObjectNode


class MyExtension(Extension):
    def __init__(self) -> None:
        super().__init__()
        self.state_thingy = "initial stuff"
        self.list_of_things = []

    def on_object(
        self,
        *,
        obj: griffe.Object,
        loader: griffe.GriffeLoader,
        **kwargs,
    ) -> None:
        """Do something with `obj`."""
```

### Static/dynamic support

Extensions can support both static and dynamic analysis of modules.

Objects have an `analysis` attribute whose value will be `"static"` if they were loaded using static analysis, or `"dynamic"` if they were loaded using dynamic analysis. If the value is `None`, it means the object was created manually (for example by another extension).

To support static analysis, dynamic analysis, or both in your load events, you can therefore check the value of the `analysis` attribute:

```
import griffe


class MyExtension(griffe.Extension):
    def on_object(self, *, obj: griffe.Object, **kwargs) -> None:
        """Do something with `obj`."""
        if obj.analysis == "static":
            ...  # Apply logic for static analysis.
        elif obj.analysis == "dynamic":
            ...  # Apply logic for dynamic analysis.
        else:
            ...  # Apply logic for manually built objects.
```

### Visiting trees

Extensions provide basic functionality to help you visit trees during analysis of the code:

- visit: call `self.visit(node)` to start visiting an abstract syntax tree.
- generic_visit: call `self.generic_visit(node)` to visit each subnode of a given node.
- inspect: call `self.inspect(node)` to start visiting an object tree. Nodes contain references to the runtime objects, see ObjectNode.
- generic_inspect: call `self.generic_inspect(node)` to visit each subnode of a given node.

Calling `self.visit(node)` or `self.inspect(node)` will do nothing unless you actually implement methods that handle specific types of nodes:

- for ASTs, methods must be named `visit_<node_type>` where `<node_type>` is replaced with the lowercase name of the node's class. For example, to allow visiting ClassDef nodes, you must implement the `visit_classdef` method:

  ```
  import ast
  from griffe import Extension


  class MyExtension(Extension):
      def visit_classdef(node: ast.ClassDef) -> None:
          # Do something with the node...
          ...
          # ...then visit the subnodes
          # (it only makes sense if you implement other methods
          # such as visit_functiondef or visit_assign for example).
          self.generic_visit(node)
  ```

  See the [list of existing AST classes](#ast-nodes) to learn what method you can implement.

- for object trees, methods must be named `inspect_<node_type>`, where `<node_type>` is replaced with the string value of the node's kind. The different kinds are listed in the ObjectKind enumeration. For example, to allow inspecting coroutine nodes, you must implement the `inspect_coroutine` method:

  ```
  from griffe import Extension, ObjectNode


  class MyExtension(Extension):
      def inspect_coroutine(node: ObjectNode) -> None:
          # Do something with the node...
          ...
          # ...then visit the subnodes if it makes sense.
          self.generic_inspect(node)
  ```

### Triggering other extensions

If your extension creates new objects, you might want to trigger the other enabled extensions on these object instances. To do this you can use agent.extensions.call:

```
import ast
import griffe


class MyExtension(griffe.Extension):
    # Example from within a load event:
    def on_package(self, *, pkg: griffe.Module, loader: griffe.GriffeLoader, **kwargs) -> None:
        # New object created for whatever reason.
        function = griffe.Function(...)

        # Trigger other extensions.
        loader.extensions.call("on_function", func=function, loader=loader)

    # Example from within an analysis event:
    def on_node(self, *, node: ast.AST | griffe.ObjectNode, agent: griffe.Visitor | griffe.Inspector, **kwargs) -> None:
        # New object created for whatever reason.
        function = griffe.Function(...)

        # Trigger other extensions.
        agent.extensions.call("on_function_instance", node=node, agent=agent, func=function, **kwargs)
```

### Extra data

All Griffe objects (modules, classes, functions, attributes, type aliases) can store additional (meta)data in their `extra` attribute. This attribute is a dictionary of dictionaries. The first layer is used as namespacing: each extension writes into its own namespace, or integrates with other projects by reading/writing in their namespaces, according to what they support and document.

```
import griffe

self_namespace = "my_extension"


class MyExtension(griffe.Extension):
    def on_object(self, obj: griffe.Object, **kwargs) -> None:
        obj.extra[self_namespace]["some_key"] = "some_value"
```

For example, [mkdocstrings-python](https://mkdocstrings.github.io/python) looks into the `mkdocstrings` namespace for a `template` key. Extensions can therefore provide a custom template value by writing into `extra["mkdocstrings"]["template"]`:

```
import griffe

self_namespace = "my_extension"
mkdocstrings_namespace = "mkdocstrings"


class MyExtension(griffe.Extension):
    def on_class(self, cls: griffe.Class, **kwargs) -> None:
        cls.extra[mkdocstrings_namespace]["template"] = "my_custom_template"
```

[Read more about mkdocstrings handler extensions.](https://mkdocstrings.github.io/usage/handlers/#handler-extensions)

### Options

Extensions can be made to support options. These options can then be passed from the [command-line](#on-the-command-line) using JSON, from Python directly, or from other tools like MkDocs, in `mkdocs.yml`.

```
import griffe


class MyExtension(griffe.Extension):
    def __init__(self, option1: str, option2: bool = False) -> None:
        super().__init__()
        self.option1 = option1
        self.option2 = option2

    def on_attribute(self, attr: griffe.Attribute, **kwargs) -> None:
        if self.option2:
            ...  # Do something.
```

### Logging

To better integrate with Griffe and other tools in the ecosystem (notably MkDocs), use Griffe loggers to log messages:

```
import griffe

logger = griffe.get_logger(__name__)


class MyExtension(griffe.Extension):
    def on_module(self, mod: griffe.Module, **kwargs) -> None:
        logger.info("Doing some work on module %s", mod.path)
```

### Full example

The following example shows how one could write a "dynamic docstrings" extension that dynamically imports objects that declare their docstrings dynamically, to improve support for such docstrings. The extension is configurable to run only on user-selected objects.

Package structure (or just write your extension in a local script):

```
📁 ./
├──  pyproject.toml
└── 📁 src/
    └── 📁 dynamic_docstrings/
        ├──  __init__.py
        └──  extension.py
```

./src/dynamic_docstrings/extension.py

```
import ast
import inspect
import griffe

logger = griffe.get_logger(__name__)


class DynamicDocstrings(griffe.Extension):
    def __init__(self, object_paths: list[str] | None = None) -> None:
        self.object_paths = object_paths

    def on_object(
        self,
        obj: griffe.Object,
        loader: griffe.GriffeLoader,
        **kwargs,
    ) -> None:
        if obj.analysis == "dynamic":
            return  # Skip runtime objects, their docstrings are already right.

        if self.object_paths and obj.path not in self.object_paths:
            return  # Skip objects that were not selected.

        # Import object to get its evaluated docstring.
        try:
            runtime_obj = griffe.dynamic_import(obj.path)
            docstring = runtime_obj.__doc__
        except ImportError:
            logger.debug(f"Could not get dynamic docstring for {obj.path}")
            return
        except AttributeError:
            logger.debug(f"Object {obj.path} does not have a __doc__ attribute")
            return

        # Update the object instance with the evaluated docstring.
        docstring = inspect.cleandoc(docstring)
        if obj.docstring:
            obj.docstring.value = docstring
        else:
            obj.docstring = griffe.Docstring(
                docstring,
                parent=obj,
                docstring_parser=loader.docstring_parser,
                docstring_options=loader.docstring_options,
            )
```

You can then expose this extension in the top-level module of your package:

./src/dynamic_docstrings/__init__.py

```
from dynamic_docstrings.extension import DynamicDocstrings

__all__ = ["DynamicDocstrings"]
```

This will allow users to load and use this extension by referring to it as `dynamic_docstrings` (your Python package name).

See [how to use extensions](#using-extensions) to learn more about how to load and use your new extension.

## AST nodes

> |     |
> | --- |
> |     |
>
> - Add
> - alias
> - And
> - AnnAssign
> - arg
> - arguments
> - Assert
> - Assign
> - AsyncFor
> - AsyncFunctionDef
> - AsyncWith
> - Attribute
> - AugAssign
> - Await
> - BinOp
> - BitAnd
> - BitOr
> - BitXor
> - BoolOp
> - Break
> - `Bytes`[1](#fn:1)
> - Call
> - ClassDef
> - Compare
> - comprehension
> - Constant
> - Continue
> - Del
> - Delete
> - Dict
>
> |
>
> - DictComp
> - Div
> - `Ellipsis`[1](#fn:1)
> - Eq
> - ExceptHandler
> - Expr
> - `Expression`[1](#fn:1)
> - `ExtSlice`[2](#fn:2)
> - FloorDiv
> - For
> - FormattedValue
> - FunctionDef
> - GeneratorExp
> - Global
> - Gt
> - GtE
> - If
> - IfExp
> - Import
> - ImportFrom
> - In
> - `Index`[2](#fn:2)
> - `Interactive`[3](#fn:3)
> - Invert
> - Is
> - IsNot
> - JoinedStr
> - keyword
> - Lambda
> - List
>
> |
>
> - ListComp
> - Load
> - LShift
> - Lt
> - LtE
> - Match
> - MatchAs
> - match_case
> - MatchClass
> - MatchMapping
> - MatchOr
> - MatchSequence
> - MatchSingleton
> - MatchStar
> - MatchValue
> - MatMult
> - Mod
> - `Module`[3](#fn:3)
> - Mult
> - Name
> - `NameConstant`[1](#fn:1)
> - NamedExpr
> - Nonlocal
> - Not
> - NotEq
> - NotIn
> - `Num`[1](#fn:1)
> - Or
> - ParamSpec
> - Pass
>
> |
>
> - `pattern`[3](#fn:3)
> - Pow
> - `Print`[4](#fn:4)
> - Raise
> - Return
> - RShift
> - Set
> - SetComp
> - Slice
> - Starred
> - Store
> - `Str`[1](#fn:1)
> - Sub
> - Subscript
> - Try
> - `TryExcept`[5](#fn:5)
> - `TryFinally`[6](#fn:6)
> - Tuple
> - TypeAlias
> - TypeVar
> - TypeVarTuple
> - UAdd
> - UnaryOp
> - USub
> - While
> - With
> - withitem
> - Yield
> - YieldFrom

## Next steps

Extensions are a powerful mechanism to customize or enhance the data loaded by Griffe. But sometimes, all you need to do to improve the data is to make Griffe happy by following a few conventions. We therefore invite you to read our recommendations on [public APIs](../recommendations/public-apis/), [Python code best practices](../recommendations/python-code/) and [docstrings](../recommendations/docstrings/).

______________________________________________________________________

1. Deprecated since Python 3.8. [↩](#fnref:1 "Jump back to footnote 1 in the text")[↩](#fnref2:1 "Jump back to footnote 1 in the text")[↩](#fnref3:1 "Jump back to footnote 1 in the text")[↩](#fnref4:1 "Jump back to footnote 1 in the text")[↩](#fnref5:1 "Jump back to footnote 1 in the text")[↩](#fnref6:1 "Jump back to footnote 1 in the text")
1. Deprecated since Python 3.9. [↩](#fnref:2 "Jump back to footnote 2 in the text")[↩](#fnref2:2 "Jump back to footnote 2 in the text")
1. Not documented. [↩](#fnref:3 "Jump back to footnote 3 in the text")[↩](#fnref2:3 "Jump back to footnote 3 in the text")[↩](#fnref3:3 "Jump back to footnote 3 in the text")
1. `print` became a builtin (instead of a keyword) in Python 3. [↩](#fnref:4 "Jump back to footnote 4 in the text")
1. Now `ExceptHandler`, in the `handlers` attribute of `Try` nodes. [↩](#fnref:5 "Jump back to footnote 5 in the text")
1. Now a list of expressions in the `finalbody` attribute of `Try` nodes. [↩](#fnref:6 "Jump back to footnote 6 in the text")
