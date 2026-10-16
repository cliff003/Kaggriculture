r"""For one live game, list both sides' SELL orders for the given items per step (with slot index) and the executed
units and prices (exact replay with an engine hook), to see who wins same-step races.
    .venv\Scripts\python.exe gold\front\racecmp.py GAME_ID ITEM[,ITEM] [FILE]"""
import sys, gzip, json, collections, glob
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools'); sys.path.insert(0, 'gold/front')
import fastarena, forceshops
from kaggle_environments.envs.kaggriculture import kaggriculture as K
if __name__ == '__main__':
    gid, items = int(sys.argv[1]), set(sys.argv[2].split(','))
    files = [sys.argv[3]] if len(sys.argv) > 3 else glob.glob('gold/front/*.jsonl.gz') + glob.glob('data/games/live_*.jsonl.gz')
    rec = None
    for f in files:
        for l in gzip.open(f, 'rt', encoding='utf-8'):
            if l.strip():
                r = json.loads(l)
                if r['id'] == gid: rec = r; break
        if rec: break
    me = rec['teams'].index('42')
    forceshops.force(rec['shops'])
    LOG = collections.defaultdict(list)
    CUR = {}
    orig_pm, orig_cu = K._process_market, K._commit_unit
    def pm(state, env):
        CUR['step'] = state[0].observation.step; CUR['farms'] = state[0].observation.farms
        return orig_pm(state, env)
    def cu(op, item, price, farm, private, market, shed_capacity=100):
        ok = orig_cu(op, item, price, farm, private, market, shed_capacity)
        if ok and op == 'SELL' and item in items:
            pid = [i for i, f in enumerate(CUR['farms']) if f is farm][0]
            LOG[(CUR['step'], pid)].append(price)
        return ok
    K._process_market = pm; K._commit_unit = cu
    tapes = [[rec['acts'][s][t + 1] if t + 1 < len(rec['acts'][s]) else None for t in range(719)] for s in range(2)]
    PASS = {"farmer": ["PASS"], "hands": [], "market": []}
    def tape(seat):
        def f(obs, conf=None):
            a = tapes[seat][int(obs['step'])]
            return json.loads(json.dumps(a)) if isinstance(a, dict) else dict(PASS)
        return f
    fastarena.run_game(tape(0), tape(1), rec['seed'])
    tot = collections.Counter(); won = collections.Counter()
    for t in range(719):
        rows = []
        for s in range(2):
            m = (tapes[s][t] or {}).get('market') or []
            sl = [(i, o[1], o[2]) for i, o in enumerate(m) if isinstance(o, list) and len(o) >= 3 and o[0] == 'SELL' and o[1] in items]
            ex = LOG.get((t, s), [])
            if sl or ex:
                rows.append((('US ' if s == me else 'OPP'), sl, len(ex), round(sum(ex) / max(1, len(ex)), 1)))
                tot[('US' if s == me else 'OPP')] += sum(ex)
        if len(rows) == 2 and t >= 240:
            print(f"s{t} d{t // 24}h{t % 24:02d}", rows)
    print('totals', dict(tot))
