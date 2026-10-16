r"""Trace what the agent in seat 0 does on SW tiles (x 0-4, y 5-9): seed buys on day 11 and every unit action on SW
strawberry tiles planted on day 11, over the rest of the game. One local game vs the given opponent.
    .venv\Scripts\python.exe gold\front\sw_trace.py AGENT OPP SEED"""
import sys, collections, json
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools')
import fastarena
if __name__ == '__main__':
    agent, opp, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
    f = fastarena.load_agent(agent); g = fastarena.load_agent(opp)
    EV = []
    SW = {(x, y) for x in range(5) for y in range(5, 10)}
    def wrap(obs, conf=None):
        a = f(obs, conf)
        t = int(obs['step']); d = t // 24
        if d < 10 or not isinstance(a, dict):
            return a
        farm = obs['farms'][0]
        pos = [tuple(farm['farmer'])] + [tuple(h) for h in farm.get('hands', [])]
        us = [a.get('farmer')] + list(a.get('hands') or [])
        for i, u in enumerate(us):
            if i < len(pos) and pos[i] in SW and isinstance(u, list) and u and u[0] in ('PLANT', 'WATER', 'HARVEST', 'FERTILIZE', 'DIG'):
                x, y = pos[i]; tile = farm['tiles'][y][x]
                crop = tile.get('crop') if isinstance(tile, dict) else (tile if isinstance(tile, str) else None)
                age = d - tile['planted_day'] if isinstance(tile, dict) and 'planted_day' in tile else None
                EV.append((t, d, t % 24, i, pos[i], u[0], u[1] if len(u) > 1 else '', crop, age))
        for o in a.get('market') or []:
            if isinstance(o, list) and len(o) >= 2 and o[0] in ('BUY_SEED', 'BUY_LAND') and d in (10, 11, 12):
                EV.append((t, d, t % 24, -1, None, o[0], o[1] if len(o) > 1 else '', o[2] if len(o) > 2 else '', None))
        return a
    r = fastarena.run_game(wrap, g, seed)
    print('rewards', r['rewards'])
    st = [e for e in EV if e[5] == 'PLANT' and e[6] == 'STRAWBERRY' and e[1] == 11]
    tiles = {e[4] for e in st}
    print('day-11 SW strawberry plantings:', [(e[2], e[3], e[4]) for e in st])
    print('day 10-12 seed/land buys:', [(e[1], e[2], e[5], e[6], e[7]) for e in EV if e[3] == -1])
    per = collections.defaultdict(list)
    for e in EV:
        if e[4] in tiles and e[3] >= 0:
            per[e[4]].append(f"d{e[1]}h{e[2]:02d}:{e[5][:4]}{'/' + str(e[8]) if e[8] is not None else ''}")
    for t, v in sorted(per.items()):
        print(t, ' '.join(v))
