"""Print the markdown cells (and short code-cell heads) of a Kaggle notebook .ipynb."""
import json
import sys

nb = json.load(open(sys.argv[1], encoding="utf-8"))
maxc = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
for i, c in enumerate(nb.get("cells", [])):
    src = "".join(c.get("source", []))
    if c.get("cell_type") == "markdown":
        print(f"--- md {i}\n{src[:maxc]}")
    else:
        head = src.strip().split("\n")[0][:160]
        print(f"--- code {i} ({len(src)} chars): {head}")
