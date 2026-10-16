r"""Append the FEEDECON layer (feed animals only when it pays at today's prices) as the outermost layer.

add_feedecon.py IN_MAIN_PY OUT_DIR [--from-day 12] [--margin 1.0] [--no-buyblock]

In v8 self-play milk falls to 4-13% of its base price after day 20 and wool to 1-25% without yarn stores,
while wheat trades at 1.4-1.7x base: the tape keeps feeding (about $37 of wheat per animal-day) animals
whose output is nearly worthless. From --from-day on, a unit's FEED is turned into PASS (and its CARE with
it) when the feed is worth less than the wheat it uses, valuing at the current market price:
  * the care bonus it unlocks on a production day (pending units) plus the one it banks for the next
    production (x0.8), and
  * when the animal went unfed yesterday (it escapes tonight if unfed again), its remaining base output
    minus the cheapest upkeep (a feed every other day).
A CARE whose animal is not fed today is useless and becomes PASS too. BUY_ANIMAL orders are dropped from
the same day when the animal's remaining base output at today's price is below its cost plus upkeep.
"""
import argparse
import os

LAYER = r'''

# ---------------------------------------------------------------------------
# Team 42 FEEDECON layer (outermost): see prod/tools/add_feedecon.py.
_FE_FROM_DAY = @FROM@
_FE_MARGIN = @MARGIN@
_FE_BUYBLOCK = @BUYBLOCK@
_FE_ANIMALS = {"GOOSE": ("EGG", 4, 1, 300), "COW": ("MILK", 8, 2, 400), "SHEEP": ("WOOL", 6, 3, 500)}
_FE_LOG = {}


def _fe_g(o, k, d=None):
    if isinstance(o, dict):
        return o.get(k, d)
    return getattr(o, k, d)


def _fe_future(placed, first, interval, day, last=28):
    n = 0
    for D in range(day + 1, last + 1):
        dsf = D + 1 - placed - first
        if dsf >= 0 and dsf % interval == 0:
            n += 1
    return n


def _feedecon(obs, action):
    step = int(_fe_g(obs, "step", 0) or 0)
    day = step // 24
    if day < _FE_FROM_DAY or day >= 29 or not isinstance(action, dict):
        return action
    me = int(_fe_g(obs, "player", 0) or 0)
    farm = _fe_g(obs, "farms")[me]
    tiles = _fe_g(farm, "tiles")
    prices = dict(_fe_g(_fe_g(obs, "market", {}), "prices", {}) or {})
    W = float(prices.get("WHEAT", 25))
    units = [tuple(_fe_g(farm, "farmer"))] + [tuple(h) for h in (_fe_g(farm, "hands", []) or [])]
    acts = [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])
    out = [list(a) if isinstance(a, (list, tuple)) else a for a in acts]
    skipped = set()
    changed = False
    for i, (p, a) in enumerate(zip(units, acts)):
        if not a or a[0] != "FEED":
            continue
        t = tiles[p[1]][p[0]]
        if not isinstance(t, dict) or t.get("animal") not in _FE_ANIMALS or t.get("fed_today"):
            continue
        prod, first, interval, _ = _FE_ANIMALS[t["animal"]]
        P = float(prices.get(prod, 0))
        placed = int(t.get("placed_day", 0))
        dsf = day + 1 - placed - first
        prod_today = dsf >= 0 and dsf % interval == 0
        nfut = _fe_future(placed, first, interval, day)
        pend = int(t.get("pending_care_bonus", 0) or 0)
        value = P * (pend if prod_today else 0) + (0.8 * P if nfut > 0 else 0.0)
        if int(t.get("consecutive_unfed", 0) or 0) >= 1:
            keep = nfut * P - ((28 - day) // 2) * W
            value += max(0.0, keep)
        if value < W * _FE_MARGIN:
            out[i] = ["PASS"]
            skipped.add(p)
            changed = True
    for i, (p, a) in enumerate(zip(units, acts)):
        if not a or a[0] != "CARE" or out[i] != list(a):
            continue
        t = tiles[p[1]][p[0]]
        if isinstance(t, dict) and t.get("animal") and not t.get("fed_today") and \
                not any(units[j] == p and acts[j] and acts[j][0] == "FEED" and out[j] == list(acts[j]) for j in range(len(units))):
            out[i] = ["PASS"]
            changed = True
    market = list(action.get("market") or [])
    if _FE_BUYBLOCK:
        keep_m = []
        for o in market:
            if isinstance(o, (list, tuple)) and len(o) >= 2 and o[0] == "BUY_ANIMAL" and o[1] in _FE_ANIMALS:
                prod, first, interval, cost = _FE_ANIMALS[o[1]]
                P = float(prices.get(prod, 0))
                nfut = _fe_future(day + 1, first, interval, day)
                if nfut * P < cost + ((28 - day) // 2) * W:
                    changed = True
                    continue
            keep_m.append(o)
        market = keep_m
    if not changed:
        return action
    _FE_LOG[day] = _FE_LOG.get(day, 0) + len(skipped)
    res = dict(action)
    res["farmer"] = out[0]
    res["hands"] = out[1:]
    res["market"] = market
    return res


_PRE_FE_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    action = _PRE_FE_AGENT(observation, configuration)
    try:
        return _feedecon(observation, action)
    except Exception:
        return action
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--from-day", type=int, default=12)
    ap.add_argument("--margin", type=float, default=1.0)
    ap.add_argument("--no-buyblock", action="store_true")
    a = ap.parse_args()
    code = (open(a.src, encoding="utf-8").read().replace("\r\n", "\n").rstrip("\n") + "\n"
            + LAYER.replace("@FROM@", str(a.from_day)).replace("@MARGIN@", str(a.margin))
            .replace("@BUYBLOCK@", "False" if a.no_buyblock else "True"))
    compile(code, "main.py", "exec")
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "main.py"), "w", encoding="utf-8", newline="\n") as f:
        f.write(code)
    print("wrote", os.path.join(a.out, "main.py"))


if __name__ == "__main__":
    main()
