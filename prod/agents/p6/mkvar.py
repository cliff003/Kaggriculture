r"""Make a p6 variant file: a wrapped p6 build plus a CFG override (team 42 research).

    .venv/bin/python prod/agents/p6/mkvar.py NAME '{"land_days": [6, 8, 99]}' [--no-tick]

Writes prod/agents/p6v/NAME/main.py = prod/agents/p6m/main.py (or p6mn with --no-tick) followed by one line that
sets STATE["_override"]; p6's new_state() reads it at the start of every game, so the variant needs no rebuild.
Lists in the JSON are turned into tuples (the CFG uses tuples for land_days and the like).
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def tup(v):
    if isinstance(v, list):
        return tuple(tup(x) for x in v)
    if isinstance(v, dict):
        return {k: tup(x) for k, x in v.items()}
    return v


def main():
    name, js = sys.argv[1], sys.argv[2]
    base = "p6mn" if "--no-tick" in sys.argv else "p6m"
    ov = {k: tup(v) for k, v in json.loads(js).items()}
    src = open(os.path.join(ROOT, "prod", "agents", base, "main.py"), encoding="utf-8").read()
    assert "STATE" in src
    src = src.rstrip("\n") + "\n\n# p6 variant " + name + "\nSTATE[\"_override\"] = " + repr(ov) + "\n"
    ns = {"__name__": "p6var_check"}
    exec(compile(src, "main.py", "exec"), ns)
    last = [v for v in ns.values() if callable(v)][-1]
    assert getattr(last, "__name__", "") == "agent", last
    out = os.path.join(ROOT, "prod", "agents", "p6v", name)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "main.py"), "w", encoding="utf-8", newline="\n") as f:
        f.write(src)
    print("wrote", os.path.join(out, "main.py"), ov)


if __name__ == "__main__":
    main()
