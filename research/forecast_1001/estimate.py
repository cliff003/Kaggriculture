"""Conditional 14-day medal-margin scenarios, not a calibrated final BT forecast."""
import csv
import io
import json
import shutil
from datetime import datetime
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def main():
    frozen = HERE / "leaderboard_1001_1502.zip"
    if not frozen.exists():
        shutil.copy2(ROOT / "data/lb/kaggriculture.zip", frozen)
    with zipfile.ZipFile(frozen) as archive:
        name, = archive.namelist()
        rows = sorted(csv.DictReader(io.StringIO(archive.read(name).decode("utf-8-sig"))), key=lambda r: int(r["Rank"]))
    now = datetime.strptime(name[len("kaggriculture-publicleaderboard-"):-4], "%Y-%m-%dT%H:%M:%S")
    ours = next(r for r in rows if r["TeamId"] == "16908623")
    cuts = {}
    for label, rank in (("silver", len(rows) // 20), ("bronze", len(rows) // 10)):
        cuts[label] = {"rank": rank, "score": float(rows[rank - 1]["Score"]),
                       "buffer": round(float(ours["Score"]) - float(rows[rank - 1]["Score"]), 1)}
    current = {"time_utc": now.isoformat(), "rank": int(ours["Rank"]), "score": float(ours["Score"]), "cuts": cuts}
    anchors = [
        {"time_utc": "2026-09-29T12:00:53", "silver_buffer": 215.7, "source": "results/live_0929_review.md"},
        {"time_utc": "2026-09-30T15:49:40", "silver_buffer": 111.7, "source": "results/agent_rescue_0930.md"},
        {"time_utc": "2026-10-01T04:38:45", "silver_buffer": 82.1, "bronze_buffer": 324.3, "source": "results/final_medal_status_1001.md"},
        {"time_utc": "2026-10-01T10:52:58", "silver_buffer": 78.4, "bronze_buffer": 313.1, "source": "results/postdeadline_review_1001.md"},
        {"time_utc": "2026-10-01T14:37:00", "silver_buffer": 78.5, "bronze_buffer": 309.1, "source": "results/rank_change_1001.md"},
    ]
    windows = []
    for anchor in anchors:
        days = (now - datetime.fromisoformat(anchor["time_utc"])).total_seconds() / 86400
        change = cuts["silver"]["buffer"] - anchor["silver_buffer"]
        shrink = -change / days
        window = {"start_utc": anchor["time_utc"], "hours": round(days * 24, 4),
                  "silver_change": round(change, 1), "silver_shrink_per_day": round(shrink, 4),
                  "silver_buffer_if_same_rate_14_days": round(cuts["silver"]["buffer"] - shrink * 14, 1),
                  "silver_days_to_zero_if_same_rate": round(cuts["silver"]["buffer"] / shrink, 2) if shrink > 0 else None}
        if "bronze_buffer" in anchor:
            bs = (anchor["bronze_buffer"] - cuts["bronze"]["buffer"]) / days
            window.update(bronze_shrink_per_day=round(bs, 4),
                          bronze_buffer_if_same_rate_14_days=round(cuts["bronze"]["buffer"] - bs * 14, 1),
                          bronze_days_to_zero_if_same_rate=round(cuts["bronze"]["buffer"] / bs, 2) if bs > 0 else None)
            crossing = ((cuts["bronze"]["buffer"] - cuts["silver"]["buffer"]) / (bs - shrink)) if bs > shrink else None
            window["cutoff_order_violated_after_days_if_both_rates_fixed"] = round(crossing, 2) if crossing is not None else None
            window["joint_linear_projection_valid_for14days"] = crossing is None or crossing >= 14
        windows.append(window)
    scenarios = [{"silver_shrink_per_day": rate,
                  "silver_buffer_after14": round(cuts["silver"]["buffer"] - 14 * rate, 1),
                  "days_to_silver_line": round(cuts["silver"]["buffer"] / rate, 2) if rate else None}
                 for rate in (0, 3, 6, 8, 12)]
    agents = {}
    for sid in (56649860, 56713491):
        source = ROOT / f"data/episodes/{sid}.json"
        shutil.copy2(source, HERE / f"episodes_{sid}.json")
        data = json.loads(source.read_text())
        games = []
        for e in data["episodes"]:
            if e.get("state") != "COMPLETED" or e.get("type") != "EPISODE_TYPE_PUBLIC":
                continue
            me = next((g for g in e.get("agents", []) if g.get("submissionId") == sid), None)
            if me is None or len(e["agents"]) != 2:
                continue
            op = next(g for g in e["agents"] if g is not me)
            games.append({"end_utc": e["endTime"], "margin": (me.get("reward") or 0) - (op.get("reward") or 0)})
        games.sort(key=lambda g: g["end_utc"])
        def stats(gs):
            return {"n": len(gs), "wins": sum(g["margin"] > 0 for g in gs), "losses": sum(g["margin"] < 0 for g in gs)}
        agents[str(sid)] = {"last30": stats(games[-30:]),
                            "postdeadline": stats([g for g in games if g["end_utc"] >= "2026-10-01T00:00:00"]),
                            "last_game_utc": games[-1]["end_utc"]}
    summary = {"current": current, "anchors": anchors, "windows": windows, "silver_scenarios": scenarios,
               "max_average_daily_shrink_to_remain_above_line_14days": {label: round(cuts[label]["buffer"] / 14, 4) for label in cuts},
               "agents": agents,
               "limits": ["Linear sensitivity scenarios are not fitted or calibrated outcome probabilities.",
                          "Predeadline pool changes and score convergence invalidate a stationary slope assumption.",
                          "Final Bradley-Terry ranking is different from extrapolated ladder rating.",
                          "Joint silver/bronze linear trends can reverse the required cutoff ordering and become impossible.",
                          "Recent best-team margin can change when the better active submission changes.",
                          "Recent short-term stability does not establish a final plateau."]}
    (HERE / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: value for key, value in summary.items() if key not in ("anchors", "limits")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
