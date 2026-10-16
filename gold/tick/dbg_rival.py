import sys, glob, gzip, json
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools')
import fastarena, forceshops
from cfroute import tape_file
if __name__ == '__main__':
    gid, cand = int(sys.argv[1]), sys.argv[2]
    rec = None
    for f in sorted(glob.glob('data/games/live_*.jsonl.gz')):
        for line in gzip.open(f, 'rt', encoding='utf-8'):
            r = json.loads(line)
            if r['id'] == gid:
                rec = r; break
        if rec: break
    me = rec['teams'].index('42')
    tape = tape_file(rec, 1 - me)
    forceshops.force(rec['shops'])
    f = fastarena.load_agent(cand); g = fastarena.load_agent(tape)
    r = fastarena.run_game(f, g, rec['seed']) if me == 0 else fastarena.run_game(g, f, rec['seed'])
    G = f.__globals__
    tel = G.get('TEL') or G.get('_TICK_NS', {}).get('TEL')
    mem = (G.get('_MEM') or {}).get(me, {})
    print('opp', rec['teams'][1 - me], 'rewards', r['rewards'], 'me', me, 'TEL', tel)
    fl = mem.get('flow', {})
    acts = rec['acts'][1 - me]
    shown = 0
    for t in sorted(fl):
        if 240 <= t < 300 and t % 4 in (0, 1):
            a = acts[t + 1] if t + 1 < len(acts) else None
            w = [o for o in ((a or {}).get('market') or []) if isinstance(o, list) and len(o) >= 3 and o[1] == 'WHEAT']
            print(t, t % 24, 'inferred', fl[t], 'actual orders', w)
