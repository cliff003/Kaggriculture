r"""Per-product revenue of CAND vs the kept opponent tape in harvested games of a lineage (CAND replaces the
other seat). Shows where CAND loses money relative to that opponent.
    .venv\Scripts\python.exe gold\front\prodcmp.py CAND.py LINEAGE [--max 20] [--workers 12]"""
import sys, glob, gzip, json, collections, multiprocessing as mp, os, statistics as st
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools'); sys.path.insert(0, 'gold/front')

def main():
    import gstat
    from seatswap import tape_file
    from daycmp import totals
    cand, lin = sys.argv[1], sys.argv[2]
    mx = int(sys.argv[sys.argv.index('--max') + 1]) if '--max' in sys.argv else 20
    cls = {x['name']: x for x in json.load(open('gold/front/classify.json', encoding='utf-8'))}
    teams = {k for k, v in cls.items() if v.get('lineage') == lin}
    recs = {}
    for p in glob.glob('gold/front/front_*.jsonl.gz'):
        for l in gzip.open(p, 'rt', encoding='utf-8'):
            if l.strip():
                r = json.loads(l); recs[r['id']] = r
    jobs, meta = [], []
    for r in recs.values():
        for s, t in enumerate(r['teams']):
            if t in teams and len(jobs) < mx and len(r.get('shops') or []) >= 8:
                me = 1 - s
                tape = tape_file(r, s)
                seats = (cand, tape) if me == 0 else (tape, cand)
                jobs.append((seats[0], seats[1], r['seed'], me, r['shops'])); meta.append((r, t, me))
    with mp.get_context('spawn').Pool(12, maxtasksperchild=1) as pool:
        out = list(pool.imap(gstat.play_one, jobs))
    agg = collections.defaultdict(list)
    wins = 0
    for (r, t, me), g in zip(meta, out):
        ra, ua, _ = totals(g['days'][me]); rb, ub, _ = totals(g['days'][1 - me])
        wins += g['rewards'][me] > g['rewards'][1 - me]
        for k in set(ra) | set(rb):
            agg[k].append((ra[k] - rb[k], ua[k], ub[k], ra[k] / max(1, ua[k]), rb[k] / max(1, ub[k])))
        agg['_money'].append((g['rewards'][me] - g['rewards'][1 - me], 0, 0, 0, 0))
    print(f"{cand} vs lineage {lin}: games {len(out)} wins {wins}")
    for k, v in sorted(agg.items(), key=lambda kv: st.mean(x[0] for x in kv[1])):
        print(f"  {k:12s} mean diff {st.mean(x[0] for x in v):+8.0f}  units us/them {st.mean(x[1] for x in v):6.0f}/{st.mean(x[2] for x in v):6.0f}  "
              f"avg price us/them {st.mean(x[3] for x in v):6.1f}/{st.mean(x[4] for x in v):6.1f}")

if __name__ == '__main__':
    main()
