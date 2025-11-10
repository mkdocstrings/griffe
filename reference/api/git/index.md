# Git utilities

Deprecated utilities.

We have decided to stop exposing Git-related utilities as it's not a core part of the library's functionality. The functions documented on this page will become unavailable in the next major version.

## assert_git_repo

```
assert_git_repo(path: str | Path) -> None
```

Deprecated. Assert that a directory is a Git repository.

This function is deprecated and will become unavailable in the next major version.

Parameters:

- ### **`path`**

  (`str | Path`) – Path to a directory.

Raises:

- `OSError` – When the directory is not a Git repository.

Source code in `src/griffe/_internal/git.py`

```
def _assert_git_repo(path: str | Path) -> None:
    """Deprecated. Assert that a directory is a Git repository.

    Parameters:
        path: Path to a directory.

    Raises:
        OSError: When the directory is not a Git repository.
    """
    if not shutil.which("git"):
        raise RuntimeError("Could not find git executable. Please install git.")
    try:
        _git("-C", str(path), "rev-parse", "--is-inside-work-tree")
    except GitError as error:
        raise OSError(f"Not a git repository: {path}") from error
```

## get_latest_tag

```
get_latest_tag(repo: str | Path) -> str
```

Deprecated. Get latest tag of a Git repository.

This function is deprecated and will become unavailable in the next major version.

Parameters:

- ### **`repo`**

  (`str | Path`) – The path to Git repository.

Returns:

- `str` – The latest tag.

Source code in `src/griffe/_internal/git.py`

```
def _get_latest_tag(repo: str | Path) -> str:
    """Deprecated. Get latest tag of a Git repository.

    Parameters:
        repo: The path to Git repository.

    Returns:
        The latest tag.
    """
    if isinstance(repo, str):
        repo = Path(repo)
    if not repo.is_dir():
        repo = repo.parent
    try:
        output = _git("tag", "-l", "--sort=-creatordate")
    except GitError as error:
        raise GitError(f"Cannot list Git tags in {repo}: {error or 'no tags'}") from error
    return output.split("\n", 1)[0]
```

## get_repo_root

```
get_repo_root(repo: str | Path) -> Path
```

Deprecated. Get the root of a Git repository.

This function is deprecated and will become unavailable in the next major version.

Parameters:

- ### **`repo`**

  (`str | Path`) – The path to a Git repository.

Returns:

- `Path` – The root of the repository.

Source code in `src/griffe/_internal/git.py`

```
def _get_repo_root(repo: str | Path) -> Path:
    """Deprecated. Get the root of a Git repository.

    Parameters:
        repo: The path to a Git repository.

    Returns:
        The root of the repository.
    """
    if isinstance(repo, str):
        repo = Path(repo)
    if not repo.is_dir():
        repo = repo.parent
    return Path(_git("-C", str(repo), "rev-parse", "--show-toplevel"))
```

## tmp_worktree

```
tmp_worktree(
    repo: str | Path = ".", ref: str = "HEAD"
) -> Iterator[Path]
```

Deprecated. Context manager that checks out the given reference in the given repository to a temporary worktree.

This function is deprecated and will become unavailable in the next major version.

Parameters:

- ### **`repo`**

  (`str | Path`, default: `'.'` ) – Path to the repository (i.e. the directory containing the .git directory)

- ### **`ref`**

  (`str`, default: `'HEAD'` ) – A Git reference such as a commit, tag or branch.

Yields:

- `Path` – The path to the temporary worktree.

Raises:

- `OSError` – If repo is not a valid .git repository
- `RuntimeError` – If the git executable is unavailable, or if it cannot create a worktree

Source code in `src/griffe/_internal/git.py`

```
@contextmanager
def _tmp_worktree(repo: str | Path = ".", ref: str = "HEAD") -> Iterator[Path]:
    """Deprecated. Context manager that checks out the given reference in the given repository to a temporary worktree.

    Parameters:
        repo: Path to the repository (i.e. the directory *containing* the `.git` directory)
        ref: A Git reference such as a commit, tag or branch.

    Yields:
        The path to the temporary worktree.

    Raises:
        OSError: If `repo` is not a valid `.git` repository
        RuntimeError: If the `git` executable is unavailable, or if it cannot create a worktree
    """
    _assert_git_repo(repo)
    repo_name = Path(repo).resolve().name
    normref = _normalize(ref)  # Branch names can contain slashes.
    with TemporaryDirectory(prefix=f"{_WORKTREE_PREFIX}{repo_name}-{normref}-") as tmp_dir:
        location = os.path.join(tmp_dir, normref)  # noqa: PTH118
        tmp_branch = f"griffe-{normref}"  # Temporary branch name must not already exist.
        try:
            _git("-C", str(repo), "worktree", "add", "-b", tmp_branch, location, ref)
        except GitError as error:
            raise RuntimeError(f"Could not create git worktree: {error}") from error

        try:
            yield Path(location)
        finally:
            _git("-C", str(repo), "worktree", "remove", location, check=False)
            _git("-C", str(repo), "worktree", "prune", check=False)
            _git("-C", str(repo), "branch", "-D", tmp_branch, check=False)
```
