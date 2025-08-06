# Environment setup

To work on the project, whether to update the code or the documentation, you will have to setup a development environment.

## Requirements

The only requirement is that you have [Python](https://www.python.org/) and [uv](https://docs.astral.sh/uv/) installed and available on your command line path.

```
curl -LsSf https://astral.sh/uv/install.sh | sh

```

See [Installation methods](https://docs.astral.sh/uv/getting-started/installation/).

```
pip install --user uv

```

[pip](https://pip.pypa.io/en/stable/) is the main package installer for Python.

```
pipx install uv

```

[pipx](https://pipx.pypa.io/stable/) allows to install and run Python applications in isolated environments.

```
rye install uv

```

[Rye](https://rye.astral.sh/) is an all-in-one solution for Python project management, written in Rust.

Optionally, we recommend using [direnv](https://direnv.net/), which will add our `scripts` folder to your path when working on the project, allowing to call our `make` Python script with the usual `make` command.

## Fork and clone

[Fork the repository on GitHub](https://github.com/mkdocstrings/griffe/fork), then clone it locally:

```
gh repo clone griffe

```

The [`gh` GitHub CLI](https://cli.github.com/) allows you to interact with GitHub on the command line.

```
git clone git@github.com:your-username/griffe

```

See the documentation on GitHub for [Connecting with SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh) and for [Cloning a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository).

```
git clone https://github.com/your-username/griffe

```

See the documentation on GitHub for [Cloning a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository).

## Install dependencies

First, enter the repository.

If you installed [direnv](https://direnv.net/):

- run `direnv allow`
- run `make setup`

If you didn't install [direnv](https://direnv.net/), just run `./scripts/make setup`.

The setup command will install all the Python dependencies required to work on the project. This command will create a virtual environment in the `.venv` folder, as well as one virtual environment per supported Python version in the `.venvs/3.x` folders. If you cloned the repository on the same file-system as [uv](https://docs.astral.sh/uv/)'s cache, everything will be hard linked from the cache, so don't worry about wasting disk space.

## IDE setup

If you work in VSCode, we provide [a command to configure VSCode](../commands/#vscode) for the project.
