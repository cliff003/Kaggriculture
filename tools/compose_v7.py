r"""Compose a v7-style agent: a build_v5.py output as the embedded base plus the wheat lead-sell block of v7b.

.venv\Scripts\python.exe tools\compose_v7.py BASE_MAIN_PY OUT_DIR [--layers-from research\cands\v7b\main.py]

The base's final `agent` is renamed `_v6_agent` and everything from the "# Everything above is the live v6" line of
the layers file (the _CFG block, gold/hybrid/layers.py wrap and the final agent) is appended unchanged.
"""
import argparse
import os

MARK = "# Everything above is the live v6"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("out")
    ap.add_argument("--layers-from", default=os.path.join("research", "cands", "v7b", "main.py"))
    a = ap.parse_args()
    base = open(a.base, encoding="utf-8").read().replace("\r\n", "\n")
    head = "def agent(observation, configuration=None):"
    assert base.count(head) == 1, "base must define exactly one module-level agent"
    base = base.replace(head, "def _v6_agent(observation, configuration=None):")
    layers = open(a.layers_from, encoding="utf-8").read().replace("\r\n", "\n")
    i = layers.index(MARK)
    code = base.rstrip("\n") + "\n\n\n" + layers[i:]
    compile(code, "main.py", "exec")
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "main.py"), "w", encoding="utf-8", newline="\n") as f:
        f.write(code)
    print("wrote", os.path.join(a.out, "main.py"), len(code))


if __name__ == "__main__":
    main()
