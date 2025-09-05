# YORE: Bump 2: Remove file.

from typing import Any

import griffe


class ModuleGetAttrExtension(griffe.Extension):
    def on_package(self, *, pkg: griffe.Module, **kwargs: Any) -> None:  # noqa: ARG002,D102
        if pkg.name == "griffe":
            for name in griffe._deprecated_names:
                try:
                    target = pkg[f"_internal.git._{name}"]
                except KeyError:
                    # Old version where the utility was not yet renamed.
                    continue
                pkg.set_member(name, griffe.Alias(name, target=f"griffe._internal.git._{name}"))
                admonition = griffe.DocstringSectionAdmonition(
                    kind="danger",
                    text="",
                    title="This function is deprecated and will become unavailable in the next major version.",
                )
                target.docstring.parsed.insert(1, admonition)
                target.labels.add("deprecated")
