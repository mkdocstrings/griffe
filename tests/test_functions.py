"""Test functions loading."""

import inspect

from griffe.loader import GriffeLoader
from tests import FIXTURES_DIR

loader = GriffeLoader()


def test_loading_functions_arguments():  # noqa: WPS218
    """Test functions arguments loading."""
    module = loader.load_module(FIXTURES_DIR / "functions" / "arguments.py")
    assert module.members
    assert len(module.members) == 11  # noqa: WPS432

    function = module["f_posonly"]
    assert len(function.arguments) == 1
    arg = function.arguments[0]
    assert arg is function.arguments["posonly"]
    assert arg.name == "posonly"
    assert arg.kind is inspect.Parameter.POSITIONAL_ONLY
    assert arg.default is None

    function = module["f_posonly_default"]
    assert len(function.arguments) == 1
    arg = function.arguments[0]
    assert arg is function.arguments["posonly"]
    assert arg.name == "posonly"
    assert arg.kind is inspect.Parameter.POSITIONAL_ONLY
    assert arg.default == "0"

    function = module["f_posonly_poskw"]
    assert len(function.arguments) == 2
    arg = function.arguments[0]
    assert arg is function.arguments["posonly"]
    assert arg.name == "posonly"
    assert arg.kind is inspect.Parameter.POSITIONAL_ONLY
    assert arg.default is None
    arg = function.arguments[1]
    assert arg is function.arguments["poskw"]
    assert arg.name == "poskw"
    assert arg.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert arg.default is None

    function = module["f_posonly_poskw_default"]
    assert len(function.arguments) == 2
    arg = function.arguments[0]
    assert arg is function.arguments["posonly"]
    assert arg.name == "posonly"
    assert arg.kind is inspect.Parameter.POSITIONAL_ONLY
    assert arg.default is None
    arg = function.arguments[1]
    assert arg is function.arguments["poskw"]
    assert arg.name == "poskw"
    assert arg.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert arg.default == "0"

    function = module["f_posonly_default_poskw_default"]
    assert len(function.arguments) == 2
    arg = function.arguments[0]
    assert arg is function.arguments["posonly"]
    assert arg.name == "posonly"
    assert arg.kind is inspect.Parameter.POSITIONAL_ONLY
    assert arg.default == "0"
    arg = function.arguments[1]
    assert arg is function.arguments["poskw"]
    assert arg.name == "poskw"
    assert arg.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert arg.default == "1"

    function = module["f_posonly_poskw_kwonly"]
    assert len(function.arguments) == 3
    arg = function.arguments[0]
    assert arg is function.arguments["posonly"]
    assert arg.name == "posonly"
    assert arg.kind is inspect.Parameter.POSITIONAL_ONLY
    assert arg.default is None
    arg = function.arguments[1]
    assert arg is function.arguments["poskw"]
    assert arg.name == "poskw"
    assert arg.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert arg.default is None
    arg = function.arguments[2]
    assert arg is function.arguments["kwonly"]
    assert arg.name == "kwonly"
    assert arg.kind is inspect.Parameter.KEYWORD_ONLY
    assert arg.default is None

    function = module["f_posonly_poskw_kwonly_default"]
    assert len(function.arguments) == 3
    arg = function.arguments[0]
    assert arg is function.arguments["posonly"]
    assert arg.name == "posonly"
    assert arg.kind is inspect.Parameter.POSITIONAL_ONLY
    assert arg.default is None
    arg = function.arguments[1]
    assert arg is function.arguments["poskw"]
    assert arg.name == "poskw"
    assert arg.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert arg.default is None
    arg = function.arguments[2]
    assert arg is function.arguments["kwonly"]
    assert arg.name == "kwonly"
    assert arg.kind is inspect.Parameter.KEYWORD_ONLY
    assert arg.default == "0"

    function = module["f_posonly_poskw_default_kwonly_default"]
    assert len(function.arguments) == 3
    arg = function.arguments[0]
    assert arg is function.arguments["posonly"]
    assert arg.name == "posonly"
    assert arg.kind is inspect.Parameter.POSITIONAL_ONLY
    assert arg.default is None
    arg = function.arguments[1]
    assert arg is function.arguments["poskw"]
    assert arg.name == "poskw"
    assert arg.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert arg.default == "0"
    arg = function.arguments[2]
    assert arg is function.arguments["kwonly"]
    assert arg.name == "kwonly"
    assert arg.kind is inspect.Parameter.KEYWORD_ONLY
    assert arg.default == "1"

    function = module["f_posonly_default_poskw_default_kwonly_default"]
    arg = function.arguments[0]
    assert arg is function.arguments["posonly"]
    assert arg.name == "posonly"
    assert arg.kind is inspect.Parameter.POSITIONAL_ONLY
    assert arg.default == "0"
    arg = function.arguments[1]
    assert arg is function.arguments["poskw"]
    assert arg.name == "poskw"
    assert arg.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert arg.default == "1"
    arg = function.arguments[2]
    assert arg is function.arguments["kwonly"]
    assert arg.name == "kwonly"
    assert arg.kind is inspect.Parameter.KEYWORD_ONLY
    assert arg.default == "2"

    function = module["f_var"]
    assert len(function.arguments) == 3
    arg = function.arguments[0]
    assert arg.name == "*args"
    assert arg.annotation == "str"
    arg = function.arguments[1]
    assert arg.annotation is None
    arg = function.arguments[2]
    assert arg.name == "**kwargs"
    assert arg.annotation == "int"

    function = module["f_annorations"]
    assert len(function.arguments) == 4
    arg = function.arguments[0]
    assert arg.annotation == "str"
    arg = function.arguments[1]
    assert arg.annotation == "Any"
    arg = function.arguments[2]
    assert arg.annotation == "typing.Optional[typing.List[int]]"
    arg = function.arguments[3]
    assert arg.annotation == "float | None"
