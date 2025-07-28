# Supporting custom decorators

Griffe aims to support the Python language itself, as well as its standard library. It means that built-in objects and objects from the standard library that can be used or are often used as decorators, should be supported natively or through official extensions, for example `@property`, `@functools.cache`, `@warnings.deprecated`, etc.

Custom decorators however (the ones you define in your code-base) won't be supported by default, at least statically (dynamic analysis might be able to support them), because Griffe doesn't try to infer anything more than the obvious. Griffe is not a type-checker and so doesn't have the same inference abilities.

Therefore, to support your own decorators (at least statically), you have to write Griffe extensions. Don't worry, extensions that support custom decorators are generally super easy to write.

---

Lets assume we have a decorator whose path is `my_package.utils.enhance`. It is used throughout our code base like so:

```python
from my_package.utils import enhance

@enhance
def my_function() -> ...:
    ...
```

Start by creating an extensions module (a simple Python file) somewhere in your repository, if you don't already have one. Within it, create an extension class:

```python
import griffe


class MyDecorator(griffe.Extension):
    """An extension to suport my decorator."""
```

Now we can declare the [`on_instance`][griffe.Extension.on_instance] hook, which receives any kind of Griffe object ([`Module`][griffe.Module], [`Class`][griffe.Class], [`Function`][griffe.Function], [`Attribute`][griffe.Attribute], [`TypeAlias`][griffe.TypeAlias]), or we could use a kind-specific hook such as [`on_module_instance`][griffe.Extension.on_module_instance], [`on_class_instance`][griffe.Extension.on_class_instance], [`on_function_instance`][griffe.Extension.on_function_instance], [`on_attribute_instance`][griffe.Extension.on_attribute_instance] and [`on_type_alias_instance`][griffe.Extension.on_type_alias_instance]. For example, if you know your decorator is only ever used on class declarations, it would make sense to use `on_class_instance`.

For the example, lets use the `on_function_instance` hook, which receives `Function` instances.

```python hl_lines="7-8"
import griffe


class MyDecorator(griffe.Extension):
    """An extension to suport my decorator."""

    def on_function_instance(self, *, func: griffe.Function, **kwargs) -> None:
        ...
```

In this hook, we check if our function is decorated with our custom decorator:

```python hl_lines="8-10"
import griffe


class MyDecorator(griffe.Extension):
    """An extension to suport my decorator."""

    def on_function_instance(self, *, func: griffe.Function, **kwargs) -> None:
        for decorator in func.decorators:
            if decorator.callable_path == "my_package.utils.enhance":
                ...  # Update the function attributes.
```

Now all that is left to do is to actually write the code that updates the function according to what the decorator is doing. We could update the function's docstring, or its return type, or its parameters: it all depends on your decorator and what it does to the objects it decorates. Check out the [API reference for function objects][griffe.Function] to see what data this object stores.
