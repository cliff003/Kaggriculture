"""Measured cash contribution gaps; these are diagnostics, not causal interventions."""
from collections import Counter
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
def main():
    rows = json.loads((HERE/'economic_profiles.json').read_text())
    report = {'matches': len(rows), 'groups': {}, 'cases': []}
    for label in ('all','losses','wins'):
        gap = Counter()
        selected = []
        own_wheat = []
        opp_wheat = []
        for r in rows:
            p = r['teams'].index('42')
            me,opp = r['sides'][p],r['sides'][1-p]
            margin = me['money']-opp['money']
            if label == 'losses' and margin >= 0 or label == 'wins' and margin <= 0:
                continue
            selected.append(r)
            gap.update({k:opp['net_cash'].get(k,0)-me['net_cash'].get(k,0)
                        for k in set(me['net_cash'])|set(opp['net_cash'])})
            own_wheat.append(me['net_cash'].get('WHEAT',0))
            opp_wheat.append(opp['net_cash'].get('WHEAT',0))
        n = len(selected)
        report['groups'][label] = {'n': n,
                                   'mean_opponent_cash_advantage_by_account': {k:round(v/n,3) for k,v in gap.items()},
                                   'mean_own_wheat_net_cash': sum(own_wheat)/n,
                                   'mean_opponent_wheat_net_cash': sum(opp_wheat)/n}
    for r in rows:
        p = r['teams'].index('42')
        me,opp = r['sides'][p],r['sides'][1-p]
        report['cases'].append({'id':r['id'],'opponent':r['teams'][1-p],
                                'margin':me['money']-opp['money'],
                                'shops':r['shops_end'],
                                'ours':{k:me[k] for k in ('money','land','hire_cost','peak','net_cash','units','sales','tiles_by_day')},
                                'opponent_profile':{k:opp[k] for k in ('money','land','hire_cost','peak','net_cash','units','sales','tiles_by_day')}})
    report['verification'] = {'maximum_server_reward_error': max(r['max_reward_error'] for r in rows),
                               'initial_cash_residuals': sorted({v for r in rows for v in r['initial_cash_residual']}),
                               'own_wheat_net_positive_matches': sum(c['ours']['net_cash'].get('WHEAT',0)>0 for c in report['cases']),
                               'losses_with_gap_at_most_1500': sum(-1500<=c['margin']<0 for c in report['cases']),
                               'wins_with_gap_at_most_1500': sum(0<c['margin']<=1500 for c in report['cases']),
                               'tape_sha256': hashlib.sha256((HERE/'newgames.jsonl.gz').read_bytes()).hexdigest(),
                               'profile_sha256': hashlib.sha256((HERE/'economic_profiles.json').read_bytes()).hexdigest()}
    (HERE/'economic_summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'cases'},ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
