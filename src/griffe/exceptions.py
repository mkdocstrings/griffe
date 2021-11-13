"""This module contains all the exceptions specific to Griffe."""


class ResolutionError(Exception):
    """Exception for names that cannot be resolved in a object scope."""


class UnhandledPthFileError(Exception):
    """Exception for unhandled .path files, when searching modules."""
