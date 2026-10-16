r"""Background hill-climb over p4 heuristic parameters on Kaggle.

kgsearch.py STATE.json [--agent prod/agents/p4mn/main.py] [--opp submissions/v7c.../main.py] [--rounds 50]
        [--cands 8] [--seeds 6050-6099] [--per 2]

Each round perturbs 2-4 parameters of the incumbent to make --cands candidates, runs them (plus the
incumbent again) on Kaggle kernels (--per variants per kernel, 100 games each by default), and moves to the best
candidate when it beats the re-measured incumbent by more than one standard error on the same seeds; the new
incumbent is then checked on fresh seeds before the next round. Everything is logged in STATE.json and
prod/kg/search_log.tsv so a restart resumes where it stopped.
"""
import argparse
import json
import os
import random
import re
import shlex
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PY = (os.path.join(ROOT, ".venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(ROOT, ".venv", "bin", "python"))
KG = os.path.join(ROOT, "prod", "tools", "kgrun.py")

# name: (kind, choices or (lo, hi, step))
SPACE = {
    "melons_d0": ("c", [8, 10, 12, 14]),
    "cows_d0": ("c", [2, 3]),
    "sheep_d0": ("c", [2, 3]),
    "sheep_base": ("i", (2, 5, 1)),
    "cow_base": ("i", (3, 7, 1)),
    "animal_total": ("i", (18, 26, 1)),
    "straw_a": ("i", (9, 18, 1)),
    "straw_b": ("f", (5.0, 11.0, 0.5)),
    "tom_a": ("i", (8, 24, 2)),
    "tom_b": ("f", (4.0, 9.0, 0.5)),
    "car_a": ("i", (2, 13, 1)),
    "car_b": ("i", (1, 6, 1)),
    "straw_early": ("i", (6, 12, 1)),
    "straw_last": ("i", (11, 16, 1)),
    "tom_first": ("i", (7, 11, 1)),
    "tom_last": ("i", (15, 21, 1)),
    "car_first": ("i", (8, 15, 1)),
    "car_early_frac": ("f", (0.1, 0.7, 0.05)),
    "animal_last_day": ("i", (10, 15, 1)),
    "hands_min": ("i", (3, 5, 1)),
    "max_hands": ("i", (11, 14, 1)),
    "land_days": ("c", [[6, 9, 99], [6, 10, 99], [6, 11, 99], [6, 12, 99], [5, 11, 99], [7, 11, 99], [6, 11, 16]]),
    "land_last": ("i", (12, 16, 1)),
    "fert_wheat_max": ("i", (40, 110, 10)),
    "wheat_per_animal": ("f", (0.5, 1.1, 0.05)),
    "ongoing_harvest_min": ("i", (1, 3, 1)),
    "extra_hand_ratio": ("f", (0.8, 2.5, 0.1)),
    "feed_ratio": ("f", (1.5, 4.0, 0.25)),
    "steal_slack": ("i", (1, 4, 1)),
    "shed_place_min": ("i", (150, 600, 50)),
    "early_cows": ("c", [0, 1, 2, 3]),
    "idle_care": ("c", [False, True]),
    "carrot_age3": ("c", [False, True]),
    "late_from": ("c", [99, 27, 26, 25]),
}


def sample(name, cur):
    kind, sp = SPACE[name]
    if kind == "c":
        opts = [x for x in sp if x != cur] or sp
        return random.choice(opts)
    lo, hi, st = sp
    if cur is None:
        cur = lo
    k = random.choice([-2, -1, 1, 2])
    v = cur + k * st
    v = max(lo, min(hi, v))
    if kind == "i":
        return int(round(v))
    return round(v, 3)


def fmt(cfg):
    return " ".join(shlex.quote(f"{k}={json.dumps(v, separators=(',', ':'))}") for k, v in sorted(cfg.items()))


def run_batch(tag, variants, agent, opp, seeds, per):
    """variants: list of (name, cfg). Returns {name: (margin, se, wins, n)}."""
    kernels = []
    for k in range(0, len(variants), per):
        kname = f"{tag}{k // per}"
        cmds = []
        for name, cfg in variants[k:k + per]:
            cmds.append(f"python prod/tools/bench.py {agent} {opp} --seeds {seeds} -j 4 --tag {name} --set {fmt(cfg)}")
        args = [PY, KG, "push", kname, "--include", "tools/fastarena.py", "prod/tools", agent, opp]
        for c in cmds:
            args += ["--cmd", c]
        subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
        kernels.append(kname)
    out = {}
    for kname in kernels:
        subprocess.run([PY, KG, "wait", kname, "--poll", "60"], cwd=ROOT, capture_output=True, text=True)
        d = os.path.join(ROOT, "prod", "kg", kname, "out")
        for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if not (f.startswith("out_") and f.endswith(".txt")):
                continue
            first = open(os.path.join(d, f), encoding="utf-8", errors="replace").readline()
            m = re.match(r"(\S+) .*n=(\d+) W (\d+) T \d+ me (\d+) opp (\d+) margin (-?\d+) \(se (\d+)\).*errs (\d+)", first)
            if m:
                name, n, w, me, op, mg, se, errs = m.groups()
                out[name] = (float(mg), float(se), int(w), int(n), int(errs))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("state")
    ap.add_argument("--agent", default="prod/agents/p4mn/main.py")
    ap.add_argument("--opp", default="submissions/v7c_own_cha22_eager_wheatlead_fixes/main.py")
    ap.add_argument("--rounds", type=int, default=50)
    ap.add_argument("--cands", type=int, default=8)
    ap.add_argument("--seeds", default="6050-6099")
    ap.add_argument("--fresh", default="7000-7099")
    ap.add_argument("--per", type=int, default=3)
    a = ap.parse_args()
    st = json.load(open(a.state)) if os.path.exists(a.state) else {"inc": {}, "round": 0, "hist": []}
    log = os.path.join(ROOT, "prod", "kg", "search_log.tsv")
    fixed = st.get("fixed", {})
    while st["round"] < a.rounds:
        r = st["round"]
        random.seed(1000 + r)
        inc = dict(st["inc"])
        cands = [("inc", dict(fixed, **inc))]
        for c in range(a.cands):
            cfg = dict(inc)
            for name in random.sample(sorted(SPACE), random.choice([2, 3, 4])):
                cfg[name] = sample(name, cfg.get(name))
            cands.append((f"c{c}", dict(fixed, **cfg)))
        res = run_batch(f"sr{r}x", cands, a.agent, a.opp, a.seeds, a.per)
        base = res.get("inc")
        best = None
        for name, cfg in cands[1:]:
            v = res.get(name)
            if not v or v[4] > 0 or base is None:
                continue
            if v[0] > base[0] + max(v[1], base[1]) and (best is None or v[0] > best[1][0]):
                best = (name, v, cfg)
        with open(log, "a", encoding="utf-8") as f:
            for name, cfg in cands:
                v = res.get(name)
                f.write(f"{r}\t{name}\t{v}\t{json.dumps({k: x for k, x in cfg.items() if k not in fixed})}\n")
        moved = False
        if best:
            # confirm on fresh seeds against the incumbent
            conf = run_batch(f"sq{r}x", [("inc", dict(fixed, **inc)), ("new", best[2])], a.agent, a.opp, a.fresh, 2)
            if conf.get("new") and conf.get("inc") and conf["new"][0] > conf["inc"][0]:
                st["inc"] = {k: x for k, x in best[2].items() if k not in fixed}
                moved = True
            with open(log, "a", encoding="utf-8") as f:
                f.write(f"{r}\tconfirm\t{conf}\tmoved={moved}\n")
        st["hist"].append({"round": r, "inc": base, "best": best[1] if best else None, "moved": moved})
        st["round"] = r + 1
        json.dump(st, open(a.state, "w"), indent=1)
        print(f"round {r}: inc {base} best {best[0] + ' ' + str(best[1]) if best else None} moved {moved}", flush=True)


if __name__ == "__main__":
    main()
