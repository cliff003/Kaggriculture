r"""Build v12_12: v12_11 with a tape-based room reserve for the FADE / GFADE restock (bigger fade lots).

    .venv/bin/python gold/front/pack_v12_12.py [OUT_DIR] [HORIZON=3] [PER_HARVEST=2]

Audit of 60 live replays (9/28, scratchpad roomscan.py): at the fade restock steps the hands carry 39 units on average,
and the restock reserved room for all of it ("a DROP into a full shed deletes goods"), so the fade lot averaged 47 units
while the rival churned 60-90. The lot only sits in the shed until the next phase-0 sell (3 steps), and the base's route
tape says exactly which units DROP in those steps: v12_12 reserves what those units carry (plus PER_HARVEST units per
HARVEST / COLLECT_FERTILIZER they do before dropping) and, when a day end (hour 23, engine auto-deposit) falls inside the
horizon, everything carried, as before. Units without a tape route keep the old full reserve. Everything else is
byte-identical to v12_11.
"""
import hashlib
import io
import os
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(ROOT, "submissions", "v12_11_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind")
TAG = "v12_12"

HELPER = '''

def _fd_drop_reserve(seat, step, pinvs, horizon=__HORIZON__, per_harvest=__PER_HARVEST__):
    """v12_12: shed room to keep for the goods the route's units will DROP within `horizon` steps (the fade lot is sold
    again at the next phase-0 step). Falls back to everything carried without a tape route or across a day end."""
    carried_all = sum(int(v) for inv in pinvs for v in inv.values() if int(v) > 0)
    try:
        ns = globals().get("_BASE_NS") or globals()
        chassis = ns["_IMPL"].chassis
        native = chassis.players.get(seat)
        if not native or native.get("route") is None:
            return carried_all
        reserve = 0
        pending = {}
        for t in range(step + 1, min(719, step + 1 + horizon)):
            if t % 24 == 23:
                return carried_all
            tape = chassis.routes.get(2 if t >= 648 else native["route"]) or []
            a = tape[t] if t < len(tape) and isinstance(tape[t], dict) else {}
            units = [a.get("farmer") or ["PASS"]] + list(a.get("hands") or [])
            for k, c in enumerate(units):
                if not (isinstance(c, list) and c):
                    continue
                if c[0] in ("HARVEST", "COLLECT_FERTILIZER"):
                    pending[k] = pending.get(k, 0) + per_harvest
                elif c[0] == "DROP":
                    inv = pinvs[k] if k < len(pinvs) else {}
                    reserve += sum(int(v) for v in inv.values() if int(v) > 0) + pending.pop(k, 0)
        return int(min(carried_all, reserve))
    except Exception:
        return carried_all
'''

EDITS = [
    # helper after _fd_pickups
    ('def _fd_rival_n(mem, step):\n', HELPER.lstrip("\n") + '\n\ndef _fd_rival_n(mem, step):\n'),
    # FADE restock
    ('        pshed, pinvs = _project(obs, dict(action, market=[o for o in market if o]))[:2]\n'
     '        carried = sum(int(v) for inv in pinvs for v in inv.values() if int(v) > 0)\n'
     '        room = 100 - sum(int(v) for v in pshed.values()) - carried - 3\n'
     '        cash = money - _FD_RESERVE\n',
     '        pshed, pinvs = _project(obs, dict(action, market=[o for o in market if o]))[:2]\n'
     '        carried = _fd_drop_reserve(seat, step, pinvs)   # v12_12: only what the tape drops before the next sell\n'
     '        room = 100 - sum(int(v) for v in pshed.values()) - carried - 3\n'
     '        cash = money - _FD_RESERVE\n'),
    # GFADE restock
    ('        pshed, pinvs = _project(obs, dict(action, market=live))[:2]\n'
     '        carried = sum(int(v) for inv in pinvs for v in inv.values() if int(v) > 0)\n'
     '        room = 100 - sum(int(v) for v in pshed.values()) - carried - 3\n'
     '        cash = money - _GF_CFG["RESERVE"]\n',
     '        pshed, pinvs = _project(obs, dict(action, market=live))[:2]\n'
     '        carried = _fd_drop_reserve(seat, step, pinvs)   # v12_12: only what the tape drops before the next sell\n'
     '        room = 100 - sum(int(v) for v in pshed.values()) - carried - 3\n'
     '        cash = money - _GF_CFG["RESERVE"]\n'),
]


def main():
    args = [x for x in sys.argv[1:] if "=" not in x]
    kv = dict(x.split("=", 1) for x in sys.argv[1:] if "=" in x)
    out_dir = args[0] if args else os.path.join(
        ROOT, "submissions", "v12_12_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room")
    horizon, per_h = int(kv.get("HORIZON", 3)), int(kv.get("PER_HARVEST", 2))
    raw = open(os.path.join(SRC, "main.py"), "rb").read()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8").replace("\r\n", "\n")
    assert "_fd_drop_reserve" not in s
    for old, new in EDITS:
        new = new.replace("__HORIZON__", str(horizon)).replace("__PER_HARVEST__", str(per_h))
        assert s.count(old) == 1, old[:80]
        s = s.replace(old, new)
    compile(s, "main.py", "exec")
    main = (s.replace("\n", "\r\n") if crlf else s).encode("utf-8")
    assert b"C:\\Users" not in main and b"/Users/cliff/" not in main
    notice = open(os.path.join(SRC, "NOTICE.txt"), "rb").read()
    h, rest = notice.split(b"\n\n", 1)
    h = h + (f" In {TAG} the room kept free when restocking those lots covers only the goods the route brings to the shed before the lot is sold again.").encode()
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
    print("out", out_dir, "horizon", horizon, "per_harvest", per_h)
    print("main.py", hashlib.sha256(main).hexdigest())
    print("tar.gz", hashlib.sha256(buf.getvalue()).hexdigest())


if __name__ == "__main__":
    main()
