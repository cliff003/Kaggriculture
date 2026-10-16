r"""Build a v7c-style agent in one go: build_v5.py base -> compose_v7 (wheat lead-sell block of v7b)
-> add_sheepfeed -> add_fertmore. Extra arguments go to build_v5.py.

.venv\Scripts\python.exe tools\build_v7chain.py OUT_DIR [--fert-extra 0] [--patch r51] -- [build_v5.py options]

With the default build options (below) the result is byte-identical in behaviour to v7c.
"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = (os.path.join(ROOT, ".venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(ROOT, ".venv", "bin", "python"))
BASE = os.path.join(ROOT, "submissions", "v4_public_cha22_verbatim", "main.py")
DEFAULT = ["--guard-all-items", "--sort-sells", "--eager-from", "288",
           "--eager-items", "MILK:0.3:99,STRAWBERRY:0.3:99,WOOL:0.3:99", "--label", "cha22"]


# --patch NAME: string patches applied to the cha22 source before it is embedded (research; a submission built
# with a patch must say so in its header and NOTICE, since the base is then no longer embedded unchanged)
PATCHES = {
    # R51 fertilizer helper relaxed (gold/results/topstudy_0925.md: r51_cheap)
    "r51": [(b"if value<1.5*cost+50 or farm['money']<total_cost+cost+3000:break",
             b"if value<1.0*cost+20 or farm['money']<total_cost+cost+3000:break"),
            (b"new_gross-1.5*fertilizer*len(new_path)", b"new_gross-0.75*fertilizer*len(new_path)"),
            (b"_R51_INPUT_MAX_WORKERS=2", b"_R51_INPUT_MAX_WORKERS=3")],
    # R51 tours take spare shed fertilizer (stock the route's own pickups later today do not need) and only buy
    # the shortfall, instead of buying every tour's fertilizer at the market
    "r51own": [(b"changed=copy.deepcopy(action);changed['market'] += [['BUY_PRODUCT','FERTILIZER',total_q+topup]]"
                b"+[['HIRE'] for _ in plans];return changed",
                b"later=sum(max(0,int(c[2]) if len(c)>2 else 1) for a in planned[hour+1:] for c in "
                b"[a.get('farmer') or ['PASS'],*(a.get('hands') or [])] if len(c)>1 and c[:2]==['PICKUP','FERTILIZER'])\n"
                b"    buy=max(0,total_q+later-available)\n"
                b"    changed=copy.deepcopy(action);changed['market'] += ([['BUY_PRODUCT','FERTILIZER',buy]] if buy else [])"
                b"+[['HIRE'] for _ in plans];return changed")],
    # V219 tomato investment (day 18, >= 3 pizza/farmers shops) on 15 SE cells (rows 5-7) instead of 10 (rows 5-6):
    # 15 seeds, two crop workers on the watering days, one row per worker when three, fertilizer loads for 15,
    # R53's fixed 10-cell labour groups off. (An opponent planting 18 out-earned our 10 by ~3.9k in live play.)
    "v219x15": [(b"extra += [['BUY_LAND'],['BUY_SEED','TOMATO',10]]", b"extra += [['BUY_LAND'],['BUY_SEED','TOMATO',15]]"),
                (b"'targets':[(x,y) for y in (5,6) for x in range(5,10)]",
                 b"'targets':[(x,y) for y in (5,6,7) for x in range(5,10)]"),
                (b"crop_workers=1 if day in (19,20,21,22,23,25) and offset<=2 else (3 if 26<=day<=28 else 2)",
                 b"crop_workers=2 if day in (19,20,21,22,23,25) and offset<=2 else 3"),
                (b"elif pending['crop_workers']==2:targets=state['targets'][index*5:index*5+5]",
                 b"elif pending['crop_workers']==2:targets=state['targets'][index*8:index*8+8]"),
                (b"else:targets=[[(5,5),(6,5),(7,5)],[(8,5),(9,5),(9,6),(8,6)],[(5,6),(6,6),(7,6)]][index]",
                 b"else:targets=state['targets'][index*5:index*5+5]"),
                (b"desired=role.get('fertilizer_quantity',10 if role['kind']=='fertilizer' else 5)",
                 b"desired=role.get('fertilizer_quantity',15 if role['kind']=='fertilizer' else 8)", 2),
                (b"if day not in (26,27,28) or step%24>2:return None", b"if True:return None"),
                (b"if not state.get('committed'):budget+=4500", b"if not state.get('committed'):budget+=4750"),
                (b"quantity=max(10,10+native_need-max(0,stock.get('FERTILIZER',0)))",
                 b"quantity=max(15,15+native_need-max(0,stock.get('FERTILIZER',0)))"),
                (b"farm=obs['farms'][obs['player']];day=int(obs['step'])//24;bonus=0\r\n    for y in (5,6):",
                 b"farm=obs['farms'][obs['player']];day=int(obs['step'])//24;bonus=0\r\n    for y in (5,6,7):"),
                (b"10*fertilizer+extra_labor", b"15*fertilizer+extra_labor")],
    # audits of cha22's own production investments: switch one off
    "v219off": [(b"def _v219_qualifies(obs, native):\r\n    farm=obs['farms'][obs['player']]\r\n",
                 b"def _v219_qualifies(obs, native):\r\n    return False\r\n    farm=obs['farms'][obs['player']]\r\n")],
    "v233off": [(b"def _v233_eligible(obs,native):\r\n    farm=obs['farms'][obs['player']];prices=obs['market']['prices']\r\n",
                 b"def _v233_eligible(obs,native):\r\n    return False\r\n"
                 b"    farm=obs['farms'][obs['player']];prices=obs['market']['prices']\r\n")],
}


def run(args):
    r = subprocess.run([PY] + args, cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit(r.returncode)


def main():
    argv = sys.argv[1:]
    out = argv[0]
    rest = argv[1:]
    fert_extra = "0"
    if "--fert-extra" in rest:
        i = rest.index("--fert-extra")
        fert_extra = rest[i + 1]
        rest = rest[:i] + rest[i + 2:]
    patches = []
    while "--patch" in rest:
        i = rest.index("--patch")
        patches.append(rest[i + 1])
        rest = rest[:i] + rest[i + 2:]
    if "--" in rest:
        rest = rest[rest.index("--") + 1:]
    build_args = rest or DEFAULT
    with tempfile.TemporaryDirectory() as tmp:
        base = BASE
        if patches:
            src = open(BASE, "rb").read()
            for name in patches:
                for entry in PATCHES[name]:
                    old, new = entry[:2]
                    count = entry[2] if len(entry) > 2 else 1
                    assert src.count(old) == count, old
                    src = src.replace(old, new)
            base = os.path.join(tmp, "patched_base.py")
            with open(base, "wb") as f:
                f.write(src)
        run([os.path.join("tools", "build_v5.py"), base, os.path.join(tmp, "base")] + build_args)
        run([os.path.join("tools", "compose_v7.py"), os.path.join(tmp, "base", "main.py"), os.path.join(tmp, "comp")])
        run([os.path.join("tools", "add_sheepfeed.py"), os.path.join(tmp, "comp", "main.py"), os.path.join(tmp, "sf")])
        run([os.path.join("tools", "add_fertmore.py"), os.path.join(tmp, "sf", "main.py"), out, "--extra", fert_extra])
    print("wrote", os.path.join(out, "main.py"))


if __name__ == "__main__":
    main()
