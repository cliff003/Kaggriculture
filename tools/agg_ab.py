import json, collections, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
agg = collections.defaultdict(lambda: [0, 0, 0, 0.0, 0])
for d in rows:
    key = (d['cand'].split('/')[-2], d['opp'].split('/')[-2])
    a = agg[key]
    if d['me'] > d['op']: a[0] += 1
    elif d['me'] < d['op']: a[1] += 1
    else: a[2] += 1
    a[3] += d['me'] - d['op']; a[4] += 1
    if d['status'] != ['DONE', 'DONE']: print('BAD STATUS', d)
tot = collections.defaultdict(lambda: [0.0, 0])
for (c, o), (w, l, t, m, n) in sorted(agg.items()):
    print(f'{c:22s} vs {o:22s} W/L/T {w}/{l}/{t}  pts {(w+0.5*t)/n:.3f}  margin {m/n:8.0f}  n={n}')
    tot[c][0] += w + 0.5 * t; tot[c][1] += n
for c, (p, n) in tot.items():
    print(f'{c:22s} overall {p/n:.3f} (n={n})')
