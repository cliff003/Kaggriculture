"""Round-robin tournament among agents in agents/*/main.py"""
import itertools, json, multiprocessing as mp, sys, os, time, glob
from fastarena import play
import argparse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seeds', type=int, default=4)
    ap.add_argument('--seed0', type=int, default=2000)
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--agents', nargs='*', default=None)
    ap.add_argument('--out', default='results/rr.jsonl')
    ap.add_argument('--both', action='store_true')
    ap.add_argument('--vs', default=None, help='only play this agent against the others')
    ap.add_argument('--resume', action='store_true', help='skip games already in --out')
    ap.add_argument('--field', nargs='*', default=[], help='also play every agent against each of these; they do not play each other')
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
    agents = args.agents or sorted(glob.glob('agents/*/main.py'))
    pairs = []
    if args.vs:
        for a in agents:
            if a != args.vs:
                pairs.append((args.vs, a))
    else:
        pairs = list(itertools.combinations(agents, 2))
    pairs += [(a, f) for a in agents for f in args.field]
    jobs = []
    for (a, b) in pairs:
        for i in range(args.seeds):
            s = args.seed0 + i
            if args.both:
                jobs.append((a, b, s)); jobs.append((b, a, s))
            elif i % 2 == 0:
                jobs.append((a, b, s))
            else:
                jobs.append((b, a, s))
    if args.resume and os.path.exists(args.out):
        done = {(d['a'], d['b'], d['seed']) for d in map(json.loads, open(args.out))}
        jobs = [j for j in jobs if j not in done]
    print('jobs', len(jobs), flush=True)
    t0 = time.time()
    # Windows has no fork; spawn re-imports this file, hence the main() guard
    ctx = mp.get_context('spawn' if os.name == 'nt' else 'fork')
    with ctx.Pool(args.workers, maxtasksperchild=1) as pool, open(args.out, 'a') as f:
        for k, info in enumerate(pool.imap_unordered(play, jobs)):
            f.write(json.dumps(info) + '\n'); f.flush()
            if k % 10 == 0:
                print(k, f'{time.time()-t0:.0f}s', info['a'].split('/')[-2], info['ra'], info['b'].split('/')[-2], info['rb'], flush=True)
    print('done', time.time() - t0)


if __name__ == '__main__':
    main()
