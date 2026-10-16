"""Read formal history of the exact opponent versions in four fresh losses."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import kg

CASES = [(56720360,'Mengfei Li',116220727),
         (56720127,'Have a nice trip in USST',116262342),
         (56722344,'Agricola',116259129),
         (56722063,'american gothic',116275122)]

def main():
    report = {'checked_utc':datetime.now(timezone.utc).isoformat(),'opponents':[]}
    for sid,name,eid in CASES:
        data = kg.web('POST',kg.LIST_EPISODES_URL,6,json={'submissionId':sid}).json()
        (HERE/f'raw_episodes_{sid}.json').write_text(json.dumps(data))
        games = []
        for e in data.get('episodes') or []:
            if e.get('state') != 'COMPLETED' or e.get('type') != 'EPISODE_TYPE_PUBLIC':
                continue
            a = e.get('agents') or []
            me = next((g for g in a if g.get('submissionId') == sid),None)
            if me is None or len(a) != 2:
                continue
            opp = next(g for g in a if g is not me)
            margin = (me.get('reward') or 0)-(opp.get('reward') or 0)
            games.append({'id':e['id'],'end_utc':e['endTime'],
                          'end_ny':datetime.fromisoformat(e['endTime'].replace('Z','+00:00')).astimezone(ZoneInfo('America/New_York')).isoformat(),
                          'margin':margin,'score':me.get('updatedScore'),
                          'opponent_submission':opp.get('submissionId')})
        games.sort(key=lambda g:g['end_utc'])
        match = next(g for g in games if g['id'] == eid)
        def stats(rows):
            return {'n':len(rows),'wins':sum(g['margin']>0 for g in rows),
                    'losses':sum(g['margin']<0 for g in rows),'ties':sum(g['margin']==0 for g in rows)}
        before = [g for g in games if g['end_utc'] < match['end_utc']]
        row = {'submission':sid,'name':name,'our_loss_episode':eid,'our_match':match,
               'first_formal_match':games[0], 'latest_formal_match':games[-1],
               'all':stats(games),
               'before_deadline':stats([g for g in games if g['end_utc']<'2026-09-30T23:59:00']),
               'before_our_match':stats(before),
               'last_predeadline_score':next((g['score'] for g in reversed(games) if g['end_utc']<'2026-09-30T23:59:00'),None)}
        report['opponents'].append(row)
        print(json.dumps(row,ensure_ascii=False),flush=True)
        (HERE/'opponent_history_summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')

if __name__ == '__main__':
    main()
