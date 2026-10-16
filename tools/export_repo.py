r"""Sync the shareable part of this project into github_repo/ (the team's GitHub repository).

.venv\Scripts\python.exe tools\export_repo.py [--repo github_repo] [--dry-run]

Copies, by a fixed list:
  * every package we ran on the live ladder (plus the sealed candidate) from its submission.tar.gz: main.py,
    LICENSE.txt and NOTICE.txt byte for byte, and the tar.gz itself;
  * our own scripts (tools, gold research code, engine, DSM analysis) and the experiment reports (*.md).
Never copies data/, replays, public third-party agents, Frank's own agent code, credentials or root-level notes.
README.md, docs/ and the repo's LICENSE/NOTICE are written by hand in the repo and are left alone.
Existing files are overwritten; files removed here are not deleted there (check `git status` in the repo).
"""
import argparse
import glob
import hashlib
import os
import shutil
import tarfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (source dir holding submission.tar.gz, folder name in the repo)
PACKAGES = [
    ("submissions/V10_CarreraGT", "V10_CarreraGT"),
    ("submissions/V12_AventadorSVJ", "V12_AventadorSVJ"),
    ("submissions/v12_17_own_cha22_sheep_cash_reserve", "v12_17_own_cha22_sheep_cash_reserve"),
    ("submissions/v12_18_own_cha22_cash_tomato_late", "v12_18_own_cha22_cash_tomato_late"),
    ("submissions/v12_19_own_cha22_adaptive_inputs", "v12_19_own_cha22_adaptive_inputs"),
    ("submissions/v3_own_rescue_slot", "v3_own_rescue_slot"),
    ("submissions/v4_own_cha22_slot", "v4_own_cha22_slot"),
    ("submissions/v6_own_cha22_eager_g90", "v6_own_cha22_eager_g90"),
    ("gold/candidates/b14_feed4", "v7_own_cha22_band_wheatlead"),
    ("submissions/v6b_own_cha22_eager_noceil", "v6b_own_cha22_eager_noceil"),
    ("submissions/v7b_own_cha22_eager_wheatlead", "v7b_own_cha22_eager_wheatlead"),
    ("submissions/v7c_own_cha22_eager_wheatlead_fixes", "v7c_own_cha22_eager_wheatlead_fixes"),
    ("submissions/v8_own_cha22_tick_guard10", "v8_own_cha22_tick_guard10"),
    ("submissions/v9_own_cha22_tick_trapguard", "v9_own_cha22_tick_trapguard"),
    ("submissions/v10_own_cha22_tick_trapguard_tomato", "v10_own_cha22_tick_trapguard_tomato"),
    ("submissions/v12_own_cha22_tick_fade_resume", "v12_own_cha22_tick_fade_resume"),
    ("submissions/v12_1_own_cha22_tick_fade_resume_late", "v12_1_own_cha22_tick_fade_resume_late"),
    ("submissions/v12_2_own_cha22_tick_fade_resume_late_sched", "v12_2_own_cha22_tick_fade_resume_late_sched"),
    ("submissions/v12_3_own_cha22_tick_fade_resume_late_sched_trap",
     "v12_3_own_cha22_tick_fade_resume_late_sched_trap"),
    ("submissions/v12_4_own_cha22_tick_fade_resume_late_sched_trap_tomato",
     "v12_4_own_cha22_tick_fade_resume_late_sched_trap_tomato"),
    ("submissions/v10_own_cha22_tick_trapguard_tomato",
     "v10_own_cha22_tick_trapguard_tomato"),
    ("submissions/v11_own_cha22_tick_trapguard_tomato_prebuy0",
     "v11_own_cha22_tick_trapguard_tomato_prebuy0"),
    ("submissions/v11_own_cha22_tick_trapguard_tomato_prebuy0_eod_rev",
     "v11_own_cha22_tick_trapguard_tomato_prebuy0_eod_rev"),
    ("submissions/v12_5_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard",
     "v12_5_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard"),
    ("submissions/v12_6_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade",
     "v12_6_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade"),
    ("submissions/v12_7_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0",
     "v12_7_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0"),
    ("submissions/v12_8_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod",
     "v12_8_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod"),
    ("submissions/v12_9_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n",
     "v12_9_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n"),
    ("submissions/v12_10_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_sq",
     "v12_10_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_sq"),
    ("submissions/v12_11_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind",
     "v12_11_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind"),
    ("submissions/v12_12_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room",
     "v12_12_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room"),
    ("submissions/v12_13_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room_cap",
     "v12_13_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room_cap"),
    ("submissions/v12_14_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room_cap40",
     "v12_14_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room_cap40"),
    ("submissions/v12_15_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room_cap40_x18g",
     "v12_15_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room_cap40_x18g"),
    ("submissions/v12_16_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room_cap40_x18g_strawx",
     "v12_16_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room_cap40_x18g_strawx"),
]

# glob patterns relative to ROOT; each match keeps its relative path in the repo
FILES = [
    "research/rating_path_1008/analyze.py",
    "research/rating_path_1008/summary.json",
    "research/rating_path_1008/findings.md",
    "research/v19_oct6_1008/audit.py",
    "research/v19_oct6_1008/summary_compact.json",
    "research/v19_oct6_1008/mechanisms.py",
    "research/v19_oct6_1008/mechanisms.json",
    "research/v19_recent_1008/audit.py",
    "research/v19_recent_1008/summary.json",
    "research/v19_review_1008/static_summary.json",
    "research/review_1008/status.py",
    "research/review_1008/status_summary.json",
    "research/notebook_1008/scan.py",
    "research/notebook_1008/pull_sources.py",
    "research/notebook_1008/summarize.py",
    "research/notebook_1008/summary.json",
    "research/forecast_1001/estimate.py",
    "research/forecast_1001/summary.json",
    "research/rank_change_1001/analyze.py",
    "research/rank_change_1001/summary.json",
    "research/opponent_provenance_1001/query.py",
    "research/opponent_provenance_1001/earlier_versions.py",
    "research/opponent_provenance_1001/pull_sources.py",
    "research/opponent_provenance_1001/source_summary.py",
    "research/opponent_provenance_1001/opponent_history_summary.json",
    "research/opponent_provenance_1001/earlier_versions_summary.json",
    "research/opponent_provenance_1001/source_summary.json",
    "research/postdeadline_1001_1049/scan.py",
    "research/postdeadline_1001_1049/status.py",
    "research/postdeadline_1001_1049/fetch.py",
    "research/postdeadline_1001_1049/audit.py",
    "research/postdeadline_1001_1049/summarize.py",
    "research/postdeadline_1001_1049/status_summary.json",
    "research/postdeadline_1001_1049/economic_summary.json",
    "research/postdeadline_1001_1049/latest100.json",
    "research/final_status_1001/episodes_summary.json",
    "research/notebook_0930_2032/scan.py",
    "research/notebook_0930_2032/pull.py",
    "research/notebook_0930_2032/output.py",
    "research/notebook_0930_2032/probe_settlement.py",
    "research/notebook_0930_2032/summarize.py",
    "research/notebook_0930_2032/summary.json",
    "research/rescue_0930/build_adaptive_input.py",
    "research/rescue_0930/replay_cached.py",
    "research/rescue_0930/summarize.py",
    "research/rescue_0930/package_adaptive.py",
    "research/rescue_0930/release_summary.json",
    "research/rescue_0930/package_manifest.json",
    "research/rescue_0930/status_v12_19.py",
    "research/rescue_0930/submission_receipt.json",
    "research/live_0929/audit.py",
    "research/live_0929/trace.py",
    "research/live_0929/build_sheep_cash.py",
    "research/live_0929/build_tomato_probe.py",
    "research/live_0929/package_sheep.py",
    "research/live_0929/panel_sheep.py",
    "research/live_0929/sheep_summary.json",
    "research/live_0929/combined_stopped.json",
    "research/port_0927/evaluate.py",
    "research/port_0927/panel.py",
    "tools/*.py",
    "engine/*.py",
    "gold/tick/*.py",
    "gold/hybrid/layers.py",
    "gold/tools/*.py",
    "gold/arena/*.py",
    "gold/arena/*.md",
    "gold/front/*.py",
    "gold/agent/*.py",
    "gold/newagent/*.py",
    "gold/oracle/*.py",
    "gold/sx/*.py",
    "gold/churn/*.py",
    "gold/results/*.md",
    "gold/topstudy/*.md",
    "gold/public/nb/NOTES.md",
    "gold/tmp/knob_notes.md",
    "research/notebook_insights.md",
    "research/dsm_plan/*.py",
    "research/dsm_plan/*.md",
    "research/dsm_plan/out/*.md",
    "research/dsm_sales/*.py",
    "research/dsm_sales/*.md",
    "research/panel/emu_eager/main.py",
    "research/panel/emu_eager_m/main.py",
    "research/panel/emu_tick0/main.py",
    "research/panel/emu_tick3/main.py",
    "research/panel/emu_tick30/main.py",
    "research/panel/emu_prebuy0/main.py",
    "research/panel/emu_antifade/main.py",
    "research/panel/emu_antifade2/main.py",
    "research/panel/emu_sw8/main.py",
    "research/carrera/*.py",
    "research/carrera/*.md",
    "research/carrera/unreal_lib/*.py",
    "research/live_0930/*.py",
    "prod/agents/p6/*.py",
    "prod/oracle/*.py",
    "research/carrera/layers/*.py",
    "research/carrera/results/*.md",
    "results/*.md",
    "prod/tools/*.py",
    "prod/agents/p1/*.py",
    "prod/agents/p2/*.py",
    "prod/agents/p3/*.py",
    "prod/agents/p3b/*.py",
    "prod/agents/p4/*.py",
    "prod/agents/p5/*.py",
    "prod/agents/hyb/*.py",
    "prod/results/*.md",
    "bc/*.py",
    "bc/*.txt",
    "bc/*.log",
    "bc/opening.json",
]

# credentials, and files kept out of the public repository
SKIP_NAMES = {"access_token", "kaggle.json", "credentials.json", "prompt_production_vs_unreal.md"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def put(dest, data, dry):
    old = open(dest, "rb").read() if os.path.exists(dest) else None
    if old == data:
        return "same"
    if not dry:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)
    return "new" if old is None else "changed"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=os.path.join(ROOT, "github_repo"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    repo = os.path.abspath(a.repo)
    assert os.path.isdir(os.path.join(repo, ".git")), f"{repo} is not a git checkout"
    counts = {"new": 0, "changed": 0, "same": 0}

    print("packages (sha256 of submission.tar.gz / main.py inside it):")
    for src, name in PACKAGES:
        tgz = os.path.join(ROOT, src, "submission.tar.gz")
        blob = open(tgz, "rb").read()
        with tarfile.open(tgz, "r:gz") as tar:
            members = {m.name: tar.extractfile(m).read() for m in tar.getmembers() if m.isfile()}
        assert set(members) >= {"main.py", "LICENSE.txt", "NOTICE.txt"}, (src, sorted(members))
        dest = os.path.join(repo, "submissions", name)
        for n in ("main.py", "LICENSE.txt", "NOTICE.txt"):
            counts[put(os.path.join(dest, n), members[n], a.dry_run)] += 1
        counts[put(os.path.join(dest, "submission.tar.gz"), blob, a.dry_run)] += 1
        print(f"  {name:40s} {sha(blob)[:8]}  {sha(members['main.py'])[:8]}")

    for pat in FILES:
        for path in sorted(glob.glob(os.path.join(ROOT, pat))):
            if os.path.basename(path) in SKIP_NAMES or "__pycache__" in path:
                continue
            rel = os.path.relpath(path, ROOT)
            counts[put(os.path.join(repo, rel), open(path, "rb").read(), a.dry_run)] += 1

    print(("dry run: " if a.dry_run else "") + ", ".join(f"{k} {v}" for k, v in counts.items()))


if __name__ == "__main__":
    main()
