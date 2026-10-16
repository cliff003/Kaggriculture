r"""Where our units get destroyed by a full shed in live games: item, day, hour, end-of-day drop vs unit DROP,
and the shed contents (ours) at that moment.

.venv/bin/python research/carrera/lostdetail.py TAPES.jsonl.gz [--workers 8]
"""
import collections, gzip, json, multiprocessing as mp, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "tools"))


def job(rec):
    import econ
    K = econ.K
    me = rec["teams"].index("42")
    events = []
    inner_eod = K._drop_inventories_to_shed
    inner_unit = K._apply_unit_action

    def eod(private, capacity):
        n0 = len(econ._CUR["log"])
        shed = dict(private["shed"])
        inner_eod(private, capacity)
        for e in econ._CUR["log"][n0:]:
            if e[2] == "LOST":
                events.append(("EOD",) + tuple(e) + (shed,))

    def unit(farm, private, idx, action, *a, **kw):
        n0 = len(econ._CUR["log"])
        shed = dict(private["shed"])
        inner_unit(farm, private, idx, action, *a, **kw)
        for e in econ._CUR["log"][n0:]:
            if e[2] == "LOST":
                events.append(("DROP",) + tuple(e) + (shed,))

    K._drop_inventories_to_shed, K._apply_unit_action = eod, unit
    try:
        env = econ.make("kaggriculture", configuration={"episodeSteps": 720, "seed": rec["seed"]}, debug=False)
        env.reset(2)
        state = env.state
        econ._CUR.update(log=[], farms=state[0].observation.farms, privates=[s.observation.private for s in state],
                         prices=state[0].observation.market["prices"])
        n = len(rec["acts"][0])
        for t in range(719):
            econ._CUR["step"] = t
            for i in range(2):
                a = rec["acts"][i][t + 1] if t + 1 < n else None
                state[i].action = a if isinstance(a, dict) else None
            K.interpreter(state, env)
            state[0].observation.step = t + 1
    finally:
        K._drop_inventories_to_shed, K._apply_unit_action = inner_eod, inner_unit
    return rec["id"], [(kind, step, item, val, shed) for kind, step, p, op, item, val, shed in events if p == me]


def main():
    path = sys.argv[1]
    W = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 8
    recs = [json.loads(l) for l in gzip.open(path, "rt", encoding="utf-8") if l.strip()]
    with mp.get_context("spawn").Pool(W) as pool:
        res = pool.map(job, recs, chunksize=1)
    by_kind, by_item, by_day, by_hour = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    shed_wheat = []
    games = 0
    for gid, ev in res:
        games += bool(ev)
        for kind, step, item, val, shed in ev:
            by_kind[kind] += val; by_item[item] += val; by_day[step // 24] += val; by_hour[step % 24] += val
            shed_wheat.append((shed.get("WHEAT", 0), sum(shed.values())))
    tot = sum(by_kind.values())
    print(f"games with losses {games}/{len(res)}, total value {tot:.0f} ({tot/len(res):.0f} per game)")
    print("by kind:", {k: round(v) for k, v in by_kind.items()})
    print("by item:", {k: round(v) for k, v in by_item.most_common()})
    print("by day:", {k: round(v) for k, v in sorted(by_day.items())})
    print("by hour:", {k: round(v) for k, v in sorted(by_hour.items())})
    if shed_wheat:
        import statistics as st
        print(f"at loss events: shed total median {st.median(s for _, s in shed_wheat)}, wheat in shed median {st.median(w for w, _ in shed_wheat)}, "
              f"events with >=20 wheat in shed {sum(w >= 20 for w, _ in shed_wheat)}/{len(shed_wheat)}")


if __name__ == "__main__":
    main()
