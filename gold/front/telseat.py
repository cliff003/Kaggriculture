r"""Run CAND in a team's seat of a harvested game (opponent tape kept) in-process and print the TICK layer telemetry.
    .venv\Scripts\python.exe gold\front\telseat.py GAME_ID TEAM CAND.py"""
import sys, glob, gzip, json
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools'); sys.path.insert(0, 'gold/front')
import fastarena, forceshops
from seatswap import tape_file
if __name__ == '__main__':
    gid, team, cand = int(sys.argv[1]), sys.argv[2], sys.argv[3]
    rec = None
    for p in glob.glob('gold/front/front_*.jsonl.gz'):
        for l in gzip.open(p, 'rt', encoding='utf-8'):
            if l.strip():
                r = json.loads(l)
                if r['id'] == gid: rec = r
    seat = rec['teams'].index(team)
    forceshops.force(rec['shops'])
    f = fastarena.load_agent(cand)
    g = fastarena.load_agent(tape_file(rec, 1 - seat))
    r = fastarena.run_game(f, g, rec['seed']) if seat == 0 else fastarena.run_game(g, f, rec['seed'])
    G = f.__globals__
    ns = G.get('_TICK_NS') or G
    tel = ns.get('TEL')
    mem = (ns.get('_MEM') or {}).get(seat, {})
    fl = mem.get('flow', {})
    big = [(t, v) for t, v in sorted(fl.items()) if abs(v) >= 10]
    print(rec['teams'], 'team seat', seat, 'rewards', r['rewards'], 'live', rec['rewards'])
    print('TEL', tel, 'rival', mem.get('rival'))
    print('rival flows >=10 (step, net sold):', big[:40])
