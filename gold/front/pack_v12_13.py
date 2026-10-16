r"""Build v12_13: v12_12 with the base's wheat sales capped at the base's own wheat while a fade lot is held.

    .venv/bin/python gold/front/pack_v12_13.py [OUT_DIR]

Trace of the live game against Ken_Ken_Pa (9/28, scratchpad lottrace.py): the base cha22 treats the fade lot in the shed
as its own surplus and sells it (typically at phase 3, one step before the fade's own sell into the rival's lift), then
its supply module buys the "shortage" back at phase 0 in lockstep with the rival's buy. FADE sold on only 44 of its 71
restocks against Ken_Ken_Pa, 32 of 56 against Wang H2O. Hiding the lot from the base instead (tried first) starved its
feeding and supply modules (-5k to -17k per game), so v12_13 keeps the base's view and only caps its SELL WHEAT orders at
the wheat the base owns (shed minus the fade lot, counted from the fade layers' own restocks and sells, clamped to the
shed) while the faded rival is still churning; when the rival goes quiet the lot is left to the base's own surplus sale as
before; the cap is lifted at hour 23 so the base's warehouse close can still sell wheat to make room for the day-end
deposit, and GFADE's restock goes back to the full carried reserve (its rivals are irregular; v12_12's bigger lots lost
2.4k against american gothic). Everything else is byte-identical to v12_12.
"""
import hashlib
import io
import os
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(ROOT, "submissions", "v12_12_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room")
TAG = "v12_13"

HELPERS = '''
_FD_HIDDEN = {}   # v12_13: seat -> wheat units of the fade lots (restocks add, fade sells subtract, clamped to the shed)


def _fd_hidden_clamp(seat, obs):
    try:
        w = int((obs["private"].get("shed") or {}).get("WHEAT", 0))
    except Exception:
        return
    _FD_HIDDEN[seat] = max(0, min(int(_FD_HIDDEN.get(seat, 0)), w))


def _fd_cap_sells(market, obs, lot):
    """Cap the inner layers' SELL WHEAT orders at the wheat that is not the fade lot. Returns True when changed."""
    try:
        own = max(0, int((obs["private"].get("shed") or {}).get("WHEAT", 0)) - int(lot))
    except Exception:
        return False
    changed = False
    for o in market:
        if o and o[0] == "SELL" and len(o) >= 3 and o[1] == "WHEAT":
            try:
                q = int(o[2])
            except Exception:
                continue
            keep = max(0, min(q, own))
            own -= keep
            if keep != q:
                o[2] = keep   # a zero-quantity order keeps the later slots in place
                changed = True
    return changed
'''

EDITS = [
    ('_FD_REPORT = {"sells": 0, "sold": 0, "buys": 0, "bought": 0, "active_steps": 0}\n',
     '_FD_REPORT = {"sells": 0, "sold": 0, "buys": 0, "bought": 0, "active_steps": 0}\n' + HELPERS),
    # FADE: reset, clamp, cap, sells, buys, liquidation
    ('        st = _FD_STATE[seat] = {"step": -1, "sold": {}}\n    st["step"] = step\n',
     '        st = _FD_STATE[seat] = {"step": -1, "sold": {}}\n        _FD_HIDDEN[seat] = 0\n    st["step"] = step\n    _fd_hidden_clamp(seat, obs)\n'),
    ('    quote = int(prices.get("WHEAT", 40))\n    changed = False\n    try:\n        shed_w = int(_project(obs, dict(action, market=[o for o in market if o]))[0].get("WHEAT", 0))\n',
     '    quote = int(prices.get("WHEAT", 40))\n    changed = False\n'
     '    lot = int(_FD_HIDDEN.get(seat, 0))\n'
     '    if lot > 0 and step % 24 != 23 and _fd_rival_n(mem, step - step % 4) > 0 and _fd_cap_sells(market, obs, lot):   # v12_13: the base must not dump the lot (except at its hour-23 warehouse close)\n'
     '        changed = True\n'
     '    try:\n        shed_w = int(_project(obs, dict(action, market=[o for o in market if o]))[0].get("WHEAT", 0))\n'),
    ('                    _FD_REPORT["liquidated"] = _FD_REPORT.get("liquidated", 0) + y\n',
     '                    _FD_REPORT["liquidated"] = _FD_REPORT.get("liquidated", 0) + y\n                    _FD_HIDDEN[seat] = max(0, _FD_HIDDEN.get(seat, 0) - y)\n'),
    ('                    st["sold"][step] = (x, shed_w)\n',
     '                    st["sold"][step] = (x, shed_w)\n                    _FD_HIDDEN[seat] = max(0, _FD_HIDDEN.get(seat, 0) - x)\n'),
    ('                _FD_REPORT["bought"] += want\n',
     '                _FD_REPORT["bought"] += want\n                _FD_HIDDEN[seat] = _FD_HIDDEN.get(seat, 0) + want\n'),
    # GFADE: reset, cap, sells, buys, liquidation
    ('            st = _GF_STATE[seat] = {"step": -1, "sold": {}, "legs": [], "off": False, "phase": None, "round": None}\n',
     '            st = _GF_STATE[seat] = {"step": -1, "sold": {}, "legs": [], "off": False, "phase": None, "round": None}\n            _FD_HIDDEN[seat] = 0\n'),
    ('    st["phase"] = p\n    changed = False\n    try:\n        shed_w = int(_project(obs, dict(action, market=live))[0].get("WHEAT", 0))\n',
     '    st["phase"] = p\n    changed = False\n'
     '    lot = int(_FD_HIDDEN.get(seat, 0))\n'
     '    if lot > 0 and step % 24 != 23 and p is not None and n > 0 and _fd_cap_sells(live, obs, lot):   # v12_13: the base must not dump the lot (except at its hour-23 warehouse close)\n'
     '        changed = True\n'
     '    try:\n        shed_w = int(_project(obs, dict(action, market=live))[0].get("WHEAT", 0))\n'),
    ('                    _GF_REPORT["liquidated"] += y\n',
     '                    _GF_REPORT["liquidated"] += y\n                    _FD_HIDDEN[seat] = max(0, _FD_HIDDEN.get(seat, 0) - y)\n'),
    ('            st["sold"][step] = x\n',
     '            st["sold"][step] = x\n            _FD_HIDDEN[seat] = max(0, _FD_HIDDEN.get(seat, 0) - x)\n'),
    ('            _GF_REPORT["bought"] += want\n',
     '            _GF_REPORT["bought"] += want\n            _FD_HIDDEN[seat] = _FD_HIDDEN.get(seat, 0) + want\n'),
    ('        carried = _fd_drop_reserve(seat, step, pinvs)   # v12_12: only what the tape drops before the next sell\n        room = 100 - sum(int(v) for v in pshed.values()) - carried - 3\n        cash = money - _GF_CFG["RESERVE"]\n',
     '        carried = sum(int(v) for inv in pinvs for v in inv.values() if int(v) > 0)   # v12_13: GFADE keeps the full reserve (irregular rivals)\n        room = 100 - sum(int(v) for v in pshed.values()) - carried - 3\n        cash = money - _GF_CFG["RESERVE"]\n'),
]


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 and "=" not in sys.argv[1] else os.path.join(
        ROOT, "submissions", "v12_13_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room_cap")
    raw = open(os.path.join(SRC, "main.py"), "rb").read()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8").replace("\r\n", "\n")
    assert "_FD_HIDDEN" not in s
    g0 = s.index("def _gfade(")
    assert "live = [" in s[g0:s.index('    st["phase"] = p\n', g0)], "GFADE builds `live` before the anchor"
    for old, new in EDITS:
        assert s.count(old) == 1, (s.count(old), old[:70])
        s = s.replace(old, new)
    compile(s, "main.py", "exec")
    main = (s.replace("\n", "\r\n") if crlf else s).encode("utf-8")
    assert b"C:\\Users" not in main and b"/Users/cliff/" not in main
    notice = open(os.path.join(SRC, "NOTICE.txt"), "rb").read()
    h, rest = notice.split(b"\n\n", 1)
    h = h + (f" In {TAG} the base's own wheat sales are capped at the wheat that is not part of those lots while the rival keeps churning.").encode()
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
    print("main.py", hashlib.sha256(main).hexdigest())
    print("tar.gz", hashlib.sha256(buf.getvalue()).hexdigest())


if __name__ == "__main__":
    main()
