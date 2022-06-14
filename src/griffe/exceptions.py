"""This module contains all the exceptions specific to Griffe."""

from __future__ import annotations


class GriffeError(Exception):
    """The base exception for all Griffe errors."""


class LoadingError(GriffeError):
    """The base exception for all Griffe errors."""


class NameResolutionError(GriffeError):
    """Exception for names that cannot be resolved in a object scope."""


class UnhandledEditablesModuleError(GriffeError):
    """Exception for unhandled editables modules, when searching modules."""


class UnimportableModuleError(GriffeError):
    """Exception for modules that cannot be imported."""


class AliasResolutionError(GriffeError):
    """Exception for alias that cannot be resolved."""

    def __init__(self, target_path: str) -> None:
        """Initialize the exception.

        Parameters:
            target_path: The problematic target path.
        """
        self.target_path: str = target_path
        super().__init__(f"Could not resolve {self.target_path}")


class CyclicAliasError(GriffeError):
    """Exception raised when a cycle is detected in aliases."""

    def __init__(self, chain: list[str]) -> None:
        """Initialize the exception.

        Parameters:
            chain: The cyclic chain of items (such as target path).
        """
        self.chain: list[str] = chain
        super().__init__("Cyclic aliases detected:\n  " + "\n  ".join(self.chain))


class LastNodeError(GriffeError):
    """Exception raised when trying to access a next or previous node."""


class RootNodeError(GriffeError):
    """Exception raised when trying to use siblings properties on a root node."""


class BuiltinModuleError(GriffeError):
    """Exception raised when trying to access the filepath of a builtin module."""


class ExtensionError(GriffeError):
    """Base class for errors raised by extensions."""


class ExtensionNotLoadedError(ExtensionError):
    """Exception raised when an extension could not be loaded."""
