r"""Log every wheat fill of chosen steps in a recorded game, unit by unit (used for figure 03).

LOCAL ONLY: needs the recorded games under ../data/games (not in the repository) and kaggle-environments 1.32.7.

python docs/figures/rounds.py GAMES.jsonl.gz GAME_ID --team 42 --steps 300 301 [--cand AGENT_MAIN_PY]

Without --cand both seats replay their recorded actions (the game as it was played). With --cand our seat plays the
candidate code against the rival's recorded actions and the recorded shop order (a live-replay counterfactual).
Prints one JSON object: rewards, our seat, and per step the town's wheat consumption and the fills per slot and player.
"""
import argparse
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("games")
    ap.add_argument("game_id", type=int)
    ap.add_argument("--team", default="42")
    ap.add_argument("--steps", type=int, nargs="+", required=True)
    ap.add_argument("--cand")
    a = ap.parse_args()

    rec = None
    for line in gzip.open(a.games, "rt", encoding="utf-8"):
        r = json.loads(line)
        if r["id"] == a.game_id:
            rec = r
            break
    assert rec, f"game {a.game_id} not found"
    me = rec["teams"].index(a.team)

    import fastarena  # noqa: F401  (loads only the kaggriculture environment)
    import forceshops
    from cfreplay import tape_agent
    from kaggle_environments.envs.kaggriculture import kaggriculture as K

    steps = set(a.steps)
    log = {"cur": None, "slot": 0, "farms": None, "in_market": False}
    fills = []          # (step, slot, player, op, price)
    eaten = {}          # step -> wheat eaten by the town
    stock = {}          # step -> wheat stock at the start of the market

    orig_pm, orig_rp, orig_cu, orig_tc = K._process_market, K._refresh_prices, K._commit_unit, K._town_consume

    def process_market(state, env):
        o = state[0].observation
        log["cur"] = int(o.step)
        log["slot"] = 0
        log["farms"] = o.farms
        log["in_market"] = True
        if log["cur"] in steps:
            stock[log["cur"]] = o.market["inventory"]["WHEAT"]
        try:
            return orig_pm(state, env)
        finally:
            log["in_market"] = False

    def refresh_prices(market):
        if log["in_market"]:
            log["slot"] += 1
        return orig_rp(market)

    def commit_unit(op, item, price, farm, private, market, shed_capacity=100):
        ok = orig_cu(op, item, price, farm, private, market, shed_capacity)
        if ok and item == "WHEAT" and log["cur"] in steps and op in ("SELL", "BUY_PRODUCT"):
            player = 0 if farm is log["farms"][0] else 1
            fills.append((log["cur"], log["slot"], player, op, price))
        return ok

    def town_consume(env, state, step):
        before = state[0].observation.market["inventory"]["WHEAT"]
        r = orig_tc(env, state, step)
        if step in steps:
            eaten[step] = before - state[0].observation.market["inventory"]["WHEAT"]
        return r

    K._process_market, K._refresh_prices, K._commit_unit, K._town_consume = (
        process_market, refresh_prices, commit_unit, town_consume)

    if a.cand:
        forceshops.force(rec.get("shops"))
        ours = fastarena.load_agent(a.cand)
    else:
        ours = tape_agent(rec["acts"][me])
    theirs = tape_agent(rec["acts"][1 - me])
    agents = [ours, theirs] if me == 0 else [theirs, ours]
    res = fastarena.run_game(agents[0], agents[1], rec["seed"])

    out = {"game": a.game_id, "teams": rec["teams"], "our_seat": me, "live_rewards": rec["rewards"],
           "rewards": res["rewards"], "mode": "replay" if a.cand else "live", "steps": {}}
    for s in sorted(steps):
        rows = {}
        for st, slot, pl, op, price in fills:
            if st != s:
                continue
            k = (slot, pl, op)
            r = rows.setdefault(k, {"slot": slot, "who": "us" if pl == me else "rival", "op": op,
                                    "units": 0, "first": price, "last": price, "total": 0})
            r["units"] += 1
            r["last"] = price
            r["total"] += price
        out["steps"][str(s)] = {"stock_start": stock.get(s), "gap_start": (10000 - stock[s]) if s in stock else None,
                                "eaten": eaten.get(s), "day": s // 24, "hour": s % 24,
                                "fills": sorted(rows.values(), key=lambda r: (r["slot"], r["who"] != "rival"))}
    print(json.dumps(out))


if __name__ == "__main__":
    main()
