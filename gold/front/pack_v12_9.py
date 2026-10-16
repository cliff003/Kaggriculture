r"""Build v12_9: v12_8 with the FADE and GFADE lot capped at twice the rival's churn size instead of once.

    .venv/bin/python gold/front/pack_v12_9.py [OUT_DIR]

Our own round trip is maximised at x = N (profit ~ x*N*slope - x^2*slope/2), but the margin also includes the rival's
loss: its unwind of N units sells into the book we refilled by x, so the relative gain is ~ 2*x*N*slope - x^2*slope/2,
maximised at x = 2N (still within XMAX, the rival's size window, shed room and feed reserve). Seen live 9/28 against
Ilya & Yurnero (slot-0 churner with ~28-unit lots): FADE sold 28 a round and the game ended -119, while the public
line's 80-unit counter ended +1382 on the same tape. Everything else is byte-identical to v12_8.
"""
import hashlib
import io
import os
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(ROOT, "submissions", "v12_8_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod")
TAG = "v12_9"
EDITS = [
    ('            x = int(min(_FD_XMAX, n, shed_w - reserve))\n',
     '            x = int(min(_FD_XMAX, 2 * n, shed_w - reserve))   # v12_9: the rival unwinds into our refill, so 2N pays\n'),
    ('        x = int(min(_GF_CFG["XMAX"], n, shed_w - reserve))\n',
     '        x = int(min(_GF_CFG["XMAX"], 2 * n, shed_w - reserve))   # v12_9: same 2N cap as FADE\n'),
]


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 and "=" not in sys.argv[1] else os.path.join(
        ROOT, "submissions", "v12_9_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n")
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
    h = h + (f" In {TAG} the fade lots may be up to twice the rival's churn size.").encode()
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
