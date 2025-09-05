# User guide

Welcome to the Griffe user guide!

## Manipulating APIs

The following topics will guide you through the various methods Griffe offers for exploring and exploiting Python APIs.

- **Loading**

  ______________________________________________________________________

  Griffe can find packages and modules to scan them statically or dynamically and extract API-related information.

  [Learn how to load data](loading/)

- **Navigating**

  ______________________________________________________________________

  Griffe exposes the extracted API information into data models, making it easy to navigate your API.

  [Learn how to navigate data](navigating/)

- **Serializing**

  ______________________________________________________________________

  Griffe can serialize your API data into JSON, for other tools to navigate or manipulate it.

  [Learn how to serialize data](serializing/)

- **Checking**

  ______________________________________________________________________

  Griffe can compare snapshots of the same API to find breaking changes.

  [Learn how to detect and handle breaking changes](checking/)

- **Extending**

  ______________________________________________________________________

  API data can be augmented or modified thanks to Griffe's extension system.

  [Learn how to write and use extensions](extending/)

## Recommendations

These topics explore the user side: how to write code to better integrate with Griffe.

- **Public API**

  ______________________________________________________________________

  See our recommendations for exposing public APIs to your users.

  [See our public API recommendations](recommendations/public-apis/)

- **Python code best practices**

  ______________________________________________________________________

  See our best practices for writing Python code.

  [See our best practices](recommendations/python-code/)

- **Docstrings**

  ______________________________________________________________________

  Griffe supports multiple docstring styles. Learn about these different styles, and see our recommendations to write docstrings.

  [See our docstring recommendations](recommendations/docstrings/)

## How-to

These how-tos will show you how to achieve specific things with Griffe.

- **Parse docstrings**

  ______________________________________________________________________

  Griffe can be used as a docstring-parsing library.

  [See how to parse docstrings](how-to/parse-docstrings/)

- **@ Support custom decorators**

  ______________________________________________________________________

  Griffe will rarely support custom decorators through static analysis, but you can easily write extensions to do so.

  [See how to support custom decorators](how-to/support-decorators/)

- **Selectively inspect objects**

  ______________________________________________________________________

  Sometimes static analysis is not enough, so you might want to use dynamic analysis (inspection) on certain objects.

  [See how to selectively inspect objects](how-to/selectively-inspect/)

- **Set objects' docstring style**

  ______________________________________________________________________

  Sometimes the wrong docstring styles are attached to objects. You can fix this with a few different methods.

  [See how to set the correct docstring styles on objects](how-to/set-docstring-styles/)

- **Set Git source info on objects**

  ______________________________________________________________________

  Griffe tries to find the right Git remote URL to provide source links to loaded objects. In some cases you might want to override the Git information or the source link directly.

  [See how to set the correct Git information or source link on objects](how-to/set-git-info/)
