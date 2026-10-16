r"""Run local research jobs on a private Kaggle CPU notebook instead of this machine.

kgrun.py push NAME --include PATH [PATH ...] --cmd "CMD" [--cmd "CMD" ...]
    Packs the included files/dirs (paths kept relative to the project root) into one private script
    kernel kefeiyan/kgr-NAME, which installs kaggle-environments 1.32.7, unpacks the files and runs each
    CMD in order ("python" means the notebook's interpreter). stdout of CMD k goes to out_k.txt.
kgrun.py wait NAME [--out DIR]
    Polls until the kernel finishes, then downloads its outputs to DIR (default prod/kg/NAME).
Kernels are always private; nothing here touches the competition.
"""
import argparse
import base64
import io
import json
import os
import subprocess
import sys
import time
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
USER = "kefeiyan"
WORK = os.path.join(ROOT, "prod", "kg")

RUNNER = r'''
import base64, io, os, subprocess, sys, time, zipfile
t0 = time.time()
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "kaggle-environments==1.32.7"], check=False)
os.makedirs("/kaggle/working/src", exist_ok=True)
if PAYLOAD:
    zipfile.ZipFile(io.BytesIO(base64.b85decode(PAYLOAD))).extractall("/kaggle/working/src")
else:
    import glob
    hits = glob.glob("/kaggle/input/**/payload.bin", recursive=True)
    print("payload", hits, flush=True)
    zipfile.ZipFile(hits[0]).extractall("/kaggle/working/src")
os.chdir("/kaggle/working/src")
print("cpus", os.cpu_count(), "setup", round(time.time() - t0), "s", flush=True)
for k, cmd in enumerate(CMDS):
    cmd = cmd.replace("python ", sys.executable + " ", 1) if cmd.startswith("python ") else cmd
    t1 = time.time()
    with open(f"/kaggle/working/out_{k}.txt", "w") as f:
        p = subprocess.run(cmd, shell=True, stdout=f, stderr=subprocess.STDOUT)
    print(k, "exit", p.returncode, round(time.time() - t1), "s", cmd[:200], flush=True)
    print(open(f"/kaggle/working/out_{k}.txt").read()[-3000:], flush=True)
'''


def pack(paths, raw=False):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in paths:
            full = os.path.join(ROOT, p)
            if os.path.isdir(full):
                for dp, dn, fn in os.walk(full):
                    dn[:] = [d for d in dn if d != "__pycache__"]
                    for f in fn:
                        if f.endswith((".py", ".json", ".txt", ".gz")):
                            fp = os.path.join(dp, f)
                            z.write(fp, os.path.relpath(fp, ROOT).replace("\\", "/"))
            else:
                z.write(full, os.path.relpath(full, ROOT).replace("\\", "/"))
    return buf.getvalue() if raw else base64.b85encode(buf.getvalue()).decode("ascii")


def push(a):
    d = os.path.join(WORK, a.name, "kernel")
    os.makedirs(d, exist_ok=True)
    payload = pack(a.include)
    sources = []
    if len(payload) > 700_000:
        # too big for a kernel source: ship the files as a private dataset instead
        dd = os.path.join(WORK, a.name, "data")
        os.makedirs(dd, exist_ok=True)
        open(os.path.join(dd, "payload.bin"), "wb").write(pack(a.include, raw=True))
        slug = f"kgr-{a.name}-data"
        json.dump({"title": slug, "id": f"{USER}/{slug}", "licenses": [{"name": "CC0-1.0"}]},
                  open(os.path.join(dd, "dataset-metadata.json"), "w"), indent=1)
        r = subprocess.run(["kaggle", "datasets", "create", "-p", dd], capture_output=True, text=True)
        print((r.stdout + r.stderr).strip()[-300:])
        if r.returncode or "already" in (r.stdout + r.stderr).lower():
            subprocess.run(["kaggle", "datasets", "version", "-p", dd, "-m", "update"], check=True)
        st = ""
        for _ in range(60):
            time.sleep(10)
            st = subprocess.run(["kaggle", "datasets", "status", f"{USER}/{slug}"], capture_output=True, text=True).stdout
            if "ready" in st.lower():
                break
        print("dataset", st.strip())
        sources = [f"{USER}/{slug}"]
        payload = ""
    src = f"PAYLOAD = {payload!r}\nCMDS = {a.cmd!r}\n" + RUNNER
    open(os.path.join(d, "run.py"), "w", encoding="utf-8").write(src)
    meta = {"id": f"{USER}/kgr-{a.name}", "title": f"kgr-{a.name}", "code_file": "run.py", "language": "python",
            "kernel_type": "script", "is_private": True, "enable_gpu": False, "enable_tpu": False,
            "enable_internet": True, "dataset_sources": sources, "competition_sources": [], "kernel_sources": [],
            "model_sources": []}
    json.dump(meta, open(os.path.join(d, "kernel-metadata.json"), "w"), indent=1)
    print(f"payload {len(payload) / 1e6:.2f} MB")
    # at most 5 batch CPU sessions run at once: wait for a free slot
    while True:
        r = subprocess.run(["kaggle", "kernels", "push", "-p", d], capture_output=True, text=True)
        msg = (r.stdout + r.stderr).strip()
        if "Maximum batch CPU session count" in msg:
            time.sleep(60)
            continue
        print(msg[-300:])
        if r.returncode:
            raise SystemExit(r.returncode)
        break


def wait(a):
    ref = f"{USER}/kgr-{a.name}"
    out = a.out or os.path.join(WORK, a.name, "out")
    while True:
        s = subprocess.run(["kaggle", "kernels", "status", ref], capture_output=True, text=True).stdout
        low = s.lower()
        if "complete" in low or "error" in low or "cancel" in low:
            print(s.strip())
            break
        time.sleep(a.poll)
    os.makedirs(out, exist_ok=True)
    subprocess.run(["kaggle", "kernels", "output", ref, "-p", out, "-o"], check=False,
                   stdout=subprocess.DEVNULL)
    for f in sorted(os.listdir(out)):
        if f.startswith("out_") and f.endswith(".txt"):
            print(f"== {f}")
            print(open(os.path.join(out, f), encoding="utf-8", errors="replace").read()[-4000:])


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="op", required=True)
    p = sub.add_parser("push")
    p.add_argument("name")
    p.add_argument("--include", nargs="+", required=True)
    p.add_argument("--cmd", action="append", required=True)
    w = sub.add_parser("wait")
    w.add_argument("name")
    w.add_argument("--out", default="")
    w.add_argument("--poll", type=int, default=60)
    a = ap.parse_args()
    push(a) if a.op == "push" else wait(a)


if __name__ == "__main__":
    main()
