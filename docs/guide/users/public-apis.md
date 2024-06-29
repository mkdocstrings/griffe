# Public APIs

what is public api?

conventions (private, class-private, `from ... import x as x`, wildcards and `__all__`)

modules: internal vs public, private package

classes: no `__all__`, have to rely on names

globally: unique names

cli is part of the api

linters and "protected usage" warnings

tests (all public objects exposed, all names unique, all public objects documented in api reference, nothing else added to inventory)

third-party libraries (modul, public, slothy)