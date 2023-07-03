"""This module contains utilities for extracting information from nodes."""

from __future__ import annotations

import enum
import inspect
import sys
from ast import AST, PyCF_ONLY_AST
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
from ast import NamedExpr as NodeNamedExpr
from ast import Not as NodeNot
from ast import NotEq as NodeNotEq
from ast import NotIn as NodeNotIn
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
from contextlib import contextmanager, suppress
from functools import cached_property, partial
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Iterator, Sequence

from griffe.exceptions import LastNodeError, RootNodeError
from griffe.expressions import Expression, Name
from griffe.logger import LogLevel, get_logger

# TODO: remove once Python 3.8 support is dropped
if sys.version_info < (3, 9):
    from ast import ExtSlice as NodeExtSlice
    from ast import Index as NodeIndex

if TYPE_CHECKING:
    from pathlib import Path

    from griffe.collections import LinesCollection
    from griffe.dataclasses import Class, Module


logger = get_logger(__name__)


class ASTNode:
    """This class is dynamically added to the bases of each AST node class."""

    parent: ASTNode

    @cached_property
    def kind(self) -> str:
        """Return the kind of this node.

        Returns:
            The node kind.
        """
        return self.__class__.__name__.lower()

    @cached_property
    def children(self) -> Sequence[ASTNode]:
        """Build and return the children of this node.

        Returns:
            A list of children.
        """
        children = []
        for field_name in self._fields:  # type: ignore[attr-defined]
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

    @cached_property
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
    def last_child(self) -> ASTNode:
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
    exclude_specials: ClassVar[set[str]] = {"__builtins__", "__loader__", "__spec__"}

    def __init__(self, obj: Any, name: str, parent: ObjectNode | None = None) -> None:
        """Initialize the object.

        Arguments:
            obj: A Python object.
            name: The object's name.
            parent: The object's parent node.
        """
        try:
            obj = inspect.unwrap(obj)
        except Exception as error:  # noqa: BLE001
            # inspect.unwrap at some point runs hasattr(obj, "__wrapped__"),
            # which triggers the __getattr__ method of the object, which in
            # turn can raise various exceptions. Probably not just __getattr__.
            # See https://github.com/pawamoy/pytkdocs/issues/45
            logger.debug(f"Could not unwrap {name}: {error!r}")

        self.obj: Any = obj
        self.name: str = name
        self.parent: ObjectNode | None = parent

    def __repr__(self) -> str:
        return f"ObjectNode(name={self.name!r})"

    @cached_property
    def path(self) -> str:
        """The object's (Python) path."""
        if self.parent is None:
            return self.name
        return f"{self.parent.path}.{self.name}"

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
    def children(self) -> Sequence[ObjectNode]:
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
        """Tell if this node's object is a module.

        Returns:
            The root of the tree.
        """
        return inspect.ismodule(self.obj)

    @cached_property
    def is_class(self) -> bool:
        """Tell if this node's object is a class.

        Returns:
            If this node's object is a class.
        """
        return inspect.isclass(self.obj)

    @cached_property
    def is_function(self) -> bool:
        """Tell if this node's object is a function.

        Returns:
            If this node's object is a function.
        """
        return inspect.isfunction(self.obj)

    @cached_property
    def is_builtin_function(self) -> bool:
        """Tell if this node's object is a builtin function.

        Returns:
            If this node's object is a builtin function.
        """
        return inspect.isbuiltin(self.obj)

    @cached_property
    def is_coroutine(self) -> bool:
        """Tell if this node's object is a coroutine.

        Returns:
            If this node's object is a coroutine.
        """
        return inspect.iscoroutinefunction(self.obj)

    @cached_property
    def is_property(self) -> bool:
        """Tell if this node's object is a property.

        Returns:
            If this node's object is a property.
        """
        return isinstance(self.obj, property) or self.is_cached_property

    @cached_property
    def is_cached_property(self) -> bool:
        """Tell if this node's object is a cached property.

        Returns:
            If this node's object is a cached property.
        """
        return isinstance(self.obj, cached_property)

    @cached_property
    def parent_is_class(self) -> bool:
        """Tell if the object of this node's parent is a class.

        Returns:
            If the object of this node's parent is a class.
        """
        return bool(self.parent and self.parent.is_class)

    @cached_property
    def is_method(self) -> bool:
        """Tell if this node's object is a method.

        Returns:
            If this node's object is a method.
        """
        function_type = type(lambda: None)
        return self.parent_is_class and isinstance(self.obj, function_type)

    @cached_property
    def is_method_descriptor(self) -> bool:
        """Tell if this node's object is a method descriptor.

        Built-in methods (e.g. those implemented in C/Rust) are often
        method descriptors, rather than normal methods.

        Returns:
            If this node's object is a method descriptor.
        """
        return inspect.ismethoddescriptor(self.obj)

    @cached_property
    def is_builtin_method(self) -> bool:
        """Tell if this node's object is a builtin method.

        Returns:
            If this node's object is a builtin method.
        """
        return self.is_builtin_function and self.parent_is_class

    @cached_property
    def is_staticmethod(self) -> bool:
        """Tell if this node's object is a staticmethod.

        Returns:
            If this node's object is a staticmethod.
        """
        if self.parent is None:
            return False
        try:
            self_from_parent = self.parent.obj.__dict__.get(self.name, None)
        except AttributeError:
            return False
        return self.parent_is_class and isinstance(self_from_parent, staticmethod)

    @cached_property
    def is_classmethod(self) -> bool:
        """Tell if this node's object is a classmethod.

        Returns:
            If this node's object is a classmethod.
        """
        if self.parent is None:
            return False
        try:
            self_from_parent = self.parent.obj.__dict__.get(self.name, None)
        except AttributeError:
            return False
        return self.parent_is_class and isinstance(self_from_parent, classmethod)

    @cached_property
    def _ids(self) -> set[int]:
        if self.parent is None:
            return {id(self.obj)}
        return {id(self.obj)} | self.parent._ids

    def _pick_member(self, name: str, member: Any) -> bool:
        return (
            name not in self.exclude_specials
            and member is not type
            and member is not object
            and id(member) not in self._ids
            and name in vars(self.obj)
        )


def _join(sequence: Sequence, item: str) -> list:
    if not sequence:
        return []
    new_sequence = [sequence[0]]
    for element in sequence[1:]:
        new_sequence.append(item)
        new_sequence.append(element)
    return new_sequence


# ===========================================================
# __all__ assignments
class _AllExtractor:
    def __init__(self, parent: Module) -> None:
        self.parent = parent
        self._node_map: dict[type, Callable[[Any], list[str | Name]]] = {
            NodeConstant: self._extract_constant,  # type: ignore[dict-item]
            NodeName: self._extract_name,  # type: ignore[dict-item]
            NodeStarred: self._extract_starred,
            NodeList: self._extract_sequence,
            NodeSet: self._extract_sequence,
            NodeTuple: self._extract_sequence,
            NodeBinOp: self._extract_binop,
        }

    def _extract_constant(self, node: NodeConstant) -> list[str]:
        return [node.value]

    def _extract_name(self, node: NodeName) -> list[Name]:
        return [Name(node.id, partial(self.parent.resolve, node.id))]

    def _extract_starred(self, node: NodeStarred) -> list[str | Name]:
        return self._extract(node.value)

    def _extract_sequence(self, node: NodeList | NodeSet | NodeTuple) -> list[str | Name]:
        sequence = []
        for elt in node.elts:
            sequence.extend(self._extract(elt))
        return sequence

    def _extract_binop(self, node: NodeBinOp) -> list[str | Name]:
        left = self._extract(node.left)
        right = self._extract(node.right)
        return left + right

    def _extract(self, node: AST) -> list[str | Name]:
        return self._node_map[type(node)](node)


def get__all__(node: NodeAssign | NodeAugAssign, parent: Module) -> list[str | Name]:
    """Get the values declared in `__all__`.

    Parameters:
        node: The assignment node.
        parent: The parent module.

    Returns:
        A set of names.
    """
    if node.value is None:
        return []
    extractor = _AllExtractor(parent)
    return extractor._extract(node.value)


def safe_get__all__(
    node: NodeAssign | NodeAugAssign,
    parent: Module,
    log_level: LogLevel = LogLevel.debug,  # TODO: set to error when we handle more things
) -> list[str | Name]:
    """Safely (no exception) extract values in `__all__`.

    Parameters:
        node: The `__all__` assignment node.
        parent: The parent used to resolve the names.
        log_level: Log level to use to log a message.

    Returns:
        A list of strings or resovable names.
    """
    try:
        return get__all__(node, parent)
    except Exception as error:  # noqa: BLE001
        message = f"Failed to extract `__all__` value: {get_value(node.value)}"
        with suppress(Exception):
            message += f" at {parent.relative_filepath}:{node.lineno}"
        if isinstance(error, KeyError):
            message += f": unsupported node {error}"
        else:
            message += f": {error}"
        getattr(logger, log_level.value)(message)
        return []


# ===========================================================
# annotations, base classes, type-guarding conditions, values
class _ExpressionBuilder:
    __slots__ = ("parent", "_node_map", "_literal_strings", "_parse_strings")

    def __init__(self, parent: Module | Class, *, parse_strings: bool | None = None) -> None:
        self.parent = parent
        self._node_map: dict[type, Callable[[Any], str | Name | Expression]] = {
            NodeAttribute: self._build_attribute,
            NodeBinOp: self._build_binop,
            NodeBitAnd: self._build_bitand,
            NodeBitOr: self._build_bitor,
            NodeCall: self._build_call,
            NodeConstant: self._build_constant,
            NodeEllipsis: self._build_ellipsis,
            NodeIfExp: self._build_ifexp,
            NodeInvert: self._build_invert,
            NodeKeyword: self._build_keyword,
            NodeList: self._build_list,
            NodeName: self._build_name,
            NodeSubscript: self._build_subscript,
            NodeTuple: self._build_tuple,
            NodeUnaryOp: self._build_unaryop,
            NodeUAdd: self._build_uadd,
            NodeUSub: self._build_usub,
        }

        self._literal_strings = False
        if parse_strings is None:
            try:
                module = parent.module
            except ValueError:
                self._parse_strings = False
            else:
                self._parse_strings = not module.imports_future_annotations
        else:
            self._parse_strings = parse_strings

        # TODO: remove once Python 3.8 support is dropped
        if sys.version_info < (3, 9):
            self._node_map[NodeIndex] = self._build_index

    @contextmanager
    def literal_strings(self) -> Iterator[None]:
        self._literal_strings = True
        try:
            yield
        finally:
            self._literal_strings = False

    def _build_attribute(self, node: NodeAttribute) -> Expression:
        left = self._build(node.value)

        def resolver() -> str:
            return f"{left.full}.{node.attr}"  # type: ignore[union-attr]

        right = Name(node.attr, resolver, first_attr_name=False)
        return Expression(left, ".", right)

    def _build_binop(self, node: NodeBinOp) -> Expression:
        left = self._build(node.left)
        right = self._build(node.right)
        return Expression(left, self._build(node.op), right)

    def _build_bitand(self, node: NodeBitAnd) -> str:  # noqa: ARG002
        return " & "

    def _build_bitor(self, node: NodeBitOr) -> str:  # noqa: ARG002
        return " | "

    def _build_call(self, node: NodeCall) -> Expression:
        posargs = Expression(*_join([self._build(arg) for arg in node.args], ", "))
        kwargs = Expression(*_join([self._build(kwarg) for kwarg in node.keywords], ", "))
        args: Expression | str
        if posargs and kwargs:
            args = Expression(posargs, ", ", kwargs)
        elif posargs:
            args = posargs
        elif kwargs:
            args = kwargs
        else:
            args = ""
        return Expression(self._build(node.func), "(", args, ")")

    def _build_constant(self, node: NodeConstant) -> str | Name | Expression:
        if self._parse_strings and isinstance(node.value, str) and not self._literal_strings:
            # A string in an annotation is a stringified annotation: we parse and build it again.
            # If we fail to parse it (syntax errors), we consider it's a literal string and log a message.
            # Literal strings must be wrapped in Literal[...] to be picked up as such.
            try:
                parsed = compile(
                    node.value,
                    mode="eval",
                    filename="<string-annotation>",
                    flags=PyCF_ONLY_AST,
                    optimize=1,
                )
            except SyntaxError:
                logger.debug(
                    f"Tried and failed to parse {node.value!r} as Python code, "
                    "falling back to using it as a string literal "
                    "(postponed annotations might help: https://peps.python.org/pep-0563/)",
                )
            else:
                return self._build(parsed.body)  # type: ignore[attr-defined]
        return self._build_literal(node)

    def _build_literal(self, node: NodeConstant) -> str:
        return {type(...): lambda _: "..."}.get(type(node.value), repr)(node.value)

    def _build_ellipsis(self, node: NodeEllipsis) -> str:  # noqa: ARG002
        return "..."

    def _build_ifexp(self, node: NodeIfExp) -> Expression:
        return Expression(
            self._build(node.body),
            " if ",
            self._build(node.test),
            " else",
            self._build(node.orelse),
        )

    def _build_invert(self, node: NodeInvert) -> str:  # noqa: ARG002
        return "~"

    def _build_keyword(self, node: NodeKeyword) -> Expression:
        return Expression(f"{node.arg}=", self._build(node.value))

    def _build_list(self, node: NodeList) -> Expression:
        return Expression("[", *_join([self._build(el) for el in node.elts], ", "), "]")

    def _build_name(self, node: NodeName) -> Name:
        return Name(node.id, partial(self.parent.resolve, node.id))

    def _build_subscript(self, node: NodeSubscript) -> Expression:
        left = self._build(node.value)
        if self._parse_strings and left.full in {"typing.Literal", "typing_extensions.Literal"}:  # type: ignore[union-attr]
            with self.literal_strings():
                subscript = self._build(node.slice)
        else:
            subscript = self._build(node.slice)
        return Expression(left, "[", subscript, "]")

    def _build_tuple(self, node: NodeTuple) -> Expression:
        return Expression(*_join([self._build(el) for el in node.elts], ", "))

    def _build_unaryop(self, node: NodeUnaryOp) -> Expression:
        return Expression(self._build(node.op), self._build(node.operand))

    def _build_uadd(self, node: NodeUAdd) -> str:  # noqa: ARG002
        return "+"

    def _build_usub(self, node: NodeUSub) -> str:  # noqa: ARG002
        return "-"

    # TODO: remove once Python 3.8 support is dropped
    if sys.version_info < (3, 9):

        def _build_index(self, node: NodeIndex) -> str | Name | Expression:
            return self._build(node.value)

    def _build(self, node: AST) -> str | Name | Expression:
        return self._node_map[type(node)](node)


def get_expression(
    node: AST | None,
    parent: Module | Class,
    *,
    parse_strings: bool | None = None,
) -> str | Name | Expression | None:
    """Build an expression from an AST.

    Parameters:
        node: The annotation node.
        parent: The parent used to resolve the name.
        parse_strings: Whether to try and parse strings as type annotations.

    Returns:
        A string or resovable name or expression.
    """
    if node is None:
        return None
    builder = _ExpressionBuilder(parent, parse_strings=parse_strings)
    return builder._build(node)


def safe_get_expression(
    node: AST | None,
    parent: Module | Class,
    *,
    parse_strings: bool | None = None,
    log_level: LogLevel | None = LogLevel.error,
    msg_format: str = "{path}:{lineno}: Failed to get expression from {node_class}: {error}",
) -> str | Name | Expression | None:
    """Safely (no exception) build a resolvable annotation.

    Parameters:
        node: The annotation node.
        parent: The parent used to resolve the name.
        parse_strings: Whether to try and parse strings as type annotations.
        log_level: Log level to use to log a message. None to disable logging.
        msg_format: A format string for the log message. Available placeholders:
            path, lineno, node, error.

    Returns:
        A string or resovable name or expression.
    """
    try:
        return get_expression(node, parent, parse_strings=parse_strings)
    except Exception as error:  # noqa: BLE001
        if log_level is None:
            return None
        node_class = node.__class__.__name__
        try:
            path: Path | str = parent.relative_filepath
        except ValueError:
            path = "<in-memory>"
        lineno = node.lineno  # type: ignore[union-attr]
        message = msg_format.format(path=path, lineno=lineno, node_class=node_class, error=error)
        getattr(logger, log_level.value)(message)
    return None


_msg_format = "{path}:{lineno}: Failed to get %s expression from {node_class}: {error}"
get_annotation = partial(get_expression, parse_strings=None)
safe_get_annotation = partial(
    safe_get_expression,
    parse_strings=None,
    msg_format=_msg_format % "annotation",
)
get_base_class = partial(get_expression, parse_strings=False)
safe_get_base_class = partial(
    safe_get_expression,
    parse_strings=False,
    msg_format=_msg_format % "base class",
)
get_condition = partial(get_expression, parse_strings=False)
safe_get_condition = partial(
    safe_get_expression,
    parse_strings=False,
    msg_format=_msg_format % "condition",
)


# ==========================================================
# docstrings
def get_docstring(
    node: AST,
    *,
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
        return doc.value, doc.lineno, doc.end_lineno
    if isinstance(doc, NodeStr):
        lineno = doc.lineno
        return doc.s, lineno, doc.end_lineno
    return None, None, None


# ==========================================================
# values
class _ValueExtractor:
    __slots__ = ("_node_map",)

    def __init__(self) -> None:
        self._node_map: dict[type, Callable[[Any], str]] = {
            NodeAdd: self._extract_add,
            NodeAnd: self._extract_and,
            NodeArguments: self._extract_arguments,
            NodeAttribute: self._extract_attribute,
            NodeBinOp: self._extract_binop,
            NodeBitAnd: self._extract_bitand,
            NodeBitOr: self._extract_bitor,
            NodeBitXor: self._extract_bitxor,
            NodeBoolOp: self._extract_boolop,
            NodeCall: self._extract_call,
            NodeCompare: self._extract_compare,
            NodeComprehension: self._extract_comprehension,
            NodeConstant: self._extract_constant,
            NodeDictComp: self._extract_dictcomp,
            NodeDict: self._extract_dict,
            NodeDiv: self._extract_div,
            NodeEllipsis: self._extract_ellipsis,
            NodeEq: self._extract_eq,
            NodeFloorDiv: self._extract_floordiv,
            NodeFormattedValue: self._extract_formatted,
            NodeGeneratorExp: self._extract_generatorexp,
            NodeGtE: self._extract_gte,
            NodeGt: self._extract_gt,
            NodeIfExp: self._extract_ifexp,
            NodeIn: self._extract_in,
            NodeInvert: self._extract_invert,
            NodeIs: self._extract_is,
            NodeIsNot: self._extract_isnot,
            NodeJoinedStr: self._extract_joinedstr,
            NodeKeyword: self._extract_keyword,
            NodeLambda: self._extract_lambda,
            NodeListComp: self._extract_listcomp,
            NodeList: self._extract_list,
            NodeLShift: self._extract_lshift,
            NodeLtE: self._extract_lte,
            NodeLt: self._extract_lt,
            NodeMatMult: self._extract_matmult,
            NodeMod: self._extract_mod,
            NodeMult: self._extract_mult,
            NodeName: self._extract_name,
            NodeNotEq: self._extract_noteq,
            NodeNot: self._extract_not,
            NodeNotIn: self._extract_notin,
            NodeOr: self._extract_or,
            NodePow: self._extract_pow,
            NodeRShift: self._extract_rshift,
            NodeSetComp: self._extract_setcomp,
            NodeSet: self._extract_set,
            NodeSlice: self._extract_slice,
            NodeStarred: self._extract_starred,
            NodeSub: self._extract_sub,
            NodeSubscript: self._extract_subscript,
            NodeTuple: self._extract_tuple,
            NodeUAdd: self._extract_uadd,
            NodeUnaryOp: self._extract_unaryop,
            NodeUSub: self._extract_usub,
            NodeYield: self._extract_yield,
        }

        self._node_map[NodeNamedExpr] = self._extract_named_expr

        # TODO: remove once Python 3.8 support is dropped
        if sys.version_info < (3, 9):
            self._node_map[NodeExtSlice] = self._extract_extslice
            self._node_map[NodeIndex] = self._extract_index

    def _extract_add(self, node: NodeAdd) -> str:  # noqa: ARG002
        return "+"

    def _extract_and(self, node: NodeAnd) -> str:  # noqa: ARG002
        return " and "

    def _extract_arguments(self, node: NodeArguments) -> str:
        return ", ".join(arg.arg for arg in node.args)

    def _extract_attribute(self, node: NodeAttribute) -> str:
        return f"{self._extract(node.value)}.{node.attr}"

    def _extract_binop(self, node: NodeBinOp) -> str:
        return f"{self._extract(node.left)} {self._extract(node.op)} {self._extract(node.right)}"

    def _extract_bitor(self, node: NodeBitOr) -> str:  # noqa: ARG002
        return "|"

    def _extract_bitand(self, node: NodeBitAnd) -> str:  # noqa: ARG002
        return "&"

    def _extract_bitxor(self, node: NodeBitXor) -> str:  # noqa: ARG002
        return "^"

    def _extract_boolop(self, node: NodeBoolOp) -> str:
        return self._extract(node.op).join(self._extract(value) for value in node.values)

    def _extract_call(self, node: NodeCall) -> str:
        posargs = ", ".join(self._extract(arg) for arg in node.args)
        kwargs = ", ".join(self._extract(kwarg) for kwarg in node.keywords)
        if posargs and kwargs:
            args = f"{posargs}, {kwargs}"
        elif posargs:
            args = posargs
        elif kwargs:
            args = kwargs
        else:
            args = ""
        return f"{self._extract(node.func)}({args})"

    def _extract_compare(self, node: NodeCompare) -> str:
        left = self._extract(node.left)
        ops = [self._extract(op) for op in node.ops]
        comparators = [self._extract(comparator) for comparator in node.comparators]
        return f"{left} " + " ".join(f"{op} {comp}" for op, comp in zip(ops, comparators))

    def _extract_comprehension(self, node: NodeComprehension) -> str:
        target = self._extract(node.target)
        iterable = self._extract(node.iter)
        conditions = [self._extract(condition) for condition in node.ifs]
        value = f"for {target} in {iterable}"
        if conditions:
            value = f"{value} if " + " if ".join(conditions)
        if node.is_async:
            return f"async {value}"
        return value

    def _extract_constant(self, node: NodeConstant) -> str:
        return repr(node.value)

    def _extract_constant_no_string_repr(self, node: NodeConstant) -> str:
        if isinstance(node.value, str):
            return node.value
        return repr(node.value)

    def _extract_dict(self, node: NodeDict) -> str:
        pairs = zip(node.keys, node.values)
        gen = (f"{'None' if key is None else self._extract(key)}: {self._extract(value)}" for key, value in pairs)
        return "{" + ", ".join(gen) + "}"

    def _extract_dictcomp(self, node: NodeDictComp) -> str:
        key = self._extract(node.key)
        value = self._extract(node.value)
        generators = [self._extract(gen) for gen in node.generators]
        return f"{{{key}: {value} " + " ".join(generators) + "}"

    def _extract_div(self, node: NodeDiv) -> str:  # noqa: ARG002
        return "/"

    def _extract_ellipsis(self, node: NodeEllipsis) -> str:  # noqa: ARG002
        return "..."

    def _extract_eq(self, node: NodeEq) -> str:  # noqa: ARG002
        return "=="

    def _extract_floordiv(self, node: NodeFloorDiv) -> str:  # noqa: ARG002
        return "//"

    def _extract_formatted(self, node: NodeFormattedValue) -> str:
        return f"{{{self._extract(node.value)}}}"

    def _extract_generatorexp(self, node: NodeGeneratorExp) -> str:
        element = self._extract(node.elt)
        generators = [self._extract(gen) for gen in node.generators]
        return f"{element} " + " ".join(generators)

    def _extract_gte(self, node: NodeNotEq) -> str:  # noqa: ARG002
        return ">="

    def _extract_gt(self, node: NodeNotEq) -> str:  # noqa: ARG002
        return ">"

    def _extract_ifexp(self, node: NodeIfExp) -> str:
        return f"{self._extract(node.body)} if {self._extract(node.test)} else {self._extract(node.orelse)}"

    def _extract_invert(self, node: NodeInvert) -> str:  # noqa: ARG002
        return "~"

    def _extract_in(self, node: NodeIn) -> str:  # noqa: ARG002
        return "in"

    def _extract_is(self, node: NodeIs) -> str:  # noqa: ARG002
        return "is"

    def _extract_isnot(self, node: NodeIsNot) -> str:  # noqa: ARG002
        return "is not"

    def _extract_joinedstr(self, node: NodeJoinedStr) -> str:
        self._node_map[NodeConstant] = self._extract_constant_no_string_repr
        try:
            return "f" + repr("".join(self._extract(value) for value in node.values))
        finally:
            self._node_map[NodeConstant] = self._extract_constant

    def _extract_keyword(self, node: NodeKeyword) -> str:
        return f"{node.arg}={self._extract(node.value)}"

    def _extract_lambda(self, node: NodeLambda) -> str:
        return f"lambda {self._extract(node.args)}: {self._extract(node.body)}"

    def _extract_list(self, node: NodeList) -> str:
        return "[" + ", ".join(self._extract(el) for el in node.elts) + "]"

    def _extract_listcomp(self, node: NodeListComp) -> str:
        element = self._extract(node.elt)
        generators = [self._extract(gen) for gen in node.generators]
        return f"[{element} " + " ".join(generators) + "]"

    def _extract_lshift(self, node: NodeLShift) -> str:  # noqa: ARG002
        return "<<"

    def _extract_lte(self, node: NodeNotEq) -> str:  # noqa: ARG002
        return "<="

    def _extract_lt(self, node: NodeNotEq) -> str:  # noqa: ARG002
        return "<"

    def _extract_matmult(self, node: NodeMatMult) -> str:  # noqa: ARG002
        return "@"

    def _extract_mod(self, node: NodeMod) -> str:  # noqa: ARG002
        return "%"

    def _extract_mult(self, node: NodeMult) -> str:  # noqa: ARG002
        return "*"

    def _extract_name(self, node: NodeName) -> str:
        return node.id

    def _extract_not(self, node: NodeNot) -> str:  # noqa: ARG002
        return "not "

    def _extract_noteq(self, node: NodeNotEq) -> str:  # noqa: ARG002
        return "!="

    def _extract_notin(self, node: NodeNotIn) -> str:  # noqa: ARG002
        return "not in"

    def _extract_or(self, node: NodeOr) -> str:  # noqa: ARG002
        return " or "

    def _extract_pow(self, node: NodePow) -> str:  # noqa: ARG002
        return "**"

    def _extract_rshift(self, node: NodeRShift) -> str:  # noqa: ARG002
        return ">>"

    def _extract_set(self, node: NodeSet) -> str:
        return "{" + ", ".join(self._extract(el) for el in node.elts) + "}"

    def _extract_setcomp(self, node: NodeSetComp) -> str:
        element = self._extract(node.elt)
        generators = [self._extract(gen) for gen in node.generators]
        return f"{{{element} " + " ".join(generators) + "}"

    def _extract_slice(self, node: NodeSlice) -> str:
        value = f"{self._extract(node.lower) if node.lower else ''}:{self._extract(node.upper) if node.upper else ''}"
        if node.step:
            return f"{value}:{self._extract(node.step)}"
        return value

    def _extract_starred(self, node: NodeStarred) -> str:
        return self._extract(node.value)

    def _extract_sub(self, node: NodeSub) -> str:  # noqa: ARG002
        return "-"

    def _extract_subscript(self, node: NodeSubscript) -> str:
        subscript = self._extract(node.slice)
        if isinstance(subscript, str) and subscript.startswith("(") and subscript.endswith(")"):
            subscript = subscript[1:-1]
        return f"{self._extract(node.value)}[{subscript}]"

    def _extract_tuple(self, node: NodeTuple) -> str:
        return "(" + ", ".join(self._extract(el) for el in node.elts) + ")"

    def _extract_uadd(self, node: NodeUAdd) -> str:  # noqa: ARG002
        return "+"

    def _extract_unaryop(self, node: NodeUnaryOp) -> str:
        return f"{self._extract(node.op)}{self._extract(node.operand)}"

    def _extract_usub(self, node: NodeUSub) -> str:  # noqa: ARG002
        return "-"

    def _extract_yield(self, node: NodeYield) -> str:
        if node.value is None:
            return repr(None)
        return self._extract(node.value)

    def _extract_named_expr(self, node: NodeNamedExpr) -> str:
        return f"({self._extract(node.target)} := {self._extract(node.value)})"

    # TODO: remove once Python 3.8 support is
    if sys.version_info < (3, 9):

        def _extract_extslice(self, node: NodeExtSlice) -> str:
            return ",".join(self._extract(dim) for dim in node.dims)

        def _extract_index(self, node: NodeIndex) -> str:
            return self._extract(node.value)

    def _extract(self, node: AST) -> str:
        return self._node_map[type(node)](node)


def get_value(node: AST | None) -> str | None:
    """Get the string representation of a node.

    Parameters:
        node: The node to represent.

    Returns:
        The representing code for the node.
    """
    if node is None:
        return None
    extractor = _ValueExtractor()
    return extractor._extract(node)


def safe_get_value(node: AST | None, filepath: str | Path | None = None) -> str | None:
    """Safely (no exception) get the string representation of a node.

    Parameters:
        node: The node to represent.
        filepath: An optional filepath from where the node comes.

    Returns:
        The representing code for the node.
    """
    try:
        return get_value(node)
    except Exception as error:
        message = f"Failed to represent node {node}"
        if filepath:
            message += f" at {filepath}:{node.lineno}"  # type: ignore[union-attr]
        message += f": {error}"
        logger.exception(message)
        return None


# ==========================================================
# names
def _get_attribute_name(node: NodeAttribute) -> str:
    return f"{get_name(node.value)}.{node.attr}"


def _get_name_name(node: NodeName) -> str:
    return node.id


_node_name_map: dict[type, Callable[[Any], str]] = {
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


_node_names_map: dict[type, Callable[[Any], list[str]]] = {
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
    default = safe_get_value(node)
    if default is not None:
        return default
    if node.lineno == node.end_lineno:
        return lines_collection[filepath][node.lineno - 1][node.col_offset : node.end_col_offset]
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
