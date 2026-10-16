"""Verify paired results and print compact, reproducible decision numbers."""
import json
import hashlib
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def read(path):
    return [json.loads(line) for line in path.open() if line.strip()]


def pair(label, base, cand):
    assert set(base) == set(cand), (label, len(base), len(cand), len(set(base) ^ set(cand)))
    ids = list(base)
    b = [base[i] for i in ids]
    c = [cand[i] for i in ids]
    delta = [y-x for x,y in zip(b,c)]
    return dict(label=label, n=len(ids), base_wins=sum(x>0 for x in b),
                cand_wins=sum(x>0 for x in c),
                mean_delta=round(statistics.mean(delta), 2),
                changed=sum(x!=0 for x in delta), better=sum(x>0 for x in delta),
                worse=sum(x<0 for x in delta),
                up=[i for i in ids if base[i]<=0<cand[i]],
                down=[i for i in ids if cand[i]<=0<base[i]])


def replay(label, path):
    rows = read(path)
    base = {r['id']:r['margin'] for r in rows if '/submissions/V12_AventadorSVJ/' in r['path']}
    cand = {r['id']:r['margin'] for r in rows if '/submissions/V12_AventadorSVJ/' not in r['path']}
    assert all(r['status']==['DONE','DONE'] and r['errors']==[0,0] for r in rows)
    return pair(label, base, cand)


def panel(label, path):
    rows = read(path)
    key = lambda r:(r['seed'],r['seat'],r['opponent'])
    base = {key(r):r['margin'] for r in rows if '/submissions/V12_AventadorSVJ/' in r['path']}
    cand = {key(r):r['margin'] for r in rows if '/submissions/V12_AventadorSVJ/' not in r['path']}
    assert all(r['status']==['DONE','DONE'] and r['errors']==[0,0] for r in rows)
    return pair(label, base, cand)


def main():
    candidate_path = HERE/'prototypes/combined/main.py'
    candidate_sha = hashlib.sha256(candidate_path.read_bytes()).hexdigest()
    assert candidate_sha == 'a63ac3394d273b6d4e3a699e0f44febf9cb9d476774368a6245d93cfe43ebb85'
    for path in (HERE/'combined_1480.meta.json',
                 HERE/'latest30_combined.meta.json'):
        meta = json.loads(path.read_text())
        assert candidate_sha in meta['sha256'].values()
    for path in (HERE/'panel_combined_tomato/tomato_panel_metadata.json',
                 HERE/'panel_holdout_tomato/tomato_panel_metadata.json',
                 HERE/'panel_combined_sheep/sheep_panel_metadata.json'):
        meta = json.loads(path.read_text())
        assert candidate_sha in meta['paths'].values()
    cached = read(ROOT / 'research/carrera/results/08a0d374aedd.jsonl')
    combined = read(HERE / 'combined_1480.jsonl')
    assert len(combined)==1480 and all(r['status']==['DONE','DONE'] and r['errors']==[0,0] for r in combined)
    ids = {r['id'] for r in combined}
    baseline = {r['id']:r['margin'] for r in cached if r['id'] in ids}
    candidate = {r['id']:r['margin'] for r in combined}
    outcomes = [pair('1480 历史实盘录像',baseline,candidate),
                replay('9/30 最新 30 局',HERE/'latest30_combined.jsonl'),
                panel('番茄开发面板 128 局',HERE/'panel_combined_tomato/tomato_panel.jsonl'),
                panel('番茄独立面板 128 局',HERE/'panel_holdout_tomato/tomato_panel.jsonl'),
                panel('羊毛面板 192 局',HERE/'panel_combined_sheep/sheep_panel.jsonl')]
    for r in outcomes:
        print(json.dumps(r,ensure_ascii=False))
    (HERE/'summary.json').write_text(json.dumps(outcomes,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
