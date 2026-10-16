r"""Opponents' WHEAT / FERTILIZER market orders in harvested games: volume, hour-of-day pattern, slot.
    .venv\Scripts\python.exe gold\front\opptrade.py FILE.jsonl.gz [--team 42] [--min 200]"""
import sys, gzip, json, collections, argparse
ap = argparse.ArgumentParser(); ap.add_argument('file'); ap.add_argument('--team', default='42'); ap.add_argument('--min', type=int, default=200)
a = ap.parse_args()
rows = []
for l in gzip.open(a.file, 'rt', encoding='utf-8'):
    if not l.strip():
        continue
    r = json.loads(l)
    if a.team not in r['teams']:
        continue
    me = r['teams'].index(a.team); op = 1 - me
    acts = r['acts'][op]
    st = collections.Counter(); hrs = collections.defaultdict(collections.Counter); slots = collections.defaultdict(list); big = collections.defaultdict(list)
    for t in range(1, len(acts)):
        s = t - 1
        m = (acts[t] or {}).get('market') or []
        for i, o in enumerate(m):
            if not o or len(o) < 3 or o[1] not in ('WHEAT', 'FERTILIZER') or o[0] not in ('BUY_PRODUCT', 'SELL'):
                continue
            try:
                q = int(o[2])
            except Exception:
                continue
            if q <= 0:
                continue
            k = ('B' if o[0] == 'BUY_PRODUCT' else 'S') + o[1][0]
            st[k] += q; hrs[k][s % 24] += q; slots[k].append(i)
            if q >= 20 and s >= 240:
                big[k].append((s, i, q))
    margin = r['rewards'][me] - r['rewards'][op]
    rows.append((r['id'], r['teams'][op], margin, st, hrs, slots, big))
print(f"{'id':>10s} {'opp':20s} {'margin':>7s} {'BW':>5s} {'SW':>5s} {'BF':>5s} {'SF':>5s}  top buy-fert hours / big fert buys (step,slot,qty)")
for rid, name, margin, st, hrs, slots, big in sorted(rows, key=lambda x: x[2]):
    if st['BF'] + st['BW'] < a.min:
        continue
    th = ' '.join(f"h{h}:{q}" for h, q in hrs['BF'].most_common(4))
    bb = ' '.join(f"{s}/{i}/{q}" for s, i, q in big['BF'][:8])
    print(f"{rid:>10d} {name[:20]:20s} {margin:+7.0f} {st['BW']:5d} {st['SW']:5d} {st['BF']:5d} {st['SF']:5d}  {th} | {bb}")
