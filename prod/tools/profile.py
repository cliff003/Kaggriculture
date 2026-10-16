r"""Behaviour profile of one team from recorded games (both seats replayed from their own actions).

profile.py GAMES.jsonl.gz TEAM [--max N] [--events OUT.json]
Prints per-day hands / composition / land, planting choices by day, market habits (sell hours and slots,
hires, animal and seed buys), animal fed/cared rates, crop harvest ages and fertilizer use.
--events saves the raw planting and purchase events for further study.
"""
import argparse
import collections
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "tools"))
import fastarena  # noqa: E402
from fidelity import tape_agent  # noqa: E402
from kaggle_environments.envs.kaggriculture import kaggriculture as K  # noqa: E402


def load(p):
    out = []
    with gzip.open(p, "rt", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    out.append(json.loads(line))
                except Exception:
                    break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("games")
    ap.add_argument("team")
    ap.add_argument("--max", type=int, default=500)
    ap.add_argument("--events", default="")
    a = ap.parse_args()
    recs = [r for r in load(a.games) if a.team in r["teams"]][:a.max]
    per_day = collections.defaultdict(collections.Counter)
    plant = collections.defaultdict(collections.Counter)
    sell_hour = collections.defaultdict(collections.Counter)
    sell_slot = collections.defaultdict(collections.Counter)
    buy = collections.defaultdict(collections.Counter)
    hires_hour = collections.Counter()
    land_day = collections.Counter()
    animal_rate = collections.defaultdict(lambda: [0, 0, 0])
    harv_age = collections.defaultdict(collections.Counter)
    fert_age = collections.defaultdict(collections.Counter)
    water_age = collections.defaultdict(collections.Counter)
    events = []
    money = collections.defaultdict(list)
    orig = K.interpreter
    for gi, r in enumerate(recs):
        me = r["teams"].index(a.team)

        def interp(state, env, me=me, gi=gi):
            o = state[0].observation
            if not (hasattr(o, "farms") and o.farms):
                return orig(state, env)
            st = o.get("step", 0)
            day, hour = st // 24, st % 24
            farm = o.farms[me]
            act = state[me].action or {}
            acts = [act.get("farmer") or ["PASS"]] + list(act.get("hands") or [])
            pos = [tuple(farm["farmer"])] + [tuple(h) for h in farm["hands"]]
            prices = dict(o.market["prices"])
            shops = list(o.town.get("unlocked_shops", []))
            for a_, p in zip(acts, pos):
                if not a_:
                    continue
                t = farm["tiles"][p[1]][p[0]]
                if a_[0] == "PLANT" and len(a_) > 1:
                    plant[day][a_[1]] += 1
                    events.append({"g": gi, "type": "plant", "day": day, "hour": hour, "crop": a_[1], "pos": p,
                                   "shops": shops, "prices": prices})
                if isinstance(t, dict) and t.get("kind") == "PLANT":
                    age = day - t["planted_day"]
                    if a_[0] == "HARVEST":
                        harv_age[t["crop"]][age] += 1
                    elif a_[0] == "FERTILIZE":
                        fert_age[t["crop"]][age] += 1
                    elif a_[0] == "WATER":
                        water_age[t["crop"]][age] += 1
            for k, o_ in enumerate(act.get("market") or []):
                if not o_:
                    continue
                if o_[0] == "SELL" and len(o_) >= 3:
                    sell_hour[o_[1]][hour] += o_[2]
                    sell_slot[o_[1]][k] += 1
                elif o_[0] == "HIRE":
                    hires_hour[hour] += 1
                elif o_[0] in ("BUY_ANIMAL", "BUY_SEED", "BUY_PRODUCT") and len(o_) >= 3:
                    buy[o_[0] + ":" + o_[1]][day] += o_[2]
                    if o_[0] != "BUY_PRODUCT":
                        events.append({"g": gi, "type": o_[0], "day": day, "hour": hour, "item": o_[1], "n": o_[2],
                                       "shops": shops, "prices": prices, "money": farm["money"]})
                elif o_[0] == "BUY_LAND":
                    land_day[day] += 1
            if hour == 23:
                c = collections.Counter()
                for row in farm["tiles"]:
                    for t in row:
                        if isinstance(t, dict):
                            if t.get("animal"):
                                c["A_" + t["animal"]] += 1
                                ar = animal_rate[t["animal"]]
                                ar[0] += 1
                                ar[1] += 1 if t.get("fed_today") else 0
                                ar[2] += 1 if t.get("cared_today") else 0
                            elif t.get("kind") == "PLANT":
                                c["P_" + t["crop"]] += 1
                c["hands"] = len(farm["hands"])
                c["quads"] = len(farm["unlocked_quadrants"])
                per_day[day].update(c)
                money[day].append(farm["money"])
            return orig(state, env)

        K.interpreter = interp
        try:
            fastarena.run_game(tape_agent(r["acts"][0]), tape_agent(r["acts"][1]), r["seed"])
        finally:
            K.interpreter = orig
    n = len(recs)
    mine = [r["rewards"][r["teams"].index(a.team)] for r in recs]
    theirs = [r["rewards"][1 - r["teams"].index(a.team)] for r in recs]
    print(f"{a.team}: {n} games; mean money {sum(mine) / n:.0f} vs opp {sum(theirs) / n:.0f}, "
          f"wins {sum(x > y for x, y in zip(mine, theirs))}")
    keys = ["hands", "quads", "A_COW", "A_SHEEP", "A_GOOSE", "P_WHEAT", "P_STRAWBERRY", "P_MELON", "P_TOMATO", "P_CARROT"]
    print("day   money " + " ".join(f"{k[-7:]:>7}" for k in keys) + "   planted today")
    for d in range(30):
        m = sum(money[d]) / max(1, len(money[d]))
        pl = " ".join(f"{c[:3]}{v / n:.1f}" for c, v in sorted(plant[d].items()))
        print(f"{d:3d} {m:7.0f} " + " ".join(f"{per_day[d][k] / n:7.1f}" for k in keys) + "   " + pl)
    print("land bought by day:", dict(sorted((d, round(v / n, 2)) for d, v in land_day.items())))
    print("hires per day by hour:", {h: round(v / n / 30, 2) for h, v in sorted(hires_hour.items())})
    print("animal fed%/cared%:", {k: (round(100 * v[1] / max(1, v[0])), round(100 * v[2] / max(1, v[0]))) for k, v in animal_rate.items()})
    for k in sorted(buy):
        tot = sum(buy[k].values()) / n
        by = " ".join(f"d{d}:{v / n:.1f}" for d, v in sorted(buy[k].items()) if v / n >= 0.05)
        print(f"buy {k:22s} {tot:7.1f}/game  {by[:300]}")
    for item in sorted(sell_hour):
        h = sell_hour[item]
        tot = sum(h.values())
        top = " ".join(f"h{x}:{100 * v / tot:.0f}%" for x, v in sorted(h.items()) if v / tot >= 0.04)
        sl = sell_slot[item]
        slt = sum(sl.values())
        print(f"sell {item:11s} {tot / n:6.0f}/game  hours {top}  slot0 {100 * sl[0] / max(1, slt):.0f}%")
    for c in sorted(set(harv_age) | set(water_age)):
        print(f"crop {c:11s} harvest ages {dict(sorted(harv_age[c].items()))}")
        print(f"                 fert ages {dict(sorted(fert_age[c].items()))}")
        print(f"                water ages {dict(sorted(water_age[c].items()))}")
    if a.events:
        json.dump(events, open(a.events, "w"))


if __name__ == "__main__":
    main()
