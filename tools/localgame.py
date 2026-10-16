r"""Play one local game and save it as a harvest-format record, so econ.py can break it down.

.venv\Scripts\python.exe tools\localgame.py A_MAIN_PY B_MAIN_PY SEED OUT.jsonl.gz [--names A B]
then: .venv\Scripts\python.exe tools\econ.py OUT.jsonl.gz --id SEED
"""
import argparse
import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fastarena


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("seed", type=int)
    ap.add_argument("out")
    ap.add_argument("--names", nargs=2, default=None)
    a = ap.parse_args()
    names = a.names or [os.path.basename(os.path.dirname(os.path.abspath(p))) for p in (a.a, a.b)]
    r = fastarena.run_game(fastarena.load_agent(a.a), fastarena.load_agent(a.b), a.seed, record=True)
    h = r["history"]
    state = r["final_state"]
    rec = {"id": a.seed, "seed": a.seed, "teams": names, "rewards": r["rewards"],
           "shops": list(state[0].observation.town["unlocked_shops"]),
           "acts": [[None] + [h[t][i]["action"] for t in range(len(h))] for i in range(2)]}
    with gzip.open(a.out, "at", encoding="utf-8") as f:
        f.write(json.dumps(rec, separators=(",", ":")) + "\n")
    print("saved", a.out, names, r["rewards"])


if __name__ == "__main__":
    main()
