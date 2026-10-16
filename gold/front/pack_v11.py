r"""Build v11: v10 with the trap guard's prebuy rule extended to the phase-0 unwind (2026-09-27).

    .venv/bin/python gold/front/pack_v11.py [OUT_DIR]

New live trap (kwon yong deuk -18k, curiosity -11k, both cha22-tape mirrors): the rival buys 73-90 wheat at s % 4 == 3
(slot 0/1) and sells the same amount at s % 4 == 0 in slot 9, i.e. in lockstep with our last-slot tick buy. The lift is
already in the quote we see at s % 4 == 0, so the cash check sees no deviation, and the old prebuy rule only looked for
an unwind at s % 4 == 1. The rule now also counts an unwind of TH+ at s0 itself (the five public scheduled-fade steps
excluded), after which TICK pauses for the game and the existing phase-3 counter sells its own lot into the rival's
lift and restocks at s % 4 == 1. No FADE-type layer is added (public line). Everything else is byte-identical to v10.
"""
import hashlib
import io
import os
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(ROOT, "submissions", "v10_own_cha22_tick_trapguard_tomato")
TAG = "v11"

OLD = '''def _prebuy_hits(fl, step):
    hits = 0
    for s0 in range(step - 2, step - 2 - 4 * CFG["WIN"], -4):
        if fl.get(s0 - 1, 0) <= -CFG["TH"] and fl.get(s0 + 1, 0) >= CFG["TH"]:
            hits += 1
    return hits
'''
NEW = '''_PB_SCHED = {327, 375, 419, 435, 487}


def _prebuy_hits(fl, step):
    """Rival buys TH+ one step before our tick buy (s0 - 1) and unwinds either with our tick sell (s0 + 1) or
    against our tick buy itself in a late slot (s0; the public fixed-step wheat buys at 327/375/419/435/487 are not
    counted, they unwind at s0 too but never trap)."""
    hits = 0
    for s0 in range(step - 2, step - 2 - 4 * CFG["WIN"], -4):
        if fl.get(s0 - 1, 0) <= -CFG["TH"] and (fl.get(s0 + 1, 0) >= CFG["TH"] or
                                                (fl.get(s0, 0) >= CFG["TH"] and (s0 - 1) not in _PB_SCHED)):
            hits += 1
    return hits
'''


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 and "=" not in sys.argv[1] else os.path.join(
        ROOT, "submissions", "v11_own_cha22_tick_trapguard_tomato_prebuy0")
    raw = open(os.path.join(SRC, "main.py"), "rb").read()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8").replace("\r\n", "\n")
    assert s.count(OLD) == 1, "prebuy rule text not found once"
    assert "_PB_SCHED" not in s
    s = s.replace(OLD, NEW)
    s = s.replace("# Team 42 TICK TRAP GUARD layer (outermost, v9).",
                  "# Team 42 TICK TRAP GUARD layer (outermost, v9; v11 also pauses on a prebuy unwound at s % 4 == 0).") \
        if "# Team 42 TICK TRAP GUARD layer (outermost, v9)." in s else s
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
    print("crlf", crlf)
    print("main.py", hashlib.sha256(main).hexdigest())
    print("tar.gz", hashlib.sha256(buf.getvalue()).hexdigest())


if __name__ == "__main__":
    main()
