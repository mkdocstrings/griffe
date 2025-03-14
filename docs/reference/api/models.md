# Models

Griffe stores information extracted from Python source code into data models.

These models represent trees of objects, starting with modules, and containing classes, functions, attributes, and type aliases.

Modules can have submodules, classes, functions, attributes, and type aliases. Classes can have nested classes, methods, attributes, and type aliases. Functions and attributes do not have any members.

Indirections to objects declared in other modules are represented as "aliases". An alias therefore represents an imported object, and behaves almost exactly like the object it points to: it is a light wrapper around the object, with special methods and properties that allow to access the target's data transparently.

The 6 models:

- [`Module`][griffe.Module]
- [`Class`][griffe.Class]
- [`Function`][griffe.Function]
- [`Attribute`][griffe.Attribute]
- [`Alias`][griffe.Alias]
- [`TypeAlias`][griffe.TypeAlias]

## **Model kind enumeration**

::: griffe.Kind

## **Models base classes**

::: griffe.GetMembersMixin

::: griffe.SetMembersMixin

::: griffe.DelMembersMixin

::: griffe.SerializationMixin

::: griffe.ObjectAliasMixin

::: griffe.Object

## **Models type parameter**

::: griffe.TypeParameters

::: griffe.TypeParameter

::: griffe.TypeParameterKind
