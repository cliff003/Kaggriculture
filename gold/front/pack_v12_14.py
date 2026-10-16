r"""Build v12_14: v12_13 with the base's wheat-sale cap applied only against rivals churning at least MIN_N units a cycle.

    .venv/bin/python gold/front/pack_v12_14.py [OUT_DIR] [MIN_N=40]

v12_13's cap (the base may not sell the fade lot while the faded rival keeps churning) pays against big churners but lost
2 of 24 panel games to the 30-unit churner emulator (research/panel/emu_tick30) and -193/game in the 917 replays' band of
10-34-unit churners: against small lots the fade's edge per round is small and blocking the base's own wheat sales costs
more than it saves. v12_14 gates the cap on the rival's recent mean churn size (FADE: _fd_rival_n, GFADE: its phase's n)
being at least MIN_N. Mini panel of the gated build: emu_tick30 24/0 +6478 (v12_12 level), emu_tick0 +37248 (v12_13
level), emu_antifade +3086. Everything else is byte-identical to v12_13.
"""
import hashlib
import io
import os
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(ROOT, "submissions", "v12_13_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room_cap")
TAG = "v12_14"


def main():
    args = [x for x in sys.argv[1:] if "=" not in x]
    kv = dict(x.split("=", 1) for x in sys.argv[1:] if "=" in x)
    min_n = int(kv.get("MIN_N", 40))
    out_dir = args[0] if args else os.path.join(
        ROOT, "submissions", "v12_14_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room_cap40")
    raw = open(os.path.join(SRC, "main.py"), "rb").read()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8").replace("\r\n", "\n")
    edits = [
        ("    if lot > 0 and step % 24 != 23 and _fd_rival_n(mem, step - step % 4) > 0 and _fd_cap_sells(market, obs, lot):",
         "    if lot > 0 and step % 24 != 23 and _fd_rival_n(mem, step - step % 4) >= _FD_CAP_MIN_N and _fd_cap_sells(market, obs, lot):"),
        ("    if lot > 0 and step % 24 != 23 and p is not None and n > 0 and _fd_cap_sells(live, obs, lot):",
         "    if lot > 0 and step % 24 != 23 and p is not None and n >= _FD_CAP_MIN_N and _fd_cap_sells(live, obs, lot):"),
        ("_FD_HIDDEN = {}   # v12_13",
         f"_FD_CAP_MIN_N = {min_n}   # {TAG}: the base's wheat sales are capped only against rivals churning this much a cycle\n_FD_HIDDEN = {{}}   # v12_13"),
    ]
    assert "_FD_CAP_MIN_N" not in s
    for old, new in edits:
        assert s.count(old) == 1, old[:60]
        s = s.replace(old, new)
    compile(s, "main.py", "exec")
    main = (s.replace("\n", "\r\n") if crlf else s).encode("utf-8")
    assert b"C:\\Users" not in main and b"/Users/cliff/" not in main
    notice = open(os.path.join(SRC, "NOTICE.txt"), "rb").read()
    h, rest = notice.split(b"\n\n", 1)
    h = h + (f" In {TAG} that cap applies only against rivals whose wheat round trips are at least {min_n} units.").encode()
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
    print("out", out_dir, "MIN_N", min_n)
    print("main.py", hashlib.sha256(main).hexdigest())
    print("tar.gz", hashlib.sha256(buf.getvalue()).hexdigest())


if __name__ == "__main__":
    main()
