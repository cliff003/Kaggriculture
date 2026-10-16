"""Summarize paired notebook screens against the frozen v12_19, without uploading."""
from collections import defaultdict
import ast
import hashlib
import json
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LATE = ROOT / "research/notebook_1001_0144"
BASE = ROOT / "submissions/v12_19_own_cha22_adaptive_inputs/main.py"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_results(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def compare(rows, baseline):
    by_path = defaultdict(dict)
    for row in rows:
        assert row["status"] == ["DONE", "DONE"] and not any(row["errors"])
        assert row["id"] not in by_path[row["path"]]
        by_path[row["path"]][row["id"]] = row
    out = []
    for name, games in by_path.items():
        assert set(games) == set(baseline)
        changes = [r["margin"] - baseline[i]["margin"] for i, r in games.items()]
        out.append({
            "path": str(Path(name).relative_to(ROOT)),
            "main_sha256": digest(Path(name)),
            "games": len(games),
            "wins": sum(r["margin"] > 0 for r in games.values()),
            "ties": sum(r["margin"] == 0 for r in games.values()),
            "flips_up_vs_v12_19": sum(baseline[i]["margin"] <= 0 < r["margin"] for i, r in games.items()),
            "flips_down_vs_v12_19": sum(r["margin"] <= 0 < baseline[i]["margin"] for i, r in games.items()),
            "mean_margin_delta_vs_v12_19": round(statistics.mean(changes), 2),
            "changed_games": sum(v != 0 for v in changes),
            "all_done": True,
            "agent_errors": 0,
        })
    return sorted(out, key=lambda r: r["path"])


def equal_code(first, second):
    assert first.read_bytes() == second.read_bytes()
    return {"first": str(first.relative_to(ROOT)), "second": str(second.relative_to(ROOT)), "main_sha256": digest(first)}


def function_tree(path, name):
    nodes = [n for n in ast.parse(path.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == name]
    assert len(nodes) == 1
    return ast.dump(nodes[0], include_attributes=False)


def main():
    assert digest(BASE) == "3b6a78997364b12f0cca080ff657c31acd1cd087bcfb5f8362e41da69a137f87"
    rows = read_results(HERE / "replay20.jsonl")
    baseline = {r["id"]: r for r in rows if Path(r["path"]) == BASE}
    assert len(baseline) == 20
    screening = compare(rows + read_results(LATE / "late20.jsonl"), baseline)
    settlement = compare(read_results(HERE / "settlement20.jsonl"), baseline)
    exact_matches = [
        equal_code(HERE / "outputs/haodou092__kaggriculture-harvest-ledger/main.py", ROOT / "research/panel/pub0928_ledger/main.py"),
        equal_code(HERE / "outputs/flexonafft__kaggriculture-multi-route-farming-agent/main.py", ROOT / "data/public/agents/ars_v43/main.py"),
        equal_code(HERE / "outputs/farhanabidtech786__kaggriculture-beginner-friendly/main.py", ROOT / "data/public/agents/reyhan_market/main.py"),
        equal_code(LATE / "leo_final/main.py", HERE / "extracted/leoprovorov__a-song-of-ice-and-fire-fixed-flexible/main.py"),
    ]
    shared_functions = []
    for folder in ["anhadmahajan06__kaggriculture-autonomous-ai-farming-agent", "evgendvorkin__kaggriculture-version-31-26-09-bronze-going-up"]:
        source = HERE / "outputs" / folder / "main.py"
        for name in ["e402_agent", "e410_agent"]:
            assert function_tree(source, name) == function_tree(ROOT / "research/rescue_0930/base_expanded.py", name)
        shared_functions.append({"public_main_sha256": digest(source), "functions": ["e402_agent", "e410_agent"], "already_in_our_base": True})
    latest = json.loads((HERE / "latest100.json").read_text())
    report = {
        "checked_utc": latest["checked_utc"],
        "metadata_meaning": "last run time, not first publication time or proof of a new policy",
        "latest_notebooks": latest["kernels"][:10],
        "screen": {"engine": "1.32.7", "source": "research/rescue_0930/latest20.jsonl.gz", "source_sha256": digest(ROOT / "research/rescue_0930/latest20.jsonl.gz"), "episode_ids": sorted(baseline), "forced_shops": True, "fixed_opponent_actions": True, "independent_holdout": False, "comparisons": screening},
        "isolated_settlement_port": {"comparisons": settlement, "decision": "rejected: no extra win and negative mean margin delta; no full panel, packaging or upload"},
        "byte_exact_matches": exact_matches,
        "already_present_functions": shared_functions,
        "anhad_late_change": {"sha256": digest(LATE / "anhad_latest/main.py"), "change": "step-91 wheat sale filter threshold 31 -> 15; telemetry threshold also changed", "notebook_markdown_claim_not_validation": True},
        "online_changes_this_review": False,
    }
    (HERE / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    for row in screening:
        print(json.dumps(row, ensure_ascii=False))
    print("SETTLEMENT", json.dumps(settlement, ensure_ascii=False))


if __name__ == "__main__":
    main()
