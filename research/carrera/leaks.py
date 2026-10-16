r"""Money leaks of team 42 in harvested live games, by exact re-simulation of both tapes (tools/econ.py hooks).

.venv/bin/python research/carrera/leaks.py TAPES.jsonl.gz [--workers 8] [--out research/carrera/leaks.json]

Per game and side: final money, sales and purchases by item, hires, units lost to a full shed (valued at the
quote of that step), stock left unsold at the end (shed plus carried, valued at the final quotes), and farm
snapshots. "mirror" marks opponents whose farm equals ours at the end of day 8 (same cha22 route early on).
Prints a summary of where close losses (margin -3000..0) lose money relative to the opponent.
"""
import argparse
import collections
import json
import multiprocessing as mp
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))


def resim(rec):
    import econ
    K = econ.K
    env = econ.make("kaggriculture", configuration={"episodeSteps": 720, "seed": rec["seed"]}, debug=False)
    env.reset(2)
    state = env.state
    econ._CUR.update(log=[], farms=state[0].observation.farms, privates=[s.observation.private for s in state],
                     prices=state[0].observation.market["prices"])
    days = [[], []]
    n = len(rec["acts"][0])
    for t in range(719):
        econ._CUR["step"] = t
        for i in range(2):
            a = rec["acts"][i][t + 1] if t + 1 < n else None
            state[i].action = a if isinstance(a, dict) else None
        K.interpreter(state, env)
        state[0].observation.step = t + 1
        if (t + 1) % 24 == 0:
            for i in range(2):
                f = state[0].observation.farms[i]
                days[i].append({"money": f["money"], "tiles": dict(econ.tiles(f)),
                                "shed": sum(state[i].observation.private["shed"].values())})
    prices = dict(state[0].observation.market["prices"])
    out = []
    for i in range(2):
        priv = state[i].observation.private
        left = collections.Counter({k: v for k, v in priv["shed"].items() if v > 0})
        for inv in priv["inventories"]:
            left.update({k: v for k, v in inv.items() if v > 0})
        sales = collections.defaultdict(lambda: [0, 0.0])
        late = collections.defaultdict(float)   # revenue on days 26-29
        buys = collections.Counter()
        lost = collections.Counter()
        hire = [0.0] * 30
        for step, p, op, item, price in econ._CUR["log"]:
            if p != i:
                continue
            if op == "SELL":
                sales[item][0] += 1
                sales[item][1] += price
                if step >= 26 * 24:
                    late[item] += price
            elif op == "LOST":
                lost[item] += price
            elif op == "HIRE":
                hire[step // 24] += price
            elif op == "LAND":
                buys["LAND"] += price
            else:
                buys[op.replace("BUY_", "") + ":" + item] += price
        out.append({"money": state[0].observation.farms[i]["money"], "sales": dict(sales), "late": dict(late),
                    "buys": dict(buys), "lost": dict(lost), "hire": hire, "days": days[i],
                    "left": dict(left), "left_value": sum(v * prices.get(k, 0) for k, v in left.items())})
    return out


def job(rec):
    try:
        r = resim(rec)
    except Exception as e:  # keep going; report the failure
        return {"id": rec["id"], "error": repr(e)}
    me = rec["teams"].index("42")
    us, op = r[me], r[1 - me]
    mirror = us["days"][8]["tiles"] == op["days"][8]["tiles"] if len(us["days"]) > 8 else False
    return {"id": rec["id"], "opp": rec["teams"][1 - me], "seat": me, "shops": rec["shops"],
            "server": [rec["rewards"][me], rec["rewards"][1 - me]], "us": us, "op": op, "mirror": mirror}


def item_net(side):
    """Net cash by item: sales minus purchases of that product/seed/animal (animals mapped to their product)."""
    net = collections.Counter()
    for k, (u, rev) in side["sales"].items():
        net[k] += rev
    amap = {"COW": "MILK", "SHEEP": "WOOL", "GOOSE": "EGG"}
    for k, v in side["buys"].items():
        if k == "LAND":
            net["LAND"] -= v
            continue
        kind, item = k.split(":")
        net[amap.get(item, item) if kind == "ANIMAL" else item] -= v
    net["HIRE"] -= sum(side["hire"])
    return net


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tapes")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", default=os.path.join(HERE, "leaks.json"))
    a = ap.parse_args()
    import gzip
    recs = [json.loads(l) for l in gzip.open(a.tapes, "rt", encoding="utf-8") if l.strip()]
    recs = [r for r in recs if "42" in r["teams"]]
    with mp.get_context("spawn").Pool(a.workers) as pool:
        res = pool.map(job, recs, chunksize=1)
    bad = [r for r in res if "error" in r]
    res = [r for r in res if "error" not in r]
    json.dump(res, open(a.out, "w"))
    mism = [r["id"] for r in res if (round(r["us"]["money"]), round(r["op"]["money"])) != tuple(map(round, r["server"]))]
    print(f"games {len(res)}, errors {len(bad)}, local money != server in {len(mism)}")

    def margin(r):
        return r["us"]["money"] - r["op"]["money"]
    groups = {"all": res, "mirror": [r for r in res if r["mirror"]], "other": [r for r in res if not r["mirror"]]}
    print("\n| group | games | W/L | close losses (-3000..0) | close wins (0..3000) |")
    print("|---|---|---|---|---|")
    for g, rs in groups.items():
        w = sum(margin(r) > 0 for r in rs); l = sum(margin(r) < 0 for r in rs)
        cl = sum(-3000 <= margin(r) < 0 for r in rs); cw = sum(0 < margin(r) <= 3000 for r in rs)
        print(f"| {g} | {len(rs)} | {w}/{l} | {cl} | {cw} |")
    lost = [sum(r["us"]["lost"].values()) for r in res]
    left = [r["us"]["left_value"] for r in res]
    print(f"\nour units lost to a full shed: in {sum(x > 0 for x in lost)} games, mean {st.mean(lost):.0f}, max {max(lost):.0f}")
    print(f"our stock left unsold at the end: in {sum(x > 0 for x in left)} games, mean value {st.mean(left):.0f}, max {max(left):.0f}")
    opl = [r["op"]["left_value"] for r in res]
    print(f"opponent stock left unsold at the end: mean {st.mean(opl):.0f}")
    for name, rs in (("close losses", [r for r in res if -3000 <= margin(r) < 0]),
                     ("close losses vs mirror", [r for r in res if -3000 <= margin(r) < 0 and r["mirror"]])):
        if not rs:
            continue
        diff = collections.Counter()
        late = collections.Counter()
        for r in rs:
            nu, no = item_net(r["us"]), item_net(r["op"])
            for k in set(nu) | set(no):
                diff[k] += (no[k] - nu[k]) / len(rs)
            for k in set(r["us"]["late"]) | set(r["op"]["late"]):
                late[k] += (r["op"]["late"].get(k, 0) - r["us"]["late"].get(k, 0)) / len(rs)
        print(f"\n{name} ({len(rs)} games, mean margin {st.mean(margin(r) for r in rs):+.0f}): opponent minus us, net cash by item")
        for k, v in sorted(diff.items(), key=lambda kv: -abs(kv[1]))[:10]:
            print(f"   {k:12s} {v:+8.0f}   (of which sales on days 26-29: {late.get(k, 0):+.0f})")


if __name__ == "__main__":
    main()
