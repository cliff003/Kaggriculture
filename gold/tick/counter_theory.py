r"""Per-cycle value of a counter trade against a slot-0 tick churner, from a live game's market inventory path.
For every churn cycle (rival buys N at s % 4 == 0, sells at s + 1): selling X after its buy at s and buying X back
after its sell at s + 1 earns sum_i p(I_s_after_buy + i) - sum_i p(I_s1_after_sell - X + i)."""
import sys, json, glob, gzip, math
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools')
from kaggle_environments.envs.kaggriculture import kaggriculture as K
def p(inv): return K.market_price('WHEAT', inv)
if __name__ == '__main__':
    gid, X = int(sys.argv[1]), int(sys.argv[2])
    rec = None
    for f in sorted(glob.glob('data/games/live_*.jsonl.gz')) + sorted(glob.glob('gold/front/front_*.jsonl.gz')):
        for line in gzip.open(f, 'rt', encoding='utf-8'):
            r = json.loads(line)
            if r['id'] == gid:
                rec = r; break
        if rec: break
    rival = int(sys.argv[3]) if len(sys.argv) > 3 else 1 - rec['teams'].index('42')
    acts = rec['acts'][rival]
    # reconstruct wheat inventory before each step's market with a local replay
    import fastarena, forceshops
    forceshops.force(rec['shops'])
    INV = {}
    orig = K._process_market
    def pm(state, env):
        INV[state[0].observation.step] = state[0].observation.market['inventory']['WHEAT']
        return orig(state, env)
    K._process_market = pm
    tapes = [[rec['acts'][s][t + 1] if t + 1 < len(rec['acts'][s]) else None for t in range(719)] for s in range(2)]
    def tape(seat):
        def f(obs, conf=None):
            a = tapes[seat][int(obs['step'])]
            return json.loads(json.dumps(a)) if isinstance(a, dict) else {"farmer": ["PASS"], "hands": [], "market": []}
        return f
    fastarena.run_game(tape(0), tape(1), rec['seed'])
    tot = 0; n = 0
    for t in range(24, 717):
        if t % 4: continue
        m = (acts[t + 1] if t + 1 < len(acts) else None) or {}
        b = [o for o in (m.get('market') or []) if isinstance(o, list) and len(o) >= 3 and o[0] == 'BUY_PRODUCT' and o[1] == 'WHEAT']
        m2 = (acts[t + 2] if t + 2 < len(acts) else None) or {}
        s = [o for o in (m2.get('market') or []) if isinstance(o, list) and len(o) >= 3 and o[0] == 'SELL' and o[1] == 'WHEAT']
        if not b or not s: continue
        N = int(b[0][2]); M = int(s[0][2])
        if N < 10: continue
        I0 = INV[t]            # before market at s
        after_buy = I0 - N     # rival buy at slot 0 (ignoring other orders)
        sell = sum(p(after_buy + i) for i in range(X))
        I1 = INV[t + 1]        # before market at s+1 (includes our X sold? no: local replay has no counter) -> add X
        I1c = I1 + X
        after_sell = I1c + M
        buy = sum(p(after_sell - 1 - i) for i in range(X))
        tot += sell - buy; n += 1
        if n <= 8 or n % 10 == 0: print(f"  s{t} I0 {I0} N {N} M {M} p(I0) {p(I0)} p(I0-N) {p(after_buy)} I1 {I1} p(I1) {p(I1)} sell {sell} buy {buy}")
    print(f"game {gid} rival {rec['teams'][rival]} cycles {n} X {X} counter value {tot:+.0f} ({tot / max(1, n):+.1f} per cycle)")
