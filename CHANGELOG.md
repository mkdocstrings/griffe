# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [1.4.0](https://github.com/mkdocstrings/griffe/releases/tag/1.4.0) - 2024-10-11

<small>[Compare with 1.3.2](https://github.com/mkdocstrings/griffe/compare/1.3.2...1.4.0)</small>

### Features

- Add Markdown and GitHub output formats to the `griffe check` command ([806805c](https://github.com/mkdocstrings/griffe/commit/806805c3970a7cf3f32eec436255ea1323a60e1a) by Timothée Mazzucotelli).

## [1.3.2](https://github.com/mkdocstrings/griffe/releases/tag/1.3.2) - 2024-10-01

<small>[Compare with 1.3.1](https://github.com/mkdocstrings/griffe/compare/1.3.1...1.3.2)</small>

### Bug Fixes

- Normalize paths of temporary Git worktrees ([0821e67](https://github.com/mkdocstrings/griffe/commit/0821e6784e5a3aeb56020867c8b46f9477621ed3) by Timothée Mazzucotelli). [Issue-324](https://github.com/mkdocstrings/griffe/issues/324)

## [1.3.1](https://github.com/mkdocstrings/griffe/releases/tag/1.3.1) - 2024-09-12

<small>[Compare with 1.3.0](https://github.com/mkdocstrings/griffe/compare/1.3.0...1.3.1)</small>

### Bug Fixes

- Refactor and fix logic again for fetching returns/yields/receives annotation from parents ([a80bd3c](https://github.com/mkdocstrings/griffe/commit/a80bd3c0cc14e5f6efc30fb804b8c7fccb319276) by Timothée Mazzucotelli). [Follow-up-of-PR-322](https://github.com/mkdocstrings/griffe/pull/322)
- Don't crash on invalid signature given "Receives" section ([1cb8f51](https://github.com/mkdocstrings/griffe/commit/1cb8f514eae9d588cfce8cbbfc3ef84d7deadb47) by Timothée Mazzucotelli).

## [1.3.0](https://github.com/mkdocstrings/griffe/releases/tag/1.3.0) - 2024-09-10

<small>[Compare with 1.2.0](https://github.com/mkdocstrings/griffe/compare/1.2.0...1.3.0)</small>

### Features

- Allow deselecting multiple or named items in Yields and Receives ([344df50](https://github.com/mkdocstrings/griffe/commit/344df50bfcd66ddb3b8d8250babb40012cbc82b5) by Marco Ricci). [Issue-263](https://github.com/mkdocstrings/griffe/issues/263)

### Bug Fixes

- Don't crash when trying to merge stubs into a compiled module that has no file path ([e1f3ed9](https://github.com/mkdocstrings/griffe/commit/e1f3ed9ad3b046bf137de22f855bb392a76ca116) by Timothée Mazzucotelli). [Issue-323](https://github.com/mkdocstrings/griffe/issues/323)
- Fix identity checks in inspector when handling attributes ([676cfb4](https://github.com/mkdocstrings/griffe/commit/676cfb44a79e059f74514ff492035e930ed57d03) by Timothée Mazzucotelli).

### Code Refactoring

- Extract common functionality in Returns, Yields and Receives parsing ([c768356](https://github.com/mkdocstrings/griffe/commit/c768356023e1fedaaa3f896b073457a0af34ce0e) by Marco Ricci). [Issue-263](https://github.com/mkdocstrings/griffe/issues/263)
- Remove useless branch in `resolve` method, add tests for it ([aa6c7e4](https://github.com/mkdocstrings/griffe/commit/aa6c7e4d3dbabef384193b778cfdafd05a7102c2) by Timothée Mazzucotelli).

## [1.2.0](https://github.com/mkdocstrings/griffe/releases/tag/1.2.0) - 2024-08-23

<small>[Compare with 1.1.1](https://github.com/mkdocstrings/griffe/compare/1.1.1...1.2.0)</small>

### Features

- Support attribute syntax in `__all__` values ([ad99794](https://github.com/mkdocstrings/griffe/commit/ad997940b136d315787fcb11c03fc70a40c7e8c2) by Timothée Mazzucotelli). [Issue-316](https://github.com/mkdocstrings/griffe/issues/316)

## [1.1.1](https://github.com/mkdocstrings/griffe/releases/tag/1.1.1) - 2024-08-20

<small>[Compare with 1.1.0](https://github.com/mkdocstrings/griffe/compare/1.1.0...1.1.1)</small>

### Bug Fixes

- Preemptively expand `__all__` values and wildcard imports before firing the `on_package_loaded` event ([21b3780](https://github.com/mkdocstrings/griffe/commit/21b3780b1a3f7ac62a3380089857a720b646dc4a) by Timothée Mazzucotelli).

## [1.1.0](https://github.com/mkdocstrings/griffe/releases/tag/1.1.0) - 2024-08-17

<small>[Compare with 1.0.0](https://github.com/mkdocstrings/griffe/compare/1.0.0...1.1.0)</small>

### Features

- Add `on_wildcard_expansion` event ([c6bc6fa](https://github.com/mkdocstrings/griffe/commit/c6bc6fa858a43ea2180f97fd270075d7ee7169e3) by Timothée Mazzucotelli). [Issue-282](https://github.com/mkdocstrings/griffe/issues/282)
- Add `on_alias` event ([a760a8c](https://github.com/mkdocstrings/griffe/commit/a760a8c684cae0da6b6cc83e37d1d374bfeed662) by Timothée Mazzucotelli). [Issue-282](https://github.com/mkdocstrings/griffe/issues/282)
- Pass `loader` to `on_package_loaded` hooks ([7f82dc3](https://github.com/mkdocstrings/griffe/commit/7f82dc382f1f20ee9e5f58a9ef7a775563894056) by Timothée Mazzucotelli).

## [1.0.0](https://github.com/mkdocstrings/griffe/releases/tag/1.0.0) - 2024-08-15

<small>[Compare with 0.49.0](https://github.com/mkdocstrings/griffe/compare/0.49.0...1.0.0)</small>

**V1!** :rocket: :fire: :rainbow:

### Breaking changes

Highlights:

- Extensions inherit from `Extension`, (`VisitorExtension` and `InspectorExtension` are removed)
- Members are serialized (`as_dict`/JSON) as a dictionary instead of a list
- All objects are available in the top-level `griffe` module, nowhere else

Removed objects:

- all modules under the `griffe` package
- the `griffe.DocstringWarningCallable` class
- the `griffe.When` class
- the `griffe.ExtensionType` type
- the `griffe.InspectorExtension` class
- the `griffe.VisitorExtension` class
- the `griffe.HybridExtension` extension
- the `griffe.patch_logger` function
- the `griffe.JSONEncoder.docstring_parser` attribute
- the `griffe.JSONEncoder.docstring_options` attribute
- the `griffe.Extensions.attach_visitor` method
- the `griffe.Extensions.attach_inspector` method
- the `griffe.Extensions.before_visit` method
- the `griffe.Extensions.before_children_visit` method
- the `griffe.Extensions.after_children_visit` method
- the `griffe.Extensions.after_visit` method
- the `griffe.Extensions.before_inspection` method
- the `griffe.Extensions.before_children_inspection` method
- the `griffe.Extensions.after_children_inspection` method
- the `griffe.Extensions.after_inspection` method
- the `griffe.GriffeLoader.load_module` method
- the `has_special_name` and `has_private_name` properties on objects
- the `is_explicitely_exported` and `is_implicitely_exported` properties on objects
- the `member_is_exported` method on objects


Renamed/moved objects:

- `griffe.Function.setter` -> `griffe.Attribute.setter`
- `griffe.Function.deleter` -> `griffe.Attribute.deleter`

Signatures:

- `griffe.docstring_warning(name)` parameter was removed
- `griffe.GriffeLoader.load(module)` parameter was removed
- `griffe.load(module)` parameter was removed
- `griffe.load_git(module)` parameter was removed
- `griffe.find_breaking_changes(ignore_private)` parameter was removed
- see previous deprecations

### Code Refactoring

- Remove all legacy code for v1 ([86d321e](https://github.com/mkdocstrings/griffe/commit/86d321ed1303f7bde28950f14ea75412be1d6888) and [fd72083](https://github.com/mkdocstrings/griffe/commit/fd72083fa06c3eb4ef76fe74c5126eef308766c0)by Timothée Mazzucotelli). [PR-314](https://github.com/mkdocstrings/griffe/pull/314)

## [0.49.0](https://github.com/mkdocstrings/griffe/releases/tag/0.49.0) - 2024-08-14

<small>[Compare with 0.48.0](https://github.com/mkdocstrings/griffe/compare/0.48.0...0.49.0)</small>

WARNING: **⚡ Imminent v1! ⚡🚀 See [v0.46](#0460-2024-06-16).**

### Deprecations

- Cancel deprecation of `get_logger` and `patch_loggers` (and deprecate `patch_logger` instead). Extensions need loggers too, distinct ones, and they were forgotten... Sorry for the back and forth 🙇
- Attributes `setter` and `deleter` on `Function` are deprecated. They were moved into the `Attribute` class since properties are instantiated as attributes, not functions.
- Extension hooks must accept `**kwargs` in their signature, to allow forward-compatibility. Accepting `**kwargs` also makes it possible to remove unused arguments from the signature.
- In version 1, Griffe will serialize object members as dictionaries instead of lists. Lists were initially used to preserve source order, but source order can be re-obtained thanks to the line number attributes (`lineno`, `endlineno`). Version 0.49 is able to load both lists and dictionaries from JSON dumps, and version 1 will maintain this ability. However external tools loading JSON dumps will need to be updated.

### Features

- Add `temporary_inspected_package` helper ([3c4ba16](https://github.com/mkdocstrings/griffe/commit/3c4ba160ca4c3407bc60d9125e0d93ae5e08d8f3) by Timothée Mazzucotelli).
- Accept alias resolution related parameters in `temporary_visited_package` ([7d5408a](https://github.com/mkdocstrings/griffe/commit/7d5408a3bf81d64841bbe620b883bc16cb633f82) by Timothée Mazzucotelli).
- Accept `inits` parameter in `temporary_visited_package` ([a4859b7](https://github.com/mkdocstrings/griffe/commit/a4859b74bf52ca29cbb46c147a2b6df4532297e1) by Timothée Mazzucotelli).
- Warn (DEBUG) when an object coming from a sibling, parent or external module instead of the current module or a submodule is exported (listed in `__all__`) ([f82317a](https://github.com/mkdocstrings/griffe/commit/f82317a00333e1b8971625f14e4452e93e9840ff) by Timothée Mazzucotelli). [Issue-249](https://github.com/mkdocstrings/griffe/issues/249), [Related-to-PR-251](https://github.com/mkdocstrings/griffe/pull/251)
- Pass down agent to extension hooks ([71acb01](https://github.com/mkdocstrings/griffe/commit/71acb018716031331bc26d79bc27fd45f67735c1) by Timothée Mazzucotelli). [Issue-312](https://github.com/mkdocstrings/griffe/issues/312)
- Add `source` property to docstrings, which return the docstring lines as written in the source ([3f6a71a](https://github.com/mkdocstrings/griffe/commit/3f6a71a34f503e95fad55038292e3c8ab2ce30b6) by Timothée Mazzucotelli). [Issue-90](https://github.com/mkdocstrings/griffe/issues/90)

### Bug Fixes

- Move `setter` and `deleter` to `Attribute` class instead of `Function`, since that's how properties are instantiated ([309c6e3](https://github.com/mkdocstrings/griffe/commit/309c6e34aded516dcfeab0dd81c2fbcecd2691ac) by Timothée Mazzucotelli). [Issue-311](https://github.com/mkdocstrings/griffe/issues/311)
- Reduce risk of recursion errors by excluding imported objects from `has_docstrings`, unless they're public ([9296ca7](https://github.com/mkdocstrings/griffe/commit/9296ca7273eb1e6b7255b92793a09b82fd3bc4a9) by Timothée Mazzucotelli). [Issue-302](https://github.com/mkdocstrings/griffe/issues/302)
- Fix retrieval of annotations from parent for Yields section in properties ([8a21f4d](https://github.com/mkdocstrings/griffe/commit/8a21f4db1743902c56875980a4aa2366609642c1) by Timothée Mazzucotelli). [Issue-298](https://github.com/mkdocstrings/griffe/issues/298)
- Fix parsing Yields section (Google-style) when yielded values are tuples, and the description has more lines than tuple values ([9091776](https://github.com/mkdocstrings/griffe/commit/90917761ef7ea71ccda8147b3e1ebbc4675d9685) by Timothée Mazzucotelli).
- Fix condition on objects kinds when merging stubs ([727f99b](https://github.com/mkdocstrings/griffe/commit/727f99b084c703937393d52e930aba4ee5739c3b) by Timothée Mazzucotelli).

### Code Refactoring

- Sort keys when dumping JSON from the command line ([8cdffe9](https://github.com/mkdocstrings/griffe/commit/8cdffe9a68383369f6598820ec867740bee58207) by Timothée Mazzucotelli). [Issue-310](https://github.com/mkdocstrings/griffe/issues/310)
- Handle both lists and dicts for members when loading JSON data in preparation of v1 ([f89050c](https://github.com/mkdocstrings/griffe/commit/f89050c3dced88d5295971ab019e5c9a5706f6cc) by Timothée Mazzucotelli). [Issue-310](https://github.com/mkdocstrings/griffe/issues/310)
- Accept `**kwargs` in extension hooks to allow forward-compatibility ([2621d52](https://github.com/mkdocstrings/griffe/commit/2621d52e4d1e89e043e022efb8eba087df5d321e) by Timothée Mazzucotelli). [Issue-312](https://github.com/mkdocstrings/griffe/issues/312)
- Revert deprecation of `patch_loggers` in favor of `patch_logger` ([a20796a](https://github.com/mkdocstrings/griffe/commit/a20796ac821ac72b22082fde2a68ad9dac735076) by Timothée Mazzucotelli).
- Expose dummy `load_pypi` in non-Insiders version ([a69cffd](https://github.com/mkdocstrings/griffe/commit/a69cffd89215dbe629cec892ccda3c259d5572ef) by Timothée Mazzucotelli).
- Don't emit deprecation warnings through own usage of deprecated API ([9922d74](https://github.com/mkdocstrings/griffe/commit/9922d741dc1f9538e5e5f00dd115b297665ac6f8) by Timothée Mazzucotelli). [Issue-mkdocstrings#676](https://github.com/mkdocstrings/mkdocstrings/issues/676)
- Finish preparing docstring style auto-detection feature ([03bdec6](https://github.com/mkdocstrings/griffe/commit/03bdec61bbba86b1fa1b98cb890c034bbfcd44c3) by Timothée Mazzucotelli). [Issue-5](https://github.com/mkdocstrings/griffe/issues/5)
- Add DocstringStyle literal type to prepare docstring style auto detection feature ([b7aaf64](https://github.com/mkdocstrings/griffe/commit/b7aaf6487f04876b498237726b36d08f8e35b905) by Timothée Mazzucotelli). [Issue-5](https://github.com/mkdocstrings/griffe/issues/5)
- Inherit from `str, Enum` instead of `StrEnum` which needs a backport ([77f1544](https://github.com/mkdocstrings/griffe/commit/77f15443540acd2d279e08675b41bd69470f76d9) by Timothée Mazzucotelli). [Issue-307](https://github.com/mkdocstrings/griffe/issues/307)

## [0.48.0](https://github.com/mkdocstrings/griffe/releases/tag/0.48.0) - 2024-07-15

<small>[Compare with 0.47.0](https://github.com/mkdocstrings/griffe/compare/0.47.0...0.48.0)</small>

WARNING: **⚡ Imminent v1! ⚡🚀 See [v0.46](#0460-2024-06-16).**

### Deprecations

- All submodules are deprecated. All objects are now exposed in the top-level `griffe` module.
- All logger names are deprecated, and will be replaced with `"griffe"` in v1. In v1 our single `"griffe"` logger will provide a method to temporarily disable logging, [`logger.disable()`][griffe.Logger.disable], since that's the most common third-party use.
- The `get_logger` function is deprecated. Instead, we'll use a global `logger` internally, and users are welcome to use it too.
- The `patch_loggers` function is renamed `patch_logger`.
- Following the logging changes, the [`docstring_warning`][griffe.docstring_warning] function can now directly log a warning message instead of returning a callable that does. Passing it a logger name (to get a callable) is deprecated in favor of passing it a docstring, message and offset directly.

### Features

- Support `FORCE_COLOR` environment variable ([e1b7bd9](https://github.com/mkdocstrings/griffe/commit/e1b7bd9c3a5be585815dc972a86a51cb1b63bfe7) by Timothée Mazzucotelli).

### Bug Fixes

- Don't take a shortcut to the end of an alias chain when getting/setting/deleting alias members ([1930609](https://github.com/mkdocstrings/griffe/commit/193060908aa1cecb9931553abbb0f9fa182c66a1) by Timothée Mazzucotelli).
- Short-circuit `__all__` convention when checking if a module is public ([5abf4e3](https://github.com/mkdocstrings/griffe/commit/5abf4e3343410dbd41760415cff7c5f9e8c2b6b8) by Timothée Mazzucotelli).
- Reuse existing loggers, preventing overwriting issues ([3c2825f](https://github.com/mkdocstrings/griffe/commit/3c2825f9cf34eb8b0dbedd9fb542e14af3d24c33) by Timothée Mazzucotelli).
- Ignore .pth files that are not utf-8 encoded ([ea299dc](https://github.com/mkdocstrings/griffe/commit/ea299dcb38ad78c9b3de961e88da214ccadd31be) by Andrew Sansom). [Issue-300](https://github.com/mkdocstrings/griffe/issues/300), [PR-301](https://github.com/mkdocstrings/griffe/pull/301)
- Attributes without annotations cannot be dataclass parameters ([c9b2e09](https://github.com/mkdocstrings/griffe/commit/c9b2e09344538778426c446dad306c4881a873b2) by Hassan Kibirige). [PR-297](https://github.com/mkdocstrings/griffe/pull/297)
- When deciding to alias an object or not during inspection, consider module paths to be equivalent even with arbitrary private components ([8c9f6e6](https://github.com/mkdocstrings/griffe/commit/8c9f6e609a1bb93d0c8c41962bb5a9f410862769) by Timothée Mazzucotelli). [Issue-296](https://github.com/mkdocstrings/griffe/issues/296)
- Fix target path computation: use qualified names to maintain classes in the path ([6e17def](https://github.com/mkdocstrings/griffe/commit/6e17def0759409c7d5148c1a2f7747d029f17594) by Timothée Mazzucotelli). [Issue-296](https://github.com/mkdocstrings/griffe/issues/296)

### Code Refactoring

- Prepare loggers for simplification ([381f10f](https://github.com/mkdocstrings/griffe/commit/381f10f9cc3c2e8b7e9f54db23c13334dacc1203) by Timothée Mazzucotelli).
- Add all previous modules for backward compatibility ([a86e44e](https://github.com/mkdocstrings/griffe/commit/a86e44e14b8f7be5b6fa9fb2e6a1614da65a3918) by Timothée Mazzucotelli).
- Add main public modules ([fb860b3](https://github.com/mkdocstrings/griffe/commit/fb860b3200699ae85fed52289f3a6136ea522618) by Timothée Mazzucotelli).
- Simplify "is imported" check in `is_public` property ([c2bbc10](https://github.com/mkdocstrings/griffe/commit/c2bbc10082da8e3b11d2fe4576db9719b25054e0) by Timothée Mazzucotelli).
- Use string and integer enumerations ([06b383b](https://github.com/mkdocstrings/griffe/commit/06b383b5d61bc5083c53745e2c19d0da75e55481) by Timothée Mazzucotelli).
- Renamed agents nodes modules ([ddc5b0c](https://github.com/mkdocstrings/griffe/commit/ddc5b0cc5bba3e0901fe6c7e9f9fe5b70bd2883c) by Timothée Mazzucotelli).
- Clean up and document internal API, mark legacy code ([92594a9](https://github.com/mkdocstrings/griffe/commit/92594a99fed42eb2daa3bbeb797edbf3507f3068) by Timothée Mazzucotelli).
- Renamed `dataclasses` internal modules to `models` ([5555de6](https://github.com/mkdocstrings/griffe/commit/5555de62426063483196888f1bc73757e7492ce8) by Timothée Mazzucotelli).
- Move sources under `_griffe` internal package ([cbce6a5](https://github.com/mkdocstrings/griffe/commit/cbce6a5c4740a5964f9b0eb605adbd6f554e99bc) by Timothée Mazzucotelli).

## [0.47.0](https://github.com/mkdocstrings/griffe/releases/tag/0.47.0) - 2024-06-18

<small>[Compare with 0.46.1](https://github.com/mkdocstrings/griffe/compare/0.46.1...0.47.0)</small>

WARNING: **⚡ Imminent v1! ⚡🚀 See [v0.46](#0460-2024-06-16).**

### Deprecations

- The `has_private_name` and `has_special_name` properties on objects and aliases have been renamed `is_private` and `is_special`. The `is_private` property now only returns true if the name is *not* special.

### Features

- Add `deprecated` attribute and `is_deprecated` property to objects/aliases ([2a75d84](https://github.com/mkdocstrings/griffe/commit/2a75d84265b40983ce4a1eb148677efb803f78c6) by Timothée Mazzucotelli).
- Add `is_imported` property to objects/aliases ([de926cc](https://github.com/mkdocstrings/griffe/commit/de926cc4782d53b9b28a2f887890d7711dfbc667) by Timothée Mazzucotelli).
- Add `is_class_private` property to objects/aliases ([491b6c4](https://github.com/mkdocstrings/griffe/commit/491b6c4da086a68e8e1eee13f2d4b7840390b6b9) by Timothée Mazzucotelli).

### Code Refactoring

- Rename `has_private_name` and `has_special_name` to `is_private` and `is_special` ([ae7c7e7](https://github.com/mkdocstrings/griffe/commit/ae7c7e73e7bf7f02b86fc58503888113d98e8e39) by Timothée Mazzucotelli).

## [0.46.1](https://github.com/mkdocstrings/griffe/releases/tag/0.46.1) - 2024-06-17

<small>[Compare with 0.46.0](https://github.com/mkdocstrings/griffe/compare/0.46.0...0.46.1)</small>

WARNING: **⚡ Imminent v1! ⚡🚀 See [v0.46](#0460-2024-06-16).**

### Bug Fixes

- Always consider special objects ("dunder" attributes/methods/etc.) to be public ([3319410](https://github.com/mkdocstrings/griffe/commit/331941029decd9d400b30ea1471b6bcc384fd54f) by Timothée Mazzucotelli). [Issue-294](https://github.com/mkdocstrings/griffe/issues/294), [Issue-295](https://github.com/mkdocstrings/griffe/issues/295)
- Don't consider imported objects as public ([ea90952](https://github.com/mkdocstrings/griffe/commit/ea909526f3a637849364544daff74cd49ccaf428) by Timothée Mazzucotelli). [Discussion-169](https://github.com/mkdocstrings/python/discussions/169)

## [0.46.0](https://github.com/mkdocstrings/griffe/releases/tag/0.46.0) - 2024-06-16

<small>[Compare with 0.45.3](https://github.com/mkdocstrings/griffe/compare/0.45.3...0.46.0)</small>

WARNING: **⚡ Imminent v1! ⚡🚀**
We are working on v1, and it will come soon, so we recommend that you consider adding an upper bound on Griffe. Version 1 will remove all legacy code! There will be a couple more v0 before so that you get all the deprecation warnings needed to upgrade your code using Griffe before upgrading to v1. See breaking changes and deprecations for v0.46 below.

### Breaking Changes

We are still in v0, so no major bump yet.

- Calling objects' [`has_labels()`][griffe.Object.has_labels] method with a `labels` keyword argument is not supported anymore. The parameter became a variadic positional parameter, so it cannot be used as a keyword argument anymore. Passing a sequence instead of multiple positional arguments still works but will emit a deprecation warning.
- Calling the [`load_extensions()`][griffe.load_extensions] function with an `exts` keyword argument is not supported anymore. The parameter became a variadic positional parameter, so it cannot be used as a keyword argument anymore. Passing a sequence instead of multiple positional arguments still works but will emit a deprecation warning.

### Deprecations

- As seen above in the breaking changes section, the only parameters of [`Object.has_labels()`][griffe.Object.has_labels] and [`load_extensions()`][griffe.load_extensions] both became variadic positional parameters. Passing a sequence as single argument is deprecated in favor of passing multiple arguments. This is an ergonomic change: I myself often forgot to wrap extensions in a list. Passing sequences of labels (lists, sets, tuples) is also difficult from Jinja templates.
- The following methods and properties on objects and aliases are deprecated: `member_is_exported()`, `is_explicitely_exported`, `is_implicitely_exported`. Use the [`is_exported`][griffe.ObjectAliasMixin.is_exported] property instead. See [issue 281](https://github.com/mkdocstrings/griffe/issues/281).
- The [`is_exported()`][griffe.ObjectAliasMixin.is_exported] and [`is_public()`][griffe.ObjectAliasMixin.is_public] methods became properties. They can still be called like methods, but will emit deprecation warnings when doing so. See [issue 281](https://github.com/mkdocstrings/griffe/issues/281).
- The `ignore_private` parameter of the [`find_breaking_changes()`][griffe.find_breaking_changes] function is now deprecated and unused. With the reworked "exported" and "public" API, this parameter became useless. See [issue 281](https://github.com/mkdocstrings/griffe/issues/281).
- Using `stats()` instead of [`Stats`][griffe.Stats] will now emit a deprecation warning.

### Features

- Add `docstring` attribute to parameters ([e21eabe](https://github.com/mkdocstrings/griffe/commit/e21eabe8c48e3650d04fec805804683cb743ce12) by Hassan Kibirige). [Issue-286](https://github.com/mkdocstrings/griffe/issues/286), [Related-to-mkdocstrings/griffe#252](https://github.com/mkdocstrings/griffe/pull/252), [PR-288](https://github.com/mkdocstrings/griffe/pull/288), Co-authored-by: Timothée Mazzucotelli <dev@pawamoy.fr>
- Provide line numbers for classes and functions when inspecting ([b6ddcc4](https://github.com/mkdocstrings/griffe/commit/b6ddcc4e6da42318961bb7cb7be59041a43c6451) by Timothée Mazzucotelli). [Issue-272](https://github.com/mkdocstrings/griffe/issues/272)
- Populate lines collection within helpers ([ab2e947](https://github.com/mkdocstrings/griffe/commit/ab2e9479c2b94dc7b6736e40024db87fb87b4e62) by Timothée Mazzucotelli). [GitHub-issue-270](https://github.com/mkdocstrings/griffe/issues/270), [Radicle-issue-0d6a513](https://app.radicle.xyz/nodes/seed.radicle.garden/rad:z23ZVuA1DWS99PDJ1rcarCtJi99x1/issues/0d6a51328f554f235c38a2a652b844c4ba21bba5)

### Bug Fixes

- Handle partials as functions while inspecting ([be29c32](https://github.com/mkdocstrings/griffe/commit/be29c3214680dc20c9c776d12a2a15ca690fa8d0) by Timothée Mazzucotelli).
- Populate lines collection before visiting/inspecting modules within helpers ([08c3f40](https://github.com/mkdocstrings/griffe/commit/08c3f409f3fc130f07b2d717cddff38d47d4dbca) by Timothée Mazzucotelli). [Issue-272](https://github.com/mkdocstrings/griffe/issues/272)
- Don't return all lines when line numbers are missing ([9e6dcaa](https://github.com/mkdocstrings/griffe/commit/9e6dcaa8f30132ebef59eb27b1f2f3ff7bc03bae) by Timothée Mazzucotelli). [Issue-271](https://github.com/mkdocstrings/griffe/issues/271)

### Code Refactoring

- Emit deprecation warning when accessing `stats` instead of `Stats` ([e5572d2](https://github.com/mkdocstrings/griffe/commit/e5572d2eb1dd8dbe8f9b43b33119bd9becc4a4d9) by Timothée Mazzucotelli).
- Rework "exported" and "public" logic ([b327b90](https://github.com/mkdocstrings/griffe/commit/b327b908d9546c8eb8f4ce5d3a216309937a6552) by Timothée Mazzucotelli). [Issue-281](https://github.com/mkdocstrings/griffe/issues/281)
- Allow passing multiple extensions to `load_extensions` instead of a sequence ([fadb72b](https://github.com/mkdocstrings/griffe/commit/fadb72b4b693f418ebc11aefba3be188a2522c7e) by Timothée Mazzucotelli). [Issue-268](https://github.com/mkdocstrings/griffe/issues/268)
- Allow passing multiple labels to `Object.has_labels` instead of set ([c4e3bf2](https://github.com/mkdocstrings/griffe/commit/c4e3bf2c1a6ff7a1a66f203ae7abec859cbdea44) by Timothée Mazzucotelli). [Issue-267](https://github.com/mkdocstrings/griffe/issues/267)

## [0.45.3](https://github.com/mkdocstrings/griffe/releases/tag/0.45.3) - 2024-06-09

<small>[Compare with 0.45.2](https://github.com/mkdocstrings/griffe/compare/0.45.2...0.45.3)</small>

### Bug Fixes

- Always call `on_package_loaded` hook on a package, and not any other object ([40db38d](https://github.com/mkdocstrings/griffe/commit/40db38d6d55c5a7926d39408e7fd51ec198b62b9) by Timothée Mazzucotelli). [Issue-283](https://github.com/mkdocstrings/griffe/issues/283)

## [0.45.2](https://github.com/mkdocstrings/griffe/releases/tag/0.45.2) - 2024-05-23

<small>[Compare with 0.45.1](https://github.com/mkdocstrings/griffe/compare/0.45.1...0.45.2)</small>

### Bug Fixes

- Support setuptools' new editable modules using type annotations ([14d45e8](https://github.com/mkdocstrings/griffe/commit/14d45e83d4a48c67b2347965351145cc78d7abe9) by Timothée Mazzucotelli). [Issue-273](https://github.com/mkdocstrings/griffe/issues/273)

## [0.45.1](https://github.com/mkdocstrings/griffe/releases/tag/0.45.1) - 2024-05-18

<small>[Compare with 0.45.0](https://github.com/mkdocstrings/griffe/compare/0.45.0...0.45.1)</small>

### Bug Fixes

- Fix loading of importable modules thanks to their `__path__` attribute ([56f5363](https://github.com/mkdocstrings/griffe/commit/56f5363063b54bc43a7e61da7ac6b177db2f158f) by Timothée Mazzucotelli). [Issue-269](https://github.com/mkdocstrings/griffe/issues/269)

## [0.45.0](https://github.com/mkdocstrings/griffe/releases/tag/0.45.0) - 2024-05-12

<small>[Compare with 0.44.0](https://github.com/mkdocstrings/griffe/compare/0.44.0...0.45.0)</small>

### Features

- Implement `-x`, `--force-inspection` CLI option ([776063d](https://github.com/mkdocstrings/griffe/commit/776063d971b059576c62f62fdd2e1199de033711) by Timothée Mazzucotelli).
- Implement `force_inspection` option in the loader API ([3266f22](https://github.com/mkdocstrings/griffe/commit/3266f2290637d3f46d782fe7ce222ff29f549043) by Timothée Mazzucotelli).
- Support inspecting packages (`__init__` modules) ([3f74f67](https://github.com/mkdocstrings/griffe/commit/3f74f679de15df098482fead505d0402bff84401) by Timothée Mazzucotelli).
- Add parameters for resolving aliases to `load` functions ([e418dee](https://github.com/mkdocstrings/griffe/commit/e418dee1563e2a02ec61c920842e8b8a13419448) by Timothée Mazzucotelli).
- Load private sibling modules by default when resolving aliases ([4806189](https://github.com/mkdocstrings/griffe/commit/4806189111572495466638bb7899cf906eeebfe9) by Timothée Mazzucotelli).

### Bug Fixes

- Pass down modules collection when inspecting ([bc0f74b](https://github.com/mkdocstrings/griffe/commit/bc0f74bef40a812e00765a7ab17507b0bfbd62c3) by Timothée Mazzucotelli).
- Catch loading errors when loading additional modules during wildcard expansion and alias resolution ([964e0d2](https://github.com/mkdocstrings/griffe/commit/964e0d2b78d3bc3530601009148fb4a5905b8721) by Timothée Mazzucotelli).

### Code Refactoring

- Improve stats code and performance ([eeb497f](https://github.com/mkdocstrings/griffe/commit/eeb497fa41acf50801cc6a7a240d079cc1592e79) by Timothée Mazzucotelli).
- Recurse immediately into non-discoverable submodules (no path on disk) during dynamic analysis ([d0b7a1d](https://github.com/mkdocstrings/griffe/commit/d0b7a1d96a4dd7513f34673b0ef6cd02aa7d0fca) by Timothée Mazzucotelli).
- Simplify the code that checks if an object should be aliased or not during dynamic analysis ([fc794c2](https://github.com/mkdocstrings/griffe/commit/fc794c24c578fe868900483b20601937db3f3d05) by Timothée Mazzucotelli).
- Avoid side-effect in inspector by checking early if an object is a cached property ([a6bfcfd](https://github.com/mkdocstrings/griffe/commit/a6bfcfdb9e2a0740d72abbd1480e0aa7e23c9af1) by Timothée Mazzucotelli).

## [0.44.0](https://github.com/mkdocstrings/griffe/releases/tag/0.44.0) - 2024-04-19

<small>[Compare with 0.43.0](https://github.com/mkdocstrings/griffe/compare/0.43.0...0.44.0)</small>

### Features

- Add `resolved` property on expression names, returning the corresponding Griffe object ([9b5ca45](https://github.com/mkdocstrings/griffe/commit/9b5ca4574250f847fd33a8cb92af56806db50c1b) by Timothée Mazzucotelli).

### Bug Fixes

- Fix enumeration properties on expression names ([6f22256](https://github.com/mkdocstrings/griffe/commit/6f22256ad02439d961bce2bb1afa32d4e9e10b10) by Timothée Mazzucotelli).

## [0.43.0](https://github.com/mkdocstrings/griffe/releases/tag/0.43.0) - 2024-04-18

<small>[Compare with 0.42.2](https://github.com/mkdocstrings/griffe/compare/0.42.2...0.43.0)</small>

### Features

- Add properties telling whether an expression name resolves to an enumeration class, instance or value ([fdb21d9](https://github.com/mkdocstrings/griffe/commit/fdb21d943f72fb10a4406930bf3e3bf7aceff6b0) by Timothée Mazzucotelli). [Issue-mkdocstrings/python#124](https://github.com/mkdocstrings/python/issues/124)

## [0.42.2](https://github.com/mkdocstrings/griffe/releases/tag/0.42.2) - 2024-04-15

<small>[Compare with 0.42.1](https://github.com/mkdocstrings/griffe/compare/0.42.1...0.42.2)</small>

### Bug Fixes

- Fix target path of aliases for multipart imports (`import a.b.c as x`) ([ee27ad9](https://github.com/mkdocstrings/griffe/commit/ee27ad97669a7321d18e6724e6c155cef601a289) by Timothée Mazzucotelli). [Issue-259](https://github.com/mkdocstrings/griffe/issues/259)

## [0.42.1](https://github.com/mkdocstrings/griffe/releases/tag/0.42.1) - 2024-03-19

<small>[Compare with 0.42.0](https://github.com/mkdocstrings/griffe/compare/0.42.0...0.42.1)</small>

### Bug Fixes

- Don't return class variables as parameters of dataclasses ([2729c22](https://github.com/mkdocstrings/griffe/commit/2729c22505d87b771ab7a70c91c9f8301275aa8c) by Hassan Kibirige). [PR-253](https://github.com/mkdocstrings/griffe/pull/253)
- Don't turn items annotated as InitVar into dataclass members ([6835ea3](https://github.com/mkdocstrings/griffe/commit/6835ea361325a205c0af69acabc66ca5193156c5) by Hassan Kibirige). [PR-252](https://github.com/mkdocstrings/griffe/pull/252)

## [0.42.0](https://github.com/mkdocstrings/griffe/releases/tag/0.42.0) - 2024-03-11

<small>[Compare with 0.41.3](https://github.com/mkdocstrings/griffe/compare/0.41.3...0.42.0)</small>

### Features

- Better support for dataclasses ([82a9d57](https://github.com/mkdocstrings/griffe/commit/82a9d5798b2eebddfd640b918415a0e3de2ca739) by Timothée Mazzucotelli). [Issue-33](https://github.com/mkdocstrings/griffe/issues/233), [Issue-34](https://github.com/mkdocstrings/griffe/issues/234), [Issue-38](https://github.com/mkdocstrings/griffe/issues/238), [Issue-39](https://github.com/mkdocstrings/griffe/issues/239), [PR-240](https://github.com/mkdocstrings/griffe/pull/240)

### Bug Fixes

- Don't return properties as parameters of dataclasses (again) ([8c48397](https://github.com/mkdocstrings/griffe/commit/8c48397e7301bbb296e2f2630405f2d22f7222e3) by Hassan Kibirige). [Issue-232](https://github.com/mkdocstrings/griffe/issues/232), [PR-248](https://github.com/mkdocstrings/griffe/pull/248)
- Fix getting return type from parent property when parsing Sphinx docstrings ([f314957](https://github.com/mkdocstrings/griffe/commit/f314957c9da7805a9eb1a23d1a7f3d47b0b1e4c0) by Timothée Mazzucotelli). [Issue-125](https://github.com/mkdocstrings/griffe/issues/125)

### Code Refactoring

- Warn (debug) when a submodule shadows a member with the same name ([cdc9e1c](https://github.com/mkdocstrings/griffe/commit/cdc9e1c5ee92a4c621314a9d9c6c465bfdd2ad92) by Timothée Mazzucotelli). [Issue-124](https://github.com/mkdocstrings/griffe/issues/124)

## [0.41.3](https://github.com/mkdocstrings/griffe/releases/tag/0.41.3) - 2024-03-04

<small>[Compare with 0.41.2](https://github.com/mkdocstrings/griffe/compare/0.41.2...0.41.3)</small>

### Code Refactoring

- Catch index errors when finding top module in case of search path misconfiguration ([46c56c7](https://github.com/mkdocstrings/griffe/commit/46c56c7ff505531f5422f526ad38095ed463cc1b) by Timothée Mazzucotelli). [Issue-#246](https://github.com/mkdocstrings/griffe/issues/246)

## [0.41.2](https://github.com/mkdocstrings/griffe/releases/tag/0.41.2) - 2024-03-03

<small>[Compare with 0.41.1](https://github.com/mkdocstrings/griffe/compare/0.41.1...0.41.2)</small>

### Bug Fixes

- Fix discovery of packages in the current working directory ([44f9617](https://github.com/mkdocstrings/griffe/commit/44f96173df188568bb1db54a20270ff0a08298c6) by Timothée Mazzucotelli). [Discussion-mkdocstrings#654](https://github.com/mkdocstrings/mkdocstrings/discussions/654)

## [0.41.1](https://github.com/mkdocstrings/griffe/releases/tag/0.41.1) - 2024-03-01

<small>[Compare with 0.41.0](https://github.com/mkdocstrings/griffe/compare/0.41.0...0.41.1)</small>

### Deprecations

- The `load_git` function moved from `griffe.git` to `griffe.loader`.
  It is still importable from `griffe.git`, but will emit a deprecation warning.

### Code Refactoring

- Expose Git utilities, move `load_git` into the `loader` module ([327cc5b](https://github.com/mkdocstrings/griffe/commit/327cc5b0f28f7236eaaf1c028674b6e0006611da) by Timothée Mazzucotelli).

## [0.41.0](https://github.com/mkdocstrings/griffe/releases/tag/0.41.0) - 2024-02-26

<small>[Compare with 0.40.1](https://github.com/mkdocstrings/griffe/compare/0.40.1...0.41.0)</small>

### Features

- Add option to append `sys.path` to search paths to the check command too ([d153fa0](https://github.com/mkdocstrings/griffe/commit/d153fa0aeaa248ae13101f189f887f9bfee27f04) by Timothée Mazzucotelli).

### Bug Fixes

- Special case NumpyDoc "warnings" and "notes" sections (plural) ([3b47cdb](https://github.com/mkdocstrings/griffe/commit/3b47cdb889e08106404bfcdbd3ce651f7eee6cdf) by Ethan Henderson). [PR #236](https://github.com/mkdocstrings/griffe/pull/236)
- Serialize line numbers even if zero ([55e6e0e](https://github.com/mkdocstrings/griffe/commit/55e6e0e6c01351aa832aaf934d001442f66c8598) by Timothée Mazzucotelli).
- Fix handling of lambda expressions ([598d08a](https://github.com/mkdocstrings/griffe/commit/598d08ae0dcd7d266194237211e6431ee65aee67) by Timothée Mazzucotelli).
- Fix building expressions (and string values) for `yield` and `yield from` statements ([439f65e](https://github.com/mkdocstrings/griffe/commit/439f65e3703c5cad7d68aa3b2da371599236f58b) by Timothée Mazzucotelli).
- Do not create aliases pointing to themselves ([356305f](https://github.com/mkdocstrings/griffe/commit/356305f69664c1d955f4dbf7c865cb4f553488fc) by Timothée Mazzucotelli).

### Code Refactoring

- Remove `get_call_keyword_arguments` utility function, as it is implemented with a single line and creates a cyclic dependency with expressions ([35cf170](https://github.com/mkdocstrings/griffe/commit/35cf170cc91ba740e6f997d76f99d6a07e8d4437) by Timothée Mazzucotelli).
- Further prevent cyclic dependency between node utils and expressions ([9614c83](https://github.com/mkdocstrings/griffe/commit/9614c83c037637d7823a4c06f115c3e2e4b6e10f) by Timothée Mazzucotelli).
- Avoid cyclic dependency between node utils and expressions ([aedf39c](https://github.com/mkdocstrings/griffe/commit/aedf39c3795197deb6067e039da8bdec182bd363) by Timothée Mazzucotelli).
- Move arguments node-parsing logic into its own module (used by visitor and lambda expressions) ([ad68e65](https://github.com/mkdocstrings/griffe/commit/ad68e65363c4338d7f38ccade2f9cc05d41f8100) by Timothée Mazzucotelli).
- Use canonical imports ([3091660](https://github.com/mkdocstrings/griffe/commit/3091660ae1b6253e481cedbdcc31b73c0ab334df) by Timothée Mazzucotelli).
- Use `ast.unparse` instead of our own unparser ([6fe1316](https://github.com/mkdocstrings/griffe/commit/6fe1316807870cbf93bba79f3d400cae6630ea73) by Timothée Mazzucotelli).
- Only return 0 for the line number of removed objects when the location is reworked as relative ([3a4d054](https://github.com/mkdocstrings/griffe/commit/3a4d054e993e8a53cce9e53057e81479ab5f6034) by Timothée Mazzucotelli).

## [0.40.1](https://github.com/mkdocstrings/griffe/releases/tag/0.40.1) - 2024-02-08

<small>[Compare with 0.40.0](https://github.com/mkdocstrings/griffe/compare/0.40.0...0.40.1)</small>

### Bug Fixes

- Don't return properties as parameters of dataclasses ([5a5c03b](https://github.com/mkdocstrings/griffe/commit/5a5c03b38366049f19fc2b65f09153e7df5748ce) by Timothée Mazzucotelli). [Issue #232](https://github.com/mkdocstrings/griffe/issues/232)

## [0.40.0](https://github.com/mkdocstrings/griffe/releases/tag/0.40.0) - 2024-01-30

<small>[Compare with 0.39.1](https://github.com/mkdocstrings/griffe/compare/0.39.1...0.40.0)</small>

### Features

- Store reference to function call in keyword expressions ([d72f9d3](https://github.com/mkdocstrings/griffe/commit/d72f9d3a425fee11f23f9f7b44814b6fda458e6e) by Timothée Mazzucotelli). [PR #231](https://github.com/mkdocstrings/griffe/pull/231)

## [0.39.1](https://github.com/mkdocstrings/griffe/releases/tag/0.39.1) - 2024-01-18

<small>[Compare with 0.39.0](https://github.com/mkdocstrings/griffe/compare/0.39.0...0.39.1)</small>

### Bug Fixes

- De-duplicate search paths in finder as they could lead to the same modules being yielded twice or more when scanning namespace packages ([80a158a](https://github.com/mkdocstrings/griffe/commit/80a158a2de8d53a054405c3e14113b09d73335a3) by Timothée Mazzucotelli).
- Fix logic for skipping already encountered modules when scanning namespace packages ([21a48d0](https://github.com/mkdocstrings/griffe/commit/21a48d0b9248467fe3c36440bee649ce8879f295) by Timothée Mazzucotelli). [Issue mkdocstrings#646](https://github.com/mkdocstrings/mkdocstrings/issues/646)

## [0.39.0](https://github.com/mkdocstrings/griffe/releases/tag/0.39.0) - 2024-01-16

<small>[Compare with 0.38.1](https://github.com/mkdocstrings/griffe/compare/0.38.1...0.39.0)</small>

### Features

- Support editable installs dynamically exposing modules from other directories ([2c4ba75](https://github.com/mkdocstrings/griffe/commit/2c4ba751d7d47eb48b47179d316722315e5d4647) by Timothée Mazzucotelli). [Issue #229](https://github.com/mkdocstrings/griffe/issues/229)
- Support meson-python editable modules ([9123897](https://github.com/mkdocstrings/griffe/commit/9123897ad8d85e48bd3c435ffabcf9a36a0ed355) by Timothée Mazzucotelli).
- Support admonitions in Numpydoc docstrings ([1e311a4](https://github.com/mkdocstrings/griffe/commit/1e311a4eb935c58d488c928a86493ab3f3368f06) by Michael Chow). [Issue #214](https://github.com/mkdocstrings/griffe/issues/214), [PR #219](https://github.com/mkdocstrings/griffe/pull/219), Co-authored-by: Timothée Mazzucotelli <pawamoy@pm.me>
- Expose module properties on all objects ([123f8c5](https://github.com/mkdocstrings/griffe/commit/123f8c5ba1826435e90dafffbfe304bd6ab8e187) by Timothée Mazzucotelli). [Issue #226](https://github.com/mkdocstrings/griffe/issues/226)

### Bug Fixes

- Consider space-only lines to be empty, never break Numpydoc sections on blank lines ([8c57354](https://github.com/mkdocstrings/griffe/commit/8c5735497578417e1dd723625590539016e7b7a5) by Timothée Mazzucotelli). [PR #220](https://github.com/mkdocstrings/griffe/pull/220), [Related to PR #219](https://github.com/mkdocstrings/griffe/pull/219), [Numpydoc discussion](https://github.com/numpy/numpydoc/issues/463)
- Allow merging stubs into alias targets ([3cf7958](https://github.com/mkdocstrings/griffe/commit/3cf795871a0549b901d9374705d6a1eb84700128) by Timothée Mazzucotelli).
- Insert the right directory in front of import paths before inspecting a module (dynamically imported) ([7d75c71](https://github.com/mkdocstrings/griffe/commit/7d75c71477ccb208e071bfe3c3204a0490274b44) by Timothée Mazzucotelli).

### Code Refactoring

- Set lineno to 0 for removed objects when checking API ([b660c34](https://github.com/mkdocstrings/griffe/commit/b660c346feb3a95fbe54a6dad460e988a9a41774) by Timothée Mazzucotelli).
- Prepare support for new output formats (styles) of the check command ([f2ece1e](https://github.com/mkdocstrings/griffe/commit/f2ece1e602b0fb3d888a60d892089a55fdcf60f0) by Timothée Mazzucotelli).
- Transform finder's package and namespace package classes into dataclasses ([16be6a4](https://github.com/mkdocstrings/griffe/commit/16be6a4a7660d8ed13ccdcf9c571eda647e078f0) by Timothée Mazzucotelli).

## [0.38.1](https://github.com/mkdocstrings/griffe/releases/tag/0.38.1) - 2023-12-06

<small>[Compare with 0.38.0](https://github.com/mkdocstrings/griffe/compare/0.38.0...0.38.1)</small>

### Bug Fixes

- Support absolute Windows paths for extensions ([4e67d8f](https://github.com/mkdocstrings/griffe/commit/4e67d8fa5f0e9f23c1df2e1d772fc0f1e4e6c2e0) by Timothée Mazzucotelli). [Issue mkdocstrings-python#116](https://github.com/mkdocstrings/python/issues/116)

## [0.38.0](https://github.com/mkdocstrings/griffe/releases/tag/0.38.0) - 2023-11-13

<small>[Compare with 0.37.0](https://github.com/mkdocstrings/griffe/compare/0.37.0...0.38.0)</small>

### Features

- Allow passing load parameters to the temporary package visit helper ([3a7854f](https://github.com/mkdocstrings/griffe/commit/3a7854fb180e34392fd520d9d25a6298d4b80830) by Timothée Mazzucotelli).

## [0.37.0](https://github.com/mkdocstrings/griffe/releases/tag/0.37.0) - 2023-11-12

<small>[Compare with 0.36.9](https://github.com/mkdocstrings/griffe/compare/0.36.9...0.37.0)</small>

### Deprecations

- The loader `load_module` method was renamed `load`,
    Its `module` parameter was renamed `objspec` and is now positional-only.
    This method always returned the specified object, not just modules,
    so it made more sense to rename it `load` and to rename the parameter
    specifying the object. Old usages (`load_module` and `module=...`)
    will continue to work for some time (a few months, a year, more),
    and will emit deprecation warnings.

### Features

- Add option to warn about unknown parameters in Sphinx docstrings ([8b11d77](https://github.com/mkdocstrings/griffe/commit/8b11d77315ca7a5e15da519db1663d05805dd075) by Ashwin Vinod). [Issue #64](https://github.com/mkdocstrings/griffe/issues/64), [PR #210](https://github.com/mkdocstrings/griffe/pull/210), Co-authored-by: Timothée Mazzucotelli <pawamoy@pm.me>
- Add `on_package_loaded` event ([a5cf654](https://github.com/mkdocstrings/griffe/commit/a5cf6543b43db06c4d0f24d2631ddc86b1fee41e) by Timothée Mazzucotelli).
- Add option to find, load and merge stubs-only packages ([6e55f3b](https://github.com/mkdocstrings/griffe/commit/6e55f3bd0838e3f229fcd37d3aeced0146d33ff1) by Romain). [PR #221](https://github.com/mkdocstrings/griffe/pull/221), Co-authored-by: Timothée Mazzucotelli <pawamoy@pm.me>

### Bug Fixes

- Report attributes who lost their value as "unset" ([dfffa4b](https://github.com/mkdocstrings/griffe/commit/dfffa4b96a8a70f93b899bd41aefeaa9939819e9) by Geethakrishna-Puligundla). [Issue #218](https://github.com/mkdocstrings/griffe/issues/218), [PR #225](https://github.com/mkdocstrings/griffe/pull/225)
- Don't crash when computing MRO for a class that is named after its parent ([a2dd8a6](https://github.com/mkdocstrings/griffe/commit/a2dd8a6bc3f95679e1c2e79ce05d175fb8f89ccc) by Timothée Mazzucotelli).

### Code Refactoring

- Rename loader `load_module` method to `load` ([2bfe206](https://github.com/mkdocstrings/griffe/commit/2bfe206b57f607b56f7bcb5a85a7e2a25fe3bf47) by Timothée Mazzucotelli).

## [0.36.9](https://github.com/mkdocstrings/griffe/releases/tag/0.36.9) - 2023-10-27

<small>[Compare with 0.36.8](https://github.com/mkdocstrings/griffe/compare/0.36.8...0.36.9)</small>

### Bug Fixes

- Fix accessing alias members with `__getitem__` ([8929409](https://github.com/mkdocstrings/griffe/commit/8929409d4703c6b684084e88aae0d99423e05dbf) by Timothée Mazzucotelli). [Issue mkdocstrings-python#111](https://github.com/mkdocstrings/python/issues/111)

### Code Refactoring

- Expose parser enumeration and parser functions in top-level module ([785baa0](https://github.com/mkdocstrings/griffe/commit/785baa04e3081fcf80756f56dddb95a00cb9b025) by Timothée Mazzucotelli).

## [0.36.8](https://github.com/mkdocstrings/griffe/releases/tag/0.36.8) - 2023-10-25

<small>[Compare with 0.36.7](https://github.com/mkdocstrings/griffe/compare/0.36.7...0.36.8)</small>

### Bug Fixes

- Use already parsed docstring sections when dumping full data ([311807b](https://github.com/mkdocstrings/griffe/commit/311807b8fa1716dabe5ba18d3e12c947286afd8e) by Timothée Mazzucotelli). [Discussion griffe-typingdoc#6](https://github.com/mkdocstrings/griffe-typingdoc/discussions/6)

## [0.36.7](https://github.com/mkdocstrings/griffe/releases/tag/0.36.7) - 2023-10-17

<small>[Compare with 0.36.6](https://github.com/mkdocstrings/griffe/compare/0.36.6...0.36.7)</small>

### Bug Fixes

- Add missing proxies (methods/properties) to aliases ([7320640](https://github.com/mkdocstrings/griffe/commit/7320640d42ebb4546f787fe458d5032a67ea20b7) by Timothée Mazzucotelli).

### Code Refactoring

- Use final target in alias proxies ([731d662](https://github.com/mkdocstrings/griffe/commit/731d66237252e754b7a935ca4d0344f554edb5ff) by Timothée Mazzucotelli).

## [0.36.6](https://github.com/mkdocstrings/griffe/releases/tag/0.36.6) - 2023-10-16

<small>[Compare with 0.36.5](https://github.com/mkdocstrings/griffe/compare/0.36.5...0.36.6)</small>

### Code Refactoring

- Only consider presence/absence for docstrings truthiness, not emptiness of their value ([4c49611](https://github.com/mkdocstrings/griffe/commit/4c496117880d2166bfc2bc8c40a235c23cef8527) by Timothée Mazzucotelli).

## [0.36.5](https://github.com/mkdocstrings/griffe/releases/tag/0.36.5) - 2023-10-09

<small>[Compare with 0.36.4](https://github.com/mkdocstrings/griffe/compare/0.36.4...0.36.5)</small>

### Bug Fixes

- Force extension import path to be a string (coming from MkDocs' `!relative` tag) ([34e21a9](https://github.com/mkdocstrings/griffe/commit/34e21a9545a38b61a1b80192af312d70f6c607f2) by Timothée Mazzucotelli).
- Fix crash when trying to get a decorator callable path (found thanks to pysource-codegen) ([e57f08e](https://github.com/mkdocstrings/griffe/commit/e57f08eb5770eb3a9ed12e97da3076b87f109224) by Timothée Mazzucotelli).
- Fix crash when trying to get docstring after assignment (found thanks to pysource-codegen) ([fb0a0c1](https://github.com/mkdocstrings/griffe/commit/fb0a0c1a8558c9d04855b75e4a9f579b46e2edd8) by Timothée Mazzucotelli).
- Fix type errors in expressions and value extractor, don't pass duplicate arguments (found thanks to pysource-codegen) ([7e53288](https://github.com/mkdocstrings/griffe/commit/7e53288586bd90198cfd6a898002850c67213209) by Timothée Mazzucotelli).

## [0.36.4](https://github.com/mkdocstrings/griffe/releases/tag/0.36.4) - 2023-09-28

<small>[Compare with 0.36.3](https://github.com/mkdocstrings/griffe/compare/0.36.3...0.36.4)</small>

### Bug Fixes

- Fix visiting relative imports in non-init modules ([c1138c3](https://github.com/mkdocstrings/griffe/commit/c1138c34b89965fd780d669c7dd6b12f245d8cd9) by Timothée Mazzucotelli).

## [0.36.3](https://github.com/mkdocstrings/griffe/releases/tag/0.36.3) - 2023-09-28

<small>[Compare with 0.36.2](https://github.com/mkdocstrings/griffe/compare/0.36.2...0.36.3)</small>

### Bug Fixes

- Fix parsing of choices in Numpy parameters ([5f2d997](https://github.com/mkdocstrings/griffe/commit/5f2d99776e326679d2c0d1d9cb6b06d6436971c6) by Timothée Mazzucotelli). [Issue #212](https://github.com/mkdocstrings/griffe/issues/212)

### Code Refactoring

- Add `repr` methods to function parameters ([9442234](https://github.com/mkdocstrings/griffe/commit/94422349483a25db627921dfe13c7a89b81e700e) by Timothée Mazzucotelli).

## [0.36.2](https://github.com/mkdocstrings/griffe/releases/tag/0.36.2) - 2023-09-10

<small>[Compare with 0.36.1](https://github.com/mkdocstrings/griffe/compare/0.36.1...0.36.2)</small>

### Bug Fixes

- Fix warnings for docstrings in builtin modules ([6ba3e04](https://github.com/mkdocstrings/griffe/commit/6ba3e0461647c2c76d0fd68889d37bbada686259) by Timothée Mazzucotelli).
- Fix dumping `filepath` to a dict when it is a list ([066a4a7](https://github.com/mkdocstrings/griffe/commit/066a4a7f22827783c930feacd6a339ed3d00ec27) by davfsa). [PR #207](https://github.com/mkdocstrings/griffe/pull/207)

## [0.36.1](https://github.com/mkdocstrings/griffe/releases/tag/0.36.1) - 2023-09-04

<small>[Compare with 0.36.0](https://github.com/mkdocstrings/griffe/compare/0.36.0...0.36.1)</small>

### Bug Fixes

- Fix iterating non-flat expressions (some nodes were skipped) ([3249155](https://github.com/mkdocstrings/griffe/commit/324915507c1100e04ffed6d926143f66f0016870) by Timothée Mazzucotelli).

## [0.36.0](https://github.com/mkdocstrings/griffe/releases/tag/0.36.0) - 2023-09-01

<small>[Compare with 0.35.2](https://github.com/mkdocstrings/griffe/compare/0.35.2...0.36.0)</small>

### Features

- Add option to read return type of properties in their summary (Google-style) ([096970f](https://github.com/mkdocstrings/griffe/commit/096970ffa66f491ef34ae1121e8b907f2da4c742) by Timothée Mazzucotelli). [Issue #137](https://github.com/mkdocstrings/griffe/issues/137), [PR #206](https://github.com/mkdocstrings/griffe/pull/206)
- Add option to make parentheses around the type of returned values optional (Google-style) ([b0620f8](https://github.com/mkdocstrings/griffe/commit/b0620f86e1767183d776771992ce12f961efe395) by Timothée Mazzucotelli). [Issue #137](https://github.com/mkdocstrings/griffe/issues/137)
- Get class parameters from parent's `__init__` method ([e8a9fdc](https://github.com/mkdocstrings/griffe/commit/e8a9fdcce1cffdc7db5a216f833d10da6116db5a) by Timothée Mazzucotelli). [Issue #205](https://github.com/mkdocstrings/griffe/issues/205)

### Bug Fixes

- Use all members (declared and inherited) when checking for breakages, avoid false-positives when a member of a class is moved into a parent class ([1c4340b](https://github.com/mkdocstrings/griffe/commit/1c4340b09b111313a5a242caa986a2fa3fdef852) by Timothée Mazzucotelli). [Issue #203](https://github.com/mkdocstrings/griffe/issues/203)
- Skip early submodules with dots in their path ([5e81b8a](https://github.com/mkdocstrings/griffe/commit/5e81b8afef4e6ce8294cdbaf348f4f1a05add1d8) by Timothée Mazzucotelli). [Issue #185](https://github.com/mkdocstrings/griffe/issues/185)

### Code Refactoring

- Allow iterating on expressions in both flat and nested ways ([3957fa7](https://github.com/mkdocstrings/griffe/commit/3957fa70abf3f2d8af1a4ab4b1041b873bc724e0) by Timothée Mazzucotelli).

## [0.35.2](https://github.com/mkdocstrings/griffe/releases/tag/0.35.2) - 2023-08-27

<small>[Compare with 0.35.1](https://github.com/mkdocstrings/griffe/compare/0.35.1...0.35.2)</small>

### Code Refactoring

- Be more strict when parsing sections in Google docstrings ([6a8a228](https://github.com/mkdocstrings/griffe/commit/6a8a2280f8910d4268380400d7888cb8d72b4296) by Timothée Mazzucotelli). [Issue #204](https://github.com/mkdocstrings/griffe/issues/204)

## [0.35.1](https://github.com/mkdocstrings/griffe/releases/tag/0.35.1) - 2023-08-26

<small>[Compare with 0.35.0](https://github.com/mkdocstrings/griffe/compare/0.35.0...0.35.1)</small>

### Bug Fixes

- Preserve inherited attribute on alias inherited members ([1e19e7b](https://github.com/mkdocstrings/griffe/commit/1e19e7b2c3f2bb10c822c7d8b63b04a76024b4f7) by Timothée Mazzucotelli). [Issue mkdocstrings/python#102](https://github.com/mkdocstrings/python/issues/102)

## [0.35.0](https://github.com/mkdocstrings/griffe/releases/tag/0.35.0) - 2023-08-24

<small>[Compare with 0.34.0](https://github.com/mkdocstrings/griffe/compare/0.34.0...0.35.0)</small>

### Features

- Add an `is_public` helper method to guess if an object is public ([b823639](https://github.com/mkdocstrings/griffe/commit/b8236391f4ac8b16e9ee861c322e75ea10d6a39b) by Timothée Mazzucotelli).
- Add option to Google parser allowing to parse Returns sections with or without multiple items ([65fee70](https://github.com/mkdocstrings/griffe/commit/65fee70cf87399b7da92f054180791de0eb4f22d) by Antoine Dechaume). [PR #196](https://github.com/mkdocstrings/griffe/pull/196)

### Bug Fixes

- Allow passing `warn_unknown_params` option to Google and Numpy parsers ([5bf0746](https://github.com/mkdocstrings/griffe/commit/5bf07468d38a158f8e58e3e1c562e8d886d83321) by Timothée Mazzucotelli).

### Code Refactoring

- Preserve alias members path by re-aliasing members instead of returning target's members ([d400cb1](https://github.com/mkdocstrings/griffe/commit/d400cb13c8b7c250ff1e6b6c8ec9be1c7b6ff989) by Timothée Mazzucotelli).

## [0.34.0](https://github.com/mkdocstrings/griffe/releases/tag/0.34.0) - 2023-08-20

<small>[Compare with 0.33.0](https://github.com/mkdocstrings/griffe/compare/0.33.0...0.34.0)</small>

### Features

- Allow checking if docstring section is empty or not with `if section` ([f6cf559](https://github.com/mkdocstrings/griffe/commit/f6cf559db50718e86cde40eae9d14489cabd9ed8) by Timothée Mazzucotelli).
- Implement Functions (or Methods), Classes and Modules docstring sections ([929e615](https://github.com/mkdocstrings/griffe/commit/929e6158c093b021ba80773e17613406b38fbf0c) by Timothée Mazzucotelli).
- Allow passing a docstring parser name instead of its enumeration value ([ce59b7d](https://github.com/mkdocstrings/griffe/commit/ce59b7dca69e3a9946a0735405535e296e0ec9c9) by Timothée Mazzucotelli).

### Code Refactoring

- Explicit checks for subprocess runs ([cc3ca2e](https://github.com/mkdocstrings/griffe/commit/cc3ca2e18877c17fe23e2ceeb1c13e10c9fe46d2) by Timothée Mazzucotelli).

## [0.33.0](https://github.com/mkdocstrings/griffe/releases/tag/0.33.0) - 2023-08-16

<small>[Compare with 0.32.3](https://github.com/mkdocstrings/griffe/compare/0.32.3...0.33.0)</small>

### Breaking Changes

- Removed `griffe.expressions.Expression` in favor of [`griffe.Expr`][] and subclasses
- Removed `griffe.expressions.Name` in favor of [`griffe.ExprName`][]

### Features

- Add `-V`, `--version` CLI flag to show version ([a41515f](https://github.com/mkdocstrings/griffe/commit/a41515f39e6e5e2e28d68980c44cc07a7e0ebbe0) by jgart). [Issue #186](https://github.com/mkdocstrings/griffe/issues/186), [PR #187](https://github.com/mkdocstrings/griffe/pull/187), Co-authored-by: Timothée Mazzucotelli <pawamoy@pm.me>

### Code Refactoring

- Improve expressions ([66c8ad5](https://github.com/mkdocstrings/griffe/commit/66c8ad5074e1475aa88a51d8652b5e197760d774) and [0fe8f91](https://github.com/mkdocstrings/griffe/commit/0fe8f9155b571714b0fe2a1bd7aef0b9b0738b08) by Timothée Mazzucotelli).

## [0.32.3](https://github.com/mkdocstrings/griffe/releases/tag/0.32.3) - 2023-07-17

<small>[Compare with 0.32.2](https://github.com/mkdocstrings/griffe/compare/0.32.2...0.32.3)</small>

### Bug Fixes

- Fix detecting whether an object should be an alias during inspection ([6a63b37](https://github.com/mkdocstrings/griffe/commit/6a63b375db7d639dd05589c56a2f89d1be9d66a8) by Timothée Mazzucotelli). [Issue #180](https://github.com/mkdocstrings/griffe/issues/180)

### Code Refactoring

- Improve log message when trying to stubs-merge objects of different kinds ([d34a3ba](https://github.com/mkdocstrings/griffe/commit/d34a3ba4bbd15c3fafe9cc5e2e82a2281cf3e094) by Timothée Mazzucotelli).
- De-duplicate stubs merging log message ([cedc062](https://github.com/mkdocstrings/griffe/commit/cedc062cd4035a4ad0f3a14b4ef31bea4e39374d) by Timothée Mazzucotelli).

## [0.32.2](https://github.com/mkdocstrings/griffe/releases/tag/0.32.2) - 2023-07-17

<small>[Compare with 0.32.1](https://github.com/mkdocstrings/griffe/compare/0.32.1...0.32.2)</small>

### Bug Fixes

- Keep parentheses around tuples, except within subscripts ([df6e636](https://github.com/mkdocstrings/griffe/commit/df6e636c3ecfaa6befdfdaf26e898e1a71218675) by Timothée Mazzucotelli). [Issue mkdocstrings/python#88](https://github.com/mkdocstrings/python/issues/88)

## [0.32.1](https://github.com/mkdocstrings/griffe/releases/tag/0.32.1) - 2023-07-15

<small>[Compare with 0.32.0](https://github.com/mkdocstrings/griffe/compare/0.32.0...0.32.1)</small>

### Bug Fixes

- Fix aliases for direct nested imports ([e9867f7](https://github.com/mkdocstrings/griffe/commit/e9867f78044a2a33b575e274224d3a4c16b62439) by Timothée Mazzucotelli). [Issue mkdocstrings/python#32](https://github.com/mkdocstrings/python/issues/32)

### Code Refactoring

- Simplify AST imports, stop using deprecated code from `ast` ([21d5832](https://github.com/mkdocstrings/griffe/commit/21d5832ba6db051b9754f515f1d7125126dd801f) by Timothée Mazzucotelli). [Issue #179](https://github.com/mkdocstrings/griffe/issues/179)

## [0.32.0](https://github.com/mkdocstrings/griffe/releases/tag/0.32.0) - 2023-07-13

<small>[Compare with 0.31.0](https://github.com/mkdocstrings/griffe/compare/0.31.0...0.32.0)</small>

### Deprecations

- Classes `InspectorExtension` and `VisitorExtension`
    are deprecated in favor of [`Extension`][griffe.Extension].
    As a side-effect, the `hybrid` extension is also deprecated.
    See [how to use and write extensions](guide/users/extending.md).

### Breaking Changes

- Module `griffe.agents.base` was removed
- Module `griffe.docstrings.markdown` was removed
- Class `ASTNode` was removed
- Class `BaseInspector` was removed
- Class `BaseVisitor` was removed
- Function `get_parameter_default` was removed
- Function `load_extension` was removed (made private)
- Function `patch_ast` was removed
- Function `tmp_worktree` was removed (made private)
- Type [`Extension`][griffe.Extension] is now a class

### Features

- Numpy parser: handle return section items with just type, or no name and no type ([bdec37d](https://github.com/mkdocstrings/griffe/commit/bdec37dd32a5d4e089ee5e14e5a66be645bb8360) by Michael Chow). [Issue #173](https://github.com/mkdocstrings/griffe/issues/173), [PR #174](https://github.com/mkdocstrings/griffe/pull/174), Co-authored-by: Timothée Mazzucotelli <pawamoy@pm.me>
- Rework extension system ([dea4c83](https://github.com/mkdocstrings/griffe/commit/dea4c830e3bfa0bf7c9f307975cb53e1314c50eb) by Timothée Mazzucotelli).
- Parse attribute values, parameter defaults and decorators as expressions ([7b653b3](https://github.com/mkdocstrings/griffe/commit/7b653b31bd9c38bf8d960baa5ab75dd56c62fbcb) by Timothée Mazzucotelli).
- Add loader option to avoid storing source code, reducing memory footprint ([d592edf](https://github.com/mkdocstrings/griffe/commit/d592edf477d9e7a5f9723c96cc259db65b1cae71) by Timothée Mazzucotelli).
- Add `extra` attribute to objects ([707a348](https://github.com/mkdocstrings/griffe/commit/707a34833f56cf4a1aa302cb1201ad96ff361252) by Timothée Mazzucotelli).

### Bug Fixes

- Numpy-style: don't strip spaces from the left of indented lines ([f13fc0a](https://github.com/mkdocstrings/griffe/commit/f13fc0a7edc7c8ac14c8c482b58735a5f7301bd6) by Timothée Mazzucotelli). [Discussion #587](https://github.com/mkdocstrings/mkdocstrings/discussions/587)
- Fix relative paths for old versions when checking API ([96fd45b](https://github.com/mkdocstrings/griffe/commit/96fd45b41186eb503d6a2ff4e587cae427aea013) by Timothée Mazzucotelli).

### Performance Improvements

- Don't store source when dumping as JSON ([d7f314a](https://github.com/mkdocstrings/griffe/commit/d7f314a62dd40c38c8c76ec7102233a588c1e64a) by Timothée Mazzucotelli).
- Stop caching properties on Object methods ([15bdd74](https://github.com/mkdocstrings/griffe/commit/15bdd744db1f089f4448b952f9acf184c43289ea) by Timothée Mazzucotelli).
- Stop patching AST, use functions instead ([7302f17](https://github.com/mkdocstrings/griffe/commit/7302f178392c70890d083a1617f1cf4e72395be3) by Timothée Mazzucotelli). [Issue #171](https://github.com/mkdocstrings/griffe/issues/171)

### Code Refactoring

- Privatize/remove objects ([fdeb16f](https://github.com/mkdocstrings/griffe/commit/fdeb16f61cb5ae7db2394ef2a8ec31843b7ae85b) by Timothée Mazzucotelli).
- Document public objects with `__all__` ([db0e0e3](https://github.com/mkdocstrings/griffe/commit/db0e0e340efcd48904f448a6e4397a9df36ac50f) by Timothée Mazzucotelli).
- Remove base visitor and inspector ([bc446e4](https://github.com/mkdocstrings/griffe/commit/bc446e4ac9445636be7fdadbfc0b056cbc1d73e3) by Timothée Mazzucotelli).
- Auto-register module in collection within loading helpers ([591bacc](https://github.com/mkdocstrings/griffe/commit/591bacc6c46d91beb30f6e01e0ae96f8e3102cf8) by Timothée Mazzucotelli). [Issue #177](https://github.com/mkdocstrings/griffe/issues/177)

## [0.31.0](https://github.com/mkdocstrings/griffe/releases/tag/0.31.0) - 2023-07-04

<small>[Compare with 0.30.1](https://github.com/mkdocstrings/griffe/compare/0.30.1...0.31.0)</small>

### Breaking Changes

- Drop support for Python 3.7
- API changes:
    - [`GriffeLoader.resolve_aliases(only_exported)`][griffe.GriffeLoader.resolve_aliases]: Deprecated parameter was removed and replaced by `implicit` (inverse semantics)
    - [`GriffeLoader.resolve_aliases(only_known_modules)`][griffe.GriffeLoader.resolve_aliases]: Deprecated parameter was removed and replaced by `external` (inverse semantics)
    - [`LinesCollection.tokens`][griffe.LinesCollection]: Public object was removed (Python 3.7)
    - `ASTNode.end_lineno`: Public object was removed (Python 3.7)
    - `griffe.agents.extensions`: Deprecated module was removed and replaced by `griffe.extensions`

### Features

- Add `--color`, `--no-color` options to check subcommand ([eac783c](https://github.com/mkdocstrings/griffe/commit/eac783c2df5a0ba57612b71b0797a74cf7fc8e39) by Timothée Mazzucotelli).

### Bug Fixes

- Report removed public modules ([68906cb](https://github.com/mkdocstrings/griffe/commit/68906cb6083e5f7cad3a1cb5a74878d6e74f9c69) by Timothée Mazzucotelli).

### Code Refactoring

- Improve check output ([6b0a1f0](https://github.com/mkdocstrings/griffe/commit/6b0a1f0397d153a95d1b6c69d109ce141e39e1f1) by Timothée Mazzucotelli).
- Remove deprecated `griffe.agents.extensions` module ([b555c78](https://github.com/mkdocstrings/griffe/commit/b555c788b624fa5aa0c871e2c199079868252f22) by Timothée Mazzucotelli).
- Remove deprecated parameters from loader's `resolve_aliases` method ([dd98acd](https://github.com/mkdocstrings/griffe/commit/dd98acd5f0c85661c7a00002805c92caa4c11a21) by Timothée Mazzucotelli).
- Drop Python 3.7 support ([e4be30a](https://github.com/mkdocstrings/griffe/commit/e4be30a4c1025fd2f99f088c76f8e263714d8e33) by Timothée Mazzucotelli).

## [0.30.1](https://github.com/mkdocstrings/griffe/releases/tag/0.30.1) - 2023-07-02

<small>[Compare with 0.30.0](https://github.com/mkdocstrings/griffe/compare/0.30.0...0.30.1)</small>

### Bug Fixes

- Prevent duplicate yields of breaking changes ([9edef90](https://github.com/mkdocstrings/griffe/commit/9edef90d6c54b330046582e2a52ad88b5798d32c) by Timothée Mazzucotelli). [Issue #162](https://github.com/mkdocstrings/griffe/issues/162)
- Prevent alias resolution errors when checking for API breaking changes ([93c964a](https://github.com/mkdocstrings/griffe/commit/93c964a4cc3f759d101db45af5816a4d3b07c85e) by Timothée Mazzucotelli). [Issue #145](https://github.com/mkdocstrings/griffe/issues/145)
- Handle Git errors when checking for API breaking changes ([f9e8ba3](https://github.com/mkdocstrings/griffe/commit/f9e8ba381b75f650cfeb7bc96c976fec2251ac7a) by Timothée Mazzucotelli). [Issue #144](https://github.com/mkdocstrings/griffe/issues/144)

### Code Refactoring

- Force remove worktree branch when done checking ([45332ba](https://github.com/mkdocstrings/griffe/commit/45332ba89e213b4f9490ea7d2507d972267bed73) by Timothée Mazzucotelli).
- Change command to obtain latest tag ([f70f630](https://github.com/mkdocstrings/griffe/commit/f70f630ef7c67589d60c17ef4fb19c90127b2e06) by Timothée Mazzucotelli).

## [0.30.0](https://github.com/mkdocstrings/griffe/releases/tag/0.30.0) - 2023-06-30

<small>[Compare with 0.29.1](https://github.com/mkdocstrings/griffe/compare/0.29.1...0.30.0)</small>

### Features

- Add `allow_section_blank_line` option to the Numpy parser ([245845e](https://github.com/mkdocstrings/griffe/commit/245845ecaabedf4abb0af80d783702e55ea83883) by Michael Chow). [Issue #167](https://github.com/mkdocstrings/griffe/issues/167), [PR #168](https://github.com/mkdocstrings/griffe/pull/168)
- Support inheritance ([08bbe09](https://github.com/mkdocstrings/griffe/commit/08bbe09879dfa5440a359c8b2ad0b896c20c1dfc) by Timothée Mazzucotelli). [PR #170](https://github.com/mkdocstrings/griffe/pull/170)

### Bug Fixes

- Handle semi-colons in pth files ([e2ec661](https://github.com/mkdocstrings/griffe/commit/e2ec661e614df6c5f4fda1444468363777985b7c) by Michael Chow). [Issue #172](https://github.com/mkdocstrings/griffe/issues/172), [PR #175](https://github.com/mkdocstrings/griffe/pull/175)

### Code Refactoring

- Split members API in two parts: producer and consumer ([2269449](https://github.com/mkdocstrings/griffe/commit/226944983a9073d643ed09b47e7d3f99c76d3d5e) by Timothée Mazzucotelli). [PR #170](https://github.com/mkdocstrings/griffe/pull/170)

## [0.29.1](https://github.com/mkdocstrings/griffe/releases/tag/0.29.1) - 2023-06-19

<small>[Compare with 0.29.0](https://github.com/mkdocstrings/griffe/compare/0.29.0...0.29.1)</small>

### Bug Fixes

- Fix detection of optional and default in Numpydoc-style parameters ([3509106](https://github.com/mkdocstrings/griffe/commit/3509106399c5475ef71bb074dfa8f885e6759058) by Timothée Mazzucotelli). [Issue #165](https://github.com/mkdocstrings/griffe/issues/165)
- Fallback to string literal when parsing fails with syntax error ([53827c8](https://github.com/mkdocstrings/griffe/commit/53827c8c073e55a7f6d8ef61b36e9baf51f1c2bc) by Timothée Mazzucotelli). [Issue mkdocstrings/python#80](https://github.com/mkdocstrings/python/issues/80)
- Don't mutate finder's import paths ([a9e025a](https://github.com/mkdocstrings/griffe/commit/a9e025a16571b83713ce44f2be2356e498a847a2) by Timothée Mazzucotelli).
- Respect `external` when expanding wildcards ([8ef92c8](https://github.com/mkdocstrings/griffe/commit/8ef92c873db175dbd35e6d09277f6023a8fde32d) by Timothée Mazzucotelli).
- Extract actual type for yielded/received values ([3ea37ba](https://github.com/mkdocstrings/griffe/commit/3ea37ba2bcafea47f4b28bab6ae916ecb921b5ce) by Timothée Mazzucotelli). [Issue mkdocstrings/python#75](https://github.com/mkdocstrings/python/issues/75)

### Code Refactoring

- Improve error handling when importing a module ([a732e21](https://github.com/mkdocstrings/griffe/commit/a732e217622cc5ab2161479b9dde0ce59e2361af) by Timothée Mazzucotelli).
- Improve tests helpers (accept all visit/inspection parameters) ([6da5869](https://github.com/mkdocstrings/griffe/commit/6da586963cddff4dceadcd4b485dbb805830b6ea) by Timothée Mazzucotelli).
- Allow passing a modules collection to the inspector, for consistency with the visitor ([5f73a28](https://github.com/mkdocstrings/griffe/commit/5f73a28a09a4b445fa253356034c5ef40b9ecfec) by Timothée Mazzucotelli).
- Always add import path of module to inspect when it has a file path ([4021e6f](https://github.com/mkdocstrings/griffe/commit/4021e6fe9f5e06543f9709e7ae42f6ad8cd0b093) by Timothée Mazzucotelli).

## [0.29.0](https://github.com/mkdocstrings/griffe/releases/tag/0.29.0) - 2023-05-26

<small>[Compare with 0.28.2](https://github.com/mkdocstrings/griffe/compare/0.28.2...0.29.0)</small>

### Features

- Provide test helpers and pytest fixtures ([611ed58](https://github.com/mkdocstrings/griffe/commit/611ed5868e22ac3ada6467ba25c6dab606f5dee7) by Timothée Mazzucotelli).

## [0.28.2](https://github.com/mkdocstrings/griffe/releases/tag/0.28.2) - 2023-05-24

<small>[Compare with 0.28.1](https://github.com/mkdocstrings/griffe/compare/0.28.1...0.28.2)</small>

### Bug Fixes

- Correctly resolve full expressions ([fa57f4f](https://github.com/mkdocstrings/griffe/commit/fa57f4ff6495679b4e7e70d72d5adb80bd8ebc56) by Timothée Mazzucotelli). [Issue mkdocstrings/autorefs#23](https://github.com/mkdocstrings/autorefs/issues/23)
- Use `full` attribute instead of `canonical` for expressions ([4338ccc](https://github.com/mkdocstrings/griffe/commit/4338ccc9234f0c4df0ea302a81092a4f3d29f0bf) by Michael Chow). [Issue #163](https://github.com/mkdocstrings/griffe/issues/163), [PR #164](https://github.com/mkdocstrings/griffe/pull/164)

## [0.28.1](https://github.com/mkdocstrings/griffe/releases/tag/0.28.1) - 2023-05-22

<small>[Compare with 0.28.0](https://github.com/mkdocstrings/griffe/compare/0.28.0...0.28.1)</small>

### Bug Fixes

- Return docstring warnings as warnings, not attributes ([7bd51ba](https://github.com/mkdocstrings/griffe/commit/7bd51ba7c9c268a1cc378d38fdff3a891adc520c) by Matthew Anderson). [PR #161](https://github.com/mkdocstrings/griffe/pull/161)

### Code Refactoring

- Refactor AST nodes parsers ([7e53127](https://github.com/mkdocstrings/griffe/commit/7e5312744cd7f6ad3baba54fe8194d15896f5e6d) by Timothée Mazzucotelli). [Issue #160](https://github.com/mkdocstrings/griffe/issues/160)
- Full expressions use canonical names ([65c7184](https://github.com/mkdocstrings/griffe/commit/65c7184b5462b70debce1195c69449935cb0a0b1) by Timothée Mazzucotelli).

## [0.28.0](https://github.com/mkdocstrings/griffe/releases/tag/0.28.0) - 2023-05-17

<small>[Compare with 0.27.5](https://github.com/mkdocstrings/griffe/compare/0.27.5...0.28.0)</small>

### Features

- Support scikit-build-core editable modules (partially) ([eb64779](https://github.com/mkdocstrings/griffe/commit/eb64779cb5408553bd4923ab9cdfc72d0b5e6103) by Timothée Mazzucotelli). [Issue #154](https://github.com/mkdocstrings/griffe/issues/154)

### Bug Fixes

- Parse complex, stringified annotations ([f743616](https://github.com/mkdocstrings/griffe/commit/f74361684a2cd5db153875b8880788c254828e95) by Timothée Mazzucotelli). [Issue #159](https://github.com/mkdocstrings/griffe/issues/159)

## [0.27.5](https://github.com/mkdocstrings/griffe/releases/tag/0.27.5) - 2023-05-12

<small>[Compare with 0.27.4](https://github.com/mkdocstrings/griffe/compare/0.27.4...0.27.5)</small>

### Code Refactoring

- Represent function using their names when inspecting default values ([9116c1f](https://github.com/mkdocstrings/griffe/commit/9116c1fbb562c894547d72207921c02259147958) by Timothée Mazzucotelli). [Issue mkdocstrings/mkdocstrings#180](https://github.com/mkdocstrings/mkdocstrings/issues/180)

## [0.27.4](https://github.com/mkdocstrings/griffe/releases/tag/0.27.4) - 2023-05-10

<small>[Compare with 0.27.3](https://github.com/mkdocstrings/griffe/compare/0.27.3...0.27.4)</small>

### Bug Fixes

- Don't recurse through targets, get directly to final target and handle alias-related errors ([c5bc197](https://github.com/mkdocstrings/griffe/commit/c5bc1973975951389501addf567622c0e3eb71c6) by Timothée Mazzucotelli). [Issue #155](https://github.com/mkdocstrings/griffe/issues/155)

### Code Refactoring

- Follow `.pth` files to extend search paths with editable modules ([79bf724](https://github.com/mkdocstrings/griffe/commit/79bf72498150588d05ccdfc80a898c0330e08247) by Timothée Mazzucotelli). [Issue #154](https://github.com/mkdocstrings/griffe/issues/154)
- Add default values to `_load_packages` helper ([f104c20](https://github.com/mkdocstrings/griffe/commit/f104c20304dcf24c5d2e39220302a941db4161eb) by Timothée Mazzucotelli).

## [0.27.3](https://github.com/mkdocstrings/griffe/releases/tag/0.27.3) - 2023-05-05

<small>[Compare with 0.27.2](https://github.com/mkdocstrings/griffe/compare/0.27.2...0.27.3)</small>

### Bug Fixes

- Allow setting docstring through alias ([2e0f553](https://github.com/mkdocstrings/griffe/commit/2e0f553c833e9b27f5e97c05065c2127212b603c) by Timothée Mazzucotelli).
- Prevent infinite recursion ([0e98546](https://github.com/mkdocstrings/griffe/commit/0e985460eb886ea832e7cbefca261620eedb0e56) by Timothée Mazzucotelli). [Issue #155](https://github.com/mkdocstrings/griffe/issues/155)

## [0.27.2](https://github.com/mkdocstrings/griffe/releases/tag/0.27.2) - 2023-05-03

<small>[Compare with 0.27.1](https://github.com/mkdocstrings/griffe/compare/0.27.1...0.27.2)</small>

### Dependencies

- Remove async extra (aiofiles) ([70d9b93](https://github.com/mkdocstrings/griffe/commit/70d9b9305370f03c221876838aaad9b72dc388d3) by Timothée Mazzucotelli).

### Bug Fixes

- Support walrus operator ([bf721f4](https://github.com/mkdocstrings/griffe/commit/bf721f4dd2bb7f1a6695b5c880df821920b994a6) by Timothée Mazzucotelli). [Issue #152](https://github.com/mkdocstrings/griffe/issues/152)
- Respect `ClassVar` annotation ([60e01c1](https://github.com/mkdocstrings/griffe/commit/60e01c126df4e0529fe3806f9c2637a5a45dd138) by Victor Westerhuis). [PR #150](https://github.com/mkdocstrings/griffe/pull/150), Co-authored-by: Timothée Mazzucotelli <pawamoy@pm.me>
- Add missing "other args" section aliases ([f5c0a0e](https://github.com/mkdocstrings/griffe/commit/f5c0a0ee70c34063ea38a8e76dcba4923f9673cb) by Timothée Mazzucotelli).

### Code Refactoring

- Move utils from cli to respective modules ([c6ce49e](https://github.com/mkdocstrings/griffe/commit/c6ce49eb75c1799982b40a7862a1a7888f0fab93) by Timothée Mazzucotelli).

## [0.27.1](https://github.com/mkdocstrings/griffe/releases/tag/0.27.1) - 2023-04-16

<small>[Compare with 0.27.0](https://github.com/mkdocstrings/griffe/compare/0.27.0...0.27.1)</small>

### Bug Fixes

- Actually parse warnings sections ([bc00da5](https://github.com/mkdocstrings/griffe/commit/bc00da5e9dfe4b2aee906000759e0c1e0a2f893b) by Timothée Mazzucotelli).
- Allow Raises and Warns items to start with a newline ([f3b088c](https://github.com/mkdocstrings/griffe/commit/f3b088c02b3be86934125b142876b0dfb3702677) by Victor Westerhuis). [PR #149](https://github.com/mkdocstrings/griffe/pull/149), Co-authored-by: Timothée Mazzucotelli <pawamoy@pm.me>

## [0.27.0](https://github.com/mkdocstrings/griffe/releases/tag/0.27.0) - 2023-04-10

<small>[Compare with 0.26.0](https://github.com/mkdocstrings/griffe/compare/0.26.0...0.27.0)</small>

### Features

- Implement basic handling of Alias for breaking changes ([aa8ce00](https://github.com/mkdocstrings/griffe/commit/aa8ce009c8d69f7830bc46bc80dac34907b8ae83) by Yurii). [PR #140](https://github.com/mkdocstrings/griffe/pull/140), Co-authored-by: Timothée Mazzucotelli <pawamoy@pm.me>

### Bug Fixes

- Support `Literal` imported from `typing_extensions` ([3a16e58](https://github.com/mkdocstrings/griffe/commit/3a16e5858649f7d786ef8a60b9dfd588f406cd9d) by Timothée Mazzucotelli). [Issue mkdocstrings/mkdocstrings#545](https://github.com/mkdocstrings/mkdocstrings/issues/545)
- Fix parameter default checking logic and diff tests ([1b940fd](https://github.com/mkdocstrings/griffe/commit/1b940fd270b3e51dc0f62edb500a6a3e85908953) by Timothée Mazzucotelli).

## [0.26.0](https://github.com/mkdocstrings/griffe/releases/tag/0.26.0) - 2023-04-03

<small>[Compare with 0.25.5](https://github.com/mkdocstrings/griffe/compare/0.25.5...0.26.0)</small>

### Breaking Changes

- `AliasResolutionError` instances don't have a `target_path` attribute anymore.
    It is instead replaced by an `alias` attribute which is a reference to an `Alias` instance.
- Lots of positional-or-keyword parameters were changed to keyword-only parameters.

### Deprecations

- The `griffe.agents.extensions` module was moved to `griffe.extensions`.
    The old path is deprecated.

### Features

- Support newer versions of `editables` ([ab7a3be](https://github.com/mkdocstrings/griffe/commit/ab7a3be3902af5f4af1d1e762b2b6e532826569f) by Timothée Mazzucotelli): the names of editable modules have changed from `__editables_*` to `_editable_impl_*`.
- Provide a JSON schema ([7dfed39](https://github.com/mkdocstrings/griffe/commit/7dfed391c7714a9d1aea9223e1f8c9403d47e8bb) by Timothée Mazzucotelli).
- Allow hybrid extension to filter objects and run multiple inspectors ([f8ff53a](https://github.com/mkdocstrings/griffe/commit/f8ff53a69a3a131998649d1a9ba272827b7f2adc) by Timothée Mazzucotelli).
- Allow loading extension from file path ([131454e](https://github.com/mkdocstrings/griffe/commit/131454eece81da33cd7f1a8bf2ae030950df8441) by Timothée Mazzucotelli).
- Add back `relative_filepath` which now really returns the filepath relative to the current working directory ([40fe0c5](https://github.com/mkdocstrings/griffe/commit/40fe0c53be8ff72f254bd88e9c9cf6df36d3bcb9) by Timothée Mazzucotelli).

### Bug Fixes

- Fix JSON schema for ending line numbers (and add test) ([318c6b4](https://github.com/mkdocstrings/griffe/commit/318c6b41c0160070de1b10118d210cacd5f2e711) by Timothée Mazzucotelli).
- Prevent cyclic aliases by not overwriting a module member with an indirect alias to itself ([c188a95](https://github.com/mkdocstrings/griffe/commit/c188a95b823e876f89ba9046df2cb06348f92459) by Timothée Mazzucotelli). [Issue #122](https://github.com/mkdocstrings/griffe/issues/122)
- Prevent alias resolution errors when copying docstring or labels from previously existing attribute ([48747b6](https://github.com/mkdocstrings/griffe/commit/48747b6d14bdf1be03cfa5bbf849771e3e6801b0) by Timothée Mazzucotelli).
- Fix Google admonition regular expression ([ef0be5f](https://github.com/mkdocstrings/griffe/commit/ef0be5f8f276a5ef2397ad89c0cfce0e1b41020e) by Timothée Mazzucotelli).
- Add back `griffe.agents.extensions` module (deprecated) ([7129477](https://github.com/mkdocstrings/griffe/commit/7129477184f0b88d3bf165dfe8e1f6158c30914a) by Timothée Mazzucotelli).
- Forward class attribute docstrings to instances ([7bf4952](https://github.com/mkdocstrings/griffe/commit/7bf49528541e211af37c2ac5c1a74a4523699c65) by Rodrigo Girão Serrão). [Issue #128](https://github.com/mkdocstrings/griffe/issues/128), [PR #135](https://github.com/mkdocstrings/griffe/pull/135)
- Prevent errors related to getting attributes in the inspector ([5d15d27](https://github.com/mkdocstrings/griffe/commit/5d15d276259a4b9a70fbe490d86234e667711180) by Timothée Mazzucotelli).
- Catch "member does not exist" errors while expanding wildcards ([a966022](https://github.com/mkdocstrings/griffe/commit/a9660220c0b5e9e786877efa228452a643e93c76) by Timothée Mazzucotelli).
- Catch more inspection errors ([4f6eef9](https://github.com/mkdocstrings/griffe/commit/4f6eef9b0fbcdf56d61ac4bec9dc4ef3b90dd116) by Timothée Mazzucotelli).

### Code Refactoring

- Log final path after resolving alias ([c7ec7f7](https://github.com/mkdocstrings/griffe/commit/c7ec7f7ca029492ced68737851d66256c5035f70) by Timothée Mazzucotelli).
- Move extensions one level up ([67ebd71](https://github.com/mkdocstrings/griffe/commit/67ebd71f9b0933f08b263d0b21520dc0b1a5c4ff) by Timothée Mazzucotelli).
- Set default `when` value on extension base classes ([e8ad889](https://github.com/mkdocstrings/griffe/commit/e8ad8893aaad2549bff134a7bf3dfe5a86bfc960) by Timothée Mazzucotelli).
- Rename `relative_filepath` to `relative_package_filepath` to better express what it does ([6148f85](https://github.com/mkdocstrings/griffe/commit/6148f85c56848c6bb3e7df8986f1bb208e7083cf) by Timothée Mazzucotelli).
- Show file name and line number in alias resolution error messages ([c48928d](https://github.com/mkdocstrings/griffe/commit/c48928df4a75be35771d39bf96699d801485b31d) by Timothée Mazzucotelli).

## [0.25.5](https://github.com/mkdocstrings/griffe/releases/tag/0.25.5) - 2023-02-16

<small>[Compare with 0.25.4](https://github.com/mkdocstrings/griffe/compare/0.25.4...0.25.5)</small>

### Bug Fixes

- Fix parsing empty lines with indentation in Google docstrings ([705edff](https://github.com/mkdocstrings/griffe/commit/705edff6c208281bdab387a464799de613b087b5) by Timothée Mazzucotelli). [Issue #129](https://github.com/mkdocstrings/griffe/issues/129)

## [0.25.4](https://github.com/mkdocstrings/griffe/releases/tag/0.25.4) - 2023-01-19

<small>[Compare with 0.25.3](https://github.com/mkdocstrings/griffe/compare/0.25.3...0.25.4)</small>

### Bug Fixes

- Fix creation of aliases to modules when inspecting ([54242cb](https://github.com/mkdocstrings/griffe/commit/54242cbdbbcb68785942fa327113cd6508815fa9) by Timothée Mazzucotelli).
- Support (setuptools) editable packages with multiple roots ([bd37dfb](https://github.com/mkdocstrings/griffe/commit/bd37dfb16b43fac53207b426ee02218e57a5d5d1) by Gilad). [PR #126](https://github.com/mkdocstrings/griffe/pull/126)

## [0.25.3](https://github.com/mkdocstrings/griffe/releases/tag/0.25.3) - 2023-01-04

<small>[Compare with 0.25.2](https://github.com/mkdocstrings/griffe/compare/0.25.2...0.25.3)</small>

### Bug Fixes

- Fix parsing of annotations in Numpy attributes sections ([18fa396](https://github.com/mkdocstrings/griffe/commit/18fa39612b828e2892665b7367f7cdf76908970c) by Timothée Mazzucotelli). [Issue #72](https://github.com/mkdocstrings/griffe/issues/72)

## [0.25.2](https://github.com/mkdocstrings/griffe/releases/tag/0.25.2) - 2022-12-24

<small>[Compare with 0.25.1](https://github.com/mkdocstrings/griffe/compare/0.25.1...0.25.2)</small>

### Bug Fixes

- Make sure passage through aliases is reset ([79733f4](https://github.com/mkdocstrings/griffe/commit/79733f4d03f3f66b948dc17c57404349d9e72c9a) by Timothée Mazzucotelli). [Issue #123](https://github.com/mkdocstrings/griffe/issues/123)
- Ignore cyclic alias errors when updating target aliases ([bb62b2f](https://github.com/mkdocstrings/griffe/commit/bb62b2f744d221efedeba1cb33151b3787d2ee57) by Timothée Mazzucotelli). [Issue #123](https://github.com/mkdocstrings/griffe/issues/123)


## [0.25.1](https://github.com/mkdocstrings/griffe/releases/tag/0.25.1) - 2022-12-20

<small>[Compare with 0.25.0](https://github.com/mkdocstrings/griffe/compare/0.25.0...0.25.1)</small>

### Bug Fixes
- Pass through aliases earlier to prevent infinite recursion ([e533f29](https://github.com/mkdocstrings/griffe/commit/e533f29258838a1e171dea702fb033bfa68ed089) by Timothée Mazzucotelli). [Issue #83](https://github.com/mkdocstrings/griffe/issues/83), [#122](https://github.com/mkdocstrings/griffe/issues/122)

## [0.25.0](https://github.com/mkdocstrings/griffe/releases/tag/0.25.0) - 2022-12-11

<small>[Compare with 0.24.1](https://github.com/mkdocstrings/griffe/compare/0.24.1...0.25.0)</small>

### Breaking changes
- Parameter `only_known_modules` was renamed `external` in the [`expand_wildcards()`][griffe.GriffeLoader.expand_wildcards] method of the loader.
- Exception `UnhandledEditablesModuleError` was renamed `UnhandledEditableModuleError` since we now support editable installation from other packages than `editables`.

### Highlights

- Properties are now fetched as attributes rather than functions, since that is how they are used. This was asked by users, and since Griffe generates signatures for Python APIs (emphasis on **APIs**), it makes sense to return data that matches the interface provided to users. Such property objects in Griffe's output will still have the associated `property` labels of course.
- Lots of bug fixes. These bugs were discovered by running Griffe on *many* major packages as well as the standard library (again). Particularly, alias resolution should be more robust now, and should generate less issues like cyclic aliases, meaning indirect/wildcard imports should be better understood. We still highly discourage the use of wildcard imports :grinning:

### Features

- Support `setuptools` editable modules ([abc18f7](https://github.com/mkdocstrings/griffe/commit/abc18f7b94cea7b7850bb9f14ebc4822beb1d27c) by Timothée Mazzucotelli). [Issue mkdocstrings/mkdocstrings#463](https://github.com/mkdocstrings/mkdocstrings/issues/463)
- Support merging stubs on wildcard imported objects ([0ed9c36](https://github.com/mkdocstrings/griffe/commit/0ed9c363b6b064361d311acee1732e757899291b) by Timothée Mazzucotelli). [Issue #116](https://github.com/mkdocstrings/griffe/issues/116)

### Bug Fixes

- Prevent cyclic alias creation when expanding wildcards ([a77e4e8](https://github.com/mkdocstrings/griffe/commit/a77e4e8bbba8a24d9f604eaff4cc57c6851c14c3) by Timothée Mazzucotelli).
- Don't crash and show hint when wildcard expansion fails ([336faf6](https://github.com/mkdocstrings/griffe/commit/336faf6dff679c970e594151a7a5d2bd99f52af6) by Timothée Mazzucotelli).
- Register top module after inspection ([86454ec](https://github.com/mkdocstrings/griffe/commit/86454ececfa8e88b0f1024bde49e6dd0cb8542d0) by Timothée Mazzucotelli).
- Set alias attributes early ([2ac1a9b](https://github.com/mkdocstrings/griffe/commit/2ac1a9bafb632daa491b3d26f2c39d74c9b31e3d) by Timothée Mazzucotelli).
- Allow writing attributes on aliases ([c8f736e](https://github.com/mkdocstrings/griffe/commit/c8f736efcee354d2c47675413955390e80e77425) by Timothée Mazzucotelli).
- Don't crash on inspection of functions signatures ([051e337](https://github.com/mkdocstrings/griffe/commit/051e337306006a60b4ae0da030a6fb912db1f05c) by Timothée Mazzucotelli).
- Don't crash on inspection of method descriptors' docstrings ([09571bb](https://github.com/mkdocstrings/griffe/commit/09571bb6ffebe041ac9fdd143fc4a1cb239dda63) by Timothée Mazzucotelli).
- Fix stats computing (handle stubs and namespace packages) ([a81f8dc](https://github.com/mkdocstrings/griffe/commit/a81f8dcf9e8eedc3a42cfdaaaaa28ec9379e2c4b) by Timothée Mazzucotelli).
- Support documenting multiple items for optional tuples ([727456d](https://github.com/mkdocstrings/griffe/commit/727456deba90ac01a04119371b72c011755360b6) by Timothée Mazzucotelli). [Issue #117](https://github.com/mkdocstrings/griffe/issues/117)
- Fix comparing names with strings ([37ae0a2](https://github.com/mkdocstrings/griffe/commit/37ae0a2f37c7e446c890d9e1204edddfb3591dc7) by Timothée Mazzucotelli). [Issue #114](https://github.com/mkdocstrings/griffe/issues/114)
- Fix deepcopy crashing because of `__getattr__` ([11b023b](https://github.com/mkdocstrings/griffe/commit/11b023b8bc0575313a9aea1f6ef99944c8b02537) by Timothée Mazzucotelli). [Issue #73](https://github.com/mkdocstrings/griffe/issues/73), [PR #119](https://github.com/mkdocstrings/griffe/pull/119)

### Code Refactoring

- Prevent reloading of failed modules ([8ef14ab](https://github.com/mkdocstrings/griffe/commit/8ef14ab6389bb06e1903c7628dd1d811f2af101a) by Timothée Mazzucotelli).
- Rename `only_known_modules` parameter to `external` ([5f816c6](https://github.com/mkdocstrings/griffe/commit/5f816c67222f9aa1bd008782430501a2de26d5a4) by Timothée Mazzucotelli).
- Rework alias creation decision in the inspector ([f434943](https://github.com/mkdocstrings/griffe/commit/f434943579e02fb02c28f7e2be65293f6ab6b657) by Timothée Mazzucotelli).
- Resolve alias chain recursively ([6cdd3b2](https://github.com/mkdocstrings/griffe/commit/6cdd3b2ed4170347282118c06407b587cd65fd36) by Timothée Mazzucotelli).
- Don't try to stubs-merge identical modules ([7099971](https://github.com/mkdocstrings/griffe/commit/7099971e441d5dd804c0304f010343a558685f9a) by Timothée Mazzucotelli).
- Load properties as attributes ([5c97a45](https://github.com/mkdocstrings/griffe/commit/5c97a45087e0ba8c39a9745d9c5248c4c35909a8) by Timothée Mazzucotelli). [Issue mkdocstrings/python#9](https://github.com/mkdocstrings/python/issues/9)
- Use a cyclic relationship map for inspection ([9a2a711](https://github.com/mkdocstrings/griffe/commit/9a2a7117d2d9d7b8327e640e8760594349531627) by Timothée Mazzucotelli). [PR #115](https://github.com/mkdocstrings/griffe/pull/115)

## [0.24.1](https://github.com/mkdocstrings/griffe/releases/tag/0.24.1) - 2022-11-18

<small>[Compare with 0.24.0](https://github.com/mkdocstrings/griffe/compare/0.24.0...0.24.1)</small>

### Bug Fixes

- Support nested namespace packages ([d571f8f](https://github.com/mkdocstrings/griffe/commit/d571f8f726d50b34c84fbdaa6db3b2059cfe9dec) by Timothée Mazzucotelli).

## [0.24.0](https://github.com/mkdocstrings/griffe/releases/tag/0.24.0) - 2022-11-13

<small>[Compare with 0.23.0](https://github.com/mkdocstrings/griffe/compare/0.23.0...0.24.0)</small>

The "Breaking Changes" and "Deprecations" sections are proudly written
with the help of our new API breakage detection feature :smile:!
Many thanks to Talley Lambert ([@tlambert03](https://github.com/tlambert03))
for the initial code allowing to compare two Griffe trees.

### Breaking Changes

- All parameters of the [`load_git`][griffe.load_git] function, except `module`, are now keyword-only.
- Parameter `try_relative_path` of the [`load_git`][griffe.load_git] function was removed.
- Parameter `commit` was renamed `ref` in the [`load_git`][griffe.load_git] function.
- Parameter `commit` was renamed `ref` in the `tmp_worktree` helper, which will probably become private later.
- Parameters `ref` and `repo` switched positions in the `tmp_worktree` helper.
- All parameters of the [`resolve_aliases`][griffe.GriffeLoader.resolve_aliases] method are now keyword-only.
- Parameters `only_exported` and `only_known_modules` of the [`resolve_module_aliases`][griffe.GriffeLoader.resolve_module_aliases]
    method were removed. This method is most probably not used by anyone, and will probably be made private in the future.

### Deprecations

- Parameters `only_exported` and `only_known_modules` of the [`resolve_aliases`][griffe.GriffeLoader.resolve_aliases]
    method are deprecated in favor of their inverted counter-part `implicit` and `external` parameters.

    - Example before: `loader.resolve_aliases(only_exported=True, only_known_modules=True)`
    - Example after: `loader.resolve_aliases(implicit=False, external=False)`

### Features

- Add CLI command to check for API breakages ([90bded4](https://github.com/mkdocstrings/griffe/commit/90bded46ccaab0417ed57ed11d3b67597f3845ba) by Timothée Mazzucotelli). [Issue #75](https://github.com/mkdocstrings/griffe/issues/75), [PR #105](https://github.com/mkdocstrings/griffe/pull/105)
- Add function to find API breaking changes ([a4f1280](https://github.com/mkdocstrings/griffe/commit/a4f1280a2b65fabc4caa4448d556ac3e83b2f0d0) by Talley Lambert and Timothée Mazzucotelli). [Issue #75](https://github.com/mkdocstrings/griffe/issues/75), [PR #105](https://github.com/mkdocstrings/griffe/pull/105)

### Bug Fixes

- Fix labels mismatch staticmethod-classmethod in inspector ([25060f6](https://github.com/mkdocstrings/griffe/commit/25060f6dad686c73bd32203dc1b3ac789fdc4aef) by Timothée Mazzucotelli). [Issue #111](https://github.com/mkdocstrings/griffe/issues/111)
- Prevent infinite loop while looking for package's parent folder ([f297f1a](https://github.com/mkdocstrings/griffe/commit/f297f1a6550ecadf77c34effe45802327340b1c4) by Timothée Mazzucotelli). [Issue mkdocstrings/mkdocstrings#72](https://github.com/mkdocstrings/mkdocstrings/issues/72)
- Fix comparing names and expressions ([07bffff](https://github.com/mkdocstrings/griffe/commit/07bffff71845d3c9e66007a6a7de269f17312d2b) by Timothée Mazzucotelli).

### Code Refactoring

- Rename some parameters in Git module ([9ad7a2c](https://github.com/mkdocstrings/griffe/commit/9ad7a2c1abde97556d9b4657bef4231e1ef6fa19) by Timothée Mazzucotelli).
- Set parameters as keyword-only ([44c01be](https://github.com/mkdocstrings/griffe/commit/44c01bec147add34ba3f5ac716ac6722540e3ba7) by Timothée Mazzucotelli).
- Remove stars from parameters names ([91dce14](https://github.com/mkdocstrings/griffe/commit/91dce14d7fa3c8c2075a3319fdd7636443fe6cbc) by Timothée Mazzucotelli).
- Refactor CLI to use subcommands ([760b091](https://github.com/mkdocstrings/griffe/commit/760b0918c60911386932cec720418af8d3360c1b) by Timothée Mazzucotelli). [PR #110](https://github.com/mkdocstrings/griffe/pull/110)
- Rename parameters used when resolving aliases ([3d3a4eb](https://github.com/mkdocstrings/griffe/commit/3d3a4eb99e587bd9dd7bfadca4c45737fb886139) by Timothée Mazzucotelli).

## [0.23.0](https://github.com/mkdocstrings/griffe/releases/tag/0.23.0) - 2022-10-26

<small>[Compare with 0.22.2](https://github.com/mkdocstrings/griffe/compare/0.22.2...0.23.0)</small>

### Features

- Support `typing_extensions.overload` ([c29fad5](https://github.com/mkdocstrings/griffe/commit/c29fad58c721399badfc93ff8e0f10a6f92c359e) by Nyuan Zhang). [PR #108](https://github.com/mkdocstrings/griffe/pull/108)

### Bug Fixes

- Log debug instead of errors when failing to parse NumPy annotations for additional sections ([568ff60](https://github.com/mkdocstrings/griffe/commit/568ff60621c0b5cc35ac0e0d0209fa3bc1b2ba8a) by Sigurd Spieckermann). [Issue #93](https://github.com/mkdocstrings/griffe/issues/93), [PR #109](https://github.com/mkdocstrings/griffe/pull/109)
- Don't strip too many parentheses around a call node ([bb5c5e7](https://github.com/mkdocstrings/griffe/commit/bb5c5e71f95c537ca2d19299b157a0bbf59e5279) by Timothée Mazzucotelli). [PR #107](https://github.com/mkdocstrings/griffe/pull/107)
- Guard against more alias resolution errors ([2be135d](https://github.com/mkdocstrings/griffe/commit/2be135d8ab88d6f97175c958e31e76b0d7d8f934) by Timothée Mazzucotelli). [Issue #83](https://github.com/mkdocstrings/griffe/issues/83), [PR #103](https://github.com/mkdocstrings/griffe/pull/103)

## [0.22.2](https://github.com/mkdocstrings/griffe/releases/tag/0.22.2) - 2022-09-24

<small>[Compare with 0.22.1](https://github.com/mkdocstrings/griffe/compare/0.22.1...0.22.2)</small>

### Bug Fixes

- Log debug instead of errors when failing to parse Numpy annotations ([75eeeda](https://github.com/mkdocstrings/griffe/commit/75eeeda2f1181ae680b3d47df3814bad200220d3) by Timothée Mazzucotelli). [Issue #93](https://github.com/mkdocstrings/griffe/issues/93)
- Don't crash on unsupported module names (containing dots) ([6a57194](https://github.com/mkdocstrings/griffe/commit/6a571949000a3d2910990337f96751c0cac7e815) by Timothée Mazzucotelli). [Issue #94](https://github.com/mkdocstrings/griffe/issues/94)
- Show correct docstring line numbers on Python 3.7 ([edd4b6d](https://github.com/mkdocstrings/griffe/commit/edd4b6d23f4399960db4e16a8c269318aef033d6) by Timothée Mazzucotelli). [Issue #98](https://github.com/mkdocstrings/griffe/issues/98)
- Fix parsing of Numpy docstring with an Examples section at the end ([3114727](https://github.com/mkdocstrings/griffe/commit/3114727296891fdd5cacecf487652774ee6e4fc8) by Timothée Mazzucotelli). [Issue #97](https://github.com/mkdocstrings/griffe/issues/97)
- Don't crash on unsupported item in `__all__` (log a warning instead) ([9e5df0a](https://github.com/mkdocstrings/griffe/commit/9e5df0aea8e615217554e5204221a35c9df25938) by Timothée Mazzucotelli). [Issue #92](https://github.com/mkdocstrings/griffe/issues/92)
- Prevent infinite recursion while expanding exports ([68446f7](https://github.com/mkdocstrings/griffe/commit/68446f7ab94536596dccb690fb2cac613cd32460) by Timothée Mazzucotelli).
- Add missing check while expanding wildcards ([7e816ed](https://github.com/mkdocstrings/griffe/commit/7e816ed141d6f13bf1ae7c758c32e68cc663fe0e) by Timothée Mazzucotelli).

## [0.22.1](https://github.com/mkdocstrings/griffe/releases/tag/0.22.1) - 2022-09-10

<small>[Compare with 0.22.0](https://github.com/mkdocstrings/griffe/compare/0.22.0...0.22.1)</small>

### Bug Fixes

- Always use `encoding="utf8"` when reading text files ([3b279bf](https://github.com/mkdocstrings/griffe/commit/3b279bf61afabc7312e9e58745fd19a53d97ac74) by Rudolf Byker). [Issue #99](https://github.com/mkdocstrings/griffe/issues/99), [PR #100](https://github.com/mkdocstrings/griffe/pull/100)

## [0.22.0](https://github.com/mkdocstrings/griffe/releases/tag/0.22.0) - 2022-06-28

<small>[Compare with 0.21.0](https://github.com/mkdocstrings/griffe/compare/0.21.0...0.22.0)</small>

### Features

- Support forward references ([245daea](https://github.com/mkdocstrings/griffe/commit/245daeabc8130bd7ecab86f55c4906d9161b9e73) by Timothée Mazzucotelli). [Issue #86](https://github.com/mkdocstrings/griffe/issues/86)

### Code Refactoring

- Safely parse annotations and values ([b023e2b](https://github.com/mkdocstrings/griffe/commit/b023e2be509f3ac39dbe1ed9adf21247e4416e53) by Timothée Mazzucotelli).

## [0.21.0](https://github.com/mkdocstrings/griffe/releases/tag/0.21.0) - 2022-06-25

<small>[Compare with 0.20.0](https://github.com/mkdocstrings/griffe/compare/0.20.0...0.21.0)</small>

### Features

- Add `load_git` function allowing to load data from a specific git ref ([b2c3946](https://github.com/mkdocstrings/griffe/commit/b2c39467630c33edc914dd7e6dc96fb611267905) by Talley Lambert). [Issue #75](https://github.com/mkdocstrings/griffe/issues/75), [PR #76](https://github.com/mkdocstrings/griffe/pull/76)

### Bug Fixes

- Fix detecting and merging stubs for single-file packages ([6a82542](https://github.com/mkdocstrings/griffe/commit/6a825423a9dfd86343532c2872980240f2e98b74) by Talley Lambert). [Issue #77](https://github.com/mkdocstrings/griffe/issues/77), [PR #78](https://github.com/mkdocstrings/griffe/pull/78)
- Fix parsing ExtSlice nodes when getting values ([b2fe968](https://github.com/mkdocstrings/griffe/commit/b2fe9684f274786decdf9fb395bebc5057235eda) by Timothée Mazzucotelli). [Issue #87](https://github.com/mkdocstrings/griffe/issues/87)
- Don't trigger alias resolution when merging stubs ([2b88627](https://github.com/mkdocstrings/griffe/commit/2b88627862b8db50045cc97ae5644abd36f36b5a) by Timothée Mazzucotelli). [Issue #89](https://github.com/mkdocstrings/griffe/issues/89)
- Fix handling of .pth files ([f212dd3](https://github.com/mkdocstrings/griffe/commit/f212dd3b92f51a64795fdbb30aefd0a730393523) by Gabriel Dugny). [Issue #84](https://github.com/mkdocstrings/griffe/issues/84), [PR #85](https://github.com/mkdocstrings/griffe/pull/85)

## [0.20.0](https://github.com/mkdocstrings/griffe/releases/tag/0.20.0) - 2022-06-03

<small>[Compare with 0.19.3](https://github.com/mkdocstrings/griffe/compare/0.19.3...0.20.0)</small>

### Features

- Add `as_json` and `from_json` convenience methods on objects ([5c3d751](https://github.com/mkdocstrings/griffe/commit/5c3d7511d2465e16805fa564c3d60d44618410d8) by Talley Lambert). [PR #74](https://github.com/mkdocstrings/griffe/pull/74)

### Bug Fixes

- Fix unparsing of f-strings ([9ca74bd](https://github.com/mkdocstrings/griffe/commit/9ca74bd144167de9506cf5b0725a784e52f5e67a) by Timothée Mazzucotelli). [Issue #80](https://github.com/mkdocstrings/griffe/issues/80)
- Don't crash when overwriting a submodule with a wildcard imported attribute ([bfad1cc](https://github.com/mkdocstrings/griffe/commit/bfad1ccf079e69fa0161754d9f1f7edd5819f943) by Timothée Mazzucotelli). [Issue #72](https://github.com/mkdocstrings/griffe/issues/72), [#79](https://github.com/mkdocstrings/griffe/issues/79), [mkdocstrings/mkdocstrings#438](https://github.com/mkdocstrings/mkdocstrings/issues/438)

## [0.19.3](https://github.com/mkdocstrings/griffe/releases/tag/0.19.3) - 2022-05-26

<small>[Compare with 0.19.2](https://github.com/mkdocstrings/griffe/compare/0.19.2...0.19.3)</small>

### Bug Fixes

- Support USub and UAdd nodes in annotations ([1169c51](https://github.com/mkdocstrings/griffe/commit/1169c51bd6ae04f491fa5e50cae93d99e8ce920d) by Timothée Mazzucotelli). [Issue #71](https://github.com/mkdocstrings/griffe/issues/71)

## [0.19.2](https://github.com/mkdocstrings/griffe/releases/tag/0.19.2) - 2022-05-18

<small>[Compare with 0.19.1](https://github.com/mkdocstrings/griffe/compare/0.19.1...0.19.2)</small>

### Bug Fixes

- Don't crash on single line docstrings with trailing whitespace (Google) ([8d9ccd5](https://github.com/mkdocstrings/griffe/commit/8d9ccd531dd91c6fbfa0922a0133680f881733b0) by Timothée Mazzucotelli).

## [0.19.1](https://github.com/mkdocstrings/griffe/releases/tag/0.19.1) - 2022-05-07

<small>[Compare with 0.19.0](https://github.com/mkdocstrings/griffe/compare/0.19.0...0.19.1)</small>

### Bug Fixes

- Don't crash on nested functions in `__init__` methods ([cd5af43](https://github.com/mkdocstrings/griffe/commit/cd5af43f3a98d54d822015818b7aa0ef15159286) by Timothée Mazzucotelli). [Issue #68](https://github.com/mkdocstrings/griffe/issues/68)

## [0.19.0](https://github.com/mkdocstrings/griffe/releases/tag/0.19.0) - 2022-05-06

<small>[Compare with 0.18.0](https://github.com/mkdocstrings/griffe/compare/0.18.0...0.19.0)</small>

### Features

- Add `load` shortcut function for convenience ([f38a42d](https://github.com/mkdocstrings/griffe/commit/f38a42ddd7ac9d58f36627d9f2a69f4acd65df50) by Timothée Mazzucotelli).
- Support loading (and merging) `*.pyi` files ([41518f4](https://github.com/mkdocstrings/griffe/commit/41518f4aa9e00756a910067cf6f01f07ca7327da) by Timothée Mazzucotelli). [Issue mkdocstrings/mkdocstrings#404](https://github.com/mkdocstrings/mkdocstrings/issues/404)
- Improve support for call nodes in annotations ([45e5bf5](https://github.com/mkdocstrings/griffe/commit/45e5bf53d509344b3f28118836d356903c64bbf3) by Timothée Mazzucotelli). [Issue #66](https://github.com/mkdocstrings/griffe/issues/66)
- Support `dataclass` decorators on classes ([f579431](https://github.com/mkdocstrings/griffe/commit/f579431474cc4db687e4264f5062074654dec2f3) by Timothée Mazzucotelli).

### Code Refactoring

- Handle absence of values ([190585d](https://github.com/mkdocstrings/griffe/commit/190585d3482bfc3a72694910529b7a0aac35444c) by Timothée Mazzucotelli).
- Simplify decorators to labels function ([04e768f](https://github.com/mkdocstrings/griffe/commit/04e768fb621898faf7a96cc7e7170f10da876664) by Timothée Mazzucotelli).
- Always sort labels when serializing ([bd2504b](https://github.com/mkdocstrings/griffe/commit/bd2504bdb43df3e290c88bd8d25903823f5fc2d6) by Timothée Mazzucotelli).

## [0.18.0](https://github.com/mkdocstrings/griffe/releases/tag/0.18.0) - 2022-04-19

<small>[Compare with 0.17.0](https://github.com/mkdocstrings/griffe/compare/0.17.0...0.18.0)</small>

### Features

- Add CLI option to disallow inspection ([8f71a07](https://github.com/mkdocstrings/griffe/commit/8f71a07c17de4cfb2b519dc2b4086f102de4d325) by Timothée Mazzucotelli).
- Support complex `__all__` assignments ([9a2128b](https://github.com/mkdocstrings/griffe/commit/9a2128b8d4533119b705ec47fc1eca404b4282ef) by Timothée Mazzucotelli). [Issue #40](https://github.com/mkdocstrings/griffe/issues/40)
- Inherit class parameters from `__init__` method ([e195593](https://github.com/mkdocstrings/griffe/commit/e195593b181690313c9e447c8bc2befa72fd6e09) by François Rozet). [Issue mkdocstrings/python#19](https://github.com/mkdocstrings/python/issues/19), [PR #65](https://github.com/mkdocstrings/python/pull/65).
  It allows to write "Parameters" sections in the docstring of the class itself.

### Performance Improvements

- Avoid using `__len__` as boolean method ([d465493](https://github.com/mkdocstrings/griffe/commit/d4654930577186fb6d3e89ea1561a2daf15b3a65) by Timothée Mazzucotelli).

### Bug Fixes

- Don't crash on unhandle `__all__` assignments ([cbc103c](https://github.com/mkdocstrings/griffe/commit/cbc103c91836db2e235a46a0f9048c1230de507d) by Timothée Mazzucotelli).
- Handle empty packages names in CLI ([52b51c4](https://github.com/mkdocstrings/griffe/commit/52b51c49a14783c986beb851abd33cbcd0ab8729) by Timothée Mazzucotelli).
- Don't crash on Google parameters sections found in non-function docstrings ([4a417bc](https://github.com/mkdocstrings/griffe/commit/4a417bc6c0e83b42fe1a74a4a8b0881d3955075f) by Timothée Mazzucotelli). [Issue mkdocstrings/python#19](https://github.com/mkdocstrings/python/issues/19)

### Code Refactoring

- Improve "unknown parameter" messages ([7191799](https://github.com/mkdocstrings/griffe/commit/7191799c92d7544f949c5870cf2867e02d406c57) by Timothée Mazzucotelli). [Issue mkdocstrings/mkdocstrings#423](https://github.com/mkdocstrings/mkdocstrings/issues/423)
- Set property label on `@cached_property`-decorated methods ([bc068f8](https://github.com/mkdocstrings/griffe/commit/bc068f8123c5bcbe4dce272dda52840019141b06) by Timothée Mazzucotelli).

## [0.17.0](https://github.com/mkdocstrings/griffe/releases/tag/0.17.0) - 2022-04-15

<small>[Compare with 0.16.0](https://github.com/mkdocstrings/griffe/compare/0.16.0...0.17.0)</small>

### Features

- Handle properties setters and deleters ([50a4490](https://github.com/mkdocstrings/griffe/commit/50a449069de89bb83da854b1bbd1681ec68f0395) by Timothée Mazzucotelli).
- Handle `typing.overload` decorator ([927bbd9](https://github.com/mkdocstrings/griffe/commit/927bbd9fe7712e8d0fc9763fb51d89bef3173350) by Timothée Mazzucotelli). [Issue mkdocstrings/mkdocstrings#308](https://github.com/mkdocstrings/mkdocstrings/issues/308)
- Set labels on functions using decorators ([1c1feb2](https://github.com/mkdocstrings/griffe/commit/1c1feb264c748f4a78ffebf3b9ea1966f2533522) by Timothée Mazzucotelli). [Issue #47](https://github.com/mkdocstrings/griffe/issues/47)
- Add `runtime` attribute to objects/aliases and handle type guarded objects ([2f2a04e](https://github.com/mkdocstrings/griffe/commit/2f2a04ea498aa50133b1404f3bc3498a25648545) by Timothée Mazzucotelli). [Issue #42](https://github.com/mkdocstrings/griffe/issues/42)
- Support pkg-style namespace packages ([efba0c6](https://github.com/mkdocstrings/griffe/commit/efba0c6a5e1dc185e96e5a09c05e94c751abc4cb) by Timothée Mazzucotelli). [Issue #58](https://github.com/mkdocstrings/griffe/issues/58)

### Code Refactoring

- Remove useless attribute ([c4a92b7](https://github.com/mkdocstrings/griffe/commit/c4a92b7e2cbe240a376d5d6944b7b0d23255648b) by Timothée Mazzucotelli).
- Improve Google warnings ([641089a](https://github.com/mkdocstrings/griffe/commit/641089aed53423894df8733941e404f7e6505b94) by Timothée Mazzucotelli).
- Remove useless import nodes generic visits ([f83fc8e](https://github.com/mkdocstrings/griffe/commit/f83fc8e629451abd4f4eadfe34b448fb3b77b9b6) by Timothée Mazzucotelli).

## [0.16.0](https://github.com/mkdocstrings/griffe/releases/tag/0.16.0) - 2022-04-09

<small>[Compare with 0.15.1](https://github.com/mkdocstrings/griffe/compare/0.15.1...0.16.0)</small>

### Features

- Warn about unknown parameters in Numpy docstrings ([23f63f2](https://github.com/mkdocstrings/griffe/commit/23f63f255eef5aa2dbaa1765f93634ecaf94dbb3) by Timothée Mazzucotelli).
- Warn about unknown parameters in Google docstrings ([72be993](https://github.com/mkdocstrings/griffe/commit/72be993c95460a6465a4e70a95b79ae4095db541) by Kevin Musgrave). [Issue mkdocstrings/mkdocstrings#408](https://github.com/mkdocstrings/mkdocstrings/issues/408), [PR #63](https://github.com/mkdocstrings/griffe/issues/63)

### Bug Fixes

- Don't crash on unhandled AST nodes while parsing text annotations ([f3be3a6](https://github.com/mkdocstrings/griffe/commit/f3be3a68141e24a9c0c6b9a87e3f22e75a168d80) by Timothée Mazzucotelli). [Issue mkdocstrings/mkdocstrings#416](https://github.com/mkdocstrings/mkdocstrings/issues/416)

## [0.15.1](https://github.com/mkdocstrings/griffe/releases/tag/0.15.1) - 2022-04-08

<small>[Compare with 0.15.0](https://github.com/mkdocstrings/griffe/compare/0.15.0...0.15.1)</small>

### Bug Fixes

- Don't overwrite existing (lower) members when expanding wildcards ([9ff86e3](https://github.com/mkdocstrings/griffe/commit/9ff86e369d8fb3a6eeb7d94cd60c87fa26bf74b4) by Timothée Mazzucotelli).
- Don't insert admonition before current section (Google parser) ([8d8a46f](https://github.com/mkdocstrings/griffe/commit/8d8a46fca7df917c4bba979128d94d3b79252ff5) by Timothée Mazzucotelli).
- Handle aliases chains in `has_docstrings` method ([77c6943](https://github.com/mkdocstrings/griffe/commit/77c69430ddc74fedaa33fa65afd59ac546900829) by Timothée Mazzucotelli).
- Actually check for docstrings recursively ([15f4193](https://github.com/mkdocstrings/griffe/commit/15f4193b764f85dcab042ab193e984bebf151029) by Timothée Mazzucotelli).

## [0.15.0](https://github.com/mkdocstrings/griffe/releases/tag/0.15.0) - 2022-04-03

<small>[Compare with 0.14.1](https://github.com/mkdocstrings/griffe/compare/0.14.1...0.15.0)</small>

### Features

- Support `ignore_init_summary` in Numpy parser ([f8cd147](https://github.com/mkdocstrings/griffe/commit/f8cd14734603d29e6e72c9a350f663dccdeb36b4) by Timothée Mazzucotelli). [Issue #44](https://github.com/mkdocstrings/griffe/issues/44)
- Enable cross-references for Numpy docstrings annotations ([e32a73c](https://github.com/mkdocstrings/griffe/commit/e32a73c9e100cf0778768c4a1f76152d9aecc451) by Timothée Mazzucotelli). Issues [#11](https://github.com/mkdocstrings/griffe/issues/11), [#12](https://github.com/mkdocstrings/griffe/issues/12), [#13](https://github.com/mkdocstrings/griffe/issues/13), [#14](https://github.com/mkdocstrings/griffe/issues/14), [#15](https://github.com/mkdocstrings/griffe/issues/15), [#16](https://github.com/mkdocstrings/griffe/issues/16), [#17](https://github.com/mkdocstrings/griffe/issues/17), [#18](https://github.com/mkdocstrings/griffe/issues/18)
- Retrieve annotations from parent in Numpy parser ([8d4eae3](https://github.com/mkdocstrings/griffe/commit/8d4eae353cbd42f47fe6f8101e6e1f8be4054c84) by Timothée Mazzucotelli). Issues [#29](https://github.com/mkdocstrings/griffe/issues/29), [#30](https://github.com/mkdocstrings/griffe/issues/30), [#31](https://github.com/mkdocstrings/griffe/issues/31), [#32](https://github.com/mkdocstrings/griffe/issues/32)
- Parse annotations in Iterator/Generator for Google docstrings ([f0129ef](https://github.com/mkdocstrings/griffe/commit/f0129efa2046089355ee62c48f23eb0189b054ce) by Timothée Mazzucotelli). [Issue #28](https://github.com/mkdocstrings/griffe/issues/28)

### Bug Fixes

- Fix missing "receives" entry in Google parser ([35d63fb](https://github.com/mkdocstrings/griffe/commit/35d63fbd566fa439a255c3f44ffeb4a9474db7f9) by Timothée Mazzucotelli).
- Fix serialization of Windows paths ([b7e8da8](https://github.com/mkdocstrings/griffe/commit/b7e8da868cd6ec8230f2d58a8f3c38248f7c97b2) by Timothée Mazzucotelli).

### Code Refactoring

- Be less strict on spacing around ":" in Numpy docstrings ([aa592b5](https://github.com/mkdocstrings/griffe/commit/aa592b5f38b71e6eadd883257d2239fceec43752) by Timothée Mazzucotelli).
- Be less strict in Numpy regular expressions ([603dc0e](https://github.com/mkdocstrings/griffe/commit/603dc0e21aa12754ec4f76ffc40869bf8519935d) by Timothée Mazzucotelli).
- Rename variables in Numpy module ([4407244](https://github.com/mkdocstrings/griffe/commit/4407244a2e4b59c988c61e4c7b9f07532cad5b3c) by Timothée Mazzucotelli).

## [0.14.1](https://github.com/mkdocstrings/griffe/releases/tag/0.14.1) - 2022-04-01

<small>[Compare with 0.14.0](https://github.com/mkdocstrings/griffe/compare/0.14.0...0.14.1)</small>

### Bug Fixes

- Retrieve default value for non-string parameters ([15952ed](https://github.com/mkdocstrings/griffe/commit/15952ed72f6f5db3a4dec2fc60cb256c838be6a3) by ThomasPJ). [Issue #59](https://github.com/mkdocstrings/griffe/issues/59), [issue mkdocstrings/python#8](https://github.com/mkdocstrings/python/issues/8), [PR #60](https://github.com/mkdocstrings/griffe/pull/60)
- Prevent infinite recursion while expanding wildcards ([428628f](https://github.com/mkdocstrings/griffe/commit/428628f423192611529b9b346cd295999d0dad25) by Timothée Mazzucotelli). [Issue #57](https://github.com/mkdocstrings/griffe/issues/57)

## [0.14.0](https://github.com/mkdocstrings/griffe/releases/tag/0.14.0) - 2022-03-06

<small>[Compare with 0.13.2](https://github.com/mkdocstrings/griffe/compare/0.13.2...0.14.0)</small>

### Features

- Ignore `__doc__` from parent classes ([10aa59e](https://github.com/mkdocstrings/griffe/commit/10aa59ef2fbf1db2c8829e0905bea88406495c41) by Will Da Silva). [Issue #55](https://github.com/mkdocstrings/griffe/issues/55), [PR #56](https://github.com/mkdocstrings/griffe/pull/56)

## [0.13.2](https://github.com/mkdocstrings/griffe/releases/tag/0.13.2) - 2022-03-01

<small>[Compare with 0.13.1](https://github.com/mkdocstrings/griffe/compare/0.13.1...0.13.2)</small>

### Bug Fixes

- Fix type regex in Numpy parser ([3a10fda](https://github.com/mkdocstrings/griffe/commit/3a10fda89c2e32e2d8acd89eb1ce8ab20a0fc251) by Timothée Mazzucotelli).
- Current module must not be available in its members' scope ([54f9688](https://github.com/mkdocstrings/griffe/commit/54f9688c11a1f7d3893ca774a07afe876f0b809c) by Timothée Mazzucotelli).
- Allow named sections after numpydoc examples ([a44d9c6](https://github.com/mkdocstrings/griffe/commit/a44d9c65cf24d2820e805d23365f38aab82c8c07) by Lucina). [PR #54](https://github.com/mkdocstrings/griffe/pull/54)

## [0.13.1](https://github.com/mkdocstrings/griffe/releases/tag/0.13.1) - 2022-02-24

<small>[Compare with 0.13.0](https://github.com/mkdocstrings/griffe/compare/0.13.0...0.13.1)</small>

### Bug Fixes

- Don't cut through wildcard-expanded aliases chains ([65dafa4](https://github.com/mkdocstrings/griffe/commit/65dafa4660e8c95687cad4d5c5145a56f126ae61) by Timothée Mazzucotelli).
- Fix docstrings warnings when there's no parent module ([e080549](https://github.com/mkdocstrings/griffe/commit/e080549e3eaf887a0f037a4457329eab35bd6409) by Timothée Mazzucotelli). [Issue #51](https://github.com/mkdocstrings/griffe/issues/51)

### Code Refactoring

- Use proper classes for docstrings sections ([46eddac](https://github.com/mkdocstrings/griffe/commit/46eddac0b847eeb75e4964a3186069f7698235b0) by Timothée Mazzucotelli). [Issue mkdocstrings/python#3](https://github.com/mkdocstrings/python/issues/3), [PR #52](https://github.com/mkdocstrings/griffe/pull/52)

## [0.13.0](https://github.com/mkdocstrings/griffe/releases/tag/0.13.0) - 2022-02-23

<small>[Compare with 0.12.6](https://github.com/mkdocstrings/griffe/compare/0.12.6...0.13.0)</small>

### Features

- Implement `trim_doctest_flags` for Google and Numpy ([8057153](https://github.com/mkdocstrings/griffe/commit/8057153823711d8f486b1c52469090ce404771cb) by Jeremy Goh). [Issue mkdocstrings/mkdocstrings#386](https://github.com/mkdocstrings/mkdocstrings/issues/386), [PR #48](https://github.com/mkdocstrings/griffe/pull/48)

### Bug Fixes

- Rename keyword parameters to keyword arguments ([ce3eb6b](https://github.com/mkdocstrings/griffe/commit/ce3eb6b5d7caad6df41496dd300924535d92dc7f) by Jeremy Goh).

## [0.12.6](https://github.com/mkdocstrings/griffe/releases/tag/0.12.6) - 2022-02-18

<small>[Compare with 0.12.5](https://github.com/mkdocstrings/griffe/compare/0.12.5...0.12.6)</small>

### Bug Fixes

- Support starred parameters in Numpy docstrings ([27f0fc2](https://github.com/mkdocstrings/griffe/commit/27f0fc21299a41a3afc07b46afbe8f37757c3918) by Timothée Mazzucotelli). [Issue #43](https://github.com/mkdocstrings/griffe/issues/43)

## [0.12.5](https://github.com/mkdocstrings/griffe/releases/tag/0.12.5) - 2022-02-17

<small>[Compare with 0.12.4](https://github.com/mkdocstrings/griffe/compare/0.12.4...0.12.5)</small>

### Bug Fixes

- Fix getting line numbers on aliases ([351750e](https://github.com/mkdocstrings/griffe/commit/351750ea70d0ab3f10c2766846c10d00612cda1d) by Timothée Mazzucotelli).

## [0.12.4](https://github.com/mkdocstrings/griffe/releases/tag/0.12.4) - 2022-02-16

<small>[Compare with 0.12.3](https://github.com/mkdocstrings/griffe/compare/0.12.3...0.12.4)</small>

### Bug Fixes

- Update target path when changing alias target ([5eda646](https://github.com/mkdocstrings/griffe/commit/5eda646f7bc2fdb112887fdeaa07f8a2f4635c12) by Timothée Mazzucotelli).
- Fix relative imports to absolute with wildcards ([69500dd](https://github.com/mkdocstrings/griffe/commit/69500dd0ce06f4acc91eb60ff20ac8d79303a281) by Timothée Mazzucotelli). [Issue mkdocstrings/mkdocstrings#382](https://github.com/mkdocstrings/mkdocstrings/issues/382)
- Fix accessing members using tuples ([87ff1df](https://github.com/mkdocstrings/griffe/commit/87ff1dfae93d9eb6f735f9c1290092d61cac7591) by Timothée Mazzucotelli).
- Fix recursive wildcard expansion ([60e6edf](https://github.com/mkdocstrings/griffe/commit/60e6edf9dcade104b069946380a0d1dcc22bce9a) by Timothée Mazzucotelli). [Issue mkdocstrings/mkdocstrings#382](https://github.com/mkdocstrings/mkdocstrings/issues/382)
- Only export submodules if they were imported ([98c72db](https://github.com/mkdocstrings/griffe/commit/98c72dbab114fd7782efd6f2f9bbf78e3f4ccb27) by Timothée Mazzucotelli). [Issue mkdocstrings/mkdocstrings#382](https://github.com/mkdocstrings/mkdocstrings/issues/382)

## [0.12.3](https://github.com/mkdocstrings/griffe/releases/tag/0.12.3) - 2022-02-15

<small>[Compare with 0.12.2](https://github.com/mkdocstrings/griffe/compare/0.12.2...0.12.3)</small>

### Bug Fixes

- Always decode source as UTF8 ([563469b](https://github.com/mkdocstrings/griffe/commit/563469b4cf320ea38096846312dc757a614d8094) by Timothée Mazzucotelli).
- Fix JSON encoder and decoder ([3e768d6](https://github.com/mkdocstrings/griffe/commit/3e768d6574a45624237e0897c1d6a6c87e446016) by Timothée Mazzucotelli).

### Code Refactoring

- Improve error handling ([7b15a51](https://github.com/mkdocstrings/griffe/commit/7b15a51fb9dd4722757f272f00402ce29ef2bd3f) by Timothée Mazzucotelli).

## [0.12.2](https://github.com/mkdocstrings/griffe/releases/tag/0.12.2) - 2022-02-13

<small>[Compare with 0.12.1](https://github.com/mkdocstrings/griffe/compare/0.12.1...0.12.2)</small>

### Bug Fixes

- Fix JSON unable to serialize docstring kind values ([91e6719](https://github.com/mkdocstrings/griffe/commit/91e67190fc4f69911ad6ea3eb239a74fc1f15ba6) by Timothée Mazzucotelli).

### Code Refactoring

- Make attribute labels more explicit ([19eac2e](https://github.com/mkdocstrings/griffe/commit/19eac2e5a13d77175849c199ba3337a66e3824a2) by Timothée Mazzucotelli).

## [0.12.1](https://github.com/mkdocstrings/griffe/releases/tag/0.12.1) - 2022-02-12

<small>[Compare with 0.11.7](https://github.com/mkdocstrings/griffe/compare/0.11.7...0.12.1)</small>

### Features

- Add `ignore_init_summary` option to the Google parser ([81f0333](https://github.com/mkdocstrings/griffe/commit/81f0333b1691955f6020095051b2cf869f0c2c24) by Timothée Mazzucotelli).
- Add `is_KIND` properties on objects ([17a08cd](https://github.com/mkdocstrings/griffe/commit/17a08cd7142bdee041577735d5e5ac246c181ec9) by Timothée Mazzucotelli).

## [0.11.7](https://github.com/mkdocstrings/griffe/releases/tag/0.11.7) - 2022-02-12

<small>[Compare with 0.11.6](https://github.com/mkdocstrings/griffe/compare/0.11.6...0.11.7)</small>

### Bug Fixes

- Keep only first assignment in conditions ([0104440](https://github.com/mkdocstrings/griffe/commit/010444018ca6ba437e70166e0da3e2d2ca6bbbe8) by Timothée Mazzucotelli).
- Support invert unary op in annotations ([734ef55](https://github.com/mkdocstrings/griffe/commit/734ef551f5c5b2b4b48de32033d4c2e7cff0a124) by Timothée Mazzucotelli).
- Fix handling of missing modules during dynamic imports ([7a3b383](https://github.com/mkdocstrings/griffe/commit/7a3b38349712c5b66792da1a8a9efae1b6f663a7) by Timothée Mazzucotelli). [Issue mkdocstrings/mkdocstrings#380](https://github.com/mkdocstrings/mkdocstrings/issues/380)
- Fix getting lines of compiled modules ([899461b](https://github.com/mkdocstrings/griffe/commit/899461b2f48622f334ceeaa6d73c935bacb540ea) by Timothée Mazzucotelli).

### Code Refactoring

- Get annotation with the same property on functions ([ecc7bba](https://github.com/mkdocstrings/griffe/commit/ecc7bba8880f90417a21830e0e9cccf30f582399) by Timothée Mazzucotelli).

## [0.11.6](https://github.com/mkdocstrings/griffe/releases/tag/0.11.6) - 2022-02-10

<small>[Compare with 0.11.5](https://github.com/mkdocstrings/griffe/compare/0.11.5...0.11.6)</small>

### Bug Fixes

- Fix infinite loop in Google parser ([8b7b97b](https://github.com/mkdocstrings/griffe/commit/8b7b97b6f507dc91b957592e1d247d79bd3e9a5b) by Timothée Mazzucotelli). [Issue #38](https://github.com/mkdocstrings/griffe/issues/38)

## [0.11.5](https://github.com/mkdocstrings/griffe/releases/tag/0.11.5) - 2022-02-08

<small>[Compare with 0.11.4](https://github.com/mkdocstrings/griffe/compare/0.11.4...0.11.5)</small>

### Bug Fixes

- Fix building title and kind of Google admonitions ([87ab56c](https://github.com/mkdocstrings/griffe/commit/87ab56cfe5458b313527bc2eb47ea418fcb231ab) by Timothée Mazzucotelli). [Issue mkdocstrings#379](https://github.com/mkdocstrings/mkdocstrings/issues/379)

## [0.11.4](https://github.com/mkdocstrings/griffe/releases/tag/0.11.4) - 2022-02-07

<small>[Compare with 0.11.3](https://github.com/mkdocstrings/griffe/compare/0.11.3...0.11.4)</small>

### Bug Fixes

- Don't trigger alias resolution while checking docstrings presence ([dda72ea](https://github.com/mkdocstrings/griffe/commit/dda72ea56b091d1c9bc1b7aa369548328894da29) by Timothée Mazzucotelli). [Issue #37](https://github.com/mkdocstrings/griffe/issues/37)

## [0.11.3](https://github.com/mkdocstrings/griffe/releases/tag/0.11.3) - 2022-02-05

<small>[Compare with 0.11.2](https://github.com/mkdocstrings/griffe/compare/0.11.2...0.11.3)</small>

### Bug Fixes

- Fix getting params defaults on Python 3.7 ([0afd867](https://github.com/mkdocstrings/griffe/commit/0afd8675d2d24302d68619f31adbe5ac5d8ff5a7) by Timothée Mazzucotelli).

## [0.11.2](https://github.com/mkdocstrings/griffe/releases/tag/0.11.2) - 2022-02-03

<small>[Compare with 0.11.1](https://github.com/mkdocstrings/griffe/compare/0.11.1...0.11.2)</small>

### Code Refactoring

- Factorize docstring annotation parser ([19609be](https://github.com/mkdocstrings/griffe/commit/19609bede6227998a1322dbed6fcc1ae2e924bc8) by Timothée Mazzucotelli).

## [0.11.1](https://github.com/mkdocstrings/griffe/releases/tag/0.11.1) - 2022-02-01

<small>[Compare with 0.11.0](https://github.com/mkdocstrings/griffe/compare/0.11.0...0.11.1)</small>

### Code Refactoring

- Rename RST parser to Sphinx ([a612cb1](https://github.com/mkdocstrings/griffe/commit/a612cb1c8d52fabe5a1ebaf892e9b82c67d15a30) by Timothée Mazzucotelli).

## [0.11.0](https://github.com/mkdocstrings/griffe/releases/tag/0.11.0) - 2022-01-31

<small>[Compare with 0.10.0](https://github.com/mkdocstrings/griffe/compare/0.10.0...0.11.0)</small>

### Features

- Support matrix multiplication operator in visitor ([6129e17](https://github.com/mkdocstrings/griffe/commit/6129e17c86ff49a8e539039dcd04a58b30e3648e) by Timothée Mazzucotelli).

### Bug Fixes

- Fix name resolution for inspected data ([ed3e7e5](https://github.com/mkdocstrings/griffe/commit/ed3e7e5fa8a9d702c92f47e8244635cf11a923f2) by Timothée Mazzucotelli).
- Make importer actually able to import any nested object ([d007219](https://github.com/mkdocstrings/griffe/commit/d00721971c7b820e16e463408f04cc3e81a14db6) by Timothée Mazzucotelli).

### Code Refactoring

- Always use search paths to import modules ([a9a378f](https://github.com/mkdocstrings/griffe/commit/a9a378fc6e47678e08a22383879e4d01acd16b54) by Timothée Mazzucotelli).
- Split out module finder ([7290642](https://github.com/mkdocstrings/griffe/commit/7290642e36341e64b8ed770e237e9f232e05eada) by Timothée Mazzucotelli).

## [0.10.0](https://github.com/mkdocstrings/griffe/releases/tag/0.10.0) - 2022-01-14

<small>[Compare with 0.9.0](https://github.com/mkdocstrings/griffe/compare/0.9.0...0.10.0)</small>

### Bug Fixes

- Fix infinite recursion errors in alias resolver ([133b4e4](https://github.com/mkdocstrings/griffe/commit/133b4e4bf721fc7536a1ca957f13f7c9f83bf07a) by Timothée Mazzucotelli).
- Fix inspection of nodes children (aliases or not) ([bb354f2](https://github.com/mkdocstrings/griffe/commit/bb354f21e7b079f4c1e8dd50297d53810c18450e) by Timothée Mazzucotelli).
- Fix relative to absolute import conversion ([464c39e](https://github.com/mkdocstrings/griffe/commit/464c39eaa812a927190469b18bd910e95e3c1d3c) by Timothée Mazzucotelli).

### Code Refactoring

- Rename some CLI options ([1323268](https://github.com/mkdocstrings/griffe/commit/13232685b0f2752d92428ab786d428d0af11743b) by Timothée Mazzucotelli).
- Return the loader the to main function ([9c6317e](https://github.com/mkdocstrings/griffe/commit/9c6317e5afa25dd11d18906503b8010046878868) by Timothée Mazzucotelli).
- Improve logging messages ([b8eb16e](https://github.com/mkdocstrings/griffe/commit/b8eb16e0fedfe50f2c3ad65e326f4dc6e6918ac0) by Timothée Mazzucotelli).
- Skip inspection of some debug packages ([4ee8968](https://github.com/mkdocstrings/griffe/commit/4ee896864f1227e32d40571da03f7894c9404579) by Timothée Mazzucotelli).
- Return ... instead of Ellipsis ([f9ae31d](https://github.com/mkdocstrings/griffe/commit/f9ae31d0f4c904a89c7f581aaa031692740edaef) by Timothée Mazzucotelli).
- Catch attribute errors when cross-referencing docstring annotations ([288803a](https://github.com/mkdocstrings/griffe/commit/288803a3be93c4e077576ed36dded2a76ce33955) by Timothée Mazzucotelli).
- Support dict methods in lines collection ([1b0cb94](https://github.com/mkdocstrings/griffe/commit/1b0cb945dba619df7ce1358f7961e4bd80f70218) by Timothée Mazzucotelli).

### Features

- Compute and show some stats ([1b8d0a1](https://github.com/mkdocstrings/griffe/commit/1b8d0a1c91e03dfa5f92ad9c6dff02863a43fc01) by Timothée Mazzucotelli).
- Add CLI options for alias resolution ([87a59cb](https://github.com/mkdocstrings/griffe/commit/87a59cb7af5f8e7df9ddba41fb4a4b65cb264481) by Timothée Mazzucotelli).
- Support Google raises annotations cross-refs ([8006ae1](https://github.com/mkdocstrings/griffe/commit/8006ae13bc27d117ce6b8fdc8ac91dc8541a670f) by Timothée Mazzucotelli).

## [0.9.0](https://github.com/mkdocstrings/griffe/releases/tag/0.9.0) - 2022-01-04

<small>[Compare with 0.8.0](https://github.com/mkdocstrings/griffe/compare/0.8.0...0.9.0)</small>

### Features

- Loader option to only follow aliases in known modules ([879d91b](https://github.com/mkdocstrings/griffe/commit/879d91b4c50832620ce6ee7bdcc85107a6df9a1f) by Timothée Mazzucotelli).
- Use aliases when inspecting too ([60439ee](https://github.com/mkdocstrings/griffe/commit/60439eefb4635e58e4bd898e5565eab48a5c91d0) by Timothée Mazzucotelli).

### Bug Fixes

- Handle more errors when loading modules ([1aa571a](https://github.com/mkdocstrings/griffe/commit/1aa571a112e3b2ca955c23f2eef97b36f34bcd8c) by Timothée Mazzucotelli).
- Handle more errors when getting signature ([2db85e7](https://github.com/mkdocstrings/griffe/commit/2db85e7f655c1e383ba310f40195844c2867e1b9) by Timothée Mazzucotelli).
- Fix checking parent truthfulness ([6129e50](https://github.com/mkdocstrings/griffe/commit/6129e50331f6e36bcbee2e07b871abee45f7e872) by Timothée Mazzucotelli).
- Fix getting subscript value ([1699f12](https://github.com/mkdocstrings/griffe/commit/1699f121adc13fcc48f81f46dfca85946e2fb74f) by Timothée Mazzucotelli).
- Support yield nodes ([7d536d5](https://github.com/mkdocstrings/griffe/commit/7d536d58ffc0faa4caf43f09194d88c35fc47704) by Timothée Mazzucotelli).
- Exclude some special low-level members that cause cyclic issues ([b54ab34](https://github.com/mkdocstrings/griffe/commit/b54ab346308bb24cba66be9c8f1ee8599481381d) by Timothée Mazzucotelli).
- Fix transforming elements of signatures to annotations ([e278c11](https://github.com/mkdocstrings/griffe/commit/e278c1102b2762b74bf6b83a2e97a5f87b566e2e) by Timothée Mazzucotelli).
- Detect cyclic aliases and prevent resolution errors ([de5dd12](https://github.com/mkdocstrings/griffe/commit/de5dd12240acf8a203a86b04e458ce33b67ced9e) by Timothée Mazzucotelli).
- Don't crash while trying to get the representation of an attribute value ([77ac55d](https://github.com/mkdocstrings/griffe/commit/77ac55d5033e83790c79f3303fdbd05ea66ab729) by Timothée Mazzucotelli).
- Fix building value for joined strings ([6154b69](https://github.com/mkdocstrings/griffe/commit/6154b69b6da5d63c508ec5095aebe487e491b553) by Timothée Mazzucotelli).
- Fix prevention of cycles while building objects nodes ([48062ac](https://github.com/mkdocstrings/griffe/commit/48062ac1f8356099b8e0e1069e4321a467073d33) by Timothée Mazzucotelli).
- Better handle relative imports ([91b42de](https://github.com/mkdocstrings/griffe/commit/91b42dea73c035b2dc20db1e328a53960c51a645) by Timothée Mazzucotelli).
- Fix Google parser missing lines ending with colon ([2f7969c](https://github.com/mkdocstrings/griffe/commit/2f7969ccbf91b63ae22deb742250068c114fe1a9) by Timothée Mazzucotelli).

### Code Refactoring

- Improve alias resolution robustness ([e708139](https://github.com/mkdocstrings/griffe/commit/e708139c9bd19be320bdb279310560212872326f) by Timothée Mazzucotelli).
- Remove async loader for now ([acc5ecf](https://github.com/mkdocstrings/griffe/commit/acc5ecf2bb45dcebdd56d763a657a1075c4a3002) by Timothée Mazzucotelli).
- Improve handling of Google admonitions ([8aa5ed0](https://github.com/mkdocstrings/griffe/commit/8aa5ed0be4f1902dbdfbce9b4a9c7ac619418d43) by Timothée Mazzucotelli).
- Better handling of import errors and system exits while inspecting modules ([7ba1589](https://github.com/mkdocstrings/griffe/commit/7ba1589552fb37fba3c2f3093058e135a6e48a27) by Timothée Mazzucotelli).
- Empty generic visit/inspect methods in base classes ([338760e](https://github.com/mkdocstrings/griffe/commit/338760ea2189e74577250b8c3f4ffe91f81e6b6e) by Timothée Mazzucotelli).

## [0.8.0](https://github.com/mkdocstrings/griffe/releases/tag/0.8.0) - 2022-01-02

<small>[Compare with 0.7.1](https://github.com/mkdocstrings/griffe/compare/0.7.1...0.8.0)</small>

### Features

- Support getting attribute annotation from parent in RST docstring parser ([25db61a](https://github.com/mkdocstrings/griffe/commit/25db61ab01042ad797ac5cdea0b2f7e2382191c1) by Timothée Mazzucotelli).
- Handle relative imports ([62b0927](https://github.com/mkdocstrings/griffe/commit/62b0927516ca345de61aa3cc03e977d4d37220de) by Timothée Mazzucotelli).
- Support wildcard imports ([77a3cb7](https://github.com/mkdocstrings/griffe/commit/77a3cb7e4198dc2e2cea953c5f621544b564552c) by Timothée Mazzucotelli).
- Support configuring log level (CLI/env var) ([839d78e](https://github.com/mkdocstrings/griffe/commit/839d78ea302df004fba1b6fad9eb84d861f0f4aa) by Timothée Mazzucotelli).
- Support loading `*.py[cod]` and `*.so` modules ([cd98a6f](https://github.com/mkdocstrings/griffe/commit/cd98a6f3afbbf8f6a176aa7780a8b916a9ee64f2) by Timothée Mazzucotelli).
- Support inspecting builtin functions/methods ([aa1fce3](https://github.com/mkdocstrings/griffe/commit/aa1fce330ce3e2af4dd9a3c43827637d1e220dde) by Timothée Mazzucotelli).

### Code Refactoring

- Handle extensions errors ([11278ca](https://github.com/mkdocstrings/griffe/commit/11278caea27e9f91a1dc9cc160414f01b24f5354) by Timothée Mazzucotelli).
- Don't always try to find a module as a relative  path ([e6df277](https://github.com/mkdocstrings/griffe/commit/e6df2774bfd631fd9a09913480b4d61d137bc0c6) by Timothée Mazzucotelli).
- Improve loggers patching ([f4b262a](https://github.com/mkdocstrings/griffe/commit/f4b262ab5a3d874591324adc2b5ffff214c7e7da) by Timothée Mazzucotelli).
- Improve dynamic imports ([2998195](https://github.com/mkdocstrings/griffe/commit/299819519b7eb9b07b938d22bfb3a27e3b05095d) by Timothée Mazzucotelli).

## [0.7.1](https://github.com/mkdocstrings/griffe/releases/tag/0.7.1) - 2021-12-28

<small>[Compare with 0.7.0](https://github.com/mkdocstrings/griffe/compare/0.7.0...0.7.1)</small>

### Code Refactoring

- Only log warning if async mode is used ([356e848](https://github.com/mkdocstrings/griffe/commit/356e848c8e233334401461b02a0188731b71a8cf) by Timothée Mazzucotelli).

## [0.7.0](https://github.com/mkdocstrings/griffe/releases/tag/0.7.0) - 2021-12-28

<small>[Compare with 0.6.0](https://github.com/mkdocstrings/griffe/compare/0.6.0...0.7.0)</small>

### Features

- Support more nodes on Python 3.7 ([7f2c4ec](https://github.com/mkdocstrings/griffe/commit/7f2c4ec3bf610ade7305e19ab220a4b447bed41d) by Timothée Mazzucotelli).

### Code Refactoring

- Don't crash on syntax errors and log an error ([10bb6b1](https://github.com/mkdocstrings/griffe/commit/10bb6b15bb9b132626c525b81f3ee33c3bb5746f) by Timothée Mazzucotelli).

## [0.6.0](https://github.com/mkdocstrings/griffe/releases/tag/0.6.0) - 2021-12-27

<small>[Compare with 0.5.0](https://github.com/mkdocstrings/griffe/compare/0.5.0...0.6.0)</small>

### Features

- Support more AST nodes ([cd1b305](https://github.com/mkdocstrings/griffe/commit/cd1b305932832ad5347ce829a48a311e3c44d542) by Timothée Mazzucotelli).

### Code Refactoring

- Use annotation getter for base classes ([8b1a7ed](https://github.com/mkdocstrings/griffe/commit/8b1a7edc11a72f679689fa9ba9e632907f9304f8) by Timothée Mazzucotelli).

## [0.5.0](https://github.com/mkdocstrings/griffe/releases/tag/0.5.0) - 2021-12-20

<small>[Compare with 0.4.0](https://github.com/mkdocstrings/griffe/compare/0.4.0...0.5.0)</small>

### Features

- Add support for Python 3.7 ([4535adc](https://github.com/mkdocstrings/griffe/commit/4535adce19edbe7e9cde90f3b1075a8245a6ebc8) by Timothée Mazzucotelli).

### Bug Fixes

- Don't propagate aliases of an alias ([8af48f8](https://github.com/mkdocstrings/griffe/commit/8af48f87e2e6bb0f2cf1531fa10287a069f67289) by Timothée Mazzucotelli).
- Don't reassign members defined in except clauses ([d918b4e](https://github.com/mkdocstrings/griffe/commit/d918b4efcedcedbec6db214ade8cde921d7e97b2) by Timothée Mazzucotelli).

## [0.4.0](https://github.com/mkdocstrings/griffe/releases/tag/0.4.0) - 2021-11-28

<small>[Compare with 0.3.0](https://github.com/mkdocstrings/griffe/compare/0.3.0...0.4.0)</small>

### Features

- Add a prototype 'hybrid' extension ([8cb3c16](https://github.com/mkdocstrings/griffe/commit/8cb3c1661223378a2511fd42a0693d0fbfe924d8) by Timothée Mazzucotelli).
- Allow passing extensions config as JSON on the CLI ([9a7fa8b](https://github.com/mkdocstrings/griffe/commit/9a7fa8bd88752ca1a074179db3a4c7fc41b68028) by Timothée Mazzucotelli).
- Support names for returns, yields and receives sections items ([1c5a4c9](https://github.com/mkdocstrings/griffe/commit/1c5a4c95738615ea9bb6a816c61d078e6133100a) by Timothée Mazzucotelli).
- Store aliases on each object ([91ba643](https://github.com/mkdocstrings/griffe/commit/91ba643b3e8e9a8f56f3280f699a18b1e654ccd7) by Timothée Mazzucotelli).
- Support inspection/introspection ([3a0587d](https://github.com/mkdocstrings/griffe/commit/3a0587dbf26f288722c7d27e781d0887c5cdf641) by Timothée Mazzucotelli).
- Support multiple return, yield and receive items ([0fc70cb](https://github.com/mkdocstrings/griffe/commit/0fc70cbcc07c63ecf1026e4bef30bd0ff3f73958) by Timothée Mazzucotelli).
- Support namespace packages ([2414c8e](https://github.com/mkdocstrings/griffe/commit/2414c8e24b7ba7ee986d95b301662fd06ef350fe) by Timothée Mazzucotelli).

### Bug Fixes

- Fix extensions loader ([78fb70b](https://github.com/mkdocstrings/griffe/commit/78fb70b77076b68fa30592caa5e92a91f0ce2caa) by Timothée Mazzucotelli).
- Avoid visiting/inspecting multiple times ([75a8a8b](https://github.com/mkdocstrings/griffe/commit/75a8a8b7145e1872cbecf93f8e33749b51b5b77b) by Timothée Mazzucotelli).
- Set modules collection attribute earlier ([592c0bd](https://github.com/mkdocstrings/griffe/commit/592c0bde6b6959615bc56030758098c8e45119a2) by Timothée Mazzucotelli).
- Support inequality nodes ([b0ed247](https://github.com/mkdocstrings/griffe/commit/b0ed247c9fe42a324a4e8e4a972676afbaa26976) by Timothée Mazzucotelli).
- Handle Div nodes for values ([272e4d6](https://github.com/mkdocstrings/griffe/commit/272e4d64b5ca557732af903d35aefbe405bd3ac0) by Timothée Mazzucotelli).

### Code Refactoring

- Set log level to INFO ([718e73e](https://github.com/mkdocstrings/griffe/commit/718e73ebb6767c0b10c03482d6f92cf135778ec7) by Timothée Mazzucotelli).
- Add target setter ([7f0064c](https://github.com/mkdocstrings/griffe/commit/7f0064c154459b4f4da7fc25bc49f8dd1e4fd2c0) by Timothée Mazzucotelli).
- Reorganize conditions ([15ab876](https://github.com/mkdocstrings/griffe/commit/15ab8763acc92d9160b847dc878f8bdad7f0b705) by Timothée Mazzucotelli).
- Avoid recursion loops ([ea6acec](https://github.com/mkdocstrings/griffe/commit/ea6acec10c0a805a9ae4e03ae0b92fb2a54cf79b) by Timothée Mazzucotelli).
- Update aliases when replacing a member ([99a0f8b](https://github.com/mkdocstrings/griffe/commit/99a0f8b9a425251ddcde853f2ad9ee95504b2127) by Timothée Mazzucotelli).
- Reorganize code ([31fcdb1](https://github.com/mkdocstrings/griffe/commit/31fcdb1cbe0eceedc59cc7c1c692dc4ef210ef53) by Timothée Mazzucotelli).
- Replace DocstringException with DocstringRaise ([d5ed87a](https://github.com/mkdocstrings/griffe/commit/d5ed87a478411aeb8248e948dbb6c228b80f5fbe) by Timothée Mazzucotelli).
- Refactor loaders ([d9b94bb](https://github.com/mkdocstrings/griffe/commit/d9b94bbcb55c29268ab1e077420e2b0d5297638c) by Timothée Mazzucotelli).
- Improve typing ([e08bcfa](https://github.com/mkdocstrings/griffe/commit/e08bcfac68aa22dc4bc58914b3340c1743f87ee7) by Timothée Mazzucotelli).

## [0.3.0](https://github.com/mkdocstrings/griffe/releases/tag/0.3.0) - 2021-11-21

<small>[Compare with 0.2.0](https://github.com/mkdocstrings/griffe/compare/0.2.0...0.3.0)</small>

### Features

- Handle aliases and their resolution ([67ae903](https://github.com/mkdocstrings/griffe/commit/67ae9034ac25061bc7d5c6def63715209643ca20) by Timothée Mazzucotelli).
- Resolve annotations in docstrings ([847384a](https://github.com/mkdocstrings/griffe/commit/847384a322017ca94bd40d4342eb4b8b42858f91) by Timothée Mazzucotelli).
- Resolve annotations ([6451eff](https://github.com/mkdocstrings/griffe/commit/6451effa01aa09cd3db1584fe111152de649e525) by Timothée Mazzucotelli).
- Add lines property to objects ([7daf7db](https://github.com/mkdocstrings/griffe/commit/7daf7db9ae58fb13985d1adacbde5d0bec2a35e4) by Timothée Mazzucotelli).
- Allow setting docstring parser and options on each object ([07a1d2e](https://github.com/mkdocstrings/griffe/commit/07a1d2e83c12bfa0f7b0dd35149b5cc0d0f600d6) by Timothée Mazzucotelli).
- Get attributes annotations from parent ([003b990](https://github.com/mkdocstrings/griffe/commit/003b99020f45b350d29329690d18f6c6cb3821f9) by Timothée Mazzucotelli).
- Draft extensions loader ([17ccd03](https://github.com/mkdocstrings/griffe/commit/17ccd03cadc5cbb230071e78beab96a0b97456a1) by Timothée Mazzucotelli).
- Add properties to objects ([0ec301a](https://github.com/mkdocstrings/griffe/commit/0ec301a5e97bee6556b62cb6ee35af9976f8410b) by Timothée Mazzucotelli).
- Handle .pth files when searching modules ([2a2e182](https://github.com/mkdocstrings/griffe/commit/2a2e1826fe0235c5bd47b5d6b1b64a30a81a3f4b) by Timothée Mazzucotelli).
- Add `default` property to docstring parameters ([6298ba3](https://github.com/mkdocstrings/griffe/commit/6298ba34d4e769568e519e21549137df3649e01b) by Timothée Mazzucotelli).
- Accept RST and Numpy parsers ([1cf147d](https://github.com/mkdocstrings/griffe/commit/1cf147d8df0491104efd084ce3308da77fc2c817) by Timothée Mazzucotelli).
- Support data (attributes/variables) ([dce84d1](https://github.com/mkdocstrings/griffe/commit/dce84d106cf067f11305f804a24cfd7d5643d902) by Timothée Mazzucotelli).
- Add Numpy-style parser ([ad5b72d](https://github.com/mkdocstrings/griffe/commit/ad5b72d174433764e85f937ea1096c0f458532f8) by Timothée Mazzucotelli).
- Support more section kinds in Google-style ([9d3d047](https://github.com/mkdocstrings/griffe/commit/9d3d0472d0bb55352b371de3da0816419fcf59e0) by Timothée Mazzucotelli).
- Add docstring section kinds ([b270483](https://github.com/mkdocstrings/griffe/commit/b2704833bc74131269306b9947ea2b46edafd349) by Timothée Mazzucotelli).
- Accept initial arguments when creating container ([90c5956](https://github.com/mkdocstrings/griffe/commit/90c59568bb6cdbf18efe182bd821973f2a133663) by Timothée Mazzucotelli).
- Add an RST-style docstring parser ([742e7b2](https://github.com/mkdocstrings/griffe/commit/742e7b2e2101d0679571645584c5a6d3077a9764) by Timothée Mazzucotelli).

### Performance Improvements

- Improve JSON encoder perfs ([6a78eb0](https://github.com/mkdocstrings/griffe/commit/6a78eb0b707a148356fb5bc69d9d0c2115239074) by Timothée Mazzucotelli).

### Bug Fixes

- Handle serialization of Posix paths ([3a66b95](https://github.com/mkdocstrings/griffe/commit/3a66b95a4c91e6160d161acc457c66196adaa4fe) by Timothée Mazzucotelli).
- Fix list annotation getter ([5ae800a](https://github.com/mkdocstrings/griffe/commit/5ae800a8902a28b5241192c0905b1914e2bfe906) by Timothée Mazzucotelli).
- Show accurate line number in Google warnings ([2953590](https://github.com/mkdocstrings/griffe/commit/29535902d53b553906f59295104690c9417eb79f) by Timothée Mazzucotelli).
- Fix assignment names getters ([6990846](https://github.com/mkdocstrings/griffe/commit/69908460b4fe47d1dc3d8d9f6b43d49dee5823aa) by Timothée Mazzucotelli).
- Fix async loader (passing parent) ([57e866e](https://github.com/mkdocstrings/griffe/commit/57e866e4c48f4646142a26c6d2537f4da10e3a2c) by Timothée Mazzucotelli).
- Fix exception name ([4b8b85d](https://github.com/mkdocstrings/griffe/commit/4b8b85dde72a552091534b3293399b844523786f) by Timothée Mazzucotelli).
- Fix Google sections titles logic ([87dd329](https://github.com/mkdocstrings/griffe/commit/87dd32988a9164c47dadf96c0c74a0da8af16bd8) by Timothée Mazzucotelli).
- Prepend current module to base classes (still needs resolution) ([a4b1dee](https://github.com/mkdocstrings/griffe/commit/a4b1deef4beb0e9e79adc920d80232f04ddfdc31) by Timothée Mazzucotelli).
- Fix Google admonition regex ([3902e74](https://github.com/mkdocstrings/griffe/commit/3902e7497ef8b388c3d232a8116cb3bd27fdaad2) by Timothée Mazzucotelli).
- Fix docstring getter ([1442eba](https://github.com/mkdocstrings/griffe/commit/1442eba93479f24a4d90cd9b25f57d304a65cd6c) by Timothée Mazzucotelli).
- Fix getting arguments defaults in the Google-style parser ([67adbaf](https://github.com/mkdocstrings/griffe/commit/67adbafe04de1c8effc124b26565bef59adfb393) by Timothée Mazzucotelli).
- Fix getting arguments annotations in the Google-style parser ([8bcbfba](https://github.com/mkdocstrings/griffe/commit/8bcbfbae861be4c3f9c2b8841c8bc86f39611168) by Timothée Mazzucotelli).

### Code Refactoring

- Export parsers and main function in docstrings module ([96469da](https://github.com/mkdocstrings/griffe/commit/96469dab63a28c061e1d064528f8e07f394c2d81) by Timothée Mazzucotelli).
- Remove top exports ([cd76694](https://github.com/mkdocstrings/griffe/commit/cd7669481a272d7c939b61f6ff2df1cb55eab39e) by Timothée Mazzucotelli).
- Reorganize exceptions ([7f9b805](https://github.com/mkdocstrings/griffe/commit/7f9b8055aa069816b3b55fd02730e97e37a6bea4) by Timothée Mazzucotelli).
- Avoid circular import ([ef27dcd](https://github.com/mkdocstrings/griffe/commit/ef27dcd6cc85590d1982ee14b7f520d379d658b8) by Timothée Mazzucotelli).
- Rename index to [new] offset ([c07cc7d](https://github.com/mkdocstrings/griffe/commit/c07cc7d916d613545073e1159d86c65d58d98b37) by Timothée Mazzucotelli).
- Reorganize code ([5f4fff2](https://github.com/mkdocstrings/griffe/commit/5f4fff21d1da7e1b33554cfb8017b23955999ad5) by Timothée Mazzucotelli).
- Use keyword only parameters ([d34edd6](https://github.com/mkdocstrings/griffe/commit/d34edd629589796d53dbc29d77c5f7041acea5ab) by Timothée Mazzucotelli).
- Default to no parsing for serialization ([8fecd9e](https://github.com/mkdocstrings/griffe/commit/8fecd9ef63f773220bb85379537c4ad25ea0e4fd) by Timothée Mazzucotelli).
- Always extend AST ([c227ae6](https://github.com/mkdocstrings/griffe/commit/c227ae62ee5a3cc764f2c6fc9185400f0c9c48e7) by Timothée Mazzucotelli).
- Set default for kwargs parameters ([7a0b85e](https://github.com/mkdocstrings/griffe/commit/7a0b85e5fd255db743c122e1a13916cdc3eb46ff) by Timothée Mazzucotelli).
- Rename visitor method ([3e0c43c](https://github.com/mkdocstrings/griffe/commit/3e0c43cbed6cec563367f80e86f245b3ba89694c) by Timothée Mazzucotelli).
- Improve typing ([ac86f17](https://github.com/mkdocstrings/griffe/commit/ac86f17bfbfc98d3c41f1830e4356fecc2ed76fc) by Timothée Mazzucotelli).
- Fix typo ([a9ed6e9](https://github.com/mkdocstrings/griffe/commit/a9ed6e95992381df41554a895ed6304ca61048f7) by Timothée Mazzucotelli).
- Rewrite ParameterKind ([90249df](https://github.com/mkdocstrings/griffe/commit/90249df0b478f147fc50a18dfb56ad96ad09e78c) by Timothée Mazzucotelli).
- Add bool methods to docstrings and objects ([548f72e](https://github.com/mkdocstrings/griffe/commit/548f72ed5289aa531c125e4da6ff72a1ff34124d) by Timothée Mazzucotelli).
- Allow setting docstring parser and options on each docstring ([752e084](https://github.com/mkdocstrings/griffe/commit/752e0843bc7388c9a2c7ce9ae2dce03ffa9243e3) by Timothée Mazzucotelli).
- Skip attribute assignments ([e9cc2cd](https://github.com/mkdocstrings/griffe/commit/e9cc2cdd8cae1d15b98ffaa60e777b679ac55e23) by Timothée Mazzucotelli).
- Improve visitor getters ([2ea88c0](https://github.com/mkdocstrings/griffe/commit/2ea88c020481e78060c90d8307a4f6a68047eaa2) by Timothée Mazzucotelli).
- Use relative filepath in docstring warnings ([e894df7](https://github.com/mkdocstrings/griffe/commit/e894df767262623720a45c0b5c16fed544fae106) by Timothée Mazzucotelli).
- Set submodules parent earlier ([53767c0](https://github.com/mkdocstrings/griffe/commit/53767c0c4ef90bfe405dcffd6087e365b98efafc) by Timothée Mazzucotelli).
- Rename Data to Attribute ([febc12e](https://github.com/mkdocstrings/griffe/commit/febc12e5e33bbbdd448298f2cc277a45fd986204) by Timothée Mazzucotelli).
- Rename arguments to parameters ([957856c](https://github.com/mkdocstrings/griffe/commit/957856cf22772584bcced30141afb8ca6a2ac378) by Timothée Mazzucotelli).
- Improve annotation support ([5b2262f](https://github.com/mkdocstrings/griffe/commit/5b2262f9cacce4044716661e6de49a1773ea3aa8) by Timothée Mazzucotelli).
- Always set parent ([cae85de](https://github.com/mkdocstrings/griffe/commit/cae85def4af1f67b537daabdb1e8ae9830dcaec7) by Timothée Mazzucotelli).
- Factorize function handling ([dfece1c](https://github.com/mkdocstrings/griffe/commit/dfece1c0c73076c7d87d4df551f0994b4c2e3b69) by Timothée Mazzucotelli).
- Privatize stuff, fix loggers ([5513ed5](https://github.com/mkdocstrings/griffe/commit/5513ed5345db185e7c08890ca08de17932b34f51) by Timothée Mazzucotelli).
- Use keyword only arguments ([e853fe9](https://github.com/mkdocstrings/griffe/commit/e853fe9188fd2cd2ccc90e5fa1f52443bb00bab7) by Timothée Mazzucotelli).
- Set default values for Argument arguments ([d5cccaa](https://github.com/mkdocstrings/griffe/commit/d5cccaa6ee73e14ca4456b974fba6d01d40bf848) by Timothée Mazzucotelli).
- Swallow extra parsing options ([3d9ebe7](https://github.com/mkdocstrings/griffe/commit/3d9ebe775e1b936e89115d166144610b3a90290c) by Timothée Mazzucotelli).
- Rename `start_index` argument to `offset` ([dd88358](https://github.com/mkdocstrings/griffe/commit/dd88358d8db78636ba5f39fcad92ff5192791852) by Timothée Mazzucotelli).
- Reuse parsers warn function ([03dfdd3](https://github.com/mkdocstrings/griffe/commit/03dfdd38c5977ee83383f95acda1280b3f9ac86b) by Timothée Mazzucotelli).

## [0.2.0](https://github.com/mkdocstrings/griffe/releases/tag/0.2.0) - 2021-09-25

<small>[Compare with 0.1.0](https://github.com/mkdocstrings/griffe/compare/0.1.0...0.2.0)</small>

### Features

- Add Google-style docstring parser ([cdefccc](https://github.com/mkdocstrings/griffe/commit/cdefcccff2cb8236003736545cffaf0bd6f46539) by Timothée Mazzucotelli).
- Support all kinds of functions arguments ([c177562](https://github.com/mkdocstrings/griffe/commit/c177562c358f89da8c541b51d86f9470dd849c8f) by Timothée Mazzucotelli).
- Initial support for class decorators and bases ([8e229aa](https://github.com/mkdocstrings/griffe/commit/8e229aa5f04d21bde108dca517166d291fd2147a) by Timothée Mazzucotelli).
- Add functions decorators support ([fee304d](https://github.com/mkdocstrings/griffe/commit/fee304d44ce33286dedd6bb13a9b7200ea3d4dfa) by Timothée Mazzucotelli).
- Add async loader ([3218bd0](https://github.com/mkdocstrings/griffe/commit/3218bd03fd754a04a4280c29319e6b8d55aac015) by Timothée Mazzucotelli).
- Add relative file path and package properties ([d26ee1f](https://github.com/mkdocstrings/griffe/commit/d26ee1f3f09337af925c8071b4f24b8ae69b01d3) by Timothée Mazzucotelli).
- Add search and output option to the CLI ([3b37692](https://github.com/mkdocstrings/griffe/commit/3b3769234aed87e100ef917fa2db550e650bff0d) by Timothée Mazzucotelli).
- Load docstrings and functions arguments ([cdf29a3](https://github.com/mkdocstrings/griffe/commit/cdf29a3b12b4c04235dfeba1c8ef7461cc05248f) by Timothée Mazzucotelli).
- Support paths in loader ([8f4df75](https://github.com/mkdocstrings/griffe/commit/8f4df7518ee5164e695e27fc9dcedae7a8b05133) by Timothée Mazzucotelli).

### Performance Improvements

- Avoid name lookups in visitor ([00de148](https://github.com/mkdocstrings/griffe/commit/00de1482891e0c0091e79c14fdc318c6a95e4f6f) by Timothée Mazzucotelli).
- Factorize and improve main and extensions visitors ([9b27b56](https://github.com/mkdocstrings/griffe/commit/9b27b56c0fc17d94144fd0b7e3783d3f6f572d3d) by Timothée Mazzucotelli).
- Delegate children computation at runtime ([8d54c87](https://github.com/mkdocstrings/griffe/commit/8d54c8792f2a98c744374ae290bcb31fa81141b4) by Timothée Mazzucotelli).
- Cache dataclasses properties ([2d7447d](https://github.com/mkdocstrings/griffe/commit/2d7447db05c2a3227e6cb66be46d374dac5fdf19) by Timothée Mazzucotelli).
- Optimize node linker ([03f955e](https://github.com/mkdocstrings/griffe/commit/03f955ee698adffb7217528c03691876f299f8ca) by Timothée Mazzucotelli).
- Optimize docstring getter ([4a05516](https://github.com/mkdocstrings/griffe/commit/4a05516de320473b5defd70f208b4e90763f2208) by Timothée Mazzucotelli).

## [0.1.0](https://github.com/mkdocstrings/griffe/releases/tag/0.1.0) - 2021-09-09

<small>[Compare with first commit](https://github.com/mkdocstrings/griffe/compare/7ea73adcc6aebcbe0eb64982916220773731a6b3...0.1.0)</small>

### Features

- Add initial code ([8cbdf7a](https://github.com/mkdocstrings/griffe/commit/8cbdf7a49202dcf3cd617ae905c0f04cdfe053dd) by Timothée Mazzucotelli).
- Generate project from copier-pdm template ([7ea73ad](https://github.com/mkdocstrings/griffe/commit/7ea73adcc6aebcbe0eb64982916220773731a6b3) by Timothée Mazzucotelli).
