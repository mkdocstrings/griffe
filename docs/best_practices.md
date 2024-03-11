# Best practices

This document describes some best practices to adopt when using Griffe,
or when writing Python code that will be analyzed by Griffe.

## Avoid member-submodule name shadowing

Sometimes we find that an `__init__` module defines or import an object
which has the same name as a submodule of the parent package.

**Case 1**

```tree
package/
    __init__.py
    subpackage/
        __init__.py
        thing.py
```

```python title="package/subpackage/__init__.py"
thing = "thing from init module"
```

```python title="package/subpackage/thing.py"
other_thing = "other thing from thing submodule"
```

We recommend not doing that.

Why? Because the `package.subpackage.thing` submodule
can eventually **shadow** the `package.subpackage.thing` attribute.
Try this:

```bash
# Replicate the file tree from above.
mkdir -p package/subpackage
echo 'thing = "thing from init module"' > package/subpackage/__init__.py
echo 'other_thing = "other thing from thing submodule"' > package/subpackage/thing.py
# Run a Python interpreter.
python
```

```pycon
>>> from package import subpackage
>>> subpackage.thing
'thing from init module'
>>> # OK, but...
>>> from package.subpackage.thing import other_thing
>>> subpackage.thing
<module 'package.subpackage.thing' from 'package/subpackage/thing.py'>
```

By simply importing from the `thing` submodule,
the `thing` attribute of `subpackage` was overwritten by the `thing` submodule.

**Case 2**

In a particular case though, the situation improves: if we *import* `thing`
in the init module instead of declaring it, then further imports will
not overwrite anything:

```python title="package/subpackage/__init__.py"
from package.subpackage.thing import thing
```

```python title="package/subpackage/thing.py"
thing = "thing from thing submodule"
```

```bash
# Update the modules.
echo 'from package.subpackage.thing import thing' > package/subpackage/__init__.py
echo 'thing = "thing from thing submodule"' > package/subpackage/thing.py
# Run a Python interpreter.
python
```

```pycon
>>> from package import subpackage
>>> subpackage.thing
'thing from thing'
>>> # OK
>>> from package.subpackage.thing import thing
>>> subpackage.thing
'thing from thing'
>>> # Still OK
```

From an API perspective, and given that both cases are very similar
but differ in behavior, we recommend not doing that either.

If the goal is to isolate a single object into its own module,
to then expose it in the parent module,
then it would make sense that this object is the only object
of the submodule to be exposed in the public API,
and therefore the submodule could be marked as private
by prefixing its name with an underscore:

```tree
package/
    __init__.py
    subpackage/
        __init__.py
        _thing.py
```

With this, there is no ambiguity as to what `subpackage.thing` points to.

For the reasons mentioned above,
**Griffe does not support this kind of name shadowing.**
During static analysis, the submodule will take precedence
over the attribute. During dynamic analysis, Griffe's behavior
is undefined.

## Avoid wildcard imports

Wildcard imports allow to import all public objects from a module.
Public objects can either be explicitly listed in the module's `__all__` list/tuple,
or implicitly marked as such by prefixing private objects with an underscore.

```tree
package/
    __init__.py
    module.py
```

**Explicitly public**

```python title="package/module.py"
__all__ = [
    "SomeClass",
    "some_function",
    "some_attribute",
]

class SomeClass: ...
class SomeOtherClass: ...

def some_function(): ...
def some_other_function(): ...

some_attribute = 0
some_other_attribute = 1
```

**Implicitly public**

```python title="package/module.py"
class SomeClass: ...
class _SomeOtherClass: ...

def some_function(): ...
def _some_other_function(): ...

some_attribute = 0
_some_other_attribute = 1
```

In both cases, using a wildcard import will only import
`SomeClass`, `some_function` and `some_attribute`, and
not their "other" counterparts:

```python title="package/__init__.py"
from package.module import *
```

While we recommend declaring your public API with `__all__` lists,
we do not recommend using wildcard imports.

In the implicit case, any other object imported in `module.py`
will also be exported by the wildcard:

```python title="package/module.py"
from somewhere_else import this, that

class SomeClass: ...
class _SomeOtherClass: ...

def some_function(): ...
def _some_other_function(): ...

some_attribute = 0
_some_other_attribute = 1
```

Here, `this` and `that` will also be imported when we do
`from package.module import *`. To prevent that, we would have
to alias these names as such:

```python title="package/module.py"
from somewhere_else import this as _this, that as _that
```

...which is not ideal.

It gets even worse if `module.py` itself uses wildcard imports:

```python title="package/module.py"
from somewhere_else import *
```

Now using `from package.module import *` will import all implicitly public objects
declared in the module, but also all the implicitly public objects imported by it,
and also all the implicitly public objects imported by the modules of the imported objects,
etc., recursively. Soon enough, we end up with dozens and dozens of objects exposed in
`package`, while just a few of them are useful/meaningful to users.

Not only that, but it also increases the risk of creating cycles in imports.
Python can handle some of these cycles, but static analysis tools such as Griffe
can have a much harder time trying to resolve them.

In the explicit case, the situation improves, as only the objects listed
in `__all__` will be exported to the modules that wildcard imports them.
It effectively stops namespace pollution, but it only decreases
the risk of cyclic imports.

We have seen code bases where parent modules wildcard imports from submodules,
while these submodules also wildcard imports from the parent modules...
Python somehow handles this, but it is *hell* to handle statically,
and it is just too error prone (cyclic imports, name shadowing,
namespaces become dependent on the order of imports, etc.).

For these reasons, we recommend not using wildcard imports.
Instead, we recommend declaring your public API explicitly with `__all__`,
and combining `__all__` lists together if needed:

```tree
package/
    __init__.py
    module.py
    other_module.py
```

Completely explicit:

```python title="package/__init__.py"
from package.module import only, needed, objects
from package.other_module import some, more

__all__ = [
    "only",
    "needed",
    "some",
    "function",
]

def function(): ...
```

Combining `__all__` lists:

```python title="package/__init__.py"
from package.module import only, needed, objects, __all__ as module_all
from package.other_module import some, more, __all__ as other_module_all

__all__ = [
    *module_all,
    *other_module_all,
    "function",
]

def function(): ...
```

Most Python linting tools allow to forbid the use of wildcard imports.

## Prefer canonical imports

Within your own code base, we recommend using canonical imports.
By canonical, we mean importing objects from the module
they are declared in, and not from another module that also imports them.

Given the following tree:

```tree
package/
    __init__.py
    module_a.py
    module_b.py
```

```python title="package/module_a.py"
from package.module_b import thing
```

```python title="package/module_b.py"
thing = True
```

Don't do that:

```python title="package/__init__.py"
from package.module_a import thing  # Indirect import, bad.
```

Instead, do this:

```python title="package/__init__.py"
from package.module_b import thing  # Canonical import, good.
```

---

We especially recommend canonical imports over indirect imports
from sibling modules passing through the parent:

```python title="package/__init__.py"
from package.module_a import thing  # Canonical import, good.
```

```python title="package/module_a.py"
thing = True
```

```python title="package/module_b.py"
from package import thing  # Indirect import passing through parent, bad.

# Do this instead:
from package.module_a import thing  # Canonical import, good.
```

---

Similarly, avoid exposing the API of external packages from your own package
and recommending to use this indirect API.

```python title="package.py"
import numpy as np

__all__ = ["np"]  # Bad.

# Recommending users to do `from package import np`
# or `import package; package.np.etc`: bad.
```

Instead, let users import Numpy themselves, with `import numpy as np`.
This will help other analysis tools, for example to detect
that Numpy is used directly and should therefore be listed as a dependency.

---

Using canonical imports provides several benefits:

- it can reduce the risk of cyclic imports
- it can increase performance by reducing hoops and importing less things
  (for example by not passing through a parent module that imports many things
  from siblings modules)
- it makes the code more readable and easier to refactor (less indirections)
- it makes the life of static analysis tools easier (less indirections)

We recommend using the [canonical-imports](https://github.com/15r10nk/canonical-imports) tool
to automatically rewrite your imports as canonical.

Note however that we recommend using public imports
(importing from the "public" locations rather than the canonical ones) when:

- importing from other packages
- importing from your own package within your tests suite

Apply these recommandations at your discretion:
there may be other special cases where it might not make sense
to use canonical imports.
