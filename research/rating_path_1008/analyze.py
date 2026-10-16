"""Read frozen episode metadata; summarize observed rating updates without fitting a formula."""
import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = Path(__file__).resolve().parents[2]
SOURCE = BASE / "research/review_1008"
OUT = Path(__file__).parent
NY = ZoneInfo("America/New_York")
CUT = datetime(2026, 9, 30, 23, 59, tzinfo=timezone.utc)


def time(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def numeric_summary(values):
    if not values:
        return {}
    return {
        "n": len(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0,
    }


def group_stats(rows):
    return {
        "n": len(rows),
        "wins": sum(r["outcome"] == "W" for r in rows),
        "losses": sum(r["outcome"] == "L" for r in rows),
        "ties": sum(r["outcome"] == "T" for r in rows),
        "delta_sum": sum(r["delta"] for r in rows),
        "initial_first": rows[0]["initial"] if rows else None,
        "updated_last": rows[-1]["updated"] if rows else None,
        "opponent_initial": numeric_summary([r["opponent_initial"] for r in rows]),
        "opponent_minus_own_initial": numeric_summary([r["opponent_initial"] - r["initial"] for r in rows]),
        "reward_margin": numeric_summary([r["margin"] for r in rows]),
        "win_delta": numeric_summary([r["delta"] for r in rows if r["outcome"] == "W"]),
        "loss_delta": numeric_summary([r["delta"] for r in rows if r["outcome"] == "L"]),
        "distinct_opponent_submissions": len({r["opponent_submission"] for r in rows}),
    }


def analyze(sub):
    data = json.loads((SOURCE / f"episodes_{sub}.json").read_text())
    rows = []
    scored_rows = []
    rejected = Counter()
    excluded_public = []
    for e in data["episodes"]:
        if e.get("type") != "EPISODE_TYPE_PUBLIC":
            rejected["nonpublic"] += 1
            continue
        if e["state"] != "COMPLETED":
            rejected[e["state"]] += 1
            excluded_public.append({"id": e["id"], "state": e["state"], "createTime": e.get("createTime"), "endTime": e.get("endTime"), "agents": e["agents"]})
        own = next(a for a in e["agents"] if a["submissionId"] == sub)
        opponent = next(a for a in e["agents"] if a["id"] != own["id"])
        if "initialScore" not in own or "updatedScore" not in own or "reward" not in own or "reward" not in opponent:
            rejected["incomplete_fields"] += 1
            continue
        margin = own["reward"] - opponent["reward"]
        row = {
            "id": e["id"], "createTime": e["createTime"], "endTime": e["endTime"],
            "day_ny": time(e["endTime"]).astimezone(NY).date().isoformat(),
            "initial": own["initialScore"], "updated": own["updatedScore"],
            "delta": own["updatedScore"] - own["initialScore"],
            "opponent_submission": opponent["submissionId"], "opponent_team": opponent["teamId"],
            "opponent_initial": opponent.get("initialScore"),
            "seat": own.get("index", 0), "margin": margin,
            "outcome": "W" if margin > 0 else "L" if margin < 0 else "T", "state": e["state"],
        }
        scored_rows.append(row)
        if e["state"] == "COMPLETED":
            rows.append(row)
    rows.sort(key=lambda r: time(r["endTime"]))
    scored_rows.sort(key=lambda r: time(r["endTime"]))
    chain_gaps = []
    for previous, current in zip(rows, rows[1:]):
        if abs(previous["updated"] - current["initial"]) > 1e-7:
            chain_gaps.append({"previous": previous["id"], "current": current["id"], "difference": current["initial"] - previous["updated"]})
    duplicate_initials = Counter(r["initial"] for r in rows)
    post = [r for r in rows if time(r["endTime"]) >= CUT]
    scored_post = [r for r in scored_rows if time(r["endTime"]) >= CUT]
    scored_chain_gaps = []
    for previous, current in zip(scored_rows, scored_rows[1:]):
        if abs(previous["updated"] - current["initial"]) > 1e-7:
            scored_chain_gaps.append({"previous": previous["id"], "current": current["id"], "difference": current["initial"] - previous["updated"]})
    days = defaultdict(list)
    bands = defaultdict(list)
    relative = defaultdict(list)
    seats = defaultdict(list)
    for r in post:
        days[r["day_ny"]].append(r)
        lo = int(r["opponent_initial"] // 100) * 100
        bands[f"{lo}-{lo + 100}"].append(r)
        gap = r["opponent_initial"] - r["initial"]
        name = "opp_below_by_50plus" if gap < -50 else "within_50" if gap <= 50 else "opp_above_by_50plus"
        relative[name].append(r)
        seats[r["seat"]].append(r)
    predecessor = [r for r in rows if time(r["endTime"]) < CUT][-1]
    result = {
        "submission": sub,
        "cutoff_utc": CUT.isoformat(),
        "data_last_ny": time(rows[-1]["endTime"]).astimezone(NY).isoformat(),
        "excluded_counts": dict(rejected), "excluded_public": excluded_public,
        "all_formal": group_stats(rows), "post_cutoff": group_stats(post),
        "last_before_cutoff": predecessor,
        "daily_ny": {day: {**group_stats(group), "actual_endpoint_change": group[-1]["updated"] - group[0]["initial"], "endpoint_minus_completed_delta_sum": group[-1]["updated"] - group[0]["initial"] - sum(r["delta"] for r in group)} for day, group in sorted(days.items())},
        "opponent_score_bands": {band: group_stats(group) for band, group in sorted(bands.items())},
        "relative_opponent_bands": {band: group_stats(group) for band, group in relative.items()},
        "seats": {str(seat): group_stats(group) for seat, group in seats.items()},
        "rating_chain_gaps": chain_gaps,
        "duplicated_initial_ratings": {str(k): v for k, v in duplicate_initials.items() if v > 1},
        "post_cutoff_delta_vs_endpoints_difference": sum(r["delta"] for r in post) - (post[-1]["updated"] - post[0]["initial"]),
        "post_cutoff_rows": post,
        "post_cutoff_all_scored_states": group_stats(scored_post),
        "all_scored_states_chain_gaps": scored_chain_gaps,
        "all_scored_states_delta_vs_endpoints_difference": sum(r["delta"] for r in scored_post) - (scored_post[-1]["updated"] - scored_post[0]["initial"]),
        "scored_noncompleted_rows": [r for r in scored_rows if r["state"] != "COMPLETED"],
    }
    return result


def main():
    results = {str(sub): analyze(sub) for sub in (56649860, 56713491)}
    overlap = set(r["opponent_submission"] for r in results["56649860"]["post_cutoff_rows"]) & set(r["opponent_submission"] for r in results["56713491"]["post_cutoff_rows"])
    comparison = {}
    for sub, data in results.items():
        common = [r for r in data["post_cutoff_rows"] if r["opponent_submission"] in overlap]
        not_oct6 = [r for r in data["post_cutoff_rows"] if r["day_ny"] != "2026-10-06"]
        comparison[sub] = {"shared_opponents_rows": group_stats(common), "without_oct6": group_stats(not_oct6)}
    all_rows = {sub: data.pop("post_cutoff_rows") for sub, data in results.items()}
    (OUT / "rating_rows_local.json").write_text(json.dumps(all_rows, ensure_ascii=False, indent=2) + "\n")
    notes = ["All deltas are observed updatedScore minus initialScore, no assumed Elo formula.", "Opponent versions, world seeds and game times differ; aggregate correlations do not establish patch causality.", "NY calendar days are grouped by episode endTime.", "One ERRORED episode for the new version has a scored win; it is included in all-scored-state totals but excluded from completed-state win rates.", "Two simultaneous episodes can expose the same initial score with distinct updated scores; summing individual deltas then differs from the actual endpoint change."]
    output = {"notes": notes, "results": results, "common_opponent_submission_count": len(overlap), "comparison": comparison}
    (OUT / "details_local.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")

    def compact_group(group):
        return {key: group[key] for key in ("n", "wins", "losses", "ties", "delta_sum", "initial_first", "updated_last", "distinct_opponent_submissions")} | {
            "opponent_initial_mean": group["opponent_initial"]["mean"],
            "opponent_minus_own_initial_mean": group["opponent_minus_own_initial"]["mean"],
        }

    compact_results = {}
    for sub, data in results.items():
        fork_cases = []
        rows = all_rows[sub]
        for gap in data["all_scored_states_chain_gaps"]:
            position = next(i for i, row in enumerate(rows) if row["id"] == gap["current"])
            fork_cases.append({"chain_difference": gap["difference"], "rows": [{key: row[key] for key in ("id", "endTime", "initial", "updated", "delta", "outcome")} for row in rows[position - 1: position + 2]]})
        compact_results[sub] = {
            "cutoff_utc": data["cutoff_utc"], "data_last_ny": data["data_last_ny"],
            "post_cutoff_completed": compact_group(data["post_cutoff"]),
            "post_cutoff_all_scored_states": compact_group(data["post_cutoff_all_scored_states"]),
            "daily_ny": {day: compact_group(group) | {key: group[key] for key in ("actual_endpoint_change", "endpoint_minus_completed_delta_sum")} | {"win_delta_mean": group["win_delta"]["mean"], "loss_delta_mean": group["loss_delta"]["mean"]} for day, group in data["daily_ny"].items()},
            "opponent_score_bands": {band: compact_group(group) for band, group in data["opponent_score_bands"].items()},
            "relative_opponent_bands": {band: compact_group(group) for band, group in data["relative_opponent_bands"].items()},
            "shared_opponent_submissions_rows": compact_group(comparison[sub]["shared_opponents_rows"]),
            "scored_noncompleted_rows": [{key: row[key] for key in ("id", "endTime", "initial", "updated", "delta", "outcome", "state")} for row in data["scored_noncompleted_rows"]],
            "rating_metadata_fork_cases": fork_cases,
        }
    compact_output = {"notes": notes, "common_opponent_submission_count": len(overlap), "results": compact_results}
    (OUT / "summary.json").write_text(json.dumps(compact_output, ensure_ascii=False, indent=2) + "\n")
    for sub, data in results.items():
        post = data["post_cutoff"]
        print(sub, "completed", post["n"], post["wins"], post["losses"], "end", round(post["updated_last"], 3), "opponent_mean", round(post["opponent_initial"]["mean"], 3))
        print("all scored chain gaps", data["all_scored_states_chain_gaps"])
        for day, group in data["daily_ny"].items():
            print(day, group["n"], group["wins"], group["losses"], round(group["delta_sum"], 3), round(group["initial_first"], 3), round(group["updated_last"], 3), "opp", round(group["opponent_initial"]["mean"], 2), "relative", round(group["opponent_minus_own_initial"]["mean"], 2))
        common = comparison[sub]["shared_opponents_rows"]
        print("shared opponent submissions", common["distinct_opponent_submissions"], "rows", common["n"], "wins", common["wins"], "losses", common["losses"])


if __name__ == "__main__":
    main()
