# YORE: Bump 2: Remove file.

from typing import Any

import griffelib


class ModuleGetAttrExtension(griffe.Extension):
    def on_package(self, *, pkg: griffelib.Module, **kwargs: Any) -> None:  # noqa: ARG002,D102
        if pkg.name == "griffe":
            for name in griffelib._deprecated_names:
                try:
                    target = pkg[f"_internal.git._{name}"]
                except KeyError:
                    # Old version where the utility was not yet renamed.
                    continue
                pkg.set_member(name, griffelib.Alias(name, target=f"griffe._internal.git._{name}"))
                admonition = griffelib.DocstringSectionAdmonition(
                    kind="danger",
                    text="",
                    title="This function is deprecated and will become unavailable in the next major version.",
                )
                target.docstring.parsed.insert(1, admonition)
                target.labels.add("deprecated")
