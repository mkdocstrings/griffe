# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
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
