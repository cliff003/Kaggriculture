r"""Build a route-library agent from DSM's live games, replayed through cha22's Chassis.

.venv\Scripts\python.exe engine\build_dsmlib.py OUT_DIR [--games data\games\dsm.jsonl.gz] [--team DSM]
                                             [--chassis submissions\v4_public_cha22_verbatim\main.py]

Route 0 is the game whose first 144 steps are the most typical (DSM's day 0 is a fixed tape and its NW
grid at the end of day 5 is identical in 86 of 92 games); it plays steps 0-143. At step 144 the router
picks the game with the same first two shops (the highest-margin one when several), else one with the
same first shop, else keeps route 0. Actions are stored once and referenced by index. Our order-slot
and day-end room-guard layers wrap the result.
"""
import argparse
import base64
import collections
import gzip
import hashlib
import json
import os
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import build_v5

TEMPLATE = '''# Kaggriculture submission, team 42. Route library built from {n_routes} live games of the team "{team}",
# replayed through the Chassis of the embedded Apache-2.0 agent (sha256 {csha}), whose notices are retained
# inside its source. Router: route 0 for steps < 144, then the route matching the first two town shops.
import base64 as _b64
import json as _json
import zlib as _zlib


def _unz(blob):
    return _zlib.decompress(_b64.b85decode(blob)).decode("utf-8")


_CH_NS = {{"__name__": "chassis_host"}}
exec(compile(_unz(
{cblob}), "chassis_host.py", "exec"), _CH_NS)
_LIB = _json.loads(_unz(
{rblob}))
_ACTIONS = _LIB["actions"]
_ROUTES = {{int(k): [_ACTIONS[i] for i in ids] for k, ids in _LIB["routes"].items()}}
_BY_PAIR = {{tuple(p): r for p, r in _LIB["by_pair"]}}
_BY_FIRST = {{f: r for f, r in _LIB["by_first"]}}
del _LIB


def _router(observation, step, state):
    if step >= 144 and not state.get("chosen"):
        town = observation["town"] if "town" in observation else getattr(observation, "town", {{}})
        shops = list((town["unlocked_shops"] if "unlocked_shops" in town else []) or [])
        route = _BY_PAIR.get(tuple(shops[:2]))
        if route is None and shops:
            route = _BY_FIRST.get(shops[0])
        state["route"] = route if route is not None else 0
        state["chosen"] = True
    return state.get("route", 0)


_IMPL = _CH_NS["make_agent"](_ROUTES, router=_router, **_CH_NS["_SETTINGS"])


def _library_agent(observation, configuration=None):
    try:
        return _IMPL(observation, configuration)
    except Exception:
        return {{"farmer": ["PASS"], "hands": [], "market": []}}
'''


def blob(text):
    enc = base64.b85encode(zlib.compress(text.encode("utf-8"), 9)).decode("ascii")
    return "\n".join("    '" + enc[i:i + 120] + "'" for i in range(0, len(enc), 120))


def build(out_dir, games_path, team, chassis_path):
    games = [json.loads(l) for l in gzip.open(games_path, "rt", encoding="utf-8")]
    tapes = []
    for g in games:
        if team not in g["teams"]:
            continue
        side = g["teams"].index(team)
        acts = g["acts"][side][1:]
        tape = [a if isinstance(a, dict) else {"farmer": ["PASS"], "hands": [], "market": []} for a in acts]
        margin = g["rewards"][side] - g["rewards"][1 - side]
        tapes.append((g, tape, margin))
    # route 0: the game whose first 144 actions agree most with the per-step modal action
    keyed = [[json.dumps(a, sort_keys=True) for a in t[:144]] for _, t, _ in tapes]
    modal = [collections.Counter(k[s] for k in keyed).most_common(1)[0][0] for s in range(144)]
    score = [sum(1 for s in range(144) if k[s] == modal[s]) for k in keyed]
    opening = max(range(len(tapes)), key=lambda i: (score[i], tapes[i][2]))
    # one game per first-two-shop pair (best margin), and per first shop
    by_pair, by_first = {}, {}
    for i, (g, _, m) in enumerate(tapes):
        p = tuple(g["shops"][:2])
        if p not in by_pair or m > tapes[by_pair[p]][2]:
            by_pair[p] = i
        f = g["shops"][0]
        if f not in by_first or m > tapes[by_first[f]][2]:
            by_first[f] = i
    chosen = sorted({opening} | set(by_pair.values()) | set(by_first.values()))
    rid = {opening: 0}
    for i in chosen:
        if i != opening:
            rid[i] = len(rid)
    table, index = [], {}
    routes = {}
    for i in chosen:
        ids = []
        for a in tapes[i][1]:
            key = json.dumps(a, sort_keys=True, separators=(",", ":"))
            if key not in index:
                index[key] = len(table)
                table.append(a)
            ids.append(index[key])
        routes[rid[i]] = ids
    lib = {"actions": table, "routes": routes,
           "by_pair": [[list(p), rid[i]] for p, i in by_pair.items()],
           "by_first": [[f, rid[i]] for f, i in by_first.items()]}
    csrc = open(chassis_path, encoding="utf-8").read()
    code = TEMPLATE.format(n_routes=len(routes), team=team, csha=hashlib.sha256(csrc.encode("utf-8")).hexdigest(),
                           cblob=blob(csrc), rblob=blob(json.dumps(lib, separators=(",", ":"))))
    os.makedirs(out_dir, exist_ok=True)
    lib_path = os.path.join(out_dir, "library_agent.py")
    with open(lib_path, "w", encoding="utf-8") as f:
        f.write(code)
    compile(code, lib_path, "exec")
    print(f"routes {len(routes)} (opening = game {tapes[opening][0]['id']}, agrees on {score[opening]}/144 steps), "
          f"pairs {len(by_pair)}, unique actions {len(table)}, library {os.path.getsize(lib_path)} bytes")
    # wrap with the order-slot and room-guard layers into main.py
    return build_v5.build(lib_path, out_dir, label=f"route library of {team} games", date="2026-09-24",
                          items=build_v5.ALL_ITEMS)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--games", default=os.path.join(ROOT, "data", "games", "dsm.jsonl.gz"))
    ap.add_argument("--team", default="DSM")
    ap.add_argument("--chassis", default=os.path.join(ROOT, "submissions", "v4_public_cha22_verbatim", "main.py"))
    a = ap.parse_args()
    p, sha = build(a.out, a.games, a.team, a.chassis)
    print("wrote", p, os.path.getsize(p))
