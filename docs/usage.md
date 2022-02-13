# Usage

## On the command line

Pass the names of packages to the `griffe` command:

```console
$ griffe httpx fastapi
[
  {
    "name": "httpx",
    ...
  }
]
```

It will output a JSON-serialized version of the packages signatures.

Try it out on Griffe itself:

```console
$ griffe griffe
[
  {
    "name": "griffe",
    ...
  }
]
```

See [the full Griffe JSON dump](griffe.json). 

By default, Griffe will search in `sys.path`, so if you installed it through *pipx*,
there are few chances it will find your packages.
To explicitely specify search paths, use the `-s, --search <PATH>` option.
You can use it multiple times.
You can also add the search paths to the `PYTHONPATH` environment variable.
If Griffe can't find the packages, it will fail with a `ModuleNotFoundError`.

## With Python

Create a loader to load modules data, recursively:

```python
from griffe.loader import GriffeLoader

loader = GriffeLoader()
griffe = loader.load_module("griffe")
```

If you don't want to recurse in the submodules:

```python
griffe = loader.load_module("griffe", submodules=False)
```

The [`load_module`][griffe.loader.GriffeLoader.load_module] method
returns a [`Module`][griffe.dataclasses.Module] instance.
There are several ways to access members of an object:

- through its `members` attribute, which is a dictionary,
  with the usual `keys()`, `values()` and `items()` methods.
- thanks to its `__getitem__` method. For example `griffe["dataclasses"]`
  returns the `Module` instance representing Griffe's `dataclasses` module.
  Since this module also has members, you can chain calls: `griffe["dataclasses"]["Module"]`.
  Conveniently, you can chain the names with dots in a single call: `griffe["dataclasses.Module"]`.
  You can even pass a tuple instead of a string: `griffe[("dataclasses", "Module")]`.
- through the [`modules`][griffe.dataclasses.Object.modules],
  [`classes`][griffe.dataclasses.Object.classes],
  [`functions`][griffe.dataclasses.Object.functions] and
  [`attributes`][griffe.dataclasses.Object.attributes] properties,
  which take care of filtering members based on their kind, and return dictionaries.

Most of the time, you will only use classes from the [`griffe.dataclasses`][griffe.dataclasses]
and [`griffe.docstrings.dataclasses`][griffe.docstrings.dataclasses] modules.

### Extensions

You can pass extensions to the loader to augment its capacities:

```python
from griffe.loader import GriffeLoader
from griffe.extensions import VisitorExtension, Extensions, When

# import extensions
from some.package import TheirExtension


# or define your own
class ClassStartsAtOddLineNumberExtension(VisitorExtension):
    when = When.after_all

    def visit_classdef(self, node) -> None:
        if node.lineno % 2 == 1:
            self.visitor.current.labels.add("starts at odd line number")


extensions = Extensions(TheirExtension, ClassStartsAtOddLineNumberExtension)
griffe = GriffeLoader(extensions=extensions)
fastapi = griffe.load_module("fastapi")
```

Extensions are subclasses of a custom version of [`ast.NodeVisitor`][ast.NodeVisitor].
Griffe uses a node visitor as well, that we will call the *main visitor*.
The extensions are instantiated with a reference to this main visitor,
so they can benefit from its capacities (navigating the nodes, getting the current
class or module, etc.).

Each time a node is visited, the main visitor will make the extensions visit the node as well.
Implement the `visit_<NODE_TYPE_LOWER>` methods to visit nodes of certain types,
and act on their properties. See the [full list of AST nodes](#ast-nodes).

!!! warning "Important note"
    Because the main visitor recursively walks the tree itself,
    calling extensions on each node,
    **you must not visit child nodes in your `.visit_*` methods!**
    Otherwise, nodes down the tree will be visited twice or more:
    once by the main visitor, and as many times more as your extension is called.
    Let the main visitor do the walking, and just take care of the current node,
    without handling its children.

You can access the main visitor state and data through the `.visitor` attribute,
and the nodes instances are extended with additional attributes and properties:

```python
class MyExtension(Extension):
    def visit_functiondef(self, node) -> None:
        node.parent  # the parent node
        node.children  # the list of children nodes
        node.siblings  # all the siblings nodes, from top to bottom
        node.previous_siblings  # only the previous siblings, from closest to top
        node.next_siblings  # only the next siblings, from closest to bottom
        node.previous  # first previous sibling
        node.next  # first next sibling

        self.visitor  # the main visitor
        self.visitor.current  # the current data object
        self.visitor.current.kind  # the kind of object: module, class, function, attribute 
```

See the data classes ([`Module`][griffe.dataclasses.Module],
[`Class`][griffe.dataclasses.Class], [`Function`][griffe.dataclasses.Function]
and [`Attribute`][griffe.dataclasses.Attribute])
for a complete description of their methods and attributes.

Extensions are run at certain moments while walking the Abstract Syntax Tree (AST):

- before the visit/inspection: `When.before_all`.
  The current node has been grafted to its parent.
  If this node represents a data object, the object (`self.visitor.current`/`self.inspector.current`) **is not** yet instantiated.
- before the children visit/inspection: `When.before_children`.
  If this node represents a data object, the object (`self.visitor.current`/`self.inspector.current`) **is** now instantiated.
  Children **have not** yet been visited/inspected.
- after the children visit/inspection: `When.after_children`.
  Children **have** now been visited/inspected.
- after the visit/inspection: `When.after_all`

See [the `When` enumeration][griffe.agents.extensions.When].

To tell the main visitor to run your extension at a certain time,
set its `when` attribute:

```python
class MyExtension(Extension):
    when = When.after_children
```

By default, it will run the extension after the visit/inspection of the node:
that's when the full data for this node and its children is loaded.

## Using Griffe as a docstring-parsing library

You can use Griffe to parse arbitrary docstrings.
You don't have to load anything through the Griffe loader.
You need to import the [`parse`][griffe.docstrings.parsers.parse] function,
the [`Parser`][griffe.docstrings.parsers.Parser] enumeration,
and the [`Docstring`][griffe.dataclasses.Docstring] class.
Then you can build a `Docstring` instance and call `parse` on it,
choosing the parsing-style to use:

```python
from griffe.dataclasses import Docstring
from griffe.docstrings.parsers import Parser, parse

text = "Hello I'm a docstring!"
docstring = Docstring(text, lineno=1)
parsed = parse(docstring, Parser.google)
```

If you want to take advantage of the parsers ability to fetch
annotations from the object from which the docstring originates,
you can manually create the parent objects and link them to the docstring:

```python
from griffe.dataclasses import Docstring, Function, Parameters, Parameter, ParameterKind
from griffe.docstrings.parsers import Parser, parse

function = Function(
    "func",
    parameters=Parameters(
        Parameter("param1", annotation="str", kind=ParameterKind.positional_or_keyword),
        Parameter("param2", annotation="int", kind=ParameterKind.keyword_only),
    )
)
text = """
Hello I'm a docstring!

Parameters:
    param1: Description.
    param2: Description.
"""
docstring = Docstring(text, lineno=1, parent=function)
parsed = parse(docstring, Parser.google)
```

With this the parser will fetch the `str` and `int` annotations
from the parent function's parameters.

## AST nodes

> <table style="border: none; background-color: unset;"><tbody><tr><td>
>
> - [`Add`][ast.Add]
> - [`alias`][ast.alias]
> - [`And`][ast.And]
> - [`AnnAssign`][ast.AnnAssign]
> - [`arg`][ast.arg]
> - [`arguments`][ast.arguments]
> - [`Assert`][ast.Assert]
> - [`Assign`][ast.Assign]
> - [`AsyncFor`][ast.AsyncFor]
> - [`AsyncFunctionDef`][ast.AsyncFunctionDef]
> - [`AsyncWith`][ast.AsyncWith]
> - [`Attribute`][ast.Attribute]
> - [`AugAssign`][ast.AugAssign]
> - [`Await`][ast.Await]
> - [`BinOp`][ast.BinOp]
> - [`BitAnd`][ast.BitAnd]
> - [`BitOr`][ast.BitOr]
> - [`BitXor`][ast.BitXor]
> - [`BoolOp`][ast.BoolOp]
> - [`Break`][ast.Break]
> - `Bytes`[^1]
> - [`Call`][ast.Call]
> - [`ClassDef`][ast.ClassDef]
> - [`Compare`][ast.Compare]
> - [`comprehension`][ast.comprehension]
> - [`Constant`][ast.Constant]
> - [`Continue`][ast.Continue]
> - [`Del`][ast.Del]
> - [`Delete`][ast.Delete]
>
> </td><td>
>
> - [`Dict`][ast.Dict]
> - [`DictComp`][ast.DictComp]
> - [`Div`][ast.Div]
> - `Ellipsis`[^1]
> - [`Eq`][ast.Eq]
> - [`ExceptHandler`][ast.ExceptHandler]
> - [`Expr`][ast.Expr]
> - `Expression`[^1]
> - `ExtSlice`[^2]
> - [`FloorDiv`][ast.FloorDiv]
> - [`For`][ast.For]
> - [`FormattedValue`][ast.FormattedValue]
> - [`FunctionDef`][ast.FunctionDef]
> - [`GeneratorExp`][ast.GeneratorExp]
> - [`Global`][ast.Global]
> - [`Gt`][ast.Gt]
> - [`GtE`][ast.GtE]
> - [`If`][ast.If]
> - [`IfExp`][ast.IfExp]
> - [`Import`][ast.Import]
> - [`ImportFrom`][ast.ImportFrom]
> - [`In`][ast.In]
> - `Index`[^2]
> - `Interactive`[^3]
> - [`Invert`][ast.Invert]
> - [`Is`][ast.Is]
> - [`IsNot`][ast.IsNot]
> - [`JoinedStr`][ast.JoinedStr]
> - [`keyword`][ast.keyword]
>
> </td><td>
>
> - [`Lambda`][ast.Lambda]
> - [`List`][ast.List]
> - [`ListComp`][ast.ListComp]
> - [`Load`][ast.Load]
> - [`LShift`][ast.LShift]
> - [`Lt`][ast.Lt]
> - [`LtE`][ast.LtE]
> - [`Match`][ast.Match]
> - [`MatchAs`][ast.MatchAs]
> - [`match_case`][ast.match_case]
> - [`MatchClass`][ast.MatchClass]
> - [`MatchMapping`][ast.MatchMapping]
> - [`MatchOr`][ast.MatchOr]
> - [`MatchSequence`][ast.MatchSequence]
> - [`MatchSingleton`][ast.MatchSingleton]
> - [`MatchStar`][ast.MatchStar]
> - [`MatchValue`][ast.MatchValue]
> - [`MatMult`][ast.MatMult]
> - [`Mod`][ast.Mod]
> - `Module`[^3]
> - [`Mult`][ast.Mult]
> - [`Name`][ast.Name]
> - `NameConstant`[^1]
> - [`NamedExpr`][ast.NamedExpr]
> - [`Nonlocal`][ast.Nonlocal]
> - [`Not`][ast.Not]
> - [`NotEq`][ast.NotEq]
> - [`NotIn`][ast.NotIn]
> - `Num`[^1]
>
> </td><td>
>
> - [`Or`][ast.Or]
> - [`Pass`][ast.Pass]
> - `pattern`[^3]
> - [`Pow`][ast.Pow]
> - `Print`[^4]
> - [`Raise`][ast.Raise]
> - [`Return`][ast.Return]
> - [`RShift`][ast.RShift]
> - [`Set`][ast.Set]
> - [`SetComp`][ast.SetComp]
> - [`Slice`][ast.Slice]
> - [`Starred`][ast.Starred]
> - [`Store`][ast.Store]
> - `Str`[^1]
> - [`Sub`][ast.Sub]
> - [`Subscript`][ast.Subscript]
> - [`Try`][ast.Try]
> - `TryExcept`[^5]
> - `TryFinally`[^6]
> - [`Tuple`][ast.Tuple]
> - [`UAdd`][ast.UAdd]
> - [`UnaryOp`][ast.UnaryOp]
> - [`USub`][ast.USub]
> - [`While`][ast.While]
> - [`With`][ast.With]
> - [`withitem`][ast.withitem]
> - [`Yield`][ast.Yield]
> - [`YieldFrom`][ast.YieldFrom]
> 
> </td></tr></tbody></table>

[^1]: Deprecated since Python 3.8.
[^2]: Deprecated since Python 3.9.
[^3]: Not documented.
[^4]: `print` became a builtin (instead of a keyword) in Python 3.
[^5]: Now `ExceptHandler`, in the `handlers` attribute of `Try` nodes.
[^6]: Now a list of expressions in the `finalbody` attribute of `Try` nodes.
