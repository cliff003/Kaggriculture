r"""Watch the Kaggriculture Code page: top public notebooks by score and what changed since the last run.

.venv\Scripts\python.exe tools\watch_code.py [--top 30] [--ref abhinav0370/cha22-agent]

Uses the public web endpoint KernelsService/ListKernels (no login; the same score the Code page shows).
Snapshots go to data/watch/. Flags: new in the top N, new version, score up by 30 or more, and anything 30 or more
above the reference notebook with a new version in the last 3 days (old notebooks keep scores from a weaker field).
"""
import argparse
import datetime as dt
import json
import os
import sys

import kg

LIST_KERNELS_URL = "https://www.kaggle.com/api/i/kernels.KernelsService/ListKernels"
COMPETITION_ID = 147734
WATCH = os.path.join(kg.DATA, "watch")


def fetch(top, gap):
    out = []
    page = 1
    while len(out) < top:
        body = {"kernelFilterCriteria": {"search": "", "listRequest": {
            "competitionId": COMPETITION_ID, "sortBy": "SCORE_DESCENDING", "pageSize": 20, "group": "EVERYONE",
            "page": page, "modelIds": [], "modelInstanceIds": [], "excludeKernelIds": [], "tagIds": "",
            "excludeResultsFilesOutputs": False, "wantOutputFiles": False, "excludeNonAccessedDatasources": True}},
            "detailFilterCriteria": {"deletedAccessBehavior": "RETURN_NOTHING", "unauthorizedAccessBehavior": "RETURN_NOTHING",
                                     "excludeResultsFilesOutputs": False, "wantOutputFiles": False, "kernelIds": [],
                                     "outputFileTypes": [], "includeInvalidDataSources": False}}
        ks = kg.web("POST", LIST_KERNELS_URL, gap, json=body).json().get("kernels") or []
        if not ks:
            break
        for k in ks:
            if k.get("bestPublicScore") is None:
                continue
            out.append({"id": k["id"], "ref": f"{k['author']['userName']}/{k['currentUrlSlug']}", "title": k.get("title", ""),
                        "score": k["bestPublicScore"], "version": k.get("scriptVersionId"),
                        "updated": k.get("scriptVersionDateCreated") or k.get("lastRunTime") or "",
                        "votes": k.get("totalVotes", 0)})
        page += 1
    return out[:top]


def main():
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(errors="replace")
    p = argparse.ArgumentParser(description="Code 页前 N 名 notebook 的变化")
    p.add_argument("--top", type=int, default=30)
    p.add_argument("--ref", default="abhinav0370/cha22-agent", help="拿来比较的 notebook（默认 cha22 原版）")
    p.add_argument("--gap", type=float, default=6.0)
    a = p.parse_args()

    now = dt.datetime.now(dt.timezone.utc)
    cur = fetch(a.top, a.gap)
    os.makedirs(WATCH, exist_ok=True)
    last_path = os.path.join(WATCH, "code_last.json")
    prev = None
    if os.path.exists(last_path):
        with open(last_path, encoding="utf-8") as f:
            prev = json.load(f)
    snap = {"time": now.isoformat(timespec="seconds"), "kernels": cur}
    for path in (os.path.join(WATCH, f"code_{now:%Y%m%d_%H%M}.json"), last_path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(snap, f, ensure_ascii=False, indent=1)

    old = {k["id"]: k for k in (prev or {}).get("kernels", [])}
    ref = next((k for k in cur if k["ref"] == a.ref), None)
    rows, alerts = [], []
    for i, k in enumerate(cur, 1):
        o = old.get(k["id"])
        age = now - dt.datetime.fromisoformat(k["updated"].replace("Z", "+00:00")) if k["updated"] else None
        marks = []
        if prev is not None and o is None:
            marks.append("新进前 %d" % a.top)
        if o is not None and o["version"] != k["version"]:
            marks.append("新版本")
        if o is not None and k["score"] - o["score"] >= 30:
            marks.append(f"涨了 {k['score'] - o['score']:.0f}")
        if ref is not None and k["score"] >= ref["score"] + 30 and age is not None and age < dt.timedelta(days=3):
            marks.append("比 cha22 高 30 分以上且 3 天内更新")
        if marks:
            alerts.append(f"{k['ref']}（{k['score']:.1f}）：{'，'.join(marks)}")
        rows.append([i, k["ref"], f"{k['score']:.1f}", "" if o is None else f"{k['score'] - o['score']:+.1f}",
                     f"{age.days} 天前" if age and age.days else (f"{age.seconds // 3600} 小时前" if age else ""), k["votes"],
                     "，".join(marks)])

    since = f"，上次 {prev['time'][:16].replace('T', ' ')} UTC" if prev else "（第一次运行，没有可比的快照）"
    print(f"Code 页前 {len(cur)} 名，{now:%Y-%m-%d %H:%M} UTC{since}")
    print("需要注意：" if alerts else "没有需要注意的变化")
    for x in alerts:
        print("  " + x)
    print()
    kg.table(["名次", "notebook", "分数", "变化", "最近版本", "票数", "标记"], rows)


if __name__ == "__main__":
    main()
