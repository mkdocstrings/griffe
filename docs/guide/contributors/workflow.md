# Development workflow

This document describes our workflow when developing features, fixing bugs and updating the documentation. It also includes guidelines for pull requests on GitHub.

## Features and bug fixes

The development worklow is rather usual.

**For a new feature:**

1. create a new branch: `git switch -c feat-summary`
2. edit the code and the documentation
3. write new tests

**For a bug fix:**

1. create a new branch: `git switch -c fix-summary`
2. write tests that fail but are expected to pass once the bug is fixed
3. run [`make test`][task-test] to make sure the new tests fail
4. fix the code

**For a docs update:**

<div class="annotate" markdown>

1. create a new branch: `git switch -c docs-summary`
2. start the live reloading server: `make docs` (1)
3. update the documentation
4. preview changes at http://localhost:8000

</div>

1. To speed-up the live reloading, disable mkdocstrings with `MKDOCSTRINGS_ENABLED=false make docs`.

**Before committing:**

1. run [`make format`][task-format] to auto-format the code
2. run [`make check`][task-check] to check everything (fix any warning)
3. run [`make test`][task-test] to run the tests (fix any issue)
4. if you updated the documentation or the project dependencies:
    1. run [`make docs`][task-docs]
    2. go to http://localhost:8000 and check that everything looks good

Once you are ready to commit, follow our [commit message convention](#commit-message-convention).

NOTE: **Occasional contributors**  
If you are unsure about how to fix or ignore a warning, just let the continuous integration fail, and we will help you during review. Don't bother updating the changelog, we will take care of this.

## Breaking changes and deprecations

Breaking changes should generally be avoided. If we decide to add a breaking change anyway, we should first allow a deprecation period. To deprecate parts of the API, check [Griffe's hints on how to deprecate things](../users/checking.md).

Use [`make check-api`][task-check-api] to check if there are any breaking changes. All of them should allow deprecation periods. Run this command again until no breaking changes are detected.

Deprecated code should also be marked as legacy code. We use [Yore](https://pawamoy.github.io/yore/) to mark legacy code. Similarly, code branches made to support older version of Python should be marked as legacy code using Yore too.

Examples:

```python title="Remove function when we bump to 2.0"
# YORE: Bump 2: Remove block.
def deprecated_function():
    ...
```

```python title="Simplify imports when Python 3.9 is EOL"
# YORE: EOL 3.9: Replace block with line 4.
try:
    import ...
except ImportError:
    import ...
```

Check [Yore's docs](https://pawamoy.github.io/yore/), and Yore-comments in our own code base (`git grep -A1 YORE`) to learn how to use it.

NOTE: **Occasional contributors**  
If you are unsure about how to deprecate something or mark legacy code, let us do it during review.

## Commit message convention

Commit messages must follow our convention based on the [Angular style](https://gist.github.com/stephenparish/9941e89d80e2bc58a153#format-of-the-commit-message) or the [Karma convention](https://karma-runner.github.io/4.0/dev/git-commit-msg.html):

```
type(scope): Subject

Body.
```

**Subject and body must be valid Markdown.** Subject must have proper casing (uppercase for first letter if it makes sense), but no dot at the end, and no punctuation in general. Example:

```
feat: Add CLI option to run in verbose mode
```

Scope and body are optional. Type can be:

- `build`: About packaging, building wheels, etc.
- `chore`: About packaging or repo/files management.
- `ci`: About Continuous Integration.
- `deps`: Dependencies update.
- `docs`: About documentation.
- `feat`: New feature.
- `fix`: Bug fix.
- `perf`: About performance.
- `refactor`: Changes that are not features or bug fixes.
- `style`: A change in code style/format.
- `tests`: About tests.

If you write a body, please add trailers at the end (for example issues and PR references, or co-authors), without relying on GitHub's flavored Markdown:

```
This is the body of the commit message.

Issue-10: https://github.com/namespace/project/issues/10
Related-to-PR-namespace/other-project#15: https://github.com/namespace/other-project/pull/15
```

These "trailers" must appear at the end of the body, without any blank lines between them. The trailer title can contain any character except colons `:`. We expect a full URI for each trailer, not just GitHub autolinks (for example, full GitHub URLs for commits and issues, not the hash or the #issue-number).

We do not enforce a line length on commit messages summary and body.

NOTE: **Occasional contributors**  
If this convention seems unclear to you, just write the message of your choice, and we will rewrite it ourselves before merging.

## Pull requests guidelines

Link to any related issue in the Pull Request message.

During the review, we recommend using fixups:

```bash
# SHA is the SHA of the commit you want to fix
git commit --fixup=SHA
```

Once all the changes are approved, you can squash your commits:

```bash
git rebase -i --autosquash main
```

And force-push:

```bash
git push -f
```

NOTE: **Occasional contributors**  
If this seems all too complicated, you can push or force-push each new commit, and we will squash them ourselves if needed, before merging.

## Release process

Occasional or even regular contributors don't *have* to read this, but can anyway if they are interested in our release process.

Once we are ready for a new release (a few bugfixes and/or features merged in the main branch), maintainers should update the changelog. If our [commit message convention](workflow.md#commit-message-convention) was properly followed, the changelog can be automatically updated from the messages in the Git history with [`make changelog`][task-changelog]. This task updates the changelog in place to add a new version entry.

Once the changelog is updated, maintainers should review the new version entry, to:

- (optionally) add general notes for this new version, like highlights
- insert **Breaking changes** and **Deprecations** sections if needed, before other sections
- add links to the relevant parts of the documentation
- fix typos or markup if needed

Once the changelog is ready, a new release can be made with [`make release`][task-release]. If the version wasn't passed on the command-line with `make release version=x.x.x`, the task will prompt you for it. **Use the same version as the one that was just added to the changelog.** For example if the new version added to the changelog is `7.8.9`, use `make release version=7.8.9`.

The [release task][task-release] will stage the changelog, commit, tag, push, then build distributions and upload them to PyPI.org, and finally deploy the documentation. If any of these steps fail, you can manually run each step with Git commands, then [`make build`][task-build], [`make publish`][task-publish] and [`make docs-deploy`][task-docs-deploy].
