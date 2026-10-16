r"""Anti-tick trap scan with round-trip matching, by episode recency (team 42 experiment, 2026-09-26)."""
import sys, glob, gzip, json, collections
pats = ['data/games/live_*.jsonl.gz', 'gold/front/front_*.jsonl.gz', 'gold/top30/*.jsonl.gz']
seen = {}
for p in pats:
    for f in glob.glob(p):
        for l in gzip.open(f, 'rt', encoding='utf-8'):
            if l.strip():
                r = json.loads(l)
                seen.setdefault(r['id'], r)
def wq(m, op, slots=None):
    return sum(int(o[2]) for i, o in enumerate(m) if o and len(o) >= 3 and o[0] == op and o[1] == 'WHEAT'
               and (slots is None or i in slots))
rows = []
for gid, r in seen.items():
    for seat in range(2):
        name = r['teams'][seat]
        acts = r['acts'][seat]
        sw = pb = 0
        for t in range(1, len(acts) - 2):
            s = t - 1
            m = (acts[t] or {}).get('market') or []
            if s % 4 == 0:
                b = wq(m, 'BUY_PRODUCT', {0, 1, 2}); sl = wq(m, 'SELL', {9})
                if b >= 30 and sl >= 30 and abs(b - sl) <= 0.2 * b:
                    sw += 1
            if s % 4 == 3:
                b = wq(m, 'BUY_PRODUCT')
                m2 = (acts[t + 2] or {}).get('market') or []
                sl = wq(m2, 'SELL')
                m1 = (acts[t + 1] or {}).get('market') or []
                if b >= 30 and abs(sl - b) <= 0.25 * b and wq(m1, 'SELL') < 10 and wq(m1, 'BUY_PRODUCT') < 10:
                    pb += 1
        if sw >= 3 or pb >= 5:
            rows.append((gid, name, sw, pb, r['teams'][1 - seat]))
rows.sort()
print('games', len(seen))
c = collections.Counter()
for gid, name, sw, pb, opp in rows:
    c[(name, 'sandwich' if sw >= 3 else 'prebuy')] += 1
for (n, k), v in sorted(c.items(), key=lambda x: -x[1]):
    print(f'{k:9s} {n[:30]:30s} {v}')
print('\nmost recent 25:')
for gid, name, sw, pb, opp in rows[-25:]:
    print(gid, name[:24], 'sandwich', sw, 'prebuy', pb, 'vs', opp[:20])
