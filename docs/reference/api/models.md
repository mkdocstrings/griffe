# Models

Griffe stores information extracted from Python source code into data models.

These models represent trees of objects, starting with modules, and containing classes, functions, attributes, and type aliases.

Modules can have submodules, classes, functions, attributes, and type aliases. Classes can have nested classes, methods, attributes, and type aliases. Functions and attributes do not have any members.

Indirections to objects declared in other modules are represented as "aliases". An alias therefore represents an imported object, and behaves almost exactly like the object it points to: it is a light wrapper around the object, with special methods and properties that allow to access the target's data transparently.

The 6 models:

- [`Module`][griffelib.Module]
- [`Class`][griffelib.Class]
- [`Function`][griffelib.Function]
- [`Attribute`][griffelib.Attribute]
- [`Alias`][griffelib.Alias]
- [`TypeAlias`][griffelib.TypeAlias]

## **Model kind enumeration**

::: griffe.Kind

## **Model base classes**

::: griffe.GetMembersMixin

::: griffe.SetMembersMixin

::: griffe.DelMembersMixin

::: griffe.SerializationMixin

::: griffe.ObjectAliasMixin

::: griffe.Object

## **Type parameters**

::: griffe.TypeParameters

::: griffe.TypeParameter

::: griffe.TypeParameterKind

## **Git information**

::: griffe.KnownGitService

::: griffe.GitInfo
