r"""Extract an agent from a pulled notebook (.ipynb) without executing it.

.venv\Scripts\python.exe tools\nb_extract.py NOTEBOOK.ipynb OUT_DIR

Writes all_code.py (code cells with `# ---- cell N ----` markers), markdown.md, every %%writefile
target, and runs tools_decode_blobs.py on the code (base85/base64 + zlib/gzip/tar blobs) into
OUT_DIR/extracted. Prints the sha256 of every main.py found and any sha256 the notebook text quotes.
"""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tools_decode_blobs


def main(nb_path, out):
    nb = json.load(open(nb_path, encoding="utf-8"))
    os.makedirs(out, exist_ok=True)
    code, md = [], []
    for i, c in enumerate(nb.get("cells", [])):
        s = c.get("source", "")
        s = "".join(s) if isinstance(s, list) else s
        if c.get("cell_type") != "code":
            md.append(s)
            continue
        code.append(f"# ---- cell {i} ----\n" + s)
        m = re.match(r"\s*%%writefile\s+(?:-a\s+)?(\S+)\s*\n", s)
        if m:
            name = os.path.basename(m.group(1))
            with open(os.path.join(out, name), "w", encoding="utf-8") as f:
                f.write(s[m.end():])
            print("writefile", name, len(s) - m.end())
    with open(os.path.join(out, "all_code.py"), "w", encoding="utf-8") as f:
        f.write("\n\n".join(code))
    with open(os.path.join(out, "markdown.md"), "w", encoding="utf-8") as f:
        f.write("\n\n".join(md))
    tools_decode_blobs.main(os.path.join(out, "all_code.py"), os.path.join(out, "extracted"))
    for root, _, files in os.walk(out):
        for name in files:
            if name.endswith(".py") and name != "all_code.py":
                p = os.path.join(root, name)
                data = open(p, "rb").read()
                print(f"{os.path.relpath(p, out)}: {len(data)} bytes sha256 {hashlib.sha256(data).hexdigest()}")
    quoted = set(re.findall(r"\b[0-9a-f]{64}\b", "\n".join(md + code)))
    print("sha256 quoted in notebook:", sorted(quoted)[:10])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
