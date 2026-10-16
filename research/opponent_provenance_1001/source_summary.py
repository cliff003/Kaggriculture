"""Document public source availability without redistributing third-party files."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def main():
    rows=[]
    for metadata in sorted((HERE/'sources').glob('*/kernel-metadata.json')):
        m=json.loads(metadata.read_text())
        files=[{'name':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
               for p in sorted(metadata.parent.glob('*.ipynb'))]
        rows.append({'ref':m.get('id'),'dataset_sources':m.get('dataset_sources',[]),
                     'kernel_sources':m.get('kernel_sources',[]),'source_files':files})
    latest=json.loads((ROOT/'research/postdeadline_1001_1049/latest100.json').read_text())
    listed={r['ref'] for r in latest['kernels']}
    for r in rows:
        r['included_in_recent100_snapshot']=r['ref'] in listed
    old=json.loads((ROOT/'data/watch/code_20260930_2033.json').read_text())
    now=json.loads((ROOT/'data/watch/code_last.json').read_text())
    previous={r['id']:r for r in old['kernels']}
    changed=[r['ref'] for r in now['kernels'] if r['id'] not in previous or r['version']!=previous[r['id']]['version']]
    result={'checked_utc':datetime.now(timezone.utc).isoformat(),'public_document_sources':rows,
            'code_top30_checked_utc':now['time'],'version_changes_vs_sep30_2033':changed,
            'notes':['Availability is not proof that a named opponent used this source.',
                     'Source and notebooks were downloaded but not executed.',
                     'Recent100 is a bounded dateRun list, not an exhaustive public-code inventory.']}
    (HERE/'source_summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
