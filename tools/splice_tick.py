r"""Append the TICK layer of a v8 build to another team-42 agent (the TICK block is self-contained).

.venv\Scripts\python.exe tools\splice_tick.py TICK_SOURCE_MAIN_PY TARGET_MAIN_PY OUT_DIR

TICK_SOURCE is e.g. submissions\v8_own_cha22_tick_guard10\main.py; the block from the "Team 42 TICK layer" header to
the end of that file is appended to TARGET (which must not already carry a TICK layer).
"""
import os
import sys

MARK = "# ---------------------------------------------------------------------------\n# Team 42 TICK layer"


def main():
    src, target, out = sys.argv[1], sys.argv[2], sys.argv[3]
    tick = open(src, "rb").read().decode("utf-8").replace("\r\n", "\n")
    base = open(target, "rb").read().decode("utf-8").replace("\r\n", "\n")
    assert MARK in tick and MARK not in base
    code = base.rstrip("\n") + "\n\n" + tick[tick.index(MARK):]
    compile(code, "main.py", "exec")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "main.py"), "wb") as f:
        f.write(code.encode("utf-8"))
    print("wrote", os.path.join(out, "main.py"))


if __name__ == "__main__":
    main()
