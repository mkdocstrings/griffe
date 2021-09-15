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

griffe = GriffeLoader()
fastapi = griffe.load_module("fastapi")
```

If you don't want to recurse in the submodules:

```python
fastapi = griffe.load_module("fastapi", recursive=False)
```

### Extensions

You can pass extensions to the loader to augment its capacities:

```python
from griffe.loader import GriffeLoader
from griffe.extensions import Extension, Extensions, When

# import extensions
from some.package import TheirExtension


# or define your own
class ClassStartsAtOddLineNumberExtension(Extension):
    when = When.visit_stops

    def visit_ClassDef(self, node) -> None:
        if node.lineno % 2 == 1:
            self.visitor.current.labels.add("starts at odd line number")


extensions = Extensions(TheirExtension, ClassStartsAtOddLineNumberExtension)
griffe = GriffeLoader(extensions=extensions)
fastapi = griffe.load_module("fastapi")
```

Extensions are subclasses of [`ast.NodeVisitor`][ast.NodeVisitor].
Griffe uses a node visitor as well, that we will call the *main visitor*.
The extensions are instantiated with a reference to this main visitor,
so they can benefit from its capacities (navigating the nodes, getting the current
class or module, etc.).

Each time a node is visited, the main visitor will make the extensions visit the node as well.
Implement the `visit_<NODE_TYPE>` methods to visit nodes of certain types,
and act on their properties.

!!! warning "Important note"
    Because the main visitor recursively walks the tree itself,
    calling extensions on each node,
    **you must not call the `.generic_visit(node)` method in your `.visit_*` methods!**
    Otherwise, nodes down the tree will be visited twice or more:
    once by the main visitor, and as many times more as your extension is called.
    Let the main visitor do the walking, and just take care of the current node,
    without handling its children (what the `generic_visit` does).

You can access the main visitor state and data through the `.visitor` attribute,
and the nodes instances are extended with additional attributes and properties:

```python
class MyExtension(Extension):
    def visit_FunctionDef(self, node) -> None:
        node.parent  # the parent node
        node.children  # the list of children nodes
        node.siblings  # all the siblings nodes, from top to bottom
        node.previous_siblings  # only the previous siblings, from closest to top
        node.next_siblings  # only the next siblings, from closest to bottom
        node.previous  # first previous sibling
        node.next  # first next sibling

        self.visitor  # the main visitor
        self.visitor.current  # the current data object
        self.visitor.current.kind  # the kind of object: module, class, function, data 
```

See the data classes ([Module][griffe.dataclasses.Module],
[Class][griffe.dataclasses.Class], [Function][griffe.dataclasses.Function]
and [Data][griffe.dataclasses.Data])
for a complete description of their methods and attributes.

Extensions are run at certain moments while walking the Abstract Syntax Tree (AST):

- before the visit starts: `When.visit_starts`.
  The current node has been grafted to its parent.
  If this node represents a data object, the object (`self.visitor.current`) **is not** yet instantiated.
- before the children visit starts: `When.children_visit_starts`.
  If this node represents a data object, the object (`self.visitor.current`) **is** now instantiated.
  Children **have not** yet been visited.
- after the children visit stops: `When.children_visit_stops`.
  Children **have** now been visited.
- after the visit stops: `When.visit_stops`

See [the `When` enumeration][griffe.extensions.When].

To tell the main visitor to run your extension at a certain time,
set its `when` attribute:

```python
class MyExtension(Extension):
    when = When.children_visit_stops
```

By default, it will run it when the visit for the node stops:
that's when all the data for this node and its children is loaded.
