---
hide:
- feedback
- navigation
- toc
---

# Welcome

<img src="logo.svg" alt="Griffe logo, created by François Rozet &lt;francois.rozet@outlook.com&gt;" title="Griffe logo, created by François Rozet &lt;francois.rozet@outlook.com&gt;" style="float: right; max-width: 200px; margin: 0 15px;">

> Griffe, pronounced "grif" (`/ɡʁif/`), is a french word that means "claw", but also "signature" in a familiar way. "On reconnaît bien là sa griffe."

<div class="grid cards" markdown>

- :material-run-fast:{ .lg .middle } **Getting started**

    ---

    Learn how to quickly install and use Griffe.

    [:octicons-download-16: Installation](installation.md){ .md-button .md-button--primary } [:material-book-open-variant: Introduction](introduction.md){ .md-button .md-button--primary }

- :material-diving-scuba:{ .lg .middle } **Deep dive**

    ---

    Learn everything you can do with Griffe.

    [:fontawesome-solid-book: Guide](guide/users.md){ .md-button .md-button--primary } [:material-code-parentheses: API reference](reference/api.md){ .md-button .md-button--primary }

</div>

## What is Griffe?

Griffe is a Python tool and library that gives you signatures for entire Python programs. It extracts the structure, the frame, the skeleton of your project, to generate API documentation or find breaking changes in your API.

Griffe can be used as a Python library. For example, the [Python handler](https://mkdocstrings.github.io/python) of [mkdocstrings](https://mkdocstrings.github.io/) uses Griffe to collect API data and render API documentation in HTML. Griffe can also be used on the command-line, to load and serialize your API data to JSON, or find breaking changes in your API since the previous version of your library.

<div class="grid cards" markdown>
<div markdown>

```console exec="1" source="console" result="json" title="Serializing as JSON"
$ export FORCE_COLOR=1  # markdown-exec: hide
$ griffe dump griffe -ssrc -r 2>/dev/null | head -n29
```

</div>
<div markdown>

```console exec="1" source="console" result="ansi" returncode="1" title="Checking for API breaking changes"
$ export FORCE_COLOR=1  # markdown-exec: hide
$ griffe check griffe -ssrc -b0.46.0 -a0.45.0 --verbose
```

</div>
</div>

[:material-play: Playground](playground.md){ .md-button }
[:simple-gitter: Join our Gitter channel](https://app.gitter.im/#/room/#mkdocstrings_griffe:gitter.im){ .md-button target="_blank" }
