r"""Append the LATE sale-timing layer (outermost) to a v8-line build: hold chosen goods and sell them once a day.

.venv\Scripts\python.exe tools\add_late.py IN_MAIN_PY OUT_DIR --items MILK:20[,WOOL:20,...] [--from 288] [--last 696]
    [--room 90]

The town eats every good right after the market of steps s % 4 == 0, so the quote only recovers between sales. A
rival that sells its daily output when it reaches the shed (cha22 family, h0-h1) or in the evening (Justin Yang h21,
Arman h22, Vadim lineage h21-h2) takes the recovered price if it sells before us. Before hour H of each day this layer
removes every SELL of ITEM from the turn's orders (inner layers' eager and tape sells alike; later orders move up
unless they sit behind empty padding, which keeps them in their slots); from hour H to the end of the day it sells the whole shed stock of ITEM
(the existing SELL order grows, or a new one goes to slot 0). Steps before FROM and from LAST on are left alone, and
so is any turn whose projected shed (with the held goods and everything the units carry) would exceed ROOM.
"""
import argparse
import os

LAYER = r'''

# ---------------------------------------------------------------------------
# Team 42 LATE layer (outermost): see tools/add_late.py.
_LT_ITEMS = @ITEMS@
_LT_FROM = @FROM@
_LT_LAST = @LAST@
_LT_ROOM = @ROOM@
_LT_REPORT = {"held_turns": 0, "sold_turns": 0, "room_skips": 0}


def _lt_strip(market, i):
    """Remove order i; if an empty padding run follows it (a layer placed an order in a late slot), grow that run
    by one so the padded orders keep their slots. Orders before the padding move up, as if never there."""
    market.pop(i)
    j = next((k for k in range(i, len(market)) if not market[k]), None)
    if j is not None:
        market.insert(j, [])


def _late(obs, action):
    step = int(obs["step"])
    if not isinstance(action, dict) or step < _LT_FROM or step >= _LT_LAST:
        return action
    hour = step % 24
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, (list, tuple))]
    changed = False
    held = False
    pre = None
    for item, h in _LT_ITEMS.items():
        idx = [i for i, o in enumerate(market) if o and o[0] == "SELL" and len(o) >= 3 and o[1] == item]
        if hour < h:
            for i in reversed(idx):
                _lt_strip(market, i)
            changed = changed or bool(idx)
            held = True
            continue
        if pre is None:
            pre = _project(obs, dict(action, market=[]))[0]
        n = int(pre.get(item, 0))
        if n <= 0:
            continue
        if idx:
            if int(market[idx[0]][2]) != n or len(idx) > 1:
                market[idx[0]][2] = n
                for i in reversed(idx[1:]):
                    _lt_strip(market, i)
                changed = True
            continue
        market.insert(0, ["SELL", item, n])
        if len(market) > 10:
            pad = next((i for i, o in enumerate(market) if not o), None)
            if pad is None:
                market.pop(0)
                continue
            market.pop(pad)
        _LT_REPORT["sold_turns"] += 1
        changed = True
    if not changed:
        return action
    if held:
        shed, invs = _project(obs, dict(action, market=[o for o in market if o]))[:2]
        load = sum(int(v) for v in shed.values()) + sum(int(v) for inv in invs for v in inv.values() if int(v) > 0)
        if load > _LT_ROOM:
            _LT_REPORT["room_skips"] += 1
            return action
        _LT_REPORT["held_turns"] += 1
    while market and not market[-1]:
        market.pop()
    out = dict(action)
    out["market"] = market[:10]
    return out


_PRE_LT_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    action = _PRE_LT_AGENT(observation, configuration)
    try:
        return _late(observation, action)
    except Exception:
        return action
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--items", required=True)
    ap.add_argument("--from", dest="start", type=int, default=288)
    ap.add_argument("--last", type=int, default=696)
    ap.add_argument("--room", type=int, default=90)
    a = ap.parse_args()
    items = {}
    for part in a.items.split(","):
        name, hour = part.split(":")
        items[name.strip().upper()] = int(hour)
    raw = open(a.src, "rb").read()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8").replace("\r\n", "\n")
    assert "_project(" in s and "Team 42 LATE layer" not in s
    layer = (LAYER.replace("@ITEMS@", repr(items)).replace("@FROM@", str(a.start))
             .replace("@LAST@", str(a.last)).replace("@ROOM@", str(a.room)))
    s = s.rstrip("\n") + "\n" + layer
    compile(s, "main.py", "exec")
    if crlf:
        s = s.replace("\n", "\r\n")
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "main.py"), "wb") as f:
        f.write(s.encode("utf-8"))
    print("wrote", os.path.join(a.out, "main.py"))


if __name__ == "__main__":
    main()
