r"""Local panel for V10_CarreraGT candidates: every path plays every rival on the same random shop worlds, seats
alternating, with per-rival paired comparison against the first path (the rivals react, unlike tape replays).

.venv/bin/python research/carrera/panel.py BASE.py CAND.py [CAND.py ...] [--rivals a,b,c] [--worlds 30]
                                            [--seed 2026092801] [--workers 8] --out OUT.jsonl

Rivals are research/panel/<name>/main.py. Results are appended to OUT (resumable: finished games are skipped).
PYTHONHASHSEED is fixed to 0 in the workers.
"""
import argparse
import collections
import hashlib
import json
import multiprocessing as mp
import os
import random
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
SHOPS = ["BAKERY", "PIZZA_SHOP", "BRUNCH_SPOT", "YARN_STORE", "ICE_CREAM_SHOP", "PET_CAFE", "SMOOTHIE_SHOP", "FARMERS_MARKET"]
DEFAULT = ("cha22,emu_eager,emu_eager_m,morewheat,rescue,herdsafe_race,v15stack,emu_tick0,"
           "emu_tick3,emu_prebuy0,emu_antifade,emu_antifade2,emu_sw8")


def run(job):
    import fastarena
    import forceshops
    rival, rpath, path, seed, shops, me = job
    forceshops.force(shops)
    fns = [fastarena.load_agent(path), fastarena.load_agent(rpath)]
    if me:
        fns.reverse()
    r = fastarena.run_game(*fns, seed)
    return {"rival": rival, "path": path, "seed": seed, "seat": me, "status": r["status"],
            "margin": r["rewards"][me] - r["rewards"][1 - me], "money": r["rewards"][me]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--rivals", default=DEFAULT)
    ap.add_argument("--worlds", type=int, default=30)
    ap.add_argument("--seed", type=int, default=2026092801)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.environ["PYTHONHASHSEED"] = "0"
    rivals = {n: os.path.join(ROOT, "research", "panel", n, "main.py") for n in a.rivals.split(",")}
    rng = random.Random(a.seed)
    worlds = [(a.seed + i, [rng.choice(SHOPS) for _ in range(8)], i % 2) for i in range(a.worlds)]
    paths = [os.path.abspath(p) for p in a.paths]
    done = set()
    if os.path.exists(a.out):
        for line in open(a.out):
            d = json.loads(line)
            done.add((d["rival"], d["path"], d["seed"]))
    jobs = [(n, rp, p, s, sh, me) for s, sh, me in worlds for n, rp in rivals.items() for p in paths if (n, p, s) not in done]
    print(f"{len(worlds)} worlds x {len(rivals)} rivals x {len(paths)} paths; {len(jobs)} games to play", flush=True)
    with mp.get_context("spawn").Pool(a.workers, maxtasksperchild=20) as pool, open(a.out, "a") as fh:
        for k, r in enumerate(pool.imap_unordered(run, jobs, chunksize=1)):
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            if (k + 1) % 100 == 0:
                print(f"   {k + 1}/{len(jobs)}", flush=True)
    res = [json.loads(l) for l in open(a.out)]
    seeds = {s for s, _, _ in worlds}
    res = [r for r in res if r["seed"] in seeds and r["path"] in paths and r["rival"] in rivals]
    key = lambda r: (r["rival"], r["seed"])
    base = {key(r): r["margin"] for r in res if r["path"] == paths[0]}
    for p in paths:
        sub = [r for r in res if r["path"] == p and key(r) in base]
        name = os.path.relpath(p, ROOT)
        bad = sum(r["status"] != ["DONE", "DONE"] for r in sub)
        print(f"\n{name} [{hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]}]: {len(sub)} games, "
              f"wins {sum(r['margin'] > 0 for r in sub)}, mean change {st.mean(r['margin'] - base[key(r)] for r in sub):+.0f}, "
              f"flips up {sum(base[key(r)] <= 0 < r['margin'] for r in sub)} down {sum(r['margin'] <= 0 < base[key(r)] for r in sub)}, not DONE {bad}")
        by = collections.defaultdict(list)
        for r in sub:
            by[r["rival"]].append(r)
        print("   " + "  ".join(f"{n}: {sum(r['margin'] > 0 for r in rs)}/{len(rs)} {st.mean(r['margin'] - base[key(r)] for r in rs):+.0f}"
                              for n, rs in sorted(by.items())))


if __name__ == "__main__":
    main()
