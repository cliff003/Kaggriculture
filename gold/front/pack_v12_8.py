r"""Build v12_8: v12_7 plus the end-of-day pickup deferral layer (research/carrera/layers/eod_defer2.py, the other
session's eod2: +68/game on 954 live replays, 1 flip up 0 down, +104/game on the panel when added to v10).

    .venv/bin/python gold/front/pack_v12_8.py [OUT_DIR]

The layer is appended outermost, byte for byte from the carrera layer file; it only rewrites HARVEST actions at the
last step of a day when the projected shed plus carried units would exceed the 100-unit cap.
"""
import hashlib
import io
import os
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(ROOT, "submissions", "v12_7_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0")
LAYER = os.path.join(ROOT, "research", "carrera", "layers", "eod_defer2.py")
TAG = "v12_8"


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 and "=" not in sys.argv[1] else os.path.join(
        ROOT, "submissions", "v12_8_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod")
    raw = open(os.path.join(SRC, "main.py"), "rb").read()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8").replace("\r\n", "\n").rstrip("\n")
    layer = open(LAYER, encoding="utf-8").read().replace("\r\n", "\n").strip("\n")
    for name in ("_cg_eod_defer", "_PRE_CG_EOD_AGENT"):
        assert name not in s, name
    for name in ("def _project(", "def _g(", "_CAP = "):
        assert name in s, name
    code = s + "\n\n" + layer.replace("# V10_CarreraGT layer (team 42, 2026-09-27)", "# Team 42 layer (2026-09-27, v12_8)") + "\n"
    compile(code, "main.py", "exec")
    ns = {"__name__": "cand_check"}
    exec(compile(code, "main.py", "exec"), ns)
    last = [v for v in ns.values() if callable(v)][-1]
    assert getattr(last, "__name__", "") == "agent", last
    main = (code.replace("\n", "\r\n") if crlf else code).encode("utf-8")
    assert b"C:\\Users" not in main and b"/Users/cliff/" not in main
    notice = open(os.path.join(SRC, "NOTICE.txt"), "rb").read()
    h, rest = notice.split(b"\n\n", 1)
    h = h + (f" In {TAG} an end-of-day layer defers animal and ongoing-crop harvests at the last step of a day when the "
             f"shed would overflow (the overflow would be destroyed).").encode()
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
