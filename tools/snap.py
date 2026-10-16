"""Print farm layouts at given days for a game."""
import sys, json, io, contextlib
import fastarena
from kaggle_environments.envs.kaggriculture import kaggriculture as K

def tile_str(t):
    if t is None: return '.'
    if t == 'LOCKED': return '#'
    k = t.get('kind')
    if k == 'WEED': return 'x'
    if k == 'PLANT': return t['crop'][0].lower() if t['crop'] != 'STRAWBERRY' else 's'
    if 'animal' in t: return {'GOOSE':'G','COW':'C','SHEEP':'S'}[t['animal']]
    if k == 'COOP': return 'o'
    if k == 'PASTURE': return 'p'
    return '?'

a, b, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
days = [int(x) for x in sys.argv[4].split(',')] if len(sys.argv) > 4 else [2,5,8,12,16,20,24,28]
snaps = {}
orig = K._end_of_day
def eod(state, env, day):
    if day in days:
        farms = state[0].observation.farms
        snaps[day] = [[[tile_str(t) for t in row] for row in f['tiles']] for f in farms] + [[dict(state[i].observation.private['shed']) for i in range(2)], [f['money'] for f in farms], dict(state[0].observation.market['prices'])]
    return orig(state, env, day)
K._end_of_day = eod
r = fastarena.run_game(fastarena.load_agent(a), fastarena.load_agent(b), seed)
print('rewards', r['rewards'], 'shops', r['final_state'][0].observation.town['unlocked_shops'])
for d in sorted(snaps):
    f0, f1, sheds, money, prices = snaps[d]
    print(f'--- end of day {d}: money {money[0]:.0f} / {money[1]:.0f}; prices {prices}')
    for y in range(10):
        print('  ' + ' '.join(f0[y]) + '    ' + ' '.join(f1[y]))
    print('  shed0', {k:v for k,v in sheds[0].items() if v}, '\n  shed1', {k:v for k,v in sheds[1].items() if v})
