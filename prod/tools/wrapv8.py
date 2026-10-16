r"""Wrap any agent source with v8's market layers (order-slot priority, day-end room guard, eager sales,
sell sorting, wheat TICK arbitrage with its rival guard). cha22-specific layers (wheat lead-sell, six-sheep
fix, FERTMORE) are left out.

wrapv8.py BASE_MAIN.py OUT_DIR [--v8 submissions/v8_own_cha22_tick_guard10/main.py] [--no-tick] [--no-eager]
The base's own `agent` is the innermost layer; its STATE dict is re-exported so bench.py --set still works.
"""
import argparse
import base64
import os
import zlib


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("out")
    ap.add_argument("--v8", default="submissions/v8_own_cha22_tick_guard10/main.py")
    ap.add_argument("--no-tick", action="store_true")
    ap.add_argument("--no-eager", action="store_true")
    a = ap.parse_args()
    v8 = open(a.v8, encoding="utf-8").read().replace("\r\n", "\n").split("\n")
    idx = {l.split("(")[0].split(" =")[0]: i for i, l in enumerate(v8) if l.startswith(("def ", "_"))}
    lo = next(i for i, l in enumerate(v8) if l.startswith("_SLOT_START = "))
    hi = next(i for i, l in enumerate(v8) if l.startswith("# ---- team 42 arena build"))
    tk = next(i for i, l in enumerate(v8) if l.startswith("_TICK_SRC = r'''"))
    base = open(a.base, encoding="utf-8").read().replace("\r\n", "\n")
    payload = base64.b85encode(zlib.compress(base.encode("utf-8"), 9)).decode("ascii")
    lines = "\n".join("    " + repr(payload[i:i + 120]) for i in range(0, len(payload), 120))
    out = [
        "# team 42 research build: base agent wrapped with v8 market layers (prod/tools/wrapv8.py)",
        "import base64 as _b64",
        "import math",
        "import zlib as _zlib",
        "",
        "_BASE_SRC = _zlib.decompress(_b64.b85decode(",
        lines,
        ')).decode("utf-8")',
        "_BASE_NS = {}",
        'exec(compile(_BASE_SRC, "base_agent.py", "exec"), _BASE_NS)',
        '_BASE_AGENT = _BASE_NS["agent"]',
        'STATE = _BASE_NS.get("STATE", {})',
    ]
    out += v8[lo:hi]
    out += ["", "_EAGER_BANDS = {'MILK': (0.3, 99.0), 'STRAWBERRY': (0.3, 99.0), 'WOOL': (0.3, 99.0)}"]
    if a.no_eager:
        out += ["_EAGER_FROM = 720"]
    out += ["", "", "def agent(observation, configuration=None):", "    return _v6_agent(observation, configuration)", ""]
    if not a.no_tick:
        out += v8[tk:]
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "main.py"), "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
    print("wrote", os.path.join(a.out, "main.py"))


if __name__ == "__main__":
    main()
