r"""Assemble prod/agents/p6/main.py from its parts and self-check it (team 42 research, phase 2 production agent).

    .venv/bin/python prod/agents/p6/build.py

main.py = part0.py + part1.py (+ part2.py when present), LF line endings. Checks: compiles, loads in a fresh
namespace, the last callable in module order is `agent` (the Kaggle loader calls the last callable), and no local
machine paths appear in the source.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PARTS = ["part0.py", "part1.py", "part2.py"]


def main():
    src = ""
    for name in PARTS:
        path = os.path.join(HERE, name)
        if os.path.exists(path):
            part = open(path, encoding="utf-8").read().replace("\r\n", "\n")
            src += part if part.endswith("\n") else part + "\n"
    assert "/Users/" not in src and "C:\\Users" not in src, "local path in source"
    code = compile(src, "main.py", "exec")
    ns = {"__name__": "p6_check"}
    exec(code, ns)
    last = [v for v in ns.values() if callable(v)][-1]
    assert getattr(last, "__name__", "") == "agent", f"last callable is {last!r}, not agent"
    out = os.path.join(HERE, "main.py")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(src)
    print("wrote", out, len(src.encode("utf-8")), "bytes")


if __name__ == "__main__":
    sys.exit(main())
