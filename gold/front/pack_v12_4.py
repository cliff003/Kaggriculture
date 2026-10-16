r"""Build the v12_4 package: v12_3 with the embedded cha22 source patched by tools/patch_base.py --patch v219n2e
(V219 tomato investment also with two early pizza / farmers-market shops), header and NOTICE updated.

    .venv\Scripts\python.exe gold\front\pack_v12_4.py
"""
import hashlib
import io
import os
import subprocess
import sys
import tarfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "submissions", "v12_3_own_cha22_tick_fade_resume_late_sched_trap")
OUT = os.path.join(ROOT, "submissions", "v12_4_own_cha22_tick_fade_resume_late_sched_trap_tomato")
PATCHED_SHA = "ea87e3cb780642abb7501f03ab37ffb430b040d6be1d736c26e6a3fb68ac5718"


def main():
    tmp = os.path.join(ROOT, "gold", "tmp", "v12_4_patch")
    subprocess.check_call([sys.executable, os.path.join(ROOT, "tools", "patch_base.py"), os.path.join(SRC, "main.py"), tmp,
                           "--patch", "v219n2e"])
    raw = open(os.path.join(tmp, "main.py"), "rb").read()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8").replace("\r\n", "\n")
    old_sha = '_BASE_SHA256 = "127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652"'
    assert s.count(old_sha) == 1
    s = s.replace(old_sha, f'_BASE_SHA256 = "{PATCHED_SHA}"   # upstream cha22 127ed3e6, patched: see header')
    anchor = "#    The base policy is otherwise unchanged.\n"
    assert s.count(anchor) == 1
    s = s.replace(anchor, anchor +
                  "# v12_4 (2026-09-27): the embedded cha22 source carries one change. Its V219 tomato investment (day 18,\n"
                  "#    south-east quadrant, 10 tomatoes) needed three pizza / farmers-market shops; it now also qualifies\n"
                  "#    with two when they open early (tomato shop-days by day 18 >= 24, i.e. days 3 and 6 or 3 and 9).\n")
    compile(s, "main.py", "exec")
    main_bytes = (s.replace("\n", "\r\n") if crlf else s).encode("utf-8")
    notice = open(os.path.join(SRC, "NOTICE.txt"), "rb").read()
    old = b"Base source embedded unchanged, SHA-256 127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652."
    new = (b"Base source 127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652 embedded with one change (v12_4): "
           b"its V219 tomato investment also qualifies with two pizza / farmers-market shops when they open early (see "
           b"main.py header).")
    assert notice.count(old) == 1, "NOTICE sentence not found"
    notice = notice.replace(old, new)
    lic = open(os.path.join(SRC, "LICENSE.txt"), "rb").read()
    os.makedirs(OUT, exist_ok=True)
    members = [("main.py", main_bytes), ("LICENSE.txt", lic), ("NOTICE.txt", notice)]
    for n, d in members:
        open(os.path.join(OUT, n), "wb").write(d)
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for n, d in members:
            info = tarfile.TarInfo(n)
            info.size = len(d)
            info.mode = 0o644
            info.mtime = 0
            tar.addfile(info, io.BytesIO(d))
    open(os.path.join(OUT, "submission.tar.gz"), "wb").write(buf.getvalue())
    print("crlf", crlf)
    print("main.py", hashlib.sha256(main_bytes).hexdigest())
    print("tar.gz", hashlib.sha256(buf.getvalue()).hexdigest())


if __name__ == "__main__":
    main()
