from _griffe.enumerations import ParameterKind
from _griffe.loader import load
from _griffe.models import Function, Parameter, Parameters


def test_construct_signature():
    # Start the test with a simple function
    simple_params = Parameters(
        Parameter("x", annotation="int"),
        Parameter("y", annotation="int", default="0")
    )

    simple_func = Function(
        "simple_function",
        parameters=simple_params,
        returns="int"
    )

    simple_signature = simple_func.construct_signature()
    print(f"{simple_signature=}")

    simple_expected = "simple_function(x: int, y: int = 0) -> int"
    assert simple_signature == simple_expected, f"Expected: {simple_expected}\nGot: {simple_signature}"

    # Create a more complex function with various parameter types
    params = Parameters(
        Parameter("a", kind=ParameterKind.positional_only),
        Parameter("b", kind=ParameterKind.positional_only, annotation="int", default="0"),
        Parameter("c", kind=ParameterKind.positional_or_keyword),
        Parameter("d", kind=ParameterKind.positional_or_keyword, annotation="str", default="''"),
        Parameter("args", kind=ParameterKind.var_positional),
        Parameter("e", kind=ParameterKind.keyword_only),
        Parameter("f", kind=ParameterKind.keyword_only, annotation="bool", default="False"),
        Parameter("kwargs", kind=ParameterKind.var_keyword)
    )

    func = Function(
        "test_function",
        parameters=params,
        returns="None"
    )

    # Get the signature
    signature = func.construct_signature()
    print(f"{signature=}")

    expected = "test_function(a, b: int = 0, /, c, d: str = '', *args, e, f: bool = False, **kwargs) -> None"
    assert signature == expected, f"Expected: {expected}\nGot: {signature}"

    function_cls = load("_griffe.models.Function")
    mod_signature = function_cls["construct_signature"].construct_signature()
    print(f"{mod_signature=}")
    assert mod_signature == "construct_signature() -> str"


if __name__ == "__main__":
    test_construct_signature()
