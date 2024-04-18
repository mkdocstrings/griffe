from griffe.dataclasses import Object
from griffe.expressions import ExprName
from griffe.tests import temporary_visited_module


with temporary_visited_module(
    """
    from enum import Enum

    class MyEnum(Enum):
        MY_FIELD = "hello"

    my_fields = [MyEnum.MY_FIELD.value]
    """,
) as module:
    expression = module["my_fields"].value


attribute = expression.elements[0]
print(attribute.last.parent.is_enum_value)
