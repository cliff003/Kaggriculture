r"""Package v7c + TICK layer as a self-contained submission (main.py, LICENSE.txt, NOTICE.txt -> submission.tar.gz).

    .venv\Scripts\python.exe gold\tick\pack.py OUT_DIR [KEY=VALUE ...]

KEY=VALUE pairs go to mk_tick.py (BUYSLOT=pad is the tested setting and the default here).
"""
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
V7C = os.path.join(ROOT, "submissions", "v7c_own_cha22_eager_wheatlead_fixes")


def main():
    out = os.path.abspath(sys.argv[1])
    kv = dict(x.split("=", 1) for x in sys.argv[2:])
    kv.setdefault("BUYSLOT", "pad")
    kv["SELF"] = "1"
    kv["BASE"] = os.path.join(V7C, "main.py")
    name = "_pack_tmp"
    py = (os.path.join(ROOT, ".venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(ROOT, ".venv", "bin", "python"))
    subprocess.run([py, os.path.join(HERE, "mk_tick.py"), name] + [f"{k}={v}" for k, v in kv.items()], check=True)
    src = open(os.path.join(ROOT, "gold", "builds", name, "main.py"), "rb").read()
    assert b"C:\\Users" not in src and b"C:/Users" not in src and b"/Users/cliff/" not in src, "local path leaked into main.py"
    notice = open(os.path.join(V7C, "NOTICE.txt"), "rb").read()
    head, rest = notice.split(b"\n\n", 1)
    head = head.replace(b"(v7c)", b"(v8)").replace(b") and FERTMORE layer", b"), FERTMORE layer").replace(
        b"appended around the base agent",
        b"and TICK layer (wheat bought at steps where the town eats wheat and sold the next step; off once the rival "
        b"is seen doing the same) appended around the base agent")
    notice = head + b"\n\n" + rest
    os.makedirs(out, exist_ok=True)
    members = [("main.py", src), ("LICENSE.txt", open(os.path.join(V7C, "LICENSE.txt"), "rb").read()),
               ("NOTICE.txt", notice)]
    for n, data in members:
        open(os.path.join(out, n), "wb").write(data)
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for n, data in members:
            info = tarfile.TarInfo(n)
            info.size = len(data)
            info.mode = 0o644
            info.mtime = 0
            tar.addfile(info, io.BytesIO(data))
    open(os.path.join(out, "submission.tar.gz"), "wb").write(buf.getvalue())
    shutil.rmtree(os.path.join(ROOT, "gold", "builds", name))
    print("main.py sha256", hashlib.sha256(src).hexdigest())
    print("submission.tar.gz sha256", hashlib.sha256(buf.getvalue()).hexdigest(), len(buf.getvalue()), "bytes")


if __name__ == "__main__":
    main()
