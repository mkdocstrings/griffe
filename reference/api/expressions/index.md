# Expressions

## **Helpers**

## get_annotation

```
get_annotation = partial(get_expression, parse_strings=None)

```

## get_base_class

```
get_base_class = partial(
    get_expression, parse_strings=False
)

```

## get_condition

```
get_condition = partial(get_expression, parse_strings=False)

```

## get_expression

```
get_expression(
    node: AST | None,
    parent: Module | Class,
    *,
    member: str | None = None,
    parse_strings: bool | None = None,
) -> Expr | None

```

Build an expression from an AST.

Parameters:

- ### **`node`**

  (`AST | None`) – The annotation node.

- ### **`parent`**

  (`Module | Class`) – The parent used to resolve the name.

- ### **`member`**

  (`str | None`, default: `None` ) – The member name (for resolution in its scope).

- ### **`parse_strings`**

  (`bool | None`, default: `None` ) – Whether to try and parse strings as type annotations.

Returns:

- `Expr | None` – A string or resovable name or expression.

## safe_get_annotation

```
safe_get_annotation = partial(
    safe_get_expression,
    parse_strings=None,
    msg_format=_msg_format % "annotation",
)

```

## safe_get_base_class

```
safe_get_base_class = partial(
    safe_get_expression,
    parse_strings=False,
    msg_format=_msg_format % "base class",
)

```

## safe_get_condition

```
safe_get_condition = partial(
    safe_get_expression,
    parse_strings=False,
    msg_format=_msg_format % "condition",
)

```

## safe_get_expression

```
safe_get_expression(
    node: AST | None,
    parent: Module | Class,
    *,
    member: str | None = None,
    parse_strings: bool | None = None,
    log_level: LogLevel | None = error,
    msg_format: str = "{path}:{lineno}: Failed to get expression from {node_class}: {error}",
) -> Expr | None

```

Safely (no exception) build a resolvable annotation.

Parameters:

- ### **`node`**

  (`AST | None`) – The annotation node.

- ### **`parent`**

  (`Module | Class`) – The parent used to resolve the name.

- ### **`member`**

  (`str | None`, default: `None` ) – The member name (for resolution in its scope).

- ### **`parse_strings`**

  (`bool | None`, default: `None` ) – Whether to try and parse strings as type annotations.

- ### **`log_level`**

  (`LogLevel | None`, default: `error` ) – Log level to use to log a message. None to disable logging.

- ### **`msg_format`**

  (`str`, default: `'{path}:{lineno}: Failed to get expression from {node_class}: {error}'` ) – A format string for the log message. Available placeholders: path, lineno, node, error.

Returns:

- `Expr | None` – A string or resovable name or expression.

## **Expression nodes**

## Expr

```
Expr()

```

Base class for expressions.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`path`** (`str`) – Path of the expressed name/attribute.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### path

```
path: str

```

Path of the expressed name/attribute.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprAttribute

```
ExprAttribute(values: list[str | Expr])

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprAttribute[ExprAttribute]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprAttribute
                


              click griffe.ExprAttribute href "" "griffe.ExprAttribute"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Attributes like `a.b`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`append`** – Append a name to this attribute.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – The canonical path of this attribute.
- **`classname`** (`str`) – The expression class name.
- **`first`** (`str | Expr`) – The first part of this attribute (on the left).
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`last`** (`ExprName`) – The last part of this attribute (on the right).
- **`path`** (`str`) – The path of this attribute.
- **`values`** (`list[str | Expr]`) – The different parts of the dotted chain.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

The canonical path of this attribute.

### classname

```
classname: str

```

The expression class name.

### first

```
first: str | Expr

```

The first part of this attribute (on the left).

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### last

```
last: ExprName

```

The last part of this attribute (on the right).

### path

```
path: str

```

The path of this attribute.

### values

```
values: list[str | Expr]

```

The different parts of the dotted chain.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### append

```
append(value: ExprName) -> None

```

Append a name to this attribute.

Parameters:

- #### **`value`**

  (`ExprName`) – The expression name to append.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> ExprName | ExprAttribute

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprBinOp

```
ExprBinOp(
    left: str | Expr, operator: str, right: str | Expr
)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprBinOp[ExprBinOp]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprBinOp
                


              click griffe.ExprBinOp href "" "griffe.ExprBinOp"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Binary operations like `a + b`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`left`** (`str | Expr`) – Left part.
- **`operator`** (`str`) – Binary operator.
- **`path`** (`str`) – Path of the expressed name/attribute.
- **`right`** (`str | Expr`) – Right part.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### left

```
left: str | Expr

```

Left part.

### operator

```
operator: str

```

Binary operator.

### path

```
path: str

```

Path of the expressed name/attribute.

### right

```
right: str | Expr

```

Right part.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprBoolOp

```
ExprBoolOp(operator: str, values: Sequence[str | Expr])

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprBoolOp[ExprBoolOp]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprBoolOp
                


              click griffe.ExprBoolOp href "" "griffe.ExprBoolOp"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Boolean operations like `a or b`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`operator`** (`str`) – Boolean operator.
- **`path`** (`str`) – Path of the expressed name/attribute.
- **`values`** (`Sequence[str | Expr]`) – Operands.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### operator

```
operator: str

```

Boolean operator.

### path

```
path: str

```

Path of the expressed name/attribute.

### values

```
values: Sequence[str | Expr]

```

Operands.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprCall

```
ExprCall(function: Expr, arguments: Sequence[str | Expr])

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprCall[ExprCall]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprCall
                


              click griffe.ExprCall href "" "griffe.ExprCall"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Calls like `f()`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`arguments`** (`Sequence[str | Expr]`) – Passed arguments.
- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – The canonical path of this subscript's left part.
- **`classname`** (`str`) – The expression class name.
- **`function`** (`Expr`) – Function called.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`path`** (`str`) – Path of the expressed name/attribute.

### arguments

```
arguments: Sequence[str | Expr]

```

Passed arguments.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

The canonical path of this subscript's left part.

### classname

```
classname: str

```

The expression class name.

### function

```
function: Expr

```

Function called.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### path

```
path: str

```

Path of the expressed name/attribute.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprCompare

```
ExprCompare(
    left: str | Expr,
    operators: Sequence[str],
    comparators: Sequence[str | Expr],
)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprCompare[ExprCompare]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprCompare
                


              click griffe.ExprCompare href "" "griffe.ExprCompare"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Comparisons like `a > b`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`comparators`** (`Sequence[str | Expr]`) – Things compared.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`left`** (`str | Expr`) – Left part.
- **`operators`** (`Sequence[str]`) – Comparison operators.
- **`path`** (`str`) – Path of the expressed name/attribute.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### comparators

```
comparators: Sequence[str | Expr]

```

Things compared.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### left

```
left: str | Expr

```

Left part.

### operators

```
operators: Sequence[str]

```

Comparison operators.

### path

```
path: str

```

Path of the expressed name/attribute.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprComprehension

```
ExprComprehension(
    target: str | Expr,
    iterable: str | Expr,
    conditions: Sequence[str | Expr],
    is_async: bool = False,
)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprComprehension[ExprComprehension]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprComprehension
                


              click griffe.ExprComprehension href "" "griffe.ExprComprehension"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Comprehensions like `a for b in c if d`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`conditions`** (`Sequence[str | Expr]`) – Conditions to include the target in the result.
- **`is_async`** (`bool`) – Async comprehension or not.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`iterable`** (`str | Expr`) – Value iterated on.
- **`path`** (`str`) – Path of the expressed name/attribute.
- **`target`** (`str | Expr`) – Comprehension target (value added to the result).

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### conditions

```
conditions: Sequence[str | Expr]

```

Conditions to include the target in the result.

### is_async

```
is_async: bool = False

```

Async comprehension or not.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### iterable

```
iterable: str | Expr

```

Value iterated on.

### path

```
path: str

```

Path of the expressed name/attribute.

### target

```
target: str | Expr

```

Comprehension target (value added to the result).

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprConstant

```
ExprConstant(value: str)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprConstant[ExprConstant]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprConstant
                


              click griffe.ExprConstant href "" "griffe.ExprConstant"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Constants like `"a"` or `1`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`path`** (`str`) – Path of the expressed name/attribute.
- **`value`** (`str`) – Constant value.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### path

```
path: str

```

Path of the expressed name/attribute.

### value

```
value: str

```

Constant value.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprDict

```
ExprDict(
    keys: Sequence[str | Expr | None],
    values: Sequence[str | Expr],
)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprDict[ExprDict]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprDict
                


              click griffe.ExprDict href "" "griffe.ExprDict"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Dictionaries like `{"a": 0}`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`keys`** (`Sequence[str | Expr | None]`) – Dict keys.
- **`path`** (`str`) – Path of the expressed name/attribute.
- **`values`** (`Sequence[str | Expr]`) – Dict values.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### keys

```
keys: Sequence[str | Expr | None]

```

Dict keys.

### path

```
path: str

```

Path of the expressed name/attribute.

### values

```
values: Sequence[str | Expr]

```

Dict values.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprDictComp

```
ExprDictComp(
    key: str | Expr,
    value: str | Expr,
    generators: Sequence[Expr],
)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprDictComp[ExprDictComp]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprDictComp
                


              click griffe.ExprDictComp href "" "griffe.ExprDictComp"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Dict comprehensions like `{k: v for k, v in a}`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`generators`** (`Sequence[Expr]`) – Generators iterated on.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`key`** (`str | Expr`) – Target key.
- **`path`** (`str`) – Path of the expressed name/attribute.
- **`value`** (`str | Expr`) – Target value.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### generators

```
generators: Sequence[Expr]

```

Generators iterated on.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### key

```
key: str | Expr

```

Target key.

### path

```
path: str

```

Path of the expressed name/attribute.

### value

```
value: str | Expr

```

Target value.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprExtSlice

```
ExprExtSlice(dims: Sequence[str | Expr])

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprExtSlice[ExprExtSlice]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprExtSlice
                


              click griffe.ExprExtSlice href "" "griffe.ExprExtSlice"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Extended slice like `a[x:y, z]`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`dims`** (`Sequence[str | Expr]`) – Dims.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`path`** (`str`) – Path of the expressed name/attribute.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### dims

```
dims: Sequence[str | Expr]

```

Dims.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### path

```
path: str

```

Path of the expressed name/attribute.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprFormatted

```
ExprFormatted(value: str | Expr)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprFormatted[ExprFormatted]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprFormatted
                


              click griffe.ExprFormatted href "" "griffe.ExprFormatted"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Formatted string like `{1 + 1}`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`path`** (`str`) – Path of the expressed name/attribute.
- **`value`** (`str | Expr`) – Formatted value.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### path

```
path: str

```

Path of the expressed name/attribute.

### value

```
value: str | Expr

```

Formatted value.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprGeneratorExp

```
ExprGeneratorExp(
    element: str | Expr, generators: Sequence[Expr]
)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprGeneratorExp[ExprGeneratorExp]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprGeneratorExp
                


              click griffe.ExprGeneratorExp href "" "griffe.ExprGeneratorExp"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Generator expressions like `a for b in c for d in e`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`element`** (`str | Expr`) – Yielded element.
- **`generators`** (`Sequence[Expr]`) – Generators iterated on.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`path`** (`str`) – Path of the expressed name/attribute.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### element

```
element: str | Expr

```

Yielded element.

### generators

```
generators: Sequence[Expr]

```

Generators iterated on.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### path

```
path: str

```

Path of the expressed name/attribute.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprIfExp

```
ExprIfExp(
    body: str | Expr, test: str | Expr, orelse: str | Expr
)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprIfExp[ExprIfExp]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprIfExp
                


              click griffe.ExprIfExp href "" "griffe.ExprIfExp"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Conditions like `a if b else c`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`body`** (`str | Expr`) – Value if test.
- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`orelse`** (`str | Expr`) – Other expression.
- **`path`** (`str`) – Path of the expressed name/attribute.
- **`test`** (`str | Expr`) – Condition.

### body

```
body: str | Expr

```

Value if test.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### orelse

```
orelse: str | Expr

```

Other expression.

### path

```
path: str

```

Path of the expressed name/attribute.

### test

```
test: str | Expr

```

Condition.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprJoinedStr

```
ExprJoinedStr(values: Sequence[str | Expr])

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprJoinedStr[ExprJoinedStr]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprJoinedStr
                


              click griffe.ExprJoinedStr href "" "griffe.ExprJoinedStr"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Joined strings like `f"a {b} c"`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`path`** (`str`) – Path of the expressed name/attribute.
- **`values`** (`Sequence[str | Expr]`) – Joined values.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### path

```
path: str

```

Path of the expressed name/attribute.

### values

```
values: Sequence[str | Expr]

```

Joined values.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprKeyword

```
ExprKeyword(
    name: str,
    value: str | Expr,
    function: Expr | None = None,
)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprKeyword[ExprKeyword]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprKeyword
                


              click griffe.ExprKeyword href "" "griffe.ExprKeyword"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Keyword arguments like `a=b`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed keyword.
- **`classname`** (`str`) – The expression class name.
- **`function`** (`Expr | None`) – Expression referencing the function called with this parameter.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`name`** (`str`) – Name.
- **`path`** (`str`) – Path of the expressed name/attribute.
- **`value`** (`str | Expr`) – Value.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed keyword.

### classname

```
classname: str

```

The expression class name.

### function

```
function: Expr | None = None

```

Expression referencing the function called with this parameter.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### name

```
name: str

```

Name.

### path

```
path: str

```

Path of the expressed name/attribute.

### value

```
value: str | Expr

```

Value.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprVarPositional

```
ExprVarPositional(value: Expr)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprVarPositional[ExprVarPositional]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprVarPositional
                


              click griffe.ExprVarPositional href "" "griffe.ExprVarPositional"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Variadic positional parameters like `*args`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`path`** (`str`) – Path of the expressed name/attribute.
- **`value`** (`Expr`) – Starred value.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### path

```
path: str

```

Path of the expressed name/attribute.

### value

```
value: Expr

```

Starred value.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprVarKeyword

```
ExprVarKeyword(value: Expr)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprVarKeyword[ExprVarKeyword]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprVarKeyword
                


              click griffe.ExprVarKeyword href "" "griffe.ExprVarKeyword"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Variadic keyword parameters like `**kwargs`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`path`** (`str`) – Path of the expressed name/attribute.
- **`value`** (`Expr`) – Double-starred value.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### path

```
path: str

```

Path of the expressed name/attribute.

### value

```
value: Expr

```

Double-starred value.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprLambda

```
ExprLambda(
    parameters: Sequence[ExprParameter], body: str | Expr
)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprLambda[ExprLambda]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprLambda
                


              click griffe.ExprLambda href "" "griffe.ExprLambda"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Lambda expressions like `lambda a: a.b`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`body`** (`str | Expr`) – Lambda's body.
- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`parameters`** (`Sequence[ExprParameter]`) – Lambda's parameters.
- **`path`** (`str`) – Path of the expressed name/attribute.

### body

```
body: str | Expr

```

Lambda's body.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### parameters

```
parameters: Sequence[ExprParameter]

```

Lambda's parameters.

### path

```
path: str

```

Path of the expressed name/attribute.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprList

```
ExprList(elements: Sequence[Expr])

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprList[ExprList]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprList
                


              click griffe.ExprList href "" "griffe.ExprList"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Lists like `[0, 1, 2]`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`elements`** (`Sequence[Expr]`) – List elements.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`path`** (`str`) – Path of the expressed name/attribute.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### elements

```
elements: Sequence[Expr]

```

List elements.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### path

```
path: str

```

Path of the expressed name/attribute.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprListComp

```
ExprListComp(
    element: str | Expr, generators: Sequence[Expr]
)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprListComp[ExprListComp]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprListComp
                


              click griffe.ExprListComp href "" "griffe.ExprListComp"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

List comprehensions like `[a for b in c]`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`element`** (`str | Expr`) – Target value.
- **`generators`** (`Sequence[Expr]`) – Generators iterated on.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`path`** (`str`) – Path of the expressed name/attribute.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### element

```
element: str | Expr

```

Target value.

### generators

```
generators: Sequence[Expr]

```

Generators iterated on.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### path

```
path: str

```

Path of the expressed name/attribute.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprName

```
ExprName(
    name: str,
    parent: str
    | ExprName
    | Module
    | Class
    | Function
    | None = None,
    member: str | None = None,
)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprName[ExprName]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprName
                


              click griffe.ExprName href "" "griffe.ExprName"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

This class represents a Python object identified by a name in a given scope.

Methods:

- **`__eq__`** – Two name expressions are equal if they have the same name value (parent is ignored).
- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – The canonical name (resolved one, not alias name).
- **`classname`** (`str`) – The expression class name.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_enum_class`** (`bool`) – Whether this name resolves to an enumeration class.
- **`is_enum_instance`** (`bool`) – Whether this name resolves to an enumeration instance.
- **`is_enum_value`** (`bool`) – Whether this name resolves to an enumeration value.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`is_type_parameter`** (`bool`) – Whether this name resolves to a type parameter.
- **`member`** (`str | None`) – Member name (for resolution in its scope).
- **`name`** (`str`) – Actual name.
- **`parent`** (`str | ExprName | Module | Class | Function | None`) – Parent (for resolution in its scope).
- **`path`** (`str`) – The full, resolved name.
- **`resolved`** (`Module | Class | None`) – The resolved object this name refers to.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

The canonical name (resolved one, not alias name).

### classname

```
classname: str

```

The expression class name.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_enum_class

```
is_enum_class: bool

```

Whether this name resolves to an enumeration class.

### is_enum_instance

```
is_enum_instance: bool

```

Whether this name resolves to an enumeration instance.

### is_enum_value

```
is_enum_value: bool

```

Whether this name resolves to an enumeration value.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### is_type_parameter

```
is_type_parameter: bool

```

Whether this name resolves to a type parameter.

### member

```
member: str | None = None

```

Member name (for resolution in its scope).

### name

```
name: str

```

Actual name.

### parent

```
parent: (
    str | ExprName | Module | Class | Function | None
) = None

```

Parent (for resolution in its scope).

### path

```
path: str

```

The full, resolved name.

If it was given when creating the name, return that. If a callable was given, call it and return its result. It the name cannot be resolved, return the source.

### resolved

```
resolved: Module | Class | None

```

The resolved object this name refers to.

### __eq__

```
__eq__(other: object) -> bool

```

Two name expressions are equal if they have the same `name` value (`parent` is ignored).

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[ExprName]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> ExprName

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprNamedExpr

```
ExprNamedExpr(target: Expr, value: str | Expr)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprNamedExpr[ExprNamedExpr]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprNamedExpr
                


              click griffe.ExprNamedExpr href "" "griffe.ExprNamedExpr"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Named/assignment expressions like `a := b`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`path`** (`str`) – Path of the expressed name/attribute.
- **`target`** (`Expr`) – Target name.
- **`value`** (`str | Expr`) – Value.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### path

```
path: str

```

Path of the expressed name/attribute.

### target

```
target: Expr

```

Target name.

### value

```
value: str | Expr

```

Value.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprParameter

```
ExprParameter(
    name: str,
    kind: ParameterKind = positional_or_keyword,
    annotation: Expr | None = None,
    default: str | Expr | None = None,
)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprParameter[ExprParameter]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprParameter
                


              click griffe.ExprParameter href "" "griffe.ExprParameter"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Parameters in function signatures like `a: int = 0`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`annotation`** (`Expr | None`) – Parameter type.
- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`default`** (`str | Expr | None`) – Parameter default.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`kind`** (`ParameterKind`) – Parameter kind.
- **`name`** (`str`) – Parameter name.
- **`path`** (`str`) – Path of the expressed name/attribute.

### annotation

```
annotation: Expr | None = None

```

Parameter type.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### default

```
default: str | Expr | None = None

```

Parameter default.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### kind

```
kind: ParameterKind = positional_or_keyword

```

Parameter kind.

### name

```
name: str

```

Parameter name.

### path

```
path: str

```

Path of the expressed name/attribute.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprSet

```
ExprSet(elements: Sequence[str | Expr])

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprSet[ExprSet]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprSet
                


              click griffe.ExprSet href "" "griffe.ExprSet"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Sets like `{0, 1, 2}`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`elements`** (`Sequence[str | Expr]`) – Set elements.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`path`** (`str`) – Path of the expressed name/attribute.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### elements

```
elements: Sequence[str | Expr]

```

Set elements.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### path

```
path: str

```

Path of the expressed name/attribute.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprSetComp

```
ExprSetComp(
    element: str | Expr, generators: Sequence[Expr]
)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprSetComp[ExprSetComp]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprSetComp
                


              click griffe.ExprSetComp href "" "griffe.ExprSetComp"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Set comprehensions like `{a for b in c}`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`element`** (`str | Expr`) – Target value.
- **`generators`** (`Sequence[Expr]`) – Generators iterated on.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`path`** (`str`) – Path of the expressed name/attribute.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### element

```
element: str | Expr

```

Target value.

### generators

```
generators: Sequence[Expr]

```

Generators iterated on.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### path

```
path: str

```

Path of the expressed name/attribute.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprSlice

```
ExprSlice(
    lower: str | Expr | None = None,
    upper: str | Expr | None = None,
    step: str | Expr | None = None,
)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprSlice[ExprSlice]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprSlice
                


              click griffe.ExprSlice href "" "griffe.ExprSlice"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Slices like `[a:b:c]`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`lower`** (`str | Expr | None`) – Lower bound.
- **`path`** (`str`) – Path of the expressed name/attribute.
- **`step`** (`str | Expr | None`) – Iteration step.
- **`upper`** (`str | Expr | None`) – Upper bound.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### lower

```
lower: str | Expr | None = None

```

Lower bound.

### path

```
path: str

```

Path of the expressed name/attribute.

### step

```
step: str | Expr | None = None

```

Iteration step.

### upper

```
upper: str | Expr | None = None

```

Upper bound.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprSubscript

```
ExprSubscript(left: str | Expr, slice: str | Expr)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprSubscript[ExprSubscript]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprSubscript
                


              click griffe.ExprSubscript href "" "griffe.ExprSubscript"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Subscripts like `a[b]`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – The canonical path of this subscript's left part.
- **`classname`** (`str`) – The expression class name.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`left`** (`str | Expr`) – Left part.
- **`path`** (`str`) – The path of this subscript's left part.
- **`slice`** (`str | Expr`) – Slice part.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

The canonical path of this subscript's left part.

### classname

```
classname: str

```

The expression class name.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### left

```
left: str | Expr

```

Left part.

### path

```
path: str

```

The path of this subscript's left part.

### slice

```
slice: str | Expr

```

Slice part.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> ExprBinOp | ExprSubscript

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprTuple

```
ExprTuple(
    elements: Sequence[str | Expr], implicit: bool = False
)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprTuple[ExprTuple]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprTuple
                


              click griffe.ExprTuple href "" "griffe.ExprTuple"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Tuples like `(0, 1, 2)`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`elements`** (`Sequence[str | Expr]`) – Tuple elements.
- **`implicit`** (`bool`) – Whether the tuple is implicit (e.g. without parentheses in a subscript's slice).
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`path`** (`str`) – Path of the expressed name/attribute.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### elements

```
elements: Sequence[str | Expr]

```

Tuple elements.

### implicit

```
implicit: bool = False

```

Whether the tuple is implicit (e.g. without parentheses in a subscript's slice).

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### path

```
path: str

```

Path of the expressed name/attribute.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> ExprTuple

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprUnaryOp

```
ExprUnaryOp(operator: str, value: str | Expr)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprUnaryOp[ExprUnaryOp]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprUnaryOp
                


              click griffe.ExprUnaryOp href "" "griffe.ExprUnaryOp"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Unary operations like `-1`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`operator`** (`str`) – Unary operator.
- **`path`** (`str`) – Path of the expressed name/attribute.
- **`value`** (`str | Expr`) – Value.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### operator

```
operator: str

```

Unary operator.

### path

```
path: str

```

Path of the expressed name/attribute.

### value

```
value: str | Expr

```

Value.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprYield

```
ExprYield(value: str | Expr | None = None)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprYield[ExprYield]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprYield
                


              click griffe.ExprYield href "" "griffe.ExprYield"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Yield statements like `yield a`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`path`** (`str`) – Path of the expressed name/attribute.
- **`value`** (`str | Expr | None`) – Yielded value.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### path

```
path: str

```

Path of the expressed name/attribute.

### value

```
value: str | Expr | None = None

```

Yielded value.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.

## ExprYieldFrom

```
ExprYieldFrom(value: str | Expr)

```

Bases: `Expr`

```

              flowchart TD
              griffe.ExprYieldFrom[ExprYieldFrom]
              _griffe.expressions.Expr[Expr]

                              _griffe.expressions.Expr --> griffe.ExprYieldFrom
                


              click griffe.ExprYieldFrom href "" "griffe.ExprYieldFrom"
              click _griffe.expressions.Expr href "" "_griffe.expressions.Expr"
            
```

Yield statements like `yield from a`.

Methods:

- **`__iter__`** – Iterate on the expression syntax and elements.
- **`as_dict`** – Return the expression as a dictionary.
- **`iterate`** – Iterate on the expression elements.
- **`modernize`** – Modernize the expression.

Attributes:

- **`canonical_name`** (`str`) – Name of the expressed name/attribute/parameter.
- **`canonical_path`** (`str`) – Path of the expressed name/attribute.
- **`classname`** (`str`) – The expression class name.
- **`is_classvar`** (`bool`) – Whether this attribute is annotated with ClassVar.
- **`is_generator`** (`bool`) – Whether this expression is a generator.
- **`is_iterator`** (`bool`) – Whether this expression is an iterator.
- **`is_tuple`** (`bool`) – Whether this expression is a tuple.
- **`path`** (`str`) – Path of the expressed name/attribute.
- **`value`** (`str | Expr`) – Yielded-from value.

### canonical_name

```
canonical_name: str

```

Name of the expressed name/attribute/parameter.

### canonical_path

```
canonical_path: str

```

Path of the expressed name/attribute.

### classname

```
classname: str

```

The expression class name.

### is_classvar

```
is_classvar: bool

```

Whether this attribute is annotated with `ClassVar`.

### is_generator

```
is_generator: bool

```

Whether this expression is a generator.

### is_iterator

```
is_iterator: bool

```

Whether this expression is an iterator.

### is_tuple

```
is_tuple: bool

```

Whether this expression is a tuple.

### path

```
path: str

```

Path of the expressed name/attribute.

### value

```
value: str | Expr

```

Yielded-from value.

### __iter__

```
__iter__() -> Iterator[str | Expr]

```

Iterate on the expression syntax and elements.

### as_dict

```
as_dict(**kwargs: Any) -> dict[str, Any]

```

Return the expression as a dictionary.

Parameters:

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Configuration options (none available yet).

Returns:

- `dict[str, Any]` – A dictionary.

### iterate

```
iterate(*, flat: bool = True) -> Iterator[str | Expr]

```

Iterate on the expression elements.

Parameters:

- #### **`flat`**

  (`bool`, default: `True` ) – Expressions are trees. When flat is false, this method iterates only on the first layer of the tree. To iterate on all the subparts of the expression, you have to do so recursively. It allows to handle each subpart specifically (for example subscripts, attribute, etc.), without them getting rendered as strings. On the contrary, when flat is true, the whole tree is flattened as a sequence of strings and instances of Names.

Yields:

- `str | Expr` – Strings and names when flat, strings and expressions otherwise.

### modernize

```
modernize() -> Expr

```

Modernize the expression.

For example, use PEP 604 type unions `|` instead of `typing.Union`.

Returns:

- `Expr` – A modernized expression.
