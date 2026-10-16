r"""Bold challenger generator with a cheap pre-screen (team 42, gold effort).

Each round copies the arena champion's configuration and changes 2 to 5 things at once: internal switches of the
embedded cha22 (whole reactive layers on/off, race horizons, herd and crop thresholds), the v6 and composite knobs of
search.py, the late-game route and a "hold premium goods" layer. The candidate first plays a 16-game screen against
the champion (8 seeds x 2 seats, rotating worlds, seeds 300000+); only screens with score >= 59% and more wins than
losses go to the arena queue (prefix 00s_, ahead of search.py's challengers). Every screen is logged to
gold/arena/bold.jsonl so the effect of each switch can be estimated later.

.venv\Scripts\python.exe gold\arena\boldsearch.py [--workers 4] [--seed 7]
Stops when gold/arena/STOP_BOLD exists.
"""
import argparse
import ast
import copy
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
import layers  # noqa: E402
import search  # noqa: E402

search.LAYER_CHOICES.pop("wheat_mm", None)   # wheat market making lost 60 of 64 earlier; never re-enable it here
PY = (os.path.join(ROOT, ".venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(ROOT, ".venv", "bin", "python"))
LOG = os.path.join(ARENA, "bold.jsonl")
SEED_BASE = 300000
SCREEN_SEEDS = 8
PASS_RATE = 0.59

# Alternatives for internal cha22 switches (the current value is never picked again for the same knob). 03:45 rewrite
# from gold/results/cha22_knobs_0925.md (mirror screens of single knobs, cha22 vs cha22): dead knobs (APPLY_TIMING, V9_HERD_*,
# _RACE_HORIZON_*, V9_RACE_MAX/WINDOW/GAP, _CS_*, _HD2_* except FUTURE, V9_CARROT_*, _V231_CAP, _R37_*) and clearly
# harmful ones (_R85_FEED off, _R88_PHASE off, _V219_FERTILIZE off, _ADV_FRONT, _ADV_BOOK) are out; the sell-timing
# layers that decide mirror games (MPX, MP, DP, EV, ADV, OR2, FX, RACEGATE, CXD) are in.
H = lambda a, b: tuple(range(a, b + 1))  # noqa: E731
BOLD_BASE = {
    "_MPX_HOURS": [H(12, 22), H(0, 23), H(6, 23), H(10, 23), H(14, 22)],
    "_MP_HOURS": [H(10, 13), H(6, 14), H(8, 14), H(10, 16), H(6, 16)],
    "_MP_H": [8, 12, 16, 24],
    "_DP_HOURS": [H(0, 2), H(0, 5), H(0, 3), H(0, 7)],
    "_EV_HOURS": [H(15, 20), H(13, 21), H(17, 22), H(15, 23)],
    "_ADV_LOOK": [3, 4, 6, 8],
    "_ADV_PROTECT": [True, False],
    "_OR2_SN_K": [0, 1, 2, 4],
    "_OR2_SN_H": [24, 48],
    "_FX_FLOW_MIN": [999, 3, 4, 6],
    "_FX_LEAD_H": [12, 24, 36],
    "V9_RACEGATE_MARGIN": [0, -30, -60, -90],
    "V9_RACEPX_MARGIN": [0, -30, -60],
    "_CXD_BUDGET": [800, 1600, 3000],
    "V9_FERT_FIRST_DAY": [8, 10, 12, 14],
    "_CS_SHOP_RULE": ["nomilk", ""],
    "_HD2_FUTURE": [0.0, 0.3, 0.6],
    "_R51_INPUT_MAX_WORKERS": [2, 3],
    "_SR_MARGIN": [0, 4, 8, 16],
}
LATE = ["keep", 0, 1, 2, 3, 100]
HOLD = [None, {"floor": 0.7, "dump_from": 696, "min_room": 20}, {"floor": 0.9, "dump_from": 696, "min_room": 20},
        {"floor": 1.1, "dump_from": 672, "min_room": 25}]


def parse_full(path):
    """Champion configuration including route_table / late_route (search.parse_cfg drops those)."""
    cfg = search.parse_cfg(path)
    try:
        tree = ast.parse(open(path, encoding="utf-8").read())
        for node in tree.body:
            if (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id == "_CFG"):
                full = ast.literal_eval(node.value)
                for k in ("route_table", "late_route", "force_route"):
                    if k in full:
                        cfg[k] = full[k]
    except Exception:
        pass
    return cfg


DEFAULTS = {}


def load_defaults():
    ns = {"__name__": "bold_defaults"}
    exec(compile(open(layers.CHAMP0, encoding="utf-8").read(), layers.CHAMP0, "exec"), ns)
    for k in BOLD_BASE:
        DEFAULTS[k] = ns["_BASE_NS"].get(k)


def bold_mutate(rng, parent):
    cfg = copy.deepcopy(parent)
    tags = []
    for _ in range(rng.choice([2, 3, 3, 4, 5])):
        u = rng.random()
        # late-route changes (-23k per game) and hold_premium (-15k to -23k in screens) are not mutated any more
        if u < 0.6:
            key = rng.choice(sorted(BOLD_BASE))
            vals = [v for v in BOLD_BASE[key] if v != cfg["base"].get(key, DEFAULTS.get(key))]
            v = rng.choice(vals)
            cfg["base"][key] = v
            vs = f"{v[0]}to{v[-1]}" if isinstance(v, tuple) and v else str(v)
            tags.append(f"{key.strip('_').lower()[:14]}{vs}")
        else:
            cfg, t = search.mutate(rng, cfg)
            tags.append(t)
    cfg["layers"].pop("hold_premium", None)
    return cfg, "_".join(tags)


def screen(path, champ_path, n, workers):
    seed0 = SEED_BASE + SCREEN_SEEDS * n
    js = os.path.join(ARENA, "games", f"bold_{n:04d}.json")
    subprocess.run([PY, os.path.join(ROOT, "gold", "tools", "gstat.py"), path, champ_path, "--seeds", str(SCREEN_SEEDS),
                    "--seed0", str(seed0), "--both", "--workers", str(workers), "--worlds", "--world0",
                    str(seed0 % 92), "--json", js], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    d = json.load(open(js))
    w = l = t = errs = 0
    diffs = []
    for g in d["games"]:
        ra, rb = g["rewards"][g["cand_side"]], g["rewards"][1 - g["cand_side"]]
        errs += sum(g.get("errors") or [0])
        if ra is None or rb is None:
            l += 1
            continue
        diffs.append(ra - rb)
        w, l, t = w + (ra > rb), l + (ra < rb), t + (ra == rb)
    return {"w": w, "l": l, "t": t, "diff": sum(diffs) / max(1, len(diffs)), "errors": errs}


EMU = os.path.join(ROOT, "research", "panel", "emu_eager", "main.py")
EMU_WORLDS = os.path.join(ARENA, "emuworlds.json")
SHOP_TYPES = sorted(["BAKERY", "PIZZA_SHOP", "BRUNCH_SPOT", "YARN_STORE", "ICE_CREAM_SHOP", "PET_CAFE", "SMOOTHIE_SHOP",
                     "FARMERS_MARKET"])


def vs_emu(path, js, workers):
    """16 fixed random worlds vs emu_eager (the live 'sell on arrival' cha22 variants), seats alternating."""
    if not os.path.exists(EMU_WORLDS):
        rng = random.Random(777)
        json.dump([[rng.choice(SHOP_TYPES) for _ in range(8)] for _ in range(16)], open(EMU_WORLDS, "w"))
    if not os.path.exists(js):
        subprocess.run([PY, os.path.join(ROOT, "gold", "tools", "gstat.py"), path, EMU, "--seeds", "16", "--seed0", "66000",
                        "--alt", "--workers", str(workers), "--worlds-file", EMU_WORLDS, "--json", js], cwd=ROOT,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    d = json.load(open(js))
    w = l = t = errs = 0
    diffs = []
    for g in d["games"]:
        ra, rb = g["rewards"][g["cand_side"]], g["rewards"][1 - g["cand_side"]]
        errs += sum(g.get("errors") or [0])
        if ra is None or rb is None:
            l += 1
            continue
        diffs.append(ra - rb)
        w, l, t = w + (ra > rb), l + (ra < rb), t + (ra == rb)
    return {"w": w, "l": l, "t": t, "diff": sum(diffs) / max(1, len(diffs)), "errors": errs}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--screen", choices=["champ", "emu"], default="champ",
                    help="champ: 16 games vs the champion; emu: 16 worlds vs emu_eager, paired with the champion's "
                         "result on the same worlds (pass: >= 2 more wins and a mean margin not lower)")
    a = ap.parse_args()
    rng = random.Random(a.seed)
    load_defaults()
    done = search.load_jsonl(LOG) if hasattr(search, "load_jsonl") else (
        [json.loads(x) for x in open(LOG, encoding="utf-8") if x.strip()] if os.path.exists(LOG) else [])
    n = max([r["n"] for r in done] + [0])
    while not os.path.exists(os.path.join(ARENA, "STOP_BOLD")):
        n += 1
        champ = json.load(open(os.path.join(ARENA, "champion.json"), encoding="utf-8"))
        parent = parse_full(champ["path"])
        cfg, tag = bold_mutate(rng, parent)
        name = re.sub(r"[^A-Za-z0-9_]", "", f"b{a.seed}_{n:03d}_{tag}".replace(".", "p").replace("-", "m"))[:90]
        desc = f"大胆搜索第 {n} 个，父本 {champ['name']}：{tag}"
        path = os.path.join(ROOT, "gold", "hybrid", f"cx_{name}.py")
        layers.write(path, name, desc, cfg)
        if a.screen == "emu":
            base = vs_emu(champ["path"], os.path.join(ARENA, "games", f"emu_champ_{champ['name']}.json"), a.workers)
            r = vs_emu(path, os.path.join(ARENA, "games", f"emu_{n:04d}.json"), a.workers)
            r["champ_w"], r["champ_diff"] = base["w"], base["diff"]
            games = r["w"] + r["l"] + r["t"]
            rate = (r["w"] + 0.5 * r["t"]) / max(1, games)
            ok = r["w"] >= base["w"] + 2 and r["diff"] >= base["diff"] and r["errors"] == 0
        else:
            r = screen(path, champ["path"], n, a.workers)
            games = r["w"] + r["l"] + r["t"]
            rate = (r["w"] + 0.5 * r["t"]) / max(1, games)
            ok = rate >= PASS_RATE and r["w"] > r["l"] and r["errors"] == 0
        rec = dict(r, n=n, name=name, tag=tag, parent=champ["name"], rate=rate, queued=ok, cfg=repr(cfg), screen=a.screen)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if ok:
            open(os.path.join(ARENA, "queue", f"00s_{n:03d}_{name}.txt"), "w", encoding="utf-8").write(
                path + "\n" + desc + f"（快筛 {r['w']}-{r['l']}-{r['t']}）\n")


if __name__ == "__main__":
    main()
