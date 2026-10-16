r"""Download public Kaggriculture notebooks' outputs (the files the authors submit) into gold/public/<owner>__<slug>/,
extract main.py from tar.gz outputs, and record sha256 in gold/public/manifest.json.

.venv\Scripts\python.exe gold\tools\fetch_public.py owner/slug [owner/slug ...] [--src]
--src also pulls the notebook source (kernels pull) into gold/public/src__<owner>__<slug>/ for reading.
"""
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "gold", "public")
KAGGLE = shutil.which("kaggle") or "kaggle"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def fetch(ref, src):
    d = os.path.join(OUT, ref.replace("/", "__"))
    os.makedirs(d, exist_ok=True)
    r = subprocess.run([KAGGLE, "kernels", "output", ref, "-p", d, "--file-pattern", r".*\.(py|gz)$"],
                       capture_output=True, text=True)
    rec = {"ref": ref, "dir": d, "err": (r.stderr or "").strip()[-300:], "files": [], "main": None, "sha": ""}
    for tgz in glob.glob(os.path.join(d, "**", "*.tar.gz"), recursive=True):
        try:
            with tarfile.open(tgz) as t:
                names = t.getnames()
                rec["files"].append(f"{os.path.relpath(tgz, d)}: {','.join(names)}")
                for m in t.getmembers():
                    if m.isfile() and os.path.basename(m.name) in ("main.py", "LICENSE.txt", "NOTICE.txt"):
                        dst = os.path.join(d, "from_tar", os.path.basename(m.name))
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        with t.extractfile(m) as f, open(dst, "wb") as g:
                            g.write(f.read())
        except Exception as e:
            rec["err"] += f" tar {tgz}: {e}"
    mains = [p for p in glob.glob(os.path.join(d, "**", "main.py"), recursive=True)]
    mains.sort(key=lambda p: ("from_tar" not in p, -os.path.getsize(p)))
    if mains:
        rec["main"] = mains[0]
        rec["sha"] = sha(mains[0])[:8]
        rec["bytes"] = os.path.getsize(mains[0])
    rec["files"] += [os.path.relpath(p, d) for p in glob.glob(os.path.join(d, "**", "*"), recursive=True) if os.path.isfile(p)]
    if src:
        sd = os.path.join(OUT, "src__" + ref.replace("/", "__"))
        os.makedirs(sd, exist_ok=True)
        r2 = subprocess.run([KAGGLE, "kernels", "pull", ref, "-p", sd], capture_output=True, text=True)
        rec["src"] = sd
        rec["src_err"] = (r2.stderr or "").strip()[-200:]
    return rec


def main():
    args = sys.argv[1:]
    src = "--src" in args
    refs = [a for a in args if not a.startswith("--")]
    man_path = os.path.join(OUT, "manifest.json")
    man = json.load(open(man_path)) if os.path.exists(man_path) else {}
    for ref in refs:
        rec = fetch(ref, src)
        man[ref] = rec
        print(f"{ref}: main={os.path.relpath(rec['main'], ROOT) if rec['main'] else None} sha={rec['sha']} "
              f"bytes={rec.get('bytes', 0)} err={rec['err'][:80]!r}")
    json.dump(man, open(man_path, "w"), indent=1)


if __name__ == "__main__":
    main()
