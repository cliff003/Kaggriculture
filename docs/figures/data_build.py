r"""Rebuild docs/figures/data/ (the committed table twins of every figure).

LOCAL ONLY: reads ../data (the final leaderboard, episode lists and recorded games, not in the repository) and
runs kaggle-environments 1.32.7. Every derived number is asserted against the value quoted in docs/.

python docs/figures/data_build.py
"""
import csv
import glob
import gzip
import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(os.path.dirname(REPO), "data")
OUT = os.path.join(HERE, "data")
OURS = 16908623
FINALS = (56649860, 56713491)

# Numbers quoted in the docs, with their source. Figures take every non-axis number from here or from data/.
FACTS = [
    ("final_rank", "#553 of 10,148", "docs/postmortem.md#final-standing"),
    ("final_score", "4499.2", "docs/postmortem.md#final-standing"),
    ("silver_line", "#507 at 4514.5", "docs/postmortem.md#final-standing"),
    ("silver_gap", "15.3 points, 46 places", "docs/postmortem.md#final-standing"),
    ("gold_line", "#30 at 5099.6", "docs/postmortem.md#final-standing"),
    ("bronze_line", "#1014 at 4398.5", "docs/postmortem.md#final-standing"),
    ("first_score", "5890.3", "docs/postmortem.md#the-final-board"),
    ("peak_rank", "#128 at 2606.7 on Sep 26 10:23", "docs/postmortem.md#final-standing"),
    ("v8_peak", "2679 at 09:39 on Sep 26", "docs/history.md"),
    ("live_end", "#547 at 2065.7; live silver line 2093.1 (27.4 above)", "docs/postmortem.md#final-standing"),
    ("finals_live", "V12_AventadorSVJ 2046.0; v12_19 2065.7", "docs/history.md"),
    ("routes", "41 recorded routes; days 0 to 5 opening, day 6 mid-game route by the first two shops, day 27 endgame; 64 shop pairs", "docs/solution.md#the-base-agent-cha22"),
    ("game", "720 steps = 30 days x 24 hours; up to 10 market orders per step", "docs/solution.md#the-game"),
    ("base_choice", "826 W / 14 L against the 21 distinct codes among the top 30 public notebooks", "docs/solution.md#the-base-agent-cha22"),
    ("planner", "1014.5", "docs/history.md"),
    ("orderslot", "97 W / 3 L from step 288; 2454 vs 2342 six hours after a simultaneous upload", "docs/solution.md#1-order-slot-priority"),
    ("fertmore", "844 to 873 wins of 980", "docs/solution.md#3-fixes-to-the-bases-behaviour"),
    ("tick", "497 to 538 wins of 576 replays; up to 95 wheat; from day 10 (finals day 13)", "docs/solution.md#4-tick-wheat-arbitrage-around-the-towns-consumption"),
    ("tick_off", "616 per game on 1,504 replays (112 flips lost)", "docs/experiments.md"),
    ("trap", "-16,743 to +13,919; limit 40; v8 lost its games against two sandwich traders by about 17k each", "docs/solution.md#5-defending-tick-peer-guard-and-trap-guard"),
    ("fade", "+2.0k to +21.5k per game against an emulated arbitrageur", "docs/solution.md#6-fade-trading-against-other-arbitrageurs"),
    ("gfade", "+1,940 per game on 9 replays", "docs/solution.md#6-fade-trading-against-other-arbitrageurs"),
    ("deferral", "+69 per game on 917 replays, 0 flips lost", "docs/solution.md"),
    ("milk", "160 at stock 10,000; price 1 after 76 extra milk, 62 strawberries, 59 wool; 20 milk: 2,802 first, 1,962 second, 2,402 each in one slot (+440, +840)", "engine market_price"),
    ("gap_top5", "547 seats; tomatoes 98% vs 11% (about 10 tiles, days 18 to 20); geese 5 vs 3; fertilizer 204 vs 117 (88 bought, 336 sold); idle 190 vs 471; cash day 9 261 vs 2,833; final 109.8k vs 100.4k", "docs/postmortem.md#the-gap-to-the-top"),
    ("unreal", "#54; 66 to 9 on 75 replays; +6.2k eggs, +3.6k strawberries, +3.2k carrots, +1.5k wheat; 28 W / 3 L, +15.7k against cha22-based farms", "docs/postmortem.md#the-gap-to-the-top"),
    ("unreal_farm", "land day 8 vs 11; peak geese 8.4 vs 2.6; 65.5 vs 50 tiles by day 8; egg income 12.3k vs 4.1k", "docs/postmortem.md#the-gap-to-the-top"),
    ("attempts", "-11.5k (about 60 variants); 0.88 accuracy, 0 wins; -7.9k; -19.1k", "docs/experiments.md"),
    ("wheat_price", "P(gap) = 25 + sqrt(gap), rounded, for wheat below the neutral stock of 10,000", "engine market_price"),
    ("fade_estimate", "90 x 0.028 x (77 - 2) = about 190 against the measured +206", "docs/solution.md"),
    ("deadline_days", "Sep 29: 20 W / 52 L against submissions uploaded after Sep 28 18:47", "docs/postmortem.md"),
    ("uploads", "39 uploads, 34 packages", "docs/history.md"),
]

# live leaderboard snapshots (docs/postmortem.md "Standing over time")
STANDING = [
    ("2026-09-26 10:23", 128), ("2026-09-27 06:08", 161), ("2026-09-28 09:46", 243), ("2026-09-28 12:25", 191),
    ("2026-09-28 18:30", 182), ("2026-09-29 01:00", 194), ("2026-09-29 12:00", 200), ("2026-09-29 13:32", 235),
    ("2026-09-29 15:22", 206), ("2026-09-30 04:49", 304), ("2026-09-30 15:49", 352), ("2026-10-01 04:38", 401),
    ("2026-10-01 15:02", 424), ("2026-10-08 06:58", 490), ("2026-10-11 21:00", 535), ("2026-10-12 05:50", 552),
    ("2026-10-13 06:47", 526), ("2026-10-16 16:01", 547),
]

# labelled teams on the final board: rank -> (approach, label)
LABELS = {
    1: ("learned", "M & M & P & Q"), 3: ("production_np", "DSM"), 4: ("learned", "Farmcore"),
    5: ("learned", "有辣条有权"), 7: ("learned", "DECEM"), 12: ("learned", "Unknown Mother-Goose"),
    13: ("learned", "MarvinTMB"),
    21: ("production", "Vadim Vasilenko"), 24: ("learned", "abozten"), 54: ("production", "unreal"),
    76: ("production", "Ryo Hasegawa"), 92: ("market", "Otter Vibe"), 429: ("market", "lumen"),
    464: ("market", "curiosity"), 553: ("us", "42"), 681: ("market", "kwon yong deuk"),
    802: ("market", "Sho Saga"), 2142: ("other", "Abhinav0370"),
}

BANDS = [(31, 100), (101, 200), (201, 300), (301, 400), (401, 507), (508, 552), (554, 600), (601, 700),
         (701, 800), (801, 1014), (1015, 20000)]


def wilson(w, n, z=1.6449):
    if n == 0:
        return 0.0, 0.0
    p = w / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)


def write_csv(name, rows, fields):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def board():
    rows = list(csv.DictReader(open(os.path.join(DATA, "lb", "final_1016", "final_api_board.csv"), encoding="utf-8")))
    assert len(rows) == 10148
    rank = {int(r["teamId"]): i + 1 for i, r in enumerate(rows)}
    score = [float(r["score"]) for r in rows]
    assert rank[OURS] == 553 and score[552] == 4499.2
    assert (score[29], score[506], score[1013], score[0]) == (5099.6, 4514.5, 4398.5, 5890.3)
    write_csv("final_board.csv", [{"rank": i + 1, "score": score[i]} for i in range(3000)], ["rank", "score"])
    lab = []
    for rk, (ap, name) in sorted(LABELS.items()):
        r = rows[rk - 1]
        assert r["teamName"].strip() == name, (rk, r["teamName"], name)
        lab.append({"rank": rk, "team": name, "score": score[rk - 1], "approach": ap})
    write_csv("labels.csv", lab, ["rank", "team", "score", "approach"])
    return rank


def bands(rank):
    seen, counted = set(), []
    for sid in FINALS:
        d = json.load(open(os.path.join(DATA, "episodes", f"{sid}.json"), encoding="utf-8"))
        for e in d["episodes"]:
            if e.get("state") != "COMPLETED" or not e.get("endTime") or e["endTime"] < "2026-10-01":
                continue
            me = [a for a in e["agents"] if a.get("submissionId") == sid]
            op = [a for a in e["agents"] if a.get("submissionId") != sid]
            if len(me) != 1 or len(op) != 1 or (e["id"], sid) in seen:
                continue
            seen.add((e["id"], sid))
            if me[0].get("reward") is None or op[0].get("reward") is None:
                continue
            r = rank.get(op[0].get("teamId"))
            if r is None:
                continue
            res = "W" if me[0]["reward"] > op[0]["reward"] else "L" if me[0]["reward"] < op[0]["reward"] else "D"
            counted.append((r, res))
    assert len(counted) == 1623, len(counted)
    out = []
    for lo, hi in BANDS:
        g = [res for r, res in counted if lo <= r <= hi]
        w, l, dr = g.count("W"), g.count("L"), g.count("D")
        n = len(g)
        lo_i, hi_i = wilson(w + 0.5 * dr, n)
        out.append({"lo": lo, "hi": hi, "games": n, "W": w, "L": l, "D": dr,
                    "win": round(100 * (w + 0.5 * dr) / n) if n else 0,
                    "ci_lo": round(100 * lo_i), "ci_hi": round(100 * hi_i)})
    by = {(b["lo"], b["hi"]): b for b in out}
    assert (by[(101, 200)]["W"], by[(101, 200)]["L"]) == (9, 25)
    silver = [res for r, res in counted if 31 <= r <= 507]
    bronze = [res for r, res in counted if 508 <= r <= 1014]
    assert (silver.count("W"), silver.count("L")) == (233, 472)
    assert (bronze.count("W"), bronze.count("L"), bronze.count("D")) == (572, 344, 1)
    write_csv("winrate_bands.csv", out, ["lo", "hi", "games", "W", "L", "D", "win", "ci_lo", "ci_hi"])


def milk_race():
    sys.path.insert(0, os.path.join(REPO, "tools"))
    import fastarena  # noqa: F401
    from kaggle_environments.envs.kaggriculture.kaggriculture import market_price as P
    first = sum(P("MILK", 10000 + k) for k in range(20))
    second = sum(P("MILK", 10020 + k) for k in range(20))
    same = sum(P("MILK", 10000 + 2 * k) for k in range(20))
    thr = {it: next(x for x in range(500) if P(it, 10000 + x) == 1) for it in ("MILK", "STRAWBERRY", "WOOL")}
    assert (first, second, same) == (2802, 1962, 2402) and thr == {"MILK": 76, "STRAWBERRY": 62, "WOOL": 59}
    tape = {"first": [P("MILK", 10000 + k) for k in range(40)],
            "pairs": [P("MILK", 10000 + 2 * k) for k in range(20)]}
    json.dump({"first": first, "second": second, "same_slot_each": same, "price1_after": thr,
               "milk_at_10000": P("MILK", 10000), "prices": tape},
              open(os.path.join(OUT, "milk_race.json"), "w"), indent=1)


def turn_example():
    for line in gzip.open(os.path.join(DATA, "games", "live_v8.jsonl.gz"), "rt", encoding="utf-8"):
        r = json.loads(line)
        if r["id"] == 113640990:
            seat = r["subs"].index(56573604)
            t0, t1 = r["acts"][seat][493]["market"], r["acts"][seat][494]["market"]
            assert t0[-1] == ["BUY_PRODUCT", "WHEAT", 95] and t1[-1] == ["SELL", "WHEAT", 95]
            json.dump({"game": 113640990, "step": 492, "day": 20, "hour": 12, "orders": t0, "next": t1},
                      open(os.path.join(OUT, "turn_example.json"), "w"), indent=1)
            return
    raise SystemExit("game 113640990 not found")


def rounds():
    env = dict(os.environ, PYTHONHASHSEED="0")
    py, rp = sys.executable, os.path.join(HERE, "rounds.py")
    g = lambda n: os.path.join(DATA, "games", n)
    runs = [
        ("tick_and_sandwich", [g("live_v8.jsonl.gz"), "113707384", "--steps", "300", "301", "304", "305"]),
        ("trap_guard", [g("live_v8.jsonl.gz"), "113707384", "--steps", "324", "325",
                        "--cand", os.path.join(REPO, "submissions", "v9_own_cha22_tick_trapguard", "main.py")]),
        ("fade", [g("live_churn.jsonl.gz"), "113305232", "--steps", "364", "365",
                  "--cand", os.path.join(REPO, "submissions", "V12_AventadorSVJ", "main.py")]),
    ]
    out = {}
    for name, args in runs:
        r = subprocess.run([py, rp] + args, capture_output=True, text=True, env=env, cwd=REPO)
        out[name] = json.loads(r.stdout)
    a, b = out["tick_and_sandwich"], out["trap_guard"]
    assert a["rewards"] == [104872.0, 121615.0] and b["rewards"] == [119773.0, 105854.0]
    tot = lambda st, who, op: sum(f["total"] for f in st["fills"] if f["who"] == who and f["op"] == op)
    s = a["steps"]
    assert tot(s["305"], "us", "SELL") - tot(s["304"], "us", "BUY_PRODUCT") == 9
    assert tot(s["301"], "us", "SELL") - tot(s["300"], "us", "BUY_PRODUCT") == -117
    s = b["steps"]
    assert tot(s["324"], "us", "SELL") - tot(s["325"], "us", "BUY_PRODUCT") == 241
    f = out["fade"]["steps"]
    fade_sell = sum(x["total"] for x in f["364"]["fills"] if x["who"] == "us" and x["slot"] == 9)
    fade_buy = sum(x["total"] for x in f["365"]["fills"] if x["who"] == "us" and x["slot"] == 9)
    assert fade_sell - fade_buy == 206
    # what our 95 should have cost at the opening stock of the sandwiched step (the trap guard's own-order estimate)
    sys.path.insert(0, os.path.join(REPO, "tools"))
    import fastarena  # noqa: F401
    from kaggle_environments.envs.kaggriculture.kaggriculture import market_price as P
    s0 = out["tick_and_sandwich"]["steps"]["300"]["stock_start"]
    expect = sum(P("WHEAT", s0 - 1 - k) for k in range(95))
    paid = tot(out["tick_and_sandwich"]["steps"]["300"], "us", "BUY_PRODUCT")
    assert (expect, paid - expect) == (3900, 90), (expect, paid)
    out["tick_and_sandwich"]["own_order_expectation_300"] = expect
    out["fade"]["estimate"] = {"slope": round(1 / (2 * math.sqrt(309)), 3), "lot": 90, "rival": 77, "eaten": 2,
                               "value": round(90 * (1 / (2 * math.sqrt(309))) * (77 - 2))}
    for v in out.values():
        v.pop("live_rewards", None)
    out["fade"].pop("rewards", None)   # the replay total is not cited anywhere
    json.dump(out, open(os.path.join(OUT, "wheat_rounds.json"), "w"), indent=1)


# the 34 packages in submissions/ by line: (version, lane, day, status, change); day = build or upload day (Sep)
# live = ran on the ladder and was replaced, final = active at the end. Dates: submissions/README.md (uploads),
# docs/changelog_0927_1016.md (builds from Sep 27), NOTICE.txt of v12 to v12_3 (Sep 26).
LINEAGE = [
    ("v3", "live", 24, "live", "rescue + order-slot"), ("v4", "live", 24, "live", "cha22 + order-slot"),
    ("v6", "live", 25, "live", "+ eager sell, sell order"), ("v7", "live", 25, "live", "eager band 0.2x to 1.4x"),
    ("v6b", "live", 25, "live", "no eager ceiling"), ("v7b", "live", 25, "live", "+ wheat lead"),
    ("v7c", "live", 25, "live", "+ base fixes"), ("v8", "live", 26, "live", "+ TICK"),
    ("v9", "live", 26, "live", "+ trap guard"), ("v10", "live", 27, "live", "+ tomato gate"),
    ("v11a", "public", 27, "sealed", "pre-buy rule"), ("v11", "public", 28, "live", "+ deferral, rev_guard"),
    ("V10_CarreraGT", "public", 28, "live", "+ 18 tomatoes"),
    ("v12", "ace", 26, "sealed", "v8 + FADE"), ("v12_1", "ace", 26, "sealed", "TICK from day 13"),
    ("v12_2", "ace", 26, "sealed", "scheduled fade"), ("v12_3", "ace", 26, "sealed", "+ trap guard"),
    ("v12_4", "ace", 27, "sealed", "tomato gate"), ("v12_5", "ace", 27, "sealed", "P&L guard"),
    ("v12_6", "ace", 27, "sealed", "GFADE"), ("v12_7", "ace", 27, "sealed", "pre-buy rule"),
    ("v12_8", "ace", 28, "sealed", "deferral"), ("v12_9", "ace", 28, "sealed", "fade position up to 2N"),
    ("v12_10", "ace", 28, "rejected", "squeeze layer"), ("v12_11", "ace", 28, "sealed", "fade wind-down"),
    ("v12_12", "ace", 28, "sealed", "precise warehouse room"), ("v12_13", "ace", 28, "sealed", "base wheat-sell cap"),
    ("v12_14", "ace", 28, "sealed", "cap only against 40+"), ("v12_15", "ace", 28, "sealed", "18 tomatoes"),
    ("V12_AventadorSVJ", "ace", 28, "final", "= v12_15"), ("v12_16", "ace", 28, "rejected", "strawberry block"),
    ("v12_17", "ace", 29, "sealed", "sheep cash reserve"), ("v12_18", "ace", 30, "sealed", "late tomato crews"),
    ("v12_19", "ace", 30, "final", "layout-adaptive fertilizer"),
]


def uploads():
    """All 39 uploads, parsed from the tables in docs/history.md."""
    rows = []
    for line in open(os.path.join(REPO, "docs", "history.md"), encoding="utf-8"):
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 5 or not c[0].isdigit() or not re.match(r"\d\d-\d\d \d\d:\d\d$", c[1]):
            continue
        n = int(c[0])
        if 20 <= n <= 25:          # phase 2 has a "By" column
            ver, change = c[3], c[4]
        else:
            ver, change = c[2], c[3]
        m = re.match(r"([\d.]+)", c[-1])
        rows.append({"n": n, "time_utc": "2026-" + c[1], "version": ver, "change": change,
                     "rating": m.group(1) if m else "", "climbing": int("still climbing" in c[-1]),
                     "note": "" if m and c[-1] == m.group(1) else c[-1]})
    assert [r["n"] for r in rows] == list(range(1, 40)), [r["n"] for r in rows]
    byv = {r["version"]: r for r in rows}
    assert byv["v8"]["time_utc"] == "2026-09-26 07:55" and byv["v8"]["rating"] == "2545.4"
    assert byv["v12_19"]["time_utc"] == "2026-09-30 16:41" and byv["V12_AventadorSVJ"]["rating"] == "2046.0"
    write_csv("uploads.csv", rows, ["n", "time_utc", "version", "change", "rating", "climbing", "note"])
    # packages: every package in submissions/README.md appears once in LINEAGE
    pk = []
    for line in open(os.path.join(REPO, "submissions", "README.md"), encoding="utf-8"):
        m = re.match(r"\| \[([^\]]+)\]\(", line)
        if m:
            pk.append(m.group(1))
    assert len(pk) == 34 and sorted(pk) == sorted(v for v, *_ in LINEAGE), set(pk) ^ {v for v, *_ in LINEAGE}
    json.dump([{"version": v, "lane": l, "day": d, "status": s, "change": c} for v, l, d, s, c in LINEAGE],
              open(os.path.join(OUT, "lineage.json"), "w", encoding="utf-8"), indent=1)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", help="facts standing board milk turn rounds uploads")
    a = ap.parse_args()
    run = lambda k: not a.only or k in a.only  # noqa: E731
    os.makedirs(OUT, exist_ok=True)
    if run("facts"):
        json.dump([{"id": i, "text": t, "source": s} for i, t, s in FACTS],
                  open(os.path.join(OUT, "facts.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    if run("standing"):
        write_csv("standing.csv", [{"time_utc": t, "rank": r} for t, r in STANDING], ["time_utc", "rank"])
    if run("board"):
        bands(board())
    if run("milk"):
        milk_race()
    if run("turn"):
        turn_example()
    if run("rounds"):
        rounds()
    if run("uploads"):
        uploads()
    print("data written to", OUT)


if __name__ == "__main__":
    main()
