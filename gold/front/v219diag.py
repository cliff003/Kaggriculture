r"""Why did (or didn't) the base's V219 tomato expansion fire: our money, shops and orders around day 18 h0-h6.
    .venv\Scripts\python.exe gold\front\v219diag.py CAND.py GAME_ID [--from 426] [--to 440]"""
import sys, json, argparse
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools'); sys.path.insert(0, 'gold/front')
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cand'); ap.add_argument('gid', type=int)
    ap.add_argument('--from_step', type=int, default=426); ap.add_argument('--to_step', type=int, default=440)
    a = ap.parse_args()
    import fastarena, forceshops
    from cfroute import tape_file
    from tgrun import find_recs
    rec = find_recs([a.gid])[a.gid]
    me = rec['teams'].index('42')
    forceshops.force(rec['shops'])
    ours = fastarena.load_agent(a.cand)
    LOG = []
    def wrapped(obs, conf=None):
        act = ours(obs, conf)
        s = int(obs['step'])
        if a.from_step <= s <= a.to_step:
            f = obs['farms'][obs['player']]
            shops = obs['town']['unlocked_shops']
            LOG.append((s, round(f['money']), f['unlocked_quadrants'], obs['market']['prices']['TOMATO'],
                        sum(x in ('PIZZA_SHOP', 'FARMERS_MARKET') for x in shops),
                        obs['private']['shed'].get('WHEAT', 0), [o for o in act.get('market', []) if o]))
        return act
    fns = [None, None]; fns[me] = wrapped; fns[1 - me] = fastarena.load_agent(tape_file(rec, 1 - me))
    r = fastarena.run_game(fns[0], fns[1], rec['seed'])
    for row in LOG:
        print(f"s{row[0]} d{row[0]//24}h{row[0]%24:02d} money {row[1]:6d} quads {row[2]} tomato {row[3]} pizza+fm {row[4]} shed wheat {row[5]} orders {row[6]}")
    print('margin', r['rewards'][me] - r['rewards'][1 - me])
