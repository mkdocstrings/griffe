"""This module contains some mixins classes about accessing and setting members."""

from __future__ import annotations

from typing import Any, Sequence


class GetMembersMixin:
    """This mixin adds a `__getitem__` method to a class.

    It makes it easier to access members of an object.
    The method expects a `members` attribute/property to be available on the instance.
    """

    def __getitem__(self, key: str | Sequence[str]) -> Any:
        if isinstance(key, str):
            if not key:
                return self
            parts = key.split(".", 1)
        else:
            parts = list(key)
        if not parts:
            return self
        if len(parts) == 1:
            return self.members[parts[0]]  # type: ignore
        return self.members[parts[0]][parts[1]]  # type: ignore


class SetMembersMixin:
    """This mixin adds a `__setitem__` method to a class.

    It makes it easier to set members of an object.
    The method expects a `members` attribute/property to be available on the instance.
    Each time a member is set, its `parent` attribute is set as well.
    """

    def __setitem__(self, key: str | Sequence[str], value):
        if isinstance(key, str):
            if not key:
                raise ValueError("cannot set self (empty key)")
            parts = key.split(".", 1)
        else:
            parts = list(key)
        if not parts:
            raise ValueError("cannot set self (empty parts)")
        if len(parts) == 1:
            self.members[parts[0]] = value  # type: ignore
            value.parent = self
        else:
            self.members[parts[0]][parts[1]] = value  # type: ignore


class SetCollectionMembersMixin:
    """This mixin adds a `__setitem__` method to a class.

    It makes it easier to set members of an object.
    The method expects a `members` attribute/property to be available on the instance.
    Each time a member is set, its `_modules_collection` attribute is set as well.
    """

    def __setitem__(self, key: str | Sequence[str], value):
        if isinstance(key, str):
            if not key:
                raise ValueError("cannot set self (empty key)")
            parts = key.split(".", 1)
        else:
            parts = list(key)
        if not parts:
            raise ValueError("cannot set self (empty parts)")
        if len(parts) == 1:
            self.members[parts[0]] = value  # type: ignore
            value._modules_collection = self  # noqa: WPS437
        else:
            self.members[parts[0]][parts[1]] = value  # type: ignore


class ObjectAliasMixin:
    """A mixin for methods that appear both in objects and aliases, unchanged."""

    def is_exported(self, explicitely: bool = True) -> bool:
        """Tell if this object/alias is implicitely exported by its parent.

        Parameters:
            explicitely: Whether to only return True when `__all__` is defined.

        Returns:
            True or False.
        """
        return self.parent.member_is_exported(self, explicitely=explicitely)  # type: ignore

    @property
    def is_explicitely_exported(self) -> bool:
        """Tell if this object/alias is explicitely exported by its parent.

        Returns:
            True or False.
        """
        return self.is_exported(explicitely=True)

    @property
    def is_implicitely_exported(self) -> bool:
        """Tell if this object/alias is implicitely exported by its parent.

        Returns:
            True or False.
        """
        return self.parent.exports is None  # type: ignore
