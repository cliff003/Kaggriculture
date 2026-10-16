"""Paired reactive-game cash decomposition for a fixed shop world."""
import argparse
import collections
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))


def game(path, rival, seed, shops, seat):
    import econ
    import fastarena
    import forceshops

    forceshops.force(shops)
    mine = fastarena.load_agent(str(path))
    theirs = fastarena.load_agent(str(ROOT / 'research/panel' / rival / 'main.py'))
    fns = [mine, theirs] if seat == 0 else [theirs, mine]
    K = econ.K
    orig = K.interpreter

    def interpreter(state, env):
        obs = state[0].observation
        if getattr(obs, 'farms', None) and econ._CUR.get('_env') is not env:
            econ._CUR.update(log=[], farms=obs.farms, _env=env,
                             privates=[s.observation.private for s in state],
                             prices=obs.market['prices'])
        return orig(state, env)

    def spy(fn):
        def wrapped(obs, conf=None):
            econ._CUR['step'] = int(obs['step'])
            return fn(obs, conf)
        return wrapped

    K.interpreter = interpreter
    econ._CUR.clear()
    try:
        res = fastarena.run_game(spy(fns[0]), spy(fns[1]), seed)
    finally:
        K.interpreter = orig
    assert res['status'] == ['DONE', 'DONE'] and not any(res['errors'])
    cash = collections.Counter()
    counts = collections.Counter()
    daily = collections.Counter()
    for step, player, op, item, price in econ._CUR['log']:
        if player != seat:
            continue
        key = 'HIRE' if op == 'HIRE' else 'LAND' if op == 'LAND' else item
        sign = 1 if op == 'SELL' else -1
        cash[key] += sign * price
        counts[(op, item)] += 1
        daily[(step // 24, key)] += sign * price
    return {'reward': res['rewards'][seat], 'margin': res['rewards'][seat]-res['rewards'][1-seat],
            'cash': dict(cash), 'counts': {str(k): v for k,v in counts.items()},
            'daily': {str(k): v for k,v in daily.items()}}


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--seed', type=int, default=2026092921)
    a.add_argument('--rival', default='emu_antifade')
    a.add_argument('--candidate', type=Path, default=ROOT / 'research/live_0929/prototypes/crew4_full/main.py')
    args = a.parse_args()
    worlds = json.loads((ROOT / 'research/live_0929/tomato_panel_metadata.json').read_text())['worlds']
    seed, shops, seat = next(w for w in worlds if w[0] == args.seed)
    base = game(ROOT / 'submissions/V12_AventadorSVJ/main.py', args.rival, seed, shops, seat)
    cand = game(args.candidate, args.rival, seed, shops, seat)
    print('seed', seed, 'rival', args.rival, 'seat', seat, 'shops', ','.join(shops))
    print('reward/margin', base['reward'], base['margin'], '->', cand['reward'], cand['margin'])
    for key in sorted(set(base['cash']) | set(cand['cash'])):
        b, c = base['cash'].get(key, 0), cand['cash'].get(key, 0)
        if b != c:
            print('cash', key, b, c, c-b)
    for key in sorted(set(base['counts']) | set(cand['counts'])):
        b, c = base['counts'].get(key, 0), cand['counts'].get(key, 0)
        if b != c:
            print('count', key, b, c, c-b)
    for key in sorted(set(base['daily']) | set(cand['daily'])):
        b, c = base['daily'].get(key, 0), cand['daily'].get(key, 0)
        if b != c and key.startswith(('(23,', '(24,', '(25,', '(26,', '(27,', '(28,', '(29,')):
            print('daily', key, b, c, c-b)


if __name__ == '__main__':
    main()
