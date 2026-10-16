r"""Kaggle queries for Kaggriculture, team 42: leaderboard, submissions, episodes, replays.

.venv\Scripts\python.exe tools\kg.py lb                          rank, rating, medal lines
.venv\Scripts\python.exe tools\kg.py subs                        team submissions, which two are live
.venv\Scripts\python.exe tools\kg.py episodes SUB_ID [SUB_ID ...] [--last N]
.venv\Scripts\python.exe tools\kg.py replay EPISODE_ID OUT.json [--public]
.venv\Scripts\python.exe tools\kg.py fetch SUB_ID [SUB_ID ...]   our own submission files -> data/uploads/<id>/

lb, subs, replay and fetch use the official API (credentials in ~/.kaggle). The official episode list has no
ratings, so episodes uses the public web endpoint EpisodeService/ListEpisodes (raw JSON kept in
data/episodes/). That endpoint returns 429 after about 10 quick calls, so web calls are spaced --gap
seconds apart (across processes, via data/.kg_web_last) and every call backs off on 429/5xx.
"""
import argparse
import csv
import hashlib
import io
import json
import os
import re
import statistics
import sys
import time
import unicodedata
import zipfile

import requests

COMP = "kaggriculture"
TEAM_ID = 16908623
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
LIST_EPISODES_URL = "https://www.kaggle.com/api/i/competitions.EpisodeService/ListEpisodes"
PUBLIC_REPLAY_URL = "https://www.kaggle.com/competitions/episodes/{}/replay.json"
RETRY_STATUS = {429, 500, 502, 503, 504}


def api():
    import kaggle  # authenticates from ~/.kaggle on import
    if not getattr(kaggle.api, "_authenticated", False):
        kaggle.api.authenticate()  # prints the credential help and exits if nothing works
    return kaggle.api


def retry(call, what, tries=5, base=10.0):
    for k in range(tries):
        try:
            return call()
        except (requests.ConnectionError, requests.Timeout, requests.exceptions.ChunkedEncodingError) as e:
            err, wait = e, base * 2 ** k
        except requests.HTTPError as e:
            if e.response is None or e.response.status_code not in RETRY_STATUS:
                raise
            err, wait = e, base * 2 ** k
            after = e.response.headers.get("Retry-After", "")
            if after.isdigit():
                wait = max(wait, float(after))
        if k == tries - 1:
            raise err
        print(f"{what}: {err}，{wait:.0f} 秒后重试（第 {k + 1} 次）", file=sys.stderr)
        time.sleep(wait)


def web(method, url, gap, **kw):
    stamp = os.path.join(DATA, ".kg_web_last")

    def call():
        try:
            wait = min(gap, os.path.getmtime(stamp) + gap - time.time())
        except OSError:
            wait = 0
        if wait > 0:
            time.sleep(wait)
        os.makedirs(DATA, exist_ok=True)
        with open(stamp, "w") as f:
            f.write(url)
        r = requests.request(method, url, timeout=120, **kw)
        r.raise_for_status()
        return r

    return retry(call, url.rsplit("/", 1)[-1])


def width(s):
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def isnum(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def table(headers, rows):
    rows = [["" if v is None else str(v) for v in r] for r in rows]
    ws = [max(map(width, col)) for col in zip(headers, *rows)]
    # right-align a column only when every non-empty body cell in it is a number
    right = [all(isnum(c) for c in col if c) for col in zip(*rows)] if rows else [False] * len(headers)

    def line(cells):
        out = []
        for c, w, r in zip(cells, ws, right):
            pad = " " * (w - width(c))
            out.append(pad + c if r else c + pad)
        return "  ".join(out).rstrip()

    print(line(headers))
    print("  ".join("-" * w for w in ws))
    for r in rows:
        print(line(r))


def cmd_lb(a):
    k = api()
    folder = os.path.join(DATA, "lb")
    retry(lambda: k.competition_leaderboard_download(a.comp, folder), "排行榜")
    with zipfile.ZipFile(os.path.join(folder, a.comp + ".zip")) as z:
        name = z.namelist()[0]
        rows = list(csv.DictReader(io.TextIOWrapper(z.open(name), encoding="utf-8-sig")))
    rows.sort(key=lambda r: int(r["Rank"]))
    n = len(rows)
    stamp = re.search(r"\d{4}-\d\d-\d\dT\d\d.\d\d.\d\d", name)
    print(f"排行榜时间 {stamp.group(0).replace('T', ' ') if stamp else name} UTC，共 {n} 队")
    ours = next((r for r in rows if int(r["TeamId"]) == a.team), None)
    mine = float(ours["Score"]) if ours else None
    out = [[f"我们（{ours['TeamName']}）", ours["Rank"], ours["Score"], ""] if ours else ["我们", "不在榜上", "", ""]]
    # Kaggle medals for 1000+ teams: gold top 10 plus one per 500 teams, silver top 5%, bronze top 10%
    for medal, cut in (("金牌线", 10 + n // 500), ("银牌线", n // 20), ("铜牌线", n // 10)):
        score = float(rows[cut - 1]["Score"])
        out.append([medal, cut, f"{score:.1f}", "" if mine is None else f"{mine - score:+.1f}"])
    table(["", "名次", "分数", "我们-线"], out)


def cmd_subs(a):
    k = api()
    subs = retry(lambda: k.competition_submissions(a.comp, page_size=200), "提交列表") or []
    live = {s.id for s in retry(lambda: k.competition_team_submissions(a.team), "在跑的提交") or []}
    rows = [[s.ref, s.date.strftime("%m-%d %H:%M") if s.date else "", s.submitted_by, str(s.status).split(".")[-1],
             s.public_score, "是" if s.ref in live else "", s.description] for s in subs]
    table(["id", "时间(UTC)", "提交人", "状态", "分数", "在跑", "说明"], rows)


def cmd_episodes(a):
    folder = os.path.join(DATA, "episodes")
    os.makedirs(folder, exist_ok=True)
    for i, sid in enumerate(a.submission_ids):
        if i:
            print()
        data = web("POST", LIST_EPISODES_URL, a.gap, json={"submissionId": sid}).json()
        path = os.path.join(folder, f"{sid}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        summarize(sid, data, a.last, os.path.relpath(path, ROOT))


def summarize(sid, data, last, path):
    names = {t["id"]: t.get("teamName", "") for t in data.get("teams") or []}
    games = []
    for e in data.get("episodes") or []:
        # skip the self-play validation game that runs right after upload
        if e.get("state") != "COMPLETED" or e.get("type") != "EPISODE_TYPE_PUBLIC":
            continue
        agents = e.get("agents") or []
        me = next((g for g in agents if g.get("submissionId") == sid), None)
        opp = [g for g in agents if g is not me]
        if me is None or not opp:
            continue
        # the endpoint omits zero-valued fields, so a missing reward means 0
        margin = (me.get("reward") or 0.0) - max(g.get("reward") or 0.0 for g in opp)
        games.append({"id": e["id"], "t": e.get("endTime") or "",
                      "result": "胜" if margin > 0 else "负" if margin < 0 else "平", "margin": margin,
                      "score": me.get("updatedScore"), "opp": opp[0].get("initialScore"),
                      "team": names.get(opp[0].get("teamId"), "")})
    games.sort(key=lambda g: g["t"])
    for g in games:
        g["end"] = g["t"][5:16].replace("T", " ")
    print(f"提交 {sid}：正式对局 {len(games)} 局（原始数据 {path}）")
    if not games:
        return
    n = len(games)
    w, l, d = (sum(g["result"] == x for g in games) for x in "胜负平")
    opp = [g["opp"] for g in games if g["opp"] is not None]
    table(["胜", "负", "平", "得分率", "对手分数中位数", "当前分数"],
          [[w, l, d, f"{(w + 0.5 * d) / n:.0%}", f"{statistics.median(opp):.1f}" if opp else "",
            f"{games[-1]['score']:.1f}"]])
    print()
    print("分数走势")
    picks = sorted({round(i * (n - 1) / 9) for i in range(10)})
    table(["时间(UTC)", "第几局", "分数"], [[games[i]["end"], i + 1, f"{games[i]['score']:.1f}"] for i in picks])
    if last:
        print()
        print(f"最近 {min(last, n)} 局")
        table(["episode", "时间(UTC)", "结果", "钱差", "对手分数", "对手"],
              [[g["id"], g["end"], g["result"], f"{g['margin']:+.0f}", f"{g['opp']:.1f}" if g["opp"] else "", g["team"]]
               for g in games[-last:][::-1]])


def cmd_replay(a):
    out = os.path.abspath(a.out)
    folder = os.path.dirname(out)
    os.makedirs(folder, exist_ok=True)
    source = None
    if not a.public:
        try:
            k = api()
            retry(lambda: k.competition_episode_replay(a.episode_id, path=folder, quiet=True), "官方回放")
            os.replace(os.path.join(folder, f"episode-{a.episode_id}-replay.json"), out)
            source = "官方 API"
        except (Exception, SystemExit) as e:
            print(f"官方 API 没拿到回放（{e}），改用公开地址", file=sys.stderr)
    if source is None:
        r = web("GET", PUBLIC_REPLAY_URL.format(a.episode_id), a.gap, stream=True)
        with open(out + ".part", "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
        os.replace(out + ".part", out)
        source = "公开地址"
    with open(out, encoding="utf-8") as f:
        d = json.load(f)
    info = d.get("info") or {}
    table(["项目", "内容"], [
        ["文件", out],
        ["大小", f"{os.path.getsize(out) / 1e6:.1f} MB"],
        ["来源", source],
        ["seed", info.get("seed")],
        ["步数", len(d.get("steps") or [])],
        ["队伍", " / ".join(info.get("TeamNames") or [])],
        ["得分", " / ".join("-" if x is None else f"{x:.0f}" for x in d.get("rewards") or [])],
        ["状态", " / ".join(str(x) for x in d.get("statuses") or [])],
    ])


def cmd_fetch(a):
    from kagglesdk.competitions.types.competition_api_service import ApiDownloadSubmissionRequest
    k = api()
    subs = {s.ref: s for s in retry(lambda: k.competition_submissions(a.comp, page_size=200), "提交列表") or []}
    rows = []
    for sid in a.submission_ids:
        s = subs.get(sid)
        if s is None:
            rows.append([sid, "不是我们队的提交", "", "", "", ""])
            continue
        out = os.path.join(DATA, "uploads", str(sid), s.file_name or "submission")

        def call():
            with k.build_kaggle_client() as kc:
                req = ApiDownloadSubmissionRequest()
                req.submission_id = sid
                resp = kc.competitions.competition_api_client.download_submission(req)
                k.download_file(resp, out, kc.http_client(), True)

        retry(call, f"提交 {sid}")
        with open(out, "rb") as f:
            raw = f.read()
        rows.append([sid, os.path.relpath(out, ROOT), len(raw), "对" if len(raw) == s.total_bytes else f"应为 {s.total_bytes}",
                     hashlib.sha256(raw).hexdigest()[:8], s.description or ""])
    table(["id", "文件", "字节", "大小核对", "sha256", "说明"], rows)


def main():
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(errors="replace")
    p = argparse.ArgumentParser(description="Kaggriculture 查询：排行榜、提交、对局、回放")
    p.add_argument("--comp", default=COMP)
    p.add_argument("--team", type=int, default=TEAM_ID)
    p.add_argument("--gap", type=float, default=6.0, help="网页请求之间至少隔几秒（默认 6）")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("lb", help="我们队的名次、分数和金银铜牌线")
    sub.add_parser("subs", help="我们队的提交列表")
    e = sub.add_parser("episodes", help="提交的胜负平、对手分数中位数、分数走势")
    e.add_argument("submission_ids", type=int, nargs="+")
    e.add_argument("--last", type=int, default=0, help="再列出最近 N 局")
    r = sub.add_parser("replay", help="下载一局的回放")
    r.add_argument("episode_id", type=int)
    r.add_argument("out")
    r.add_argument("--public", action="store_true", help="直接用公开地址，不走官方 API")
    f = sub.add_parser("fetch", help="下载我们队自己的提交文件到 data/uploads/<id>/")
    f.add_argument("submission_ids", type=int, nargs="+")
    a = p.parse_args()
    {"lb": cmd_lb, "subs": cmd_subs, "episodes": cmd_episodes, "replay": cmd_replay, "fetch": cmd_fetch}[a.cmd](a)


if __name__ == "__main__":
    main()
