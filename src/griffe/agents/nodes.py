"""This module contains utilities for extracting information from AST nodes."""

from __future__ import annotations

import enum
import inspect
import sys
from ast import AST
from ast import And as NodeAnd
from ast import AnnAssign as NodeAnnAssign
from ast import Assign as NodeAssign
from ast import Attribute as NodeAttribute
from ast import BinOp as NodeBinOp
from ast import BitAnd as NodeBitAnd
from ast import BitOr as NodeBitOr
from ast import BoolOp as NodeBoolOp
from ast import Call as NodeCall
from ast import Compare as NodeCompare
from ast import Constant as NodeConstant
from ast import Dict as NodeDict
from ast import DictComp as NodeDictComp
from ast import Div as NodeDiv
from ast import Ellipsis as NodeEllipsis
from ast import Expr as NodeExpr
from ast import FormattedValue as NodeFormattedValue
from ast import GeneratorExp as NodeGeneratorExp
from ast import Gt as NodeGt
from ast import GtE as NodeGtE
from ast import IfExp as NodeIfExp
from ast import JoinedStr as NodeJoinedStr
from ast import Lambda as NodeLambda
from ast import List as NodeList
from ast import ListComp as NodeListComp
from ast import Lt as NodeLt
from ast import LtE as NodeLtE
from ast import Mult as NodeMult
from ast import Name as NodeName
from ast import Not as NodeNot
from ast import NotEq as NodeNotEq
from ast import Num as NodeNum
from ast import Or as NodeOr
from ast import Set as NodeSet
from ast import Slice as NodeSlice
from ast import Starred as NodeStarred
from ast import Str as NodeStr
from ast import Subscript as NodeSubscript
from ast import Tuple as NodeTuple
from ast import UAdd as NodeUAdd
from ast import UnaryOp as NodeUnaryOp
from ast import USub as NodeUSub
from ast import arguments as NodeArguments
from ast import comprehension as NodeComprehension
from ast import keyword as NodeKeyword
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Sequence, Type

from griffe.collections import LinesCollection
from griffe.exceptions import LastNodeError, RootNodeError
from griffe.expressions import Expression, Name

# TODO: remove once Python 3.7 support is dropped
if sys.version_info < (3, 8):
    from ast import NameConstant as NodeNameConstant

    from cached_property import cached_property
else:
    from functools import cached_property  # noqa: WPS440

# TODO: remove once Python 3.8 support is dropped
if sys.version_info < (3, 9):
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
    COROUTINE: str = "coroutine"
    FUNCTION: str = "function"
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
        if self.is_method_descriptor:
            return ObjectKind.METHOD_DESCRIPTOR
        if self.is_method:
            return ObjectKind.METHOD
        if self.is_coroutine:
            return ObjectKind.COROUTINE
        if self.is_function:
            return ObjectKind.FUNCTION
        if self.is_cached_property:
            return ObjectKind.CACHED_PROPERTY
        if self.is_property:
            return ObjectKind.PROPERTY
        return ObjectKind.ATTRIBUTE

    @cached_property
    def children(self) -> Sequence[ObjectNode]:  # noqa: WPS231
        """Build and return the children of this node.

        Returns:
            A list of children.
        """
        children = []
        for name, member in inspect.getmembers(self.obj):
            if self._pick_member(member):
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
    def is_staticmethod(self) -> bool:
        """
        Tell if this node's object is a staticmethod.

        Returns:
            If this node's object is a staticmethod.
        """
        if not self.parent:
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
        if not self.parent:
            return False
        try:
            self_from_parent = self.parent.obj.__dict__.get(self.name, None)  # noqa: WPS609
        except AttributeError:
            return False
        return self.parent_is_class and isinstance(self_from_parent, classmethod)

    @cached_property
    def _ids(self) -> set[int]:
        if self.parent is None:
            return {id(self)}
        return {id(self)} | self.parent._ids  # noqa: WPS437

    def _pick_member(self, member: Any) -> bool:
        return member is not type and member is not object and id(member) not in self._ids


def _join(sequence, item):
    if not sequence:
        return []
    new_sequence = [sequence[0]]
    for element in sequence[1:]:
        new_sequence.extend((item, element))
    return new_sequence


# ==========================================================
# base classes
def _get_baseclass_name(node: NodeName, parent: Module | Class) -> Name:
    return Name(node.id, partial(parent.resolve, node.id))


def _get_baseclass_attribute(node: NodeAttribute, parent: Module | Class) -> Expression:
    left = get_baseclass(node.value, parent)

    def resolver():  # noqa: WPS430
        return f"{left.full}.{node.attr}"

    right = Name(node.attr, resolver)
    return Expression(left, ".", right)


def _get_baseclass_subscript(node: NodeSubscript, parent: Module | Class) -> Expression:
    left = get_baseclass(node.value, parent)
    subscript = get_baseclass(node.slice, parent)
    return Expression(left, "[", subscript, "]")


_node_baseclass_map: dict[Type, Callable[[Any, Module | Class], Name | Expression]] = {
    NodeName: _get_baseclass_name,
    NodeAttribute: _get_baseclass_attribute,
    NodeSubscript: _get_baseclass_subscript,
}


def get_baseclass(node: AST, parent: Module | Class) -> Name | Expression:
    """Extract a resolvable name for a given base class.

    Parameters:
        node: The base class node.
        parent: The parent used to resolve the name.

    Returns:
        A resovable name or expression.
    """
    return _node_baseclass_map[type(node)](node, parent)


# ==========================================================
# annotations
def _get_name_annotation(node: NodeName, parent: Module | Class) -> Name:
    return Name(node.id, partial(parent.resolve, node.id))


def _get_constant_annotation(node: NodeConstant, parent: Module | Class) -> str:
    return repr(node.value)


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


def _get_bitor_annotation(node: NodeBitOr, parent: Module | Class) -> str:
    return " | "


def _get_bitand_annotation(node: NodeBitOr, parent: Module | Class) -> str:
    return " & "


def _get_subscript_annotation(node: NodeSubscript, parent: Module | Class) -> Expression:
    left = _get_annotation(node.value, parent)
    subscript = _get_annotation(node.slice, parent)
    return Expression(left, "[", subscript, "]")


def _get_tuple_annotation(node: NodeTuple, parent: Module | Class) -> Expression:
    return Expression(*_join([_get_annotation(el, parent) for el in node.elts], ", "))


def _get_list_annotation(node: NodeList, parent: Module | Class) -> Expression:
    return Expression("[", *_join([_get_annotation(el, parent) for el in node.elts], ", "), "]")


_node_annotation_map: dict[Type, Callable[[Any, Module | Class], str | Name | Expression]] = {
    NodeName: _get_name_annotation,
    NodeConstant: _get_constant_annotation,
    NodeAttribute: _get_attribute_annotation,
    NodeBinOp: _get_binop_annotation,
    NodeBitOr: _get_bitor_annotation,
    NodeBitAnd: _get_bitand_annotation,
    NodeSubscript: _get_subscript_annotation,
    NodeTuple: _get_tuple_annotation,
    NodeList: _get_list_annotation,
}

# TODO: remove once Python 3.8 support is dropped
if sys.version_info < (3, 9):

    def _get_index_annotation(node: NodeIndex, parent: Module | Class) -> str | Name | Expression:
        return _get_annotation(node.value, parent)

    _node_annotation_map[NodeIndex] = _get_index_annotation

# TODO: remove once Python 3.7 support is dropped
if sys.version_info < (3, 8):

    def _get_nameconstant_annotation(node: NodeNameConstant, parent: Module | Class) -> str | Name | Expression:
        if node.value is None:
            return repr(None)
        return _get_annotation(node.value, parent)

    _node_annotation_map[NodeNameConstant] = _get_nameconstant_annotation


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
        return doc.s, doc.lineno, doc.end_lineno  # type: ignore[attr-defined]
    return None, None, None


# ==========================================================
# values
def _get_name_value(node: NodeName) -> str:
    return node.id


def _get_constant_value(node: NodeConstant) -> str:
    return repr(node.value)


def _get_attribute_value(node: NodeAttribute) -> str:
    return f"{get_value(node.value)}.{node.attr}"


def _get_binop_value(node: NodeBinOp) -> str:
    return f"{get_value(node.left)} {get_value(node.op)} {get_value(node.right)}"


def _get_bitor_value(node: NodeBitOr) -> str:
    return "|"


def _get_mult_value(node: NodeMult) -> str:
    return "*"


def _get_div_value(node: NodeDiv) -> str:
    return "/"


def _get_unaryop_value(node: NodeUnaryOp) -> str:
    return f"{get_value(node.op)}{get_value(node.operand)}"


def _get_usub_value(node: NodeUSub) -> str:
    return "-"


def _get_uadd_value(node: NodeUAdd) -> str:
    return "+"


def _get_not_value(node: NodeNot) -> str:
    return "not "


def _get_slice_value(node: NodeSlice) -> str:
    value = f"{get_value(node.lower) if node.lower else ''}:{get_value(node.upper) if node.upper else ''}"
    if node.step:
        value = f"{value}:{get_value(node.step)}"
    return value


def _get_subscript_value(node: NodeSubscript) -> str:
    return f"{get_value(node.value)}[{get_value(node.slice).strip('()')}]"


def _get_lambda_value(node: NodeLambda) -> str:
    return f"lambda {get_value(node.args)}: {get_value(node.body)}"


def _get_arguments_value(node: NodeArguments) -> str:
    return ", ".join(arg.arg for arg in node.args)


def _get_list_value(node: NodeList) -> str:
    return "[" + ", ".join(get_value(el) for el in node.elts) + "]"


def _get_tuple_value(node: NodeTuple) -> str:
    return "(" + ", ".join(get_value(el) for el in node.elts) + ")"


def _get_keyword_value(node: NodeKeyword) -> str:
    return f"{node.arg}={get_value(node.value)}"


def _get_dict_value(node: NodeDict) -> str:
    pairs = zip(node.keys, node.values)
    gen = (f"{'None' if key is None else get_value(key)}: {get_value(value)}" for key, value in pairs)  # noqa: WPS509
    return "{" + ", ".join(gen) + "}"


def _get_set_value(node: NodeSet) -> str:
    return "{" + ", ".join(get_value(el) for el in node.elts) + "}"


def _get_ellipsis_value(node: NodeEllipsis) -> str:
    return "..."


def _get_starred_value(node: NodeStarred) -> str:
    return get_value(node.value)


def _get_formatted_value(node: NodeFormattedValue) -> str:
    return f"{{{get_value(node.value)}}}"


def _get_joinedstr_value(node: NodeJoinedStr) -> str:
    return "".join(get_value(value) for value in node.values)


def _get_boolop_value(node: NodeBoolOp) -> str:
    return get_value(node.op).join(get_value(value) for value in node.values)


def _get_or_value(node: NodeOr) -> str:
    return " or "


def _get_and_value(node: NodeAnd) -> str:
    return " and "


def _get_compare_value(node: NodeCompare) -> str:
    left = get_value(node.left)
    ops = [get_value(op) for op in node.ops]
    comparators = [get_value(comparator) for comparator in node.comparators]
    return f"{left} " + " ".join(f"{op} {comp}" for op, comp in zip(ops, comparators))


def _get_noteq_value(node: NodeNotEq) -> str:
    return "!="


def _get_gte_value(node: NodeNotEq) -> str:
    return ">="


def _get_gt_value(node: NodeNotEq) -> str:
    return ">"


def _get_lte_value(node: NodeNotEq) -> str:
    return "<="


def _get_lt_value(node: NodeNotEq) -> str:
    return "<"


def _get_generatorexp_value(node: NodeGeneratorExp) -> str:
    element = get_value(node.elt)
    generators = [get_value(gen) for gen in node.generators]
    return f"{element} " + " ".join(generators)


def _get_listcomp_value(node: NodeListComp) -> str:
    element = get_value(node.elt)
    generators = [get_value(gen) for gen in node.generators]
    return f"[{element} " + " ".join(generators) + "]"


def _get_dictcomp_value(node: NodeDictComp) -> str:
    key = get_value(node.key)
    value = get_value(node.value)
    generators = [get_value(gen) for gen in node.generators]
    return f"{{{key}: {value} " + " ".join(generators) + "}"


def _get_comprehension_value(node: NodeComprehension) -> str:
    target = get_value(node.target)
    iterable = get_value(node.iter)
    conditions = [get_value(condition) for condition in node.ifs]
    value = f"for {target} in {iterable}"
    if conditions:
        value = f"{value} if " + " if ".join(conditions)
    if node.is_async:
        value = f"async {value}"
    return value


def _get_ifexp_value(node: NodeIfExp) -> str:
    return f"{get_value(node.body)} if {get_value(node.test)} else {get_value(node.orelse)}"


def _get_call_value(node: NodeCall) -> str:
    posargs = ", ".join(get_value(arg) for arg in node.args)
    kwargs = ", ".join(get_value(kwarg) for kwarg in node.keywords)
    if posargs and kwargs:
        args = f"{posargs}, {kwargs}"
    elif posargs:
        args = posargs
    elif kwargs:
        args = kwargs
    else:
        args = ""
    return f"{get_value(node.func)}({args})"


_node_value_map: dict[Type, Callable[[Any], str]] = {
    type(None): lambda _: repr(None),
    NodeName: _get_name_value,
    NodeConstant: _get_constant_value,
    NodeAttribute: _get_attribute_value,
    NodeBinOp: _get_binop_value,
    NodeUnaryOp: _get_unaryop_value,
    NodeEllipsis: _get_ellipsis_value,
    NodeSubscript: _get_subscript_value,
    NodeList: _get_list_value,
    NodeTuple: _get_tuple_value,
    NodeKeyword: _get_keyword_value,
    NodeDict: _get_dict_value,
    NodeSet: _get_set_value,
    NodeFormattedValue: _get_formatted_value,
    NodeJoinedStr: _get_joinedstr_value,
    NodeCall: _get_call_value,
    NodeSlice: _get_slice_value,
    NodeBoolOp: _get_boolop_value,
    NodeGeneratorExp: _get_generatorexp_value,
    NodeComprehension: _get_comprehension_value,
    NodeCompare: _get_compare_value,
    NodeNotEq: _get_noteq_value,
    NodeGtE: _get_gte_value,
    NodeGt: _get_gt_value,
    NodeLtE: _get_lte_value,
    NodeLt: _get_lt_value,
    NodeBitOr: _get_bitor_value,
    NodeMult: _get_mult_value,
    NodeListComp: _get_listcomp_value,
    NodeLambda: _get_lambda_value,
    NodeDictComp: _get_dictcomp_value,
    NodeStarred: _get_starred_value,
    NodeIfExp: _get_ifexp_value,
    NodeOr: _get_or_value,
    NodeAnd: _get_and_value,
    NodeUSub: _get_usub_value,
    NodeUAdd: _get_uadd_value,
    NodeNot: _get_not_value,
    NodeArguments: _get_arguments_value,
    NodeDiv: _get_div_value,
}

# TODO: remove once Python 3.8 support is dropped
if sys.version_info < (3, 9):

    def _get_index_value(node: NodeIndex) -> str:
        return get_value(node.value)

    _node_value_map[NodeIndex] = _get_index_value


# TODO: remove once Python 3.7 support is dropped
if sys.version_info < (3, 8):

    def _get_str_value(node: NodeStr) -> str:
        return repr(node.s)

    def _get_nameconstant_value(node: NodeNameConstant) -> str:
        return repr(node.value)

    def _get_num_value(node: NodeNum) -> str:
        return repr(node.n)

    _node_value_map[NodeStr] = _get_str_value
    _node_value_map[NodeNameConstant] = _get_nameconstant_value
    _node_value_map[NodeNum] = _get_num_value


def get_value(node: AST) -> str:
    """Extract a complex value as a string.

    Parameters:
        node: The node to extract the value from.

    Returns:
        The unparsed code of the node.
    """
    return _node_value_map[type(node)](node)


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
def get_parameter_default(node: AST, filepath: Path, lines_collection: LinesCollection) -> str | None:
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
    if isinstance(node, NodeConstant):
        return repr(node.value)
    if isinstance(node, NodeName):
        return node.id
    if node.lineno == node.end_lineno:  # type: ignore[attr-defined]
        return lines_collection[filepath][node.lineno - 1][node.col_offset : node.end_col_offset]  # type: ignore[attr-defined]
    # TODO: handle multiple line defaults
    return None
