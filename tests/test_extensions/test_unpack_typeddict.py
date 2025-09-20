"""Test the unpack extension."""

from griffe import DocstringSectionKind, load_extensions, temporary_visited_package


def test_typeddict_support() -> None:
    """Test our `TypedDict` support."""
    code = """
        from typing import TypedDict

        class Kwargs(TypedDict):
            a: int
            '''Docstring for a.'''
            b: str
            '''Docstring for b.'''
    """
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code},
        extensions=load_extensions("unpack_typeddict"),
        docstring_parser="google",
    ) as pkg:
        td = pkg["Kwargs"]

    # Signature of the `__init__` method.
    assert "__init__" in td.members
    init = td["__init__"]
    assert len(init.parameters) == 3
    assert "self" in init.parameters
    assert "a" in init.parameters
    assert "b" in init.parameters
    assert str(init.parameters["a"].annotation) == "int"
    assert str(init.parameters["b"].annotation) == "str"
    assert init.parameters["a"].docstring.value == "Docstring for a."
    assert init.parameters["b"].docstring.value == "Docstring for b."
    assert init.returns == "None"

    # Docstring and its "Parameters" section.
    assert init.docstring
    sections = init.docstring.parsed
    assert len(sections) == 1
    params_section = sections[0]
    assert params_section.kind is DocstringSectionKind.parameters
    assert len(params_section.value) == 2
    assert params_section.value[0].name == "a"
    assert params_section.value[0].description == "Docstring for a."
    assert str(params_section.value[0].annotation) == "int"
    assert params_section.value[1].name == "b"
    assert params_section.value[1].description == "Docstring for b."
    assert str(params_section.value[1].annotation) == "str"


def test_unpack_support() -> None:
    """Test our `Unpack` support."""
    code = """
        from typing import TypedDict, Unpack

        class Kwargs(TypedDict):
            a: int
            '''Docstring for a.'''
            b: str
            '''Docstring for b.'''

        def func(**kwargs: Unpack[Kwargs]) -> None:
            '''A function.

            Parameters:
                **kwargs: The keyword arguments.
            '''
            pass
    """
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code},
        extensions=load_extensions("unpack_typeddict"),
        docstring_parser="google",
    ) as pkg:
        func = pkg["func"]

    # Signature of the `func` function.
    assert len(func.parameters) == 2
    assert "a" in func.parameters
    assert "b" in func.parameters
    assert str(func.parameters["a"].annotation) == "int"
    assert str(func.parameters["b"].annotation) == "str"
    assert func.parameters["a"].docstring.value == "Docstring for a."
    assert func.parameters["b"].docstring.value == "Docstring for b."

    # Docstring and its "Parameters" section.
    assert func.docstring is not None
    sections = func.docstring.parsed
    assert len(sections) == 2
    params_section = sections[1]
    assert params_section.kind is DocstringSectionKind.parameters
    assert len(params_section.value) == 2
    param_a = next(param for param in params_section.value if param.name == "a")
    param_b = next(param for param in params_section.value if param.name == "b")
    assert str(param_a.annotation) == "int"
    assert str(param_b.annotation) == "str"
    assert param_a.description == "Docstring for a."
    assert param_b.description == "Docstring for b."


def test_non_total_typeddict() -> None:
    """Test our `TypedDict` support with non-total `TypedDict`s."""
    code = """
        from typing import TypedDict

        class Kwargs(TypedDict, total=False):
            a: int
            '''Docstring for a.'''
            b: str
            '''Docstring for b.'''
    """
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code},
        extensions=load_extensions("unpack_typeddict"),
        docstring_parser="google",
    ) as pkg:
        td = pkg["Kwargs"]

    # Docstring and its "Parameters" section.
    init = td["__init__"]
    assert init.docstring
    sections = init.docstring.parsed
    assert len(sections) == 1
    params_section = sections[0]
    assert params_section.kind is DocstringSectionKind.parameters
    assert len(params_section.value) == 2
    assert params_section.value[0].name == "a"
    assert params_section.value[0].description == "Docstring for a."
    assert params_section.value[0].value == "..."
    assert str(params_section.value[0].annotation) == "int"
    assert params_section.value[1].name == "b"
    assert params_section.value[1].description == "Docstring for b."
    assert params_section.value[1].value == "..."
    assert str(params_section.value[1].annotation) == "str"


def test_non_total_unpack() -> None:
    """Test unpacking non-total `TypedDict`s."""
    code = """
        from typing import TypedDict, Unpack

        class Kwargs(TypedDict, total=False):
            a: int
            '''Docstring for a.'''
            b: str
            '''Docstring for b.'''

        def func(**kwargs: Unpack[Kwargs]) -> None:
            '''A function.'''
    """
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code},
        extensions=load_extensions("unpack_typeddict"),
        docstring_parser="google",
    ) as pkg:
        td = pkg["Kwargs"]

    # Docstring and its "Parameters" section.
    init = td["__init__"]
    assert init.docstring
    sections = init.docstring.parsed
    assert len(sections) == 1
    params_section = sections[0]
    assert params_section.kind is DocstringSectionKind.parameters
    assert len(params_section.value) == 2
    assert params_section.value[0].name == "a"
    assert params_section.value[0].description == "Docstring for a."
    assert params_section.value[0].value == "..."
    assert str(params_section.value[0].annotation) == "int"
    assert params_section.value[1].name == "b"
    assert params_section.value[1].description == "Docstring for b."
    assert params_section.value[1].value == "..."
    assert str(params_section.value[1].annotation) == "str"


def test_explicit_requiredness() -> None:
    """Test our `TypedDict` support with explicit requiredness."""
    code = """
        from typing import TypedDict
        from typing_extensions import Required, NotRequired

        class Kwargs(TypedDict):
            a: NotRequired[int]
            '''Docstring for a.'''
            b: Required[str]
            '''Docstring for b.'''
    """
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code},
        extensions=load_extensions("unpack_typeddict"),
        docstring_parser="google",
    ) as pkg:
        td = pkg["Kwargs"]

    # Signature of the `__init__` method.
    assert "__init__" in td.members
    init = td["__init__"]
    assert len(init.parameters) == 3
    assert "self" in init.parameters
    assert "a" in init.parameters
    assert "b" in init.parameters
    assert str(init.parameters["a"].annotation) == "int"
    assert str(init.parameters["b"].annotation) == "str"
    assert init.parameters["a"].docstring.value == "Docstring for a."
    assert init.parameters["b"].docstring.value == "Docstring for b."
    assert init.parameters["a"].default == "..."
    assert init.parameters["b"].default is None
    assert [p.name for p in init.parameters] == ["self", "b", "a"]



def test_readonly_fields() -> None:
    """Test our `TypedDict` support with `ReadOnly` fields."""
    code = """
        from typing import TypedDict
        from typing_extensions import ReadOnly, Required, NotRequired

        class Kwargs(TypedDict):
            a: ReadOnly[int]
            '''Docstring for a.'''
            b: ReadOnly[Required[str]]
            '''Docstring for b.'''
            c: Required[ReadOnly[float]]
            '''Docstring for c.'''
    """
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code},
        extensions=load_extensions("unpack_typeddict"),
        docstring_parser="google",
    ) as pkg:
        td = pkg["Kwargs"]

    # Signature of the `__init__` method.
    assert "__init__" in td.members
    init = td["__init__"]
    assert len(init.parameters) == 4
    assert "self" in init.parameters
    assert "a" in init.parameters
    assert "b" in init.parameters
    assert "c" in init.parameters
    assert str(init.parameters["a"].annotation) == "int"
    assert str(init.parameters["b"].annotation) == "str"
    assert str(init.parameters["c"].annotation) == "float"
    assert init.parameters["a"].docstring.value == "Docstring for a."
    assert init.parameters["b"].docstring.value == "Docstring for b."
    assert init.parameters["c"].docstring.value == "Docstring for c."
    assert init.returns == "None"
