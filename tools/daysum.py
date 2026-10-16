import os
"""Day-level economic summary of a local game (mirrors the in-browser replay summary).

python research/daysum.py A.py B.py SEED
"""
import sys, json, io, contextlib, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fastarena
from kaggle_environments import make
from kaggle_environments.envs.kaggriculture import kaggriculture as K


def tiles_count(farm):
    c = collections.Counter()
    for row in farm['tiles']:
        for t in row:
            if t is None or t == 'LOCKED':
                continue
            if isinstance(t, dict):
                if t.get('kind') == 'PLANT':
                    c['P:' + t['crop']] += 1
                elif 'animal' in t:
                    c['A:' + t['animal']] += 1
                else:
                    c[t.get('kind')] += 1
            else:
                c[str(t)] += 1
    return c


def run(a, b, seed, verbose=True):
    fa, fb = fastarena.load_agent(a), fastarena.load_agent(b)
    cfg = {"episodeSteps": 720, "seed": seed}
    env = make("kaggriculture", configuration=cfg, debug=False)
    env.reset(2)
    state = env.state
    conf = fastarena._clone(dict(env.configuration))
    fns = [fa, fb]
    days = [[dict(hands=0, hires=0, land=0, sells=collections.Counter(), buys=collections.Counter()) for _ in range(30)] for _ in range(2)]
    snaps = [[None] * 30 for _ in range(2)]
    nsteps = 1
    sink = io.StringIO()
    while True:
        o0 = state[0].observation
        step = o0.step if hasattr(o0, 'step') else 0
        d = min(29, step // 24)
        actions = []
        for i in range(2):
            obs = dict(state[i].observation)
            for k in fastarena.SHARED:
                if k in o0:
                    obs[k] = o0[k]
            obs = fastarena._clone(obs)
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                act = fastarena._call(fns[i], obs, fastarena._clone(conf))
            actions.append(act)
            state[i].action = fastarena._clone(act) if act is not None else None
            if isinstance(act, dict):
                days[i][d]['hands'] = max(days[i][d]['hands'], len(act.get('hands') or []))
                for o in act.get('market') or []:
                    if not (isinstance(o, list) and o):
                        continue
                    if o[0] == 'HIRE':
                        days[i][d]['hires'] += 1
                    elif o[0] == 'BUY_LAND':
                        days[i][d]['land'] += 1
                    elif o[0] == 'SELL':
                        days[i][d]['sells'][o[1]] += int(o[2])
                    else:
                        days[i][d]['buys'][o[0].replace('BUY_', '') + ':' + o[1]] += int(o[2])
        with contextlib.redirect_stdout(sink):
            K.interpreter(state, env)
        state[0].observation.step = nsteps
        nsteps += 1
        if (nsteps - 1) % 24 == 0:
            dd = (nsteps - 2) // 24
            for i in range(2):
                f = state[0].observation.farms[i]
                snaps[i][dd] = dict(money=f['money'], quads=''.join(f['unlocked_quadrants']), tiles=tiles_count(f),
                                    shed=sum(state[i].observation.private['shed'].values()))
        if state[0].observation.step >= env.configuration.episodeSteps - 1:
            for st in state:
                if st.status in ("ACTIVE", "INACTIVE"):
                    st.status = "DONE"
        if all(st.status != "ACTIVE" for st in state):
            break
        sink.seek(0); sink.truncate(0)
    rewards = [st.reward for st in state]
    shops = list(state[0].observation.town['unlocked_shops'])
    out = []
    for i in range(2):
        rows = []
        for dd in range(30):
            s = snaps[i][dd] or {}
            x = days[i][dd]
            tiles = ','.join(f"{k.split(':')[-1][:4]}{v}" for k, v in (s.get('tiles') or {}).items())
            sells = ','.join(f"{k[:4]}{v}" for k, v in x['sells'].items())
            buys = ','.join(f"{k[:12]}{v}" for k, v in x['buys'].items())
            rows.append(f"{dd}|${s.get('money')}|{s.get('quads')}|h{x['hands']}/{x['hires']}|L{x['land']}|{tiles}|S:{sells}|B:{buys}|shed{s.get('shed')}")
        out.append(rows)
    if verbose:
        print('shops', shops, 'rewards', rewards)
        for i in range(2):
            print(f'--- P{i} {[a, b][i]}')
            print('\n'.join(out[i]))
    return rewards, shops, out


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2], int(sys.argv[3]))
