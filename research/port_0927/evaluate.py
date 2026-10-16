"""Portable paired replay harness. Every result records code hashes and engine outcomes."""
import argparse
import glob
import gzip
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))


def records():
    seen = {}
    for p in sorted((ROOT / "data/games").glob("live_*.jsonl.gz")):
        with gzip.open(p, "rt") as fh:
            for line in fh:
                r = json.loads(line)
                if "42" in r["teams"] and len(r.get("shops") or []) == 8:
                    seen.setdefault(str(r["id"]), r)
    return seen


def run(job):
    import fastarena
    import forceshops
    from cfreplay import tape_agent
    r, path, mode = job
    forceshops.force(r["shops"])
    me = r["teams"].index("42")
    fns = [tape_agent(a) for a in r["acts"]]
    fn = None
    if path:
        fn = fastarena.load_agent(path)
        fns[me] = fn
    result = fastarena.run_game(*fns, r["seed"])
    rewards = result["rewards"]
    assert result["status"] == ["DONE", "DONE"] and not any(result["errors"]), result
    out = dict(id=r["id"], path=path, rewards=rewards,
               margin=rewards[me] - rewards[1-me], live=r["rewards"][me] - r["rewards"][1-me],
               status=result["status"], errors=result["errors"], t_max=result["t_max"][me],
               opponent=r["teams"][1-me], shops=r["shops"], seed=r["seed"])
    if mode == "fidelity":
        out["expected"] = r["rewards"]
        out["exact"] = rewards == r["rewards"]
    if fn is not None:
        ns = fn.__globals__
        out["fade"] = ns.get("_FD_REPORT", {})
        out["general"] = ns.get("_GF_REPORT", {})
        tg = ns.get("_TG_NS", {})
        out["trap"] = {k:v for k,v in tg.get("TEL", {}).items() if k not in ("devs", "cycles", "cf_cycles")}
        state = result["final_state"][me].observation
        out["end_shed"] = dict(state.private.shed)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["replay", "fidelity"])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--ids", help="JSON object of episode ids, or whitespace-separated text file")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--out", required=True)
    ap.add_argument("--source", help="one compressed jsonl source instead of the full archive")
    a = ap.parse_args()
    if a.source:
        with gzip.open(a.source, "rt") as fh:
            rs = {str(r["id"]):r for r in map(json.loads, fh) if "42" in r["teams"]}
    else:
        rs = records()
    if a.ids:
        raw = Path(a.ids).read_text()
        ids = set(json.loads(raw)) if a.ids.endswith(".json") else set(raw.split())
        missing = ids - rs.keys()
        if missing:
            raise ValueError(f"Missing {len(missing)} requested episodes: {sorted(missing)[:10]}")
        rs = {k:r for k,r in rs.items() if k in ids}
    rows = sorted(rs.values(), key=lambda r:r["id"])
    if a.limit:
        rows = rows[-a.limit:]
    paths = [str(Path(p).resolve()) for p in a.paths] or [None]
    jobs = [(r,p,a.mode) for r in rows for p in paths]
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    meta = {"engine":"1.32.7", "python":sys.version, "mode":a.mode, "games":len(rows),
            "sha256":{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths if p},
            "forced_shops":True}
    out.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2))
    print(f"{len(rows)} worlds, {len(jobs)} runs", flush=True)
    results = []
    start = time.monotonic()
    with mp.get_context("spawn").Pool(a.workers, maxtasksperchild=20) as pool, out.open("w") as fh:
        for result in pool.imap_unordered(run, jobs, chunksize=1):
            results.append(result)
            fh.write(json.dumps(result, ensure_ascii=False) + "\n")
            fh.flush()
            if len(results) % 40 == 0:
                print(f"completed {len(results)}/{len(jobs)}, {time.monotonic()-start:.0f}s", flush=True)
    for p in paths:
        sub = [r for r in results if r["path"] == p]
        summary = dict(path=p, n=len(sub), wins=sum(r["margin"]>0 for r in sub),
                       ties=sum(r["margin"]==0 for r in sub),
                       margin=round(statistics.mean(r["margin"] for r in sub),2),
                       exact=sum(r.get("exact",False) for r in sub))
        if len(paths)>1 and p!=paths[0]:
            base = {r["id"]:r["margin"] for r in results if r["path"] == paths[0]}
            delta = [r["margin"] - base[r["id"]] for r in sub]
            summary.update(delta=round(statistics.mean(delta),2),
                           flips_up=sum(base[r["id"]]<=0<r["margin"] for r in sub),
                           flips_down=sum(r["margin"]<=0<base[r["id"]] for r in sub),
                           changed=sum(d!=0 for d in delta))
        print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
