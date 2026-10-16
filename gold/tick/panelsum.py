r"""Summarize an rr.py --field run: per opponent W-L and mean margin of two candidates, paired by seed.
    .venv\Scripts\python.exe gold\tick\panelsum.py RR.jsonl BASE_NAME CAND_NAME"""
import json, collections, statistics as st, os, sys
if __name__ == '__main__':
    path, bn, cn = sys.argv[1], sys.argv[2], sys.argv[3]
    rows = [json.loads(l) for l in open(path, encoding='utf-8') if l.strip()]
    def name(p): return os.path.basename(os.path.dirname(p))
    res = collections.defaultdict(dict)
    for r in rows:
        a, b = name(r['a']), name(r['b'])
        res[(a, b)][r['seed']] = (r['ra'] or 0) - (r['rb'] or 0)
        res[(b, a)][r['seed']] = (r['rb'] or 0) - (r['ra'] or 0)
    opps = sorted({k[1] for k in res if k[0] == bn and k[1] != cn})
    print(f"{'opp':15s} {bn+' W-L':>12s} {'mean':>7s} {cn+' W-L':>14s} {'mean':>7s} {'paired':>8s} {'se':>5s}")
    tw = [0, 0, 0, 0]; allp = []
    for o in opps:
        A = res[(bn, o)]; B = res[(cn, o)]
        if not A or not B:
            continue
        wa = sum(v > 0 for v in A.values()); wb = sum(v > 0 for v in B.values())
        common = sorted(set(A) & set(B)); d = [B[s] - A[s] for s in common]; allp += d
        tw[0] += wa; tw[1] += len(A) - wa; tw[2] += wb; tw[3] += len(B) - wb
        print(f"{o:15s} {wa:6d}-{len(A)-wa:<5d} {st.mean(A.values()):+7.0f} {wb:8d}-{len(B)-wb:<5d} {st.mean(B.values()):+7.0f} "
              f"{st.mean(d):+8.0f} {st.stdev(d)/len(d)**0.5:5.0f}")
    print(f"{'TOTAL':15s} {tw[0]:6d}-{tw[1]:<5d} {'':7s} {tw[2]:8d}-{tw[3]:<5d} {'':7s} {st.mean(allp):+8.0f} {st.stdev(allp)/len(allp)**0.5:5.0f}")
    H = res.get((cn, bn), {})
    if H:
        print(f"head-to-head {cn} vs {bn}: {sum(v > 0 for v in H.values())}-{sum(v < 0 for v in H.values())} mean {st.mean(H.values()):+.0f}")
