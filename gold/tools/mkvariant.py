r"""Write a parameter variant of the arena champion base (v6) and optionally queue it in the arena.

.venv\Scripts\python.exe gold\tools\mkvariant.py NAME "DESC" [--top K=V ...] [--base K=V ...] [--from PATH] [--queue]

--top  overrides v6-level globals (e.g. _EAGER_BANDS={'MILK':(0.2,1.2)}), --base overrides the embedded cha22
namespace (e.g. V9_RACE_DEFAULT=56). Values are Python literals. --from wraps another agent file instead of v6
(its globals are overridden the same way). The variant is gold/hybrid/pv_NAME.py.
"""
import argparse
import ast
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CHAMP0 = os.path.join(ROOT, "gold", "arena", "champ0", "main.py")

TEMPLATE = '''r"""Arena variant {name}: {desc}
Wraps {base_path} and overrides globals (team 42)."""
_BASE_PATH = r"{base_path}"
_NS = {{"__name__": "pv_{name}"}}
exec(compile(open(_BASE_PATH, encoding="utf-8").read(), _BASE_PATH, "exec"), _NS)
OVR_TOP = {top!r}
OVR_BASE = {base!r}
for _k, _v in OVR_TOP.items():
    _NS[_k] = _v
if OVR_BASE:
    for _k, _v in OVR_BASE.items():
        _NS["_BASE_NS"][_k] = _v
_AGENT = _NS["agent"]


def agent(observation, configuration=None):
    return _AGENT(observation, configuration)
'''


def parse_kv(items):
    out = {}
    for it in items or []:
        k, v = it.split("=", 1)
        out[k.strip()] = ast.literal_eval(v.strip())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("desc")
    ap.add_argument("--top", nargs="*")
    ap.add_argument("--base", nargs="*")
    ap.add_argument("--from", dest="src", default=CHAMP0)
    ap.add_argument("--queue", action="store_true")
    a = ap.parse_args()
    path = os.path.join(ROOT, "gold", "hybrid", f"pv_{a.name}.py")
    src = os.path.abspath(a.src)
    open(path, "w", encoding="utf-8").write(TEMPLATE.format(name=a.name, desc=a.desc, base_path=src,
                                                           top=parse_kv(a.top), base=parse_kv(a.base)))
    if a.queue:
        q = os.path.join(ROOT, "gold", "arena", "queue")
        os.makedirs(q, exist_ok=True)
        n = len(os.listdir(q)) + len(os.listdir(os.path.join(ROOT, "gold", "arena", "done")))
        open(os.path.join(q, f"{n + 1:02d}_{a.name}.txt"), "w", encoding="utf-8").write(path + "\n" + a.desc + "\n")
    print(path)


if __name__ == "__main__":
    main()
