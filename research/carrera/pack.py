r"""Package a V10_CarreraGT candidate for upload (nothing is uploaded here).

.venv/bin/python research/carrera/pack.py CAND_MAIN_PY OUT_DIR --base v11 --notice "SENTENCE" [--expected-sha256 HEX]

Writes OUT_DIR/main.py (the candidate's bytes, unchanged), LICENSE.txt (the base package's), NOTICE.txt (the base
package's NOTICE with SENTENCE appended to its first paragraph) and submission.tar.gz (those three files, fixed
mtime and modes, so the archive is reproducible), then prints every sha256. Refuses to overwrite OUT_DIR.
"""
import argparse
import gzip
import hashlib
import io
import os
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASES = {"v10": "v10_own_cha22_tick_trapguard_tomato", "v11": "v11_own_cha22_tick_trapguard_tomato_prebuy0"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cand")
    ap.add_argument("out")
    ap.add_argument("--base", default="v11", choices=sorted(BASES))
    ap.add_argument("--notice", required=True)
    ap.add_argument("--expected-sha256")
    a = ap.parse_args()
    main_py = open(a.cand, "rb").read()
    if a.expected_sha256:
        assert hashlib.sha256(main_py).hexdigest() == a.expected_sha256, "candidate changed since it was evaluated"
    compile(main_py, "main.py", "exec")
    assert b"C:\\Users" not in main_py and b"/Users/" not in main_py, "local path in main.py"
    base = os.path.join(ROOT, "submissions", BASES[a.base])
    lic = open(os.path.join(base, "LICENSE.txt"), "rb").read()
    notice = open(os.path.join(base, "NOTICE.txt"), "rb").read()
    nl = b"\r\n\r\n" if b"\r\n\r\n" in notice else b"\n\n"
    head, rest = notice.split(nl, 1)
    notice = head + b" " + a.notice.strip().encode("utf-8") + nl + rest
    members = [("main.py", main_py), ("LICENSE.txt", lic), ("NOTICE.txt", notice)]
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="") as gz:
        with tarfile.open(fileobj=gz, mode="w") as tar:
            for name, data in members:
                info = tarfile.TarInfo(name)
                info.size, info.mtime, info.mode = len(data), 0, 0o644
                tar.addfile(info, io.BytesIO(data))
    os.makedirs(a.out, exist_ok=False)
    for name, data in members + [("submission.tar.gz", buf.getvalue())]:
        with open(os.path.join(a.out, name), "wb") as f:
            f.write(data)
        print(f"{name:18s} {hashlib.sha256(data).hexdigest()}  {len(data)} bytes")


if __name__ == "__main__":
    main()
