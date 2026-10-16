"""Keep original investment against mirrors; loosen tours against different farm layouts."""
import base64
import argparse
import hashlib
from pathlib import Path
import sys
import zlib

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import fastarena
ap=argparse.ArgumentParser();ap.add_argument('--source',default='submissions/V12_AventadorSVJ/main.py')
ap.add_argument('--tag',default='v2');args=ap.parse_args()
base=(ROOT/args.source).read_text()
source=fastarena.load_agent(str(ROOT/args.source)).__globals__['_BASE_SRC']
lo=base.index('_BASE_SHA256 =');hi=base.index('_BASE_NS =',lo)

LAYER=r'''

# Team 42: choose fertilizer economics from pre-investment farm layout.
_ADIN_ENTRY_PARENT=cha20_entry_agent
_AI_STATE={}
_AI_STATS={'enabled':False,'similarities':[],'calls':0,'errors':0}
_AI_RATIO=1.5
_AI_ADD=50
_AI_PATH_PENALTY=1.5
_AI_PARENT_JOINT=_r68_joint_plans


def _r68_joint_plans(obs,action,targets,stock,purchases,topup):
    global _AI_RATIO,_AI_ADD,_AI_PATH_PENALTY
    step=int(obs['step']);seat=int(obs['player'])
    state=_AI_STATE.get(seat,{})
    if not state:
        state=_AI_STATE[seat]={'enabled':_r37_similarity(obs)<@THRESHOLD@}
        _AI_STATS['enabled']=state['enabled']
    _AI_RATIO,_AI_ADD,_AI_PATH_PENALTY=(1.0,20,.75) if state['enabled'] else (1.5,50,1.5)
    _AI_STATS['calls']+=1
    return _AI_PARENT_JOINT(obs,action,targets,stock,purchases,topup)


def adin_submission_entry(observation,configuration=None):
    seat=int(observation['player']);step=int(observation['step'])
    if step==0:
        _AI_STATE.clear();_AI_STATS.update(enabled=False,similarities=[],calls=0,errors=0)
    if step in (264,272,280):
        _AI_STATS['similarities'].append(_r37_similarity(observation))
    if step==287:
        # All samples predate the first discretionary fertilizer tour (day 12).
        scores=_AI_STATS['similarities']
        enabled=bool(len(scores)==3 and max(scores)<@THRESHOLD@)
        _AI_STATE[seat]={'enabled':enabled};_AI_STATS['enabled']=enabled
    return _ADIN_ENTRY_PARENT(observation,configuration)
'''

for threshold in (.94,.90):
    raw=source
    for old,new in [('if value<1.5*cost+50','if value<_AI_RATIO*cost+_AI_ADD'),
                    ('new_gross-1.5*fertilizer*len(new_path)','new_gross-_AI_PATH_PENALTY*fertilizer*len(new_path)')]:
        assert raw.count(old)==1;raw=raw.replace(old,new)
    raw+=LAYER.replace('@THRESHOLD@',repr(threshold))
    payload=base64.b85encode(zlib.compress(raw.encode(),9)).decode()
    embedded='_BASE_SHA256 = '+repr(hashlib.sha256(raw.encode()).hexdigest())+'\n_BASE_SRC = _zlib.decompress(_b64.b85decode(\n'
    embedded+='\n'.join('    '+repr(payload[i:i+120]) for i in range(0,len(payload),120))+'\n)).decode("utf-8")\n'
    code=base[:lo]+embedded+base[hi:]
    name='input_adaptive'+str(round(threshold*100))+'_'+args.tag
    out=HERE/'candidates'/name/'main.py';out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():assert out.read_text()==code
    else:out.write_text(code)
    compile(code,name,'exec');print(name,hashlib.sha256(code.encode()).hexdigest())
