r"""Re-base queued composite challengers onto the current champion: each queued cx_*.py keeps only what it changes
relative to OLD_PARENT (the champion it was built on) and gets that delta applied to the current champion's config.

.venv\Scripts\python.exe gold\arena\rebase.py OLD_PARENT_FILE
"""
import copy
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "gold", "hybrid"))
sys.path.insert(0, os.path.join(ROOT, "gold", "arena"))
import layers  # noqa: E402
import search  # noqa: E402


def delta(cfg, parent):
    d = {"top": {}, "base": {}, "layers": {}, "drop": []}
    for sec in ("top", "base", "layers"):
        for k, v in cfg[sec].items():
            if parent[sec].get(k) != v:
                d[sec][k] = v
        if sec == "layers":
            d["drop"] = [k for k in parent["layers"] if k not in cfg["layers"]]
    return d


def main():
    old = search.parse_cfg(sys.argv[1])
    champ = json.load(open(os.path.join(ROOT, "gold", "arena", "champion.json"), encoding="utf-8"))
    new_parent = search.parse_cfg(champ["path"])
    q = os.path.join(ROOT, "gold", "arena", "queue")
    for f in sorted(os.listdir(q)):
        lines = open(os.path.join(q, f), encoding="utf-8").read().splitlines()
        path, desc = lines[0], (lines[1] if len(lines) > 1 else "")
        if not os.path.basename(path).startswith("cx_") or not os.path.exists(path):
            continue
        cfg = search.parse_cfg(path)
        d = delta(cfg, old)
        merged = copy.deepcopy(new_parent)
        for sec in ("top", "base", "layers"):
            merged[sec].update(d[sec])
        for k in d["drop"]:
            merged["layers"].pop(k, None)
        name = os.path.splitext(os.path.basename(path))[0][3:]
        layers.write(path, name, desc + f"（已平移到擂主 {champ['name']}）", merged)
        print(f, "delta", d)


if __name__ == "__main__":
    main()
