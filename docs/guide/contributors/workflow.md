# Development workflow

As usual:

1. create a new branch: `git switch -c feature-or-bugfix-name`
1. edit the code and/or the documentation

**Before committing:**

1. run `make format` to auto-format the code
1. run `make check` to check everything (fix any warning)
1. run `make test` to run the tests (fix any issue)
1. if you updated the documentation or the project dependencies:
    1. run `make docs`
    1. go to http://localhost:8000 and check that everything looks good
1. follow our [commit message convention](#commit-message-convention)

If you are unsure about how to fix or ignore a warning,
just let the continuous integration fail,
and we will help you during review.

Don't bother updating the changelog, we will take care of this.
