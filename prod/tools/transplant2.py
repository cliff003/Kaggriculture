r"""Shop-prefix tape tree: follow a tape-like team's recorded games inside a cha22-family chassis.

transplant2.py GAMES.jsonl.gz TEAM OUT_DIR --base BASE.py [--min-margin X] [--exclude ids] [--pick margin|latest]

Every recorded game of TEAM becomes a tape (acts[t+1] is the action at step t). At each step the router
compares the observed unlocked shops (one more every 3 days) with each tape's shop list and follows a tape
with the longest common prefix, keeping the current tape while it is still among the longest matches.
If the team's agent depends only on the shop prefix, any two tapes with the same prefix are identical
until the next unlock, so switching at an unlock is seamless.

BASE can be a plain cha22 source (with the `_R42_OPENING=` anchor) or one of our packaged agents that
embed the cha22 source as `_BASE_SRC = _zlib.decompress(_b64.b85decode(...))` (v8 and later): then the
tapes are injected into the embedded source and all our outer layers stay.
"""
import argparse
import ast
import base64
import gzip
import json
import lzma
import os
import re
import zlib

INJECT = r'''
# --- team 42 research: shop-prefix tape tree of "__TEAM__" (__N__ recorded games) ---
import lzma as _tp_lzma
_TP_DATA = json.loads(_tp_lzma.decompress(base64.b85decode("__PAYLOAD__")))
_TP_SHOPS = [tuple(g) for g in _TP_DATA["shops"]]
_TP_SCORE = _TP_DATA["score"]
for _k, _v in enumerate(_TP_DATA["tapes"]):
    _ROUTES[5000 + _k] = _v
del _TP_DATA


def _tp_lcp(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


_TP_SELECT = "__SELECT__"
_TP_DEMAND = {"BAKERY": ("EGG", "WHEAT"), "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
              "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"), "YARN_STORE": ("WOOL",),
              "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"), "PET_CAFE": ("CARROT",),
              "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"), "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY")}


def _tp_dist(a, b):
    va, vb = {}, {}
    for s in a:
        for p in _TP_DEMAND.get(s, ()):
            va[p] = va.get(p, 0) + 1
    for s in b:
        for p in _TP_DEMAND.get(s, ()):
            vb[p] = vb.get(p, 0) + 1
    return sum(abs(va.get(k, 0) - vb.get(k, 0)) for k in set(va) | set(vb))


def _tp_pick(cands, shops):
    if _TP_SELECT == "sim":
        return min(cands, key=lambda k: (_tp_dist(_TP_SHOPS[k][:len(shops)], shops), -_TP_SCORE[k]))
    return max(cands, key=lambda k: _TP_SCORE[k])


def _router(observation, step, state):
    shops = tuple(_get(_get(observation, 'town', {}), 'unlocked_shops', []) or [])
    cur = state.get('tp_game')
    if state.get('tp_shops') != shops or cur is None:
        state['tp_shops'] = shops
        best = max(_tp_lcp(g, shops) for g in _TP_SHOPS)
        cands = [k for k, g in enumerate(_TP_SHOPS) if _tp_lcp(g, shops) == best]
        if cur is None or _tp_lcp(_TP_SHOPS[cur], shops) < best:
            cur = _tp_pick(cands, shops)
        elif _TP_SELECT == "sim" and best == len(shops) - 1:
            # the newest shop took us off the tree just now: every candidate shares our history so far
            cur = _tp_pick(cands, shops)
        state['tp_game'] = cur
        state.setdefault('tp_log', []).append((step, cur, best))
    return 5000 + cur


'''


def net_market(market):
    """Collapse each product's BUY_PRODUCT/SELL orders in one step into a single net order at the first one's slot."""
    net = {}
    for o in market or []:
        if isinstance(o, list) and len(o) >= 3 and o[0] in ("BUY_PRODUCT", "SELL"):
            net[o[1]] = net.get(o[1], 0) + (o[2] if o[0] == "BUY_PRODUCT" else -o[2])
    out, done = [], set()
    for o in market or []:
        if isinstance(o, list) and len(o) >= 3 and o[0] in ("BUY_PRODUCT", "SELL"):
            if o[1] in done:
                continue
            done.add(o[1])
            q = net[o[1]]
            if q > 0:
                out.append(["BUY_PRODUCT", o[1], q])
            elif q < 0:
                out.append(["SELL", o[1], -q])
        else:
            out.append(o)
    return out


def load(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def inject(src, payload_block):
    src = src.replace(chr(13) + chr(10), chr(10))
    anchor = "_R42_OPENING="
    i = src.index(anchor)
    src = src[:i] + payload_block + src[i:]
    return src.replace(
        "for _r42_tape in _ROUTES.values():\n    _r42_tape[0]=dict(_r42_tape[0],market=[list(o) for o in _R42_OPENING])",
        "for _r42_k, _r42_tape in _ROUTES.items():\n    if _r42_k < 5000:\n        _r42_tape[0]=dict(_r42_tape[0],market=[list(o) for o in _R42_OPENING])")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("games")
    ap.add_argument("team")
    ap.add_argument("out")
    ap.add_argument("--base", required=True)
    ap.add_argument("--min-margin", type=float, default=-1e9)
    ap.add_argument("--exclude", default="")
    ap.add_argument("--pick", default="margin", choices=["margin", "latest", "money"])
    ap.add_argument("--select", default="score", choices=["score", "sim"])
    ap.add_argument("--net-market", action="store_true", help="net each product's buys and sells per step")
    a = ap.parse_args()
    excl = set(int(x) for x in a.exclude.split(",") if x)
    shops, tapes, score = [], [], []
    for r in load(a.games):
        if a.team not in r["teams"] or r["id"] in excl:
            continue
        me = r["teams"].index(a.team)
        m = r["rewards"][me] - r["rewards"][1 - me]
        if m < a.min_margin:
            continue
        tape = [r["acts"][me][t + 1] if t + 1 < len(r["acts"][me]) else None for t in range(719)]
        tape = [x if isinstance(x, dict) else {"farmer": ["PASS"], "hands": [], "market": []} for x in tape]
        if a.net_market:
            tape = [dict(x, market=net_market(x.get("market"))) for x in tape]
        tapes.append(tape)
        shops.append(r["shops"])
        score.append(m if a.pick == "margin" else (r["rewards"][me] if a.pick == "money" else r["id"]))
    raw = json.dumps({"shops": shops, "tapes": tapes, "score": score}, separators=(",", ":")).encode()
    payload = base64.b85encode(lzma.compress(raw, preset=9 | lzma.PRESET_EXTREME)).decode("ascii")
    block = INJECT.replace("__TEAM__", a.team).replace("__N__", str(len(tapes))).replace("__PAYLOAD__", payload).replace("__SELECT__", a.select)
    src = open(a.base, encoding="utf-8").read()
    m = re.search(r"_BASE_SRC = _zlib\.decompress\(_b64\.b85decode\(\n(.*?)\n\)\)\.decode\(\"utf-8\"\)", src, re.S)
    if m:
        base_src = zlib.decompress(base64.b85decode(ast.literal_eval("(" + m.group(1) + ")"))).decode("utf-8")
        new = base64.b85encode(zlib.compress(inject(base_src, block).encode("utf-8"), 9)).decode("ascii")
        lines = "\n".join("    " + repr(new[i:i + 120]) for i in range(0, len(new), 120))
        src = src[:m.start(1)] + lines + src[m.end(1):]
    else:
        src = inject(src, block)
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "main.py"), "w", encoding="utf-8").write(src)
    print(f"{a.team}: {len(tapes)} tapes, payload {len(payload) / 1e6:.2f} MB -> {a.out}")


if __name__ == "__main__":
    main()
