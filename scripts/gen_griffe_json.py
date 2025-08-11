"""Generate the JSON API data file."""

import mkdocs_gen_files

python_handler = mkdocs_gen_files.config.plugins["mkdocstrings"].get_handler("python")
data = python_handler.collect("griffe", options=python_handler.get_options({}))

with mkdocs_gen_files.open("griffe.json", "w") as fd:
    print(data.as_json(full=True), file=fd)
