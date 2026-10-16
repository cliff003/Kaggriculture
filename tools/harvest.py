r"""Harvest live episodes into compact, re-simulatable game records (JSON lines, gzip).

.venv\Scripts\python.exe tools\harvest.py OUT.jsonl.gz --sub SUB_ID [--last N] [--result 胜|负|平]
.venv\Scripts\python.exe tools\harvest.py OUT.jsonl.gz --ids EPISODE_ID [EPISODE_ID ...]

--sub reads data/episodes/SUB_ID.json (written by `kg.py episodes SUB_ID`), newest games first.
A record keeps what exact local re-simulation needs: seed, both sides' per-step actions, team
names, server rewards, final shops, submission ids and pre-game ratings. Raw replays (~32 MB)
are deleted after conversion; a record is ~0.2 MB. Episodes already in OUT are skipped.
"""
import argparse
import gzip
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kg


def load(path):
    if not os.path.exists(path):
        return []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def episode_meta(sub_id):
    with open(os.path.join(kg.DATA, "episodes", f"{sub_id}.json"), encoding="utf-8") as f:
        data = json.load(f)
    out = []
    for e in data.get("episodes") or []:
        if e.get("state") != "COMPLETED" or e.get("type") != "EPISODE_TYPE_PUBLIC":
            continue
        agents = sorted(e.get("agents") or [], key=lambda g: g.get("index", 0))
        me = next((g for g in agents if g.get("submissionId") == sub_id), None)
        if me is None or len(agents) != 2:
            continue
        opp = agents[1 - agents.index(me)]
        margin = (me.get("reward") or 0.0) - (opp.get("reward") or 0.0)
        out.append({"id": e["id"], "end": e.get("endTime") or "",
                    "result": "胜" if margin > 0 else "负" if margin < 0 else "平",
                    "subs": [g.get("submissionId") for g in agents],
                    "scores": [g.get("initialScore") for g in agents]})
    out.sort(key=lambda m: m["end"], reverse=True)
    return out


def record(eid, meta, k):
    tmp = os.path.join(kg.DATA, "tmp")
    os.makedirs(tmp, exist_ok=True)
    kg.retry(lambda: k.competition_episode_replay(eid, path=tmp, quiet=True), f"replay {eid}")
    path = os.path.join(tmp, f"episode-{eid}-replay.json")
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    finally:
        os.remove(path)
    info = d.get("info") or {}
    steps = d["steps"]
    return {"id": eid, "seed": info.get("seed"), "teams": info.get("TeamNames"),
            "rewards": d.get("rewards"), "statuses": d.get("statuses"),
            "shops": steps[-1][0]["observation"]["town"]["unlocked_shops"],
            "subs": (meta or {}).get("subs"), "scores": (meta or {}).get("scores"),
            "acts": [[st[i].get("action") for st in steps] for i in range(2)]}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("out")
    p.add_argument("--sub", type=int)
    p.add_argument("--ids", type=int, nargs="*", default=[])
    p.add_argument("--last", type=int, default=0)
    p.add_argument("--result", choices=["胜", "负", "平"])
    a = p.parse_args()
    metas = {}
    ids = list(a.ids)
    if a.sub:
        ms = [m for m in episode_meta(a.sub) if not a.result or m["result"] == a.result]
        ms = ms[:a.last] if a.last else ms
        metas = {m["id"]: m for m in ms}
        ids += [m["id"] for m in ms]
    have = {g["id"] for g in load(a.out)}
    todo = [i for i in dict.fromkeys(ids) if i not in have]
    print(f"{len(ids)} 局，已有 {len(ids) - len(todo)}，要下载 {len(todo)}")
    k = kg.api()
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    for n, eid in enumerate(todo, 1):
        t = time.time()
        rec = record(eid, metas.get(eid), k)
        with gzip.open(a.out, "at", encoding="utf-8") as f:
            f.write(json.dumps(rec, separators=(",", ":")) + "\n")
        print(f"[{n}/{len(todo)}] {eid} {rec['teams']} {rec['rewards']} {time.time() - t:.1f}s")
        time.sleep(1.0)


if __name__ == "__main__":
    main()
