r"""Check candidate agents against a team's recorded games: seat the candidate in the team's seat, replay the
opponent's recorded actions, and report how many leading steps match the recorded actions exactly.

famcheck.py CANDIDATES.txt TEAM [TEAM ...] [--games N]
"""
import argparse
import glob
import gzip
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PY = (os.path.join(ROOT, ".venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(ROOT, ".venv", "bin", "python"))

RUN = r'''
import json, sys, os
sys.path.insert(0, r"%(tools)s")
sys.path.insert(0, r"%(ptools)s")
import fastarena
path = os.path.abspath(sys.argv[1]); rec = json.load(open(sys.argv[2])); me = int(sys.argv[3])
os.chdir(os.path.dirname(path)); sys.path.insert(0, os.path.dirname(path))
fa = fastarena.load_agent(path)
opp_acts = rec["acts"][1 - me]
mine = rec["acts"][me]
def oppf(obs, cfg=None):
    st = obs["step"]
    a = opp_acts[st + 1] if st + 1 < len(opp_acts) else None
    return a if isinstance(a, dict) else {"farmer": ["PASS"], "hands": [], "market": []}
first = [None]
same_fh = [0]
def cand(obs, cfg=None):
    a = fa(obs, cfg)
    st = obs["step"]
    ref = mine[st + 1] if st + 1 < len(mine) else None
    if isinstance(ref, dict) and first[0] is None:
        if json.dumps([a.get("farmer"), a.get("hands"), a.get("market")], sort_keys=True) != json.dumps([ref.get("farmer"), ref.get("hands"), ref.get("market")], sort_keys=True):
            first[0] = st
    if isinstance(ref, dict) and json.dumps([a.get("farmer"), a.get("hands")]) == json.dumps([ref.get("farmer"), ref.get("hands")]):
        same_fh[0] += 1
    if first[0] is not None and st > first[0] + 48:
        raise SystemExit(0)
    return a
agents = [cand, oppf] if me == 0 else [oppf, cand]
try:
    fastarena.run_game(agents[0], agents[1], rec["seed"])
except SystemExit:
    pass
print("RES", first[0], same_fh[0])
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cands")
    ap.add_argument("teams", nargs="+")
    ap.add_argument("--games", type=int, default=2)
    a = ap.parse_args()
    recs = []
    for f in glob.glob(os.path.join(ROOT, "data", "games", "*.jsonl.gz")) + glob.glob(os.path.join(ROOT, "gold", "front", "*.jsonl.gz")):
        try:
            for line in gzip.open(f, "rt", encoding="utf-8"):
                if not line.strip():
                    continue
                r = json.loads(line)
                for t in a.teams:
                    if t in r.get("teams", []) and "acts" in r and sum(1 for x in recs if x[0] == t) < a.games:
                        recs.append((t, r))
        except Exception:
            pass
    tmp = os.path.join(ROOT, "prod", "kg", "famcheck_rec")
    os.makedirs(tmp, exist_ok=True)
    code = RUN % {"tools": os.path.join(ROOT, "tools"), "ptools": os.path.join(ROOT, "prod", "tools")}
    for cand in [l.strip() for l in open(a.cands, encoding="utf-8") if l.strip()]:
        out = []
        for t, r in recs:
            me = r["teams"].index(t)
            rp = os.path.join(tmp, f"{r['id']}.json")
            json.dump(r, open(rp, "w"))
            try:
                p = subprocess.run([PY, "-c", code, cand, rp, str(me)], capture_output=True, text=True, timeout=300)
                res = [x for x in p.stdout.splitlines() if x.startswith("RES")]
                out.append(f"{t[:10]}:{res[0][4:] if res else 'err'}")
            except subprocess.TimeoutExpired:
                out.append(f"{t[:10]}:timeout")
        print(os.path.relpath(cand, ROOT)[:110], " | ".join(out), flush=True)


if __name__ == "__main__":
    main()
