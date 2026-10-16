r"""Diagnose a strawberry-swap build in a live-game replay: swapped tiles' fate, strawberry production events,
animals unfed / escaped, feed pickups that failed, and the margin.
    .venv\Scripts\python.exe gold\front\ssdiag.py CAND.py GAME_ID"""
import sys, json, collections
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools'); sys.path.insert(0, 'gold/front')
if __name__ == '__main__':
    cand, gid = sys.argv[1], int(sys.argv[2])
    import fastarena, forceshops
    from cfroute import tape_file
    from tgrun import find_recs
    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    rec = find_recs([gid])[gid]; me = rec['teams'].index('42')
    C = collections.Counter(); CNT = {'f': 0, 'a': 0}
    orig_p, orig_a, orig_apply = K._daily_refresh_plants, K._daily_refresh_animals, K._apply_unit_action
    def rp(farm, day, tpd):
        CNT['f'] += 1
        if (CNT['f'] - 1) % 2 == me:
            for row in farm['tiles']:
                for t in row:
                    if isinstance(t, dict) and t.get('crop') == 'STRAWBERRY':
                        C['straw_tile_days'] += 1
                        if not t['watered_today'] and t['consecutive_unwatered'] >= 1:
                            C['straw_die'] += 1
        return orig_p(farm, day, tpd)
    def ra(farm, day):
        CNT['a'] += 1
        if (CNT['a'] - 1) % 2 == me:
            for row in farm['tiles']:
                for t in row:
                    if isinstance(t, dict) and 'animal' in t:
                        C['animal_days'] += 1
                        if not t['fed_today']:
                            C['unfed'] += 1
                            if t['consecutive_unfed'] >= 1:
                                C['escape'] += 1
        return orig_a(farm, day)
    K._daily_refresh_plants, K._daily_refresh_animals = rp, ra
    forceshops.force(rec['shops'])
    fns = [None, None]; fns[me] = fastarena.load_agent(cand); fns[1 - me] = fastarena.load_agent(tape_file(rec, 1 - me))
    r = fastarena.run_game(fns[0], fns[1], rec['seed'])
    print(gid, rec['teams'][1 - me], 'margin', r['rewards'][me] - r['rewards'][1 - me], dict(C))
