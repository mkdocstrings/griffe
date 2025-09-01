# Downstream projects

Griffe is used by various projects in the Python ecosystem.

## api2mdx

[api2mdx](https://github.com/Mirascope/api2mdx) is a Python tool that generates `mdx` documentation for Python APIs. Under the hood, it uses Griffe.

## griffe2md

[griffe2md](https://mkdocstrings.github.io/griffe2md/) outputs API docs in Markdown. It uses Griffe to load the data, and then use Jinja templates to render documentation in Markdown, just like [mkdocstrings-python](https://mkdocstrings.github.io/python/), but in Markdown instead of HTML.

## Griffe TUI

[Griffe TUI](https://mkdocstrings.github.io/griffe-tui/) is a textual user interface for Griffe. It offers 100% offline, beautiful Python API docs, in your terminal, thanks to Griffe and [Textual](https://textual.textualize.io/).

## Griffonner

[Griffonner](https://will-langdale.github.io/griffonner/) is a template-first Python documentation generator that gets out of your way. Griffonner uses Griffe to parse your Python code and Jinja2 templates to generate docs in any format you want.

## Hippogriffe

[Hippogriffe](https://github.com/patrick-kidger/hippogriffe) is a set of tweaks on top of the MkDocs + mkdocstrings-python + Griffe documentation stack. It adds source links to GitHub to each top-level class or function, pretty-formats type annotations, improves unions/generics display, and more. Hippogriffe is used as a MkDocs plugin.

## mkdocstrings-python

Of course, Griffe is what powers [the Python handler of mkdocstrings](https://mkdocstrings.github.io/python/). mkdocstrings is a plugin for [MkDocs](https://www.mkdocs.org/) that allows rendering API docs easily.

## OpenAI Agents SDK

The [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) is a lightweight yet powerful framework for building multi-agent workflows. It was inspired by Pydantic AI and uses Griffe the same way, to parse docstrings in order to generate function schemas.

## pydanclick

[Pydanclick](https://pypi.org/project/pydanclick/) allows to use [Pydantic](https://docs.pydantic.dev/latest/) models as [Click](https://click.palletsprojects.com/en/8.1.x/) options. It uses Griffe to parse docstrings and find Attributes sections, to help itself build Click options.

## PydanticAI

[PydanticAI](https://ai.pydantic.dev/) is a Python Agent Framework designed to make it less painful to build production grade applications with Generative AI. It uses Griffe to extract tool and parameter descriptions from docstrings.

## quartodoc

[quartodoc](https://machow.github.io/quartodoc/) lets you quickly generate Python package API reference documentation using Markdown and [Quarto](https://quarto.org/). quartodoc is designed as an alternative to [Sphinx](https://www.sphinx-doc.org/en/master/). It uses Griffe to load API data and parse docstrings in order to render HTML documentation, just like [mkdocstrings-python](https://mkdocstrings.github.io/python/), but for Quarto instead of Mkdocs.

## rafe

[rafe](https://pypi.org/project/rafe/) is a tool for inspecting Python environments and building packages (irrespective of language) in a reproducible manner. It wraps Griffe to provide a CLI command to check for API breaking changes.

## Yapper

[Yapper](https://pypi.org/project/yapper/) converts Python docstrings to `astro` files for use by the [Astro](https://astro.build/) static site generator. It uses Griffe to parse Python modules and extracts Numpydoc-style docstrings.
