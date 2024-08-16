# Alternatives

Similar projects exist in the ecosystem. They generally allow to extract API data from Python source, or to build a representation of the Python source or Python API. Some of them also allow to compare representations to find breaking changes.

## Docspec

[Docspec](https://github.com/NiklasRosenstein/python-docspec) is a JSON object specification for representing API documentation of programming languages. While in it's current form it is targeting Python APIs, it is intended to be able to represent other programming languages in the future as well.

The repository contains two projects, docspec and docspec-python. **docspec** is the reference implementation for reading/writing the JSON format and API for representing API objects in memory. **docspec-python** is a parser for Python packages and modules based on lib2to3 producing docspec API object representations.

## Frappucino

[Frappucino](https://github.com/Carreau/frappuccino) allows you to make sure you haven't broken your API, by first taking an imprint of your API at one point in time and then compare it to the current project state. The goal is to warn you when incompatible changes have been introduced, and to list these changes.

## Other related projects

The work of [@tristanlatr](https://github.com/tristanlatr) is worth checking out, notably his [ast-nodes](https://github.com/tristanlatr/ast-nodes) and [astuce](https://github.com/tristanlatr/astuce) projects, which aim at providing lower-level Python AST utilities to help implementing API data extraction with powerful inference. Tristan is [advocating for more interoperability](https://github.com/mkdocstrings/griffe/discussions/287) between Docspec, Griffe and his own projects.

We should also mention our own simplified "Griffe" variants for other programming languages, such as [Griffe TypeDoc](https://mkdocstrings.github.io/griffe-typedoc/), which extracts API data from TypeScript sources thanks to [TypeDoc](https://typedoc.org/), and builds Python objects from it.

---

The following projects are more than API data extraction tools, but deserve being mentioned.

### Papyri

[Papyri](https://github.com/jupyter/papyri) is a set of tools to build, publish (future functionality - to be done), install and render documentation within IPython and Jupyter.

Papyri [has considered using Griffe in the past](https://github.com/jupyter/papyri/issues/249) :heart:, but eventually went with their own solution, trying to be compatible with Griffe serialization format.

### pdoc

[pdoc](https://github.com/mitmproxy/pdoc) is a documentation renderer for Python projects. pdoc's main feature is a focus on simplicity: pdoc aims to do one thing and do it well.

### Sphinx AutoAPI

[Sphinx AutoAPI](https://github.com/readthedocs/sphinx-autoapi) is a new approach to API documentation in Sphinx. It is a Sphinx extension for generating complete API documentation without needing to load, run, or import the project being documented. In contrast to the traditional [Sphinx autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html), which requires manual authoring and uses code imports, AutoAPI finds and generates documentation by parsing source code.

Sphinx AutoAPI is [considering Griffe as a data extraction backend](https://github.com/readthedocs/sphinx-autoapi/issues/444) :heart:
