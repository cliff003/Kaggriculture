r"""Build a cha22-chassis agent whose tapes come from a tape-like team's recorded games.

transplant.py GAMES.jsonl.gz TEAM OUT_DIR [--base research/panel/cha22/main.py] [--min-margin X]
        [--pick best|latest] [--opening own|base] [--from-step 0] [--keep-base-layers]

For every first-two-shop pair seen in TEAM's games, one game is chosen (best margin by default) and its
full action list (acts[t+1] is the action applied at step t) becomes a route. The router uses the team's
route for that pair from --from-step on; unseen pairs keep the base agent's own route. Writes OUT_DIR/main.py
plus OUT_DIR/tapes.json (pair -> episode id, margin).
"""
import argparse
import base64
import collections
import gzip
import json
import os
import zlib


def load(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("games")
    ap.add_argument("team")
    ap.add_argument("out")
    ap.add_argument("--base", default="research/panel/cha22/main.py")
    ap.add_argument("--pick", default="best", choices=["best", "latest", "worst"])
    ap.add_argument("--opening", default="own", choices=["own", "base"])
    ap.add_argument("--from-step", type=int, default=0)
    ap.add_argument("--min-margin", type=float, default=-1e9)
    ap.add_argument("--exclude", default="", help="comma-separated episode ids to leave out (holdout)")
    ap.add_argument("--end", default="base", choices=["base", "own"], help="from step 648 use cha22 route 2 (base) or keep the tape")
    a = ap.parse_args()
    recs = load(a.games)
    excl = set(int(x) for x in a.exclude.split(",") if x)
    by_pair = collections.defaultdict(list)
    for r in recs:
        if a.team not in r["teams"] or r["id"] in excl:
            continue
        me = r["teams"].index(a.team)
        margin = r["rewards"][me] - r["rewards"][1 - me]
        if margin < a.min_margin:
            continue
        pair = tuple(r["shops"][:2])
        tape = [r["acts"][me][t + 1] if t + 1 < len(r["acts"][me]) else None for t in range(719)]
        tape = [x if isinstance(x, dict) else {"farmer": ["PASS"], "hands": [], "market": []} for x in tape]
        by_pair[pair].append((margin, r["id"], tape))
    chosen = {}
    for pair, lst in by_pair.items():
        if a.pick == "best":
            lst.sort(key=lambda x: -x[0])
        elif a.pick == "worst":
            lst.sort(key=lambda x: x[0])
        else:
            lst.sort(key=lambda x: -x[1])
        chosen[pair] = lst[0]
    # opening: the most common day-0..5 prefix among chosen tapes is the first tape's (they should agree)
    routes = {}
    pair_route = {}
    for k, (pair, (margin, eid, tape)) in enumerate(sorted(chosen.items())):
        rid = 5000 + k
        routes[rid] = tape
        pair_route[pair] = rid
    opening_rid = min(routes) if routes else None
    payload = base64.b85encode(zlib.compress(json.dumps({
        "routes": {str(k): v for k, v in routes.items()},
        "pairs": [[list(p), r] for p, r in pair_route.items()],
        "opening": opening_rid,
    }).encode("utf-8"), 9)).decode("ascii")
    src = open(a.base, encoding="utf-8").read()
    anchor = "_R42_OPENING="
    i = src.index(anchor)
    inject = f'''
# --- team 42 research: transplanted tapes of "{a.team}" ({len(routes)} shop pairs) ---
_TP_DATA = json.loads(zlib.decompress(base64.b85decode("{payload}")))
for _k, _v in _TP_DATA["routes"].items():
    _ROUTES[int(_k)] = _v
_TP_PAIRS = {{tuple(p): r for p, r in _TP_DATA["pairs"]}}
_TP_OPENING = _TP_DATA["opening"] if "{a.opening}" == "own" else None
_TP_FROM = {a.from_step}
_TP_BASE_ROUTER = _router


def _router(observation, step, state):
    base = _TP_BASE_ROUTER(observation, step, state)
    if step >= 648 and "{a.end}" == "base":
        return base
    if step < 144:
        if _TP_OPENING is not None and step >= _TP_FROM:
            return _TP_OPENING
        return base
    shops = tuple((_get(_get(observation, 'town', {{}}), 'unlocked_shops', []) or [])[:2])
    r = _TP_PAIRS.get(shops)
    if r is not None and step >= _TP_FROM:
        state['tp_route'] = r
        return r
    if state.get('tp_route') is not None and step >= _TP_FROM:
        return state['tp_route']
    return base


del _TP_DATA
'''
    src = src[:i] + inject + src[i:]
    # the R42 opening rewrite applies to every route: keep it off our tapes
    src = src.replace("for _r42_tape in _ROUTES.values():\n    _r42_tape[0]=dict(_r42_tape[0],market=[list(o) for o in _R42_OPENING])",
                      "for _r42_k, _r42_tape in _ROUTES.items():\n    if _r42_k < 5000:\n        _r42_tape[0]=dict(_r42_tape[0],market=[list(o) for o in _R42_OPENING])")
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "main.py"), "w", encoding="utf-8").write(src)
    json.dump({" ".join(p): {"episode": v[1], "margin": v[0], "n": len(by_pair[p])} for p, v in chosen.items()},
              open(os.path.join(a.out, "tapes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{a.team}: {len(routes)} pairs from {sum(len(v) for v in by_pair.values())} games -> {a.out}")


if __name__ == "__main__":
    main()
