"""Fetch selected public notebook build artifacts without running any notebook."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
items=json.loads((HERE/'latest100.json').read_text())['kernels'][:8]


def get(row):
    ref=row['ref'];out=HERE/'outputs'/ref.replace('/','__');out.mkdir(parents=True,exist_ok=True)
    r=subprocess.run([str(ROOT/'.venv/bin/kaggle'),'kernels','output',ref,'-p',str(out),'--file-pattern',r'.*(main\.py|submission.*\.tar\.gz)$'],capture_output=True,text=True,timeout=180)
    for p in sorted(out.rglob('*.tar.gz')):
        with tarfile.open(p,'r:gz') as tar:
            for m in tar.getmembers():
                if not m.isfile() or Path(m.name).name!='main.py':continue
                dest=p.parent/(p.stem.replace('.tar','')+'_main.py')
                dest.write_bytes(tar.extractfile(m).read())
    files=[{'path':str(p.relative_to(HERE)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.rglob('*.py'))]
    return {'ref':ref,'returncode':r.returncode,'files':files,'message':(r.stdout+r.stderr)[-200:]}


if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=3) as pool:report=list(pool.map(get,items))
    (HERE/'output_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    for row in report:print(json.dumps(row))
