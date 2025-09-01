# `griffe-fastapi`

- **PyPI**: [`griffe-fastapi`](https://pypi.org/project/griffe-fastapi/)
- **GitHub**: [fbraem/griffe-fastapi](https://github.com/fbraem/griffe-fastapi)
- **Extension name:** `griffe_fastapi`

---

This extension will search for functions that are decorated with an APIRouter and adds the following extra
fields to a function:

- api: the path of the api
- method: the HTTP method
- responses: a dictionary with the responses

These fields are then rendered with a custom mkdocstrings template provided by the extension.
