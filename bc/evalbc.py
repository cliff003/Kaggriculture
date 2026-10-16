r"""Evaluate the BC agent: solo (vs PASS) and vs panel agents on fresh seeds, both seats.
.venv\Scripts\python.exe bc\evalbc.py WEIGHTS.npz [--opps cha22 v9live] [--seeds 10] [--seed0 90000]"""
import argparse, multiprocessing as mp, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "bc"))


def job(args):
    w, opp, seed, seat = args
    os.environ["BC_WEIGHTS"] = w
    import fastarena, policy
    pas = lambda obs, conf=None: {"farmer": ["PASS"], "hands": [], "market": []}
    o = pas if opp == "PASS" else fastarena.load_agent(next(os.path.join(ROOT, d, opp, "main.py") for d in (
        "research/panel", "research/cands") if os.path.exists(os.path.join(ROOT, d, opp, "main.py"))))
    agents = [policy.agent, o] if seat == 0 else [o, policy.agent]
    r = fastarena.run_game(agents[0], agents[1], seed)
    return opp, seed, seat, r["rewards"][seat] or 0, r["rewards"][1 - seat] or 0, r["errors"][seat]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("w"); ap.add_argument("--opps", nargs="+", default=["PASS", "cha22", "v9live"])
    ap.add_argument("--seeds", type=int, default=10); ap.add_argument("--seed0", type=int, default=90000)
    a = ap.parse_args()
    jobs = [(os.path.abspath(a.w), o, s, seat) for o in a.opps for s in range(a.seed0, a.seed0 + a.seeds) for seat in (0, 1)]
    with mp.get_context("spawn").Pool(16) as pool:
        res = pool.map(job, jobs)
    for o in a.opps:
        rows = [r for r in res if r[0] == o]
        w = sum(1 for r in rows if r[3] > r[4])
        print(f"vs {o:8s} games {len(rows):3d}  wins {w:3d}  our money {sum(r[3] for r in rows) / len(rows):9.0f}  "
              f"theirs {sum(r[4] for r in rows) / len(rows):9.0f}  errors {sum(r[5] for r in rows)}")
