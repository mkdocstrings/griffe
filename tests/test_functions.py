"""Test functions loading."""

import sys

import pytest

from griffe.dataclasses import ParameterKind
from griffe.loader import GriffeLoader
from tests import FIXTURES_DIR

loader = GriffeLoader()


@pytest.mark.skipif(sys.version_info < (3, 8), reason="posonly syntax not supported on Python 3.7")
def test_loading_functions_parameters():  # noqa: WPS218
    """Test functions parameters loading."""
    module = loader.load_module(FIXTURES_DIR / "functions" / "parameters.py")
    assert module.members
    assert len(module.members) == 14  # 3 imports  # noqa: WPS432

    function = module["f_posonly"]
    assert len(function.parameters) == 1
    param = function.parameters[0]
    assert param is function.parameters["posonly"]
    assert param.name == "posonly"
    assert param.kind is ParameterKind.positional_only
    assert param.default is None

    function = module["f_posonly_default"]
    assert len(function.parameters) == 1
    param = function.parameters[0]
    assert param is function.parameters["posonly"]
    assert param.name == "posonly"
    assert param.kind is ParameterKind.positional_only
    assert param.default == "0"

    function = module["f_posonly_poskw"]
    assert len(function.parameters) == 2
    param = function.parameters[0]
    assert param is function.parameters["posonly"]
    assert param.name == "posonly"
    assert param.kind is ParameterKind.positional_only
    assert param.default is None
    param = function.parameters[1]
    assert param is function.parameters["poskw"]
    assert param.name == "poskw"
    assert param.kind is ParameterKind.positional_or_keyword
    assert param.default is None

    function = module["f_posonly_poskw_default"]
    assert len(function.parameters) == 2
    param = function.parameters[0]
    assert param is function.parameters["posonly"]
    assert param.name == "posonly"
    assert param.kind is ParameterKind.positional_only
    assert param.default is None
    param = function.parameters[1]
    assert param is function.parameters["poskw"]
    assert param.name == "poskw"
    assert param.kind is ParameterKind.positional_or_keyword
    assert param.default == "0"

    function = module["f_posonly_default_poskw_default"]
    assert len(function.parameters) == 2
    param = function.parameters[0]
    assert param is function.parameters["posonly"]
    assert param.name == "posonly"
    assert param.kind is ParameterKind.positional_only
    assert param.default == "0"
    param = function.parameters[1]
    assert param is function.parameters["poskw"]
    assert param.name == "poskw"
    assert param.kind is ParameterKind.positional_or_keyword
    assert param.default == "1"

    function = module["f_posonly_poskw_kwonly"]
    assert len(function.parameters) == 3
    param = function.parameters[0]
    assert param is function.parameters["posonly"]
    assert param.name == "posonly"
    assert param.kind is ParameterKind.positional_only
    assert param.default is None
    param = function.parameters[1]
    assert param is function.parameters["poskw"]
    assert param.name == "poskw"
    assert param.kind is ParameterKind.positional_or_keyword
    assert param.default is None
    param = function.parameters[2]
    assert param is function.parameters["kwonly"]
    assert param.name == "kwonly"
    assert param.kind is ParameterKind.keyword_only
    assert param.default is None

    function = module["f_posonly_poskw_kwonly_default"]
    assert len(function.parameters) == 3
    param = function.parameters[0]
    assert param is function.parameters["posonly"]
    assert param.name == "posonly"
    assert param.kind is ParameterKind.positional_only
    assert param.default is None
    param = function.parameters[1]
    assert param is function.parameters["poskw"]
    assert param.name == "poskw"
    assert param.kind is ParameterKind.positional_or_keyword
    assert param.default is None
    param = function.parameters[2]
    assert param is function.parameters["kwonly"]
    assert param.name == "kwonly"
    assert param.kind is ParameterKind.keyword_only
    assert param.default == "0"

    function = module["f_posonly_poskw_default_kwonly_default"]
    assert len(function.parameters) == 3
    param = function.parameters[0]
    assert param is function.parameters["posonly"]
    assert param.name == "posonly"
    assert param.kind is ParameterKind.positional_only
    assert param.default is None
    param = function.parameters[1]
    assert param is function.parameters["poskw"]
    assert param.name == "poskw"
    assert param.kind is ParameterKind.positional_or_keyword
    assert param.default == "0"
    param = function.parameters[2]
    assert param is function.parameters["kwonly"]
    assert param.name == "kwonly"
    assert param.kind is ParameterKind.keyword_only
    assert param.default == "1"

    function = module["f_posonly_default_poskw_default_kwonly_default"]
    param = function.parameters[0]
    assert param is function.parameters["posonly"]
    assert param.name == "posonly"
    assert param.kind is ParameterKind.positional_only
    assert param.default == "0"
    param = function.parameters[1]
    assert param is function.parameters["poskw"]
    assert param.name == "poskw"
    assert param.kind is ParameterKind.positional_or_keyword
    assert param.default == "1"
    param = function.parameters[2]
    assert param is function.parameters["kwonly"]
    assert param.name == "kwonly"
    assert param.kind is ParameterKind.keyword_only
    assert param.default == "2"

    function = module["f_var"]
    assert len(function.parameters) == 3
    param = function.parameters[0]
    assert param.name == "*args"
    assert param.annotation.source == "str"
    assert param.annotation.full == "str"
    param = function.parameters[1]
    assert param.annotation is None
    param = function.parameters[2]
    assert param.name == "**kwargs"
    assert param.annotation.source == "int"
    assert param.annotation.full == "int"

    function = module["f_annorations"]
    assert len(function.parameters) == 4
    param = function.parameters[0]
    assert param.annotation.source == "str"
    assert param.annotation.full == "str"
    param = function.parameters[1]
    assert param.annotation.source == "Any"
    assert param.annotation.full == "typing.Any"
    param = function.parameters[2]
    assert str(param.annotation) == "typing.Optional[typing.List[int]]"
    param = function.parameters[3]
    assert str(param.annotation) == "float | None"
