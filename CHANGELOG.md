# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
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
