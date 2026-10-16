"""Build a single-file agent: gold/builds/<name>/main.py = body.py + glue.py with the executor source inlined.

    .venv\\Scripts\\python.exe gold\\newagent\\build.py n001 [KEY=VALUE ...]

KEY=VALUE rewrites a top-level constant (first line that starts with "KEY = ").
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def main():
    name = sys.argv[1]
    body = open(os.path.join(HERE, "body.py"), encoding="utf-8").read()
    glue_name = os.environ.get("GLUE", "d1glue.py")
    glue = open(os.path.join(HERE, glue_name), encoding="utf-8").read()
    ex = open(os.path.join(HERE, "executor.py"), encoding="utf-8").read()
    assert "'''" not in ex
    # drop body's own agent() so the glue's agent() is the last callable
    i = body.rindex("\ndef agent(obs, config=None):")
    body = body[:i] + "\n"
    glue = glue.replace("_EXEC_SRC = None ", "_EXEC_SRC = r'''" + ex + "''' ", 1)
    src = body + glue
    for kv in sys.argv[2:]:
        k, v = kv.split("=", 1)
        src, n = re.subn(r"(?m)^" + re.escape(k) + r" = .*$", lambda m: k + " = " + v, src, count=1)
        assert n == 1, k
    out = os.path.join(ROOT, "gold", "builds", name)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "main.py"), "w", encoding="utf-8").write(src)
    print(os.path.join(out, "main.py"))


if __name__ == "__main__":
    main()
