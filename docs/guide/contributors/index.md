# Contributor guide

!!! info "For contributors and maintainers"
    This guide explains how to change Griffe itself. To use Griffe in another project, start with the [user guide](../users/index.md).

Welcome to the Griffe contributor guide! If you are familiar with Python tooling, development, and contributions to open-source projects, see the [TL;DR](#tldr) at the end, otherwise we recommend you walk through the following pages:

- [Environment setup](setup.md)
- [Management commands](commands.md)
- [Development workflow](workflow.md)

Regular contributors might be interested in the following documents that explain Griffe's design and inner workings:

- [Architecture](architecture.md)

If you are unsure about what to contribute to, you can check out [our issue tracker](https://github.com/mkdocstrings/griffe/issues) to see if some issues are interesting to you. <!--, or you could check out [our coverage report](coverage.md) to help us cover more of the codebase with tests. -->

## TL;DR

- Install [Python](https://www.python.org/), [uv](https://docs.astral.sh/uv/) and [direnv](https://direnv.net/)
- Fork, clone, and enter repository
- Run `direnv allow` and `make setup`
- Checkout a new branch
- Edit code, tests and/or documentation
- Run `make format check test docs` to check everything
- Commit, push, open PR
