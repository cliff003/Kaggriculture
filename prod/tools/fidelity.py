r"""Replay recorded games with AGENT in TEAM's seat against the opponent's recorded actions.

fidelity.py AGENT GAMES.jsonl.gz TEAM [--ids id,id] [--max N]
Prints recorded vs reproduced money for TEAM's seat (and the opponent's) per game.
"""
import argparse
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "tools"))
import fastarena  # noqa: E402


def load(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def tape_agent(acts):
    def ag(obs, cfg=None):
        st = obs.get("step", 0) if hasattr(obs, "get") else obs["step"]
        a = acts[st + 1] if st + 1 < len(acts) else None
        return a if isinstance(a, dict) else {"farmer": ["PASS"], "hands": [], "market": []}
    return ag


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("agent")
    ap.add_argument("games")
    ap.add_argument("team")
    ap.add_argument("--ids", default="")
    ap.add_argument("--max", type=int, default=20)
    a = ap.parse_args()
    ids = set(int(x) for x in a.ids.split(",") if x)
    recs = [r for r in load(a.games) if a.team in r["teams"] and (not ids or r["id"] in ids)][:a.max]
    fa = fastarena.load_agent(a.agent)
    tot = [0, 0, 0, 0]
    for r in recs:
        me = r["teams"].index(a.team)
        opp = tape_agent(r["acts"][1 - me])
        if me == 0:
            res = fastarena.run_game(fa, opp, r["seed"])
        else:
            res = fastarena.run_game(opp, fa, r["seed"])
        got = res["rewards"]
        print(f"{r['id']} seat {me} shops {r['shops'][:2]} recorded me {r['rewards'][me]:.0f} opp {r['rewards'][1 - me]:.0f}"
              f" | reproduced me {got[me]:.0f} opp {got[1 - me]:.0f}")
        tot[0] += r["rewards"][me]
        tot[1] += got[me]
        tot[2] += r["rewards"][1 - me]
        tot[3] += got[1 - me]
    n = max(1, len(recs))
    print(f"mean recorded me {tot[0] / n:.0f} reproduced {tot[1] / n:.0f} | opp recorded {tot[2] / n:.0f} reproduced {tot[3] / n:.0f}")


if __name__ == "__main__":
    main()
