r"""Build the v12_5 package: v12_4 with a FADE profit guard inside the outermost tick-trap guard layer.

    .venv/bin/python gold/front/pack_v12_5.py [OUT_DIR] [FG_K=4] [FG_MIN=0.0] [LOG=0]

FADE (tools/add_fade.py) sells a wheat lot in the last slot at s % 4 == 0 after a flagged churner's buy and buys it back
in the last slot of s + 1 after its unwind. A rival that knows this can churn on some ticks and do the opposite on
others (sell first at s % 4 == 0, buy first at s + 1); FADE keeps trading (the flow rule still sees churn ticks) and
loses about 9 per unit on the reversed ticks. This build:
  1. gives the FADE layer an "off" switch (its per-seat state dict);
  2. extends the trap-guard layer: FADE's legs sit in the last order slot, so their fills follow exactly from the next
     observation's wheat inventory (sell leg: book = inv(s0 + 1) + town use - x; buy leg: book = inv(s1 + 1) + x) and
     the engine's price function. A round is the sell leg plus the buy leg of the next step; per unit margin
     m = revenue / sold - cost / bought. When the last FG_K rounds average m <= FG_MIN, FADE is switched off for the
     rest of the game (TEL["fd_off_step"]) and the FADE layer sells its lot once.
Everything else is byte-identical to v12_4 (same base blob, same layers, same CFG values).
"""
import hashlib
import io
import os
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import mk_tguard  # noqa: E402

SRC = os.path.join(ROOT, "submissions", "v12_4_own_cha22_tick_fade_resume_late_sched_trap_tomato")
TAG = "v12_5"

FADE_OLD = '''    st["step"] = step
    if not isinstance(action, dict) or step < 240 or step > 717:
        return action
    mem = (_TICK_NS.get("_MEM") or {}).get(seat) or {}
'''
FADE_NEW = '''    st["step"] = step
    if not isinstance(action, dict) or step < 240 or step > 717:
        return action
    if st.get("off"):   # v12_5: switched off by the outer guard once the fade rounds stop paying; sell the lot once
        if not st.get("liq") and step <= 716:
            st["liq"] = True
            try:
                market = [list(o) for o in (action.get("market") or []) if isinstance(o, (list, tuple))]
                shed_w = int(_project(obs, dict(action, market=[o for o in market if o]))[0].get("WHEAT", 0))
                y = int(min(_FD_XMAX, shed_w - _fd_pickups(seat, step, 6)))
                if y >= 5 and _fd_place(market, ["SELL", "WHEAT", y]):
                    _FD_REPORT["liquidated"] = _FD_REPORT.get("liquidated", 0) + y
                    out = dict(action)
                    out["market"] = market[:10]
                    return out
            except Exception:
                pass
        return action
    mem = (_TICK_NS.get("_MEM") or {}).get(seat) or {}
'''

# --- guard layer edits (anchors are unique lines of mk_tguard.LAYER) ---
A1_OLD = '''def _prebuy_hits(fl, step):'''
A1_NEW = '''def _fd_counts():
    rep = _NS.get("_FD_REPORT") or {}
    return (int(rep.get("sells", 0)), int(rep.get("sold", 0)), int(rep.get("buys", 0)), int(rep.get("bought", 0)))


def _fd_eval(observation, mem, step, me):
    """FADE legs sit in the last order slot, so their fills are fixed by the next observation's wheat inventory:
    sell leg at s0: book before the sell = inv(s0 + 1) + town wheat use(s0) - x, revenue = sum price(book + k);
    buy leg at s1: book before the buy = inv(s1 + 1) + x, cost = sum price(book - k). A round is one sell leg and
    the buy leg of the next step; m = revenue / sold - cost / bought (per unit)."""
    inv_w = int(dict(_get(_get(observation, "market", {}) or {}, "inventory", {}) or {}).get("WHEAT", 10000))
    keep = []
    for lg in mem.get("fd_legs") or []:
        if lg["step"] == step - 1:
            if lg["kind"] == "sell":
                inv_b = inv_w + lg["cons"] - lg["x"]
                rev = sum(_price("WHEAT", inv_b + k) for k in range(lg["x"]))
                mem["fd_round"] = {"s0": lg["step"], "rev": rev, "x": lg["x"]}
            else:
                inv_b = inv_w + lg["x"]
                cost = sum(_price("WHEAT", inv_b - k) for k in range(1, lg["x"] + 1))
                rd = mem.get("fd_round")
                if rd is not None and lg["step"] - rd["s0"] == 1:
                    m = rd["rev"] / max(1, rd["x"]) - cost / max(1, lg["x"])
                    mem["fd_round"] = None
                    if CFG.get("LOG"):
                        TEL.setdefault("fd_cycles", []).append((rd["s0"], round(rd["rev"] - cost), round(m, 2), True))
                    mem.setdefault("fd_ms", []).append(m)
                    last = mem["fd_ms"][-CFG["FG_K"]:]
                    if len(last) >= CFG["FG_K"] and sum(last) <= CFG["FG_MIN"] * len(last):
                        fst = (_NS.get("_FD_STATE") or {}).get(me)
                        if fst is not None and not fst.get("off"):
                            fst["off"] = True
                            TEL["fd_off_step"] = step
                            TEL["fd_off_ms"] = [round(v, 2) for v in last]
        elif lg["step"] >= step:
            keep.append(lg)
    mem["fd_legs"] = keep


def _prebuy_hits(fl, step):'''

A2_OLD = '''    mem["last"] = step
    tick_mem = None
    try:
        tick_mem = _NS["_TICK_NS"]["_MEM"].get(me)'''
A2_NEW = '''    mem["last"] = step
    tick_mem = None
    try:
        if CFG.get("FG"):
            _fd_eval(observation, mem, step, me)
    except Exception:
        pass
    try:
        tick_mem = _NS["_TICK_NS"]["_MEM"].get(me)'''

A3_OLD = '''    pend_before = (tick_mem or {}).get("pend") if tick_mem is not None else None
    a = _BASE(observation, configuration)'''
A3_NEW = '''    pend_before = (tick_mem or {}).get("pend") if tick_mem is not None else None
    fd0 = _fd_counts()
    a = _BASE(observation, configuration)'''

A4_OLD = '''            mem["prev"] = {"step": step, "money": float(_get(_get(observation, "farms")[me], "money", 0)), "E": E,
                           "delta": delta, "traded": traded, "inv": inv0, "shops": shops,
                           "tick": tick and pend_before is None, "tsell": pend_before is not None, "cf": cfd}'''
A4_NEW = '''            if CFG.get("FG"):
                fd1 = _fd_counts()
                if fd1[0] > fd0[0] and fd1[1] > fd0[1] and step % 4 == 0:
                    mem.setdefault("fd_legs", []).append({"kind": "sell", "step": step, "x": fd1[1] - fd0[1],
                                                          "cons": int(_cons(shops, step).get("WHEAT", 0))})
                elif fd1[2] > fd0[2] and fd1[3] > fd0[3] and step % 4 == 1:
                    mem.setdefault("fd_legs", []).append({"kind": "buy", "step": step, "x": fd1[3] - fd0[3]})
            mem["prev"] = {"step": step, "money": float(_get(_get(observation, "farms")[me], "money", 0)), "E": E,
                           "delta": delta, "traded": traded, "inv": inv0, "shops": shops,
                           "tick": tick and pend_before is None, "tsell": pend_before is not None, "cf": cfd}'''

GUARD_HEAD = "# Team 42 TICK TRAP GUARD layer (outermost, v12_3)."


def guard_layer(cfg):
    layer = mk_tguard.LAYER
    for old, new in ((A1_OLD, A1_NEW), (A2_OLD, A2_NEW), (A3_OLD, A3_NEW), (A4_OLD, A4_NEW)):
        assert layer.count(old) == 1, old[:60]
        layer = layer.replace(old, new)
    return layer.replace("__CFG__", repr(cfg))


def main():
    args = [x for x in sys.argv[1:] if "=" not in x]
    kv = dict(x.split("=", 1) for x in sys.argv[1:] if "=" in x)
    out_dir = args[0] if args else os.path.join(ROOT, "submissions",
                                                 "v12_5_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard")
    raw = open(os.path.join(SRC, "main.py"), "rb").read()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8").replace("\r\n", "\n")
    # 1. FADE off switch
    assert s.count(FADE_OLD) == 1
    s = s.replace(FADE_OLD, FADE_NEW)
    # 2. the guard tail: same CFG as v12_4 plus the FADE guard entries, rebuilt from mk_tguard.LAYER
    i = s.index(GUARD_HEAD)
    i = s.rfind("# " + "-" * 75, 0, i)
    head = s[:i].rstrip("\n")
    old_tail = s[i:]
    j = old_tail.index("CFG = ")
    old_cfg = eval(old_tail[j + len("CFG = "):old_tail.index("\n", j)])
    cfg = dict(old_cfg)
    cfg.update({"FG": 1, "FG_K": int(kv.get("FG_K", 4)), "FG_MIN": float(kv.get("FG_MIN", -1.2)), "LOG": int(kv.get("LOG", 0))})
    layer = guard_layer(cfg)
    assert "'''" not in layer
    for name in ("_PRE_TG_AGENT", "_TG_NS", "_TG_SRC", "_TG_AGENT"):
        assert name not in head, name
    tail = [
        "", "",
        "# " + "-" * 75,
        f"# Team 42 TICK TRAP GUARD layer (outermost, v12_3; {TAG} adds a FADE profit guard). Some rivals trap the TICK",
        "# layer's wheat round trip: at s % 4 == 0 they buy 80-90 wheat in slot 0 and sell as much in slot 9, against our",
        "# last-slot tick buy (net flow zero, so the flow guard cannot see it), or they buy one step before our tick buy",
        "# and sell with our tick sell. Money moves only in the market, so each step the cash of our own final orders is",
        "# simulated alone with the engine's rules and compared with the realized cash one step later. Three of the last",
        "# four tick cycles losing 40+ (or the prebuy flow pattern twice) pause TICK for the game, and a counter sells a",
        "# wheat lot into the rival's lift (middle slot) and buys it back in the last slot after its sell, while that",
        f"# keeps paying. {TAG}: each FADE round (sell leg at s % 4 == 0, buy leg at s + 1) is priced exactly from the",
        "# next observation's wheat inventory (both legs sit in the last order slot); when the last four rounds average",
        "# no gain per unit, the FADE layer is switched off for the rest of the game and its lot is sold.",
        "_TG_SRC = r'''" + layer + "'''",
        "_PRE_TG_AGENT = globals().pop(\"agent\")   # pop first: the loader takes the last callable in module order",
        "_TG_NS = {\"__name__\": \"tick_trap_guard\", \"_BASE\": _PRE_TG_AGENT, \"_PROJECT\": _project, \"_NS\": globals()}",
        "exec(compile(_TG_SRC, \"tick_trap_guard\", \"exec\"), _TG_NS)",
        "_TG_AGENT = _TG_NS[\"agent\"]",
        "", "",
        "def agent(observation, configuration=None):",
        "    return _TG_AGENT(observation, configuration)",
        "",
    ]
    code = head + "\n".join(tail)
    compile(code, "main.py", "exec")
    main = (code.replace("\n", "\r\n") if crlf else code).encode("utf-8")
    assert b"C:\\Users" not in main and b"C:/Users" not in main and b"/Users/cliff/" not in main
    notice = open(os.path.join(SRC, "NOTICE.txt"), "rb").read()
    h, rest = notice.split(b"\n\n", 1)
    h = h + (f" In {TAG} the FADE layer is switched off for the game once its rounds (measured by the same cash check) "
             f"stop paying.").encode()
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
    print("crlf", crlf)
    print("main.py", hashlib.sha256(main).hexdigest())
    print("tar.gz", hashlib.sha256(buf.getvalue()).hexdigest())


if __name__ == "__main__":
    main()
