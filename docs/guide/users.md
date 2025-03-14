# User guide

Welcome to the Griffe user guide!

## Manipulating APIs

The following topics will guide you through the various methods Griffe offers for exploring and exploiting Python APIs.

<div class="grid cards" markdown>

- :material-cube-scan:{ .lg .middle } **Loading**

    ---

    Griffe can find packages and modules to scan them statically or dynamically and extract API-related information.

    [:octicons-arrow-right-24: Learn how to load data](users/loading.md)

- :material-navigation-variant-outline:{ .lg .middle } **Navigating**

    ---

    Griffe exposes the extracted API information into data models, making it easy to navigate your API.

    [:octicons-arrow-right-24: Learn how to navigate data](users/navigating.md)

- :material-code-json:{ .lg .middle } **Serializing**

    ---

    Griffe can serialize your API data into JSON, for other tools to navigate or manipulate it.

    [:octicons-arrow-right-24: Learn how to serialize data](users/serializing.md)

- :material-target:{ .lg .middle } **Checking**

    ---

    Griffe can compare snapshots of the same API to find breaking changes.

    [:octicons-arrow-right-24: Learn how to detect and handle breaking changes](users/checking.md)

- :material-puzzle-plus:{ .lg .middle } **Extending**

    ---

    API data can be augmented or modified thanks to Griffe's extension system.

    [:octicons-arrow-right-24: Learn how to write and use extensions](users/extending.md)

</div>

## Recommendations

These topics explore the user side: how to write code to better integrate with Griffe.

<div class="grid cards" markdown>

- :material-gift-open:{ .lg .middle } **Public API**

    ---

    See our recommendations for exposing public APIs to your users.

    [:octicons-arrow-right-24: See our public API recommendations](users/recommendations/public-apis.md)

- :material-star-face:{ .lg .middle } **Python code best practices**

    ---

    See our best practices for writing Python code.

    [:octicons-arrow-right-24: See our best practices](users/recommendations/python-code.md)

- :material-text:{ .lg .middle } **Docstrings**

    ---

    Griffe supports multiple docstring styles. Learn about these different styles, and see our recommendations to write docstrings.

    [:octicons-arrow-right-24: See our docstring recommendations](users/recommendations/docstrings.md)

</div>

## How-to

These how-tos will show you how to achieve specific things with Griffe.

<div class="grid cards" markdown>

-   :octicons-ai-model-24:{ .lg .middle } **Parse docstrings**

    ---

    Griffe can be used as a docstring-parsing library.

    [:octicons-arrow-right-24: See how to parse docstrings](users/how-to/parse-docstrings.md)

-   **@ Support custom decorators**

    ---

    Griffe will rarely support custom decorators through static analysis, but you can easily write extensions to do so.

    [:octicons-arrow-right-24: See how to support custom decorators](users/how-to/support-decorators.md)

-   :material-select:{ .lg .middle } **Selectively inspect objects**

    ---

    Sometimes static analysis is not enough, so you might want to use dynamic analysis (inspection) on certain objects.

    [:octicons-arrow-right-24: See how to selectively inspect objects](users/how-to/selectively-inspect.md)

-   :material-select:{ .lg .middle } **Set objects' docstring style**

    ---

    Sometimes the wrong docstring styles are attached to objects. You can fix this with a few different methods.

    [:octicons-arrow-right-24: See how to set the correct docstring styles on objects](users/how-to/set-docstring-styles.md)

</div>
