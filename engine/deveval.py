r"""Rebuild the hybrid and play it against an opponent on several seeds (both seats), in parallel.

.venv\Scripts\python.exe engine\deveval.py [--opp research\panel\cha22\main.py] [--seeds 6] [--seed0 1]
"""
import argparse
import multiprocessing as mp
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)


def job(args):
    import fastarena
    a, b, seed = args
    r = fastarena.play((a, b, seed))
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opp", default=os.path.join(ROOT, "research", "panel", "cha22", "main.py"))
    ap.add_argument("--opening", default=os.path.join(ROOT, "research", "cands", "v5", "main.py"))
    ap.add_argument("--seeds", type=int, default=6)
    ap.add_argument("--seed0", type=int, default=1)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--switch", type=int, default=264)
    ap.add_argument("--out", default=os.path.join(ROOT, "research", "cands", "hyb"))
    a = ap.parse_args()
    import build_hybrid
    hyb = build_hybrid.build(a.opening, a.out, a.switch, os.path.join(HERE, "main.py"))
    jobs = []
    for s in range(a.seed0, a.seed0 + a.seeds):
        jobs.append((hyb, a.opp, s))
        jobs.append((a.opp, hyb, s))
    t0 = time.time()
    with mp.get_context("spawn").Pool(a.workers) as pool:
        res = pool.map(job, jobs)
    me, op, rows = [], [], []
    for r in res:
        if r["a"] == hyb:
            m, o = r["ra"], r["rb"]
        else:
            m, o = r["rb"], r["ra"]
        me.append(m or 0)
        op.append(o or 0)
        rows.append(f"seed {r['seed']:3d} seat {0 if r['a'] == hyb else 1}: hyb {m:>9.0f}  opp {o:>9.0f}  diff {m - o:+8.0f}  {r['status']}")
    print("\n".join(rows))
    n = len(me)
    wins = sum(1 for x, y in zip(me, op) if x > y)
    print(f"games {n}  hyb avg {sum(me) / n:.0f}  opp avg {sum(op) / n:.0f}  diff {(sum(me) - sum(op)) / n:+.0f}  "
          f"wins {wins}/{n}  ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
