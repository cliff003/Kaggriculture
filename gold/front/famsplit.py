r"""Split live-replay results by how closely the opponent mirrors our route (team 42 experiment, 2026-09-26).

    .venv\Scripts\python.exe gold\front\famsplit.py BASE_JSON REF=FILE.json:KEY CAND=FILE.json:KEY [...]
        [--steps 96] [--bins 0.9,0.6]

BASE_JSON: a cfroute --json file (keys are the replayed episode ids). Each REF / CAND names a cfmulti --out file
and the candidate key inside it ({cand: {episode id: margin}}); a key may be abbreviated to any unique substring.
Mirror score of a game: share of (step, unit) pairs in steps 1..STEPS where the opponent's recorded unit op equals
ours (team 42's seat of the same live game; both run the cha22 route when the opponent is family). Games are
binned by the score; per bin: games, wins of each entry, mean margin change against REF with its standard error,
flips.
"""
import argparse
import glob
import gzip
import json
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def mirror_score(r, steps):
    me = r["teams"].index("42")
    a, b = r["acts"][me], r["acts"][1 - me]
    same = tot = 0
    for t in range(1, steps + 1):
        x = (a[t] if t < len(a) else None) or {}
        y = (b[t] if t < len(b) else None) or {}
        ux = [x.get("farmer")] + list(x.get("hands") or [])
        uy = [y.get("farmer")] + list(y.get("hands") or [])
        n = max(len(ux), len(uy))
        for i in range(n):
            tot += 1
            if i < len(ux) and i < len(uy) and ux[i] == uy[i]:
                same += 1
    return same / max(1, tot)


def load_entry(spec):
    path, key = spec.rsplit(":", 1)
    d = json.load(open(path, encoding="utf-8"))
    ks = [k for k in d if key in k]
    assert len(ks) == 1, (spec, list(d))
    return ks[0], d[ks[0]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base_json")
    ap.add_argument("entries", nargs="+", help="REF first, then candidates: FILE.json:KEY")
    ap.add_argument("--steps", type=int, default=96)
    ap.add_argument("--bins", default="0.9,0.6")
    ap.add_argument("--dump", help="write {episode id: mirror score} here")
    a = ap.parse_args()
    base = json.load(open(a.base_json, encoding="utf-8"))
    score = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "games", "live_*.jsonl.gz"))):
        with gzip.open(f, "rt", encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                k = str(r["id"])
                if k in base and k not in score and "42" in r["teams"]:
                    score[k] = mirror_score(r, a.steps)
    if a.dump:
        json.dump(score, open(a.dump, "w"), ensure_ascii=False)
    cuts = [float(x) for x in a.bins.split(",")]
    def bin_of(s):
        for i, c in enumerate(cuts):
            if s >= c:
                return i
        return len(cuts)
    names = ["mirror >= %.2f" % cuts[0]] + ["%.2f..%.2f" % (cuts[i + 1], cuts[i]) for i in range(len(cuts) - 1)] + \
            ["other < %.2f" % cuts[-1]]
    ents = [load_entry(e) for e in a.entries]
    ref_name, ref = ents[0]
    hist = [0] * 11
    for s in score.values():
        hist[min(10, int(s * 10))] += 1
    print("mirror score histogram (0.0-0.1 ... 1.0):", hist)
    for bi, bname in enumerate(names + ["all"]):
        ks = [k for k in score if (bi == len(names) or bin_of(score[k]) == bi) and k in ref and all(k in e for _, e in ents)]
        if not ks:
            continue
        print(f"\n[{bname}] games {len(ks)}  opp e.g. {sorted({base[k]['opp'] for k in ks})[:6]}")
        print(f"  {os.path.basename(os.path.dirname(ref_name)) or ref_name:22s} wins {sum(ref[k] > 0 for k in ks):4d}")
        for name, e in ents[1:]:
            d = [e[k] - ref[k] for k in ks]
            se = st.stdev(d) / len(d) ** 0.5 if len(d) > 1 else 0
            fw = sum(1 for k in ks if ref[k] <= 0 < e[k])
            fl = sum(1 for k in ks if e[k] <= 0 < ref[k])
            print(f"  {os.path.basename(os.path.dirname(name)) or name:22s} wins {sum(e[k] > 0 for k in ks):4d}  "
                  f"mean {st.mean(d):+7.0f} se {se:5.0f}  flips +{fw} -{fl}")


if __name__ == "__main__":
    main()
