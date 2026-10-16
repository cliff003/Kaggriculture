"""Download public notebook source only. Does not run notebook cells or upload."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
rows=json.loads((HERE/'latest100.json').read_text())['kernels'][:10]


def get(row):
    ref=row['ref'];out=HERE/'sources'/ref.replace('/','__')
    out.mkdir(parents=True,exist_ok=True)
    result=subprocess.run([str(ROOT/'.venv/bin/kaggle'),'kernels','pull',ref,'-p',str(out),'-m'],capture_output=True,text=True,timeout=180)
    files=[]
    for path in sorted(out.glob('*')):
        if path.suffix not in ('.py','.ipynb'):continue
        raw=path.read_bytes()
        files.append({'name':path.name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
        if path.suffix=='.ipynb':
            nb=json.loads(raw)
            cells=[]
            for i,c in enumerate(nb.get('cells',[])):
                text=''.join(c.get('source',[]))
                if c.get('cell_type')=='markdown':cells.append(f'CELL {i}\n{text}\n')
            (out/'markdown.txt').write_text('\n'.join(cells))
            code='\n\n'.join(''.join(c.get('source',[])) for c in nb.get('cells',[]) if c.get('cell_type')=='code')
            (out/'cells.py.txt').write_text(code)
    return {**row,'returncode':result.returncode,'files':files,'message':(result.stdout+result.stderr)[-300:]}


if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=3) as pool:
        reports=list(pool.map(get,rows))
    (HERE/'pull_manifest.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
    for item in reports:print(json.dumps(item,ensure_ascii=False))
