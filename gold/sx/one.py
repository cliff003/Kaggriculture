import sys, os, json, collections
sys.path.insert(0, 'tools'); sys.path.insert(0, 'gold/tools')
import fastarena, forceshops
build, wfile, wi, seed = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
worlds = json.load(open(wfile))
forceshops.force(worlds[wi])
ns = {}
exec(compile(open(f'gold/builds/{build}/main.py', encoding='utf-8').read(), build, 'exec'), ns)
ours = ns['agent']
opp = fastarena.load_agent('research/panel/cha22/main.py')
seat = int(sys.argv[5]) if len(sys.argv) > 5 else 0
fa, fb = (ours, opp) if seat == 0 else (opp, ours)
r = fastarena.run_game(fa, fb, seed)
print('shops', worlds[wi])
print('rewards', r.get('rewards') if isinstance(r, dict) else r)
tel = ns.get('_SXNS', {}).get('_TEL', {})
print('SX telemetry', tel)
