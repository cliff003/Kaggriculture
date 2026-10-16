r"""Counterfactual replay: our candidate agent against a live opponent's recorded actions, same seed and seat.

.venv\Scripts\python.exe tools\cfreplay.py GAMES.jsonl.gz TEAM CANDIDATE_MAIN_PY [--ids ID ...] [--workers 12] [--force-shops]

The opponent replays its recorded actions step for step, so it does not react to our changes; for
cha22-family opponents whose farm work follows the same route as ours, the farms evolve as they did
live and the result isolates the effect of our market-side changes. Running our own live code as the
candidate should reproduce the live result exactly (a check of the method).
"""
import argparse
import gzip
import json
import multiprocessing as mp
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASS = {"farmer": ["PASS"], "hands": [], "market": []}


def tape_agent(acts):
    tape = [a if isinstance(a, dict) else PASS for a in acts[1:]]

    def agent(obs, conf=None):
        t = int(obs["step"])
        a = tape[t] if 0 <= t < len(tape) else PASS
        return json.loads(json.dumps(a))
    return agent


def job(args):
    import fastarena
    rec, team, cand = args[:3]
    if len(args) > 3 and args[3]:
        import forceshops   # keep the live shop sequence even if our farm changes the day's weed draws
        forceshops.force(rec.get("shops"))
    me = rec["teams"].index(team)
    ours = fastarena.load_agent(cand)
    theirs = tape_agent(rec["acts"][1 - me])
    agents = [ours, theirs] if me == 0 else [theirs, ours]
    r = fastarena.run_game(agents[0], agents[1], rec["seed"])
    m, o = r["rewards"][me], r["rewards"][1 - me]
    live = rec["rewards"][me] - rec["rewards"][1 - me]
    return rec["id"], rec["teams"][1 - me], live, (m or 0) - (o or 0), m, o, r["status"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("games")
    ap.add_argument("team")
    ap.add_argument("cand")
    ap.add_argument("--ids", type=int, nargs="*")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--force-shops", action="store_true", help="unlock the live game's shops in its order")
    a = ap.parse_args()
    games = []
    for line in gzip.open(a.games, "rt", encoding="utf-8"):
        try:
            games.append(json.loads(line))
        except Exception:
            break
    games = [g for g in games if a.team in g["teams"] and (not a.ids or g["id"] in a.ids)]
    with mp.get_context("spawn").Pool(a.workers) as pool:
        res = pool.map(job, [(g, a.team, os.path.abspath(a.cand), a.force_shops) for g in games])
    flips_up = flips_down = 0
    tot_live = tot_cf = 0.0
    for gid, opp, live, cf, m, o, st in res:
        tot_live += live
        tot_cf += cf
        if live <= 0 < cf:
            flips_up += 1
        if cf <= 0 < live:
            flips_down += 1
        if not a.quiet:
            print(f"{gid} {opp[:22]:22s} live {live:+8.0f}  replay {cf:+8.0f}  change {cf - live:+7.0f}  {st}")
    n = len(res)
    wl = lambda xs: f"{sum(1 for x in xs if x > 0)}/{sum(1 for x in xs if x < 0)}/{sum(1 for x in xs if x == 0)}"
    print(f"games {n}  live W/L/T {wl([r[2] for r in res])}  replay W/L/T {wl([r[3] for r in res])}  "
          f"mean change {(tot_cf - tot_live) / max(1, n):+.0f}  flips up {flips_up} down {flips_down}")


if __name__ == "__main__":
    main()
