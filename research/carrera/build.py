r"""Build a V10_CarreraGT research candidate: the live v10 main.py with layers from research/carrera/layers appended.

.venv/bin/python research/carrera/build.py [--base v10|v11] NAME LAYER [LAYER ...]
    -> research/carrera/cands/NAME/main.py (refuses to overwrite)

The base source is read byte for byte from the submitted package (its sha256 prefix is checked): v10 is the live
56600500, v11 is the other session's v10 + prebuy-trap patch (default v10). Each layer file is appended in the
order given, and the result must compile.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASES = {"v10": ("v10_own_cha22_tick_trapguard_tomato", "2a30594b"),         # live 56600500
         "v11": ("v11_own_cha22_tick_trapguard_tomato_prebuy0", "5e7dbfca")}  # v10 + prebuy-trap patch


def main():
    args = sys.argv[1:]
    base = "v10"
    base_path = None
    if args and args[0] == "--base":
        base, args = args[1], args[2:]
    elif args and args[0] == "--base-path":      # a research base, e.g. research/carrera/bases/v11a_x18/main.py
        base_path, args = args[1], args[2:]
    name, layers = args[0], args[1:]
    if base_path:
        src = open(base_path, "rb").read()
        print("base", base_path, hashlib.sha256(src).hexdigest()[:8])
    else:
        folder, prefix = BASES[base]
        src = open(os.path.join(ROOT, "submissions", folder, "main.py"), "rb").read()
        sha = hashlib.sha256(src).hexdigest()
        assert sha.startswith(prefix), f"{base} main.py changed: {sha}"
    out = src.decode("utf-8")
    nl = "\r\n" if "\r\n" in out else "\n"
    for layer in layers:
        path = layer if os.path.exists(layer) else os.path.join(HERE, "layers", layer + ".py")
        code = open(path, encoding="utf-8").read()
        out = out.rstrip() + nl + nl + code.strip().replace("\r\n", "\n").replace("\n", nl) + nl
    compile(out, "main.py", "exec")
    assert b"/Users/" not in out.encode() and "C:\\Users" not in out
    ns = {"__name__": "cand_check"}
    exec(compile(out, "main.py", "exec"), ns)   # the Kaggle loader calls the module's last callable
    last = [v for v in ns.values() if callable(v)][-1]
    assert getattr(last, "__name__", "") == "agent", f"last callable is {last!r}, not agent"
    d = os.path.join(HERE, "cands", name)
    os.makedirs(d, exist_ok=False)
    with open(os.path.join(d, "main.py"), "w", encoding="utf-8", newline="") as f:
        f.write(out)
    print(d, hashlib.sha256(out.encode("utf-8")).hexdigest()[:8], len(out.encode("utf-8")), "bytes")


if __name__ == "__main__":
    main()
