"""Summarize local counterfactual action differences without exporting raw actions."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent

def main():
    summary=json.loads((HERE/'summary.json').read_text())
    assert summary['n']==summary['selected_n']==51
    details=json.loads((HERE/'details.json').read_text())
    rows={(r['id'],r['version']):r for r in details}
    cases=[]
    for p in summary['pairs']:
        if not p['changed_steps']:continue
        n,o=rows[p['id'],'new'],rows[p['id'],'old']
        first=p['changed_steps'][0]
        counters=('input_hire_requests','input_confirmed_hires','input_purchase_requests','input_application_requests','input_confirmed_applications','input_errors')
        ns=n.get('input_telemetry') or {};os=o.get('input_telemetry') or {}
        changes={k:{'old':os.get(k,0),'new':ns.get(k,0),'delta':ns.get(k,0)-os.get(k,0)} for k in counters if ns.get(k,0)!=os.get(k,0)}
        entry=dict(id=p['id'],opponent=p['opponent'],end=p['end'],old_margin=p['old_margin'],new_margin=p['new_margin'],margin_change=p['gain'],
                   own_money_change=p['new_money']-p['old_money'],opponent_money_change=p['new_opponent_money']-p['old_opponent_money'],
                   first_changed_step=first,first_changed_day_zero_based=first//24,first_changed_hour=first%24,
                   enabled=bool((p['adaptive_stats'] or {}).get('enabled')),input_counters=changes,
                   first_old_market=o['actions'][first].get('market',[]),first_new_market=n['actions'][first].get('market',[]))
        # Both fields are our own action details; no rival actions enter this summary.
        cases.append(entry)
    result=dict(n=51,negative_margin_cases=[c for c in cases if c['margin_change']<0],
                positive_margin_cases=[c for c in cases if c['margin_change']>0],
                changed_but_equal_margin=[c for c in cases if c['margin_change']==0],
                adaptive_enabled_n=summary['enabled'],caveat='Effects use unchanged recorded rival actions. Rival policy does not adapt, but market/world outcomes can still change; no per-product attribution was audited.')
    (HERE/'mechanisms.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
