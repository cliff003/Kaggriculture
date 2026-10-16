"""Immutable-code paired replay with the existing per-hash result cache."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import statistics
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'research/carrera'))
import ab_replay


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('paths',nargs='+');ap.add_argument('--source',required=True)
    ap.add_argument('--workers',type=int,default=6);ap.add_argument('--out',required=True)
    a=ap.parse_args();os.environ['PYTHONHASHSEED']='0'
    records={r['id']:r for r in map(json.loads,gzip.open(a.source,'rt'))}
    paths=[str(Path(p).resolve()) for p in a.paths]
    hashes={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths}
    results=[];base=None
    for path in paths:
        rows=ab_replay.run(path,records,a.workers)
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==hashes[path],'Agent changed during validation.'
        if base is None:base=rows
        summary={'path':path,'sha256':hashes[path],'n':len(rows),'wins':sum(r['margin']>0 for r in rows.values()),
                 'delta':statistics.mean(rows[g]['margin']-base[g]['margin'] for g in records),
                 'up':[g for g in records if base[g]['margin']<=0<rows[g]['margin']],
                 'down':[g for g in records if rows[g]['margin']<=0<base[g]['margin']],
                 'bad':[g for g in records if rows[g]['status']!=['DONE','DONE']]}
        results.append(summary);print(json.dumps(summary,ensure_ascii=False),flush=True)
        Path(a.out).write_text(json.dumps({'source':a.source,'engine':'1.32.7','forced_shops':True,
                                         'summaries':results},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
