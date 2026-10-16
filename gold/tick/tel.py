import sys, json, time
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools')
import fastarena
if __name__ == '__main__':
    cand, opp, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
    base = sys.argv[4] if len(sys.argv) > 4 else None
    f = fastarena.load_agent(cand)
    g = fastarena.load_agent(opp)
    r = fastarena.run_game(f, g, seed)
    tel = f.__globals__.get('TEL')
    print('cand', r['rewards'], tel)
    if base:
        b = fastarena.load_agent(base)
        g2 = fastarena.load_agent(opp)
        r2 = fastarena.run_game(b, g2, seed)
        print('base', r2['rewards'], 'margin change', (r['rewards'][0] - r['rewards'][1]) - (r2['rewards'][0] - r2['rewards'][1]))
