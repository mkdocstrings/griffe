---
hide:
- toc
---

# Playground

Play with Griffe's API directly in your browser thanks to [Pyodide](https://pyodide.org/en/stable/).

You can click the **:material-play: Run** button in the top-right corner of the editor, or hit ++ctrl+enter++ to run the code.

```pyodide install="griffe" theme="tomorrow,dracula"
import griffe, micropip

# Install your favorite Python package...
await micropip.install("cowsay")

# And load it with Griffe!
cowsay = griffe.load("cowsay")
cowsay.as_json(indent=2)[:1000]
```
