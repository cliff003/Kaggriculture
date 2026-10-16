r"""Audit production events of ongoing crops (strawberry, tomato) for one seat in a local game: how many were
fertilized (+2), plain (+1), lost to the 4-unit cap, or missed because the plant was not watered.
    .venv\Scripts\python.exe gold\front\fertaudit.py AGENT.py OPP.py SEED[,SEED...] [--seat 0]"""
import argparse
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "gold", "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("agent")
    ap.add_argument("opp")
    ap.add_argument("seeds")
    ap.add_argument("--seat", type=int, default=0)
    a = ap.parse_args()
    import fastarena
    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    tot = collections.Counter()
    CNT = {"f": 0}
    orig = K._daily_refresh_plants

    def refresh(farm, current_day, turns_per_day):
        CNT["f"] += 1
        seat = (CNT["f"] - 1) % 2
        if seat == a.seat:
            nd = current_day + 1
            for row in farm["tiles"]:
                for t in row:
                    if not isinstance(t, dict) or t.get("kind") != "PLANT":
                        continue
                    cd = K.CROPS[t["crop"]]
                    if not cd["ongoing"]:
                        continue
                    dsf = nd - t["planted_day"] - cd["first_yield_day"]
                    if dsf < 0 or dsf % cd["interval"] != 0 or dsf // cd["interval"] + 1 > cd["max_yield"]:
                        continue
                    crop = t["crop"]
                    if not t["watered_today"]:
                        tot[(crop, "unwatered")] += 1
                        continue
                    fert = t.get("fertilized_until_day", -1) >= current_day
                    add = 2 if fert else 1
                    room = cd["max_yield"] - t["yield_units"]
                    tot[(crop, "fert" if fert else "plain")] += 1
                    tot[(crop, "units")] += min(add, room)
                    tot[(crop, "capped")] += max(0, add - room)
        return orig(farm, current_day, turns_per_day)

    K._daily_refresh_plants = refresh
    seeds = [int(s) for s in a.seeds.split(",")]
    for seed in seeds:
        CNT["f"] = 0
        f = fastarena.load_agent(a.agent)
        g = fastarena.load_agent(a.opp)
        fns = [f, g] if a.seat == 0 else [g, f]
        r = fastarena.run_game(fns[0], fns[1], seed)
        print(seed, r["rewards"], flush=True)
    n = len(seeds)
    for crop in ("STRAWBERRY", "TOMATO"):
        print(crop, {k: round(tot[(crop, k)] / n, 1) for k in ("fert", "plain", "unwatered", "units", "capped")})


if __name__ == "__main__":
    main()
