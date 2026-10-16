"""Download public notebook text; never execute downloaded code."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REFS = ['georgymamarin/kaggriculture-what-2600-farms-do-differently',
        'destbreso/how-reliable-is-the-public-leaderboard',
        'destbreso/x-ray-your-agent',
        'raykkretzschmar/kaggriculture-findings-from-zero-to-top-meta',
        'kirderf/kaggriculture-leaderboard-viewer']

def main():
    results = []
    for ref in REFS:
        out = HERE/'sources'/ref.replace('/','__')
        out.mkdir(parents=True, exist_ok=True)
        done = subprocess.run([str(ROOT/'.venv/bin/kaggle'), 'kernels', 'pull', ref, '-p', str(out), '-m'],
                              capture_output=True, text=True, timeout=180)
        row = {'ref': ref, 'returncode': done.returncode, 'files': []}
        for p in list(out.glob('*.ipynb')) + list(out.glob('*.py')):
            row['files'].append({'name': p.name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size})
            if p.suffix == '.ipynb':
                nb = json.loads(p.read_text())
                md = '\n\n'.join(''.join(c.get('source', [])) for c in nb.get('cells', []) if c.get('cell_type') == 'markdown')
                (out/'markdown.txt').write_text(md)
                compact = [{'cell': i, 'kind': c.get('cell_type'), 'source': ''.join(c.get('source', []))}
                           for i, c in enumerate(nb.get('cells', []))]
                (out/'cells.json').write_text(json.dumps(compact, ensure_ascii=False, indent=2))
        results.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
    (HERE/'pull_manifest.json').write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n')

if __name__ == '__main__':
    main()
