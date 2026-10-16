r"""King-of-the-hill arena (team 42, gold effort).

The champion plays every challenger dropped into gold/arena/queue/ (one .txt per challenger: first line the path of its
main.py, optional second line a short description). Each match uses a fresh block of seeds with the real shop sequences
of DSM's games forced in (gstat --worlds), both seats; from 03:00 on 09-25 the block of worlds rotates with the seeds
(--world0 = seed0 % 92), before that every match used worlds 0-31.

Title rule (from 03:15 on 09-25; the 02:40 rule compared the panel only with v6, so a challenger that beat the champion
head to head but was clearly worse on the panel could still take the title and throw away a gain):
1. head to head, score = wins + ties/2 of the challenger over 64 games (128 when the first 64 land in 52-60%);
2. panel v2 (gold/arena/biggauntlet.run2: 7 fixed opponents x 28 DSM worlds 60-87, one game per world, 196 games), run
   for every challenger with head-to-head >= 45% and fewer than 90% ties, compared with the CHAMPION's panel v2:
   title if  (a) head to head >= 60% (>= 56% of 128) and panel wins >= champion - 2 and mean >= champion - 150, or
             (b) head to head >= 45% and panel wins >= champion + 5 and mean >= champion - 100, or
             (c) head to head >= 45% and panel mean >= champion + 400 and wins >= champion - 1.
Logs: gold/arena/log.jsonl, gold/arena/gauntlet.jsonl, gold/arena/standings.md. Idle queue: re-check every 5 minutes.
Stops when gold/arena/STOP exists.

.venv\Scripts\python.exe gold\arena\arena.py [--workers 8] [--seeds 32]
"""
import argparse
import datetime as dt
import glob
import json
import os
import shutil
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
ARENA = os.path.join(ROOT, "gold", "arena")
sys.path.insert(0, ARENA)
import biggauntlet as BG  # noqa: E402

PY = (os.path.join(ROOT, ".venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(ROOT, ".venv", "bin", "python"))
QUEUE = os.path.join(ARENA, "queue")
DONE = os.path.join(ARENA, "done")
LOG = os.path.join(ARENA, "log.jsonl")
STAND = os.path.join(ARENA, "standings.md")
CHAMP = os.path.join(ARENA, "champion.json")
GLOG = os.path.join(ARENA, "gauntlet.jsonl")
GLOG2 = os.path.join(ARENA, "gauntlet2.jsonl")
CHAMP0 = os.path.join(ARENA, "champ0", "main.py")
SEED_BASE = 80000
WIN_TOL, DIFF_TOL = 4, 600


def now():
    return dt.datetime.now().strftime("%m-%d %H:%M")


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def next_seed0():
    used = [r["seed0"] + r["seeds"] for r in load_jsonl(LOG)]
    return max([SEED_BASE] + used)


def play(a, b, seeds, seed0, workers, tag):
    js = os.path.join(ARENA, "games", f"{tag}_{seed0}.json")
    os.makedirs(os.path.dirname(js), exist_ok=True)
    subprocess.run([PY, os.path.join(ROOT, "gold", "tools", "gstat.py"), a, b, "--seeds", str(seeds), "--seed0", str(seed0),
                    "--both", "--workers", str(workers), "--worlds", "--world0", str(seed0 % 92), "--json", js], cwd=ROOT,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    d = json.load(open(js))
    w = l = t = 0
    diffs, errs = [], 0
    for g in d["games"]:
        ra, rb = g["rewards"][g["cand_side"]], g["rewards"][1 - g["cand_side"]]
        errs += sum(g.get("errors") or [0])
        if ra is None or rb is None:
            l += 1
            continue
        diffs.append(ra - rb)
        if ra > rb:
            w += 1
        elif ra < rb:
            l += 1
        else:
            t += 1
    return {"w": w, "l": l, "t": t, "diff": sum(diffs) / max(1, len(diffs)), "errors": errs}


def panel(path, name, workers):
    row = BG.run(path, name, workers)
    wins = sum(v[0] + 0.5 * v[2] for v in row.values())
    mean = sum(v[3] for v in row.values()) / len(row)
    return {"results": {k: {"w": v[0], "l": v[1], "t": v[2], "diff": v[3]} for k, v in row.items()},
            "wins": wins, "mean": mean}


def panel2(path, name, workers):
    row = BG.run2(path, name, workers)
    wins = sum(v[0] + 0.5 * v[2] for v in row.values())
    mean = sum(v[3] for v in row.values()) / len(row)
    return {"results": {k: {"w": v[0], "l": v[1], "t": v[2], "diff": v[3]} for k, v in row.items()},
            "wins": wins, "mean": mean}


def write_standings(champ, ref):
    rows = load_jsonl(LOG)
    lines = ["# 擂台赛（gold/arena）", "", f"更新：{now()}　当前擂主：**{champ['name']}**（{champ['desc']}）", "",
             "| 时间 | 挑战者 | 擂主 | 局数 | 挑战者 胜-负-平 | 得分率 | 平均差 | 结果 |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        n = r["w"] + r["l"] + r["t"]
        rate = (r["w"] + 0.5 * r["t"]) / max(1, n)
        res = "**换擂主**" if r["won"] else ("正面赢但体检不过" if r.get("panel_fail") else "守擂")
        lines.append(f"| {r['time']} | {r['challenger']} | {r['champion']} | {n} | {r['w']}-{r['l']}-{r['t']} | "
                     f"{rate:.0%} | {r['diff']:+.0f} | {res} |")
    g = load_jsonl(GLOG)
    if g:
        opps = BG.OPPS
        lines += ["", "## 大体检（6 个固定对手，各 16 种子双座位，种子 61000 起）", "",
                  f"对照线：线上 v6 {ref['wins']:.0f}/192 胜，平均差 {ref['mean']:+.0f}；换擂主要求胜场不少于 v6 减 {WIN_TOL}、平均差不低于 v6 减 {DIFF_TOL}。", "",
                  "| 时间 | 版本 | " + " | ".join(opps) + " | 胜/192 | 平均差 | 通过 |", "|---|---|" + "---|" * len(opps) + "---|---|---|"]
        for e in g:
            cells = []
            for k in opps:
                r = e["results"].get(k)
                cells.append(f"{r['w']}-{r['l']}-{r['t']}（{r['diff']:+.0f}）" if r else "")
            lines.append(f"| {e['time']} | {e['name']} | " + " | ".join(cells) + f" | {e['wins']:.0f} | {e['mean']:+.0f} | "
                         f"{'是' if e.get('passed', True) else '否'} |")
    g2 = load_jsonl(GLOG2)
    if g2:
        opps = BG.OPPS2
        n2 = 28 * len(opps)
        lines += ["", f"## 体检 v2（{len(opps)} 个固定对手 × DSM 世界 60 到 87，每个世界一局、座位交替，共 {n2} 局；03:15 起换擂主看这个）", "",
                  "| 时间 | 版本 | " + " | ".join(opps) + f" | 胜/{n2} | 平均差 | 比擂主 胜场 | 比擂主 平均差 | 换擂主 |",
                  "|---|---|" + "---|" * len(opps) + "---|---|---|---|---|"]
        for e in g2:
            cells = []
            for k in opps:
                r = e["results"].get(k)
                cells.append(f"{r['w']}-{r['l']}-{r['t']}（{r['diff']:+.0f}）" if r else "")
            dw = e.get("dw")
            dm = e.get("dm")
            lines.append(f"| {e['time']} | {e['name']} | " + " | ".join(cells) + f" | {e['wins']:.0f} | {e['mean']:+.0f} | "
                         f"{'' if dw is None else f'{dw:+.0f}'} | {'' if dm is None else f'{dm:+.0f}'} | "
                         f"{'是' if e.get('passed') else ('擂主' if e.get('champion') else '否')} |")
    lines += ["", "规则（09-25 03:15 起）：先打 64 局正面（52% 到 60% 加赛到 128 局），正面不低于 45% 且平局少于九成的都打体检 v2，和现任擂主的体检 v2 比："
              "（a）正面 ≥ 60%（加赛后 ≥ 56%）且体检胜场不少于擂主减 2、平均差不低于擂主减 150（03:40 起；之前是减 3、减 250）；或（b）正面 ≥ 45% 且体检胜场比擂主多 5 场以上、平均差不低于擂主减 100；"
              "或（c）正面 ≥ 45% 且体检平均差比擂主高 400 以上、胜场不少于擂主减 1。满足其一才换擂主。"]
    lines += ["", "旧规则（09-25 02:40 到 03:15）：挑战者 64 局正面得分率达到 60%（或 52% 到 60% 时加赛到 128 局达到 56%），"
              "并且大体检胜场不比线上 v6 少 4 场以上、平均差不低于 v6 减 600（02:55 起；02:40 到 02:55 是减 250），才换擂主。02:40 之前只看正面交手，门槛是 55%/53%（02:25 起 60%/56%）。"]
    open(STAND, "w", encoding="utf-8").write("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--seeds", type=int, default=32)
    a = ap.parse_args()
    os.makedirs(QUEUE, exist_ok=True)
    os.makedirs(DONE, exist_ok=True)
    ref = panel(CHAMP0, "v6", a.workers)
    champ = json.load(open(CHAMP, encoding="utf-8"))
    write_standings(champ, ref)
    while not os.path.exists(os.path.join(ARENA, "STOP")):
        items = sorted(glob.glob(os.path.join(QUEUE, "*.txt")))
        if not items:
            time.sleep(300)
            continue
        item = items[0]
        lines = [l.strip() for l in open(item, encoding="utf-8").read().splitlines() if l.strip()]
        name = os.path.splitext(os.path.basename(item))[0]
        path = lines[0]
        desc = lines[1] if len(lines) > 1 else ""
        if not os.path.exists(path):
            shutil.move(item, os.path.join(DONE, os.path.basename(item)))
            continue
        seed0 = next_seed0()
        r = play(path, champ["path"], a.seeds, seed0, a.workers, name)
        seeds_used = a.seeds
        n = r["w"] + r["l"] + r["t"]
        rate = (r["w"] + 0.5 * r["t"]) / max(1, n)
        if 0.52 <= rate < 0.60 and r["errors"] == 0:
            r2 = play(path, champ["path"], a.seeds, seed0 + a.seeds, a.workers, name + "_x")
            for k in ("w", "l", "t"):
                r[k] += r2[k]
            r["diff"] = (r["diff"] + r2["diff"]) / 2
            r["errors"] += r2["errors"]
            seeds_used += a.seeds
            n = r["w"] + r["l"] + r["t"]
            rate = (r["w"] + 0.5 * r["t"]) / max(1, n)
            won = rate >= 0.56
        else:
            won = rate >= 0.60
        if r["errors"]:
            won = False
        rec = {"time": now(), "challenger": name, "champion": champ["name"], "path": path, "desc": desc,
               "seed0": seed0, "seeds": seeds_used, "w": r["w"], "l": r["l"], "t": r["t"], "diff": r["diff"],
               "errors": r["errors"], "won": False, "h2h_ok": won}
        if r["errors"] == 0 and (won or (rate >= 0.45 and r["t"] < 0.9 * n)):
            c = panel2(champ["path"], champ["name"], a.workers)
            p = panel2(path, name, a.workers)
            dw, dm = p["wins"] - c["wins"], p["mean"] - c["mean"]
            title = ((won and dw >= -2 and dm >= -150) or (rate >= 0.45 and dw >= 5 and dm >= -100)
                     or (rate >= 0.45 and dm >= 400 and dw >= -1))
            if not any(e.get("name") == champ["name"] for e in load_jsonl(GLOG2)):
                with open(GLOG2, "a", encoding="utf-8") as f:
                    f.write(json.dumps(dict(c, time=now(), name=champ["name"], champion=True), ensure_ascii=False) + chr(10))
            with open(GLOG2, "a", encoding="utf-8") as f:
                f.write(json.dumps(dict(p, time=now(), name=name, passed=title, dw=dw, dm=dm), ensure_ascii=False) + chr(10))
            rec["panel2"] = {"wins": p["wins"], "mean": p["mean"], "dw": dw, "dm": dm}
            rec["won"] = title
            if won and not title:
                rec["panel_fail"] = True
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if rec["won"]:
            champ = {"name": name, "path": path, "desc": desc, "since": now()}
            json.dump(champ, open(CHAMP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        shutil.move(item, os.path.join(DONE, os.path.basename(item)))
        write_standings(champ, ref)


if __name__ == "__main__":
    main()
