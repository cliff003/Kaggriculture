import sys, os, json, collections
sys.path.insert(0, 'tools'); sys.path.insert(0, 'gold/tools')
import fastarena, forceshops
build, wfile, wi, seed = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
worlds = json.load(open(wfile))
forceshops.force(worlds[wi])
ns = {}
exec(compile(open(f'gold/builds/{build}/main.py', encoding='utf-8').read(), build, 'exec'), ns)
inner = ns['agent']
SX = ns['_SXNS']
log = []
def ours(obs, cfg=None):
    a = inner(obs, cfg)
    st = SX['_ST'].get(int(obs['player']))
    step = int(obs['step'])
    if st and st.get('committed'):
        farm = obs['farms'][int(obs['player'])]
        pos = [tuple(farm['farmer'])] + [tuple(h) for h in farm['hands']]
        units = [a.get('farmer')] + list(a.get('hands') or [])
        ws = sorted(st['workers'])
        tl = []
        for (x, y) in st['tiles']:
            t = farm['tiles'][y][x]
            if isinstance(t, dict) and t.get('kind') == 'PLANT':
                tl.append(f"{t['crop'][0]}{step//24 - t['planted_day']}y{t['yield_units']}{'w' if t['watered_today'] else '-'}{'f' if t.get('fertilized_until_day',-1) >= step//24 else ''}")
            else:
                tl.append(str(t)[:6] if t else '.')
        log.append((step, [(w, pos[w] if w < len(pos) else None, units[w] if w < len(units) else None) for w in ws], tl, obs['private']['seeds'].get('STRAWBERRY', 0), [o for o in a.get('market', []) if o and o[0] in ('HIRE', 'BUY_LAND', 'BUY_SEED')]))
    return a
opp = fastarena.load_agent('research/panel/cha22/main.py')
r = fastarena.run_game(ours, opp, seed)
days = set(int(x) for x in sys.argv[5].split(','))
for (step, w, tl, seeds, mk) in log:
    if step // 24 in days:
        print(f"d{step//24} h{step%24:2d} seeds {seeds} workers {w} market {mk}")
        if step % 24 in (0, 12, 23):
            print('     tiles', tl)
print('rewards', r.get('rewards') if isinstance(r, dict) else r, SX['_TEL'])
