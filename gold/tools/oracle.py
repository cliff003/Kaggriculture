r"""Oracle diagnostic: run a variant of gold/agent/main.py that follows cha22's recorded daily layouts
(gold/tmp/cha22_plans.json) on the forced worlds, and compare with the oracle baseline.

.venv\Scripts\python.exe gold\tools\oracle.py NAME ["old=>new" ...] [--base g036O] [--seeds 48]
"""
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PY = (os.path.join(ROOT, ".venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(ROOT, ".venv", "bin", "python"))
BS = chr(92)


def main():
    args = sys.argv[1:]
    seeds, base = "48", "g036O"
    for flag in ("--seeds", "--base"):
        if flag in args:
            i = args.index(flag)
            val = args[i + 1]
            del args[i:i + 2]
            if flag == "--seeds":
                seeds = val
            else:
                base = val
    name, reps = args[0], args[1:]
    src = open(os.path.join(ROOT, "gold", "agent", "main.py"), encoding="utf-8").read()
    src = src.replace('DEBUG = bool(os.environ.get("GOLD_DEBUG"))', "DEBUG = False", 1)
    for r in reps:
        old, new = r.split("=>", 1)
        old = old.replace(BS + "n", chr(10))
        new = new.replace(BS + "n", chr(10))
        n = src.count(old)
        if n != 1:
            sys.exit(f"replacement {old!r} matches {n} times")
        src = src.replace(old, new)
    out = os.path.join(ROOT, "gold", "builds", name)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "main.py"), "w", encoding="utf-8").write(src)
    js = f"gold/tmp/{name}_w{seeds}.json"
    env = dict(os.environ, GOLD_ORACLE=os.path.join(ROOT, "gold", "tmp", "cha22_plans.json"))
    subprocess.run([PY, "gold/tools/gstat.py", f"gold/builds/{name}/main.py", "research/panel/cha22/main.py",
                    "--seeds", seeds, "--seed0", "50000", "--both", "--workers", "12", "--worlds", "--json", js],
                   cwd=ROOT, check=True, stdout=subprocess.DEVNULL, env=env)
    subprocess.run([PY, "gold/tools/cmp.py", f"gold/tmp/{base}_w{seeds}.json", js], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
