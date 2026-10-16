r"""Per-day comparison of a team's live game (exact replay of both tapes) with CAND replayed in the team's seat.
    .venv\Scripts\python.exe gold\front\daycmp.py GAME_ID TEAM CAND.py [--days 8-29]"""
import sys, glob, gzip, json, collections
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools'); sys.path.insert(0, 'gold/front')
import gstat
from seatswap import tape_file
if __name__ == '__main__':
    gid, team, cand = int(sys.argv[1]), sys.argv[2], sys.argv[3]
    lo, hi = (8, 29)
    if len(sys.argv) > 5 and sys.argv[4] == '--days':
        lo, hi = map(int, sys.argv[5].split('-'))
    rec = None
    for p in glob.glob('gold/front/front_*.jsonl.gz'):
        for l in gzip.open(p, 'rt', encoding='utf-8'):
            if l.strip():
                r = json.loads(l)
                if r['id'] == gid: rec = r
    seat = rec['teams'].index(team)
    t0, t1 = tape_file(rec, 0), tape_file(rec, 1)
    live = gstat.play_one((t0, t1, rec['seed'], seat, rec['shops']))
    seats = [t0, t1]; seats[seat] = cand
    cf = gstat.play_one((seats[0], seats[1], rec['seed'], seat, rec['shops']))
    print(team, 'vs', rec['teams'][1 - seat], 'shops', rec['shops'], 'live', live['rewards'], 'cand', cf['rewards'])
    for d in range(lo, hi + 1):
        a, b = live['days'][seat][d], cf['days'][seat][d]
        ea, eb = a.get('end') or {}, b.get('end') or {}
        def crops(e): c = e.get('crops') or {}; return '/'.join(str(c.get(k, 0)) for k in ('STRAWBERRY', 'TOMATO', 'CARROT', 'WHEAT', 'MELON'))
        def an(e): c = e.get('animals') or {}; return '/'.join(str(c.get(k, 0)) for k in ('COW', 'SHEEP', 'GOOSE'))
        def rev(x): return ' '.join(f"{k[:3]}{int(v)}" for k, v in sorted((x.get('sell_rev') or {}).items(), key=lambda kv: -kv[1])[:5])
        print(f"d{d:2d} money {ea.get('money'):>8} {eb.get('money'):>8} | crops s/t/c/w/m {crops(ea):>14} {crops(eb):>14} | "
              f"anim c/s/g {an(ea):>8} {an(eb):>8} | hires {a.get('hires')}/{b.get('hires')} land {a.get('land')}/{b.get('land')} "
              f"eff {a.get('effective')}/{b.get('effective')} move {a.get('move')}/{b.get('move')} pass {a.get('pass')}/{b.get('pass')}")
        print(f"      rev team: {rev(a)}\n      rev cand: {rev(b)}")


def totals(days):
    import collections
    rev = collections.Counter(); units = collections.Counter(); spend = collections.Counter()
    for d in days:
        for k, v in (d.get('sell_rev') or {}).items(): rev[k] += v
        for k, v in (d.get('sell_units') or {}).items(): units[k] += v
        for k, v in (d.get('buy_spend') or {}).items(): spend[k] += v
        spend['HIRE'] += d.get('hire_cost', 0) or 0
        for l in (d.get('land') or []):
            spend['LAND'] += l[2] if isinstance(l, list) and len(l) > 2 else 0
    return rev, units, spend
