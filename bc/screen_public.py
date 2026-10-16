r"""Screen many public agents against a reference agent (default v9live): K seeds x both seats each.

.venv\Scripts\python.exe bc\screen_public.py OUT.jsonl DIR [DIR ...] [--ref v9live] [--seeds 4] [--seed0 91000]

One worker handles one agent (loads it once), so slow imports are paid once. Results append to OUT (resumable).
"""
import argparse
import glob
import json
import multiprocessing as mp
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))


def job(args):
    path, ref, seeds = args
    import fastarena
    t0 = time.time()
    try:
        a = fastarena.load_agent(path)
        b = fastarena.load_agent(ref)
    except Exception as e:
        return {"agent": path, "error": f"load {type(e).__name__}: {e}"[:200]}
    games = []
    for s in seeds:
        for seat in (0, 1):
            try:
                agents = [a, b] if seat == 0 else [b, a]
                r = fastarena.run_game(agents[0], agents[1], s)
                games.append([s, seat, r["rewards"][seat], r["rewards"][1 - seat], r["errors"][seat], r["t_max"][seat]])
            except Exception as e:
                games.append([s, seat, None, None, 1, 0])
            if time.time() - t0 > 600:
                break
        if time.time() - t0 > 600:
            break
    return {"agent": path, "games": games}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--ref", default="v9live")
    ap.add_argument("--seeds", type=int, default=4)
    ap.add_argument("--seed0", type=int, default=91000)
    ap.add_argument("--workers", type=int, default=16)
    a = ap.parse_args()
    ref = next(os.path.join(ROOT, d, a.ref, "main.py") for d in ("research/cands", "research/panel", "submissions")
               if os.path.exists(os.path.join(ROOT, d, a.ref, "main.py")))
    done = set()
    if os.path.exists(a.out):
        done = {json.loads(l)["agent"] for l in open(a.out, encoding="utf-8")}
    paths = []
    for d in a.dirs:
        for p in glob.glob(os.path.join(d, "main.py")):
            if os.path.abspath(p) not in done:
                paths.append(os.path.abspath(p))
    seeds = list(range(a.seed0, a.seed0 + a.seeds))
    print(len(paths), "agents to screen against", a.ref, flush=True)
    with mp.get_context("spawn").Pool(a.workers) as pool, open(a.out, "a", encoding="utf-8") as f:
        for r in pool.imap_unordered(job, [(p, ref, seeds) for p in paths]):
            f.write(json.dumps(r) + "\n")
            f.flush()
            g = r.get("games") or []
            ok = [x for x in g if x[2] is not None]
            w = sum(1 for x in ok if x[2] > x[3])
            name = os.path.basename(os.path.dirname(r["agent"]))
            if r.get("error"):
                print(f"   {name[:60]:60s} ERROR {r['error'][:60]}", flush=True)
            else:
                mm = sum(x[2] - x[3] for x in ok) / max(1, len(ok))
                print(f"   {name[:60]:60s} {w}/{len(ok)} wins  mean margin {mm:+8.0f}", flush=True)


if __name__ == "__main__":
    main()
