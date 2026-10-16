r"""Catalog of market-arbitrage behaviours in harvested games (either seat, any team), for WHEAT and FERTILIZER.

    .venv\Scripts\python.exe gold\front\arbscan.py [--min-id 0] [--json OUT.json]

Per (game, seat, item) the recorded market lists are scanned for:
  tick      BUY >= 20 at s % 4 == 0 and SELL >= 20 at s + 1 (the public tick churn), with its buy slot
  offphase  BUY >= 20 at phase p and SELL >= 20 at the next step, p != 0
  prebuy    BUY >= 20 at s % 4 == 3 and SELL >= 20 at s + 2 (nothing big at s + 1)
  sandwich  in one step: BUY >= 20 in slots 0-2 and SELL >= 20 in slot 9 (or the reverse), net within 20%
  ladder    in one step: 3+ separate BUY and SELL orders of the item
  sched     tick-like cycles only at the fixed steps 327/375/419/435/487 (+-0)
A seat is tagged with a type when it shows >= 3 such events (>= 2 for sched). Prints teams per type, event counts,
and the team-42 results against each type.
"""
import argparse
import collections
import glob
import gzip
import json

SCHED = {327, 375, 419, 435, 487}


def qty(o):
    try:
        return int(o[2])
    except Exception:
        return 0


def scan(acts, item):
    ev = collections.Counter()
    slots = []
    for t in range(1, len(acts)):
        s = t - 1
        m = (acts[t] or {}).get("market") or []
        m1 = ((acts[t + 1] or {}).get("market") or []) if t + 1 < len(acts) else []
        m2 = ((acts[t + 2] or {}).get("market") or []) if t + 2 < len(acts) else []
        buys = [(i, qty(o)) for i, o in enumerate(m) if o and len(o) >= 3 and o[0] == "BUY_PRODUCT" and o[1] == item]
        sells = [(i, qty(o)) for i, o in enumerate(m) if o and len(o) >= 3 and o[0] == "SELL" and o[1] == item]
        b = sum(q for i, q in buys)
        sl = sum(q for i, q in sells)
        s1 = sum(qty(o) for o in m1 if o and len(o) >= 3 and o[0] == "SELL" and o[1] == item)
        b1 = sum(qty(o) for o in m1 if o and len(o) >= 3 and o[0] == "BUY_PRODUCT" and o[1] == item)
        s2 = sum(qty(o) for o in m2 if o and len(o) >= 3 and o[0] == "SELL" and o[1] == item)
        if len(buys) + len(sells) >= 3 and buys and sells:
            ev["ladder"] += 1
        early_b = sum(q for i, q in buys if i <= 2)
        late_s = sum(q for i, q in sells if i >= 9)
        early_s = sum(q for i, q in sells if i <= 2)
        late_b = sum(q for i, q in buys if i >= 9)
        if (early_b >= 20 and late_s >= 20 and abs(early_b - late_s) <= 0.2 * early_b) or \
           (early_s >= 20 and late_b >= 20 and abs(early_s - late_b) <= 0.2 * early_s):
            ev["sandwich"] += 1
            continue
        if b >= 20 and s1 >= 20 and abs(b - s1) <= 0.3 * b:
            if s in SCHED:
                ev["sched"] += 1
            elif s % 4 == 0:
                ev["tick"] += 1
                slots.append(min(i for i, q in buys))
            else:
                ev["offphase"] += 1
        elif s % 4 == 3 and b >= 20 and s2 >= 20 and s1 < 10 and b1 < 10 and abs(b - s2) <= 0.3 * b:
            ev["prebuy"] += 1
    return ev, slots


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-id", type=int, default=0)
    ap.add_argument("--json")
    a = ap.parse_args()
    recs = {}
    for f in glob.glob("data/games/live_*.jsonl.gz") + glob.glob("gold/front/front_*.jsonl.gz") + glob.glob("gold/top30/*.jsonl.gz"):
        for l in gzip.open(f, "rt", encoding="utf-8"):
            if l.strip():
                r = json.loads(l)
                if r["id"] >= a.min_id:
                    recs.setdefault(r["id"], r)
    types = collections.defaultdict(lambda: collections.defaultdict(list))
    ours = collections.defaultdict(list)
    for gid, r in recs.items():
        for seat in range(2):
            name = r["teams"][seat]
            for item in ("WHEAT", "FERTILIZER"):
                ev, slots = scan(r["acts"][seat], item)
                for k, v in ev.items():
                    if v >= (2 if k == "sched" else 3):
                        key = f"{item[:1]}:{k}"
                        types[key][name].append((gid, v))
                        if "42" in r["teams"] and name != "42":
                            me = r["teams"].index("42")
                            ours[key].append((gid, name, r["rewards"][me] - r["rewards"][1 - me]))
    print("games", len(recs))
    out = {}
    for key in sorted(types):
        teams = types[key]
        n_games = sum(len(v) for v in teams.values())
        g = ours.get(key, [])
        w = sum(1 for x in g if x[2] > 0)
        top = sorted(teams.items(), key=lambda kv: -len(kv[1]))[:10]
        print(f"\n{key}: {len(teams)} teams, {n_games} seat-games; vs team 42: {len(g)} games, we won {w}")
        print("   " + ", ".join(f"{t[:18]}({len(v)})" for t, v in top))
        out[key] = {"teams": {t: v for t, v in teams.items()}, "ours": g}
    if a.json:
        json.dump(out, open(a.json, "w", encoding="utf-8"), ensure_ascii=False)


if __name__ == "__main__":
    main()
