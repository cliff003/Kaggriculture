r"""Build v12_7: v12_6 with the trap guard's prebuy rule extended to the phase-0 unwind (same patch as gold/front/pack_v11.py).

    .venv/bin/python gold/front/pack_v12_7.py [OUT_DIR]

The rival buys 73-90 wheat at s % 4 == 3 and sells it at s % 4 == 0 in slot 9 against our last-slot tick buy (kwon yong
deuk, curiosity, 2026-09-27). GFADE already fades that rival (+26k on kwon's tape) but the guard's phase-3 counter does
better (+42k), so the guard now also counts an unwind at s0 (public scheduled-fade steps excluded); with the counter on,
GFADE stands aside on those steps by its own rule. Everything else is byte-identical to v12_6.
"""
import hashlib
import io
import os
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from pack_v11 import OLD, NEW  # noqa: E402

SRC = os.path.join(ROOT, "submissions", "v12_6_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade")
TAG = "v12_7"


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 and "=" not in sys.argv[1] else os.path.join(
        ROOT, "submissions", "v12_7_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0")
    raw = open(os.path.join(SRC, "main.py"), "rb").read()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8").replace("\r\n", "\n")
    assert s.count(OLD) == 1, "prebuy rule text not found once"
    assert "_PB_SCHED" not in s
    s = s.replace(OLD, NEW)
    compile(s, "main.py", "exec")
    main = (s.replace("\n", "\r\n") if crlf else s).encode("utf-8")
    assert b"C:\\Users" not in main and b"/Users/cliff/" not in main
    notice = open(os.path.join(SRC, "NOTICE.txt"), "rb").read()
    h, rest = notice.split(b"\n\n", 1)
    h = h + (f" In {TAG} the tick-trap guard also pauses the arbitrage when a rival buys wheat one step before our tick "
             f"buy and unwinds against it in the same step.").encode()
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
