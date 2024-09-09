# Docstrings

Here are explanations on what docstrings are, and a few recommendations on how to write them. This guide uses the [Google-style](../../../reference/docstrings.md#google-style), because that is our preferred and recommended style, but you can also use any other supported style. Skip to the [Styles](#styles) section to learn about the existing docstring styles. We invite you to read their own style guides as they are full of examples and good advice.

## Definition

A docstring is a line or block of text describing objects such as modules, classes, functions and attributes. They are written below the object signature or assignment, or appear as first expression in a module:

```python title="module.py"
"""This is the module docstring."""

a = 0
"""This is an attribute docstring."""


def b():
    """This is a function docstring."""


class C:
    """This is a class docstring."""

    def d(self):
        """This is a method docstring."""
```

## Multi-line docstrings

Each docstring can span multiple lines if it is wrapped in triple double-quotes (which is generally the case and the official recommendation even for single-line docstrings):

```python
def function():
    """This is a longer docstring.

    It spans on multiple lines.
    Blank lines are allowed, too.
    """
```

When writing multi-line docstrings, it is recommended to write a short description on the first line, then separate the rest of the docstring with a blank line. The first line is called the **summary**, and the rest of docstring is called the **body**. The summary is useful to documentation generators and other tools to show the short description of an object.

## Markup

Docstrings are just text, so you can use any markup you want. The markup you choose will generally depend on what you decide to do with your docstrings: if you generate API documentation from your docstrings, and the documentation renderer expects Markdown, then you should write your docstrings in Markdown.

Examples of markups are [Markdown](https://daringfireball.net/projects/markdown/) (which has many different implementations and many different "flavors"), [reStructuredText](https://docutils.sourceforge.io/rst.html), [AsciiDoc](https://asciidoc.org/), and [Djot](https://djot.net/).

For example, if you are using [MkDocs](https://www.mkdocs.org) and [mkdocstrings](https://mkdocstrings.github.io/) to generate your API documentation, you should write your docstrings in Markdown. If you are using [Sphinx](https://www.sphinx-doc.org/en/master/), you should probably write your docstrings in reStructuredText, unless you are also using the [MyST](https://myst-parser.readthedocs.io/en/latest/index.html) extension.

Whatever markup you choose, try to stay consistent within your code base.

## Styles

Docstrings can be written for modules, classes, functions, and attributes. But there are other aspects of a Python API that need to be documented, such as function parameters, returned values, and raised exceptions, to name a few. We could document everything in natural language, but that would make it hard for downstream tools such as documentation generators to extract information in a structured way, to allow dedicated rendering such as tables for parameters.

To compensate for the lack of structure in natural languages, docstring "styles" emerged. A docstring style is a micro-format for docstrings, allowing to structure the information by following a specific format. With the most popular Google and Numpydoc styles, information in docstrings is decomposed into **sections** of different kinds, for example "parameter" sections or "return" sections. Some kinds of section then support documenting multiple items, or support a single block of markup. For example, we can document multiple parameters in "parameter" sections, but a "note" section is only composed of a text block.

Structuring the information in sections and items allows documentation-related tools to extract and provide this information in a structured way, by parsing the docstrings according to the style they follow. Griffe has parsers for [Google-style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings), [Numpydoc-style](https://numpydoc.readthedocs.io/en/latest/format.html), and [Sphinx-style](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html) docstrings. See the complete reference for these parsers and styles in the [Docstrings reference](../../../reference/docstrings.md). We recommend that you read the style guides mentioned here as they are full of examples and good advice too.

<div class="grid cards" markdown>
<div markdown>

```python title="Google-style"
def greet(name: str, end: str = "!") -> None:
    """Greet someone.

    Parameters:
        name: The name to greet.
        end: The punctuation mark at the end.

    Note:
        Greetings are cool!
    """
    print(f"Hey {name}{end}")



‎
```

<!-- The invisible character above is here on purpose, to make both divs the same height. -->

</div>
<div markdown>

```python title="Numpydoc-style"
def greet(name: str, end: str = "!") -> None:
    """Greet someone.

    Parameters
    ----------
    name
        The name to greet.
    end
        The punctuation mark at the end.

    Note
    ----
    Greetings are cool!
    """
    print(f"Hey {name}{end}")
```

</div>
</div>

Our preferred style for docstrings is the **Google-style**, because it is in our opinion the most markup-agnostic style: it is based on any kind of markup or documentation generator. Our second choice would be the Numpydoc-style, for its readability.

For the adventurers, have a look at [PEP 727](https://peps.python.org/pep-0727/) (draft) and [griffe-typingdoc](https://mkdocstrings.github.io/griffe-typingdoc/), a Griffe extension to support PEP 727. PEP 727 proposes an alternative way to provide information in a structured way, that does not rely on a docstring micro-format. It takes advantage of `typing.Annotated` to attach documentation to any type-annotated object, like attributes, parameters and returned values. With PEP 727, docstrings styles and their sections aren't required anymore, and docstrings can be written in plain markup, without following any particular style. This makes it easier for tools like Griffe who then don't have to parse docstrings *at all*. The PEP is a bit controversial (lots of different opinions), so we invite you to make your own opinion by looking at real-world projects using it, such as [FastAPI](https://github.com/tiangolo/fastapi/blob/master/fastapi/applications.py), or by reading the (very-long) [discussion on discuss.python.org](https://discuss.python.org/t/pep-727-documentation-metadata-in-typing/32566/17). The PEP was actually written by FastAPI's author, Sebastián Ramírez.

```python title="PEP 727"
from typing_extensions import Annotated, Doc


def greet(
    name: Annotated[str, Doc("The name to greet."),
    end: Annotated[str, Doc("The punctuation mark at the end.")] = "!",
) -> None:
    """Greet someone.

    > [!NOTE]
    > Greetings are cool!
    """ # (1)!
    print(f"Hey {name}{end}")
```

1. Here we use the [GitHub syntax](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#alerts) for a "note" callout. It assumes our documentation renderer supports this syntax. The point is that we rely purely on Markdown rather than docstrings styles.

## General tips

Your docstrings will typically be used to document your API, either on a deployed (static) website, or locally, on the command line or in a Python interpreter. Therefore, when writing your docstrings, you should address to the right audience: the users of your code. Try to stay succinct and give clear examples. Docstrings are not really the place to explain architectural or technical decisions made while developing the project: this information, while extremely valuable, is better written in *code comments*, where the audience is other developers working on the code base.

Your docstrings will typically again be read online (HTML) or other types of documents such as manual pages or PDFs. Make sure to write complete sentences, with correct punctuation. That means for example, to start each parameter description with a capital letter, and to end it with a period.

When documenting objects acting as namespaces (modules, classes, enumerations), prefer documenting each attribute separately than with an Attributes section in the namespace object docstring. For example, add a docstring to each enumeration value rather than describing each value in the docstring of the enumeration class.

## Modules

Module docstrings should briefly explain what the module contains, and for what purposes these objects can be used. If the documentation generator you chose does not support generating member summaries automatically, you might want to add docstrings sections for attributes, functions, classes and submodules.

```python title="package/__init__.py"
"""A generic package to demonstrate docstrings.

This package does not really exist, and is only used as a demonstration purpose for docstrings.
Anyway, this package contains the following API, exposed directly at the top-level,
meaning you can import everything from `package` directly.

Attributes:
    ghost: A ghost wandering in this desolated land.
    dummy: A dummy you can practice on. Not for ghosts.

Classes:
    Ghost: Ah, so this is where our ghost comes from.
        Maybe create some additional ghosts so they can pass the time together?

Functions:
    deploy(): Deploy something on the web (we're not sure what exactly).
"""
```

Do the same thing for every other module of the package, except if you are [hiding your module layout](public-apis.md#module-layout).

## Classes, methods, properties

Class docstrings follow the same logic as module docstrings. Explain what the class is used for, and maybe show a few of its attributes and methods thanks to sections of the same name. A class is already more concrete than a module, so we can maybe start adding usage examples too. Such examples should only show how to create instances of the class. Examples of use for methods can be written in each respective method.

```python
class Ghost:
    """Ghosts that wander the earth.

    Ghosts are meant to... we're actually unsure.
    All we know is that, as a user, you might find it amusing to instantiate
    a few of them and put them together to see what they do.

    Methods:
        wander: Wander the earth.
        spook: Spook living organisms.
        pass_through: Pass through anything.

    Examples:
        Create a new ghost with a cool nickname:

        >>> ghost = Ghost(nickname="Rattlesnake")
    """

    def wander(self) -> None:
        """Wander the earth.
        
        That's it, really.

        Examples:
            >>> ghost.wander()
        """
        ...

    @property
    def weight(self) -> int:
        """The ghost's weight (spoiler: it's close to 0)."""
        ...
```

Note that blocks of lines starting with `>>>` or `...` are automatically parsed as code blocks by Griffe, until a blank line is found. This only works in Examples (plural!) sections. If you rely on [Python-Markdown](https://python-markdown.github.io/) to convert Markdown to HTML (which is the case for MkDocs), you can use the [markdown-pycon](https://pawamoy.github.io/markdown-pycon/) extension to recognize such `pycon` code blocks anywhere, without having to wrap them in fences. You can also choose to use explicit fences everywhere:

````python
    """
    Examples:
        Create a new ghost with a cool nickname:

        ```pycon
        >>> ghost = Ghost(nickname="Rattlesnake")
        ```
    """
````

## Functions

Function and method docstrings will typically describe their parameters and return values. For generators, it's also possible to describe what the generator yields and what it can receive, though the latter is not often used.

```python
import datetime
from typing import Generator, Iterator


class GhostOlympicGames:
    ...


class GOGTicket:
    ...


def organize_gog(date: datetime.date) -> GhostOlympicGames:
    """Organize Olympic Games for Ghosts.

    The ghost world is much simpler than the living world,
    so it's super easy to organize big events like this.

    Parameters:
        date: The date of the games.

    Returns:
        The prepared games.
    """
    ...


def yield_athletes(quantity: int) -> Iterator[Ghost]:
    """Yield a certain quantity of athletes.

    Parameters:
        quantity: How many ghost athletes you want.
    
    Yields:
        Ghost athletes. They're just regular ghosts.
    """
    ...



def gog_tickets_factory() -> Generator[GOGTicket, int, None]:
    """Generate tickets for the GOG.

    We value fairness: tickets are priced randomly.
    Unless we send a specific price to the generator.

    Yields:
        Tickets for the games.

    Receives:
        Price for the next ticket, in ghost money (???).
    """
    ...
```

## Attributes

Attribute docstrings are written below their assignment. As usual, they should have a short summary, and an optional, longer body.

```python
GHOST_MASS_CONSTANT: float = 1e-100
"""The ghost mass constant.

This is a very small number. Use it scientifically
for all ghost-related things.

Note:
    There is actually nothing scientific about any of this.
""" # (1)!
```

1. Our `Note` section here is parsed as an admonition. See [Google-style admonitions](../../../reference/docstrings.md#google-admonitions) for reference.

Class and instance attributes can be documented the same way:

```python
class GhostTown:
    instances: str
    """All the existing towns."""

    def __init__(self, name: str, size: int) -> None:
        self.name = name
        """The town's name."""

        self.size = size
        """The town's size."""
```

## Exceptions, warnings

Callables that raise exception or emit warnings can document each of these exceptions and warnings. Documenting them informs your users that they could or should catch the raised exceptions, or that they could filter or configure warnings differently. The description next to each exception or warning should explain how or when they are raised or emitted.

```python
def verify_spirit_chest():
    """Do a verification routine on the spirit chest.

    Raises:
        OverflowError: When the verification failed
            and all the ghosts escaped from the spirit chest.
    """
    ...


def negotiate_return_to_the_spirit_chest():
    """Negotiate with ghost for them to return in the spirit chest.

    Warns:
        ResourceWarning: When the ghosts refuse to go back in the chest
            because the chest is too tight.
    """
    ...
```

## Going further

There are more sections and more features to discover and use. For a complete reference on docstring styles syntax, see our [reference](../../../reference/docstrings.md).
