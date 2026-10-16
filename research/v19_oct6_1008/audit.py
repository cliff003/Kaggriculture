"""Immutable own-agent comparison on the all 51 consecutive completed New York October 6 live tapes.

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
import datetime
from zoneinfo import ZoneInfo

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
        if str(datetime.datetime.fromisoformat(e['endTime'].replace('Z','+00:00')).astimezone(ZoneInfo('America/New_York')).date())!='2026-10-06':
            continue
        episodes.append(dict(id=e['id'], end=e.get('endTime',''),
            subs=[a.get('submissionId') for a in agents],
            scores=[a.get('initialScore') for a in agents]))
    return sorted(episodes,key=lambda e:e['end'],reverse=False)

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
        actions=actions,actions_sha256=hashlib.sha256(json.dumps(actions,sort_keys=True).encode()).hexdigest())

def validate_new(r):
    assert r['version']=='new'
    assert all(v==0 for v in r['reward_errors']),('REWARD ERROR',r['id'],r['reward_errors'])
    assert r['status']==['DONE','DONE'] and not any(r['errors']),('INVALID',r['id'])

def compact_pair(n,o):
    changes=[i for i,(a,b) in enumerate(zip(n['actions'],o['actions'])) if a!=b]
    return dict(id=n['id'],opponent=n['opponent'],end=n['end'],old_margin=o['margin'],new_margin=n['margin'],
        gain=n['margin']-o['margin'],adaptive_stats=n['adaptive_stats'],input_telemetry=n['input_telemetry'],
        old_hires=o['hires_by_day'],new_hires=n['hires_by_day'],changed_steps=changes,
        new_reward_errors=n['reward_errors'],old_money=o['money'],new_money=n['money'],
        old_opponent_money=o['opponent_money'],new_opponent_money=n['opponent_money'])

def write_summary(rows,hashes):
    lookup={(r['id'],r['version']):r for r in rows}
    ids=sorted({r['id'] for r in rows if (r['id'],'new') in lookup and (r['id'],'old') in lookup},key=lambda i:lookup[i,'new']['end'])
    pairs=[compact_pair(lookup[i,'new'],lookup[i,'old']) for i in ids]
    n=len(pairs)
    summary=dict(engine='1.32.7',fixed_shops=True,fixed_opponent_actions=True,n=n,selected_n=51,
        selection='all 51 completed public episodes ending New York 2026-10-06 in saved 2026-10-08 snapshot',
        hashes=hashes,new_wins=sum(p['new_margin']>0 for p in pairs),old_wins=sum(p['old_margin']>0 for p in pairs),
        new_max_server_reward_error=max([abs(v) for p in pairs for v in p['new_reward_errors']] or [0]),
        flip_up=[p['id'] for p in pairs if p['old_margin']<=0<p['new_margin']],
        flip_down=[p['id'] for p in pairs if p['new_margin']<=0<p['old_margin']],
        mean_new_minus_old=statistics.mean(p['gain'] for p in pairs) if pairs else None,
        enabled=sum(bool((p['adaptive_stats'] or {}).get('enabled')) for p in pairs),
        identical_action_tapes=sum(not p['changed_steps'] for p in pairs),
        positive_margin_gains=sum(p['gain']>0 for p in pairs),negative_margin_gains=sum(p['gain']<0 for p in pairs),
        limitations=['One full day, not the entire seven-day production league.','Fixed opponent actions do not react to changed orders.','New version reproduction must match both server cash values exactly.','Requested hire counts are not actual audited expenditures.','This counterfactual is not an estimate of score changes.'],pairs=pairs)
    (HERE/'details.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    (HERE/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print('SUMMARY',json.dumps({k:v for k,v in summary.items() if k not in ('pairs','hashes','limitations')},ensure_ascii=False),flush=True)
    return summary

def main():
    os.environ['PYTHONHASHSEED']='0'
    selected=selection()
    assert len(selected)==51,len(selected)
    (HERE/'selection.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n')
    dest=HERE/'tapes.jsonl.gz'
    cached={r['id']:r for r in map(json.loads,gzip.open(dest,'rt'))} if dest.exists() else {}
    paths=[str(NEW),str(OLD)]
    hashes={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths}
    rows=[]
    with mp.get_context('spawn').Pool(4) as pool:
        pending={}
        for index,e in enumerate(selected):
            rec=cached.get(e['id'])
            if rec is None:
                t=time.monotonic()
                response=kg.web('GET',kg.PUBLIC_REPLAY_URL.format(e['id']),6,stream=True)
                raw=HERE/f"episode-{e['id']}.json"
                with raw.open('wb') as f:
                    for chunk in response.iter_content(1<<20):f.write(chunk)
                d=json.loads(raw.read_text());steps=d['steps'];info=d.get('info') or {}
                rec=dict(id=e['id'],end=e['end'],seed=info.get('seed'),teams=info.get('TeamNames'),
                    rewards=d.get('rewards'),statuses=d.get('statuses'),
                    shops=steps[-1][0]['observation']['town']['unlocked_shops'],subs=e['subs'],scores=e['scores'],
                    acts=[[st[i].get('action') for st in steps] for i in range(2)])
                with gzip.open(dest,'at') as f:f.write(json.dumps(rec,separators=(',',':'))+'\n')
                raw.unlink()
                print('FETCH',index+1,e['id'],rec['teams'],rec['rewards'],round(time.monotonic()-t,1),flush=True)
            for p in paths:
                pending[e['id'],p]=pool.apply_async(job,((rec,p),))
            for key,res in list(pending.items()):
                if res.ready():
                    r=res.get()
                    if r['version']=='new':validate_new(r)
                    rows.append(r);del pending[key]
            if index==15:
                for key,res in list(pending.items()):
                    r=res.get()
                    if r['version']=='new':validate_new(r)
                    rows.append(r);del pending[key]
                write_summary(rows,hashes)
        for key,res in pending.items():
            r=res.get()
            if r['version']=='new':validate_new(r)
            rows.append(r)
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==hashes[p] for p in paths)
    s=write_summary(rows,hashes)
    for p in s['pairs']:
        if p['changed_steps']:
            print('CHANGED',json.dumps(p,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
