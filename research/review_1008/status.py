"""Freeze own final agents' public games and leaderboard for the October 8 review."""
import csv
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import shutil
import statistics
import sys
from zoneinfo import ZoneInfo
import zipfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
NY = ZoneInfo("America/New_York")
sys.path.insert(0, str(ROOT / "tools"))
import kg


def stats(games):
    return {"n": len(games), "wins": sum(g["margin"] > 0 for g in games),
            "losses": sum(g["margin"] < 0 for g in games), "ties": sum(g["margin"] == 0 for g in games),
            "mean_opponent_initial_score": round(statistics.mean(g["opponent_score"] for g in games), 1) if games else None}


def main():
    api = kg.api()
    active = sorted(s.id for s in api.competition_team_submissions(16908623))
    official = api.competition_submissions("kaggriculture", page_size=200)
    selected = [s for s in official if s.ref in active]
    result = {"checked_utc": datetime.now(timezone.utc).isoformat(), "active_submission_ids": active,
              "official_submissions": [{"id": s.ref, "status": str(s.status).split(".")[-1],
                                        "public_score": s.public_score} for s in selected], "agents": {}}
    frozen = HERE / "leaderboard_1008_0658.zip"
    if not frozen.exists():
        shutil.copy2(ROOT / "data/lb/kaggriculture.zip", frozen)
    with zipfile.ZipFile(frozen) as archive:
        name, = archive.namelist()
        rows = sorted(csv.DictReader(io.StringIO(archive.read(name).decode("utf-8-sig"))), key=lambda r: int(r["Rank"]))
    time_utc = datetime.strptime(name[len("kaggriculture-publicleaderboard-"):-4], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    own = next(r for r in rows if r["TeamId"] == "16908623")
    cuts = {}
    for label, rank in (("gold", 10 + len(rows) // 500), ("silver", len(rows) // 20), ("bronze", len(rows) // 10)):
        line = rows[rank - 1]
        cuts[label] = {"rank": rank, "score": float(line["Score"]),
                       "buffer_score": round(float(own["Score"]) - float(line["Score"]), 1),
                       "buffer_rank": rank - int(own["Rank"])}
    result["leaderboard"] = {"filename": name, "time_utc": time_utc.isoformat(),
                             "time_ny": time_utc.astimezone(NY).isoformat(), "teams": len(rows),
                             "rank": int(own["Rank"]), "score": float(own["Score"]), "cuts": cuts}
    for sid in (56649860, 56713491):
        source = ROOT / f"data/episodes/{sid}.json"
        shutil.copy2(source, HERE / f"episodes_{sid}.json")
        data = json.loads(source.read_text())
        teams = {t["id"]: t.get("teamName") for t in data["teams"]}
        games = []
        for e in data["episodes"]:
            if e.get("state") != "COMPLETED" or e.get("type") != "EPISODE_TYPE_PUBLIC":
                continue
            agents = e.get("agents") or []
            me = next((g for g in agents if g.get("submissionId") == sid), None)
            if me is None or len(agents) != 2:
                continue
            op = next(g for g in agents if g is not me)
            when = datetime.fromisoformat(e["endTime"].replace("Z", "+00:00"))
            games.append({"id": e["id"], "end_utc": when.isoformat(), "end_ny": when.astimezone(NY).isoformat(),
                          "day_ny": when.astimezone(NY).date().isoformat(),
                          "margin": (me.get("reward") or 0) - (op.get("reward") or 0),
                          "score": me.get("updatedScore"), "opponent_score": op.get("initialScore") or 600,
                          "opponent_team": teams.get(op.get("teamId")), "opponent_submission": op.get("submissionId")})
        games.sort(key=lambda g: g["end_utc"])
        dates = sorted({g["day_ny"] for g in games})
        daily = []
        for date in dates:
            subset = [g for g in games if g["day_ny"] == date]
            daily.append({"date_ny": date, **stats(subset), "last_score": round(subset[-1]["score"], 1)})
        recent = games[-100:]
        bands = []
        for low, high in ((0, 2000), (2000, 2057), (2057, 2100), (2100, float("inf"))):
            subset = [g for g in recent if low <= g["opponent_score"] < high]
            bands.append({"opponent_score_band": [low, high if high != float("inf") else None], **stats(subset)})
        result["agents"][str(sid)] = {"all": stats(games), "last30": stats(games[-30:]), "last50": stats(games[-50:]),
                                     "last100": stats(recent), "daily": daily,
                                     "postdeadline": stats([g for g in games if g["end_utc"] >= "2026-10-01T00:00:00"]),
                                     "latest": games[-1], "last100_opponent_score_bands": bands}
    previous = json.loads((ROOT / "research/forecast_1001/summary.json").read_text())["current"]
    then = datetime.fromisoformat(previous["time_utc"]).replace(tzinfo=timezone.utc)
    elapsed = (time_utc - then).total_seconds() / 86400
    delta = cuts["silver"]["buffer_score"] - previous["cuts"]["silver"]["buffer"]
    result["since_oct1"] = {"previous_time_utc": then.isoformat(), "elapsed_days": round(elapsed, 4),
                            "rank_change": int(own["Rank"]) - previous["rank"],
                            "own_score_change": round(float(own["Score"]) - previous["score"], 1),
                            "silver_line_change": round(cuts["silver"]["score"] - previous["cuts"]["silver"]["score"], 1),
                            "silver_buffer_change": round(delta, 1), "silver_buffer_shrink_per_day": round(-delta / elapsed, 2),
                            "silver_days_to_zero_if_full_week_rate_continues": round(cuts["silver"]["buffer_score"] / (-delta / elapsed), 2)}
    result["remaining_week_sensitivity"] = {"horizon_days_assumed": 7,
                                           "silver_max_average_daily_shrink": round(cuts["silver"]["buffer_score"] / 7, 2),
                                           "silver_buffer_after7_if_daily_shrink": [{"daily_shrink": rate, "buffer": round(cuts["silver"]["buffer_score"] - 7 * rate, 1)} for rate in (0, 1, 2, 5)]}
    result["limits"] = ["No continuous leaderboard snapshots from Oct2-7; cannot infer the silver margin trend in the last two days.",
                        "Current ratings and current medal cutoffs are provisional, not the final Bradley-Terry ranking.",
                        "Opponent score bands use their score at game time, not a fixed current strength.",
                        "No calibrated medal probability; linear margin scenarios are conditional, not predictions.",
                        "Team count is 98 lower than Oct1; cause unknown, no disqualification claim."]
    (HERE / "status_summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"leaderboard": result["leaderboard"], "since_oct1": result["since_oct1"],
                      "official_submissions": result["official_submissions"],
                      "agents": {sid: {key: value for key, value in a.items() if key not in ("daily", "last100_opponent_score_bands")} for sid, a in result["agents"].items()}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
