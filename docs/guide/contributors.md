# Contributor guide

Welcome to the Griffe contributor guide! If you are familiar with Python tooling, development, and contributions to open-source projects, see the [TL;DR](#tldr) at the end, otherwise we recommend you walk through the following pages:

- [Environment setup](contributors/setup.md)
- [Management commands](contributors/commands.md)
- [Development workflow](contributors/workflow.md)

Regular contributors might be interested in the following documents that explain Griffe's design and inner workings:

- [Architecture](contributors/architecture.md)

If you are unsure about what to contribute to, you can check out [our issue tracker](https://github.com/mkdocstrings/griffe/issues) to see if some issues are interesting to you, or you could check out [our coverage report](contributors/coverage.md) to help us cover more of the codebase with tests.

## TL;DR

- Install [Python](https://www.python.org/), [uv](https://docs.astral.sh/uv/) and [direnv](https://direnv.net/)
- Fork, clone, and enter repository
- Run `direnv allow` and `make setup`
- Checkout a new branch
- Edit code, tests and/or documentation
- Run `make format check test docs` to check everything
- Commit, push, open PR
