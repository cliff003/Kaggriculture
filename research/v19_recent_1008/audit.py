"""Immutable own-agent comparison on the latest twelve consecutive completed live tapes.

Raw opponent actions remain local. Public replay requests use the project's shared
rate-limit stamp. Same seed/seat and recorded shop sequence, opponent actions fixed.
"""
import collections
import gzip
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import statistics
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'tools'))
import kg

OLD = ROOT/'submissions/V12_AventadorSVJ/main.py'
NEW = ROOT/'submissions/v12_19_own_cha22_adaptive_inputs/main.py'

def selection():
    data = json.loads((ROOT/'research/review_1008/episodes_56713491.json').read_text())
    episodes = []
    for e in data.get('episodes', []):
        if e.get('state')!='COMPLETED' or e.get('type')!='EPISODE_TYPE_PUBLIC':
            continue
        agents = sorted(e.get('agents') or [], key=lambda a:a.get('index',0))
        if len(agents)!=2 or not any(a.get('submissionId')==56713491 for a in agents):
            continue
        episodes.append(dict(id=e['id'], end=e.get('endTime',''),
            subs=[a.get('submissionId') for a in agents],
            scores=[a.get('initialScore') for a in agents]))
    return sorted(episodes,key=lambda e:e['end'],reverse=True)[:12]

def fetch():
    selected = selection()
    (HERE/'selection.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n')
    dest=HERE/'tapes.jsonl.gz'
    have={r['id'] for r in map(json.loads,gzip.open(dest,'rt'))} if dest.exists() else set()
    for e in selected:
        if e['id'] in have:continue
        t=time.monotonic()
        response=kg.web('GET',kg.PUBLIC_REPLAY_URL.format(e['id']),6,stream=True)
        raw=HERE/f"episode-{e['id']}.json"
        with raw.open('wb') as f:
            for chunk in response.iter_content(1<<20):f.write(chunk)
        d=json.loads(raw.read_text())
        steps=d['steps'];info=d.get('info') or {}
        rec=dict(id=e['id'],end=e['end'],seed=info.get('seed'),teams=info.get('TeamNames'),
            rewards=d.get('rewards'),statuses=d.get('statuses'),
            shops=steps[-1][0]['observation']['town']['unlocked_shops'],
            subs=e['subs'],scores=e['scores'],
            acts=[[st[i].get('action') for st in steps] for i in range(2)])
        with gzip.open(dest,'at') as f:f.write(json.dumps(rec,separators=(',',':'))+'\n')
        raw.unlink()
        print('FETCH',e['id'],rec['teams'],rec['rewards'],round(time.monotonic()-t,1),flush=True)
    return [json.loads(line) for line in gzip.open(dest,'rt') if line.strip()]

def job(args):
    import fastarena
    import forceshops
    import cfreplay
    rec,path=args
    forceshops.force(rec['shops'])
    mine=fastarena.load_agent(path)
    base=mine.__globals__['_BASE_NS']
    seat=rec['teams'].index('42')
    other=cfreplay.tape_agent(rec['acts'][1-seat])
    hires=collections.Counter()
    actions=[]
    def spy(obs,conf=None):
        a=mine(obs,conf)
        step=int(obs['step'])
        for order in a.get('market',[]):
            if isinstance(order,list) and order and order[0]=='HIRE':
                hires[step//24]+=1
        actions.append(a)
        return a
    agents=[spy,other] if seat==0 else [other,spy]
    r=fastarena.run_game(*agents,rec['seed'])
    m,o=r['rewards'][seat],r['rewards'][1-seat]
    return dict(id=rec['id'],version='old' if path==str(OLD) else 'new',opponent=rec['teams'][1-seat],
        end=rec['end'],margin=m-o,money=m,opponent_money=o,
        server_rewards=rec['rewards'],server_margin=rec['rewards'][seat]-rec['rewards'][1-seat],
        reward_errors=[r['rewards'][i]-rec['rewards'][i] for i in range(2)],
        status=r['status'],errors=r['errors'],
        adaptive_stats=base.get('_AI_STATS'),input_telemetry=base.get('_R51_INPUT_REPORT'),hires_by_day=dict(hires),
        actions_sha256=hashlib.sha256(json.dumps(actions,sort_keys=True).encode()).hexdigest())

def main():
    os.environ['PYTHONHASHSEED']='0'
    recs=fetch()
    assert len(recs)==12
    paths=[str(NEW),str(OLD)]
    hashes={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths}
    with mp.get_context('spawn').Pool(4) as pool:
        rows=list(pool.imap_unordered(job,[(r,p) for p in paths for r in recs],chunksize=1))
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==hashes[p] for p in paths)
    lookup={(r['id'],r['version']):r for r in rows}
    new=[lookup[r['id'],'new'] for r in recs]
    old=[lookup[r['id'],'old'] for r in recs]
    summary=dict(engine='1.32.7',fixed_shops=True,fixed_opponent_actions=True,n=len(recs),
        selection='latest twelve consecutive completed public episodes in saved 2026-10-08 snapshot',
        hashes=hashes,new_wins=sum(r['margin']>0 for r in new),old_wins=sum(r['margin']>0 for r in old),
        new_max_server_reward_error=max(abs(v) for r in new for v in r['reward_errors']),
        new_invalid=[r['id'] for r in new if r['status']!=['DONE','DONE'] or any(r['errors'])],
        flip_up=[n['id'] for n,o in zip(new,old) if o['margin']<=0<n['margin']],
        flip_down=[n['id'] for n,o in zip(new,old) if n['margin']<=0<o['margin']],
        mean_new_minus_old=statistics.mean(n['margin']-o['margin'] for n,o in zip(new,old)),
        enabled=sum(bool((r['adaptive_stats'] or {}).get('enabled')) for r in new),
        identical_action_tapes=sum(n['actions_sha256']==o['actions_sha256'] for n,o in zip(new,old)),
        limitations=[
            'Only twelve consecutive recent games, not a complete production league.',
            'Opponent keeps its recorded actions and does not react to changed orders.',
            'Hire counts are requested HIRE actions, not audited actual hiring expenditure.',
            'An enabled adaptive gate does not guarantee an extra tour or a changed victory.',
            'Different submission ratings cannot be causally attributed to code from this sample.'
        ],
        rows=[dict(id=r['id'],version=r['version'],opponent=r['opponent'],end=r['end'],
            margin=r['margin'],money=r['money'],opponent_money=r['opponent_money'],
            reward_errors=r['reward_errors'],status=r['status'],errors=r['errors'],
            adaptive_stats=r['adaptive_stats'],hires_requested=sum(r['hires_by_day'].values()))
            for r in sorted(rows,key=lambda r:(r['end'],r['version']),reverse=True)])
    (HERE/'details.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    (HERE/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('rows','hashes')},ensure_ascii=False),flush=True)
    for n,o in zip(new,old):
        print(n['id'],n['opponent'],'OLD',o['margin'],'NEW',n['margin'],'CHANGE',n['margin']-o['margin'],
            'ADAPT',n['adaptive_stats'],'HIRE OLD/NEW',o['hires_by_day'],n['hires_by_day'],flush=True)

if __name__=='__main__':main()
