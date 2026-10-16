"""A/B evaluation: candidate vs panel, and baseline vs panel, same seeds, alternating seats."""
import sys, json, multiprocessing as mp, collections
import fastarena
def job(args):
    cand, opp, seed, seat = args
    fa, fb = fastarena.load_agent(cand), fastarena.load_agent(opp)
    if seat == 0:
        r = fastarena.run_game(fa, fb, seed); me, op = r['rewards'][0], r['rewards'][1]
    else:
        r = fastarena.run_game(fb, fa, seed); me, op = r['rewards'][1], r['rewards'][0]
    return {'cand': cand, 'opp': opp, 'seed': seed, 'seat': seat, 'me': me, 'op': op,
            'shops': r['final_state'][0].observation.town['unlocked_shops'][:2], 'status': r['status']}
if __name__ == '__main__':
    cands = sys.argv[1].split(',')
    opps = sys.argv[2].split(',')
    seeds = list(range(int(sys.argv[3]), int(sys.argv[3]) + int(sys.argv[4])))
    out = sys.argv[5]
    jobs = []
    for c in cands:
        for o in opps:
            for i, s in enumerate(seeds):
                jobs.append((c, o, s, i % 2))
    with mp.get_context('fork').Pool(2, maxtasksperchild=4) as p, open(out, 'a') as f:
        for k, d in enumerate(p.imap_unordered(job, jobs)):
            f.write(json.dumps(d) + '\n'); f.flush()
    rows = [json.loads(l) for l in open(out)]
    agg = collections.defaultdict(lambda: [0, 0, 0, 0.0])
    for d in rows:
        key = (d['cand'].split('/')[-2], d['opp'].split('/')[-2])
        a = agg[key]
        if d['me'] > d['op']: a[0] += 1
        elif d['me'] < d['op']: a[1] += 1
        else: a[2] += 1
        a[3] += d['me'] - d['op']
    for (c, o), (w, l, t, m) in sorted(agg.items()):
        n = w + l + t
        print(f'{c:22s} vs {o:22s} W/L/T {w}/{l}/{t}  pts {(w+0.5*t)/n:.3f}  margin {m/n:8.0f}')
