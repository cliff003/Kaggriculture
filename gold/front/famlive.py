r"""Our live games against cha22-family opponents (same opening unit tape): per-product revenue of both sides from
exact local replays, so the money gap can be traced to products (same production base, different layers).
    .venv\Scripts\python.exe gold\front\famlive.py [--files data/games/live_v7b.jsonl.gz ...] [--subs 56573604 ...]"""
import sys, glob, gzip, json, collections, multiprocessing as mp, statistics as st, os
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools'); sys.path.insert(0, 'gold/front')

def sig(acts, T=12):
    out = []
    for t in range(1, T + 1):
        a = (acts[t] if t < len(acts) else None) or {}
        u = [a.get('farmer')] + list(a.get('hands') or [])
        out.append('|'.join(str(x[0] if isinstance(x, list) and x else x) for x in u))
    return ' / '.join(out)

def main():
    import gstat
    from seatswap import tape_file
    from daycmp import totals
    files = sys.argv[sys.argv.index('--files') + 1:] if '--files' in sys.argv else sorted(glob.glob('data/games/live_v7*.jsonl.gz')) + ['data/games/live_v8.jsonl.gz', 'gold/front/v8live.jsonl.gz']
    recs = {}
    for f in files:
        for l in gzip.open(f, 'rt', encoding='utf-8'):
            if l.strip():
                r = json.loads(l)
                if '42' in r['teams'] and len(r.get('shops') or []) >= 8:
                    recs[r['id']] = r
    ref = None
    for r in recs.values():
        ref = sig(r['acts'][r['teams'].index('42')]); break
    fam = [r for r in recs.values() if sig(r['acts'][1 - r['teams'].index('42')]) == ref]
    print(f"{len(recs)} live games, {len(fam)} vs cha22-family openings", flush=True)
    jobs = []
    for r in fam:
        t0, t1 = tape_file(r, 0), tape_file(r, 1)
        jobs.append((t0, t1, r['seed'], r['teams'].index('42'), r['shops']))
    with mp.get_context('spawn').Pool(12, maxtasksperchild=1) as pool:
        out = list(pool.imap(gstat.play_one, jobs))
    rows = []
    for r, g in zip(fam, out):
        me = r['teams'].index('42')
        ra, ua, sa = totals(g['days'][me]); rb, ub, sb = totals(g['days'][1 - me])
        rows.append({'id': r['id'], 'opp': r['teams'][1 - me], 'sub': (r.get('subs') or [0, 0])[me],
                     'margin': g['rewards'][me] - g['rewards'][1 - me], 'server': r['rewards'][me] - r['rewards'][1 - me],
                     'rev': {k: ra[k] - rb[k] for k in set(ra) | set(rb)},
                     'units': {k: (ua[k], ub[k]) for k in set(ua) | set(ub)},
                     'spend': {k: sa[k] - sb[k] for k in set(sa) | set(sb)}})
    json.dump(rows, open('gold/front/famlive.json', 'w', encoding='utf-8'), ensure_ascii=False)
    for band, sel in (('all', rows), ('losses', [x for x in rows if x['margin'] <= 0]), ('close (|m|<3000)', [x for x in rows if abs(x['margin']) < 3000])):
        if not sel:
            continue
        print(f"== {band}: n {len(sel)}, mean margin {st.mean(x['margin'] for x in sel):+.0f}")
        keys = sorted({k for x in sel for k in x['rev']}, key=lambda k: st.mean(x['rev'].get(k, 0) for x in sel))
        for k in keys:
            print(f"   {k:12s} rev diff {st.mean(x['rev'].get(k, 0) for x in sel):+7.0f}  units us/them "
                  f"{st.mean(x['units'].get(k, (0, 0))[0] for x in sel):5.0f}/{st.mean(x['units'].get(k, (0, 0))[1] for x in sel):5.0f}")
        sk = sorted({k for x in sel for k in x['spend']}, key=lambda k: -st.mean(x['spend'].get(k, 0) for x in sel))
        print('   spend diff (us - them): ' + ', '.join(f"{k} {st.mean(x['spend'].get(k, 0) for x in sel):+.0f}" for k in sk if abs(st.mean(x['spend'].get(k, 0) for x in sel)) > 50))

if __name__ == '__main__':
    main()
