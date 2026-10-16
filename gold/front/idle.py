r"""Idle labor of one seat in a local game: per day, unit-steps by action kind (PASS, moves, tile work, shed work),
and PASS steps by hour and by unit position (quadrant).
    .venv\Scripts\python.exe gold\front\idle.py AGENT.py OPP.py SEED [--seat 0]"""
import sys, collections, argparse
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools')
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('agent'); ap.add_argument('opp'); ap.add_argument('seed', type=int); ap.add_argument('--seat', type=int, default=0)
    a = ap.parse_args()
    import fastarena
    f = fastarena.load_agent(a.agent); g = fastarena.load_agent(a.opp)
    K = collections.defaultdict(collections.Counter)
    PQ = collections.Counter(); PH = collections.Counter()
    def wrap(obs, conf=None):
        act = f(obs, conf)
        s = int(obs['step']); d = s // 24
        farm = obs['farms'][obs['player']]
        pos = [tuple(farm['farmer'])] + [tuple(h) for h in farm['hands']]
        units = [act.get('farmer') or ['PASS']] + list(act.get('hands') or [])
        for i, p in enumerate(pos):
            u = units[i] if i < len(units) else ['PASS']
            op = u[0] if isinstance(u, list) and u else 'PASS'
            kind = 'PASS' if op == 'PASS' else ('MOVE' if op in ('NORTH', 'SOUTH', 'EAST', 'WEST') else ('SHED' if op in ('DROP', 'PICKUP', 'PLACE') else 'WORK'))
            K[d][kind] += 1
            if kind == 'PASS':
                q = ('N' if p[1] < 5 else 'S') + ('W' if p[0] < 5 else 'E')
                PQ[q] += 1; PH[s % 24] += 1
        return act
    fns = [wrap, g] if a.seat == 0 else [g, wrap]
    r = fastarena.run_game(fns[0], fns[1], a.seed)
    print('rewards', r['rewards'])
    for d in range(30):
        c = K[d]; tot = sum(c.values())
        print(f"d{d:2d} units-steps {tot:4d}  PASS {c['PASS']:4d}  MOVE {c['MOVE']:4d}  WORK {c['WORK']:4d}  SHED {c['SHED']:3d}")
    print('PASS by quadrant', PQ.most_common())
    print('PASS by hour', sorted(PH.items()))
