r"""Strawberry market signals at given days in live-game replays (our seat = CAND): quote, inventory, and the number
of strawberry-demand shops unlocked; plus the rival's strawberry sales so far.
    .venv\Scripts\python.exe gold\front\straw_signal.py CAND.py ID [ID ...]"""
import sys, json, collections, multiprocessing as mp, os
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools'); sys.path.insert(0, 'gold/front')
DEM = ('BRUNCH_SPOT', 'ICE_CREAM_SHOP', 'SMOOTHIE_SHOP', 'FARMERS_MARKET')
def play(job):
    cand, path = job
    import fastarena, forceshops
    from cfroute import tape_file
    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    rec = json.load(open(path, encoding='utf-8')); me = rec['teams'].index('42')
    snap = {}; CUR = {}; sold = collections.Counter()
    orig_pm, orig_cu = K._process_market, K._commit_unit
    def pm(state, env):
        s = state[0].observation.step; CUR['farms'] = state[0].observation.farms; CUR['s'] = s
        if s % 24 == 0:
            m = state[0].observation.market
            shops = state[0].observation.town['unlocked_shops']
            snap[s // 24] = (m['prices']['STRAWBERRY'], m['inventory']['STRAWBERRY'], sum(x in DEM for x in shops), sold[1 - me], sold[me])
        return orig_pm(state, env)
    def cu(op, item, price, farm, private, market, shed_capacity=100):
        ok = orig_cu(op, item, price, farm, private, market, shed_capacity)
        if ok and op == 'SELL' and item == 'STRAWBERRY':
            seat = [i for i, f in enumerate(CUR['farms']) if f is farm][0]
            sold[seat] += 1
        return ok
    K._process_market, K._commit_unit = pm, cu
    forceshops.force(rec['shops'])
    fns = [None, None]; fns[me] = fastarena.load_agent(cand); fns[1 - me] = fastarena.load_agent(tape_file(rec, 1 - me))
    fastarena.run_game(fns[0], fns[1], rec['seed'])
    return rec['id'], rec['teams'][1 - me], snap
if __name__ == '__main__':
    from tgrun import find_recs
    cand = os.path.abspath(sys.argv[1]); recs = find_recs(sys.argv[2:])
    jobs = []
    for rid, r in recs.items():
        p = f'gold/tmp/tgrun/{rid}.json'; json.dump(r, open(p, 'w', encoding='utf-8')); jobs.append((cand, p))
    with mp.get_context('spawn').Pool(min(12, len(jobs)), maxtasksperchild=1) as pool:
        out = list(pool.imap(play, jobs))
    for rid, opp, snap in out:
        cells = ' '.join(f"d{d}:{snap[d][0]}/{snap[d][1]-10000:+d}/s{snap[d][2]}/r{snap[d][3]}" for d in (9, 11, 13, 16, 20) if d in snap)
        print(rid, opp[:16], cells)
