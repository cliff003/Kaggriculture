"""Harvested top-agent tapes: loading, fidelity checks, tape agents, route-library agents."""
import gzip, json, io, sys, os, copy, contextlib, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fastarena

FAMILY_TEAMS = ('DSM', 'DECEM', 'Vadim Vasilenko')


def load_bundle(path):
    raw = open(path, 'rb').read()
    try:
        raw = gzip.decompress(raw)
    except OSError:
        pass
    data = json.loads(raw)
    games = data['games'] if isinstance(data, dict) and 'games' in data else data
    return games


def tape_of(game, side):
    """Agent-indexed tape: action returned at observation step t = acts[side][t+1]."""
    acts = game['acts'][side]
    return [a if isinstance(a, dict) else {"farmer": ["PASS"], "hands": [], "market": []} for a in acts[1:]]


def pure_tape_agent(tape):
    def agent(obs, conf=None):
        t = int(obs['step']) if 'step' in obs else int(getattr(obs, 'step', 0))
        if 0 <= t < len(tape):
            return copy.deepcopy(tape[t])
        return {"farmer": ["PASS"], "hands": [], "market": []}
    return agent


def fidelity(game):
    a = pure_tape_agent(tape_of(game, 0))
    b = pure_tape_agent(tape_of(game, 1))
    r = fastarena.run_game(a, b, game['seed'])
    shops = list(r['final_state'][0].observation.town['unlocked_shops'])
    return {'id': game['id'], 'server': game['rewards'], 'local': r['rewards'],
            'shops_match': shops == list(game['shops']), 'status': r['status']}


_RESCUE_NS = {}


def rescue_ns():
    if not _RESCUE_NS:
        src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'submissions', 'v3_public_rescue_verbatim', 'main.py')).read()
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(src, 'rescue_main.py', 'exec'), _RESCUE_NS)
    return _RESCUE_NS


def library_agent(opening, routes_by_pair, fallback_pair=None, settings=None, switch_step=144):
    """Chassis replaying `opening` until switch_step, then the route for the first two shops."""
    ns = rescue_ns()
    routes = {0: opening}
    pair_to_id = {}
    for i, (pair, tape) in enumerate(routes_by_pair.items(), start=1):
        routes[i] = tape
        pair_to_id[tuple(pair)] = i
    fb = pair_to_id.get(tuple(fallback_pair)) if fallback_pair else None

    def router(observation, step, state):
        if step >= switch_step and not state.get('chosen'):
            town = observation['town'] if 'town' in observation else getattr(observation, 'town', {})
            shops = tuple((town['unlocked_shops'] if 'unlocked_shops' in town else [])[:2])
            state['route'] = pair_to_id.get(shops, fb if fb is not None else 0)
            state['chosen'] = True
        return state.get('route', 0)

    st = dict(ns['_SETTINGS'])
    if settings:
        st.update(settings)
    agent = ns['make_agent'](routes, router=router, **st)
    return agent


def pure_router_agent(opening, routes_by_pair, fallback=None, switch_step=144):
    """No chassis: replay opening, then the raw tape chosen by the first two shops."""
    pair_to_tape = {tuple(p): t for p, t in routes_by_pair.items()}
    state = {}

    def agent(obs, conf=None):
        t = int(obs['step'])
        me = int(obs['player'])
        st = state.setdefault(me, {})
        if t == 0:
            st.clear()
        if t >= switch_step and 'tape' not in st:
            shops = tuple(obs['town']['unlocked_shops'][:2])
            st['tape'] = pair_to_tape.get(shops, fallback if fallback is not None else opening)
        tape = st.get('tape', opening)
        if 0 <= t < len(tape):
            a = copy.deepcopy(tape[t])
            # align hands to the real number of hands
            n = len(obs['farms'][me]['hands'])
            hands = list(a.get('hands') or [])
            hands += [["PASS"]] * max(0, n - len(hands))
            a['hands'] = hands[:n]
            return a
        return {"farmer": ["PASS"], "hands": [], "market": []}
    return agent


def family_tapes(games, teams=FAMILY_TEAMS):
    """[(game, side, tape)] for family players."""
    out = []
    for g in games:
        for side in (0, 1):
            if g['teams'][side] in teams and g['acts'][side] is not None:
                out.append((g, side, tape_of(g, side)))
    return out


def same_prefix(t1, t2, n=144):
    return all(json.dumps(t1[i], sort_keys=True) == json.dumps(t2[i], sort_keys=True) for i in range(n))
