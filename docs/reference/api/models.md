# Models

Griffe stores information extracted from Python source code into data models.

These models represent trees of objects, starting with modules, and containing classes, functions, and attributes.

Modules can have submodules, classes, functions and attributes. Classes can have nested classes, methods and attributes. Functions and attributes do not have any members.

Indirections to objects declared in other modules are represented as "aliases". An alias therefore represents an imported object, and behaves almost exactly like the object it points to: it is a light wrapper around the object, with special methods and properties that allow to access the target's data transparently.

The 5 models:

- [`Module`][griffe.Module]
- [`Class`][griffe.Class]
- [`Function`][griffe.Function]
- [`Attribute`][griffe.Attribute]
- [`Alias`][griffe.Alias]

## **Model kind enumeration**

::: griffe.Kind

## **Models base classes**

::: griffe.GetMembersMixin
        members: false

::: griffe.SetMembersMixin
        members: false

::: griffe.DelMembersMixin
        members: false

::: griffe.SerializationMixin
        members: false

::: griffe.ObjectAliasMixin
        members: false
        inherited_members: false

::: griffe.Object
