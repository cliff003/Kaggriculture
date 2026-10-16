"""Exact recorded-action accounting for the newly completed formal matches."""
import collections
import gzip
import json
import multiprocessing as mp
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'research/carrera')]

def job(rec):
    import econ
    import forceshops
    import prod_profile
    forceshops.force(rec['shops'])
    profile = prod_profile.job(rec)
    details = econ.resim(rec)
    cash = [collections.Counter(), collections.Counter()]
    daily = [collections.defaultdict(collections.Counter), collections.defaultdict(collections.Counter)]
    for step,p,op,item,value in econ._CUR['log']:
        if op == 'LOST':
            continue
        key = op if op in ('HIRE','LAND') else {'COW':'MILK','SHEEP':'WOOL','GOOSE':'EGG'}.get(item,item)
        amount = value if op == 'SELL' else -value
        cash[p][key] += amount
        daily[p][step//24][key] += amount
    for p,s in enumerate(profile['sides']):
        s['net_cash'] = dict(cash[p])
        s['daily_net_cash'] = dict(daily[p])
        s['sales'] = details[p]['sales']
        s['spend'] = details[p]['spend']
    profile['max_reward_error'] = max(abs(s['money']-s['server']) for s in details)
    profile['initial_cash_residual'] = [s['money']-sum(cash[p].values()) for p,s in enumerate(details)]
    return profile

def main():
    paths = list(HERE.glob('newgames.jsonl.gz')) or [HERE/'diagnosis10.jsonl.gz']
    recs = [json.loads(line) for path in paths for line in gzip.open(path,'rt')]
    status = json.loads((HERE/'status_summary.json').read_text())
    expected = {m['id'] for a in status['agents'].values() for m in a['latest30']
                if m['end_utc'] >= '2026-10-01T04:38:45'}
    assert {r['id'] for r in recs} == expected, 'Wait until all selected replays finish downloading.'
    with mp.get_context('spawn').Pool(4) as pool:
        rows = list(pool.imap_unordered(job,recs,chunksize=1))
    rows.sort(key=lambda r:r['id'])
    assert all(r['max_reward_error'] == 0 for r in rows), 'Replay fidelity check failed.'
    assert all(v == 3000 for r in rows for v in r['initial_cash_residual']), 'Cash decomposition failed.'
    (HERE/'economic_profiles.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    print('Matches:',len(rows),'maximum server error:',max(r['max_reward_error'] for r in rows),
          'initial cash residuals:',sorted({v for r in rows for v in r['initial_cash_residual']}))
    for r in rows:
        p = r['teams'].index('42')
        me,opp = r['sides'][p],r['sides'][1-p]
        print(r['id'],r['teams'][1-p],int(me['money']-opp['money']),
              'cash differences',dict(sorted({k:opp['net_cash'].get(k,0)-me['net_cash'].get(k,0)
                                              for k in set(me['net_cash'])|set(opp['net_cash'])}.items(),key=lambda x:-x[1])))

if __name__ == '__main__':
    main()
