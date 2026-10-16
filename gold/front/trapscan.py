r"""Scan harvested games for anti-tick traps in either seat (team 42 experiment, 2026-09-26).
    .venv\Scripts\python.exe gold\front\trapscan.py [GLOB ...]
sandwich: at s % 4 == 0 a BUY_PRODUCT WHEAT >= 30 in slot <= 2 and a SELL WHEAT >= 30 in slot 9 (lifts, then sells
          into a last-slot tick buyer); prebuy: BUY_PRODUCT WHEAT >= 30 at s % 4 == 3 and SELL WHEAT >= 30 at s + 2."""
import sys, glob, gzip, json, collections
pats = sys.argv[1:] or ['data/games/live_*.jsonl.gz', 'gold/front/front_*.jsonl.gz', 'gold/top30/*.jsonl.gz']
seen = set(); teams = collections.defaultdict(lambda: collections.Counter()); ngames = 0
for p in pats:
    for f in glob.glob(p):
        for l in gzip.open(f, 'rt', encoding='utf-8'):
            if not l.strip():
                continue
            r = json.loads(l)
            if r['id'] in seen:
                continue
            seen.add(r['id']); ngames += 1
            for seat in range(2):
                acts = r['acts'][seat]; sw = pb = 0
                for t in range(1, len(acts)):
                    s = t - 1
                    m = (acts[t] or {}).get('market') or []
                    if s % 4 == 0 and len(m) >= 10:
                        b = any(o and o[0] == 'BUY_PRODUCT' and o[1] == 'WHEAT' and int(o[2]) >= 30 for o in m[:3])
                        o9 = m[9]
                        if b and o9 and o9[0] == 'SELL' and o9[1] == 'WHEAT' and int(o9[2]) >= 30:
                            sw += 1
                    if s % 4 == 3 and any(o and o[0] == 'BUY_PRODUCT' and o[1] == 'WHEAT' and int(o[2]) >= 30 for o in m):
                        m2 = (acts[t + 2] or {}).get('market') or [] if t + 2 < len(acts) else []
                        if any(o and o[0] == 'SELL' and o[1] == 'WHEAT' and int(o[2]) >= 30 for o in m2):
                            pb += 1
                name = r['teams'][seat]
                if sw >= 3:
                    teams[name]['sandwich'] += 1
                if pb >= 3:
                    teams[name]['prebuy'] += 1
                teams[name]['games'] += 1
print('games scanned', ngames)
for kind in ('sandwich', 'prebuy'):
    rows = sorted(((c[kind], n, c['games']) for n, c in teams.items() if c[kind]), reverse=True)
    print(f'\n{kind}: {len(rows)} teams, {sum(r[0] for r in rows)} games')
    for k, n, g in rows[:40]:
        print(f'  {n[:30]:30s} {k:3d}/{g}')
