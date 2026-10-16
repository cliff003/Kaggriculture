"""Trace per-day sales and prices of a game."""
import sys, collections
import analyze2  # installs instrumentation
from analyze2 import LOG
import fastarena
from kaggle_environments.envs.kaggriculture import kaggriculture as K

a, b, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
items = sys.argv[4].split(',') if len(sys.argv) > 4 else ['STRAWBERRY','WOOL','MILK','FERTILIZER','MELON','WHEAT','CARROT','EGG','TOMATO']
LOG.clear()
prices = []
orig = K._town_consume
def tc(env, state, step):
    r = orig(env, state, step)
    prices.append(dict(state[0].observation.market['prices']))
    return r
K._town_consume = tc
r = fastarena.run_game(fastarena.load_agent(a), fastarena.load_agent(b), seed)
fid = [id(f) for f in r['final_state'][0].observation.farms]
print('rewards', r['rewards'], r['final_state'][0].observation.town['unlocked_shops'])
for item in items:
    per = collections.defaultdict(lambda: [0,0,0.0,0.0])
    turns = collections.defaultdict(lambda: [set(), set()])
    for kind, step, f, op, it, price in LOG:
        if kind=='M' and op=='SELL' and it==item:
            p = fid.index(f)
            d = step//24
            per[d][p] += 1; per[d][2+p] += price
            turns[d][p].add(step%24)
    if not per: continue
    print(f'== {item}')
    for d in sorted(per):
        n0,n1,v0,v1 = per[d]
        pr = prices[min(len(prices)-1, d*24+23)][item]
        print(f'  day {d:2d}: P0 {n0:3d} u avg {v0/max(1,n0):6.1f} hrs {sorted(turns[d][0])} | P1 {n1:3d} u avg {v1/max(1,n1):6.1f} hrs {sorted(turns[d][1])} | eod price {pr}')
