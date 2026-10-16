import json, sys, collections
fn = sys.argv[1] if len(sys.argv) > 1 else 'results/rr.jsonl'
rows = [json.loads(l) for l in open(fn)]
name = lambda p: p.split('/')[1] if '/' in p else p
W = collections.Counter(); N = collections.Counter(); M = collections.defaultdict(float); R = collections.defaultdict(list)
H = collections.defaultdict(lambda: [0,0,0])
for r in rows:
    a, b = name(r['a']), name(r['b'])
    ra, rb = r['ra'] or 0, r['rb'] or 0
    R[a].append(ra); R[b].append(rb)
    for x, y, rx, ry in ((a, b, ra, rb), (b, a, rb, ra)):
        N[x] += 1
        M[x] += rx - ry
        if rx > ry: W[x] += 1; H[(x,y)][0] += 1
        elif rx == ry: W[x] += 0.5; H[(x,y)][2] += 1
        else: H[(x,y)][1] += 1
names = sorted(N, key=lambda x: -W[x] / N[x])
print(f"{'agent':28s} {'games':>5s} {'winrate':>7s} {'margin':>8s} {'mean$':>8s}")
for x in names:
    print(f"{x:28s} {N[x]:5d} {W[x]/N[x]:7.3f} {M[x]/N[x]:8.0f} {sum(R[x])/len(R[x]):8.0f}")
print()
print('head-to-head (row W/L/T vs col):')
print(' ' * 22 + ''.join(f'{c[:10]:>12s}' for c in names))
for x in names:
    print(f'{x[:22]:22s}' + ''.join(f"{'%d/%d/%d' % tuple(H[(x,y)]) if (x,y) in H else '-':>12s}" for y in names))
