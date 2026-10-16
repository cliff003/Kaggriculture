r"""Build v12_10: v12_9 plus the SQUEEZE layer (premium goods must not wait a step because the order list is full).

    .venv/bin/python gold/front/pack_v12_10.py [OUT_DIR] [MIN=5] [RATIO=2.0] [LOG=0]

Found 9/28 on 200 live replays: in every game, about ten times a game (almost always at hour 0, when the tape hires
7-9 hands), the market list is already full, so the eager-sale layer (which only inserts when a slot is free) leaves
milk / strawberries / wool in the shed until the next step, after the rival's own hour-0 sale has moved the quote:
~105 units a game, quote drop x units about -663 a game. This layer runs just inside the trap guard (so the guard
still simulates the final list): when a premium item with a quote inside the eager band sits unsold in the
projected shed (>= MIN units) and the list has no free slot, it reuses an empty pad, or displaces the lowest-stake
SELL of fertilizer / eggs / carrots / tomatoes / melons when the premium stake is at least RATIO times larger, puts
the premium SELL at index 0 and re-issues the displaced order at the next step. It never touches HIRE, BUY_* or wheat
orders (TICK / FADE / lead-sell own those).
"""
import hashlib
import io
import os
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(ROOT, "submissions", "v12_9_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n")
TAG = "v12_10"
MARK = "# ---------------------------------------------------------------------------\n# Team 42 TICK TRAP GUARD layer"

LAYER = r'''
# ---------------------------------------------------------------------------
# Team 42 SQUEEZE layer (__TAG__): a premium sale must not wait a step for a free order slot (see gold/front/pack_v12_10.py).
_SQ_CFG = __CFG__
_SQ_STATE = {}
_SQ_REPORT = {"sells": 0, "units": 0, "pads": 0, "displaced": 0, "reissued": 0, "dropped": 0}
_SQ_DISPLACEABLE = ("FERTILIZER", "EGG", "CARROT", "TOMATO", "MELON")


def _squeeze(obs, action, st):
    step = int(_g(obs, "step", 0))
    if step < 288 or step > 716 or not isinstance(action, dict):
        return action
    market = [list(o) if isinstance(o, (list, tuple)) else o for o in (action.get("market") or [])]
    changed = False
    # re-issue what an earlier step displaced, while there is room
    if st.get("pending"):
        live_n = sum(1 for o in market if o)
        keep = []
        for o in st["pending"]:
            if live_n < 10 or any(not x for x in market):
                if live_n < 10:
                    market.append(list(o))
                    live_n += 1
                else:
                    i = next(i for i, x in enumerate(market) if not x)
                    market[i] = list(o)
                _SQ_REPORT["reissued"] += 1
                changed = True
            else:
                keep.append(o)
        st["pending"] = keep
        if len(st["pending"]) > 0 and step - st.get("pending_step", step) > 3:
            _SQ_REPORT["dropped"] += len(st["pending"])
            st["pending"] = []
    live = [o for o in market if o]
    if len(live) >= 10 or any(not x for x in market):
        prices = _g(_g(obs, "market"), "prices", {})
        try:
            shed = _project(obs, dict(action, market=live))[0]
        except Exception:
            return action if not changed else dict(action, market=market[:10])
        sold = {o[1] for o in live if o[0] == "SELL" and len(o) >= 2}
        wants = []
        for item, (lo, hi) in _EAGER_BANDS.items():
            spare = int(shed.get(item, 0))
            quote = int(_g(prices, item, 0))
            if item in sold or spare < _SQ_CFG["MIN"]:
                continue
            if quote < max(2.0, lo * _MKT[item][0]) or quote > hi * _MKT[item][0]:
                continue
            wants.append((spare * quote, item, spare))
        wants.sort(reverse=True)
        for stake, item, spare in wants:
            pad = next((i for i, x in enumerate(market) if not x), None)
            if pad is not None:
                market.pop(pad)
                market.insert(0, ["SELL", item, spare])
                _SQ_REPORT["pads"] += 1
            else:
                best = None
                for i, o in enumerate(market):
                    if o and o[0] == "SELL" and len(o) >= 3 and o[1] in _SQ_DISPLACEABLE:
                        try:
                            s = int(o[2]) * int(_g(prices, o[1], 0))
                        except Exception:
                            continue
                        if s * _SQ_CFG["RATIO"] <= stake and (best is None or s < best[0]):
                            best = (s, i)
                if best is None:
                    continue
                displaced = market.pop(best[1])
                st.setdefault("pending", []).append(displaced)
                st["pending_step"] = step
                market.insert(0, ["SELL", item, spare])
                _SQ_REPORT["displaced"] += 1
            _SQ_REPORT["sells"] += 1
            _SQ_REPORT["units"] += spare
            changed = True
            if _SQ_CFG.get("LOG"):
                _SQ_REPORT.setdefault("log", []).append((step, item, spare, int(_g(prices, item, 0))))
    if not changed:
        return action
    out = dict(action)
    out["market"] = market[:10]
    return out


_PRE_SQ_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    action = _PRE_SQ_AGENT(observation, configuration)
    try:
        step = int(_g(observation, "step", 0))
        seat = int(_g(observation, "player", 0))
        st = _SQ_STATE.get(seat)
        if st is None or step <= st["step"]:
            st = _SQ_STATE[seat] = {"step": -1, "pending": []}
        st["step"] = step
        return _squeeze(observation, action, st)
    except Exception:
        return action

'''


def main():
    args = [x for x in sys.argv[1:] if "=" not in x]
    kv = dict(x.split("=", 1) for x in sys.argv[1:] if "=" in x)
    out_dir = args[0] if args else os.path.join(
        ROOT, "submissions", "v12_10_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_sq")
    cfg = {"MIN": int(kv.get("MIN", 5)), "RATIO": float(kv.get("RATIO", 2.0)), "LOG": int(kv.get("LOG", 0))}
    raw = open(os.path.join(SRC, "main.py"), "rb").read()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8").replace("\r\n", "\n")
    for name in ("_SQ_STATE", "_PRE_SQ_AGENT", "_squeeze"):
        assert name not in s, name
    for name in ("_EAGER_BANDS", "def _project(", "def _g(", "_MKT"):
        assert name in s, name
    assert s.count(MARK) == 1
    i = s.index(MARK)
    code = s[:i].rstrip("\n") + "\n\n" + LAYER.replace("__CFG__", repr(cfg)).replace("__TAG__", TAG).lstrip("\n") + "\n" + s[i:]
    compile(code, "main.py", "exec")
    ns = {"__name__": "cand_check"}
    exec(compile(code, "main.py", "exec"), ns)
    last = [v for v in ns.values() if callable(v)][-1]
    assert getattr(last, "__name__", "") == "agent", last
    main = (code.replace("\n", "\r\n") if crlf else code).encode("utf-8")
    assert b"C:\\Users" not in main and b"/Users/cliff/" not in main
    notice = open(os.path.join(SRC, "NOTICE.txt"), "rb").read()
    h, rest = notice.split(b"\n\n", 1)
    h = h + (f" In {TAG} a premium sale that finds the order list full reuses a pad or displaces the smallest fertilizer / "
             f"egg / carrot / tomato / melon sale to the next step instead of waiting.").encode()
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
