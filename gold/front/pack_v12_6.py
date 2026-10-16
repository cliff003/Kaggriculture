r"""Build the v12_6 package: v12_5 plus the GFADE layer (generic fade of a rival's wheat churn at phases 1-3).

    .venv/bin/python gold/front/pack_v12_6.py [OUT_DIR] [XMAX=90] [MIN_N=15] [FG_K=4] [FG_MIN=-1.2] [LOG=0]

Some rivals churn wheat off the tick phase: they buy N in an early slot at steps s % 4 == 3 (an off-by-one public
layer: kyy666, len8487, emreaydin, KouFu, ZHOU HONGYI, 45-86 units a cycle) or at phases 1-2, and sell at s + 1. The
FADE layer only fades phase 0. GFADE picks the busiest off-phase p (>= HITS churn cycles of MIN_N+ in the last 4 of that
phase, from the TICK layer's inferred rival flow), sells up to XMAX wheat in the last order slot at phase p (after the
rival's lifting buy) and buys the lot back in the last slot at p + 1 (after its unwind), keeping XMAX above the route's
feed pickups. While a phase-3 churner is faded the TICK layer is held off (its buy at phase 0 would compete with the
buy-back for shed room; the fade earns about 30x more per unit). Steps of the scheduled-fade layer and steps where the
trap guard's counter is active are left alone. Each round is priced exactly from the next observations' wheat inventory
(both legs sit in the last slot: sell book = inv(s+1) + town use(s) - x, buy book = inv(s+2) + town use(s+1) + x);
when the last FG_K rounds average <= FG_MIN per unit the layer switches off for the game and sells its lot once.
"""
import hashlib
import io
import os
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(ROOT, "submissions", "v12_5_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard")
TAG = "v12_6"

LAYER = r'''
# ---------------------------------------------------------------------------
# Team 42 GFADE layer (outermost, __TAG__): generic fade of a rival's wheat churn at phases 1-3 (see gold/front/pack_v12_6.py).
_GF_CFG = __CFG__
_GF_STATE = {}
_GF_REPORT = {"sells": 0, "sold": 0, "buys": 0, "bought": 0, "off": 0, "liquidated": 0, "rounds": 0}


def _gf_sched_steps():
    try:
        sched = list(_SCH_NS["CFG"]["SCHED"])
        lead = int(_SCH_NS["CFG"].get("LEAD", 1))
        return set(sched) | {s - lead for s in sched}
    except Exception:
        return {326, 327, 374, 375, 418, 419, 434, 435, 486, 487}


_GF_SCHED = _gf_sched_steps()


def _gf_rival_n(flow, step, phase):
    """Mean size of the rival's recent churn cycles at `phase` (buy MIN_N+ at s0 = phase mod 4, sell MIN_N+ at s0 + 1),
    over the last 4 such cycles before `step`; 0 unless at least 2 of them churned."""
    sizes = []
    s0 = step - ((step - phase) % 4)
    if s0 >= step:
        s0 -= 4
    for k in range(4):
        s = s0 - 4 * k
        b, s1 = flow.get(s, 0), flow.get(s + 1, 0)
        if b <= -_GF_CFG["MIN_N"] and s1 >= _GF_CFG["MIN_N"]:
            sizes.append(min(-b, s1))
    return sum(sizes) / len(sizes) if len(sizes) >= _GF_CFG["HITS"] else 0


def _gf_pick_phase(flow, step):
    best, best_n = None, 0
    for p in (1, 2, 3):
        n = _gf_rival_n(flow, step, p)
        if n > best_n:
            best, best_n = p, n
    return best, best_n


def _gf_eval(obs, st, seat):
    """Exact pricing of the last round's legs from this step's wheat inventory (see module doc)."""
    step = int(obs["step"])
    inv_w = int(dict(obs["market"].get("inventory", {}) or {}).get("WHEAT", 10000))
    price, cons = _TG_NS["_price"], _TG_NS["_cons"]
    keep = []
    for lg in st.get("legs", []):
        if lg["step"] == step - 1:
            shops = lg["shops"]
            if lg["kind"] == "sell":
                book = inv_w + int(cons(shops, lg["step"]).get("WHEAT", 0)) - lg["x"]
                rev = sum(price("WHEAT", book + k) for k in range(lg["x"]))
                st["round"] = {"s0": lg["step"], "rev": rev, "x": lg["x"]}
            else:
                book = inv_w + int(cons(shops, lg["step"]).get("WHEAT", 0)) + lg["x"]
                cost = sum(price("WHEAT", book - k) for k in range(1, lg["x"] + 1))
                rd = st.get("round")
                if rd is not None and lg["step"] - rd["s0"] == 1:
                    m = rd["rev"] / max(1, rd["x"]) - cost / max(1, lg["x"])
                    st["round"] = None
                    st.setdefault("ms", []).append(m)
                    _GF_REPORT["rounds"] += 1
                    if _GF_CFG.get("LOG"):
                        _GF_REPORT.setdefault("cycles", []).append((rd["s0"], round(rd["rev"] - cost), round(m, 2)))
                    last = st["ms"][-_GF_CFG["FG_K"]:]
                    if len(last) >= _GF_CFG["FG_K"] and sum(last) <= _GF_CFG["FG_MIN"] * len(last) and not st["off"]:
                        st["off"] = True
                        _GF_REPORT["off"] += 1
                        _GF_REPORT["off_step"] = step
                        _GF_REPORT["off_ms"] = [round(v, 2) for v in last]
        elif lg["step"] >= step:
            keep.append(lg)
    st["legs"] = keep


def _gfade(obs, action, st, seat, tick_mem):
    step = int(obs["step"])
    if not isinstance(action, dict) or step < _GF_CFG["FROM"] or step > 717:
        return action
    flow = (tick_mem or {}).get("flow") or {}
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, (list, tuple))]
    live = [o for o in market if o]
    shops = list(obs["town"].get("unlocked_shops", []) or [])
    farm = obs["farms"][seat]
    money = float(farm.get("money", 0))
    quote = int(obs["market"]["prices"].get("WHEAT", 40))
    if st["off"]:
        if not st.get("liq") and step <= 716:
            st["liq"] = True
            try:
                shed_w = int(_project(obs, dict(action, market=live))[0].get("WHEAT", 0))
                y = int(min(_GF_CFG["XMAX"], shed_w - _fd_pickups(seat, step, 6)))
                if y >= 5 and _fd_place(market, ["SELL", "WHEAT", y]):
                    _GF_REPORT["liquidated"] += y
                    out = dict(action)
                    out["market"] = market[:10]
                    return out
            except Exception:
                pass
        return action
    if step in _GF_SCHED:
        return action
    try:
        if (_TG_NS["_MEM"].get(seat) or {}).get("cf_on"):
            return action
    except Exception:
        pass
    phase = step % 4
    p, n = _gf_pick_phase(flow, step)
    st["phase"] = p
    changed = False
    try:
        shed_w = int(_project(obs, dict(action, market=live))[0].get("WHEAT", 0))
    except Exception:
        return action
    if p is not None and phase == p and n > 0 and step <= 716:
        reserve = _fd_pickups(seat, step, 3)
        x = int(min(_GF_CFG["XMAX"], n, shed_w - reserve))
        if x >= 5 and _fd_place(market, ["SELL", "WHEAT", x]):
            st["sold"][step] = x
            st.setdefault("legs", []).append({"kind": "sell", "step": step, "x": x, "shops": shops})
            _GF_REPORT["sells"] += 1
            _GF_REPORT["sold"] += x
            changed = True
    elif (step - 1) in st["sold"] or (p is not None and phase == (p + 1) % 4 and n > 0):
        st["sold"].pop(step - 1, None)
        want = max(0, _GF_CFG["XMAX"] + _fd_pickups(seat, step, 4) - shed_w)
        pshed, pinvs = _project(obs, dict(action, market=live))[:2]
        carried = sum(int(v) for inv in pinvs for v in inv.values() if int(v) > 0)
        room = 100 - sum(int(v) for v in pshed.values()) - carried - 3
        cash = money - _GF_CFG["RESERVE"]
        want = int(max(0, min(want, room, cash // max(1, quote + 6))))
        if want >= 5 and _fd_place(market, ["BUY_PRODUCT", "WHEAT", want]):
            st.setdefault("legs", []).append({"kind": "buy", "step": step, "x": want, "shops": shops})
            _GF_REPORT["buys"] += 1
            _GF_REPORT["bought"] += want
            changed = True
    if not changed:
        return action
    out = dict(action)
    out["market"] = market[:10]
    return out


_PRE_GF_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    try:
        step = int(observation["step"])
        seat = int(observation["player"])
        st = _GF_STATE.get(seat)
        if st is None or step <= st["step"]:
            st = _GF_STATE[seat] = {"step": -1, "sold": {}, "legs": [], "off": False, "phase": None, "round": None}
        st["step"] = step
        tick_mem = (_TICK_NS.get("_MEM") or {}).get(seat)
        try:
            _gf_eval(observation, st, seat)
        except Exception:
            pass
        # hold the TICK layer off while a phase-3 churner is being faded (its buy-back needs the shed room at phase 0)
        if tick_mem is not None and not st["off"] and step >= _GF_CFG["FROM"]:
            flow = tick_mem.get("flow") or {}
            if _gf_rival_n(flow, step, 3) > 0:
                tick_mem["rival"] = True
                _GF_REPORT["tick_holds"] = _GF_REPORT.get("tick_holds", 0) + 1
    except Exception:
        st, tick_mem = None, None
    action = _PRE_GF_AGENT(observation, configuration)
    if st is None:
        return action
    try:
        return _gfade(observation, action, st, seat, tick_mem)
    except Exception:
        return action
'''


def main():
    args = [x for x in sys.argv[1:] if "=" not in x]
    kv = dict(x.split("=", 1) for x in sys.argv[1:] if "=" in x)
    out_dir = args[0] if args else os.path.join(ROOT, "submissions",
                                                 "v12_6_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade")
    cfg = {"XMAX": int(kv.get("XMAX", 90)), "MIN_N": int(kv.get("MIN_N", 15)), "RESERVE": float(kv.get("RESERVE", 1500)),
           "FROM": int(kv.get("FROM", 240)), "FG_K": int(kv.get("FG_K", 4)), "FG_MIN": float(kv.get("FG_MIN", -1.2)),
           "HITS": int(kv.get("HITS", 2)),
           "LOG": int(kv.get("LOG", 0))}
    raw = open(os.path.join(SRC, "main.py"), "rb").read()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8").replace("\r\n", "\n").rstrip("\n")
    for name in ("_GF_STATE", "_PRE_GF_AGENT", "_gfade"):
        assert name not in s, name
    for name in ("_TICK_NS", "_SCH_NS", "_TG_NS", "def _fd_pickups", "def _fd_place", "def _project"):
        assert name in s, name
    layer = LAYER.replace("__CFG__", repr(cfg)).replace("__TAG__", TAG)
    code = s + "\n\n" + layer.lstrip("\n")
    compile(code, "main.py", "exec")
    main = (code.replace("\n", "\r\n") if crlf else code).encode("utf-8")
    assert b"C:\\Users" not in main and b"C:/Users" not in main and b"/Users/cliff/" not in main
    notice = open(os.path.join(SRC, "NOTICE.txt"), "rb").read()
    h, rest = notice.split(b"\n\n", 1)
    h = h + (f" In {TAG} a GFADE layer fades a rival's wheat churn at phases 1-3 the same way (sell into its buy in the "
             f"last slot, buy back after its sale), holding the tick arbitrage off meanwhile, with the same profit check.").encode()
    notice = h + b"\n\n" + rest
    lic = open(os.path.join(SRC, "LICENSE.txt"), "rb").read()
    os.makedirs(out_dir, exist_ok=True)
    members = [("main.py", main), ("LICENSE.txt", lic), ("NOTICE.txt", notice)]
    for n, d in members:
        open(os.path.join(out_dir, n), "wb").write(d)
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for n, d in members:
            info = tarfile.TarInfo(n)
            info.size = len(d)
            info.mode = 0o644
            info.mtime = 0
            tar.addfile(info, io.BytesIO(d))
    open(os.path.join(out_dir, "submission.tar.gz"), "wb").write(buf.getvalue())
    print("out", out_dir)
    print("cfg", cfg)
    print("main.py", hashlib.sha256(main).hexdigest())
    print("tar.gz", hashlib.sha256(buf.getvalue()).hexdigest())


if __name__ == "__main__":
    main()
