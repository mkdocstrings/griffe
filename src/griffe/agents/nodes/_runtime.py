"""This module contains utilities for extracting information from nodes."""

from __future__ import annotations

import inspect
from functools import cached_property
from inspect import getmodule
from typing import Any, ClassVar, Sequence

from griffe.enumerations import ObjectKind
from griffe.logger import get_logger

logger = get_logger(__name__)

_cyclic_relationships = {
    ("os", "nt"),
    ("os", "posix"),
    ("numpy.core._multiarray_umath", "numpy.core.multiarray"),
    ("pymmcore._pymmcore_swig", "pymmcore.pymmcore_swig"),
}


class ObjectNode:
    """Helper class to represent an object tree.

    It's not really a tree but more a backward-linked list:
    each node has a reference to its parent, but not to its child (for simplicity purposes and to avoid bugs).

    Each node stores an object, its name, and a reference to its parent node.
    """

    # low level stuff known to cause issues when resolving aliases
    exclude_specials: ClassVar[set[str]] = {"__builtins__", "__loader__", "__spec__"}

    def __init__(self, obj: Any, name: str, parent: ObjectNode | None = None) -> None:
        """Initialize the object.

        Parameters:
            obj: A Python object.
            name: The object's name.
            parent: The object's parent node.
        """
        try:
            obj = inspect.unwrap(obj)
        except Exception as error:  # noqa: BLE001
            # inspect.unwrap at some point runs hasattr(obj, "__wrapped__"),
            # which triggers the __getattr__ method of the object, which in
            # turn can raise various exceptions. Probably not just __getattr__.
            # See https://github.com/pawamoy/pytkdocs/issues/45
            logger.debug(f"Could not unwrap {name}: {error!r}")

        self.obj: Any = obj
        """The actual Python object."""
        self.name: str = name
        """The Python object's name."""
        self.parent: ObjectNode | None = parent
        """The parent node."""

    def __repr__(self) -> str:
        return f"ObjectNode(name={self.name!r})"

    @property
    def path(self) -> str:
        """The object's (Python) path."""
        if self.parent is None:
            return self.name
        return f"{self.parent.path}.{self.name}"

    @property
    def module(self) -> ObjectNode:
        """The object's module."""
        if self.is_module:
            return self
        if self.parent is not None:
            return self.parent.module
        raise ValueError(f"Object node {self.path} does not have a parent module")

    @property
    def kind(self) -> ObjectKind:
        """The kind of this node."""
        if self.is_module:
            return ObjectKind.MODULE
        if self.is_class:
            return ObjectKind.CLASS
        if self.is_staticmethod:
            return ObjectKind.STATICMETHOD
        if self.is_classmethod:
            return ObjectKind.CLASSMETHOD
        if self.is_method:
            return ObjectKind.METHOD
        if self.is_builtin_method:
            return ObjectKind.BUILTIN_METHOD
        if self.is_coroutine:
            return ObjectKind.COROUTINE
        if self.is_function:
            return ObjectKind.FUNCTION
        if self.is_builtin_function:
            return ObjectKind.BUILTIN_FUNCTION
        if self.is_cached_property:
            return ObjectKind.CACHED_PROPERTY
        if self.is_property:
            return ObjectKind.PROPERTY
        if self.is_method_descriptor:
            return ObjectKind.METHOD_DESCRIPTOR
        return ObjectKind.ATTRIBUTE

    @cached_property
    def children(self) -> Sequence[ObjectNode]:
        """The children of this node."""
        children = []
        for name, member in inspect.getmembers(self.obj):
            if self._pick_member(name, member):
                children.append(ObjectNode(member, name, parent=self))
        return children

    @cached_property
    def is_module(self) -> bool:
        """Whether this node's object is a module."""
        return inspect.ismodule(self.obj)

    @cached_property
    def is_class(self) -> bool:
        """Whether this node's object is a class."""
        return inspect.isclass(self.obj)

    @cached_property
    def is_function(self) -> bool:
        """Whether this node's object is a function."""
        return inspect.isfunction(self.obj)

    @cached_property
    def is_builtin_function(self) -> bool:
        """Whether this node's object is a builtin function."""
        return inspect.isbuiltin(self.obj)

    @cached_property
    def is_coroutine(self) -> bool:
        """Whether this node's object is a coroutine."""
        return inspect.iscoroutinefunction(self.obj)

    @cached_property
    def is_property(self) -> bool:
        """Whether this node's object is a property."""
        return isinstance(self.obj, property) or self.is_cached_property

    @cached_property
    def is_cached_property(self) -> bool:
        """Whether this node's object is a cached property."""
        return isinstance(self.obj, cached_property)

    @cached_property
    def parent_is_class(self) -> bool:
        """Whether the object of this node's parent is a class."""
        return bool(self.parent and self.parent.is_class)

    @cached_property
    def is_method(self) -> bool:
        """Whether this node's object is a method."""
        function_type = type(lambda: None)
        return self.parent_is_class and isinstance(self.obj, function_type)

    @cached_property
    def is_method_descriptor(self) -> bool:
        """Whether this node's object is a method descriptor.

        Built-in methods (e.g. those implemented in C/Rust) are often
        method descriptors, rather than normal methods.
        """
        return inspect.ismethoddescriptor(self.obj)

    @cached_property
    def is_builtin_method(self) -> bool:
        """Whether this node's object is a builtin method."""
        return self.is_builtin_function and self.parent_is_class

    @cached_property
    def is_staticmethod(self) -> bool:
        """Whether this node's object is a staticmethod."""
        if self.parent is None:
            return False
        try:
            self_from_parent = self.parent.obj.__dict__.get(self.name, None)
        except AttributeError:
            return False
        return self.parent_is_class and isinstance(self_from_parent, staticmethod)

    @cached_property
    def is_classmethod(self) -> bool:
        """Whether this node's object is a classmethod."""
        if self.parent is None:
            return False
        try:
            self_from_parent = self.parent.obj.__dict__.get(self.name, None)
        except AttributeError:
            return False
        return self.parent_is_class and isinstance(self_from_parent, classmethod)

    @cached_property
    def _ids(self) -> set[int]:
        if self.parent is None:
            return {id(self.obj)}
        return {id(self.obj)} | self.parent._ids

    def _pick_member(self, name: str, member: Any) -> bool:
        return (
            name not in self.exclude_specials
            and member is not type
            and member is not object
            and id(member) not in self._ids
            and name in vars(self.obj)
        )

    @cached_property
    def alias_target_path(self) -> str | None:
        """Alias target path of this node, if the node should be an alias."""
        # the whole point of the following logic is to deal with these cases:
        # - parent object has a module member
        # - if this module is not a submodule of the parent, alias it
        # - but break special cycles coming from builtin modules
        #   like ast -> _ast -> ast (here we inspect _ast)
        #   or os -> posix/nt -> os (here we inspect posix/nt)
        if self.parent is None:
            return None

        obj = self.obj
        if isinstance(obj, cached_property):
            obj = obj.func

        try:
            child_module = getmodule(obj)
        except Exception:  # noqa: BLE001
            return None
        if not child_module:
            return None

        if self.parent.is_module:
            parent_module = self.parent.obj
        else:
            parent_module = getmodule(self.parent.obj)
            if not parent_module:
                return None

        parent_module_path = getattr(parent_module.__spec__, "name", parent_module.__name__)
        child_module_path = getattr(child_module.__spec__, "name", child_module.__name__)
        parent_base_name = parent_module_path.split(".")[-1]
        child_base_name = child_module_path.split(".")[-1]

        # special cases: inspect.getmodule does not return the real modules
        # for those, but rather the "user-facing" ones - we prevent that
        # and use the real parent module
        if (
            parent_module_path,
            child_module_path,
        ) in _cyclic_relationships or parent_base_name == f"_{child_base_name}":
            child_module = parent_module
            child_module_path = getattr(child_module.__spec__, "name", child_module.__name__)  # type: ignore[union-attr]

        if child_module_path == self.module.path or child_module_path.startswith(self.module.path + "."):
            return None

        child_module_path = child_module_path.lstrip("_")
        if self.kind is ObjectKind.MODULE:
            return child_module_path
        child_name = getattr(self.obj, "__name__", self.name)
        return f"{child_module_path}.{child_name}"


__all__ = ["ObjectKind", "ObjectNode"]
