r"""Fetch the agents of public Kaggriculture notebooks updated on 9/27-9/28 into research/panel/pub0928_<name>/main.py.

.venv/bin/python research/carrera/fetch_public_0928.py

Downloads each notebook's output files (kaggle kernels output), unpacks submission.tar.gz when present, and keeps a
rival only if a top-level main.py exists. Prints the rival names to pass to research/carrera/panel.py --rivals.
This runs third-party code only later, in the panel; this script only downloads and unpacks.
"""
import os
import subprocess
import sys
import tarfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KAGGLE = os.path.join(ROOT, ".venv", "bin", "kaggle")
NOTEBOOKS = {
    "pub0928_iceandfire": "leoprovorov/a-song-of-ice-and-fire-fixed-flexible",
    "pub0928_godsmode": "leoprovorov/god-s-mode-hacked-stores",
    "pub0928_masterv5": "guruprasaathas111/kaggriculture-master-engine-v53e01d74d8f",
    "pub0928_ledger": "haodou092/kaggriculture-harvest-ledger",
    "pub0928_hybrid2965": "haideptry/the-2965-master-hybrid-engine",
}


def main():
    ok = []
    for name, slug in NOTEBOOKS.items():
        d = os.path.join(ROOT, "research", "panel", name)
        os.makedirs(d, exist_ok=True)
        r = subprocess.run([KAGGLE, "kernels", "output", slug, "-p", d, "--file-pattern", r".*(main\.py|submission\.tar\.gz)$"],
                           capture_output=True, text=True, timeout=600)
        tgz = os.path.join(d, "submission.tar.gz")
        if os.path.exists(tgz):
            with tarfile.open(tgz) as tar:
                safe = [m for m in tar.getmembers() if not (m.name.startswith("/") or ".." in m.name)]
                tar.extractall(d, members=safe)
        main_py = os.path.join(d, "main.py")
        if os.path.exists(main_py):
            ok.append(name)
            print(f"{name}: main.py {os.path.getsize(main_py)} bytes  ({slug})")
        else:
            print(f"{name}: no main.py in the outputs ({slug}); files: {os.listdir(d)}; kaggle said: {(r.stdout + r.stderr).strip()[-200:]}")
    print("RIVALS=" + ",".join(ok))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
