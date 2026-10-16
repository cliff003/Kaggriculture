r"""Replay every recorded game in which one side runs the fixed ph3 wheat round-trip schedule, with each candidate in
the other seat (the schedule side keeps its tape).  .venv\Scripts\python.exe gold\front\schedcf.py CAND.py [CAND.py ...]"""
import sys, glob, gzip, json, multiprocessing as mp, statistics as st
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools'); sys.path.insert(0, 'gold/front')

def q(o):
    try: return int(o[2])
    except Exception: return 0

def has_sched(A):
    hits = 0
    for t in (327, 375, 419):
        m = ((A[t + 1] if t + 1 < len(A) else None) or {}).get('market') or []
        n = ((A[t + 2] if t + 2 < len(A) else None) or {}).get('market') or []
        b = sum(q(o) for o in m if isinstance(o, list) and len(o) >= 3 and o[0] == 'BUY_PRODUCT' and o[1] == 'WHEAT')
        s = sum(q(o) for o in n if isinstance(o, list) and len(o) >= 3 and o[0] == 'SELL' and o[1] == 'WHEAT')
        hits += b >= 20 and s >= 20
    return hits >= 2

def main():
    import gstat
    from seatswap import tape_file
    cands = sys.argv[1:]
    recs = {}
    for p in glob.glob('gold/front/front_*.jsonl.gz') + ['gold/front/v8live.jsonl.gz'] + glob.glob('data/games/live_*.jsonl.gz'):
        for l in gzip.open(p, 'rt', encoding='utf-8'):
            if l.strip():
                r = json.loads(l)
                if len(r.get('shops') or []) >= 8:
                    recs.setdefault(r['id'], r)
    jobs, meta = [], []
    for r in recs.values():
        for s in range(2):
            if r['teams'][s] != '42' and has_sched(r['acts'][s]):
                me = 1 - s
                tape = tape_file(r, s)
                for c in cands:
                    seats = (c, tape) if me == 0 else (tape, c)
                    jobs.append((seats[0], seats[1], r['seed'], me, r['shops'])); meta.append((r['id'], s, c, r['teams'][s]))
    print(len(jobs) // len(cands), 'games', flush=True)
    with mp.get_context('spawn').Pool(12, maxtasksperchild=1) as pool:
        out = list(pool.imap(gstat.play_one, jobs))
    res = {}
    for (gid, s, c, t), g in zip(meta, out):
        me = 1 - s
        res.setdefault(c, {})[(gid, s)] = g['rewards'][me] - g['rewards'][s]
    base = res[cands[0]]
    for c in cands:
        d = [res[c][k] - base[k] for k in res[c]]
        print(c.split('/')[-2], 'wins', sum(v > 0 for v in res[c].values()), '/', len(res[c]), 'mean diff vs first', round(st.mean(d)), 'se', round(st.stdev(d) / max(1, len(d)) ** 0.5) if len(d) > 1 else 0,
              'flips +', sum(base[k] <= 0 < res[c][k] for k in res[c]), '-', sum(res[c][k] <= 0 < base[k] for k in res[c]))

if __name__ == '__main__':
    main()
