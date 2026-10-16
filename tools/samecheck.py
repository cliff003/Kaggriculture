r"""Check that two builds of an agent play identically: same opponent, seeds and seats, exact rewards.

.venv\Scripts\python.exe tools\samecheck.py A_MAIN_PY B_MAIN_PY OPP_MAIN_PY [--seeds 30000 30001 ...]
"""
import argparse
import multiprocessing as mp
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def job(args):
    import fastarena
    me, opp, seed, seat = args
    a, b = fastarena.load_agent(me), fastarena.load_agent(opp)
    r = fastarena.run_game(a, b, seed) if seat == 0 else fastarena.run_game(b, a, seed)
    return r["rewards"][seat], r["rewards"][1 - seat]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("opp")
    ap.add_argument("--seeds", type=int, nargs="+", default=[30000, 30016, 30042])
    a = ap.parse_args()
    jobs = [(os.path.abspath(p), os.path.abspath(a.opp), s, seat) for p in (a.a, a.b) for s in a.seeds for seat in (0, 1)]
    with mp.get_context("spawn").Pool(min(12, len(jobs))) as pool:
        res = pool.map(job, jobs)
    half = len(res) // 2
    same = res[:half] == res[half:]
    for (x, y) in zip(res[:half], res[half:]):
        print(x, y, "same" if x == y else "DIFF")
    print("identical:", same)


if __name__ == "__main__":
    main()
