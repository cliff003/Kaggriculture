"""At end-of-day overflow events (ours), where are our units at hours 22 and 23 and what do they carry / do?"""
import collections, gzip, json, multiprocessing as mp, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "tools"))


def job(rec):
    import econ
    K = econ.K
    me = rec["teams"].index("42")
    env = econ.make("kaggriculture", configuration={"episodeSteps": 720, "seed": rec["seed"]}, debug=False)
    env.reset(2)
    state = env.state
    econ._CUR.update(log=[], farms=state[0].observation.farms, privates=[s.observation.private for s in state],
                     prices=state[0].observation.market["prices"])
    n = len(rec["acts"][0])
    snaps = {}
    out = []
    for t in range(719):
        econ._CUR["step"] = t
        h = t % 24
        if h in (21, 22, 23):
            farm = state[0].observation.farms[me]
            priv = state[me].observation.private
            units = []
            for idx in range(1 + len(farm.get("hands") or [])):
                pos = K._farmer_position(farm, idx)
                inv = priv["inventories"][idx] if idx < len(priv["inventories"]) else {}
                act = rec["acts"][me][t + 1] if t + 1 < n else None
                a = None
                if isinstance(act, dict):
                    a = act.get("farmer") if idx == 0 else ((act.get("hands") or [None] * 99)[idx - 1] if idx - 1 < len(act.get("hands") or []) else None)
                units.append({"adj": bool(pos) and K._is_shed_adjacent(tuple(pos), 10), "carry": sum(v for v in inv.values() if v > 0),
                              "act": (a or ["?"])[0]})
            snaps[h] = {"units": units, "shed": sum(priv["shed"].values())}
        for i in range(2):
            a = rec["acts"][i][t + 1] if t + 1 < n else None
            state[i].action = a if isinstance(a, dict) else None
        n0 = len(econ._CUR["log"])
        K.interpreter(state, env)
        state[0].observation.step = t + 1
        if h == 23:
            lost = sum(e[4] for e in econ._CUR["log"][n0:] if e[2] == "LOST" and e[1] == me)
            if lost > 0:
                out.append({"day": t // 24, "lost": lost, "snaps": snaps})
            snaps = {}
    return rec["id"], out


if __name__ == "__main__":
    recs = [json.loads(l) for l in gzip.open(sys.argv[1], "rt", encoding="utf-8") if l.strip()]
    with mp.get_context("spawn").Pool(8) as pool:
        res = pool.map(job, recs, chunksize=1)
    ev = [e for _, es in res for e in es]
    print("overflow events", len(ev), "value", round(sum(e["lost"] for e in ev)))
    for h in (21, 22, 23):
        adj_units = [sum(u["adj"] for u in e["snaps"][h]["units"]) for e in ev if h in e["snaps"]]
        adj_carry = [sum(u["carry"] for u in e["snaps"][h]["units"] if u["adj"]) for e in ev if h in e["snaps"]]
        tot_carry = [sum(u["carry"] for u in e["snaps"][h]["units"]) for e in ev if h in e["snaps"]]
        shed = [e["snaps"][h]["shed"] for e in ev if h in e["snaps"]]
        acts = collections.Counter(u["act"] for e in ev if h in e["snaps"] for u in e["snaps"][h]["units"] if u["adj"])
        import statistics as st
        print(f"hour {h}: shed-adjacent units median {st.median(adj_units)}, they carry median {st.median(adj_carry)} "
              f"(all units carry median {st.median(tot_carry)}), shed median {st.median(shed)}; actions of adjacent units {dict(acts.most_common(6))}")
    over = [sum(u['carry'] for u in e['snaps'][23]['units']) + e['snaps'][23]['shed'] - 100 for e in ev if 23 in e['snaps']]
    print("overflow units at hour 23 (carried + shed - 100): median", sorted(over)[len(over)//2], "max", max(over))
