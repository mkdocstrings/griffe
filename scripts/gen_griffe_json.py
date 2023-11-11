"""Generate the credits page."""

import mkdocs_gen_files

import griffe

data = griffe.load(
    "griffe",
    docstring_parser=griffe.Parser.google,
    docstring_options={"ignore_init_summary": True},
)
with mkdocs_gen_files.open("griffe.json", "w") as fd:
    fd.write(data.as_json(full=True, indent=0))
