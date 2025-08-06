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
              _griffe.exceptions.GriffeError[GriffeError]

                              _griffe.exceptions.GriffeError --> griffe.LoadingError
                


              click griffe.LoadingError href "" "griffe.LoadingError"
              click _griffe.exceptions.GriffeError href "" "_griffe.exceptions.GriffeError"
            
```

The base exception for all Griffe errors.

## NameResolutionError

Bases: `GriffeError`

```

              flowchart TD
              griffe.NameResolutionError[NameResolutionError]
              _griffe.exceptions.GriffeError[GriffeError]

                              _griffe.exceptions.GriffeError --> griffe.NameResolutionError
                


              click griffe.NameResolutionError href "" "griffe.NameResolutionError"
              click _griffe.exceptions.GriffeError href "" "_griffe.exceptions.GriffeError"
            
```

Exception for names that cannot be resolved in a object scope.

## UnhandledEditableModuleError

Bases: `GriffeError`

```

              flowchart TD
              griffe.UnhandledEditableModuleError[UnhandledEditableModuleError]
              _griffe.exceptions.GriffeError[GriffeError]

                              _griffe.exceptions.GriffeError --> griffe.UnhandledEditableModuleError
                


              click griffe.UnhandledEditableModuleError href "" "griffe.UnhandledEditableModuleError"
              click _griffe.exceptions.GriffeError href "" "_griffe.exceptions.GriffeError"
            
```

Exception for unhandled editables modules, when searching modules.

## UnimportableModuleError

Bases: `GriffeError`

```

              flowchart TD
              griffe.UnimportableModuleError[UnimportableModuleError]
              _griffe.exceptions.GriffeError[GriffeError]

                              _griffe.exceptions.GriffeError --> griffe.UnimportableModuleError
                


              click griffe.UnimportableModuleError href "" "griffe.UnimportableModuleError"
              click _griffe.exceptions.GriffeError href "" "_griffe.exceptions.GriffeError"
            
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
              _griffe.exceptions.GriffeError[GriffeError]

                              _griffe.exceptions.GriffeError --> griffe.AliasResolutionError
                


              click griffe.AliasResolutionError href "" "griffe.AliasResolutionError"
              click _griffe.exceptions.GriffeError href "" "_griffe.exceptions.GriffeError"
            
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
              _griffe.exceptions.GriffeError[GriffeError]

                              _griffe.exceptions.GriffeError --> griffe.CyclicAliasError
                


              click griffe.CyclicAliasError href "" "griffe.CyclicAliasError"
              click _griffe.exceptions.GriffeError href "" "_griffe.exceptions.GriffeError"
            
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
              _griffe.exceptions.GriffeError[GriffeError]

                              _griffe.exceptions.GriffeError --> griffe.LastNodeError
                


              click griffe.LastNodeError href "" "griffe.LastNodeError"
              click _griffe.exceptions.GriffeError href "" "_griffe.exceptions.GriffeError"
            
```

Exception raised when trying to access a next or previous node.

## RootNodeError

Bases: `GriffeError`

```

              flowchart TD
              griffe.RootNodeError[RootNodeError]
              _griffe.exceptions.GriffeError[GriffeError]

                              _griffe.exceptions.GriffeError --> griffe.RootNodeError
                


              click griffe.RootNodeError href "" "griffe.RootNodeError"
              click _griffe.exceptions.GriffeError href "" "_griffe.exceptions.GriffeError"
            
```

Exception raised when trying to use siblings properties on a root node.

## BuiltinModuleError

Bases: `GriffeError`

```

              flowchart TD
              griffe.BuiltinModuleError[BuiltinModuleError]
              _griffe.exceptions.GriffeError[GriffeError]

                              _griffe.exceptions.GriffeError --> griffe.BuiltinModuleError
                


              click griffe.BuiltinModuleError href "" "griffe.BuiltinModuleError"
              click _griffe.exceptions.GriffeError href "" "_griffe.exceptions.GriffeError"
            
```

Exception raised when trying to access the filepath of a builtin module.

## ExtensionError

Bases: `GriffeError`

```

              flowchart TD
              griffe.ExtensionError[ExtensionError]
              _griffe.exceptions.GriffeError[GriffeError]

                              _griffe.exceptions.GriffeError --> griffe.ExtensionError
                


              click griffe.ExtensionError href "" "griffe.ExtensionError"
              click _griffe.exceptions.GriffeError href "" "_griffe.exceptions.GriffeError"
            
```

Base class for errors raised by extensions.

## ExtensionNotLoadedError

Bases: `ExtensionError`

```

              flowchart TD
              griffe.ExtensionNotLoadedError[ExtensionNotLoadedError]
              _griffe.exceptions.ExtensionError[ExtensionError]
              _griffe.exceptions.GriffeError[GriffeError]

                              _griffe.exceptions.ExtensionError --> griffe.ExtensionNotLoadedError
                                _griffe.exceptions.GriffeError --> _griffe.exceptions.ExtensionError
                



              click griffe.ExtensionNotLoadedError href "" "griffe.ExtensionNotLoadedError"
              click _griffe.exceptions.ExtensionError href "" "_griffe.exceptions.ExtensionError"
              click _griffe.exceptions.GriffeError href "" "_griffe.exceptions.GriffeError"
            
```

Exception raised when an extension could not be loaded.

## GitError

Bases: `GriffeError`

```

              flowchart TD
              griffe.GitError[GitError]
              _griffe.exceptions.GriffeError[GriffeError]

                              _griffe.exceptions.GriffeError --> griffe.GitError
                


              click griffe.GitError href "" "griffe.GitError"
              click _griffe.exceptions.GriffeError href "" "_griffe.exceptions.GriffeError"
            
```

Exception raised for errors related to Git.
