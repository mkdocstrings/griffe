# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
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


## [0.11.0](https://github.com/pawamoy/griffe/releases/tag/0.11.0) - 2022-01-31

<small>[Compare with 0.10.0](https://github.com/pawamoy/griffe/compare/0.10.0...0.11.0)</small>

### Features
- Support matrix multiplication operator in visitor ([6129e17](https://github.com/pawamoy/griffe/commit/6129e17c86ff49a8e539039dcd04a58b30e3648e) by Timothée Mazzucotelli).

### Bug Fixes
- Fix name resolution for inspected data ([ed3e7e5](https://github.com/pawamoy/griffe/commit/ed3e7e5fa8a9d702c92f47e8244635cf11a923f2) by Timothée Mazzucotelli).
- Make importer actually able to import any nested object ([d007219](https://github.com/pawamoy/griffe/commit/d00721971c7b820e16e463408f04cc3e81a14db6) by Timothée Mazzucotelli).

### Code Refactoring
- Always use search paths to import modules ([a9a378f](https://github.com/pawamoy/griffe/commit/a9a378fc6e47678e08a22383879e4d01acd16b54) by Timothée Mazzucotelli).
- Split out module finder ([7290642](https://github.com/pawamoy/griffe/commit/7290642e36341e64b8ed770e237e9f232e05eada) by Timothée Mazzucotelli).


## [0.10.0](https://github.com/pawamoy/griffe/releases/tag/0.10.0) - 2022-01-14

<small>[Compare with 0.9.0](https://github.com/pawamoy/griffe/compare/0.9.0...0.10.0)</small>

### Bug Fixes
- Fix infinite recursion errors in alias resolver ([133b4e4](https://github.com/pawamoy/griffe/commit/133b4e4bf721fc7536a1ca957f13f7c9f83bf07a) by Timothée Mazzucotelli).
- Fix inspection of nodes children (aliases or not) ([bb354f2](https://github.com/pawamoy/griffe/commit/bb354f21e7b079f4c1e8dd50297d53810c18450e) by Timothée Mazzucotelli).
- Fix relative to absolute import conversion ([464c39e](https://github.com/pawamoy/griffe/commit/464c39eaa812a927190469b18bd910e95e3c1d3c) by Timothée Mazzucotelli).

### Code Refactoring
- Rename some CLI options ([1323268](https://github.com/pawamoy/griffe/commit/13232685b0f2752d92428ab786d428d0af11743b) by Timothée Mazzucotelli).
- Return the loader the to main function ([9c6317e](https://github.com/pawamoy/griffe/commit/9c6317e5afa25dd11d18906503b8010046878868) by Timothée Mazzucotelli).
- Improve logging messages ([b8eb16e](https://github.com/pawamoy/griffe/commit/b8eb16e0fedfe50f2c3ad65e326f4dc6e6918ac0) by Timothée Mazzucotelli).
- Skip inspection of some debug packages ([4ee8968](https://github.com/pawamoy/griffe/commit/4ee896864f1227e32d40571da03f7894c9404579) by Timothée Mazzucotelli).
- Return ... instead of Ellipsis ([f9ae31d](https://github.com/pawamoy/griffe/commit/f9ae31d0f4c904a89c7f581aaa031692740edaef) by Timothée Mazzucotelli).
- Catch attribute errors when cross-referencing docstring annotations ([288803a](https://github.com/pawamoy/griffe/commit/288803a3be93c4e077576ed36dded2a76ce33955) by Timothée Mazzucotelli).
- Support dict methods in lines collection ([1b0cb94](https://github.com/pawamoy/griffe/commit/1b0cb945dba619df7ce1358f7961e4bd80f70218) by Timothée Mazzucotelli).

### Features
- Compute and show some stats ([1b8d0a1](https://github.com/pawamoy/griffe/commit/1b8d0a1c91e03dfa5f92ad9c6dff02863a43fc01) by Timothée Mazzucotelli).
- Add CLI options for alias resolution ([87a59cb](https://github.com/pawamoy/griffe/commit/87a59cb7af5f8e7df9ddba41fb4a4b65cb264481) by Timothée Mazzucotelli).
- Support Google raises annotations cross-refs ([8006ae1](https://github.com/pawamoy/griffe/commit/8006ae13bc27d117ce6b8fdc8ac91dc8541a670f) by Timothée Mazzucotelli).


## [0.9.0](https://github.com/pawamoy/griffe/releases/tag/0.9.0) - 2022-01-04

<small>[Compare with 0.8.0](https://github.com/pawamoy/griffe/compare/0.8.0...0.9.0)</small>

### Features
- Loader option to only follow aliases in known modules ([879d91b](https://github.com/pawamoy/griffe/commit/879d91b4c50832620ce6ee7bdcc85107a6df9a1f) by Timothée Mazzucotelli).
- Use aliases when inspecting too ([60439ee](https://github.com/pawamoy/griffe/commit/60439eefb4635e58e4bd898e5565eab48a5c91d0) by Timothée Mazzucotelli).

### Bug Fixes
- Handle more errors when loading modules ([1aa571a](https://github.com/pawamoy/griffe/commit/1aa571a112e3b2ca955c23f2eef97b36f34bcd8c) by Timothée Mazzucotelli).
- Handle more errors when getting signature ([2db85e7](https://github.com/pawamoy/griffe/commit/2db85e7f655c1e383ba310f40195844c2867e1b9) by Timothée Mazzucotelli).
- Fix checking parent truthfulness ([6129e50](https://github.com/pawamoy/griffe/commit/6129e50331f6e36bcbee2e07b871abee45f7e872) by Timothée Mazzucotelli).
- Fix getting subscript value ([1699f12](https://github.com/pawamoy/griffe/commit/1699f121adc13fcc48f81f46dfca85946e2fb74f) by Timothée Mazzucotelli).
- Support yield nodes ([7d536d5](https://github.com/pawamoy/griffe/commit/7d536d58ffc0faa4caf43f09194d88c35fc47704) by Timothée Mazzucotelli).
- Exclude some special low-level members that cause cyclic issues ([b54ab34](https://github.com/pawamoy/griffe/commit/b54ab346308bb24cba66be9c8f1ee8599481381d) by Timothée Mazzucotelli).
- Fix transforming elements of signatures to annotations ([e278c11](https://github.com/pawamoy/griffe/commit/e278c1102b2762b74bf6b83a2e97a5f87b566e2e) by Timothée Mazzucotelli).
- Detect cyclic aliases and prevent resolution errors ([de5dd12](https://github.com/pawamoy/griffe/commit/de5dd12240acf8a203a86b04e458ce33b67ced9e) by Timothée Mazzucotelli).
- Don't crash while trying to get the representation of an attribute value ([77ac55d](https://github.com/pawamoy/griffe/commit/77ac55d5033e83790c79f3303fdbd05ea66ab729) by Timothée Mazzucotelli).
- Fix building value for joined strings ([6154b69](https://github.com/pawamoy/griffe/commit/6154b69b6da5d63c508ec5095aebe487e491b553) by Timothée Mazzucotelli).
- Fix prevention of cycles while building objects nodes ([48062ac](https://github.com/pawamoy/griffe/commit/48062ac1f8356099b8e0e1069e4321a467073d33) by Timothée Mazzucotelli).
- Better handle relative imports ([91b42de](https://github.com/pawamoy/griffe/commit/91b42dea73c035b2dc20db1e328a53960c51a645) by Timothée Mazzucotelli).
- Fix Google parser missing lines ending with colon ([2f7969c](https://github.com/pawamoy/griffe/commit/2f7969ccbf91b63ae22deb742250068c114fe1a9) by Timothée Mazzucotelli).

### Code Refactoring
- Improve alias resolution robustness ([e708139](https://github.com/pawamoy/griffe/commit/e708139c9bd19be320bdb279310560212872326f) by Timothée Mazzucotelli).
- Remove async loader for now ([acc5ecf](https://github.com/pawamoy/griffe/commit/acc5ecf2bb45dcebdd56d763a657a1075c4a3002) by Timothée Mazzucotelli).
- Improve handling of Google admonitions ([8aa5ed0](https://github.com/pawamoy/griffe/commit/8aa5ed0be4f1902dbdfbce9b4a9c7ac619418d43) by Timothée Mazzucotelli).
- Better handling of import errors and system exits while inspecting modules ([7ba1589](https://github.com/pawamoy/griffe/commit/7ba1589552fb37fba3c2f3093058e135a6e48a27) by Timothée Mazzucotelli).
- Empty generic visit/inspect methods in base classes ([338760e](https://github.com/pawamoy/griffe/commit/338760ea2189e74577250b8c3f4ffe91f81e6b6e) by Timothée Mazzucotelli).


## [0.8.0](https://github.com/pawamoy/griffe/releases/tag/0.8.0) - 2022-01-02

<small>[Compare with 0.7.1](https://github.com/pawamoy/griffe/compare/0.7.1...0.8.0)</small>

### Features
- Support getting attribute annotation from parent in RST docstring parser ([25db61a](https://github.com/pawamoy/griffe/commit/25db61ab01042ad797ac5cdea0b2f7e2382191c1) by Timothée Mazzucotelli).
- Handle relative imports ([62b0927](https://github.com/pawamoy/griffe/commit/62b0927516ca345de61aa3cc03e977d4d37220de) by Timothée Mazzucotelli).
- Support wildcard imports ([77a3cb7](https://github.com/pawamoy/griffe/commit/77a3cb7e4198dc2e2cea953c5f621544b564552c) by Timothée Mazzucotelli).
- Support configuring log level (CLI/env var) ([839d78e](https://github.com/pawamoy/griffe/commit/839d78ea302df004fba1b6fad9eb84d861f0f4aa) by Timothée Mazzucotelli).
- Support loading `*.py[cod]` and `*.so` modules ([cd98a6f](https://github.com/pawamoy/griffe/commit/cd98a6f3afbbf8f6a176aa7780a8b916a9ee64f2) by Timothée Mazzucotelli).
- Support inspecting builtin functions/methods ([aa1fce3](https://github.com/pawamoy/griffe/commit/aa1fce330ce3e2af4dd9a3c43827637d1e220dde) by Timothée Mazzucotelli).

### Code Refactoring
- Handle extensions errors ([11278ca](https://github.com/pawamoy/griffe/commit/11278caea27e9f91a1dc9cc160414f01b24f5354) by Timothée Mazzucotelli).
- Don't always try to find a module as a relative  path ([e6df277](https://github.com/pawamoy/griffe/commit/e6df2774bfd631fd9a09913480b4d61d137bc0c6) by Timothée Mazzucotelli).
- Improve loggers patching ([f4b262a](https://github.com/pawamoy/griffe/commit/f4b262ab5a3d874591324adc2b5ffff214c7e7da) by Timothée Mazzucotelli).
- Improve dynamic imports ([2998195](https://github.com/pawamoy/griffe/commit/299819519b7eb9b07b938d22bfb3a27e3b05095d) by Timothée Mazzucotelli).


## [0.7.1](https://github.com/pawamoy/griffe/releases/tag/0.7.1) - 2021-12-28

<small>[Compare with 0.7.0](https://github.com/pawamoy/griffe/compare/0.7.0...0.7.1)</small>

### Code Refactoring
- Only log warning if async mode is used ([356e848](https://github.com/pawamoy/griffe/commit/356e848c8e233334401461b02a0188731b71a8cf) by Timothée Mazzucotelli).


## [0.7.0](https://github.com/pawamoy/griffe/releases/tag/0.7.0) - 2021-12-28

<small>[Compare with 0.6.0](https://github.com/pawamoy/griffe/compare/0.6.0...0.7.0)</small>

### Features
- Support more nodes on Python 3.7 ([7f2c4ec](https://github.com/pawamoy/griffe/commit/7f2c4ec3bf610ade7305e19ab220a4b447bed41d) by Timothée Mazzucotelli).

### Code Refactoring
- Don't crash on syntax errors and log an error ([10bb6b1](https://github.com/pawamoy/griffe/commit/10bb6b15bb9b132626c525b81f3ee33c3bb5746f) by Timothée Mazzucotelli).


## [0.6.0](https://github.com/pawamoy/griffe/releases/tag/0.6.0) - 2021-12-27

<small>[Compare with 0.5.0](https://github.com/pawamoy/griffe/compare/0.5.0...0.6.0)</small>

### Features
- Support more AST nodes ([cd1b305](https://github.com/pawamoy/griffe/commit/cd1b305932832ad5347ce829a48a311e3c44d542) by Timothée Mazzucotelli).

### Code Refactoring
- Use annotation getter for base classes ([8b1a7ed](https://github.com/pawamoy/griffe/commit/8b1a7edc11a72f679689fa9ba9e632907f9304f8) by Timothée Mazzucotelli).


## [0.5.0](https://github.com/pawamoy/griffe/releases/tag/0.5.0) - 2021-12-20

<small>[Compare with 0.4.0](https://github.com/pawamoy/griffe/compare/0.4.0...0.5.0)</small>

### Features
- Add support for Python 3.7 ([4535adc](https://github.com/pawamoy/griffe/commit/4535adce19edbe7e9cde90f3b1075a8245a6ebc8) by Timothée Mazzucotelli).

### Bug Fixes
- Don't propagate aliases of an alias ([8af48f8](https://github.com/pawamoy/griffe/commit/8af48f87e2e6bb0f2cf1531fa10287a069f67289) by Timothée Mazzucotelli).
- Don't reassign members defined in except clauses ([d918b4e](https://github.com/pawamoy/griffe/commit/d918b4efcedcedbec6db214ade8cde921d7e97b2) by Timothée Mazzucotelli).


## [0.4.0](https://github.com/pawamoy/griffe/releases/tag/0.4.0) - 2021-11-28

<small>[Compare with 0.3.0](https://github.com/pawamoy/griffe/compare/0.3.0...0.4.0)</small>

### Features
- Add a prototype 'hybrid' extension ([8cb3c16](https://github.com/pawamoy/griffe/commit/8cb3c1661223378a2511fd42a0693d0fbfe924d8) by Timothée Mazzucotelli).
- Allow passing extensions config as JSON on the CLI ([9a7fa8b](https://github.com/pawamoy/griffe/commit/9a7fa8bd88752ca1a074179db3a4c7fc41b68028) by Timothée Mazzucotelli).
- Support names for returns, yields and receives sections items ([1c5a4c9](https://github.com/pawamoy/griffe/commit/1c5a4c95738615ea9bb6a816c61d078e6133100a) by Timothée Mazzucotelli).
- Store aliases on each object ([91ba643](https://github.com/pawamoy/griffe/commit/91ba643b3e8e9a8f56f3280f699a18b1e654ccd7) by Timothée Mazzucotelli).
- Support in[tro]spection ([3a0587d](https://github.com/pawamoy/griffe/commit/3a0587dbf26f288722c7d27e781d0887c5cdf641) by Timothée Mazzucotelli).
- Support multiple return, yield and receive items ([0fc70cb](https://github.com/pawamoy/griffe/commit/0fc70cbcc07c63ecf1026e4bef30bd0ff3f73958) by Timothée Mazzucotelli).
- Support namespace packages ([2414c8e](https://github.com/pawamoy/griffe/commit/2414c8e24b7ba7ee986d95b301662fd06ef350fe) by Timothée Mazzucotelli).

### Bug Fixes
- Fix extensions loader ([78fb70b](https://github.com/pawamoy/griffe/commit/78fb70b77076b68fa30592caa5e92a91f0ce2caa) by Timothée Mazzucotelli).
- Avoid visiting/inspecting multiple times ([75a8a8b](https://github.com/pawamoy/griffe/commit/75a8a8b7145e1872cbecf93f8e33749b51b5b77b) by Timothée Mazzucotelli).
- Set modules collection attribute earlier ([592c0bd](https://github.com/pawamoy/griffe/commit/592c0bde6b6959615bc56030758098c8e45119a2) by Timothée Mazzucotelli).
- Support inequality nodes ([b0ed247](https://github.com/pawamoy/griffe/commit/b0ed247c9fe42a324a4e8e4a972676afbaa26976) by Timothée Mazzucotelli).
- Handle Div nodes for values ([272e4d6](https://github.com/pawamoy/griffe/commit/272e4d64b5ca557732af903d35aefbe405bd3ac0) by Timothée Mazzucotelli).

### Code Refactoring
- Set log level to INFO ([718e73e](https://github.com/pawamoy/griffe/commit/718e73ebb6767c0b10c03482d6f92cf135778ec7) by Timothée Mazzucotelli).
- Add target setter ([7f0064c](https://github.com/pawamoy/griffe/commit/7f0064c154459b4f4da7fc25bc49f8dd1e4fd2c0) by Timothée Mazzucotelli).
- Reorganize conditions ([15ab876](https://github.com/pawamoy/griffe/commit/15ab8763acc92d9160b847dc878f8bdad7f0b705) by Timothée Mazzucotelli).
- Avoid recursion loops ([ea6acec](https://github.com/pawamoy/griffe/commit/ea6acec10c0a805a9ae4e03ae0b92fb2a54cf79b) by Timothée Mazzucotelli).
- Update aliases when replacing a member ([99a0f8b](https://github.com/pawamoy/griffe/commit/99a0f8b9a425251ddcde853f2ad9ee95504b2127) by Timothée Mazzucotelli).
- Reorganize code ([31fcdb1](https://github.com/pawamoy/griffe/commit/31fcdb1cbe0eceedc59cc7c1c692dc4ef210ef53) by Timothée Mazzucotelli).
- Replace DocstringException with DocstringRaise ([d5ed87a](https://github.com/pawamoy/griffe/commit/d5ed87a478411aeb8248e948dbb6c228b80f5fbe) by Timothée Mazzucotelli).
- Refactor loaders ([d9b94bb](https://github.com/pawamoy/griffe/commit/d9b94bbcb55c29268ab1e077420e2b0d5297638c) by Timothée Mazzucotelli).
- Improve typing ([e08bcfa](https://github.com/pawamoy/griffe/commit/e08bcfac68aa22dc4bc58914b3340c1743f87ee7) by Timothée Mazzucotelli).


## [0.3.0](https://github.com/pawamoy/griffe/releases/tag/0.3.0) - 2021-11-21

<small>[Compare with 0.2.0](https://github.com/pawamoy/griffe/compare/0.2.0...0.3.0)</small>

### Features
- Handle aliases and their resolution ([67ae903](https://github.com/pawamoy/griffe/commit/67ae9034ac25061bc7d5c6def63715209643ca20) by Timothée Mazzucotelli).
- Resolve annotations in docstrings ([847384a](https://github.com/pawamoy/griffe/commit/847384a322017ca94bd40d4342eb4b8b42858f91) by Timothée Mazzucotelli).
- Resolve annotations ([6451eff](https://github.com/pawamoy/griffe/commit/6451effa01aa09cd3db1584fe111152de649e525) by Timothée Mazzucotelli).
- Add lines property to objects ([7daf7db](https://github.com/pawamoy/griffe/commit/7daf7db9ae58fb13985d1adacbde5d0bec2a35e4) by Timothée Mazzucotelli).
- Allow setting docstring parser and options on each object ([07a1d2e](https://github.com/pawamoy/griffe/commit/07a1d2e83c12bfa0f7b0dd35149b5cc0d0f600d6) by Timothée Mazzucotelli).
- Get attributes annotations from parent ([003b990](https://github.com/pawamoy/griffe/commit/003b99020f45b350d29329690d18f6c6cb3821f9) by Timothée Mazzucotelli).
- Draft extensions loader ([17ccd03](https://github.com/pawamoy/griffe/commit/17ccd03cadc5cbb230071e78beab96a0b97456a1) by Timothée Mazzucotelli).
- Add properties to objects ([0ec301a](https://github.com/pawamoy/griffe/commit/0ec301a5e97bee6556b62cb6ee35af9976f8410b) by Timothée Mazzucotelli).
- Handle .pth files when searching modules ([2a2e182](https://github.com/pawamoy/griffe/commit/2a2e1826fe0235c5bd47b5d6b1b64a30a81a3f4b) by Timothée Mazzucotelli).
- Add `default` property to docstring parameters ([6298ba3](https://github.com/pawamoy/griffe/commit/6298ba34d4e769568e519e21549137df3649e01b) by Timothée Mazzucotelli).
- Accept RST and Numpy parsers ([1cf147d](https://github.com/pawamoy/griffe/commit/1cf147d8df0491104efd084ce3308da77fc2c817) by Timothée Mazzucotelli).
- Support data (attributes/variables) ([dce84d1](https://github.com/pawamoy/griffe/commit/dce84d106cf067f11305f804a24cfd7d5643d902) by Timothée Mazzucotelli).
- Add Numpy-style parser ([ad5b72d](https://github.com/pawamoy/griffe/commit/ad5b72d174433764e85f937ea1096c0f458532f8) by Timothée Mazzucotelli).
- Support more section kinds in Google-style ([9d3d047](https://github.com/pawamoy/griffe/commit/9d3d0472d0bb55352b371de3da0816419fcf59e0) by Timothée Mazzucotelli).
- Add docstring section kinds ([b270483](https://github.com/pawamoy/griffe/commit/b2704833bc74131269306b9947ea2b46edafd349) by Timothée Mazzucotelli).
- Accept initial arguments when creating container ([90c5956](https://github.com/pawamoy/griffe/commit/90c59568bb6cdbf18efe182bd821973f2a133663) by Timothée Mazzucotelli).
- Add an RST-style docstring parser ([742e7b2](https://github.com/pawamoy/griffe/commit/742e7b2e2101d0679571645584c5a6d3077a9764) by Timothée Mazzucotelli).

### Performance Improvements
- Improve JSON encoder perfs ([6a78eb0](https://github.com/pawamoy/griffe/commit/6a78eb0b707a148356fb5bc69d9d0c2115239074) by Timothée Mazzucotelli).

### Bug Fixes
- Handle serialization of Posix paths ([3a66b95](https://github.com/pawamoy/griffe/commit/3a66b95a4c91e6160d161acc457c66196adaa4fe) by Timothée Mazzucotelli).
- Fix list annotation getter ([5ae800a](https://github.com/pawamoy/griffe/commit/5ae800a8902a28b5241192c0905b1914e2bfe906) by Timothée Mazzucotelli).
- Show accurate line number in Google warnings ([2953590](https://github.com/pawamoy/griffe/commit/29535902d53b553906f59295104690c9417eb79f) by Timothée Mazzucotelli).
- Fix assignment names getters ([6990846](https://github.com/pawamoy/griffe/commit/69908460b4fe47d1dc3d8d9f6b43d49dee5823aa) by Timothée Mazzucotelli).
- Fix async loader (passing parent) ([57e866e](https://github.com/pawamoy/griffe/commit/57e866e4c48f4646142a26c6d2537f4da10e3a2c) by Timothée Mazzucotelli).
- Fix exception name ([4b8b85d](https://github.com/pawamoy/griffe/commit/4b8b85dde72a552091534b3293399b844523786f) by Timothée Mazzucotelli).
- Fix Google sections titles logic ([87dd329](https://github.com/pawamoy/griffe/commit/87dd32988a9164c47dadf96c0c74a0da8af16bd8) by Timothée Mazzucotelli).
- Prepend current module to base classes (still needs resolution) ([a4b1dee](https://github.com/pawamoy/griffe/commit/a4b1deef4beb0e9e79adc920d80232f04ddfdc31) by Timothée Mazzucotelli).
- Fix Google admonition regex ([3902e74](https://github.com/pawamoy/griffe/commit/3902e7497ef8b388c3d232a8116cb3bd27fdaad2) by Timothée Mazzucotelli).
- Fix docstring getter ([1442eba](https://github.com/pawamoy/griffe/commit/1442eba93479f24a4d90cd9b25f57d304a65cd6c) by Timothée Mazzucotelli).
- Fix getting arguments defaults in the Google-style parser ([67adbaf](https://github.com/pawamoy/griffe/commit/67adbafe04de1c8effc124b26565bef59adfb393) by Timothée Mazzucotelli).
- Fix getting arguments annotations in the Google-style parser ([8bcbfba](https://github.com/pawamoy/griffe/commit/8bcbfbae861be4c3f9c2b8841c8bc86f39611168) by Timothée Mazzucotelli).

### Code Refactoring
- Export parsers and main function in docstrings module ([96469da](https://github.com/pawamoy/griffe/commit/96469dab63a28c061e1d064528f8e07f394c2d81) by Timothée Mazzucotelli).
- Remove top exports ([cd76694](https://github.com/pawamoy/griffe/commit/cd7669481a272d7c939b61f6ff2df1cb55eab39e) by Timothée Mazzucotelli).
- Reorganize exceptions ([7f9b805](https://github.com/pawamoy/griffe/commit/7f9b8055aa069816b3b55fd02730e97e37a6bea4) by Timothée Mazzucotelli).
- Avoid circular import ([ef27dcd](https://github.com/pawamoy/griffe/commit/ef27dcd6cc85590d1982ee14b7f520d379d658b8) by Timothée Mazzucotelli).
- Rename index to [new] offset ([c07cc7d](https://github.com/pawamoy/griffe/commit/c07cc7d916d613545073e1159d86c65d58d98b37) by Timothée Mazzucotelli).
- Reorganize code ([5f4fff2](https://github.com/pawamoy/griffe/commit/5f4fff21d1da7e1b33554cfb8017b23955999ad5) by Timothée Mazzucotelli).
- Use keyword only parameters ([d34edd6](https://github.com/pawamoy/griffe/commit/d34edd629589796d53dbc29d77c5f7041acea5ab) by Timothée Mazzucotelli).
- Default to no parsing for serialization ([8fecd9e](https://github.com/pawamoy/griffe/commit/8fecd9ef63f773220bb85379537c4ad25ea0e4fd) by Timothée Mazzucotelli).
- Always extend AST ([c227ae6](https://github.com/pawamoy/griffe/commit/c227ae62ee5a3cc764f2c6fc9185400f0c9c48e7) by Timothée Mazzucotelli).
- Set default for kwargs parameters ([7a0b85e](https://github.com/pawamoy/griffe/commit/7a0b85e5fd255db743c122e1a13916cdc3eb46ff) by Timothée Mazzucotelli).
- Rename visitor method ([3e0c43c](https://github.com/pawamoy/griffe/commit/3e0c43cbed6cec563367f80e86f245b3ba89694c) by Timothée Mazzucotelli).
- Improve typing ([ac86f17](https://github.com/pawamoy/griffe/commit/ac86f17bfbfc98d3c41f1830e4356fecc2ed76fc) by Timothée Mazzucotelli).
- Fix typo ([a9ed6e9](https://github.com/pawamoy/griffe/commit/a9ed6e95992381df41554a895ed6304ca61048f7) by Timothée Mazzucotelli).
- Rewrite ParameterKind ([90249df](https://github.com/pawamoy/griffe/commit/90249df0b478f147fc50a18dfb56ad96ad09e78c) by Timothée Mazzucotelli).
- Add bool methods to docstrings and objects ([548f72e](https://github.com/pawamoy/griffe/commit/548f72ed5289aa531c125e4da6ff72a1ff34124d) by Timothée Mazzucotelli).
- Allow setting docstring parser and options on each docstring ([752e084](https://github.com/pawamoy/griffe/commit/752e0843bc7388c9a2c7ce9ae2dce03ffa9243e3) by Timothée Mazzucotelli).
- Skip attribute assignments ([e9cc2cd](https://github.com/pawamoy/griffe/commit/e9cc2cdd8cae1d15b98ffaa60e777b679ac55e23) by Timothée Mazzucotelli).
- Improve visitor getters ([2ea88c0](https://github.com/pawamoy/griffe/commit/2ea88c020481e78060c90d8307a4f6a68047eaa2) by Timothée Mazzucotelli).
- Use relative filepath in docstring warnings ([e894df7](https://github.com/pawamoy/griffe/commit/e894df767262623720a45c0b5c16fed544fae106) by Timothée Mazzucotelli).
- Set submodules parent earlier ([53767c0](https://github.com/pawamoy/griffe/commit/53767c0c4ef90bfe405dcffd6087e365b98efafc) by Timothée Mazzucotelli).
- Rename Data to Attribute ([febc12e](https://github.com/pawamoy/griffe/commit/febc12e5e33bbbdd448298f2cc277a45fd986204) by Timothée Mazzucotelli).
- Rename arguments to parameters ([957856c](https://github.com/pawamoy/griffe/commit/957856cf22772584bcced30141afb8ca6a2ac378) by Timothée Mazzucotelli).
- Improve annotation support ([5b2262f](https://github.com/pawamoy/griffe/commit/5b2262f9cacce4044716661e6de49a1773ea3aa8) by Timothée Mazzucotelli).
- Always set parent ([cae85de](https://github.com/pawamoy/griffe/commit/cae85def4af1f67b537daabdb1e8ae9830dcaec7) by Timothée Mazzucotelli).
- Factorize function handling ([dfece1c](https://github.com/pawamoy/griffe/commit/dfece1c0c73076c7d87d4df551f0994b4c2e3b69) by Timothée Mazzucotelli).
- Privatize stuff, fix loggers ([5513ed5](https://github.com/pawamoy/griffe/commit/5513ed5345db185e7c08890ca08de17932b34f51) by Timothée Mazzucotelli).
- Use keyword only arguments ([e853fe9](https://github.com/pawamoy/griffe/commit/e853fe9188fd2cd2ccc90e5fa1f52443bb00bab7) by Timothée Mazzucotelli).
- Set default values for Argument arguments ([d5cccaa](https://github.com/pawamoy/griffe/commit/d5cccaa6ee73e14ca4456b974fba6d01d40bf848) by Timothée Mazzucotelli).
- Swallow extra parsing options ([3d9ebe7](https://github.com/pawamoy/griffe/commit/3d9ebe775e1b936e89115d166144610b3a90290c) by Timothée Mazzucotelli).
- Rename `start_index` argument to `offset` ([dd88358](https://github.com/pawamoy/griffe/commit/dd88358d8db78636ba5f39fcad92ff5192791852) by Timothée Mazzucotelli).
- Reuse parsers warn function ([03dfdd3](https://github.com/pawamoy/griffe/commit/03dfdd38c5977ee83383f95acda1280b3f9ac86b) by Timothée Mazzucotelli).


## [0.2.0](https://github.com/pawamoy/griffe/releases/tag/0.2.0) - 2021-09-25

<small>[Compare with 0.1.0](https://github.com/pawamoy/griffe/compare/0.1.0...0.2.0)</small>

### Features
- Add Google-style docstring parser ([cdefccc](https://github.com/pawamoy/griffe/commit/cdefcccff2cb8236003736545cffaf0bd6f46539) by Timothée Mazzucotelli).
- Support all kinds of functions arguments ([c177562](https://github.com/pawamoy/griffe/commit/c177562c358f89da8c541b51d86f9470dd849c8f) by Timothée Mazzucotelli).
- Initial support for class decorators and bases ([8e229aa](https://github.com/pawamoy/griffe/commit/8e229aa5f04d21bde108dca517166d291fd2147a) by Timothée Mazzucotelli).
- Add functions decorators support ([fee304d](https://github.com/pawamoy/griffe/commit/fee304d44ce33286dedd6bb13a9b7200ea3d4dfa) by Timothée Mazzucotelli).
- Add async loader ([3218bd0](https://github.com/pawamoy/griffe/commit/3218bd03fd754a04a4280c29319e6b8d55aac015) by Timothée Mazzucotelli).
- Add relative file path and package properties ([d26ee1f](https://github.com/pawamoy/griffe/commit/d26ee1f3f09337af925c8071b4f24b8ae69b01d3) by Timothée Mazzucotelli).
- Add search and output option to the CLI ([3b37692](https://github.com/pawamoy/griffe/commit/3b3769234aed87e100ef917fa2db550e650bff0d) by Timothée Mazzucotelli).
- Load docstrings and functions arguments ([cdf29a3](https://github.com/pawamoy/griffe/commit/cdf29a3b12b4c04235dfeba1c8ef7461cc05248f) by Timothée Mazzucotelli).
- Support paths in loader ([8f4df75](https://github.com/pawamoy/griffe/commit/8f4df7518ee5164e695e27fc9dcedae7a8b05133) by Timothée Mazzucotelli).

### Performance Improvements
- Avoid name lookups in visitor ([00de148](https://github.com/pawamoy/griffe/commit/00de1482891e0c0091e79c14fdc318c6a95e4f6f) by Timothée Mazzucotelli).
- Factorize and improve main and extensions visitors ([9b27b56](https://github.com/pawamoy/griffe/commit/9b27b56c0fc17d94144fd0b7e3783d3f6f572d3d) by Timothée Mazzucotelli).
- Delegate children computation at runtime ([8d54c87](https://github.com/pawamoy/griffe/commit/8d54c8792f2a98c744374ae290bcb31fa81141b4) by Timothée Mazzucotelli).
- Cache dataclasses properties ([2d7447d](https://github.com/pawamoy/griffe/commit/2d7447db05c2a3227e6cb66be46d374dac5fdf19) by Timothée Mazzucotelli).
- Optimize node linker ([03f955e](https://github.com/pawamoy/griffe/commit/03f955ee698adffb7217528c03691876f299f8ca) by Timothée Mazzucotelli).
- Optimize docstring getter ([4a05516](https://github.com/pawamoy/griffe/commit/4a05516de320473b5defd70f208b4e90763f2208) by Timothée Mazzucotelli).


## [0.1.0](https://github.com/pawamoy/griffe/releases/tag/0.1.0) - 2021-09-09

<small>[Compare with first commit](https://github.com/pawamoy/griffe/compare/7ea73adcc6aebcbe0eb64982916220773731a6b3...0.1.0)</small>

### Features
- Add initial code ([8cbdf7a](https://github.com/pawamoy/griffe/commit/8cbdf7a49202dcf3cd617ae905c0f04cdfe053dd) by Timothée Mazzucotelli).
- Generate project from copier-pdm template ([7ea73ad](https://github.com/pawamoy/griffe/commit/7ea73adcc6aebcbe0eb64982916220773731a6b3) by Timothée Mazzucotelli).
