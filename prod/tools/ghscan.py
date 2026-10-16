r"""Scan public GitHub repos for Kaggriculture agents with a given opening fingerprint.

ghscan.py OUT_DIR [--query kaggriculture] [--pages 4] [--max-kb 50000]
Lists repos with the GitHub search API, downloads each default-branch zip, extracts every .py file that
defines `agent(` plus `%%writefile *.py` cells from notebooks, runs each candidate for 4 steps (own process,
timeout) against a PASS opponent and records its first actions. Candidates whose farmer does PICKUP COW on
step 1 and BUILD_PASTURE on step 2 (the private strong-production family's opening) are flagged.
Results: OUT_DIR/scan.jsonl (one line per candidate) and OUT_DIR/hits.txt.
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PY = (os.path.join(ROOT, ".venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(ROOT, ".venv", "bin", "python"))

PROBE = r'''
import json, sys, os
sys.path.insert(0, r"%(tools)s")
import fastarena
from kaggle_environments.envs.kaggriculture import kaggriculture as K
path = os.path.abspath(sys.argv[1])
os.chdir(os.path.dirname(path))
sys.path.insert(0, os.path.dirname(path))
fa = fastarena.load_agent(path)
log = []
def wrap(obs, cfg=None):
    a = fa(obs, cfg)
    if obs["step"] < 4:
        log.append(a)
    if obs["step"] >= 3:
        raise SystemExit(0)
    return a
def passer(obs, cfg=None):
    return {"farmer": ["PASS"], "hands": [], "market": []}
try:
    fastarena.run_game(wrap, passer, 4242)
except SystemExit:
    pass
print("ACTS" + json.dumps(log))
'''


def get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "team42-scan"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def list_repos(query, pages):
    out = []
    for p in range(1, pages + 1):
        data = json.loads(get(f"https://api.github.com/search/repositories?q={query}&per_page=100&page={p}&sort=updated"))
        items = data.get("items", [])
        out += items
        if len(items) < 100:
            break
        time.sleep(7)
    return out


def candidates(zbytes, dest):
    z = zipfile.ZipFile(io.BytesIO(zbytes))
    got = []
    for n in z.namelist():
        if n.endswith(".py"):
            try:
                src = z.read(n).decode("utf-8", errors="replace")
            except Exception:
                continue
            if re.search(r"^def agent\s*\(", src, re.M) and len(src) < 3_000_000:
                p = os.path.join(dest, n.replace("/", "__"))
                open(p, "w", encoding="utf-8").write(src)
                got.append((n, p))
        elif n.endswith(".ipynb"):
            try:
                nb = json.loads(z.read(n).decode("utf-8", errors="replace"))
            except Exception:
                continue
            for k, cell in enumerate(nb.get("cells", [])):
                src = "".join(cell.get("source", []))
                m = re.match(r"%%writefile\s+(\S+\.py)", src)
                if m and re.search(r"^def agent\s*\(", src, re.M):
                    body = src.split("\n", 1)[1] if "\n" in src else ""
                    p = os.path.join(dest, (n + f"__cell{k}__" + os.path.basename(m.group(1))).replace("/", "__"))
                    open(p, "w", encoding="utf-8").write(body)
                    got.append((n + f"#cell{k}", p))
    return got


def probe(path):
    code = PROBE % {"tools": os.path.join(ROOT, "tools")}
    try:
        r = subprocess.run([PY, "-c", code, path], capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return None, "timeout"
    m = re.search(r"ACTS(\[.*\])", r.stdout)
    if not m:
        return None, (r.stderr or r.stdout)[-200:]
    return json.loads(m.group(1)), ""


def is_family(acts):
    try:
        f1 = acts[1].get("farmer") or []
        f2 = acts[2].get("farmer") or []
        return f1[:2] == ["PICKUP", "COW"] and f2[:1] == ["BUILD_PASTURE"]
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--query", default="kaggriculture")
    ap.add_argument("--pages", type=int, default=4)
    ap.add_argument("--max-kb", type=int, default=50000)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    done = set()
    scan = os.path.join(a.out, "scan.jsonl")
    if os.path.exists(scan):
        for line in open(scan, encoding="utf-8"):
            done.add(json.loads(line)["repo"])
    repos = list_repos(a.query, a.pages)
    print(len(repos), "repos", flush=True)
    for r in repos:
        name = r["full_name"]
        if name in done:
            continue
        rec = {"repo": name, "pushed": r.get("pushed_at"), "size_kb": r.get("size"), "cands": []}
        if (r.get("size") or 0) > a.max_kb:
            rec["skip"] = "size"
        else:
            try:
                zb = get(f"https://codeload.github.com/{name}/zip/HEAD", timeout=120)
                dest = os.path.join(a.out, name.replace("/", "__"))
                os.makedirs(dest, exist_ok=True)
                for n, p in candidates(zb, dest):
                    acts, err = probe(p)
                    rec["cands"].append({"file": n, "path": p, "family": bool(acts) and is_family(acts),
                                         "a1": (acts[1].get("farmer") if acts and len(acts) > 1 else None),
                                         "a2": (acts[2].get("farmer") if acts and len(acts) > 2 else None),
                                         "err": err[:120]})
            except Exception as e:
                rec["skip"] = repr(e)[:120]
        open(scan, "a", encoding="utf-8").write(json.dumps(rec) + "\n")
        hits = [c for c in rec["cands"] if c["family"]]
        if hits:
            open(os.path.join(a.out, "hits.txt"), "a", encoding="utf-8").write(json.dumps({"repo": name, "hits": hits}) + "\n")
        print(name, len(rec["cands"]), "cands", "HIT" if hits else "", rec.get("skip", ""), flush=True)


if __name__ == "__main__":
    main()
