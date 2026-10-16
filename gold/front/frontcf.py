r"""Replay harvested front games with candidate agents in either seat (the other seat keeps its recorded tape).

    .venv\Scripts\python.exe gold\front\frontcf.py BASE.py CAND.py [CAND.py ...] [--workers 12] [--max-games N]
        [--out gold/front/frontcf.json] [--reuse OUT.json]

Every (game, seat) pair is one test: our agent replaces that seat, the opponent is the other seat's tape.
Summary per candidate: wins, mean margin change vs BASE with its standard error, flips; split by whether the kept
opponent is a tick churner (classify.json tick_cycles >= 5) and by opponent lineage.
--reuse skips replays already in a previous output (same agent path, game id and seat).
"""
import argparse
import collections
import glob
import gzip
import json
import multiprocessing as mp
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "gold", "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools"))


def main():
    import gstat
    from seatswap import tape_file
    ap = argparse.ArgumentParser()
    ap.add_argument("agents", nargs="+")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--max-games", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(HERE, "frontcf.json"))
    ap.add_argument("--reuse")
    a = ap.parse_args()
    cls = {x["name"]: x for x in json.load(open(os.path.join(HERE, "classify.json"), encoding="utf-8"))}
    recs = {}
    for p in sorted(glob.glob(os.path.join(HERE, "front_*.jsonl.gz"))):
        with gzip.open(p, "rt", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    if len(r.get("shops") or []) >= 8:
                        recs[r["id"]] = r
    ids = sorted(recs)
    if a.max_games:
        ids = ids[:a.max_games]
    old = {}
    if a.reuse and os.path.exists(a.reuse):
        for x in json.load(open(a.reuse, encoding="utf-8")):
            old[(x["agent"], x["id"], x["seat"])] = x
    jobs, meta, res = [], [], []
    for gid in ids:
        r = recs[gid]
        for seat in range(2):
            tape = tape_file(r, 1 - seat)
            for ag in a.agents:
                if (ag, gid, seat) in old:
                    res.append(old[(ag, gid, seat)])
                    continue
                seats = (ag, tape) if seat == 0 else (tape, ag)
                jobs.append((seats[0], seats[1], r["seed"], seat, r["shops"]))
                meta.append((ag, gid, seat))
    print(f"{len(ids)} games, {len(jobs)} replays to run, {len(res)} reused", flush=True)
    with mp.get_context("spawn").Pool(a.workers, maxtasksperchild=1) as pool:
        for (ag, gid, seat), g in zip(meta, pool.imap(gstat.play_one, jobs)):
            r = recs[gid]
            opp = r["teams"][1 - seat]
            res.append({"agent": ag, "id": gid, "seat": seat, "opp": opp,
                        "margin": (g["rewards"][seat] or 0) - (g["rewards"][1 - seat] or 0),
                        "money": g["rewards"][seat], "opp_money": g["rewards"][1 - seat]})
    json.dump(res, open(a.out, "w", encoding="utf-8"), ensure_ascii=False)
    m = {(x["agent"], x["id"], x["seat"]): x for x in res}
    base = a.agents[0]
    for ag in a.agents:
        keys = [(gid, s) for gid in ids for s in range(2) if (ag, gid, s) in m and (base, gid, s) in m]
        d = [m[(ag, gid, s)]["margin"] - m[(base, gid, s)]["margin"] for gid, s in keys]
        w = sum(m[(ag, gid, s)]["margin"] > 0 for gid, s in keys)
        fw = sum(m[(base, gid, s)]["margin"] <= 0 < m[(ag, gid, s)]["margin"] for gid, s in keys)
        fl = sum(m[(ag, gid, s)]["margin"] <= 0 < m[(base, gid, s)]["margin"] for gid, s in keys)
        line = f"{os.path.basename(os.path.dirname(ag))[:24]:24s} n {len(keys)} wins {w}"
        if ag != base and d:
            line += f"  vs base: mean {st.mean(d):+.0f} se {st.stdev(d) / len(d) ** 0.5:.0f} flips +{fw} -{fl}"
        print(line)
        if ag == base:
            continue
        grp = collections.defaultdict(list)
        for (gid, s), x in zip(keys, d):
            opp = recs[gid]["teams"][1 - s]
            c = cls.get(opp, {})
            tag = "churner" if (c.get("tick_cycles") or 0) >= 5 else ("lin:" + str(c.get("lineage", "?")))
            grp["churner" if tag == "churner" else "non-churner"].append(x)
            grp[tag].append(x)
        for k, v in sorted(grp.items(), key=lambda kv: -len(kv[1]))[:8]:
            print(f"      {k:16s} n {len(v):3d} mean {st.mean(v):+7.0f}")


if __name__ == "__main__":
    main()
