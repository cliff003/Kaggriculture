r"""Care schedule of late wheat plantings (day >= D) for seat 0 in one local game: per planted tile, the ages at which
the unit actions WATER / FERTILIZE / HARVEST happen, and the harvested units.
    .venv\Scripts\python.exe gold\front\wheat_trace.py AGENT OPP SEED [D]"""
import sys, collections, json
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools')
import fastarena
if __name__ == '__main__':
    agent, opp, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
    D = int(sys.argv[4]) if len(sys.argv) > 4 else 20
    f = fastarena.load_agent(agent); g = fastarena.load_agent(opp)
    plots = {}
    hist = collections.defaultdict(list)
    def wrap(obs, conf=None):
        a = f(obs, conf)
        t = int(obs['step']); d = t // 24
        farm = obs['farms'][0]
        pos = [tuple(farm['farmer'])] + [tuple(h) for h in farm.get('hands', [])]
        us = [a.get('farmer')] + list(a.get('hands') or [])
        for i, u in enumerate(us):
            if i >= len(pos) or not isinstance(u, list) or not u:
                continue
            x, y = pos[i]; tile = farm['tiles'][y][x]
            if u[0] == 'PLANT' and len(u) > 1 and u[1] == 'WHEAT' and d >= D and tile is None:
                plots[(x, y, d)] = t
                hist[(x, y, d)].append(f"h{t % 24:02d}:PLANT")
            elif u[0] in ('WATER', 'FERTILIZE', 'HARVEST') and isinstance(tile, dict) and tile.get('crop') == 'WHEAT':
                key = (x, y, tile['planted_day'])
                if key in plots:
                    age = d - tile['planted_day']
                    extra = f"({tile.get('yield_units')})" if u[0] == 'HARVEST' else ''
                    hist[key].append(f"a{age}h{t % 24:02d}:{u[0][:4]}{extra}")
        return a
    fastarena.run_game(wrap, g, seed)
    pat = collections.Counter()
    for k, v in sorted(hist.items()):
        s = ' '.join(x.split(':')[1] if x.startswith('h') else x.split('h')[0] + ':' + x.split(':')[1] for x in v)
        pat[s] += 1
    for s, c in pat.most_common(12):
        print(c, s)
    print('late wheat plantings', len(plots))
