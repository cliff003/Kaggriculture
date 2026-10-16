r"""Append the FADE layer (outermost) to a v8 build: trade against a rival's wheat tick churn.

.venv\Scripts\python.exe tools\add_fade.py IN_MAIN_PY OUT_DIR [--xmax 60] [--min-n 15] [--reserve 1500]

A tick churner buys N wheat early in the order list on steps s % 4 == 0 (the town eats wheat after that market)
and sells them at s + 1. Once the TICK layer's guard has flagged the rival (its wheat flow, inferred from the
market identity, shows such buy/sell pairs), this layer sells up to X wheat in the LAST order slot of s (after the
rival's buy has lifted the price) and buys the same wheat back in the last slot of s + 1 (after the rival's sale
has pushed it down). Between our two legs the market moves by the rival's unwind minus the town's use, so the
round trip earns about X * slope * (N - c), and the rival's own unwind sells into the market we have refilled.
X is capped by the shed wheat not needed for the route's pickups in the next steps, by the rival's recent N and by
XMAX; the buy-back also tops the fading stock up to X (cash and shed room permitting).
"""
import argparse
import os

LAYER = r'''

# ---------------------------------------------------------------------------
# Team 42 FADE layer (outermost): see tools/add_fade.py.
_FD_XMAX = @XMAX@
_FD_MIN_N = @MINN@
_FD_RESERVE = @RESERVE@
_FD_STATE = {}
_FD_REPORT = {"sells": 0, "sold": 0, "buys": 0, "bought": 0, "active_steps": 0}


def _fd_pickups(seat, step, horizon):
    ns = globals().get("_BASE_NS") or globals()
    chassis = ns["_IMPL"].chassis
    native = chassis.players.get(seat)
    if not native or native.get("route") is None:
        return 0
    total = 0
    for t in range(step + 1, min(719, step + 1 + horizon)):
        tape = chassis.routes.get(2 if t >= 648 else native["route"]) or []
        a = tape[t] if t < len(tape) and isinstance(tape[t], dict) else {}
        for c in [a.get("farmer") or ["PASS"]] + list(a.get("hands") or []):
            if c and c[0] == "PICKUP" and len(c) >= 2 and c[1] == "WHEAT":
                total += max(0, int(c[2]) if len(c) >= 3 else 1)
    return total


def _fd_rival_n(mem, step):
    """Mean size of the rival's recent churn buys (0 when it has not churned in the last 4 ticks)."""
    fl = mem.get("flow") or {}
    sizes = []
    for s0 in range(step - 4, step - 4 - 16, -4):
        b, s1 = fl.get(s0, 0), fl.get(s0 + 1, 0)
        if b <= -_FD_MIN_N and s1 >= _FD_MIN_N:
            sizes.append(min(-b, s1))
    return sum(sizes) / len(sizes) if len(sizes) >= 2 else 0


def _fd_place(market, order):
    """Put the order in the last slot (index 9), padding with empty orders, so it fills after every rival order
    placed earlier in the list; an empty pad of an earlier layer is reused when the list is full."""
    if len(market) >= 10:
        slot = next((i for i, o in enumerate(market) if not o), None)
        if slot is None:
            return False
        market.pop(slot)
    while len(market) < 9:
        market.append([])
    market.append(order)
    return True


def _fade(obs, action):
    step = int(obs["step"])
    seat = int(obs["player"])
    st = _FD_STATE.get(seat)
    if st is None or step <= st["step"]:
        st = _FD_STATE[seat] = {"step": -1, "sold": {}}
    st["step"] = step
    if not isinstance(action, dict) or step < 240 or step > 717:
        return action
    mem = (_TICK_NS.get("_MEM") or {}).get(seat) or {}
    if not mem.get("rival"):
        return action
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, (list, tuple))]
    farm = obs["farms"][seat]
    money = float(farm.get("money", 0))
    prices = obs["market"]["prices"]
    quote = int(prices.get("WHEAT", 40))
    changed = False
    try:
        shed_w = int(_project(obs, dict(action, market=[o for o in market if o]))[0].get("WHEAT", 0))
    except Exception:
        return action
    if step % 4 == 0 and step <= 716:
        n = _fd_rival_n(mem, step)
        if n > 0:
            _FD_REPORT["active_steps"] += 1
            reserve = _fd_pickups(seat, step, 3)
            x = int(min(_FD_XMAX, n, shed_w - reserve))
            if x > 0:
                x = x if _fd_place(market, ["SELL", "WHEAT", x]) else 0
                if x > 0:
                    st["sold"][step] = (x, shed_w)
                    _FD_REPORT["sells"] += 1
                    _FD_REPORT["sold"] += x
                    changed = True
    elif step % 4 == 1 and (_fd_rival_n(mem, step - 1) > 0 or (step - 1) in st["sold"]):
        st["sold"].pop(step - 1, None)
        # after the rival's unwind the book is at its low: restock the fading lot (XMAX above the route's
        # pickups of the next steps), within shed room and cash
        want = max(0, _FD_XMAX + _fd_pickups(seat, step, 4) - shed_w)
        # the lot stays in the shed for several steps: keep room for everything the units carry (a DROP into a
        # full shed deletes goods)
        pshed, pinvs = _project(obs, dict(action, market=[o for o in market if o]))[:2]
        carried = sum(int(v) for inv in pinvs for v in inv.values() if int(v) > 0)
        room = 100 - sum(int(v) for v in pshed.values()) - carried - 3
        cash = money - _FD_RESERVE
        want = int(max(0, min(want, room, cash // max(1, quote + 6))))
        if want > 0:
            want = want if _fd_place(market, ["BUY_PRODUCT", "WHEAT", want]) else 0
            if want > 0:
                _FD_REPORT["buys"] += 1
                _FD_REPORT["bought"] += want
                changed = True
    if not changed:
        return action
    out = dict(action)
    out["market"] = market[:10]
    return out


_PRE_FD_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    action = _PRE_FD_AGENT(observation, configuration)
    try:
        return _fade(observation, action)
    except Exception:
        return action
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--xmax", type=int, default=60)
    ap.add_argument("--min-n", type=int, default=15)
    ap.add_argument("--reserve", type=float, default=1500.0)
    a = ap.parse_args()
    raw = open(a.src, "rb").read()
    crlf = b"\r\n" in raw
    src = raw.decode("utf-8").replace("\r\n", "\n")
    assert "_TICK_NS" in src, "needs a v8 build with the TICK layer"
    code = src.rstrip("\n") + "\n" + (LAYER.replace("@XMAX@", str(a.xmax)).replace("@MINN@", str(a.min_n))
                                      .replace("@RESERVE@", repr(a.reserve)))
    compile(code, "main.py", "exec")
    if crlf:
        code = code.replace("\n", "\r\n")
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "main.py"), "wb") as f:
        f.write(code.encode("utf-8"))
    print("wrote", os.path.join(a.out, "main.py"))


if __name__ == "__main__":
    main()
