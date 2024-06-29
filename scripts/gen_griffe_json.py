"""Generate the credits page."""

import mkdocs_gen_files

import griffe

with mkdocs_gen_files.open("griffe.json", "w") as fd:
    griffe.dump(
        ["griffe", "_griffe"],
        docstring_parser=griffe.Parser.google,
        docstring_options={"ignore_init_summary": True},
        output=fd,
    )
