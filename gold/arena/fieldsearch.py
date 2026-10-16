r"""Field-aligned hill climb (team 42, 09-25 night, after self-play was shown to be biased).

Parent = gold/arena/field_best.json. Each round mutates 1 to 4 things (boldsearch.bold_mutate: live cha22 sell-timing
knobs, v6 knobs, extra layers) and screens the child against reactive cha22-family opponents instead of the parent:
  screen   emu_eager, morewheat, herdsafe_race x DSM worlds 20-39 (60 games; before 04:55 cha22, emu_eager, v4 x the
           first 20 family worlds), paired with the parent's games on the same worlds and seeds;
           pass = wins >= parent + 2 and mean margin >= parent - 100
  full     famvs (5 opponents x 40 worlds) + panel v2 (7 opponents x 28 DSM worlds); the child becomes the new parent
           when famvs wins (without the v6 column) + panel v2 wins >= parent + 4, famvs drops by at most 2 and panel v2
           (worlds never used by the screen) by at most 1
Logs gold/arena/field.jsonl. Stops when gold/arena/STOP_FIELD exists.

.venv\Scripts\python.exe gold\arena\fieldsearch.py [--workers 8] [--seed 21]
"""
import argparse
import json
import os
import random
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
ARENA = os.path.join(ROOT, "gold", "arena")
sys.path.insert(0, os.path.join(ROOT, "gold", "hybrid"))
sys.path.insert(0, ARENA)
import biggauntlet  # noqa: E402
import boldsearch  # noqa: E402
import famvs  # noqa: E402
import layers  # noqa: E402

PY = (os.path.join(ROOT, ".venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(ROOT, ".venv", "bin", "python"))
BEST = os.path.join(ARENA, "field_best.json")
LOG = os.path.join(ARENA, "field.jsonl")
# 04:55: the first screen (cha22, emu_eager, v4 on 20 random worlds) saturated at 56/60 for b14_feed4; this one uses
# the opponents it still loses to and DSM worlds 20-39, which neither the family panel nor panel v2 uses.
SCREEN_OPPS = {"emu_eager": os.path.join(ROOT, "research", "panel", "emu_eager", "main.py"),
               "morewheat": os.path.join(ROOT, "research", "panel", "morewheat", "main.py"),
               "herdsafe_race": os.path.join(ROOT, "research", "panel", "herdsafe_race", "main.py")}
SCREEN_WORLDS = os.path.join(ARENA, "dsm20_39.json")


def screen(path, tag, workers):
    """{opp: [margin per world]} over the first 20 family worlds (cached per tag)."""
    if not os.path.exists(SCREEN_WORLDS):
        sys.path.insert(0, os.path.join(ROOT, "gold", "tools"))
        import gstat
        json.dump(gstat.load_worlds()[20:40], open(SCREEN_WORLDS, "w"))
    out = {}
    for opp, opp_path in SCREEN_OPPS.items():
        js = os.path.join(ARENA, "games", f"fs2_{tag}_{opp}.json")
        if not os.path.exists(js):
            subprocess.run([PY, os.path.join(ROOT, "gold", "tools", "gstat.py"), path, opp_path, "--seeds", "20",
                            "--seed0", "68000", "--alt", "--workers", str(workers), "--worlds-file", SCREEN_WORLDS,
                            "--json", js], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        d = json.load(open(js))
        m = []
        for g in sorted(d["games"], key=lambda g: g["seed"]):
            a, b = g["rewards"][g["cand_side"]], g["rewards"][1 - g["cand_side"]]
            m.append(-99999.0 if (a is None or b is None or sum(g.get("errors") or [0])) else float(a - b))
        out[opp] = m
    return out


FAM_OPPS = ["cha22", "emu_eager", "v4"]
FAM_WORLDS = os.path.join(ARENA, "famworlds20.json")


def screen_fam(path, tag, workers):
    """Second screen (05:35): cha22, emu_eager, v4 x the first 20 family worlds; guards against children that buy
    wins against calm rivals by giving up the race against 'sell on arrival' ones."""
    if not os.path.exists(FAM_WORLDS):
        json.dump(json.load(open(famvs.WORLDS))[:20], open(FAM_WORLDS, "w"))
    w = 0
    for opp in FAM_OPPS:
        js = os.path.join(ARENA, "games", f"fs_{tag}_{opp}.json")
        if not os.path.exists(js):
            subprocess.run([PY, os.path.join(ROOT, "gold", "tools", "gstat.py"), path, famvs.OPPS[opp], "--seeds", "20",
                            "--seed0", "64000", "--alt", "--workers", str(workers), "--worlds-file", FAM_WORLDS,
                            "--json", js], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        d = json.load(open(js))
        for g in d["games"]:
            a, b = g["rewards"][g["cand_side"]], g["rewards"][1 - g["cand_side"]]
            w += (a is not None and b is not None and a > b)
    return w


def full(path, tag, workers):
    row = famvs.run(path, tag, workers)
    fam = sum(v[0] + 0.5 * v[2] for k, v in row.items() if k != "v6")
    row2 = biggauntlet.run2(path, tag, workers)
    p2 = sum(v[0] + 0.5 * v[2] for v in row2.values())
    mean = (sum(v[3] for k, v in row.items() if k != "v6") + sum(v[3] for v in row2.values())) / (len(row) - 1 + len(row2))
    return {"fam": fam, "p2": p2, "total": fam + p2, "mean": mean,
            "fam_rows": {k: v[:3] for k, v in row.items()}, "p2_rows": {k: v[:3] for k, v in row2.items()}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--seed", type=int, default=21)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    boldsearch.load_defaults()
    best = json.load(open(BEST, encoding="utf-8"))
    n = 0
    if os.path.exists(LOG):
        n = max([json.loads(l).get("n", 0) for l in open(LOG, encoding="utf-8") if l.strip()] + [0])
    while not os.path.exists(os.path.join(ARENA, "STOP_FIELD")):
        n += 1
        parent_cfg = boldsearch.parse_full(best["path"])
        cfg, tag = boldsearch.bold_mutate(rng, parent_cfg)
        name = re.sub(r"[^A-Za-z0-9_]", "", f"f{a.seed}_{n:03d}_{tag}".replace(".", "p").replace("-", "m"))[:80]
        path = os.path.join(ROOT, "gold", "hybrid", f"cx_{name}.py")
        layers.write(path, name, f"field search {n}, parent {best['name']}: {tag}", cfg)
        ps = screen(best["path"], best["name"], a.workers)
        cs = screen(path, name, a.workers)
        pw = sum(x > 0 for v in ps.values() for x in v)
        cw = sum(x > 0 for v in cs.values() for x in v)
        pm = sum(x for v in ps.values() for x in v) / 60
        cm = sum(x for v in cs.values() for x in v) / 60
        rec = {"n": n, "name": name, "tag": tag, "parent": best["name"], "screen_parent": pw, "screen_child": cw,
               "mean_parent": pm, "mean_child": cm, "cfg": repr(cfg)}
        if cw >= pw + 2 and cm >= pm - 100:
            fw_parent = screen_fam(best["path"], best["name"], a.workers)
            fw_child = screen_fam(path, name, a.workers)
            rec["fam_screen_parent"], rec["fam_screen_child"] = fw_parent, fw_child
        if cw >= pw + 2 and cm >= pm - 100 and rec["fam_screen_child"] >= rec["fam_screen_parent"] - 1:
            fp = best.get("full") or full(best["path"], best["name"], a.workers)
            best["full"] = fp
            fc = full(path, name, a.workers)
            rec["full_parent"], rec["full_child"] = fp, fc
            if fc["total"] >= fp["total"] + 4 and fc["fam"] >= fp["fam"] - 2 and fc["p2"] >= fp["p2"] - 1:
                rec["promoted"] = True
                best = {"name": name, "path": path, "full": fc, "since_n": n}
            json.dump(best, open(BEST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
