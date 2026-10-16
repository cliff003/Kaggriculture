r"""Package the final ace upload V12_AventadorSVJ from the latest sealed v12_x (code byte-identical; only the version
label in the header comment and NOTICE changes, as the other session did for v11).

    .venv/bin/python gold/front/pack_final_ace.py SRC_DIR [OUT_DIR]

Prints sha256 of main.py and submission.tar.gz and checks that the ASTs of source and output are identical.
Run it at the freeze (9/30 evening UTC) on the latest v12_x; never upload without the user's "提交".
"""
import ast
import hashlib
import io
import os
import re
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
NAME = "V12_AventadorSVJ"


def main():
    src = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "submissions", NAME)
    raw = open(os.path.join(src, "main.py"), "rb").read()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8").replace("\r\n", "\n")
    tag = re.search(r"v12_\d+(?![0-9])", os.path.basename(os.path.normpath(src)))
    assert tag, src
    tag = tag.group(0)
    pat = re.compile(r"\b" + re.escape(tag) + r"(?![0-9_])")
    out, n = pat.subn(NAME, s)   # every mention of the version tag (comments only: the AST check below proves it)
    assert ast.dump(ast.parse(out)) == ast.dump(ast.parse(s)), "AST changed"
    main_b = (out.replace("\n", "\r\n") if crlf else out).encode("utf-8")
    assert b"/Users/cliff/" not in main_b and b"C:\\Users" not in main_b
    notice = open(os.path.join(src, "NOTICE.txt"), "rb").read().decode("utf-8")
    notice = re.sub(r"\b" + re.escape(tag) + r"(?![0-9_])", NAME + " (" + tag + ")", notice, count=1)
    notice = re.sub(r"\(v12_1\)", "(" + NAME + ", built from " + tag + ")", notice, count=1).encode("utf-8")   # the stale v12_1 label of the NOTICE header
    lic = open(os.path.join(src, "LICENSE.txt"), "rb").read()
    os.makedirs(out_dir, exist_ok=True)
    members = [("main.py", main_b), ("LICENSE.txt", lic), ("NOTICE.txt", notice)]
    for name, data in members:
        open(os.path.join(out_dir, name), "wb").write(data)
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for name, data in members:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o644
            info.mtime = 0
            tar.addfile(info, io.BytesIO(data))
    open(os.path.join(out_dir, "submission.tar.gz"), "wb").write(buf.getvalue())
    print("out", out_dir, "from", tag, "labels changed", n)
    print("main.py", hashlib.sha256(main_b).hexdigest())
    print("tar.gz", hashlib.sha256(buf.getvalue()).hexdigest())


if __name__ == "__main__":
    main()
