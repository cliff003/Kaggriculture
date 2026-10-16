r"""Run a batch of bench variants on Kaggle, two per kernel, and print a result table as kernels finish.

kgq.py BATCH_NAME AGENT OPP SEEDS VARIANTS_FILE [--per 2] [--extra FILE ...]
VARIANTS_FILE: one variant per line, `tag: k=v k=v ...` (JSON values; empty after the colon = defaults).
Results are appended to prod/kg/results.tsv (batch, tag, n, wins, me, opp, margin, se).
"""
import argparse
import os
import re
import shlex
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PY = (os.path.join(ROOT, ".venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(ROOT, ".venv", "bin", "python"))
KG = os.path.join(ROOT, "prod", "tools", "kgrun.py")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("batch")
    ap.add_argument("agent")
    ap.add_argument("opp")
    ap.add_argument("seeds")
    ap.add_argument("variants")
    ap.add_argument("--per", type=int, default=2)
    ap.add_argument("--extra", nargs="*", default=[])
    a = ap.parse_args()
    vs = []
    for line in open(a.variants, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        tag, _, sets = line.partition(":")
        vs.append((tag.strip(), sets.strip()))
    kernels = []
    for k in range(0, len(vs), a.per):
        name = f"{a.batch}{k // a.per}"
        cmds = []
        for tag, sets in vs[k:k + a.per]:
            c = f"python prod/tools/bench.py {a.agent} {a.opp} --seeds {a.seeds} -j 4 --tag {tag}"
            if sets:
                c += " --set " + " ".join(shlex.quote(x) for x in sets.split())
            cmds.append(c)
        args = [PY, KG, "push", name, "--include", "tools/fastarena.py", "prod/tools", a.agent, a.opp] + a.extra
        for c in cmds:
            args += ["--cmd", c]
        r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
        print(name, "pushed" if "successfully" in (r.stdout + r.stderr) else ("FAILED " + (r.stdout + r.stderr)[-300:]), flush=True)
        kernels.append(name)
    out = os.path.join(ROOT, "prod", "kg", "results.tsv")
    for name in kernels:
        subprocess.run([PY, KG, "wait", name, "--poll", "60"], cwd=ROOT, capture_output=True, text=True)
        d = os.path.join(ROOT, "prod", "kg", name, "out")
        for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if not (f.startswith("out_") and f.endswith(".txt")):
                continue
            first = open(os.path.join(d, f), encoding="utf-8", errors="replace").readline().strip()
            m = re.match(r"(\S+) .*n=(\d+) W (\d+) T \d+ me (\d+) opp (\d+) margin (-?\d+) \(se (\d+)\)", first)
            if m:
                row = [a.batch] + list(m.groups())
                print("\t".join(row), flush=True)
                open(out, "a", encoding="utf-8").write("\t".join(row) + "\n")
            else:
                print(name, f, "no result:", first[:200], flush=True)


if __name__ == "__main__":
    main()
