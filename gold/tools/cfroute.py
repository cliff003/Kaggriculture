r"""Route-table check on live games: for every recorded live game (data/games/live_*.jsonl.gz) whose first two shops
are in the table, replay the opponent's recorded actions (same seed, same seat, the live shop sequence forced) against
(a) BASE (our agent without the table) and (b) CAND (with the table), and compare the money margins.

.venv\Scripts\python.exe gold\tools\cfroute.py BASE.py CAND.py TABLE_KEYS_JSON [--workers 8] [--all]

TABLE_KEYS_JSON: a JSON file with a dict whose keys are "SHOP1|SHOP2" (e.g. gold/arena/route_table2.json), or the
path of a composite agent file with a route_table in its _CFG. --all replays every live game (not just table pairs).
The opponent does not react (its tape is fixed); cha22-family opponents work from a tape anyway.
"""
import argparse
import ast
import glob
import gzip
import json
import multiprocessing as mp
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
TAPES = os.path.join(ROOT, "gold", "tmp", "tapes")
TEAM = "42"

TAPE_SRC = '''import json
_T = json.load(open(r"{path}"))
_PASS = {{"farmer": ["PASS"], "hands": [], "market": []}}


def agent(observation, configuration=None):
    t = int(observation["step"])
    a = _T[t] if 0 <= t < len(_T) else None
    return json.loads(json.dumps(a)) if isinstance(a, dict) else dict(_PASS)
'''


def table_keys(path):
    if path.endswith(".json"):
        return set(json.load(open(path)))
    tree = ast.parse(open(path, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "_CFG":
            return set((ast.literal_eval(node.value).get("route_table") or {}).keys())
    return set()


def tape_file(rec, seat):
    os.makedirs(TAPES, exist_ok=True)
    js = os.path.join(TAPES, f"{rec['id']}_{seat}.json")
    py = os.path.join(TAPES, f"tape_{rec['id']}_{seat}.py")
    if not os.path.exists(py):
        json.dump(rec["acts"][seat][1:], open(js, "w"))
        open(py, "w", encoding="utf-8").write(TAPE_SRC.format(path=js))
    return py


def main():
    import gstat
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("cand")
    ap.add_argument("keys")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--games", default="live_*.jsonl.gz", help="glob under data/games (default live_*.jsonl.gz)")
    ap.add_argument("--keep", help="team whose recorded actions are kept as the opponent tape; the other side becomes "
                                   "our agent (default: the side that is not team 42)")
    ap.add_argument("--json", help="write per-game margins {id: {live, base, cand, opp, pair, src}} here")
    a = ap.parse_args()
    keys = table_keys(a.keys)
    recs = []
    pattern = a.games if ("/" in a.games or "\\" in a.games) else os.path.join(ROOT, "data", "games", a.games)
    for f in sorted(glob.glob(pattern)):
        with gzip.open(f, "rt", encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                if len(r.get("shops") or []) < 8:
                    continue
                if a.keep:
                    if a.keep not in r["teams"]:
                        continue
                    r["_me"] = 1 - r["teams"].index(a.keep)
                elif TEAM in r["teams"]:
                    r["_me"] = r["teams"].index(TEAM)
                else:
                    continue
                if a.all or "|".join(r["shops"][:2]) in keys:
                    r["_src"] = os.path.basename(f)
                    recs.append(r)
    seen, uniq = set(), []
    for r in recs:
        if r["id"] not in seen:
            seen.add(r["id"])
            uniq.append(r)
    jobs, meta = [], []
    for r in uniq:
        me = r["_me"]
        tape = tape_file(r, 1 - me)
        for tag, path in (("base", a.base), ("cand", a.cand)):
            seats = (path, tape) if me == 0 else (tape, path)
            jobs.append((seats[0], seats[1], r["seed"], me, r["shops"]))
            meta.append((r, tag))
    print(f"{len(uniq)} live games, {len(jobs)} replays", flush=True)
    with mp.get_context("spawn").Pool(max(1, min(a.workers, len(jobs))), maxtasksperchild=1) as pool:
        out = list(pool.imap(gstat.play_one, jobs))
    res = {}
    for (r, tag), g in zip(meta, out):
        me = g["cand_side"]
        m, o = g["rewards"][me], g["rewards"][1 - me]
        res.setdefault(r["id"], {"rec": r})[tag] = (m or 0) - (o or 0)
    wb = wc = 0
    tot = 0.0
    print(f"{'id':>10} {'src':16} {'pair':34} {'opponent':22} {'live':>7} {'base':>7} {'cand':>7}")
    for rid, v in res.items():
        r = v["rec"]
        me = r["_me"]
        live = (r["rewards"][me] or 0) - (r["rewards"][1 - me] or 0)
        wb += v["base"] > 0
        wc += v["cand"] > 0
        tot += v["cand"] - v["base"]
        print(f"{rid:>10} {r['_src'][:16]:16} {'|'.join(r['shops'][:2])[:34]:34} {str(r['teams'][1 - me])[:22]:22} "
              f"{live:+7.0f} {v['base']:+7.0f} {v['cand']:+7.0f}")
    n = max(1, len(res))
    print(f"\nwins base {wb}/{len(res)}, cand {wc}/{len(res)}; mean margin change {tot / n:+.0f}")
    if a.json:
        out = {}
        for rid, v in res.items():
            r = v["rec"]
            me = r["_me"]
            out[str(rid)] = {"live": (r["rewards"][me] or 0) - (r["rewards"][1 - me] or 0), "base": v["base"],
                             "cand": v["cand"], "opp": str(r["teams"][1 - me]), "pair": "|".join(r["shops"][:2]),
                             "src": r["_src"]}
        json.dump(out, open(a.json, "w"), ensure_ascii=False)


if __name__ == "__main__":
    main()
