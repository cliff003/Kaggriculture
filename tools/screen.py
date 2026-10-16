r"""Quick screen of candidate agents against a fixed panel on the same seeds, both seats.

.venv\Scripts\python.exe tools\screen.py CAND_DIR [CAND_DIR ...] [--opps cha22 morewheat v15stack v5]
                                          [--seeds 30] [--seed0 30000] [--workers 12]

Each candidate plays research/panel/<opp>/main.py (or research/cands/<opp>/main.py) on every seed from
both seats; results go to results/screen_<cand>.jsonl (resumable). Prints W/L/T, score rate and mean
margin per opponent, and per-seed-cluster standard error of the mean margin.
"""
import argparse
import json
import math
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = (os.path.join(ROOT, ".venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(ROOT, ".venv", "bin", "python"))


def agent_path(name):
    for d in ("research/panel", "research/cands", "data/public/agents"):
        p = os.path.join(ROOT, d, name, "main.py")
        if os.path.exists(p):
            return p
    raise SystemExit(f"no agent {name}")


def summarize(path, cand):
    per = {}
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        a, b = r["a"].replace("\\", "/").split("/")[-2], r["b"].replace("\\", "/").split("/")[-2]
        if a == cand:
            opp, m = b, (r["ra"] or 0) - (r["rb"] or 0)
        elif b == cand:
            opp, m = a, (r["rb"] or 0) - (r["ra"] or 0)
        else:
            continue
        per.setdefault(opp, {}).setdefault(r["seed"], []).append(m)
    rows = []
    for opp, seeds in sorted(per.items()):
        ms = [m for v in seeds.values() for m in v]
        w, l, t = sum(m > 0 for m in ms), sum(m < 0 for m in ms), sum(m == 0 for m in ms)
        means = [sum(v) / len(v) for v in seeds.values()]
        mu = sum(means) / len(means)
        se = math.sqrt(sum((x - mu) ** 2 for x in means) / max(1, len(means) - 1) / len(means))
        rows.append((opp, len(ms), w, l, t, (w + 0.5 * t) / len(ms), mu, se))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cands", nargs="+")
    ap.add_argument("--opps", nargs="+", default=["cha22", "morewheat", "v15stack", "v5"])
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--seed0", type=int, default=30000)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--tag", default="screen", help="results/<tag>_<cand>.jsonl")
    a = ap.parse_args()
    for cand in a.cands:
        cp = agent_path(cand)
        out = os.path.join(ROOT, "results", f"{a.tag}_{cand}.jsonl")
        cmd = [PY, os.path.join(ROOT, "tools", "rr.py"), "--vs", cp, "--agents", cp] + [agent_path(o) for o in a.opps] + \
              ["--seeds", str(a.seeds), "--seed0", str(a.seed0), "--both", "--workers", str(a.workers), "--resume",
               "--out", out]
        subprocess.run(cmd, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"== {cand}")
        for opp, n, w, l, t, sr, mu, se in summarize(out, cand):
            if opp in a.opps:
                print(f"  {opp:12s} {n:4d} games  {w:3d}/{l:3d}/{t:3d}  score {sr:5.1%}  margin {mu:+7.0f} (se {se:4.0f})")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
