r"""Item split of "our executor on a recorded team's plan" vs "the recorded team itself", in the same games against the
same recorded opponent (team 42 research, 9/29).

    .venv/bin/python prod/oracle/gap_tape.py CAND_MAIN.py [--n 30] [--set JSON]

For each game: (a) the live game re-simulated from both tapes, (b) the candidate following the team's plan (oracle events,
hires, land days, backlog 3) in its seat against the opponent's tape. Revenue and units per item, for us and the opponent,
averaged per game.
"""
import argparse
import collections
import gzip
import json
import multiprocessing as mp
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ITEMS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]


def job(args):
    cand, plan, rec, extra = args
    sys.path.insert(0, os.path.join(ROOT, "prod", "tools"))
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import acct
    import fastarena
    import forceshops
    from cfreplay import tape_agent
    seat = plan["seat"]
    out = {}
    for mode in ("live", "cand"):
        forceshops.force(plan["shops"])
        acct._CUR["log"] = []
        acct._CUR["farms"] = None
        fns = [tape_agent(rec["acts"][0]), tape_agent(rec["acts"][1])]
        if mode == "cand":
            fa = fastarena.load_agent(cand)
            ov = {"oracle": plan["events"], "oracle_hires": plan["hires"], "oracle_backlog": 3, "land_last": 29,
                  "land_days": [plan["land"].get("NE", 99), plan["land"].get("SW", 99), plan["land"].get("SE", 99)]}
            ov.update(extra)
            fa.__globals__["STATE"]["_override"] = ov
            fns[seat] = fa
        r = fastarena.run_game(fns[0], fns[1], plan["seed"])
        agg = collections.defaultdict(float)
        for step, pl, op, item, price in acct._CUR["log"]:
            who = "me" if pl == seat else "opp"
            if op == "SELL":
                agg[f"{who}|rev|{item}"] += price
                agg[f"{who}|units|{item}"] += 1
            elif op in ("HIRE", "LAND"):
                agg[f"{who}|spend|{op}"] += price
            else:
                agg[f"{who}|spend|{op}:{item}"] += price
        agg["me|money"] = r["rewards"][seat]
        agg["opp|money"] = r["rewards"][1 - seat]
        out[mode] = dict(agg)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cand")
    ap.add_argument("--ref", default="prod/oracle/ref_unreal.json")
    ap.add_argument("--tapes", default="research/carrera/tapes/unreal_56618268.jsonl.gz")
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--set", default="{}")
    ap.add_argument("-j", type=int, default=9)
    a = ap.parse_args()
    plans = json.load(open(os.path.join(ROOT, a.ref)))
    recs = {}
    for line in gzip.open(os.path.join(ROOT, a.tapes), "rt", encoding="utf-8"):
        r = json.loads(line)
        if str(r["id"]) in plans:
            recs[str(r["id"])] = r
    keys = sorted(recs)[:a.n]
    cand = os.path.join(ROOT, a.cand)
    with mp.get_context("spawn").Pool(a.j) as pool:
        res = pool.map(job, [(cand, plans[k], recs[k], json.loads(a.set)) for k in keys])
    n = len(res)
    avg = {m: collections.defaultdict(float) for m in ("live", "cand")}
    for r in res:
        for m in ("live", "cand"):
            for k, v in r[m].items():
                avg[m][k] += v / n
    L, C = avg["live"], avg["cand"]
    print(f"games {n}: recorded team money {L['me|money']:.0f} vs ours {C['me|money']:.0f}; opponent {L['opp|money']:.0f} -> {C['opp|money']:.0f}")
    print(f"{'item':11s} {'team rev':>9s} {'our rev':>8s} {'diff':>7s} | {'team u':>6s} {'our u':>6s} | {'opp rev live':>12s} {'opp rev vs us':>13s} {'diff':>7s}")
    for it in ITEMS:
        tr, cr = L[f"me|rev|{it}"], C[f"me|rev|{it}"]
        orl, orc = L[f"opp|rev|{it}"], C[f"opp|rev|{it}"]
        print(f"{it:11s} {tr:9.0f} {cr:8.0f} {cr - tr:+7.0f} | {L[f'me|units|{it}']:6.0f} {C[f'me|units|{it}']:6.0f} | {orl:12.0f} {orc:13.0f} {orc - orl:+7.0f}")
    keys_s = sorted({k for k in list(L) + list(C) if k.startswith("me|spend|")})
    print("our spend vs the team's:", {k.split("|")[2]: (round(L[k]), round(C[k])) for k in keys_s})


if __name__ == "__main__":
    main()
