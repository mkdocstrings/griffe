"""This module contains all the exceptions specific to Griffe."""


class GriffeError(Exception):
    """The base exception for all Griffe errors."""


class NameResolutionError(GriffeError):
    """Exception for names that cannot be resolved in a object scope."""


class UnhandledPthFileError(GriffeError):
    """Exception for unhandled .path files, when searching modules."""


class AliasResolutionError(GriffeError):
    """Exception for alias that cannot be resolved."""

    def __init__(self, target_path: str) -> None:
        """Initialize the exception.

        Parameters:
            target_path: The problematic target path.
        """
        self.target_path: str = target_path
        super().__init__(f"could not resolve {self.target_path}")


class LastNodeError(GriffeError):
    """Exception raised when trying to access a next or previous node."""


class RootNodeError(GriffeError):
    """Exception raised when trying to use siblings properties on a root node."""
