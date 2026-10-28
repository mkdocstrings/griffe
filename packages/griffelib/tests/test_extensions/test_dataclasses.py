# SPDX-License-Identifier: ISC
#
# Copyright (c) 2021, Timothée Mazzucotelli and contributors
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# Test the dataclasses extension.

import pytest

from griffe import ParameterKind, load_extensions, temporary_visited_package


def test_dataclass_support() -> None:
    """Test our `dataclass` support."""
    code = """
        from dataclasses import dataclass

        @dataclass
        class Point:
            x: int
            '''Docstring for x.'''
            y: int
            '''Docstring for y.'''
    """
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code},
        extensions=load_extensions("dataclasses"),
    ) as pkg:
        point = pkg["Point"]
    assert "__init__" in point.members
    init = point["__init__"]
    assert len(init.parameters) == 3
    assert "self" in init.parameters
    assert "x" in init.parameters
    assert "y" in init.parameters
    assert str(init.parameters["x"].annotation) == "int"
    assert str(init.parameters["y"].annotation) == "int"
    assert init.parameters["x"].docstring.value == "Docstring for x."
    assert init.parameters["y"].docstring.value == "Docstring for y."
    assert init.returns == "None"


def test_non_init_fields() -> None:
    """Test that non-init fields are not included in the `__init__` method."""
    code = """
        from dataclasses import dataclass, field

        @dataclass
        class Point:
            x: int
            '''Docstring for x.'''
            y: int = field(init=False)
            '''Docstring for y.'''
    """
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code},
        extensions=load_extensions("dataclasses"),
    ) as pkg:
        point = pkg["Point"]
    assert "__init__" in point.members
    init = point["__init__"]
    assert len(init.parameters) == 2
    assert "self" in init.parameters
    assert "x" in init.parameters
    assert "y" not in init.parameters


def test_classvar_fields() -> None:
    """Test that `ClassVar` fields are not included in the `__init__` method."""
    code = """
        from dataclasses import dataclass
        from typing import ClassVar

        @dataclass
        class Point:
            x: int
            '''Docstring for x.'''
            y: ClassVar[int]
            '''Docstring for y.'''
    """
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code},
        extensions=load_extensions("dataclasses"),
    ) as pkg:
        point = pkg["Point"]
    assert "__init__" in point.members
    init = point["__init__"]
    assert len(init.parameters) == 2
    assert "self" in init.parameters
    assert "x" in init.parameters
    assert "y" not in init.parameters


def test_kw_only_fields() -> None:
    """Test that `kw_only` fields are included as keyword-only parameters in the `__init__` method."""
    code = """
        from dataclasses import dataclass, field

        @dataclass
        class Point:
            x: int
            '''Docstring for x.'''
            y: int = field(kw_only=True)
            '''Docstring for y.'''
    """
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code},
        extensions=load_extensions("dataclasses"),
    ) as pkg:
        point = pkg["Point"]
    assert "__init__" in point.members
    init = point["__init__"]
    assert len(init.parameters) == 3
    assert "self" in init.parameters
    assert "x" in init.parameters
    assert "y" in init.parameters
    assert init.parameters["y"].kind is ParameterKind.keyword_only


def test_kw_only_sentinel() -> None:
    """Test that the `KW_ONLY` sentinel works."""
    code = """
        from dataclasses import dataclass, KW_ONLY

        @dataclass
        class Point:
            x: int
            '''Docstring for x.'''
            _: KW_ONLY
            y: int
            '''Docstring for y.'''
    """
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code},
        extensions=load_extensions("dataclasses"),
    ) as pkg:
        point = pkg["Point"]
    assert "__init__" in point.members
    init = point["__init__"]
    assert len(init.parameters) == 3
    assert "self" in init.parameters
    assert "x" in init.parameters
    assert "y" in init.parameters
    assert init.parameters["y"].kind is ParameterKind.keyword_only


def test_all_kw_only_fields() -> None:
    """Test that all fields can be made keyword-only."""
    code = """
        from dataclasses import dataclass

        @dataclass(kw_only=True)
        class Point:
            x: int
            '''Docstring for x.'''
            y: int
            '''Docstring for y.'''
    """
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code},
        extensions=load_extensions("dataclasses"),
    ) as pkg:
        point = pkg["Point"]
    assert "__init__" in point.members
    init = point["__init__"]
    assert len(init.parameters) == 3
    assert "self" in init.parameters
    assert "x" in init.parameters
    assert "y" in init.parameters
    assert init.parameters["x"].kind is ParameterKind.keyword_only
    assert init.parameters["y"].kind is ParameterKind.keyword_only


def test_field_kw_only_overrides_class_kw_only() -> None:
    """Test that `field(kw_only=False)` takes precedence over `@dataclass(kw_only=True)`."""
    code = """
        from dataclasses import dataclass, field

        @dataclass(kw_only=True)
        class Point:
            x: int = 0
            y: int = field(default=0, kw_only=False)
    """
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code},
        extensions=load_extensions("dataclasses"),
    ) as pkg:
        point = pkg["Point"]
    init = point["__init__"]
    assert [param.name for param in init.parameters] == ["self", "y", "x"]
    assert init.parameters["x"].kind is ParameterKind.keyword_only
    assert init.parameters["y"].kind is ParameterKind.positional_or_keyword


def test_field_kw_only_overrides_kw_only_sentinel() -> None:
    """Test that `field(kw_only=False)` takes precedence over the `KW_ONLY` sentinel."""
    code = """
        from dataclasses import dataclass, field, KW_ONLY

        @dataclass
        class Point:
            x: int
            _: KW_ONLY
            y: int = 0
            z: int = field(default=0, kw_only=False)
    """
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code},
        extensions=load_extensions("dataclasses"),
    ) as pkg:
        point = pkg["Point"]
    init = point["__init__"]
    assert [param.name for param in init.parameters] == ["self", "x", "z", "y"]
    assert init.parameters["y"].kind is ParameterKind.keyword_only
    assert init.parameters["z"].kind is ParameterKind.positional_or_keyword


@pytest.mark.parametrize("plain_decorator", ["@dataclass", ""], ids=["dataclass", "not-dataclass"])
def test_fields_merged_from_each_base_in_diamond_inheritance(plain_decorator: str) -> None:
    """Test that each base brings all its fields, inherited ones included, in reversed MRO order like in Python."""
    code = f"""
        from dataclasses import dataclass

        @dataclass
        class Base:
            x: int = 0

        @dataclass
        class Override(Base):
            x: int = 1

        {plain_decorator}
        class Plain(Base):
            pass

        @dataclass
        class Point(Plain, Override):
            pass
    """
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code},
        extensions=load_extensions("dataclasses"),
    ) as pkg:
        point = pkg["Point"]
    init = point["__init__"]
    # `Plain` comes after `Override` in reversed MRO order, and brings back `Base.x`.
    assert [param.name for param in init.parameters] == ["self", "x"]
    assert init.parameters["x"].default == "0"
