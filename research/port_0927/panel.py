"""Paired tests on independently drawn shop worlds, including reactive phase-shift rivals."""
import argparse
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import random
import statistics
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
SHOPS = ["BAKERY", "PIZZA_SHOP", "BRUNCH_SPOT", "YARN_STORE", "ICE_CREAM_SHOP", "PET_CAFE", "SMOOTHIE_SHOP", "FARMERS_MARKET"]


def run(job):
    import fastarena
    import forceshops
    name, rival, path, seed, shops, me = job
    forceshops.force(shops)
    fns = [fastarena.load_agent(path), fastarena.load_agent(rival)]
    if me:
        fns.reverse()
    result = fastarena.run_game(*fns, seed)
    assert result["status"] == ["DONE", "DONE"] and not any(result["errors"])
    return dict(opponent=name, path=path, seed=seed, shops=shops, seat=me,
                rewards=result["rewards"], margin=result["rewards"][me]-result["rewards"][1-me],
                status=result["status"], errors=result["errors"], t_max=result["t_max"][me],
                general=fns[me].__globals__.get("_GF_REPORT",{}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--worlds", type=int, default=30)
    ap.add_argument("--seed", type=int, default=2026092701)
    ap.add_argument("--workers", type=int, default=7)
    ap.add_argument("--stress", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rivals = {n:str(ROOT / "research/panel" / n / "main.py") for n in
              ("cha22", "emu_eager", "emu_eager_m", "morewheat", "rescue", "herdsafe_race", "v15stack", "emu_tick0")}
    if a.stress:
        rivals = {}
        raw = (ROOT / "research/panel/emu_tick0/main.py").read_text()
        for p, until in ((1,716),(2,716),(3,716),(3,500)):
            name = f"phase{p}_until{until}"
            path = Path(a.out).parent / name / "main.py"
            path.parent.mkdir(parents=True, exist_ok=True)
            old = 'if step % 4 != 0 or step // 24 < CFG["FROM_DAY"] or step > 716:'
            assert raw.count(old) == 1
            path.write_text(raw.replace(old,f'if step % 4 != {p} or step // 24 < CFG["FROM_DAY"] or step > {until}:'))
            rivals[name] = str(path.resolve())
    rng = random.Random(a.seed)
    worlds = [(a.seed+i, [rng.choice(SHOPS) for _ in range(8)], i%2) for i in range(a.worlds)]
    assert len({tuple(w[1]) for w in worlds}) == len(worlds)
    paths = [str(Path(p).resolve()) for p in a.paths]
    jobs = [(n,r,p,s,sh,me) for s,sh,me in worlds for n,r in rivals.items() for p in paths]
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix('.meta.json').write_text(json.dumps(dict(seed=a.seed, worlds=worlds,
        sha256={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths},
        rivals={n:hashlib.sha256(Path(p).read_bytes()).hexdigest() for n,p in rivals.items()}),indent=2))
    results = []
    print(f"{len(worlds)} distinct worlds, {len(rivals)} opponents, {len(jobs)} runs", flush=True)
    with mp.get_context('spawn').Pool(a.workers, maxtasksperchild=20) as pool, out.open('w') as fh:
        for r in pool.imap_unordered(run,jobs):
            results.append(r)
            fh.write(json.dumps(r)+'\n'); fh.flush()
            if len(results)%60==0:
                print(f"completed {len(results)}/{len(jobs)}",flush=True)
    key = lambda r:(r['opponent'],r['seed'],r['seat'])
    base={key(r):r['margin'] for r in results if r['path']==paths[0]}
    for p in paths:
        sub=[r for r in results if r['path']==p]
        print(json.dumps(dict(path=p, n=len(sub), wins=sum(r['margin']>0 for r in sub),
            ties=sum(r['margin']==0 for r in sub),
            mean_delta=statistics.mean(r['margin']-base[key(r)] for r in sub),
            flips_up=sum(base[key(r)]<=0<r['margin'] for r in sub),
            flips_down=sum(r['margin']<=0<base[key(r)] for r in sub),
            changed=sum(r['margin']!=base[key(r)] for r in sub))),flush=True)


if __name__=='__main__':
    main()
