# This module contains some mixins classes that hold shared methods
# of the different kinds of objects, and aliases.

from __future__ import annotations

import json
from contextlib import suppress
from typing import TYPE_CHECKING, Any, TypeVar

from _griffe.enumerations import Kind
from _griffe.exceptions import AliasResolutionError, BuiltinModuleError, CyclicAliasError
from _griffe.merger import merge_stubs

if TYPE_CHECKING:
    from collections.abc import Sequence

    from _griffe.models import Alias, Attribute, Class, Function, Module, Object, TypeAlias

_ObjType = TypeVar("_ObjType")


def _get_parts(key: str | Sequence[str]) -> Sequence[str]:
    if isinstance(key, str):
        if not key:
            raise ValueError("Empty strings are not supported")
        parts = key.split(".")
    else:
        parts = list(key)
    if not parts:
        raise ValueError("Empty tuples are not supported")
    return parts


class GetMembersMixin:
    """Mixin class to share methods for accessing members.

    Methods:
        get_member: Get a member with its name or path.
        __getitem__: Same as `get_member`, with the item syntax `[]`.
    """

    def __getitem__(self, key: str | Sequence[str]) -> Any:
        """Get a member with its name or path.

        This method is part of the consumer API:
        do not use when producing Griffe trees!

        Members will be looked up in both declared members and inherited ones,
        triggering computation of the latter.

        Parameters:
            key: The name or path of the member.

        Examples:
            >>> foo = griffe_object["foo"]
            >>> bar = griffe_object["path.to.bar"]
            >>> qux = griffe_object[("path", "to", "qux")]
        """
        parts = _get_parts(key)
        if len(parts) == 1:
            return self.all_members[parts[0]]  # type: ignore[attr-defined]
        return self.all_members[parts[0]][parts[1:]]  # type: ignore[attr-defined]

    def get_member(self, key: str | Sequence[str]) -> Any:
        """Get a member with its name or path.

        This method is part of the producer API:
        you can use it safely while building Griffe trees
        (for example in Griffe extensions).

        Members will be looked up in declared members only, not inherited ones.

        Parameters:
            key: The name or path of the member.

        Examples:
            >>> foo = griffe_object["foo"]
            >>> bar = griffe_object["path.to.bar"]
            >>> bar = griffe_object[("path", "to", "bar")]
        """
        parts = _get_parts(key)
        if len(parts) == 1:
            return self.members[parts[0]]  # type: ignore[attr-defined]
        return self.members[parts[0]].get_member(parts[1:])  # type: ignore[attr-defined]


# FIXME: Are `aliases` in other objects correctly updated when we delete a member?
# Would weak references be useful there?
class DelMembersMixin:
    """Mixin class to share methods for deleting members.

    Methods:
        del_member: Delete a member with its name or path.
        __delitem__: Same as `del_member`, with the item syntax `[]`.
    """

    def __delitem__(self, key: str | Sequence[str]) -> None:
        """Delete a member with its name or path.

        This method is part of the consumer API:
        do not use when producing Griffe trees!

        Members will be looked up in both declared members and inherited ones,
        triggering computation of the latter.

        Parameters:
            key: The name or path of the member.

        Examples:
            >>> del griffe_object["foo"]
            >>> del griffe_object["path.to.bar"]
            >>> del griffe_object[("path", "to", "qux")]
        """
        parts = _get_parts(key)
        if len(parts) == 1:
            name = parts[0]
            try:
                del self.members[name]  # type: ignore[attr-defined]
            except KeyError:
                del self.inherited_members[name]  # type: ignore[attr-defined]
        else:
            del self.all_members[parts[0]][parts[1:]]  # type: ignore[attr-defined]

    def del_member(self, key: str | Sequence[str]) -> None:
        """Delete a member with its name or path.

        This method is part of the producer API:
        you can use it safely while building Griffe trees
        (for example in Griffe extensions).

        Members will be looked up in declared members only, not inherited ones.

        Parameters:
            key: The name or path of the member.

        Examples:
            >>> griffe_object.del_member("foo")
            >>> griffe_object.del_member("path.to.bar")
            >>> griffe_object.del_member(("path", "to", "qux"))
        """
        parts = _get_parts(key)
        if len(parts) == 1:
            name = parts[0]
            del self.members[name]  # type: ignore[attr-defined]
        else:
            self.members[parts[0]].del_member(parts[1:])  # type: ignore[attr-defined]


class SetMembersMixin:
    """Mixin class to share methods for setting members.

    Methods:
        set_member: Set a member with its name or path.
        __setitem__: Same as `set_member`, with the item syntax `[]`.
    """

    def __setitem__(self, key: str | Sequence[str], value: Object | Alias) -> None:
        """Set a member with its name or path.

        This method is part of the consumer API:
        do not use when producing Griffe trees!

        Parameters:
            key: The name or path of the member.
            value: The member.

        Examples:
            >>> griffe_object["foo"] = foo
            >>> griffe_object["path.to.bar"] = bar
            >>> griffe_object[("path", "to", "qux")] = qux
        """
        parts = _get_parts(key)
        if len(parts) == 1:
            name = parts[0]
            self.members[name] = value  # type: ignore[attr-defined]
            if self.is_collection:  # type: ignore[attr-defined]
                value._modules_collection = self  # type: ignore[union-attr]
            else:
                value.parent = self  # type: ignore[assignment]
        else:
            self.members[parts[0]][parts[1:]] = value  # type: ignore[attr-defined]

    def set_member(self, key: str | Sequence[str], value: Object | Alias) -> None:
        """Set a member with its name or path.

        This method is part of the producer API:
        you can use it safely while building Griffe trees
        (for example in Griffe extensions).

        Parameters:
            key: The name or path of the member.
            value: The member.

        Examples:
            >>> griffe_object.set_member("foo", foo)
            >>> griffe_object.set_member("path.to.bar", bar)
            >>> griffe_object.set_member(("path", "to", "qux"), qux)
        """
        parts = _get_parts(key)
        if len(parts) == 1:
            name = parts[0]
            if name in self.members:  # type: ignore[attr-defined]
                member = self.members[name]  # type: ignore[attr-defined]
                if not member.is_alias:
                    # When reassigning a module to an existing one,
                    # try to merge them as one regular and one stubs module
                    # (implicit support for .pyi modules).
                    if member.is_module and not (member.is_namespace_package or member.is_namespace_subpackage):
                        # Accessing attributes of the value or member can trigger alias errors.
                        # Accessing file paths can trigger a builtin module error.
                        with suppress(AliasResolutionError, CyclicAliasError, BuiltinModuleError):
                            if value.is_module and value.filepath != member.filepath:
                                with suppress(ValueError):
                                    value = merge_stubs(member, value)  # type: ignore[arg-type]
                    for alias in member.aliases.values():
                        with suppress(CyclicAliasError):
                            alias.target = value
            self.members[name] = value  # type: ignore[attr-defined]
            if self.is_collection:  # type: ignore[attr-defined]
                value._modules_collection = self  # type: ignore[union-attr]
            else:
                value.parent = self  # type: ignore[assignment]
        else:
            self.members[parts[0]].set_member(parts[1:], value)  # type: ignore[attr-defined]


class SerializationMixin:
    """Mixin class to share methods for de/serializing objects.

    Methods:
        as_json: Return this object's data as a JSON string.
        from_json: Create an instance of this class from a JSON string.
    """

    def as_json(self, *, full: bool = False, **kwargs: Any) -> str:
        """Return this object's data as a JSON string.

        Parameters:
            full: Whether to return full info, or just base info.
            **kwargs: Additional serialization options passed to encoder.

        Returns:
            A JSON string.
        """
        from _griffe.encoders import JSONEncoder  # avoid circular import

        return json.dumps(self, cls=JSONEncoder, full=full, **kwargs)

    @classmethod
    def from_json(cls: type[_ObjType], json_string: str, **kwargs: Any) -> _ObjType:  # noqa: PYI019
        """Create an instance of this class from a JSON string.

        Parameters:
            json_string: JSON to decode into Object.
            **kwargs: Additional options passed to decoder.

        Returns:
            An Object instance.

        Raises:
            TypeError: When the json_string does not represent and object
                of the class from which this classmethod has been called.
        """
        from _griffe.encoders import json_decoder  # avoid circular import

        kwargs.setdefault("object_hook", json_decoder)
        obj = json.loads(json_string, **kwargs)
        if not isinstance(obj, cls):
            raise TypeError(f"provided JSON object is not of type {cls}")
        return obj


class ObjectAliasMixin(GetMembersMixin, SetMembersMixin, DelMembersMixin, SerializationMixin):
    """Mixin class to share methods that appear both in objects and aliases, unchanged.

    Attributes:
        all_members: All members (declared and inherited).
        modules: The module members.
        classes: The class members.
        functions: The function members.
        attributes: The attribute members.
        type_aliases: The type alias members.
        is_private: Whether this object/alias is private (starts with `_`) but not special.
        is_class_private: Whether this object/alias is class-private (starts with `__` and is a class member).
        is_special: Whether this object/alias is special ("dunder" attribute/method, starts and end with `__`).
        is_imported: Whether this object/alias was imported from another module.
        is_exported: Whether this object/alias is exported (listed in `__all__`).
        is_wildcard_exposed: Whether this object/alias is exposed to wildcard imports.
        is_public: Whether this object is considered public.
        is_deprecated: Whether this object is deprecated.
    """

    @property
    def all_members(self) -> dict[str, Object | Alias]:
        """All members (declared and inherited).

        This method is part of the consumer API:
        do not use when producing Griffe trees!
        """
        if self.is_class:  # type: ignore[attr-defined]
            return {**self.inherited_members, **self.members}  # type: ignore[attr-defined]
        return self.members  # type: ignore[attr-defined]

    @property
    def modules(self) -> dict[str, Module]:
        """The module members.

        This method is part of the consumer API:
        do not use when producing Griffe trees!
        """
        return {name: member for name, member in self.all_members.items() if member.kind is Kind.MODULE}  # type: ignore[misc]

    @property
    def classes(self) -> dict[str, Class]:
        """The class members.

        This method is part of the consumer API:
        do not use when producing Griffe trees!
        """
        return {name: member for name, member in self.all_members.items() if member.kind is Kind.CLASS}  # type: ignore[misc]

    @property
    def functions(self) -> dict[str, Function]:
        """The function members.

        This method is part of the consumer API:
        do not use when producing Griffe trees!
        """
        return {name: member for name, member in self.all_members.items() if member.kind is Kind.FUNCTION}  # type: ignore[misc]

    @property
    def attributes(self) -> dict[str, Attribute]:
        """The attribute members.

        This method is part of the consumer API:
        do not use when producing Griffe trees!
        """
        return {name: member for name, member in self.all_members.items() if member.kind is Kind.ATTRIBUTE}  # type: ignore[misc]

    @property
    def type_aliases(self) -> dict[str, TypeAlias]:
        """The type alias members.

        This method is part of the consumer API:
        do not use when producing Griffe trees!
        """
        return {name: member for name, member in self.all_members.items() if member.kind is Kind.TYPE_ALIAS}  # type: ignore[misc]

    @property
    def is_private(self) -> bool:
        """Whether this object/alias is private (starts with `_`) but not special."""
        return self.name.startswith("_") and not self.is_special  # type: ignore[attr-defined]

    @property
    def is_special(self) -> bool:
        """Whether this object/alias is special ("dunder" attribute/method, starts and end with `__`)."""
        return self.name.startswith("__") and self.name.endswith("__")  # type: ignore[attr-defined]

    @property
    def is_class_private(self) -> bool:
        """Whether this object/alias is class-private (starts with `__` and is a class member)."""
        return self.parent and self.parent.is_class and self.name.startswith("__") and not self.name.endswith("__")  # type: ignore[attr-defined]

    @property
    def is_imported(self) -> bool:
        """Whether this object/alias was imported from another module."""
        return self.parent and self.name in self.parent.imports  # type: ignore[attr-defined]

    @property
    def is_exported(self) -> bool:
        """Whether this object/alias is exported (listed in `__all__`)."""
        return self.parent.is_module and bool(self.parent.exports and self.name in self.parent.exports)  # type: ignore[attr-defined]

    @property
    def is_wildcard_exposed(self) -> bool:
        """Whether this object/alias is exposed to wildcard imports.

        To be exposed to wildcard imports, an object/alias must:

        - be available at runtime
        - have a module as parent
        - be listed in `__all__` if `__all__` is defined
        - or not be private (having a name starting with an underscore)

        Special case for Griffe trees: a submodule is only exposed if its parent imports it.

        Returns:
            True or False.
        """
        # If the object is not available at runtime or is not defined at the module level, it is not exposed.
        if not self.runtime or not self.parent.is_module:  # type: ignore[attr-defined]
            return False

        # If the parent module defines `__all__`, the object is exposed if it is listed in it.
        if self.parent.exports is not None:  # type: ignore[attr-defined]
            return self.name in self.parent.exports  # type: ignore[attr-defined]

        # If the object's name starts with an underscore, it is not exposed.
        # We don't use `is_private` or `is_special` here to avoid redundant string checks.
        if self.name.startswith("_"):  # type: ignore[attr-defined]
            return False

        # Special case for Griffe trees: a submodule is only exposed if its parent imports it.
        return self.is_alias or not self.is_module or self.is_imported  # type: ignore[attr-defined]

    @property
    def is_public(self) -> bool:
        """Whether this object is considered public.

        In modules, developers can mark objects as public thanks to the `__all__` variable.
        In classes however, there is no convention or standard to do so.

        Therefore, to decide whether an object is public, we follow this algorithm:

        - If the object's `public` attribute is set (boolean), return its value.
        - If the object is listed in its parent's (a module) `__all__` attribute, it is public.
        - If the parent (module) defines `__all__` and the object is not listed in, it is private.
        - If the object has a private name, it is private.
        - If the object was imported from another module, it is private.
        - Otherwise, the object is public.
        """
        # Give priority to the `public` attribute if it is set.
        if self.public is not None:  # type: ignore[attr-defined]
            return self.public  # type: ignore[attr-defined]

        # If the object is a module and its name does not start with an underscore, it is public.
        # Modules are not subject to the `__all__` convention, only the underscore prefix one.
        if not self.is_alias and self.is_module and not self.name.startswith("_"):  # type: ignore[attr-defined]
            return True

        # If the object is defined at the module-level and is listed in `__all__`, it is public.
        # If the parent module defines `__all__` but does not list the object, it is private.
        if self.parent and self.parent.is_module and bool(self.parent.exports):  # type: ignore[attr-defined]
            return self.name in self.parent.exports  # type: ignore[attr-defined]

        # Special objects are always considered public.
        # Even if we don't access them directly, they are used through different *public* means
        # like instantiating classes (`__init__`), using operators (`__eq__`), etc..
        if self.is_private:
            return False

        # TODO: In a future version, we will support two conventions regarding imports:
        # - `from a import x as x` marks `x` as public.
        # - `from a import *` marks all wildcard imported objects as public.
        if self.is_imported:  # noqa: SIM103
            return False

        # If we reached this point, the object is public.
        return True

    @property
    def is_deprecated(self) -> bool:
        """Whether this object is deprecated."""
        # NOTE: We might want to add more ways to detect deprecations in the future.
        return bool(self.deprecated)  # type: ignore[attr-defined]

    @property
    def is_generic(self) -> bool:
        """Whether this object is generic."""
        return bool(self.type_parameters)  # type: ignore[attr-defined]
