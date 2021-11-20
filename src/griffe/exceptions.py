"""This module contains all the exceptions specific to Griffe."""


class GriffeError(Exception):
    """The base exception for all Griffe errors."""


class NameResolutionError(GriffeError):
    """Exception for names that cannot be resolved in a object scope."""


class UnhandledPthFileError(GriffeError):
    """Exception for unhandled .path files, when searching modules."""


class LastNodeError(GriffeError):
    """Exception raised when trying to access a next or previous node."""


class RootNodeError(GriffeError):
    """Exception raised when trying to use siblings properties on a root node."""
