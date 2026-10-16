"""Local-only isolated port of public Guarded Shop Settlement v2; no upload."""
import hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
public=HERE/'outputs/lynnsakurai__farmer-john-and-the-wheat-seller/main.py'
assert hashlib.sha256(public.read_bytes()).hexdigest()=='2f6da44df0ce3b4a70d7320f45f3eca32d2a0b2593ff827db005f480481ce222'
base=ROOT/'submissions/v12_19_own_cha22_adaptive_inputs/main.py'
assert hashlib.sha256(base.read_bytes()).hexdigest()=='3b6a78997364b12f0cca080ff657c31acd1cd087bcfb5f8362e41da69a137f87'
layer=public.read_text().split('# Guarded Shop Settlement v2.',1)[1]
assert layer.count('_GS2_PARENT = agent\ndel agent')==1
layer=layer.replace('_GS2_PARENT = agent\ndel agent','_GS2_PARENT = globals().pop("agent")')
code=base.read_text()+'\n\n# Local research port: Guarded Shop Settlement v2, lynnsakurai, Apache-2.0.\n# Source: https://www.kaggle.com/code/lynnsakurai/farmer-john-and-the-wheat-seller\n# Guarded Shop Settlement v2.'+layer
out=HERE/'probes/shop_settlement_v1/main.py';out.parent.mkdir(parents=True,exist_ok=True)
if out.exists():assert out.read_text()==code
else:out.write_text(code)
compile(code,str(out),'exec')
print(hashlib.sha256(out.read_bytes()).hexdigest(),out)
