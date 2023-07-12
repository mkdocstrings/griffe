# Try Griffe in your browser

Try Griffe directly in your browser thanks to Pyodide!
You can click the "Run" button in the top-right corner of each editor,
or hit ++ctrl+enter++ to run the code.


In the following example, we import `griffe` and use it to load itself.
Then we output the signature of the `Function` class as JSON.

```pyodide install="griffe"
import griffe
griffe_pkg = griffe.load("griffe")
griffe_pkg["dataclasses.Function"].as_json(indent=2)
```

Try it out with another package of your choice!
Just replace `your-dist-name` with a package's distribution name,
and `your_package_name` with the package's import name:

```pyodide
import micropip
await micropip.install("your-dist-name")
data = griffe.load("your_package_name")
data.as_json(indent=2)[:1000]  # truncate to a thousand characters...
```
