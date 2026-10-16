"""Build a self-contained submission: base agent source embedded + team-42 layers.

python build_v5.py BASE_MAIN_PY OUT_DIR [--start 288] [--no-guard] [--license L] [--notice N] [--label TEXT] [--date D]

Layers (outermost last): order-slot priority (same as build_submission.py), then the day-end room
guard: at hour 23 it projects our shed after this turn's unit actions, market orders and the
end-of-day inventory drop, exactly as the engine applies them, and sells the units that would
otherwise be discarded by the 100-item shed cap.
"""
import argparse
import base64
import hashlib
import io
import os
import tarfile
import zlib

TEMPLATE = '''# Kaggriculture submission, team 42 (Kefei Yan, Frank Yang, yirenw11).
# Base agent: {label} (Apache-2.0, upstream notices retained inside the embedded source
# and in NOTICE.txt). Modifications by team 42, {date}:
# 1. order-slot priority layer. From step {start} on, each turn's market list is rewritten so that SELL
#    orders are issued before placeholder slots and before fixed-price orders (HIRE, BUY_SEED,
#    BUY_ANIMAL, BUY_LAND). BUY_PRODUCT orders keep their relative position. Quantities are unchanged.
# 2. day-end room guard ({guard}). At hour 23 the projected shed after this turn's unit actions, market
#    orders and the end-of-day inventory drop is computed with the engine's rules; units that the
#    100-item cap would discard are sold instead.{extra_notes}
#    The base policy is otherwise unchanged.
import base64 as _b64
import math
import zlib as _zlib

_BASE_SHA256 = "{sha}"
_BASE_SRC = _zlib.decompress(_b64.b85decode(
{blob}
)).decode("utf-8")
_BASE_NS = {{}}
exec(compile(_BASE_SRC, "base_agent.py", "exec"), _BASE_NS)
_BASE_AGENT = [_v for _v in list(_BASE_NS.values()) if callable(_v)][-1]
_SLOT_START = {start}
_GUARD = {guard}
_FIXED_PRICE = frozenset(("HIRE", "BUY_SEED", "BUY_ANIMAL", "BUY_LAND"))
_CAP = 100
_SHED_TILES = frozenset(((4, 4), (5, 4), (4, 5), (5, 5)))
_PRODUCT_OF = {{"GOOSE": "EGG", "COW": "MILK", "SHEEP": "WOOL"}}
_STRUCT_OF = {{"GOOSE": "COOP", "COW": "PASTURE", "SHEEP": "PASTURE"}}
_FIRST_YIELD = {{"WHEAT": 2, "CARROT": 2, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 10}}
_SELLABLE = {items}


def _g(o, k, d=None):
    try:
        v = o[k]
    except Exception:
        v = getattr(o, k, d)
    return d if v is None else v


def _slot_priority(observation, action):
    try:
        step = int(observation["step"])
    except Exception:
        step = int(getattr(observation, "step", 0) or 0)
    if step < _SLOT_START or not isinstance(action, dict):
        return action
    market = action.get("market") or []
    if not any(isinstance(o, list) and o and o[0] == "SELL" for o in market):
        return action
    head, tail = [], []
    for o in market:
        if not (isinstance(o, list) and o):
            continue
        (tail if o[0] in _FIXED_PRICE else head).append(o)
    out = dict(action)
    out["market"] = (head + tail)[:10]
    return out


def _project(obs, action):
    """Shed and carried inventories after this turn's unit actions and market orders (engine rules)."""
    me = int(_g(obs, "player", 0))
    farm = _g(obs, "farms")[me]
    priv = _g(obs, "private")
    day = int(_g(obs, "step", 0)) // 24
    shed = {{k: int(v) for k, v in dict(_g(priv, "shed", {{}})).items() if int(v) > 0}}
    invs = [{{k: int(v) for k, v in dict(inv).items() if int(v) > 0}} for inv in _g(priv, "inventories", [{{}}])]
    pos = [tuple(_g(farm, "farmer"))] + [tuple(h) for h in _g(farm, "hands", [])]
    tiles = _g(farm, "tiles")
    size = len(tiles)
    done = set()
    units = [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])
    for idx, act in enumerate(units[:len(pos)]):
        if not (isinstance(act, list) and act):
            continue
        op = act[0]
        x, y = pos[idx]
        while len(invs) <= idx:
            invs.append({{}})
        inv = invs[idx]
        adj = (x, y) in _SHED_TILES
        tile = tiles[y][x] if 0 <= x < size and 0 <= y < size else None
        is_dict = isinstance(tile, dict) or hasattr(tile, "keys")
        if op == "HARVEST" and is_dict and ("H", x, y) not in done:
            n = int(_g(tile, "yield_units", 0))
            if n > 0 and _g(tile, "kind") == "PLANT":
                crop = _g(tile, "crop")
                if day - int(_g(tile, "planted_day", day)) >= _FIRST_YIELD.get(crop, 99):
                    inv[crop] = inv.get(crop, 0) + n
                    done.add(("H", x, y))
            elif n > 0 and _g(tile, "animal") in _PRODUCT_OF:
                prod = _PRODUCT_OF[_g(tile, "animal")]
                inv[prod] = inv.get(prod, 0) + n
                done.add(("H", x, y))
        elif op == "COLLECT_FERTILIZER" and is_dict and _g(tile, "animal") and _g(tile, "fertilizer_available", False) \\
                and ("C", x, y) not in done:
            inv["FERTILIZER"] = inv.get("FERTILIZER", 0) + 1
            done.add(("C", x, y))
        elif op == "FEED" and is_dict and _g(tile, "animal") and not _g(tile, "fed_today", False) \\
                and ("F", x, y) not in done and inv.get("WHEAT", 0) > 0:
            inv["WHEAT"] -= 1
            done.add(("F", x, y))
        elif op == "FERTILIZE" and is_dict and _g(tile, "kind") == "PLANT" and inv.get("FERTILIZER", 0) > 0:
            inv["FERTILIZER"] -= 1
        elif op == "PICKUP" and adj and len(act) >= 2:
            n = min(int(act[2]) if len(act) >= 3 else 1, shed.get(act[1], 0))
            if n > 0:
                shed[act[1]] -= n
                inv[act[1]] = inv.get(act[1], 0) + n
        elif op == "DROP" and adj:
            for item, n in list(inv.items()):
                take = min(n, max(0, _CAP - sum(shed.values())))
                if take > 0:
                    shed[item] = shed.get(item, 0) + take
                del inv[item]
        elif op == "PLACE" and len(act) >= 2:
            item = act[1]
            if item in _STRUCT_OF and is_dict and _g(tile, "kind") == _STRUCT_OF[item] and not _g(tile, "animal"):
                if inv.get(item, 0) > 0:
                    inv[item] -= 1
            elif adj:
                n = min(int(act[2]) if len(act) >= 3 else 1, inv.get(item, 0), max(0, _CAP - sum(shed.values())))
                if n > 0:
                    inv[item] -= n
                    shed[item] = shed.get(item, 0) + n
    for o in (action.get("market") or [])[:10]:
        if not (isinstance(o, list) and o):
            continue
        if o[0] == "SELL" and len(o) >= 3 and o[1] in shed:
            shed[o[1]] -= min(int(o[2]), shed[o[1]])
        elif o[0] in ("BUY_PRODUCT", "BUY_ANIMAL") and len(o) >= 3:
            n = min(int(o[2]), max(0, _CAP - sum(shed.values())))
            if n > 0:
                shed[o[1]] = shed.get(o[1], 0) + n
    return shed, invs, farm


def _room_guard(observation, action):
    step = int(_g(observation, "step", 0))
    if step % 24 != 23 or step >= 718 or not isinstance(action, dict):
        return action
    shed, invs, farm = _project(observation, action)
    carried = {{}}
    for inv in invs:
        for k, v in inv.items():
            if v > 0:
                carried[k] = carried.get(k, 0) + v
    excess = sum(v for v in shed.values() if v > 0) + sum(carried.values()) - _CAP
    if excess <= 0:
        return action
    animals = sum(1 for row in _g(farm, "tiles") for t in row
                  if (isinstance(t, dict) or hasattr(t, "keys")) and _g(t, "animal"))
    wheat_spare = shed.get("WHEAT", 0) + carried.get("WHEAT", 0) - (animals + 2)
    prices = _g(_g(observation, "market"), "prices", {{}})
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, list) and o]
    extra = []
    for item in sorted(_SELLABLE, key=lambda it: -int(_g(prices, it, 0))):
        avail = shed.get(item, 0)
        if item == "WHEAT":
            avail = min(avail, max(0, wheat_spare))
        n = min(excess, avail)
        if n <= 0 or int(_g(prices, item, 0)) <= 1:
            continue
        for o in market:
            if o[0] == "SELL" and len(o) >= 3 and o[1] == item:
                o[2] = int(o[2]) + n
                break
        else:
            extra.append(["SELL", item, n])
        excess -= n
        if excess <= 0:
            break
    out = dict(action)
    out["market"] = (extra + market)[:10]
    return out


_RACE_FROM = {race}
_RACE_SHARE = {race_share}
_RACE_ITEMS = ("MILK", "WOOL", "STRAWBERRY", "EGG", "TOMATO", "CARROT")
_SHOP_GOODS = {{"BAKERY": ("EGG", "WHEAT"), "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
               "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"), "YARN_STORE": ("WOOL",),
               "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"), "PET_CAFE": ("CARROT",),
               "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
               "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY")}}


def _kind(t):
    if not (isinstance(t, dict) or hasattr(t, "keys")):
        return None
    return _g(t, "animal") or _g(t, "crop") or _g(t, "kind")


def _similar(obs):
    """Share of occupied tiles holding the same thing on both farms (cha22-family rivals score ~1)."""
    me = int(_g(obs, "player", 0))
    farms = _g(obs, "farms")
    a, b = _g(farms[me], "tiles"), _g(farms[1 - me], "tiles")
    same = total = 0
    for y in range(len(a)):
        for x in range(len(a[y])):
            ka, kb = _kind(a[y][x]), _kind(b[y][x])
            if ka is None and kb is None:
                continue
            total += 1
            same += ka == kb
    return same / total if total else 0.0


def _race(observation, action):
    """Late game against a same-route rival: when both farms' stock of a premium good exceeds what the
    town can still eat before the end, prices only fall and the first seller wins, so every step after a
    consumption tick our remaining shed stock of that good is sold at the front of the list."""
    step = int(_g(observation, "step", 0))
    if step < _RACE_FROM or step >= 715 or step % 4 != 1 or not isinstance(action, dict):
        return action
    if _similar(observation) < 0.85:
        return action
    shed, invs, farm = _project(observation, action)
    shops = list(_g(_g(observation, "town", {{}}), "unlocked_shops", []))
    prices = _g(_g(observation, "market"), "prices", {{}})
    days_left = (718 - step) / 24.0
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, list) and o]
    planned = {{}}
    for o in market:
        if o[0] == "SELL" and len(o) >= 3:
            planned[o[1]] = planned.get(o[1], 0) + int(o[2])
    extra = []
    for item in _RACE_ITEMS:
        spare = shed.get(item, 0)
        if spare <= 0 or int(_g(prices, item, 0)) <= 2:
            continue
        rate = 1.0 + sum((12.0 if len(_SHOP_GOODS.get(sh, ())) == 1 else 6.0)
                         for sh in shops if item in _SHOP_GOODS.get(sh, ()))
        held = spare + planned.get(item, 0) + sum(i.get(item, 0) for i in invs)
        if 2 * held <= rate * days_left:
            continue
        k = int(math.ceil(spare * _RACE_SHARE))
        for o in market:
            if o[0] == "SELL" and len(o) >= 3 and o[1] == item:
                o[2] = int(o[2]) + k
                break
        else:
            extra.append(["SELL", item, k])
    if not extra and all(o == p for o, p in zip(market, action.get("market") or [])):
        return action
    out = dict(action)
    sells = [o for o in extra + market if o[0] == "SELL"]
    rest = [o for o in market if o[0] != "SELL"]
    out["market"] = (sells + rest)[:10]
    return out


_OPEN20 = {open20}


def _open20(observation, action):
    """Step 0: the base's own v9 opening trade (BUY 20 / SELL 15 wheat, net +5) instead of the plain BUY 5
    a later base layer puts there; family rivals that beat us open this way."""
    step = int(_g(observation, "step", 0))
    if step != 0 or not isinstance(action, dict):
        return action
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, list) and o]
    wheat = [o for o in market if o[0] == "BUY_PRODUCT" and len(o) >= 3 and o[1] == "WHEAT"]
    if len(wheat) != 1 or int(wheat[0][2]) != 5:
        return action
    rest = [o for o in market if o is not wheat[0]]
    out = dict(action)
    out["market"] = [["BUY_PRODUCT", "WHEAT", 20], ["SELL", "WHEAT", 15]] + rest
    return out


_EAGER_FROM = {eager_from}
_EAGER_TO = {eager_to}
_EAGER_BANDS = {eager_bands}   # item -> (floor, ceiling) as shares of the base price
_EAGER_CHUNK = {eager_chunk}   # (share of base, max units per step, from step) or None
_SORT_SELLS = {sort_sells}
_SORT_TOL = {sort_tol}
# engine MARKET_PARAMS: base, T, below_func, below_target, above_func, above_target (I0 = 10000)
_MKT = {{"WHEAT": (25, 400, "sqrt", 0.80, "log", 0.20), "CARROT": (35, 450, "hinge", 1.00, "sqrt", 0.70),
        "TOMATO": (60, 200, "hinge", 0.40, "sqrt", 0.60), "STRAWBERRY": (120, 100, "sqrt", 0.70, "linear", 1.60),
        "MELON": (250, 300, "log", 0.20, "sq", 3.60), "EGG": (50, 332, "hinge", 0.40, "log", 0.20),
        "MILK": (160, 122, "sqrt", 0.60, "linear", 1.60), "WOOL": (200, 105, "log", 0.20, "sq", 3.20),
        "FERTILIZER": (100, 200, "linear", 0.40, "linear", 0.40)}}


def _shape(f, x, T):
    x = max(0.0, x)
    if f == "linear":
        return x
    if f == "sq":
        return x * x
    if f == "sqrt":
        return math.sqrt(x)
    if f == "log":
        return math.log(1.0 + x)
    if f == "hinge":
        u = x / T
        return u + 8.0 * max(0.0, u - 1.0) ** 2
    return x


def _mprice(item, inv):
    base, T, bf, bt, af, at = _MKT[item]
    if inv < 10000:
        p = base + bt * base / _shape(bf, T, T) * _shape(bf, 10000 - inv, T)
    else:
        p = base - at * base / _shape(af, T, T) * _shape(af, inv - 10000, T)
    return max(1, int(round(p)))


def _stake(item, q, inv):
    """What our q units lose if a rival sells as many units of the same item in an earlier slot."""
    if item not in _MKT or q <= 0:
        return 0.0
    q = min(q, 40)
    return float(sum(_mprice(item, inv + k) - _mprice(item, inv + q + k) for k in range(q)))


def _eager(observation, action):
    """Sell premium goods as soon as they reach the shed instead of holding them for the base's
    scheduled lots: in a glutted market the first seller gets the price, and family rivals that
    sell on arrival beat the base's schedule by hundreds of coins."""
    step = int(_g(observation, "step", 0))
    if step < _EAGER_FROM or step >= _EAGER_TO or not isinstance(action, dict):
        return action
    shed, invs, farm = _project(observation, action)
    prices = _g(_g(observation, "market"), "prices", {{}})
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, list) and o]
    free = 10 - len(market)
    changed = False
    for item, (lo, hi) in _EAGER_BANDS.items():
        spare = shed.get(item, 0)
        quote = int(_g(prices, item, 0))
        if spare <= 0 or quote < max(2.0, lo * _MKT[item][0]) or quote > hi * _MKT[item][0]:
            continue
        if _EAGER_CHUNK and step >= _EAGER_CHUNK[2] and quote >= _EAGER_CHUNK[0] * _MKT[item][0]:
            spare = min(spare, _EAGER_CHUNK[1])   # near base price: small lots, the town lifts the quote between them
        for o in market:
            if o[0] == "SELL" and len(o) >= 3 and o[1] == item:
                o[2] = int(o[2]) + spare
                changed = True
                break
        else:
            if free > 0:
                market.insert(0, ["SELL", item, spare])
                free -= 1
                changed = True
    if not changed:
        return action
    out = dict(action)
    out["market"] = market[:10]
    return out


def _sort_sells(observation, action):
    """Permute the SELL orders among the slots they already occupy, largest stake first: in a same-step
    race the earlier slot sells every unit before the rival's first. An order only moves ahead of one it
    beats by more than _SORT_TOL coins, so a mirror rival's identical list keeps the base's order. A SELL
    after a BUY_PRODUCT of the same item (a wash) stays put; every other order keeps its slot."""
    step = int(_g(observation, "step", 0))
    if step < _SLOT_START or not isinstance(action, dict):
        return action
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, list) and o]
    inv = _g(_g(observation, "market"), "inventory", {{}})
    bought = set()
    slots, sells = [], []
    for i, o in enumerate(market):
        if o[0] == "BUY_PRODUCT" and len(o) >= 2:
            bought.add(o[1])
        elif o[0] == "SELL" and len(o) >= 3 and o[1] in _MKT and o[1] not in bought:
            slots.append(i)
            sells.append((-_stake(o[1], int(o[2]), int(_g(inv, o[1], 10000))), o))
    if len(sells) < 2:
        return action
    ranked = []
    for s, o in sells:
        pos = len(ranked)
        while pos > 0 and ranked[pos - 1][0] - s > _SORT_TOL:
            pos -= 1
        ranked.insert(pos, (s, o))
    if [o for s, o in ranked] == [o for s, o in sells]:
        return action
    for i, (s, o) in zip(slots, ranked):
        market[i] = o
    out = dict(action)
    out["market"] = market[:10]
    return out


def agent(observation, configuration=None):
    action = _BASE_AGENT(observation, configuration)
    if _OPEN20:
        try:
            action = _open20(observation, action)
        except Exception:
            pass
    if _EAGER_FROM < 720:
        try:
            action = _eager(observation, action)
        except Exception:
            pass
    try:
        action = _slot_priority(observation, action)
    except Exception:
        pass
    if _RACE_FROM < 720:
        try:
            action = _race(observation, action)
        except Exception:
            pass
    if _GUARD:
        try:
            action = _room_guard(observation, action)
        except Exception:
            pass
    if _SORT_SELLS:
        try:
            action = _sort_sells(observation, action)
        except Exception:
            pass
    return action
'''


ALL_ITEMS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER")
# wheat and fertilizer are what the base buys for tomorrow's feeding and fertilizing; selling them makes it re-buy
PREMIUM_ITEMS = ("CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL")


def build(base_path, out_dir, start=288, guard=True, license_path=None, notice_path=None, label="base",
          date="2026-09-24", items=PREMIUM_ITEMS, race=720, race_share=1.0, open20=False,
          eager_from=720, eager_to=700, eager_items=("MILK", "STRAWBERRY", "WOOL"), eager_floor=0.0, sort_sells=False,
          sort_tol=10.0, eager_ceil=99.0, eager_chunk=None):
    src = open(base_path, "rb").read()
    sha = hashlib.sha256(src).hexdigest()
    enc = base64.b85encode(zlib.compress(src, 9)).decode("ascii")
    lines = [enc[i:i + 120] for i in range(0, len(enc), 120)]
    blob = "\n".join("    '" + ln + "'" for ln in lines)
    tup = lambda xs: "(" + ", ".join(f'"{x}"' for x in xs) + ("," if len(xs) == 1 else "") + ")"
    bands = {}
    for spec in eager_items:
        parts = spec.split(":")
        bands[parts[0]] = ((float(parts[1]), float(parts[2])) if len(parts) == 3
                           else (float(eager_floor), float(eager_ceil)))
    notes, layers = [], ["order-slot priority layer", "day-end room guard"]
    if eager_from < 720:
        desc = ", ".join(f"{it} {lo:g}-{hi:g}" for it, (lo, hi) in bands.items())
        chunk_note = (f"\n#    From step {eager_chunk[2]}, while the quote is at least {eager_chunk[0]:g} of base, at most "
                      f"{eager_chunk[1]} extra units per item and step." if eager_chunk else "")
        notes.append(f"# 3. eager sale layer. From step {eager_from} to step {eager_to}, shed stock that the turn's "
                     f"orders do not\n#    already sell is sold on arrival while the quote lies in the band (share of "
                     f"base price):\n#    {desc}.{chunk_note}")
        layers.append("eager sale layer")
    if sort_sells:
        notes.append(f"# {len(notes) + 3}. sale ordering layer. From step {start}, SELL orders are permuted among the "
                     f"slots they already\n#    occupy, largest same-step race stake first (the market's own price "
                     f"function); ties within {sort_tol:g} keep\n#    the base order.")
        layers.append("sale ordering layer")
    extra_notes = ("\n" + "\n".join(notes)) if notes else ""
    code = TEMPLATE.format(label=label, start=start, sha=sha, blob=blob, date=date, guard=bool(guard),
                           extra_notes=extra_notes,
                           items=tup(items), race=int(race),
                           race_share=float(race_share), open20=bool(open20), eager_from=int(eager_from),
                           eager_to=int(eager_to), eager_bands=repr(bands),
                           sort_sells=bool(sort_sells), sort_tol=float(sort_tol), eager_chunk=repr(eager_chunk))
    os.makedirs(out_dir, exist_ok=True)
    main_path = os.path.join(out_dir, "main.py")
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(code)
    compile(code, "main.py", "exec")
    members = [("main.py", code.encode("utf-8"))]
    if license_path and os.path.exists(license_path):
        members.append(("LICENSE.txt", open(license_path, "rb").read()))
    notice = b""
    if notice_path and os.path.exists(notice_path):
        notice = open(notice_path, "rb").read()
    notice = (b"Team 42 modifications, " + date.encode() + b": " + ", ".join(layers[:-1]).encode() + b" and "
              + layers[-1].encode() + b" appended around the base agent (see main.py header). Base source embedded "
              b"unchanged, SHA-256 " + sha.encode() + b".\n\n" + notice)
    members.append(("NOTICE.txt", notice))
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for name, data in members:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o644
            info.mtime = 0
            tar.addfile(info, io.BytesIO(data))
    with open(os.path.join(out_dir, "submission.tar.gz"), "wb") as f:
        f.write(buf.getvalue())
    return main_path, sha


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("out")
    ap.add_argument("--start", type=int, default=288)
    ap.add_argument("--no-guard", action="store_true")
    ap.add_argument("--license", default=None)
    ap.add_argument("--notice", default=None)
    ap.add_argument("--label", default="base")
    ap.add_argument("--date", default="2026-09-24")
    ap.add_argument("--guard-all-items", action="store_true", help="also let the guard sell wheat and fertilizer (v5)")
    ap.add_argument("--race-day", type=int, default=30, help="late-game race layer from this day (30 = off)")
    ap.add_argument("--race-share", type=float, default=1.0)
    ap.add_argument("--open20", action="store_true", help="step-0 wheat trade BUY 20 / SELL 15")
    ap.add_argument("--eager-from", type=int, default=720, help="sell premium goods on arrival from this step (720 = off)")
    ap.add_argument("--eager-to", type=int, default=700)
    ap.add_argument("--eager-items", default="MILK,STRAWBERRY,WOOL")
    ap.add_argument("--eager-floor", type=float, default=0.0, help="only while the quote is at least this share of base")
    ap.add_argument("--sort-sells", action="store_true", help="SELLs ordered by stake in a same-step race")
    ap.add_argument("--sort-tol", type=float, default=10.0)
    ap.add_argument("--eager-ceil", type=float, default=99.0, help="only while the quote is at most this share of base")
    ap.add_argument("--eager-chunk", default=None, help="SHARE:UNITS[:FROM_STEP] cap eager lots at UNITS per step while "
                    "the quote is at least SHARE of base")
    a = ap.parse_args()
    chunk = None
    if a.eager_chunk:
        parts = a.eager_chunk.split(":")
        chunk = (float(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
    p, sha = build(a.base, a.out, a.start, not a.no_guard, a.license, a.notice, a.label, a.date,
                   ALL_ITEMS if a.guard_all_items else PREMIUM_ITEMS, a.race_day * 24, a.race_share, a.open20,
                   a.eager_from, a.eager_to, tuple(x for x in a.eager_items.split(",") if x), a.eager_floor,
                   a.sort_sells, a.sort_tol, a.eager_ceil, chunk)
    print("wrote", p, "base sha", sha, "size", os.path.getsize(p))
