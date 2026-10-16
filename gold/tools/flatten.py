r"""Flatten an arena composite (cx_*.py / lm_*.py / pv_*.py) into a self-contained submission main.py.

.venv\Scripts\python.exe gold\tools\flatten.py AGENT_FILE OUT_DIR "one-line description of the changes"

OUT_DIR gets main.py (v6 verbatim with its final `agent` renamed, followed by the config and the layer code from
gold/hybrid/layers.py), LICENSE.txt and NOTICE.txt from the live v6 archive, and submission.tar.gz. Prints sha256.
"""
import ast
import hashlib
import io
import os
import re
import sys
import tarfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "gold", "hybrid"))
sys.path.insert(0, os.path.join(ROOT, "gold", "arena"))
import search  # noqa: E402

CHAMP0_DIR = os.path.join(ROOT, "gold", "arena", "champ0")
LAYERS = os.path.join(ROOT, "gold", "hybrid", "layers.py")


def layer_source():
    """`_g` and `wrap` from layers.py, with `_g` renamed `_lg`: v6 defines its own module-level `_g` (returns the
    default for None values and indexes lists), and a second module-level `_g` would silently replace it."""
    src = open(LAYERS, encoding="utf-8").read()
    tree = ast.parse(src)
    parts = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in ("_g", "wrap"):
            parts.append(ast.get_source_segment(src, node))
    return re.sub(r"\b_g\(", "_lg(", "\n\n\n".join(parts))


def main():
    agent_file, out_dir, desc = sys.argv[1], sys.argv[2], sys.argv[3]
    cfg = search.parse_cfg(agent_file)
    txt = open(agent_file, encoding="utf-8").read()
    for key in ("force_route", "route_table", "late_route"):
        m = re.search(r"_CFG = (\{.*\})\n", txt)
        if m:
            full = ast.literal_eval(m.group(1))
            if key in full:
                cfg[key] = full[key]
    v6 = open(os.path.join(CHAMP0_DIR, "main.py"), encoding="utf-8").read().replace("\r\n", "\n")
    defs = [m.start() for m in re.finditer(r"^def agent\(observation, configuration=None\):", v6, re.M)]
    if len(defs) != 1:
        raise SystemExit(f"expected one top-level agent in v6, found {len(defs)}")
    v6 = v6[:defs[0]] + v6[defs[0]:].replace("def agent(observation, configuration=None):",
                                             "def _v6_agent(observation, configuration=None):", 1)
    header = (f"# ---- team 42 arena build: {desc}\n"
              "# Everything above is the live v6 (cha22 base, Apache-2.0, with team 42 layers) verbatim, except that its\n"
              "# final `agent` is renamed `_v6_agent`. Below: the configuration found by the local king-of-the-hill arena\n"
              "# (gold/arena) and the layer code from gold/hybrid/layers.py.\n")
    body = (f"\n\n{header}\n_CFG = {cfg!r}\n\n\n{layer_source()}\n\n\n"
            "agent = _v6_agent\n_LAYERED = wrap(_CFG, globals())\n\n\n"
            "def agent(observation, configuration=None):\n    return _LAYERED(observation, configuration)\n")
    os.makedirs(out_dir, exist_ok=True)
    main_py = v6 + body
    open(os.path.join(out_dir, "main.py"), "w", encoding="utf-8", newline="\n").write(main_py)
    for f in ("LICENSE.txt", "NOTICE.txt"):
        open(os.path.join(out_dir, f), "wb").write(open(os.path.join(CHAMP0_DIR, f), "rb").read())
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        for f in ("main.py", "LICENSE.txt", "NOTICE.txt"):
            data = open(os.path.join(out_dir, f), "rb").read()
            info = tarfile.TarInfo(f)
            info.size = len(data)
            info.mtime = 0
            t.addfile(info, io.BytesIO(data))
    open(os.path.join(out_dir, "submission.tar.gz"), "wb").write(buf.getvalue())
    sha_main = hashlib.sha256(main_py.encode("utf-8")).hexdigest()
    sha_tar = hashlib.sha256(buf.getvalue()).hexdigest()
    print(f"{out_dir}\\main.py sha256 {sha_main}\n{out_dir}\\submission.tar.gz sha256 {sha_tar}\ncfg {cfg}")


if __name__ == "__main__":
    main()
