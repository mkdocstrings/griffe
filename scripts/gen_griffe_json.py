"""Generate the credits page."""

import json

import mkdocs_gen_files

from griffe.docstrings.parsers import Parser
from griffe.encoders import JSONEncoder
from griffe.loader import GriffeLoader

griffe = GriffeLoader().load_module("griffe")
serialized = json.dumps(
    griffe,
    cls=JSONEncoder,
    indent=0,
    full=True,
    docstring_parser=Parser.google,
    docstring_options={"ignore_init_summary": True},
)
with mkdocs_gen_files.open("griffe.json", "w") as fd:
    fd.write(serialized)
