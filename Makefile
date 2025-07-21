# If you have `direnv` loaded in your shell, and allow it in the repository,
# the `make` command will point at the `scripts/make` shell script.
# This Makefile is just here to allow auto-completion in the terminal.

# The first target in the makefile is the default goal when no targets are specified.
# Having "help:" here above without any rule (nothing to do specified with a tab)
# only adds dependencies to that target, that is defined through "$(actions):".
# .DEFAULT_GOAL is not necessary here, but is really explicit about what is going on.
help:
.DEFAULT_GOAL: help

actions = \
	allrun \
	changelog \
	check \
	check-api \
	check-docs \
	check-quality \
	check-types \
	clean \
	coverage \
	docs \
	docs-deploy \
	format \
	help \
	multirun \
	release \
	run \
	setup \
	test \
	vscode

.PHONY: $(actions)
$(actions):
	@python scripts/make "$@"
