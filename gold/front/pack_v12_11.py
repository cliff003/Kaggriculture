r"""Build v12_11: v12_9 with the fade lots wound down before the end of the game.

    .venv/bin/python gold/front/pack_v12_11.py [OUT_DIR]

Seen 9/28 in the live game against Ilya & Yurnero (slot-0 wheat churner): the rival churned through step 716, so FADE sold
into its lift at 716 and, as every round, restocked the 80-unit lot at 717 (the last day, hour 21). No fade step can follow
(the sell legs stop at 716), the base liquidated the wheat at 718 at its own impact, and with the shed holding that lot the
base did not bring the hands' carrots, eggs and wool to the shed at the last step, so they were never sold: -736 in a game
won by 663. Fix: FADE and GFADE only restock when a later fade step exists (step <= 713), and at their last fade step (no
further sell step in the game for that phase) they sell the whole lot above the feed reserve instead of twice the rival's
size, so nothing of the lot is left for the endgame. Everything else is byte-identical to v12_9.
"""
import hashlib
import io
import os
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(ROOT, "submissions", "v12_9_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n")
TAG = "v12_11"
EDITS = [
    # FADE: restock only when another fade step follows
    ('    elif step % 4 == 1 and (_fd_rival_n(mem, step - 1) > 0 or (step - 1) in st["sold"]):\n',
     '    elif step % 4 == 1 and step <= 713 and (_fd_rival_n(mem, step - 1) > 0 or (step - 1) in st["sold"]):   # v12_11: no restock without a later fade step\n'),
    # FADE: last fade step sells the whole lot
    ('            x = int(min(_FD_XMAX, 2 * n, shed_w - reserve))   # v12_9: the rival unwinds into our refill, so 2N pays\n',
     '            x = int(min(_FD_XMAX, 2 * n, shed_w - reserve))   # v12_9: the rival unwinds into our refill, so 2N pays\n'
     '            if step + 4 > 716:   # v12_11: last fade step of the game, wind the lot down into the lift\n'
     '                x = int(min(_FD_XMAX, shed_w - reserve))\n'),
    # GFADE: same two rules
    ('    elif (step - 1) in st["sold"] or (p is not None and phase == (p + 1) % 4 and n > 0):\n',
     '    elif step <= 713 and ((step - 1) in st["sold"] or (p is not None and phase == (p + 1) % 4 and n > 0)):   # v12_11: no restock without a later fade step\n'),
    ('        x = int(min(_GF_CFG["XMAX"], 2 * n, shed_w - reserve))   # v12_9: same 2N cap as FADE\n',
     '        x = int(min(_GF_CFG["XMAX"], 2 * n, shed_w - reserve))   # v12_9: same 2N cap as FADE\n'
     '        if step + 4 > 716:   # v12_11: last fade step of the game for this phase, wind the lot down\n'
     '            x = int(min(_GF_CFG["XMAX"], shed_w - reserve))\n'),
]


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 and "=" not in sys.argv[1] else os.path.join(
        ROOT, "submissions", "v12_11_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind")
    raw = open(os.path.join(SRC, "main.py"), "rb").read()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in EDITS:
        assert s.count(old) == 1, old
        s = s.replace(old, new)
    compile(s, "main.py", "exec")
    main = (s.replace("\n", "\r\n") if crlf else s).encode("utf-8")
    assert b"C:\\Users" not in main and b"/Users/cliff/" not in main
    notice = open(os.path.join(SRC, "NOTICE.txt"), "rb").read()
    h, rest = notice.split(b"\n\n", 1)
    h = h + (f" In {TAG} the wheat lots held against a rival's churn are wound down before the last day ends.").encode()
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
