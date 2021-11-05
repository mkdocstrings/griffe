"""Generate the code reference pages and navigation."""

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

for path in sorted(Path("src").glob("**/*.py")):
    module_path = path.relative_to("src").with_suffix("")
    doc_path = path.relative_to("src", "griffe").with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    parts = list(module_path.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    elif parts[-1] == "__main__":
        continue
    nav_parts = list(parts)
    nav[nav_parts] = doc_path

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        ident = ".".join(parts)
        print("::: " + ident, file=fd)

    mkdocs_gen_files.set_edit_path(full_doc_path, path)

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
