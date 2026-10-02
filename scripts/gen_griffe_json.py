# SPDX-License-Identifier: ISC

# Copyright (c) 2021, Timothée Mazzucotelli and contributors

# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.

# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# Generate the JSON API data file.

import tomllib
from pathlib import Path

from griffe import load, load_extensions

project_dir = Path(__file__).resolve().parent.parent
with project_dir.joinpath("zensical.toml").open("rb") as config_file:
    project = tomllib.load(config_file)["project"]
python_config = project["plugins"]["mkdocstrings"]["handlers"]["python"]
options = python_config["options"]

data = load(
    "griffe",
    search_paths=[project_dir / path for path in python_config["paths"]],
    extensions=load_extensions(*options["extensions"]),
    docstring_parser=options["docstring_style"],
    docstring_options=options["docstring_options"],
    resolve_aliases=True,
)

with project_dir.joinpath(project.get("docs_dir", "docs"), "griffe.json").open("w", encoding="utf-8") as fd:
    print(data.as_json(full=True), file=fd)
