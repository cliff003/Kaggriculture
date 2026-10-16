r"""Replay a live game exactly (both recorded tapes) and trace, for one seat, what its units do on tiles where it
planted CROP in a day range: the action sequence on each such tile for the next days.
    .venv\Scripts\python.exe gold\front\tiletrace.py GAME_ID SEAT_TEAM CROP D0 D1 [--n 6]"""
import sys, json, collections, argparse
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools'); sys.path.insert(0, 'gold/front')
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('gid', type=int); ap.add_argument('team'); ap.add_argument('crop'); ap.add_argument('d0', type=int); ap.add_argument('d1', type=int); ap.add_argument('--n', type=int, default=6)
    a = ap.parse_args()
    import fastarena, forceshops
    from cfroute import tape_file
    from tgrun import find_recs
    rec = find_recs([a.gid])[a.gid]
    seat = rec['teams'].index(a.team)
    forceshops.force(rec['shops'])
    fns = [fastarena.load_agent(tape_file(rec, 0)), fastarena.load_agent(tape_file(rec, 1))]
    LOG = collections.defaultdict(list)
    planted = {}
    def wrap(f, sidx):
        def g(obs, conf=None):
            act = f(obs, conf)
            if sidx == seat:
                s = int(obs['step']); farm = obs['farms'][sidx]
                pos = [tuple(farm['farmer'])] + [tuple(h) for h in farm['hands']]
                units = [act.get('farmer') or ['PASS']] + list(act.get('hands') or [])
                for i, p in enumerate(pos):
                    u = units[i] if i < len(units) else ['PASS']
                    if not (isinstance(u, list) and u):
                        continue
                    tile = farm['tiles'][p[1]][p[0]]
                    if u[0] == 'PLANT' and len(u) > 1 and u[1] == a.crop and a.d0 <= s // 24 <= a.d1:
                        planted[p] = s
                    if p in planted and s - planted[p] <= 5 * 24 and u[0] not in ('NORTH', 'SOUTH', 'EAST', 'WEST', 'PASS'):
                        age = s // 24 - planted[p] // 24
                        y = tile.get('yield_units') if isinstance(tile, dict) else None
                        LOG[(p, planted[p])].append(f"a{age}h{s % 24:02d}:{u[0]}{'' if len(u) < 2 else '-' + str(u[1])}(y{y})")
            return act
        return g
    r = fastarena.run_game(wrap(fns[0], 0), wrap(fns[1], 1), rec['seed'])
    print(rec['teams'], r['rewards'])
    for i, (k, v) in enumerate(sorted(LOG.items(), key=lambda kv: kv[0][1])):
        if i >= a.n:
            break
        print(k, ' '.join(v))
