"""Compare saved public leaderboard snapshots; no network calls or private code."""
import csv
import io
import json
import shutil
import statistics
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
OWN_ID = "16908623"
OLD_PATH = ROOT / "data/lb/kaggriculture-publicleaderboard-2026-09-27T02_37_59.csv"


def rows_from_text(text):
    rows = list(csv.DictReader(io.StringIO(text.lstrip("\ufeff"))))
    for row in rows:
        row["Rank"] = int(row["Rank"])
        row["Score"] = float(row["Score"])
    return rows


def selected(row):
    return {key: row[key] for key in ("TeamId", "TeamName", "Rank", "Score", "LastSubmissionDate")}


def main():
    frozen = OUT / "leaderboard_1001_1437.zip"
    if not frozen.exists():
        shutil.copy2(ROOT / "data/lb/kaggriculture.zip", frozen)
    with zipfile.ZipFile(frozen) as archive:
        name, = archive.namelist()
        current = rows_from_text(archive.read(name).decode("utf-8-sig"))
    old = rows_from_text(OLD_PATH.read_text(encoding="utf-8-sig"))
    old_by_id = {row["TeamId"]: row for row in old}
    current_by_id = {row["TeamId"]: row for row in current}
    own = current_by_id[OWN_ID]
    old_own = old_by_id[OWN_ID]
    cuts = {}
    for label, rank in (("gold", 30), ("silver", len(current) // 20), ("bronze", len(current) // 10)):
        line = next(row for row in current if row["Rank"] == rank)
        cuts[label] = {"rank": rank, "score": line["Score"],
                       "score_buffer": round(own["Score"] - line["Score"], 1),
                       "rank_buffer": rank - own["Rank"]}
    # Sept 29 full leaderboard was not retained. These three values are the
    # contemporaneous saved own-team/cut snapshot in results/live_0929_review.md.
    sep29 = {"time_utc": "2026-09-29 12:00:53", "rank": 200,
             "teams": 10157, "score": 2422.4, "silver_score": 2206.7,
             "silver_buffer": 215.7, "source": "results/live_0929_review.md"}
    crossers = [row for row in current if row["Rank"] < own["Rank"] and
                (row["TeamId"] not in old_by_id or old_by_id[row["TeamId"]]["Rank"] > old_own["Rank"])]
    matched = [row for row in crossers if row["TeamId"] in old_by_id]
    deltas = [row["Score"] - old_by_id[row["TeamId"]]["Score"] for row in matched]
    recent_ids = ("16622349", "16730334", "16727266", "16630729", OWN_ID)
    recent = [{"old": selected(old_by_id[team_id]), "current": selected(current_by_id[team_id])}
              for team_id in recent_ids]
    # Illustrative selections, not a random sample or evidence of source origin.
    examples = []
    for team_name in ("Farmcore", "Gemini IS ALL YOU NEED"):
        row = next((r for r in current if r["TeamName"].replace(" ", "").lower() == team_name.replace(" ", "").lower()), None)
        if row is not None and row["TeamId"] in old_by_id:
            examples.append({"old": selected(old_by_id[row["TeamId"]]), "current": selected(row)})
    summary = {
        "current_file": name, "current_teams": len(current), "current_own": selected(own), "cuts": cuts,
        "sep29_saved_own_snapshot": sep29,
        "sep29_changes": {"rank": own["Rank"] - sep29["rank"],
                          "score": round(own["Score"] - sep29["score"], 1),
                          "silver_score": round(cuts["silver"]["score"] - sep29["silver_score"], 1),
                          "silver_buffer": round(cuts["silver"]["score_buffer"] - sep29["silver_buffer"], 1)},
        "fixed_numeric_score_2422_4_rank_on_current_board": 1 + sum(row["TeamId"] != OWN_ID and row["Score"] > sep29["score"] for row in current),
        "other_teams_between_current_score_and_2422_4": sum(row["TeamId"] != OWN_ID and own["Score"] < row["Score"] <= sep29["score"] for row in current),
        "sep27_old_own": selected(old_own),
        "sep27_crossers": {"count": len(crossers), "absent_in_old": len(crossers) - len(matched),
                           "matched_score_increased": sum(delta > 0 for delta in deltas),
                           "matched_score_same_or_fell": sum(delta <= 0 for delta in deltas),
                           "matched_median_score_change": round(statistics.median(deltas), 1),
                           "matched_last_submission_changed": sum(row["LastSubmissionDate"] != old_by_id[row["TeamId"]]["LastSubmissionDate"] for row in matched)},
        "recent_rivals": recent, "large_gain_examples": examples,
        "limits": ["No full September 29 leaderboard: cannot identify its exact 221 overtakers.",
                   "Our September 27 active versions differ from current versions.",
                   "Rating movement is not a controlled code comparison; private R&D and code origin unknown.",
                   "Fixed numeric score placement describes leaderboard density, not a prediction."]}
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
