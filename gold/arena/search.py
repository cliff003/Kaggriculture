r"""Evolutionary challenger generator for the arena (team 42, gold effort).

Keeps gold/arena/queue topped up with composite variants (gold/hybrid/layers.py) of the current champion: each new
challenger copies the champion's configuration (v6 globals, embedded cha22 globals, extra layers) and changes one or
two knobs at random. arena.py decides titles, so improvements stack: the next generation mutates the new champion.

.venv\Scripts\python.exe gold\arena\search.py [--min-queue 3] [--batch 4] [--seed 2]
Stops when gold/arena/STOP_SEARCH exists.
"""
import argparse
import ast
import copy
import json
import os
import random
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
ARENA = os.path.join(ROOT, "gold", "arena")
sys.path.insert(0, os.path.join(ROOT, "gold", "hybrid"))
import layers  # noqa: E402

ITEMS3 = ("MILK", "STRAWBERRY", "WOOL")
DEFAULT_BANDS = {"MILK": (0.3, 0.9), "STRAWBERRY": (0.3, 0.9), "WOOL": (0.3, 0.9)}
TOP_CHOICES = {
    "_EAGER_FROM": [192, 240, 264, 288, 312, 336],
    "_EAGER_TO": [672, 690, 700, 710, 716],
    "_SORT_TOL": [0.0, 5.0, 10.0, 20.0, 40.0],
    "_RACE_FROM": [720, 576, 624, 648, 672, 696],
    "_OPEN20": [False, True],
    "_SLOT_START": [0, 144, 240, 288],
}
BASE_CHOICES = {
    ("V9_RACE_DEFAULT", "V9_RACE_MAX", "V9_RACE_MARGIN"): [(44, 48, 12), (48, 56, 12), (52, 60, 16), (56, 64, 16),
                                                          (60, 68, 16), (56, 64, 20), (64, 72, 16)],
    ("V9_RACEPX_MARGIN", "V9_RACEGATE_MARGIN"): [(-40, -40), (-20, -20), (0, 0), (20, 20), (40, 40)],
    ("V9_COURIER_FROM_HOUR",): [(8,), (10,), (12,), (14,), (16,)],
    ("V9_RACE_WINDOW",): [(20,), (30,), (40,), (50,)],
    ("V9_RACE_GAP",): [(1,), (2,), (3,), (5,)],
}
LAYER_CHOICES = {
    "fert_lead": [None, {"lead": 2, "hours": [20, 21], "front": False}, {"lead": 3, "hours": [19, 20, 21], "front": False},
                  {"lead": 4, "hours": [18, 19, 20, 21], "front": False}, {"lead": 3, "hours": [19, 20, 21], "front": True},
                  {"lead": 6, "hours": [16, 17, 18, 19, 20, 21], "front": False}, {"lead": 2, "hours": [], "front": False}],
    "wheat_lead": [None, {"lead": 1, "hours": [], "front": False}, {"lead": 2, "hours": [], "front": False},
                   {"lead": 3, "hours": [], "front": True}],
    "premium_lead": [None, {"lead": 2, "items": ["MILK", "WOOL", "STRAWBERRY"]}, {"lead": 3, "items": ["MILK", "WOOL", "STRAWBERRY"]},
                     {"lead": 2, "items": ["MILK"]}, {"lead": 2, "items": ["WOOL"]}, {"lead": 2, "items": ["STRAWBERRY"]},
                     {"lead": 2, "items": ["EGG", "TOMATO", "CARROT"]}],
    "wheat_mm": [None, {"q": 20, "keep": 25}, {"q": 30, "keep": 25}, {"q": 40, "keep": 20}],
}


def parse_cfg(path):
    cfg = {"top": {}, "base": {}, "layers": {}}
    try:
        tree = ast.parse(open(path, encoding="utf-8").read())
    except Exception:
        return cfg
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            try:
                val = ast.literal_eval(node.value)
            except Exception:
                continue
            if name == "_CFG":
                return {"top": dict(val.get("top") or {}), "base": dict(val.get("base") or {}),
                        "layers": dict(val.get("layers") or {})}
            if name == "OVR_TOP":
                cfg["top"] = dict(val)
            elif name == "OVR_BASE":
                cfg["base"] = dict(val)
    return cfg


def mutate(rng, cfg):
    cfg = copy.deepcopy(cfg)
    tags = []
    for _ in range(rng.choice([1, 1, 2])):
        kind = rng.choice(["band", "top", "base", "layer", "layer"])
        if kind == "band":
            bands = dict(cfg["top"].get("_EAGER_BANDS", DEFAULT_BANDS))
            item = rng.choice(ITEMS3 + ("EGG", "TOMATO", "CARROT", "FERTILIZER"))
            lo, hi = bands.get(item, (0.3, 1.0))
            if rng.random() < 0.5:
                lo = rng.choice([0.1, 0.2, 0.3, 0.4, 0.5])
            else:
                hi = rng.choice([0.7, 0.8, 0.9, 1.0, 1.1, 1.3])
            bands[item] = (lo, max(hi, lo + 0.1))
            cfg["top"]["_EAGER_BANDS"] = bands
            tags.append(f"band{item[:3].lower()}{lo}-{hi}")
        elif kind == "top":
            key = rng.choice(sorted(TOP_CHOICES))
            vals = [v for v in TOP_CHOICES[key] if v != cfg["top"].get(key)]
            v = rng.choice(vals)
            cfg["top"][key] = v
            tags.append(f"{key.strip('_').lower()}{v}")
        elif kind == "base":
            keys = rng.choice(list(BASE_CHOICES))
            now = tuple(cfg["base"].get(k) for k in keys)
            vals = [v for v in BASE_CHOICES[keys] if tuple(v) != now]
            v = rng.choice(vals)
            for k, x in zip(keys, v):
                cfg["base"][k] = x
            tags.append(f"{keys[0].replace('V9_', '').lower()}{'-'.join(str(x) for x in v)}")
        else:
            name = rng.choice(sorted(LAYER_CHOICES))
            vals = [v for v in LAYER_CHOICES[name] if v != cfg["layers"].get(name)]
            v = rng.choice(vals)
            if v is None:
                cfg["layers"].pop(name, None)
                tags.append(f"{name}off")
            else:
                cfg["layers"][name] = v
                tags.append(f"{name}{v.get('lead', v.get('q', ''))}{'f' if v.get('front') else ''}")
    return cfg, "_".join(tags)


def queue_len():
    return len([f for f in os.listdir(os.path.join(ARENA, "queue")) if f.endswith(".txt")])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-queue", type=int, default=3)
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--seed", type=int, default=2)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    counter = 0
    while not os.path.exists(os.path.join(ARENA, "STOP_SEARCH")):
        if queue_len() < a.min_queue:
            champ = json.load(open(os.path.join(ARENA, "champion.json"), encoding="utf-8"))
            parent = parse_cfg(champ["path"])
            for _ in range(a.batch):
                counter += 1
                cfg, tag = mutate(rng, parent)
                name = f"e{a.seed}_{counter:03d}_{tag}"[:90].replace(".", "p").replace("-", "m")
                desc = f"进化第 {counter} 个，父本 {champ['name']}：{tag}"
                path = os.path.join(ROOT, "gold", "hybrid", f"cx_{name}.py")
                layers.write(path, name, desc, cfg)
                done = len(os.listdir(os.path.join(ARENA, "done")))
                n = queue_len() + done + 1
                open(os.path.join(ARENA, "queue", f"{n:03d}_{name}.txt"), "w", encoding="utf-8").write(path + "\n" + desc + "\n")
        time.sleep(60)


if __name__ == "__main__":
    main()
