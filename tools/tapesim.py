"""Fast tape-only simulator: both players replay herd route tapes (no agent layers)."""
import copy, io, contextlib, random, json
from kaggle_environments import make
from kaggle_environments.envs.kaggriculture import kaggriculture as K

_NS = None
def herd_ns(path='agents/herdsafe_race_statma/main.py'):
    global _NS
    if _NS is None:
        ns = {}
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(open(path).read(), path, 'exec'), ns)
        _NS = ns
    return _NS

def default_route(shops2, ns=None):
    ns = ns or herd_ns()
    shops = tuple(shops2)
    use_new = shops.count('YARN_STORE') <= 0
    r = ns['_R108_SHOP_ROUTES'].get(shops, 100) if use_new else ns['_R110_OLD_SHOPS'].get(shops, 0)
    r = ns['_V92_TABLE'].get(shops, r)
    return r

FORCED = {'shops': None}
_orig_eod = K._end_of_day
def _eod(state, env, day):
    _orig_eod(state, env, day)
    f = FORCED['shops']
    if f is not None:
        town = state[0].observation.town
        n = len(town['unlocked_shops'])
        town['unlocked_shops'] = list(f[:n])
K._end_of_day = _eod

def simulate(route_p0, route_p1, seed, shops=None, start_state=None, record=False):
    """route_pX: route id used from step 144 (before: opening tape, same for all routes).
    If shops given (list of 8), the town unlock sequence is forced."""
    ns = herd_ns()
    R = ns['_ROUTES']
    FORCED['shops'] = shops
    env = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': seed}, debug=False)
    env.reset(2)
    state = env.state
    routes = [route_p0, route_p1]
    for step in range(0, 719):
        for i in range(2):
            rid = routes[i]
            if step < 144:
                rid = route_p0 if i == 0 else route_p1  # all routes share opening; use own
            if step >= 648:
                rid = 2
            tape = R[rid]
            a = tape[step] if step < len(tape) else {'farmer': ['PASS'], 'hands': [], 'market': []}
            state[i].action = a
        with contextlib.redirect_stdout(io.StringIO()):
            K.interpreter(state, env)
        state[0].observation.step = step + 1
        if all(s.status != 'ACTIVE' for s in state):
            break
    FORCED['shops'] = None
    return [s.reward for s in state], state[0].observation.town['unlocked_shops']
