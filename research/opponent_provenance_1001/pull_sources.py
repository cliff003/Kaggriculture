"""Download primary public documentation only; never run notebook code."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REFS = ['destbreso/kaggriculture-measure-your-agent',
        'raykkretzschmar/kaggriculture-findings-from-zero-to-top-meta',
        'kaitofukami/177-180-fresh-top-30-v21-1-conditional-memory']

def main():
    results = []
    for ref in REFS:
        out = HERE/'sources'/ref.replace('/','__')
        out.mkdir(parents=True,exist_ok=True)
        done = subprocess.run([str(ROOT/'.venv/bin/kaggle'),'kernels','pull',ref,'-p',str(out),'-m'],
                              capture_output=True,text=True,timeout=180)
        row = {'ref':ref,'returncode':done.returncode,'files':[]}
        for p in out.glob('*.ipynb'):
            nb = json.loads(p.read_text())
            md = '\n\n'.join(''.join(c.get('source',[])) for c in nb.get('cells',[]) if c.get('cell_type')=='markdown')
            (out/'markdown.txt').write_text(md)
            row['files'].append({'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
        results.append(row)
        print(json.dumps(row,ensure_ascii=False),flush=True)
    (HERE/'pull_manifest.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')

if __name__ == '__main__':
    main()
