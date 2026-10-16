r"""Screen our submissions against a list of opponents with gstat (forced worlds, both seats) and summarize.

.venv\Scripts\python.exe gold\tools\screen_subs.py --subs A.py B.py --opps X.py Y.py [--seeds 8] [--tag pub]
Each pairing writes gold/tmp/<tag>_<sub>_vs_<opp>.json (skipped if present) and a summary table at the end.
"""
import argparse
import json
import os
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PY = (os.path.join(ROOT, ".venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(ROOT, ".venv", "bin", "python"))


def short(path):
    parts = os.path.normpath(path).split(os.sep)
    for p in reversed(parts[:-1]):
        if p not in ("from_tar", "agent", "v53_agent", "v55_agent"):
            return p[:48]
    return parts[-1]


def summary(js):
    d = json.load(open(js))
    gs = d["games"]
    ours = [g["rewards"][g["cand_side"]] for g in gs]
    opp = [g["rewards"][1 - g["cand_side"]] for g in gs]
    w = sum(1 for a, b in zip(ours, opp) if a > b)
    t = sum(1 for a, b in zip(ours, opp) if a == b)
    return len(gs), w, t, sum(ours) / len(gs), sum(opp) / len(gs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subs", nargs="+", required=True)
    ap.add_argument("--opps", nargs="+", required=True)
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--tag", default="scr")
    a = ap.parse_args()
    rows = []
    for opp in a.opps:
        for sub in a.subs:
            js = os.path.join(ROOT, "gold", "tmp", f"{a.tag}_{short(sub)}_vs_{short(opp)}.json")
            if not os.path.exists(js):
                subprocess.run([PY, "gold/tools/gstat.py", sub, opp, "--seeds", str(a.seeds), "--seed0", "50000",
                                "--both", "--workers", "12", "--worlds", "--json", js], cwd=ROOT,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(js):
                n, w, t, mo, mp = summary(js)
                rows.append((short(opp), short(sub), n, w, t, mo, mp))
                print(f"{short(sub):40s} vs {short(opp):48s} {w:2d}-{n - w - t:2d}-{t} ours {mo:8.0f} opp {mp:8.0f} diff {mo - mp:+7.0f}", flush=True)
            else:
                print(f"{short(sub)} vs {short(opp)}: FAILED", flush=True)


if __name__ == "__main__":
    main()
