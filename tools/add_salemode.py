r"""Append a SALEMODE layer (outermost, research): per-item sale window and optional drip cap.

.venv\Scripts\python.exe tools\add_salemode.py IN_MAIN_PY OUT_DIR --items STRAWBERRY:0-3,WOOL:0-3 [--drip 0]
    [--phase -1] [--from 288] [--last 696] [--room 90] [--gate none|dsm]

Inside an item's hour window [A, B) the layer sells the item's whole shed stock (the existing SELL grows, or a new
one goes to slot 0); outside the window it removes every SELL of the item (inner eager and tape sells alike), so
arrivals wait for the next window. --drip K caps each sale at K units, --phase P only sells at steps with
s % 4 == P (P = 1 is the first market after the town eats). --gate dsm acts only against a rival whose farm shows a
pasture at step 3 (the DSM-opening lineage builds one on step 2; the cha22 and public lineages on step 3 or later).
Steps before FROM and from LAST on are left alone, and so is any turn whose projected shed would exceed ROOM.
"""
import argparse
import os

LAYER = r'''

# ---------------------------------------------------------------------------
# Team 42 SALEMODE layer (outermost, research): see tools/add_salemode.py.
_SM_ITEMS = @ITEMS@
_SM_DRIP = @DRIP@
_SM_PHASE = @PHASE@
_SM_FROM = @FROM@
_SM_LAST = @LAST@
_SM_ROOM = @ROOM@
_SM_GATE = @GATE@
_SM_STATE = {}
_SM_REPORT = {"held_turns": 0, "sold_turns": 0, "room_skips": 0, "gate_on": 0}


def _sm_strip(market, i):
    market.pop(i)
    j = next((k for k in range(i, len(market)) if not market[k]), None)
    if j is not None:
        market.insert(j, [])


def _sm_rival_pasture(obs):
    me = int(obs["player"])
    farm = obs["farms"][1 - me]
    for row in farm["tiles"]:
        for t in row:
            if isinstance(t, dict) and t.get("kind") == "PASTURE":
                return True
    return False


def _salemode(obs, action):
    step = int(obs["step"])
    me = int(obs["player"])
    st = _SM_STATE.get(me)
    if st is None or step <= st["step"]:
        st = _SM_STATE[me] = {"step": step, "gate": None}
    st["step"] = step
    if _SM_GATE == "dsm" and step == 3:
        st["gate"] = _sm_rival_pasture(obs)
        if st["gate"]:
            _SM_REPORT["gate_on"] += 1
    if _SM_GATE == "dsm" and not st.get("gate"):
        return action
    if not isinstance(action, dict) or step < _SM_FROM or step >= _SM_LAST:
        return action
    hour = step % 24
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, (list, tuple))]
    changed = False
    held = False
    pre = None
    for item, (a, b) in _SM_ITEMS.items():
        idx = [i for i, o in enumerate(market) if o and o[0] == "SELL" and len(o) >= 3 and o[1] == item]
        open_now = a <= hour < b and (_SM_PHASE < 0 or step % 4 == _SM_PHASE)
        if not open_now:
            for i in reversed(idx):
                _sm_strip(market, i)
            changed = changed or bool(idx)
            held = True
            continue
        if pre is None:
            pre = _project(obs, dict(action, market=[]))[0]
        n = int(pre.get(item, 0))
        if _SM_DRIP > 0:
            n = min(n, _SM_DRIP)
            held = True
        if n <= 0:
            for i in reversed(idx):
                _sm_strip(market, i)
            changed = changed or bool(idx)
            continue
        if idx:
            if int(market[idx[0]][2]) != n or len(idx) > 1:
                market[idx[0]][2] = n
                for i in reversed(idx[1:]):
                    _sm_strip(market, i)
                changed = True
            continue
        market.insert(0, ["SELL", item, n])
        if len(market) > 10:
            pad = next((i for i, o in enumerate(market) if not o), None)
            if pad is None:
                market.pop(0)
                continue
            market.pop(pad)
        _SM_REPORT["sold_turns"] += 1
        changed = True
    if not changed:
        return action
    if held:
        shed, invs = _project(obs, dict(action, market=[o for o in market if o]))[:2]
        load = sum(int(v) for v in shed.values()) + sum(int(v) for inv in invs for v in inv.values() if int(v) > 0)
        if load > _SM_ROOM:
            _SM_REPORT["room_skips"] += 1
            return action
        _SM_REPORT["held_turns"] += 1
    while market and not market[-1]:
        market.pop()
    out = dict(action)
    out["market"] = market[:10]
    return out


_PRE_SM_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    action = _PRE_SM_AGENT(observation, configuration)
    try:
        return _salemode(observation, action)
    except Exception:
        return action
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--items", required=True)
    ap.add_argument("--drip", type=int, default=0)
    ap.add_argument("--phase", type=int, default=-1)
    ap.add_argument("--from", dest="start", type=int, default=288)
    ap.add_argument("--last", type=int, default=696)
    ap.add_argument("--room", type=int, default=90)
    ap.add_argument("--gate", default="none", choices=["none", "dsm"])
    a = ap.parse_args()
    items = {}
    for part in a.items.split(","):
        name, win = part.split(":")
        lo, hi = win.split("-")
        items[name.strip().upper()] = (int(lo), int(hi))
    raw = open(a.src, "rb").read()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8").replace("\r\n", "\n")
    assert "_project(" in s and "Team 42 SALEMODE layer" not in s
    layer = (LAYER.replace("@ITEMS@", repr(items)).replace("@DRIP@", str(a.drip)).replace("@PHASE@", str(a.phase))
             .replace("@FROM@", str(a.start)).replace("@LAST@", str(a.last)).replace("@ROOM@", str(a.room))
             .replace("@GATE@", repr(a.gate)))
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
