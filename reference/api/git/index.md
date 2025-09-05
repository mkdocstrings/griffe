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
