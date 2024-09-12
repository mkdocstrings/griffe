# Downstream projects

Griffe is used by various projects in the Python ecosystem.

## griffe2md

[griffe2md](https://mkdocstrings.github.io/griffe2md/) outputs API docs in Markdown. It uses Griffe to load the data, and then use Jinja templates to render documentation in Markdown, just like [mkdocstrings-python](https://mkdocstrings.github.io/python/), but in Markdown instead of HTML.

## Griffe TUI

[:octicons-heart-fill-24:{ .pulse } Sponsors only](insiders/index.md){ .insiders }

[Griffe TUI](https://mkdocstrings.github.io/griffe-tui/) is a textual user interface for Griffe. It offers 100% offline, beautiful Python API docs, in your terminal, thanks to Griffe and [Textual](https://textual.textualize.io/).

## quartodoc

[quartodoc](https://machow.github.io/quartodoc/) lets you quickly generate Python package API reference documentation using Markdown and [Quarto](https://quarto.org/). quartodoc is designed as an alternative to [Sphinx](https://www.sphinx-doc.org/en/master/). It uses Griffe to load API data and parse docstrings in order to render HTML documentation, just like [mkdocstrings-python](https://mkdocstrings.github.io/python/), but for Quarto instead of Mkdocs.

## pydanclick

[Pydanclick](https://pypi.org/project/pydanclick/) allows to use [Pydantic](https://docs.pydantic.dev/latest/) models as [Click](https://click.palletsprojects.com/en/8.1.x/) options. It uses Griffe to parse docstrings and find Attributes sections, to help itself build Click options.

## rafe

[rafe](https://pypi.org/project/rafe/) is a tool for inspecting python environments and building packages (irrespective of language) in a reproducible manner. It wraps Griffe to provide a CLI command to check for API breaking changes.

## Yapper

[Yapper](https://pypi.org/project/yapper/) converts Python docstrings to `astro` files for use by the [Astro](https://astro.build/) static site generator. It uses Griffe to parse Python modules and extracts Numpydoc-style docstrings.
