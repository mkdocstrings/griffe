# Python code best practices

This document describes some best practices to adopt when using Griffe, or when writing Python code that will be analyzed by Griffe.

## Avoid member-submodule name shadowing

Sometimes we find that an `__init__` module defines or import an object which has the same name as a submodule of the parent package.

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

Why? Because the `package.subpackage.thing` submodule can eventually **shadow** the `package.subpackage.thing` attribute. Try this:

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

By simply importing from the `thing` submodule, the `thing` attribute of `subpackage` was overwritten by the `thing` submodule.

**Case 2**

In a particular case though, the situation improves: if we *import* `thing` in the init module instead of declaring it, then further imports will not overwrite anything:

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

From an API perspective, and given that both cases are very similar but differ in behavior, we recommend not doing that either.

If the goal is to isolate a single object into its own module, to then expose it in the parent module, then it would make sense that this object is the only object of the submodule to be exposed in the public API, and therefore the submodule could be marked as private by prefixing its name with an underscore:

```tree
package/
    __init__.py
    subpackage/
        __init__.py
        _thing.py
```

With this, there is no ambiguity as to what `subpackage.thing` points to.

For the reasons mentioned above, **Griffe does not support this kind of name shadowing.** During static analysis, the submodule will take precedence over the attribute. During dynamic analysis, Griffe's behavior is undefined.

## Avoid wildcard imports

Wildcard imports allow to import from a module all objects that do not start with an underscore `_`, or all objects that are listed in the module's `__all__` attribute, if it is defined.

```tree
package/
    __init__.py
    module.py
```

**Explicitly exposed to wildcard imports**

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

**Implicitly exposed to wildcard imports**

```python title="package/module.py"
class SomeClass: ...
class _SomeOtherClass: ...

def some_function(): ...
def _some_other_function(): ...

some_attribute = 0
_some_other_attribute = 1
```

In both cases, using a wildcard import will only import `SomeClass`, `some_function` and `some_attribute`, and not their "other" counterparts:

```python title="package/__init__.py"
from package.module import *
```

While we recommend declaring your public API with `__all__` lists, we do not recommend using wildcard imports.

In the implicit case, any other object imported in `module.py` will also be exported by the wildcard:

```python title="package/module.py"
from somewhere_else import this, that

class SomeClass: ...
class _SomeOtherClass: ...

def some_function(): ...
def _some_other_function(): ...

some_attribute = 0
_some_other_attribute = 1
```

Here, `this` and `that` will also be imported when we do `from package.module import *`. To prevent that, we would have to alias these names as such:

```python title="package/module.py"
from somewhere_else import this as _this, that as _that
```

...which is not ideal.

It gets even worse if `module.py` itself uses wildcard imports:

```python title="package/module.py"
from somewhere_else import *
```

Now using `from package.module import *` will import all objects that do not start with an underscore declared in the module, but also all the objects imported by it that do not start with an underscore, and also all the objects imported by the modules of the imported objects that do not start with an underscore, etc., recursively. Soon enough, we end up with dozens and dozens of objects exposed in `package`, while just a few of them are useful/meaningful to users.

Not only that, but it also increases the risk of creating cycles in imports. Python can handle some of these cycles, but static analysis tools such as Griffe can have a much harder time trying to resolve them.

In the explicit case, the situation improves, as only the objects listed in `__all__` will be exported to the modules that wildcard imports them. It effectively stops namespace pollution, but it does not remove the risk of cyclic imports, only decreases it.

We have seen code bases where parent modules wildcard imports from submodules, while these submodules also wildcard imports from the parent modules... Python somehow handles this, but it is *hell* to handle statically, and it is just too error prone (cyclic imports, name shadowing, namespaces become dependent on the order of imports, etc.).

For these reasons, we recommend not using wildcard imports. Instead, we recommend declaring your public API explicitly with `__all__`, and combining `__all__` lists together if needed:

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

Within your own code base, we recommend using canonical imports. By canonical, we mean importing objects from the module they are declared in, and not from another module that also imports them.

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

We especially recommend canonical imports over indirect imports from sibling modules passing through the parent:

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

Similarly, avoid exposing the API of external packages from your own package and recommending to use this indirect API.

```python title="package.py"
import numpy as np

__all__ = ["np"]  # Bad.

# Recommending users to do `from package import np`
# or `import package; package.np.etc`: bad.
```

Instead, let users import Numpy themselves, with `import numpy as np`. This will help other analysis tools, for example to detect that Numpy is used directly and should therefore be listed as a dependency. To quote [PEP 8](https://peps.python.org/pep-0008/#public-and-internal-interfaces):

> Imported names should always be considered an implementation detail. Other modules must not rely on indirect access to such imported names unless they are an explicitly documented part of the containing module’s API, such as os.path or a package’s `__init__` module that exposes functionality from submodules.

Emphasis on *exposes functionality from submodules*: PEP 8 does not state *exposing functionality from external packages*.

---

Using canonical imports provides several benefits:

- it can reduce the risk of cyclic imports
- it can increase performance by reducing hoops and importing less things (for example by not passing through a parent module that imports many things from siblings modules)
- it makes the code more readable and easier to refactor (less indirections)
- it makes the life of static analysis tools easier (less indirections)

We recommend using the [canonical-imports](https://github.com/15r10nk/canonical-imports) tool to automatically rewrite your imports as canonical.

Note however that we recommend using public imports (importing from the "public" locations rather than the canonical ones) when:

- importing from other packages
- importing from your own package within your tests suite

Apply these recommendations at your discretion: there may be other special cases where it might not make sense to use canonical imports.

## Make your compiled objects tell their true location

Python modules can be written in other languages (C, C++, Rust) and compiled. To extract information from such compiled modules, we have to use dynamic analysis, since sources are not available.

A practice that seem common in projects including compiled modules in their distributions is to make the compiled modules private (prefix their names with an underscore), and to expose their objects from a public module higher-up in the module layout, for example by wildcard importing everything from it.

```tree
package/
    __init__.py
    module.py
    _module.cpython-312-x86_64-linux-gnu.so
```

```python title="package/module.py"
from package._module import *
```

Since the objects are exposed in `package.module` instead of `package._module`, developers sometimes decide to make their compiled objects lie about their location, and make them say that they are defined in `package.module` instead of `package._module`. Example:

```pycon
>>> from package._module import MyObject
>>> MyObject.__module__
'package.module'
```

**Don't do that.**

When using dynamic analysis and inspecting modules, Griffe must distinguish objects that were declared in the inspected module from objects that were imported from other modules. The reason is that if we didn't care where objects come from, we could end up inspecting the same objects and their members again and again, since they can be imported in many places. This could lead to infinite loops, recursivity errors, and would generally decrease performance.

So, when Griffe inspects a member of the compiled `_module`, and this member lies and says it comes from `package.module`, Griffe thinks it was imported. It means that Griffe will record the object as an indirection, or alias, instead of visiting it in-place. But that is wrong: the object was actually declared in the module, and should not have been recorded as an indirection.

Fortunately, we were able to put some guard-rails in place, which means that the case above where the compiled and public modules have the same name, except for the leading underscore, is supported, and will not trigger errors. But other cases where modules have different names will trigger issues, and we have to special case them in Griffe itself, after issues are reported.

Please, use your framework features to correctly set the `__module__` attribute of your objects (functions, classes and their methods too) as their *canonical location*, not their public location or any other location in the final package.

For example with [PyO3](https://github.com/PyO3/pyo3):

```rust
// Your module is compiled and added as `_module` into `package`,
// but its objects are exposed in `package` or `package.module`.
// Set `module = "package._module"`, not `module = "package"` or `module = "package.module"`!
#[pyclass(name = "MyClass", module = "package._module")]
struct MyClass {
    // ...
}
```

Some modules of the standard library are guilty of this too, and do so inconsistently (`ast` and `_ast`, `io` and `_io`, depending on the Python version...). For this reason, when checking if an object was declared in the currently inspected module, Griffe ultimately considers that any qualified name is equal to itself with each component stripped from leading underscores:

```
a.b.c == _a.b.c
a.b.c == _a._b._c
a.__b._c == __a.b.c
...
```

When the qualified name of the object's parent module and the currently inspected module match like above, the object is inspected in-place (added as a member of the currently inspected module) instead of created as an alias.
