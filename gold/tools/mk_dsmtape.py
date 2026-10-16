r"""Build a cha22 variant that plays DSM's recorded actions (one tape per first-two-shop pair) through cha22's own
tape chassis (hand alignment, weed repair, sale lead) and layers.

    .venv\Scripts\python.exe gold\tools\mk_dsmtape.py OUT_NAME [--pick best|median] [--switch-step 144] [--exclude-worlds FILE]

Tapes come from data\games\dsm.jsonl.gz (DSM's 92 games of 9/24, DSM's own seat, step t action = acts[seat][t+1]).
Before --switch-step every game uses the default tape (the pair-independent DSM opening); at the switch the router
picks the tape of the first two shops (falling back to a game with the same first shop, then the default).
--exclude-worlds: a JSON list of world indices (DSM game order) whose tapes are not used, so that evaluation worlds
are not played with their own recorded tape.
"""
import argparse
import base64
import collections
import gzip
import json
import os
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--pick", default="best")
    ap.add_argument("--switch-step", type=int, default=144)
    ap.add_argument("--exclude-worlds")
    ap.add_argument("--base", default=os.path.join(ROOT, "research", "panel", "cha22", "main.py"))
    a = ap.parse_args()
    excl = set(json.load(open(a.exclude_worlds))) if a.exclude_worlds else set()
    games = []
    with gzip.open(os.path.join(ROOT, "data", "games", "dsm.jsonl.gz"), "rt", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if not line.strip():
                continue
            g = json.loads(line)
            if i in excl or "DSM" not in g["teams"]:
                continue
            me = g["teams"].index("DSM")
            margin = (g["rewards"][me] or 0) - (g["rewards"][1 - me] or 0)
            tape = g["acts"][me][1:]
            if len(tape) < 719:
                continue
            games.append({"i": i, "shops": g["shops"], "margin": margin, "tape": tape[:719]})
    by_pair = collections.defaultdict(list)
    by_first = collections.defaultdict(list)
    for g in games:
        by_pair[tuple(g["shops"][:2])].append(g)
        by_first[g["shops"][0]].append(g)

    def pick(lst):
        lst = sorted(lst, key=lambda g: -g["margin"])
        return lst[0] if a.pick == "best" else lst[len(lst) // 2]

    chosen = {}
    routes = {}
    for pair, lst in by_pair.items():
        g = pick(lst)
        routes[g["i"]] = g["tape"]
        chosen[pair] = g["i"]
    first = {}
    for s, lst in by_first.items():
        g = pick(lst)
        routes[g["i"]] = g["tape"]
        first[s] = g["i"]
    default = pick(games)["i"]
    routes[default] = pick(games)["tape"]
    blob = {"routes": {str(k): v for k, v in routes.items()},
            "pairs": [{"shops": list(k), "route": v} for k, v in chosen.items()],
            "first": first, "default": default}
    enc = base64.b85encode(zlib.compress(json.dumps(blob, separators=(",", ":")).encode(), 9)).decode()
    src = open(a.base, encoding="utf-8").read()
    anchor = "_IMPL=make_agent(_ROUTES,router=_router,**_SETTINGS)"
    assert src.count(anchor) == 1
    inject = f'''
# ---- DSM tape library (team 42 experiment): DSM's recorded actions through the cha22 chassis
_DSM_LIB=json.loads(zlib.decompress(base64.b85decode({enc!r})))
_ROUTES={{int(k):v for k,v in _DSM_LIB['routes'].items()}}
_DSM_PAIRS={{tuple(p['shops']):p['route'] for p in _DSM_LIB['pairs']}}
_DSM_FIRST=_DSM_LIB['first']
_DSM_DEFAULT=_DSM_LIB['default']
del _DSM_LIB

def _router(observation,step,state):
    if step>={a.switch_step} and not state.get('dsm_pick'):
        shops=tuple((_get(_get(observation,'town',{{}}),'unlocked_shops',[]) or [])[:2])
        r=_DSM_PAIRS.get(shops)
        if r is None and shops:
            r=_DSM_FIRST.get(shops[0])
        state['route']=r if r is not None else _DSM_DEFAULT
        state['dsm_pick']=True
    return state.get('route',_DSM_DEFAULT)

'''
    src = src.replace(anchor, inject + anchor)
    out = os.path.join(ROOT, "gold", "builds", a.out)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "main.py"), "w", encoding="utf-8").write(src)
    print(out, "tapes", len(routes), "pairs", len(chosen), "blob KB", len(enc) // 1024)


if __name__ == "__main__":
    main()
