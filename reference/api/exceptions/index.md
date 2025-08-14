# Exceptions

## GriffeError

Bases: `Exception`

```

              flowchart TD
              griffe.GriffeError[GriffeError]

              

              click griffe.GriffeError href "" "griffe.GriffeError"
            
```

The base exception for all Griffe errors.

## LoadingError

Bases: `GriffeError`

```

              flowchart TD
              griffe.LoadingError[LoadingError]
              griffe._internal.exceptions.GriffeError[GriffeError]

                              griffe._internal.exceptions.GriffeError --> griffe.LoadingError
                


              click griffe.LoadingError href "" "griffe.LoadingError"
              click griffe._internal.exceptions.GriffeError href "" "griffe._internal.exceptions.GriffeError"
            
```

The base exception for all Griffe errors.

## NameResolutionError

Bases: `GriffeError`

```

              flowchart TD
              griffe.NameResolutionError[NameResolutionError]
              griffe._internal.exceptions.GriffeError[GriffeError]

                              griffe._internal.exceptions.GriffeError --> griffe.NameResolutionError
                


              click griffe.NameResolutionError href "" "griffe.NameResolutionError"
              click griffe._internal.exceptions.GriffeError href "" "griffe._internal.exceptions.GriffeError"
            
```

Exception for names that cannot be resolved in a object scope.

## UnhandledEditableModuleError

Bases: `GriffeError`

```

              flowchart TD
              griffe.UnhandledEditableModuleError[UnhandledEditableModuleError]
              griffe._internal.exceptions.GriffeError[GriffeError]

                              griffe._internal.exceptions.GriffeError --> griffe.UnhandledEditableModuleError
                


              click griffe.UnhandledEditableModuleError href "" "griffe.UnhandledEditableModuleError"
              click griffe._internal.exceptions.GriffeError href "" "griffe._internal.exceptions.GriffeError"
            
```

Exception for unhandled editables modules, when searching modules.

## UnimportableModuleError

Bases: `GriffeError`

```

              flowchart TD
              griffe.UnimportableModuleError[UnimportableModuleError]
              griffe._internal.exceptions.GriffeError[GriffeError]

                              griffe._internal.exceptions.GriffeError --> griffe.UnimportableModuleError
                


              click griffe.UnimportableModuleError href "" "griffe.UnimportableModuleError"
              click griffe._internal.exceptions.GriffeError href "" "griffe._internal.exceptions.GriffeError"
            
```

Exception for modules that cannot be imported.

## AliasResolutionError

```
AliasResolutionError(alias: Alias)

```

Bases: `GriffeError`

```

              flowchart TD
              griffe.AliasResolutionError[AliasResolutionError]
              griffe._internal.exceptions.GriffeError[GriffeError]

                              griffe._internal.exceptions.GriffeError --> griffe.AliasResolutionError
                


              click griffe.AliasResolutionError href "" "griffe.AliasResolutionError"
              click griffe._internal.exceptions.GriffeError href "" "griffe._internal.exceptions.GriffeError"
            
```

Exception for alias that cannot be resolved.

Parameters:

- ### **`alias`**

  (`Alias`) – The alias that could not be resolved.

Attributes:

- **`alias`** (`Alias`) – The alias that triggered the error.

### alias

```
alias: Alias = alias

```

The alias that triggered the error.

## CyclicAliasError

```
CyclicAliasError(chain: list[str])

```

Bases: `GriffeError`

```

              flowchart TD
              griffe.CyclicAliasError[CyclicAliasError]
              griffe._internal.exceptions.GriffeError[GriffeError]

                              griffe._internal.exceptions.GriffeError --> griffe.CyclicAliasError
                


              click griffe.CyclicAliasError href "" "griffe.CyclicAliasError"
              click griffe._internal.exceptions.GriffeError href "" "griffe._internal.exceptions.GriffeError"
            
```

Exception raised when a cycle is detected in aliases.

Parameters:

- ### **`chain`**

  (`list[str]`) – The cyclic chain of items (such as target path).

Attributes:

- **`chain`** (`list[str]`) – The chain of aliases that created the cycle.

### chain

```
chain: list[str] = chain

```

The chain of aliases that created the cycle.

## LastNodeError

Bases: `GriffeError`

```

              flowchart TD
              griffe.LastNodeError[LastNodeError]
              griffe._internal.exceptions.GriffeError[GriffeError]

                              griffe._internal.exceptions.GriffeError --> griffe.LastNodeError
                


              click griffe.LastNodeError href "" "griffe.LastNodeError"
              click griffe._internal.exceptions.GriffeError href "" "griffe._internal.exceptions.GriffeError"
            
```

Exception raised when trying to access a next or previous node.

## RootNodeError

Bases: `GriffeError`

```

              flowchart TD
              griffe.RootNodeError[RootNodeError]
              griffe._internal.exceptions.GriffeError[GriffeError]

                              griffe._internal.exceptions.GriffeError --> griffe.RootNodeError
                


              click griffe.RootNodeError href "" "griffe.RootNodeError"
              click griffe._internal.exceptions.GriffeError href "" "griffe._internal.exceptions.GriffeError"
            
```

Exception raised when trying to use siblings properties on a root node.

## BuiltinModuleError

Bases: `GriffeError`

```

              flowchart TD
              griffe.BuiltinModuleError[BuiltinModuleError]
              griffe._internal.exceptions.GriffeError[GriffeError]

                              griffe._internal.exceptions.GriffeError --> griffe.BuiltinModuleError
                


              click griffe.BuiltinModuleError href "" "griffe.BuiltinModuleError"
              click griffe._internal.exceptions.GriffeError href "" "griffe._internal.exceptions.GriffeError"
            
```

Exception raised when trying to access the filepath of a builtin module.

## ExtensionError

Bases: `GriffeError`

```

              flowchart TD
              griffe.ExtensionError[ExtensionError]
              griffe._internal.exceptions.GriffeError[GriffeError]

                              griffe._internal.exceptions.GriffeError --> griffe.ExtensionError
                


              click griffe.ExtensionError href "" "griffe.ExtensionError"
              click griffe._internal.exceptions.GriffeError href "" "griffe._internal.exceptions.GriffeError"
            
```

Base class for errors raised by extensions.

## ExtensionNotLoadedError

Bases: `ExtensionError`

```

              flowchart TD
              griffe.ExtensionNotLoadedError[ExtensionNotLoadedError]
              griffe._internal.exceptions.ExtensionError[ExtensionError]
              griffe._internal.exceptions.GriffeError[GriffeError]

                              griffe._internal.exceptions.ExtensionError --> griffe.ExtensionNotLoadedError
                                griffe._internal.exceptions.GriffeError --> griffe._internal.exceptions.ExtensionError
                



              click griffe.ExtensionNotLoadedError href "" "griffe.ExtensionNotLoadedError"
              click griffe._internal.exceptions.ExtensionError href "" "griffe._internal.exceptions.ExtensionError"
              click griffe._internal.exceptions.GriffeError href "" "griffe._internal.exceptions.GriffeError"
            
```

Exception raised when an extension could not be loaded.

## GitError

Bases: `GriffeError`

```

              flowchart TD
              griffe.GitError[GitError]
              griffe._internal.exceptions.GriffeError[GriffeError]

                              griffe._internal.exceptions.GriffeError --> griffe.GitError
                


              click griffe.GitError href "" "griffe.GitError"
              click griffe._internal.exceptions.GriffeError href "" "griffe._internal.exceptions.GriffeError"
            
```

Exception raised for errors related to Git.
