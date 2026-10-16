import os
"""Per-player profile of a local game (mirrors the in-browser replay profile)."""
import sys, io, contextlib, collections, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fastarena, forceshops
from kaggle_environments import make
from kaggle_environments.envs.kaggriculture import kaggriculture as K


def profile_game(a, b, seed, shops=None):
    forceshops.force(shops)
    fa, fb = fastarena.load_agent(a), fastarena.load_agent(b)
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.reset(2)
    state = env.state
    conf = fastarena._clone(dict(env.configuration))
    fns = [fa, fb]
    prof = [dict(land=[], hands=collections.defaultdict(int), animals={}, money={}, plant=collections.Counter(), seed=collections.Counter(),
                 sell=collections.Counter(), buyp=collections.Counter(), animBuy=collections.defaultdict(list), hires=0) for _ in range(2)]
    nq = [1, 1]
    nsteps = 1
    sink = io.StringIO()
    while True:
        o0 = state[0].observation
        step = getattr(o0, 'step', 0) or 0
        d = step // 24
        for i in range(2):
            obs = dict(state[i].observation)
            for k in fastarena.SHARED:
                if k in o0:
                    obs[k] = o0[k]
            obs = fastarena._clone(obs)
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                act = fastarena._call(fns[i], obs, fastarena._clone(conf))
            state[i].action = fastarena._clone(act) if act is not None else None
            if not isinstance(act, dict):
                continue
            P = prof[i]
            P['hands'][d] = max(P['hands'][d], len(act.get('hands') or []))
            for u in [act.get('farmer')] + list(act.get('hands') or []):
                if isinstance(u, list) and u and u[0] == 'PLANT':
                    P['plant'][u[1]] += 1
            for o in act.get('market') or []:
                if not (isinstance(o, list) and o):
                    continue
                if o[0] == 'SELL': P['sell'][o[1]] += int(o[2])
                elif o[0] == 'BUY_SEED': P['seed'][o[1]] += int(o[2])
                elif o[0] == 'BUY_PRODUCT': P['buyp'][o[1]] += int(o[2])
                elif o[0] == 'BUY_ANIMAL': P['animBuy'][o[1]].append(f'{d}x{o[2]}')
                elif o[0] == 'HIRE': P['hires'] += 1
        with contextlib.redirect_stdout(sink):
            K.interpreter(state, env)
        state[0].observation.step = nsteps
        k = nsteps
        nsteps += 1
        for i in range(2):
            f = state[0].observation.farms[i]
            q = len(f['unlocked_quadrants'])
            if q > nq[i]:
                prof[i]['land'].append(f'{(k - 1) // 24}:{(k - 1) % 24}')
                nq[i] = q
            if k % 24 == 0:
                dd = k // 24 - 1
                if dd in (4, 9, 14, 19, 24, 28):
                    prof[i]['money'][dd] = f['money']
                if dd in (7, 11, 15, 20, 25):
                    c = collections.Counter()
                    for row in f['tiles']:
                        for t in row:
                            if isinstance(t, dict):
                                key = t['crop'][:4] if t.get('kind') == 'PLANT' else (t['animal'][:4] if 'animal' in t else t['kind'][:4])
                                c[key] += 1
                    prof[i]['animals'][dd] = ','.join(f'{kk}{v}' for kk, v in c.items())
        if state[0].observation.step >= env.configuration.episodeSteps - 1:
            for st in state:
                if st.status in ("ACTIVE", "INACTIVE"):
                    st.status = "DONE"
        if all(st.status != "ACTIVE" for st in state):
            break
        sink.seek(0); sink.truncate(0)
    out = {'rewards': [st.reward for st in state], 'shops': list(state[0].observation.town['unlocked_shops']), 'p': []}
    for i in range(2):
        P = prof[i]
        P['hands'] = '/'.join(str(P['hands'].get(dd, 0)) for dd in (5, 8, 10, 12, 15, 20, 25, 29))
        P['animBuy'] = {t: ' '.join(v) for t, v in P['animBuy'].items()}
        for key in ('plant', 'seed', 'sell', 'buyp'):
            P[key] = dict(P[key])
        out['p'].append(P)
    return out


if __name__ == '__main__':
    shops = sys.argv[4].split(',') if len(sys.argv) > 4 else None
    print(json.dumps(profile_game(sys.argv[1], sys.argv[2], int(sys.argv[3]), shops)))
