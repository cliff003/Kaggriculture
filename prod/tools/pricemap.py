r"""Mean price / base by product and day, split by how many open shops demand the product.

pricemap.py A B SEEDS   (plays A vs B on each seed, records the town prices every step)
"""
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "tools"))
import fastarena  # noqa: E402
from kaggle_environments.envs.kaggriculture import kaggriculture as K  # noqa: E402

BASE = {k: v["base"] for k, v in K.MARKET_PARAMS.items()}


def main():
    a, b, seeds = sys.argv[1], sys.argv[2], [int(s) for s in sys.argv[3].split(",")]
    acc = collections.defaultdict(list)   # (item, dayband, demand) -> ratios
    orig = K.interpreter
    for seed in seeds:
        def interp(state, env):
            out = orig(state, env)
            o = state[0].observation
            if hasattr(o, "market") and o.market and o.get("step", 0) % 6 == 0:
                st = o.get("step", 0)
                shops = o.town.get("unlocked_shops", [])
                for item, p in o.market["prices"].items():
                    if item not in BASE:
                        continue
                    dem = sum((2 if len(K.SHOPS[s]) == 1 else 1) for s in shops if item in K.SHOPS[s])
                    acc[(item, min(st // 24 // 5, 5), min(dem, 3))].append(p / BASE[item])
            return out
        K.interpreter = interp
        try:
            fastarena.run_game(fastarena.load_agent(a), fastarena.load_agent(b), seed)
        finally:
            K.interpreter = orig
    items = sorted(BASE)
    print("price/base by 5-day band (rows) and demand units from shops (0,1,2,3+); n in brackets")
    for item in items:
        print(item)
        for band in range(6):
            row = []
            for dem in range(4):
                v = acc.get((item, band, dem))
                row.append(f"{sum(v) / len(v):5.2f}[{len(v):3d}]" if v else "     -     ")
            print(f"   d{band * 5:2d}-{band * 5 + 4:2d} " + "  ".join(row))


if __name__ == "__main__":
    main()
