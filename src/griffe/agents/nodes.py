"""This module contains utilities for extracting information from nodes."""

from __future__ import annotations

import enum
import inspect
import sys
from ast import AST
from ast import Add as NodeAdd
from ast import And as NodeAnd
from ast import AnnAssign as NodeAnnAssign
from ast import Assign as NodeAssign
from ast import Attribute as NodeAttribute
from ast import AugAssign as NodeAugAssign
from ast import BinOp as NodeBinOp
from ast import BitAnd as NodeBitAnd
from ast import BitOr as NodeBitOr
from ast import BitXor as NodeBitXor
from ast import BoolOp as NodeBoolOp
from ast import Call as NodeCall
from ast import Compare as NodeCompare
from ast import Constant as NodeConstant
from ast import Dict as NodeDict
from ast import DictComp as NodeDictComp
from ast import Div as NodeDiv
from ast import Ellipsis as NodeEllipsis
from ast import Eq as NodeEq
from ast import Expr as NodeExpr
from ast import FloorDiv as NodeFloorDiv
from ast import FormattedValue as NodeFormattedValue
from ast import GeneratorExp as NodeGeneratorExp
from ast import Gt as NodeGt
from ast import GtE as NodeGtE
from ast import IfExp as NodeIfExp
from ast import ImportFrom as NodeImportFrom
from ast import In as NodeIn
from ast import Invert as NodeInvert
from ast import Is as NodeIs
from ast import IsNot as NodeIsNot
from ast import JoinedStr as NodeJoinedStr
from ast import Lambda as NodeLambda
from ast import List as NodeList
from ast import ListComp as NodeListComp
from ast import LShift as NodeLShift
from ast import Lt as NodeLt
from ast import LtE as NodeLtE
from ast import MatMult as NodeMatMult
from ast import Mod as NodeMod
from ast import Mult as NodeMult
from ast import Name as NodeName
from ast import Not as NodeNot
from ast import NotEq as NodeNotEq
from ast import NotIn as NodeNotIn
from ast import Num as NodeNum
from ast import Or as NodeOr
from ast import Pow as NodePow
from ast import RShift as NodeRShift
from ast import Set as NodeSet
from ast import SetComp as NodeSetComp
from ast import Slice as NodeSlice
from ast import Starred as NodeStarred
from ast import Str as NodeStr
from ast import Sub as NodeSub
from ast import Subscript as NodeSubscript
from ast import Tuple as NodeTuple
from ast import UAdd as NodeUAdd
from ast import UnaryOp as NodeUnaryOp
from ast import USub as NodeUSub
from ast import Yield as NodeYield
from ast import alias as NodeAlias
from ast import arguments as NodeArguments
from ast import comprehension as NodeComprehension
from ast import keyword as NodeKeyword
from contextlib import suppress
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Sequence, Type

from griffe.collections import LinesCollection
from griffe.exceptions import LastNodeError, RootNodeError
from griffe.expressions import Expression, Name
from griffe.logger import LogLevel, get_logger

logger = get_logger(__name__)

# TODO: remove once Python 3.7 support is dropped
if sys.version_info < (3, 8):
    from ast import Bytes as NodeBytes
    from ast import NameConstant as NodeNameConstant

    from cached_property import cached_property
else:
    from functools import cached_property  # noqa: WPS440

# TODO: remove once Python 3.8 support is dropped
if sys.version_info < (3, 9):
    from ast import ExtSlice as NodeExtSlice
    from ast import Index as NodeIndex

if TYPE_CHECKING:
    from griffe.dataclasses import Class, Module


class ASTNode:
    """This class is dynamically added to the bases of each AST node class."""

    parent: ASTNode

    # TODO: remove once Python 3.7 support is dropped
    if sys.version_info < (3, 8):  # noqa: WPS604
        end_lineno = property(lambda node: None)

    @cached_property
    def kind(self) -> str:
        """Return the kind of this node.

        Returns:
            The node kind.
        """
        return self.__class__.__name__.lower()

    @cached_property  # noqa: WPS231
    def children(self) -> Sequence[ASTNode]:  # noqa: WPS231
        """Build and return the children of this node.

        Returns:
            A list of children.
        """
        children = []
        for field_name in self._fields:  # type: ignore[attr-defined]  # noqa: WPS437
            try:
                field = getattr(self, field_name)
            except AttributeError:
                continue
            if isinstance(field, ASTNode):
                field.parent = self
                children.append(field)
            elif isinstance(field, list):
                for child in field:
                    if isinstance(child, ASTNode):
                        child.parent = self
                        children.append(child)
        return children

    @cached_property
    def position(self) -> int:
        """Tell the position of this node amongst its siblings.

        Raises:
            RootNodeError: When the node doesn't have a parent.

        Returns:
            The node position amongst its siblings.
        """
        try:
            return self.parent.children.index(self)
        except AttributeError as error:
            raise RootNodeError("the root node does not have a parent, nor siblings, nor a position") from error

    @cached_property
    def previous_siblings(self) -> Sequence[ASTNode]:
        """Return the previous siblings of this node, starting from the closest.

        Returns:
            The previous siblings.
        """
        if self.position == 0:
            return []
        return self.parent.children[self.position - 1 :: -1]

    @cached_property
    def next_siblings(self) -> Sequence[ASTNode]:
        """Return the next siblings of this node, starting from the closest.

        Returns:
            The next siblings.
        """
        if self.position == len(self.parent.children) - 1:
            return []
        return self.parent.children[self.position + 1 :]

    @cached_property
    def siblings(self) -> Sequence[ASTNode]:
        """Return the siblings of this node.

        Returns:
            The siblings.
        """
        return [*reversed(self.previous_siblings), *self.next_siblings]

    @cached_property
    def previous(self) -> ASTNode:
        """Return the previous sibling of this node.

        Raises:
            LastNodeError: When the node does not have previous siblings.

        Returns:
            The sibling.
        """
        try:
            return self.previous_siblings[0]
        except IndexError as error:
            raise LastNodeError("there is no previous node") from error

    @cached_property  # noqa: A003
    def next(self) -> ASTNode:  # noqa: A003
        """Return the next sibling of this node.

        Raises:
            LastNodeError: When the node does not have next siblings.

        Returns:
            The sibling.
        """
        try:
            return self.next_siblings[0]
        except IndexError as error:
            raise LastNodeError("there is no next node") from error

    @cached_property
    def first_child(self) -> ASTNode:
        """Return the first child of this node.

        Raises:
            LastNodeError: When the node does not have children.

        Returns:
            The child.
        """
        try:
            return self.children[0]
        except IndexError as error:
            raise LastNodeError("there are no children node") from error

    @cached_property
    def last_child(self) -> ASTNode:  # noqa: A003
        """Return the lasts child of this node.

        Raises:
            LastNodeError: When the node does not have children.

        Returns:
            The child.
        """
        try:
            return self.children[-1]
        except IndexError as error:
            raise LastNodeError("there are no children node") from error


class ObjectKind(enum.Enum):
    """Enumeration for the different kinds of objects."""

    MODULE: str = "module"
    CLASS: str = "class"
    STATICMETHOD: str = "staticmethod"
    CLASSMETHOD: str = "classmethod"
    METHOD_DESCRIPTOR: str = "method_descriptor"
    METHOD: str = "method"
    BUILTIN_METHOD: str = "builtin_method"
    COROUTINE: str = "coroutine"
    FUNCTION: str = "function"
    BUILTIN_FUNCTION: str = "builtin_function"
    CACHED_PROPERTY: str = "cached_property"
    PROPERTY: str = "property"
    ATTRIBUTE: str = "attribute"

    def __str__(self) -> str:
        return self.value


class ObjectNode:
    """Helper class to represent an object tree.

    It's not really a tree but more a backward-linked list:
    each node has a reference to its parent, but not to its child (for simplicity purposes and to avoid bugs).

    Each node stores an object, its name, and a reference to its parent node.

    Attributes:
        obj: The actual Python object.
        name: The Python object's name.
        parent: The parent node.
    """

    # low level stuff known to cause issues when resolving aliases
    exclude_specials = {"__builtins__", "__loader__", "__spec__"}

    def __init__(self, obj: Any, name: str, parent: ObjectNode | None = None) -> None:
        """
        Initialize the object.

        Arguments:
            obj: A Python object.
            name: The object's name.
            parent: The object's parent node.
        """
        try:
            obj = inspect.unwrap(obj)
        except Exception:  # noqa: S110,W0703 (we purposely catch every possible exception)
            # inspect.unwrap at some point runs hasattr(obj, "__wrapped__"),
            # which triggers the __getattr__ method of the object, which in
            # turn can raise various exceptions. Probably not just __getattr__.
            # See https://github.com/pawamoy/pytkdocs/issues/45
            pass  # noqa: WPS420 (no other way than passing)

        self.obj: Any = obj
        self.name: str = name
        self.parent: ObjectNode | None = parent

    def __repr__(self) -> str:
        return f"ObjectNode(name={self.name!r})"

    @cached_property
    def kind(self) -> ObjectKind:
        """Return the kind of this node.

        Returns:
            The node kind.
        """
        if self.is_module:
            return ObjectKind.MODULE
        if self.is_class:
            return ObjectKind.CLASS
        if self.is_staticmethod:
            return ObjectKind.STATICMETHOD
        if self.is_classmethod:
            return ObjectKind.CLASSMETHOD
        if self.is_method:
            return ObjectKind.METHOD
        if self.is_builtin_method:
            return ObjectKind.BUILTIN_METHOD
        if self.is_coroutine:
            return ObjectKind.COROUTINE
        if self.is_function:
            return ObjectKind.FUNCTION
        if self.is_builtin_function:
            return ObjectKind.BUILTIN_FUNCTION
        if self.is_cached_property:
            return ObjectKind.CACHED_PROPERTY
        if self.is_property:
            return ObjectKind.PROPERTY
        if self.is_method_descriptor:
            return ObjectKind.METHOD_DESCRIPTOR
        return ObjectKind.ATTRIBUTE

    @cached_property
    def children(self) -> Sequence[ObjectNode]:  # noqa: WPS231
        """Build and return the children of this node.

        Returns:
            A list of children.
        """
        children = []
        for name, member in inspect.getmembers(self.obj):
            if self._pick_member(name, member):
                children.append(ObjectNode(member, name, parent=self))
        return children

    @cached_property
    def is_module(self) -> bool:
        """
        Tell if this node's object is a module.

        Returns:
            The root of the tree.
        """
        return inspect.ismodule(self.obj)

    @cached_property
    def is_class(self) -> bool:
        """
        Tell if this node's object is a class.

        Returns:
            If this node's object is a class.
        """
        return inspect.isclass(self.obj)

    @cached_property
    def is_function(self) -> bool:
        """
        Tell if this node's object is a function.

        Returns:
            If this node's object is a function.
        """
        return inspect.isfunction(self.obj)

    @cached_property
    def is_builtin_function(self) -> bool:
        """
        Tell if this node's object is a builtin function.

        Returns:
            If this node's object is a builtin function.
        """
        return inspect.isbuiltin(self.obj)

    @cached_property
    def is_coroutine(self) -> bool:
        """
        Tell if this node's object is a coroutine.

        Returns:
            If this node's object is a coroutine.
        """
        return inspect.iscoroutinefunction(self.obj)

    @cached_property
    def is_property(self) -> bool:
        """
        Tell if this node's object is a property.

        Returns:
            If this node's object is a property.
        """
        return isinstance(self.obj, property) or self.is_cached_property

    @cached_property
    def is_cached_property(self) -> bool:
        """
        Tell if this node's object is a cached property.

        Returns:
            If this node's object is a cached property.
        """
        return isinstance(self.obj, cached_property)

    @cached_property
    def parent_is_class(self) -> bool:
        """
        Tell if the object of this node's parent is a class.

        Returns:
            If the object of this node's parent is a class.
        """
        return bool(self.parent and self.parent.is_class)

    @cached_property
    def is_method(self) -> bool:
        """
        Tell if this node's object is a method.

        Returns:
            If this node's object is a method.
        """
        function_type = type(lambda: None)
        return self.parent_is_class and isinstance(self.obj, function_type)

    @cached_property
    def is_method_descriptor(self) -> bool:
        """
        Tell if this node's object is a method descriptor.

        Built-in methods (e.g. those implemented in C/Rust) are often
        method descriptors, rather than normal methods.

        Returns:
            If this node's object is a method descriptor.
        """
        return inspect.ismethoddescriptor(self.obj)

    @cached_property
    def is_builtin_method(self) -> bool:
        """
        Tell if this node's object is a builtin method.

        Returns:
            If this node's object is a builtin method.
        """
        return self.is_builtin_function and self.parent_is_class

    @cached_property
    def is_staticmethod(self) -> bool:
        """
        Tell if this node's object is a staticmethod.

        Returns:
            If this node's object is a staticmethod.
        """
        if self.parent is None:
            return False
        try:
            self_from_parent = self.parent.obj.__dict__.get(self.name, None)  # noqa: WPS609
        except AttributeError:
            return False
        return self.parent_is_class and isinstance(self_from_parent, staticmethod)

    @cached_property
    def is_classmethod(self) -> bool:
        """
        Tell if this node's object is a classmethod.

        Returns:
            If this node's object is a classmethod.
        """
        if self.parent is None:
            return False
        try:
            self_from_parent = self.parent.obj.__dict__.get(self.name, None)  # noqa: WPS609
        except AttributeError:
            return False
        return self.parent_is_class and isinstance(self_from_parent, classmethod)

    @cached_property
    def _ids(self) -> set[int]:
        if self.parent is None:
            return {id(self.obj)}
        return {id(self.obj)} | self.parent._ids  # noqa: WPS437

    def _pick_member(self, name: str, member: Any) -> bool:
        return (
            name not in self.exclude_specials
            and member is not type
            and member is not object
            and id(member) not in self._ids
        )


def _join(sequence, item):
    if not sequence:
        return []
    new_sequence = [sequence[0]]
    for element in sequence[1:]:
        new_sequence.extend((item, element))
    return new_sequence


def _parse__all__constant(node: NodeConstant, parent: Module) -> list[str]:
    try:
        return [node.value]
    except AttributeError:
        return [node.s]  # TODO: remove once Python 3.7 is dropped


def _parse__all__name(node: NodeName, parent: Module) -> list[Name]:
    return [Name(node.id, partial(parent.resolve, node.id))]


def _parse__all__starred(node: NodeStarred, parent: Module) -> list[str | Name]:
    return _parse__all__(node.value, parent)


def _parse__all__sequence(node: NodeList | NodeSet | NodeTuple, parent: Module) -> list[str | Name]:
    sequence = []
    for elt in node.elts:
        sequence.extend(_parse__all__(elt, parent))
    return sequence


def _parse__all__binop(node: NodeBinOp, parent: Module) -> list[str | Name]:
    left = _parse__all__(node.left, parent)
    right = _parse__all__(node.right, parent)
    return left + right


_node__all__map: dict[Type, Callable[[Any, Module], list[str | Name]]] = {  # noqa: WPS234
    NodeConstant: _parse__all__constant,  # type: ignore[dict-item]
    NodeName: _parse__all__name,  # type: ignore[dict-item]
    NodeStarred: _parse__all__starred,
    NodeList: _parse__all__sequence,
    NodeSet: _parse__all__sequence,
    NodeTuple: _parse__all__sequence,
    NodeBinOp: _parse__all__binop,
}

# TODO: remove once Python 3.7 support is dropped
if sys.version_info < (3, 8):

    def _parse__all__nameconstant(node: NodeNameConstant, parent: Module) -> list[Name]:
        return [node.value]

    def _parse__all__str(node: NodeStr, parent: Module) -> list[str]:
        return [node.s]

    _node__all__map[NodeNameConstant] = _parse__all__nameconstant  # type: ignore[assignment]
    _node__all__map[NodeStr] = _parse__all__str  # type: ignore[assignment]


def _parse__all__(node: AST, parent: Module) -> list[str | Name]:
    return _node__all__map[type(node)](node, parent)


def parse__all__(node: NodeAssign | NodeAugAssign, parent: Module) -> list[str | Name]:  # noqa: WPS120,WPS440
    """Get the values declared in `__all__`.

    Parameters:
        node: The assignment node.
        parent: The parent module.

    Returns:
        A set of names.
    """
    try:
        return _parse__all__(node.value, parent)
    except KeyError as error:
        logger.debug(f"Cannot parse __all__ assignment: {get_value(node.value)} ({error})")
        return []


# ==========================================================
# annotations
def _get_attribute_annotation(node: NodeAttribute, parent: Module | Class) -> Expression:
    left = _get_annotation(node.value, parent)

    def resolver():  # noqa: WPS430
        return f"{left.full}.{node.attr}"

    right = Name(node.attr, resolver)
    return Expression(left, ".", right)


def _get_binop_annotation(node: NodeBinOp, parent: Module | Class) -> Expression:
    left = _get_annotation(node.left, parent)
    right = _get_annotation(node.right, parent)
    return Expression(left, _get_annotation(node.op, parent), right)


def _get_bitand_annotation(node: NodeBitAnd, parent: Module | Class) -> str:
    return " & "


def _get_bitor_annotation(node: NodeBitOr, parent: Module | Class) -> str:
    return " | "


def _get_call_annotation(node: NodeCall, parent: Module | Class) -> Expression:
    posargs = Expression(*_join([_get_annotation(arg, parent) for arg in node.args], ", "))
    kwargs = Expression(*_join([_get_annotation(kwarg, parent) for kwarg in node.keywords], ", "))
    args: Expression | str
    if posargs and kwargs:
        args = Expression(posargs, ", ", kwargs)
    elif posargs:
        args = posargs
    elif kwargs:
        args = kwargs
    else:
        args = ""
    return Expression(_get_annotation(node.func, parent), "(", args, ")")


def _get_constant_annotation(node: NodeConstant, parent: Module | Class) -> str | Name:
    if isinstance(node.value, str):
        node.id = node.value  # type: ignore[attr-defined]  # fake node as Name
        return _get_name_annotation(node, parent)  # type: ignore[arg-type]
    return _get_literal_annotation(node, parent)


def _get_literal_annotation(node: NodeConstant, parent: Module | Class) -> str:
    return {type(...): lambda _: "..."}.get(type(node.value), repr)(node.value)


def _get_ellipsis_annotation(node: NodeEllipsis, parent: Module | Class) -> str:
    return "..."


def _get_ifexp_annotation(node: NodeIfExp, parent: Module | Class) -> Expression:
    return Expression(
        _get_annotation(node.body, parent),
        " if ",
        _get_annotation(node.test, parent),
        " else",
        _get_annotation(node.orelse, parent),
    )


def _get_invert_annotation(node: NodeInvert, parent: Module | Class) -> str:
    return "~"


def _get_keyword_annotation(node: NodeKeyword, parent: Module | Class) -> Expression:
    return Expression(f"{node.arg}=", _get_annotation(node.value, parent))


def _get_list_annotation(node: NodeList, parent: Module | Class) -> Expression:
    return Expression("[", *_join([_get_annotation(el, parent) for el in node.elts], ", "), "]")


def _get_name_annotation(node: NodeName, parent: Module | Class) -> Name:
    return Name(node.id, partial(parent.resolve, node.id))


def _get_subscript_annotation(node: NodeSubscript, parent: Module | Class) -> Expression:
    left = _get_annotation(node.value, parent)
    if left.full == "typing.Literal":  # type: ignore[union-attr]
        _node_annotation_map[NodeConstant] = _get_literal_annotation
        subscript = _get_annotation(node.slice, parent)
        _node_annotation_map[NodeConstant] = _get_constant_annotation
    else:
        subscript = _get_annotation(node.slice, parent)
    return Expression(left, "[", subscript, "]")


def _get_tuple_annotation(node: NodeTuple, parent: Module | Class) -> Expression:
    return Expression(*_join([_get_annotation(el, parent) for el in node.elts], ", "))


def _get_unaryop_annotation(node: NodeUnaryOp, parent: Module | Class) -> Expression:
    return Expression(_get_annotation(node.op, parent), _get_annotation(node.operand, parent))


def _get_uadd_annotation(node: NodeUAdd, parent: Module | Class) -> str:
    return "+"


def _get_usub_annotation(node: NodeUSub, parent: Module | Class) -> str:
    return "-"


_node_annotation_map: dict[Type, Callable[[Any, Module | Class], str | Name | Expression]] = {
    NodeAttribute: _get_attribute_annotation,
    NodeBinOp: _get_binop_annotation,
    NodeBitAnd: _get_bitand_annotation,
    NodeBitOr: _get_bitor_annotation,
    NodeCall: _get_call_annotation,
    NodeConstant: _get_constant_annotation,
    NodeEllipsis: _get_ellipsis_annotation,
    NodeIfExp: _get_ifexp_annotation,
    NodeInvert: _get_invert_annotation,
    NodeKeyword: _get_keyword_annotation,
    NodeList: _get_list_annotation,
    NodeName: _get_name_annotation,
    NodeSubscript: _get_subscript_annotation,
    NodeTuple: _get_tuple_annotation,
    NodeUnaryOp: _get_unaryop_annotation,
    NodeUAdd: _get_uadd_annotation,
    NodeUSub: _get_usub_annotation,
}

# TODO: remove once Python 3.8 support is dropped
if sys.version_info < (3, 9):

    def _get_index_annotation(node: NodeIndex, parent: Module | Class) -> str | Name | Expression:
        return _get_annotation(node.value, parent)

    _node_annotation_map[NodeIndex] = _get_index_annotation

# TODO: remove once Python 3.7 support is dropped
if sys.version_info < (3, 8):

    def _get_bytes_annotation(node: NodeBytes, parent: Module | Class) -> str:
        return repr(node.s)

    def _get_nameconstant_annotation(node: NodeNameConstant, parent: Module | Class) -> str:
        return repr(node.value)

    def _get_num_annotation(node: NodeNum, parent: Module | Class) -> str:
        return repr(node.n)

    def _get_str_annotation(node: NodeStr, parent: Module | Class) -> str | Name:
        node.value = node.s  # type: ignore[attr-defined]  # fake node as constant
        return _node_annotation_map[NodeConstant](node, parent)  # type: ignore[return-value]

    _node_annotation_map[NodeBytes] = _get_bytes_annotation
    _node_annotation_map[NodeNameConstant] = _get_nameconstant_annotation
    _node_annotation_map[NodeNum] = _get_num_annotation
    _node_annotation_map[NodeStr] = _get_str_annotation


def _get_annotation(node: AST, parent: Module | Class) -> str | Name | Expression:
    return _node_annotation_map[type(node)](node, parent)


def get_annotation(node: AST | None, parent: Module | Class) -> str | Name | Expression | None:
    """Extract a resolvable annotation.

    Parameters:
        node: The annotation node.
        parent: The parent used to resolve the name.

    Returns:
        A string or resovable name or expression.
    """
    if node is None:
        return None
    return _get_annotation(node, parent)


def safe_get_annotation(
    node: AST | None,
    parent: Module | Class,
    log_level: LogLevel = LogLevel.error,
) -> str | Name | Expression | None:
    """Safely (no exception) extract a resolvable annotation.

    Parameters:
        node: The annotation node.
        parent: The parent used to resolve the name.
        log_level: Log level to use to log a message.

    Returns:
        A string or resovable name or expression.
    """
    try:
        return get_annotation(node, parent)
    except Exception as error:
        message = f"Failed to parse annotation from '{node.__class__.__name__}' node"
        with suppress(Exception):
            message += f" at {parent.relative_filepath}:{node.lineno}"  # type: ignore[union-attr]
        if not isinstance(error, KeyError):
            message += f": {error}"
        getattr(logger, log_level.value)(message)
        return None


# ==========================================================
# docstrings
def get_docstring(
    node: AST,
    strict: bool = False,
) -> tuple[str | None, int | None, int | None]:
    """Extract a docstring.

    Parameters:
        node: The node to extract the docstring from.
        strict: Whether to skip searching the body (functions).

    Returns:
        A tuple with the value and line numbers of the docstring.
    """
    # TODO: possible optimization using a type map
    if isinstance(node, NodeExpr):
        doc = node.value
    elif node.body and isinstance(node.body[0], NodeExpr) and not strict:  # type: ignore[attr-defined]
        doc = node.body[0].value  # type: ignore[attr-defined]
    else:
        return None, None, None
    if isinstance(doc, NodeConstant) and isinstance(doc.value, str):
        return doc.value, doc.lineno, doc.end_lineno  # type: ignore[attr-defined]
    if isinstance(doc, NodeStr):

        # TODO: remove once Python 3.7 support is dropped
        # on Python 3.7, lineno seems to be the ending line of the string
        # rather than the starting one, so we substract the number of newlines
        lineno = doc.lineno
        if sys.version_info < (3, 8):
            lineno -= doc.s.count("\n")

        return doc.s, lineno, doc.end_lineno  # type: ignore[attr-defined]
    return None, None, None


# ==========================================================
# values
def _get_add_value(node: NodeAdd) -> str:
    return "+"


def _get_and_value(node: NodeAnd) -> str:
    return " and "


def _get_arguments_value(node: NodeArguments) -> str:
    return ", ".join(arg.arg for arg in node.args)


def _get_attribute_value(node: NodeAttribute) -> str:
    return f"{_get_value(node.value)}.{node.attr}"


def _get_binop_value(node: NodeBinOp) -> str:
    return f"{_get_value(node.left)} {_get_value(node.op)} {_get_value(node.right)}"


def _get_bitor_value(node: NodeBitOr) -> str:
    return "|"


def _get_bitand_value(node: NodeBitAnd) -> str:
    return "&"


def _get_bitxor_value(node: NodeBitXor) -> str:
    return "^"


def _get_boolop_value(node: NodeBoolOp) -> str:
    return _get_value(node.op).join(_get_value(value) for value in node.values)


def _get_call_value(node: NodeCall) -> str:
    posargs = ", ".join(_get_value(arg) for arg in node.args)
    kwargs = ", ".join(_get_value(kwarg) for kwarg in node.keywords)
    if posargs and kwargs:
        args = f"{posargs}, {kwargs}"
    elif posargs:
        args = posargs
    elif kwargs:
        args = kwargs
    else:
        args = ""
    return f"{_get_value(node.func)}({args})"


def _get_compare_value(node: NodeCompare) -> str:
    left = _get_value(node.left)
    ops = [_get_value(op) for op in node.ops]
    comparators = [_get_value(comparator) for comparator in node.comparators]
    return f"{left} " + " ".join(f"{op} {comp}" for op, comp in zip(ops, comparators))


def _get_comprehension_value(node: NodeComprehension) -> str:
    target = _get_value(node.target)
    iterable = _get_value(node.iter)
    conditions = [_get_value(condition) for condition in node.ifs]
    value = f"for {target} in {iterable}"
    if conditions:
        value = f"{value} if " + " if ".join(conditions)
    if node.is_async:
        value = f"async {value}"
    return value


def _get_constant_value(node: NodeConstant) -> str:
    return repr(node.value)


def _get_constant_value_no_string_repr(node: NodeConstant) -> str:
    if isinstance(node.value, str):
        return node.value
    return repr(node.value)


def _get_dict_value(node: NodeDict) -> str:
    pairs = zip(node.keys, node.values)
    gen = (f"{'None' if key is None else _get_value(key)}: {_get_value(value)}" for key, value in pairs)  # noqa: WPS509
    return "{" + ", ".join(gen) + "}"


def _get_dictcomp_value(node: NodeDictComp) -> str:
    key = _get_value(node.key)
    value = _get_value(node.value)
    generators = [_get_value(gen) for gen in node.generators]
    return f"{{{key}: {value} " + " ".join(generators) + "}"


def _get_div_value(node: NodeDiv) -> str:
    return "/"


def _get_ellipsis_value(node: NodeEllipsis) -> str:
    return "..."


def _get_eq_value(node: NodeEq) -> str:
    return "=="


def _get_floordiv_value(node: NodeFloorDiv) -> str:
    return "//"


def _get_formatted_value(node: NodeFormattedValue) -> str:
    return f"{{{_get_value(node.value)}}}"


def _get_generatorexp_value(node: NodeGeneratorExp) -> str:
    element = _get_value(node.elt)
    generators = [_get_value(gen) for gen in node.generators]
    return f"{element} " + " ".join(generators)


def _get_gte_value(node: NodeNotEq) -> str:
    return ">="


def _get_gt_value(node: NodeNotEq) -> str:
    return ">"


def _get_ifexp_value(node: NodeIfExp) -> str:
    return f"{_get_value(node.body)} if {_get_value(node.test)} else {_get_value(node.orelse)}"


def _get_invert_value(node: NodeInvert) -> str:
    return "~"


def _get_in_value(node: NodeIn) -> str:
    return "in"


def _get_is_value(node: NodeIs) -> str:
    return "is"


def _get_isnot_value(node: NodeIsNot) -> str:
    return "is not"


def _get_joinedstr_value(node: NodeJoinedStr) -> str:
    _node_value_map[NodeConstant] = _get_constant_value_no_string_repr
    result = "f" + repr("".join(_get_value(value) for value in node.values))
    _node_value_map[NodeConstant] = _get_constant_value
    return result


def _get_keyword_value(node: NodeKeyword) -> str:
    return f"{node.arg}={_get_value(node.value)}"


def _get_lambda_value(node: NodeLambda) -> str:
    return f"lambda {_get_value(node.args)}: {_get_value(node.body)}"


def _get_list_value(node: NodeList) -> str:
    return "[" + ", ".join(_get_value(el) for el in node.elts) + "]"


def _get_listcomp_value(node: NodeListComp) -> str:
    element = _get_value(node.elt)
    generators = [_get_value(gen) for gen in node.generators]
    return f"[{element} " + " ".join(generators) + "]"


def _get_lshift_value(node: NodeLShift) -> str:
    return "<<"


def _get_lte_value(node: NodeNotEq) -> str:
    return "<="


def _get_lt_value(node: NodeNotEq) -> str:
    return "<"


def _get_matmult_value(node: NodeMatMult) -> str:
    return "@"


def _get_mod_value(node: NodeMod) -> str:
    return "%"


def _get_mult_value(node: NodeMult) -> str:
    return "*"


def _get_name_value(node: NodeName) -> str:
    return node.id


def _get_not_value(node: NodeNot) -> str:
    return "not "


def _get_noteq_value(node: NodeNotEq) -> str:
    return "!="


def _get_notin_value(node: NodeNotIn) -> str:
    return "not in"


def _get_or_value(node: NodeOr) -> str:
    return " or "


def _get_pow_value(node: NodePow) -> str:
    return "**"


def _get_rshift_value(node: NodeRShift) -> str:
    return ">>"


def _get_set_value(node: NodeSet) -> str:
    return "{" + ", ".join(_get_value(el) for el in node.elts) + "}"


def _get_setcomp_value(node: NodeSetComp) -> str:
    element = _get_value(node.elt)
    generators = [_get_value(gen) for gen in node.generators]
    return f"{{{element} " + " ".join(generators) + "}"


def _get_slice_value(node: NodeSlice) -> str:
    value = f"{_get_value(node.lower) if node.lower else ''}:{_get_value(node.upper) if node.upper else ''}"
    if node.step:
        value = f"{value}:{_get_value(node.step)}"
    return value


def _get_starred_value(node: NodeStarred) -> str:
    return _get_value(node.value)


def _get_sub_value(node: NodeSub) -> str:
    return "-"


def _get_subscript_value(node: NodeSubscript) -> str:
    subscript = _get_value(node.slice)
    if isinstance(subscript, str) and subscript.startswith("(") and subscript.endswith(")"):
        subscript = subscript[1:-1]
    return f"{_get_value(node.value)}[{subscript}]"


def _get_tuple_value(node: NodeTuple) -> str:
    return "(" + ", ".join(_get_value(el) for el in node.elts) + ")"


def _get_uadd_value(node: NodeUAdd) -> str:
    return "+"


def _get_unaryop_value(node: NodeUnaryOp) -> str:
    return f"{_get_value(node.op)}{_get_value(node.operand)}"


def _get_usub_value(node: NodeUSub) -> str:
    return "-"


def _get_yield_value(node: NodeYield) -> str:
    if node.value is None:
        return repr(None)
    return _get_value(node.value)


_node_value_map: dict[Type, Callable[[Any], str]] = {
    # type(None): lambda _: repr(None),
    NodeAdd: _get_add_value,
    NodeAnd: _get_and_value,
    NodeArguments: _get_arguments_value,
    NodeAttribute: _get_attribute_value,
    NodeBinOp: _get_binop_value,
    NodeBitAnd: _get_bitand_value,
    NodeBitOr: _get_bitor_value,
    NodeBitXor: _get_bitxor_value,
    NodeBoolOp: _get_boolop_value,
    NodeCall: _get_call_value,
    NodeCompare: _get_compare_value,
    NodeComprehension: _get_comprehension_value,
    NodeConstant: _get_constant_value,
    NodeDictComp: _get_dictcomp_value,
    NodeDict: _get_dict_value,
    NodeDiv: _get_div_value,
    NodeEllipsis: _get_ellipsis_value,
    NodeEq: _get_eq_value,
    NodeFloorDiv: _get_floordiv_value,
    NodeFormattedValue: _get_formatted_value,
    NodeGeneratorExp: _get_generatorexp_value,
    NodeGtE: _get_gte_value,
    NodeGt: _get_gt_value,
    NodeIfExp: _get_ifexp_value,
    NodeIn: _get_in_value,
    NodeInvert: _get_invert_value,
    NodeIs: _get_is_value,
    NodeIsNot: _get_isnot_value,
    NodeJoinedStr: _get_joinedstr_value,
    NodeKeyword: _get_keyword_value,
    NodeLambda: _get_lambda_value,
    NodeListComp: _get_listcomp_value,
    NodeList: _get_list_value,
    NodeLShift: _get_lshift_value,
    NodeLtE: _get_lte_value,
    NodeLt: _get_lt_value,
    NodeMatMult: _get_matmult_value,
    NodeMod: _get_mod_value,
    NodeMult: _get_mult_value,
    NodeName: _get_name_value,
    NodeNotEq: _get_noteq_value,
    NodeNot: _get_not_value,
    NodeNotIn: _get_notin_value,
    NodeOr: _get_or_value,
    NodePow: _get_pow_value,
    NodeRShift: _get_rshift_value,
    NodeSetComp: _get_setcomp_value,
    NodeSet: _get_set_value,
    NodeSlice: _get_slice_value,
    NodeStarred: _get_starred_value,
    NodeSub: _get_sub_value,
    NodeSubscript: _get_subscript_value,
    NodeTuple: _get_tuple_value,
    NodeUAdd: _get_uadd_value,
    NodeUnaryOp: _get_unaryop_value,
    NodeUSub: _get_usub_value,
    NodeYield: _get_yield_value,
}

# TODO: remove once Python 3.8 support is dropped
if sys.version_info < (3, 9):

    def _get_extslice_value(node: NodeExtSlice) -> str:
        return ",".join(_get_value(dim) for dim in node.dims)

    def _get_index_value(node: NodeIndex) -> str:
        return _get_value(node.value)

    _node_value_map[NodeExtSlice] = _get_extslice_value
    _node_value_map[NodeIndex] = _get_index_value


# TODO: remove once Python 3.7 support is dropped
if sys.version_info < (3, 8):

    def _get_bytes_value(node: NodeBytes) -> str:
        return repr(node.s)

    def _get_nameconstant_value(node: NodeNameConstant) -> str:
        return repr(node.value)

    def _get_num_value(node: NodeNum) -> str:
        return repr(node.n)

    def _get_str_value(node: NodeStr) -> str:
        return repr(node.s)

    _node_value_map[NodeBytes] = _get_bytes_value
    _node_value_map[NodeNameConstant] = _get_nameconstant_value
    _node_value_map[NodeNum] = _get_num_value
    _node_value_map[NodeStr] = _get_str_value


def _get_value(node: AST) -> str:
    return _node_value_map[type(node)](node)


def get_value(node: AST | None) -> str | None:
    """Unparse a node to its string representation.

    Parameters:
        node: The node to unparse.

    Returns:
        The unparsed code of the node.
    """
    if node is None:
        return None
    return _node_value_map[type(node)](node)


def safe_get_value(node: AST | None, filepath: str | Path | None = None) -> str | None:
    """Safely (no exception) unparse a node to its string representation.

    Parameters:
        node: The node to unparse.
        filepath: An optional filepath from where the node comes.

    Returns:
        The unparsed code of the node.
    """
    try:
        return get_value(node)
    except Exception as error:
        message = f"Failed to unparse node {node}"
        if filepath:
            message += f" at {filepath}:{node.lineno}"  # type: ignore[union-attr]
        message += f": {error}"
        logger.error(message)
        return None


# ==========================================================
# names
def _get_attribute_name(node: NodeAttribute) -> str:
    return f"{get_name(node.value)}.{node.attr}"


def _get_name_name(node: NodeName) -> str:
    return node.id


_node_name_map: dict[Type, Callable[[Any], str]] = {
    NodeName: _get_name_name,
    NodeAttribute: _get_attribute_name,
}


def get_name(node: AST) -> str:
    """Extract name from an assignment node.

    Parameters:
        node: The node to extract names from.

    Returns:
        A list of names.
    """
    return _node_name_map[type(node)](node)


def _get_assign_names(node: NodeAssign) -> list[str]:
    names = (get_name(target) for target in node.targets)
    return [name for name in names if name]


def _get_annassign_names(node: NodeAnnAssign) -> list[str]:
    name = get_name(node.target)
    return [name] if name else []


_node_names_map: dict[Type, Callable[[Any], list[str]]] = {  # noqa: WPS234
    NodeAssign: _get_assign_names,
    NodeAnnAssign: _get_annassign_names,
}


def get_names(node: AST) -> list[str]:
    """Extract names from an assignment node.

    Parameters:
        node: The node to extract names from.

    Returns:
        A list of names.
    """
    return _node_names_map[type(node)](node)


def get_instance_names(node: AST) -> list[str]:
    """Extract names from an assignment node, only for instance attributes.

    Parameters:
        node: The node to extract names from.

    Returns:
        A list of names.
    """
    return [name.split(".", 1)[1] for name in get_names(node) if name.startswith("self.")]


# ==========================================================
# parameters
def get_parameter_default(node: AST | None, filepath: Path, lines_collection: LinesCollection) -> str | None:
    """Extract the default value of a function parameter.

    Parameters:
        node: The node to extract the default value from.
        filepath: The filepath in which the parameter is written.
            It allows to retrieve the actual code directly from the lines collection.
        lines_collection: A collection of source code lines.

    Returns:
        The default value as a string.
    """
    if node is None:
        return None
    with suppress(KeyError):
        return _get_value(node)
    if node.lineno == node.end_lineno:  # type: ignore[attr-defined]
        return lines_collection[filepath][node.lineno - 1][node.col_offset : node.end_col_offset]  # type: ignore[attr-defined]
    # TODO: handle multiple line defaults
    return None


# ==========================================================
# relative imports
def relative_to_absolute(node: NodeImportFrom, name: NodeAlias, current_module: Module) -> str:
    """Convert a relative import path to an absolute one.

    Parameters:
        node: The "from ... import ..." AST node.
        name: The imported name.
        current_module: The module in which the import happens.

    Returns:
        The absolute import path.
    """
    level = node.level
    if level > 0 and current_module.is_package or current_module.is_subpackage:
        level -= 1
    while level > 0 and current_module.parent is not None:
        current_module = current_module.parent  # type: ignore[assignment]
        level -= 1
    base = current_module.path + "." if node.level > 0 else ""
    node_module = node.module + "." if node.module else ""
    return base + node_module + name.name
