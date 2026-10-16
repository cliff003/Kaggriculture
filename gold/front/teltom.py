import sys, collections
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools')
import gstat, fastarena
if __name__ == '__main__':
    cand, opp, base, seeds = sys.argv[1], sys.argv[2], sys.argv[3], [int(s) for s in sys.argv[4].split(',')]
    for seed in seeds:
        f = fastarena.load_agent(cand); g = fastarena.load_agent(opp)
        r = fastarena.run_game(f, g, seed)
        tel = f.__globals__.get('TEL')
        b = fastarena.load_agent(base); g2 = fastarena.load_agent(opp)
        r2 = fastarena.run_game(b, g2, seed)
        print(seed, 'cand', r['rewards'], 'base', r2['rewards'], 'margin change', (r['rewards'][0] - r['rewards'][1]) - (r2['rewards'][0] - r2['rewards'][1]), tel)
