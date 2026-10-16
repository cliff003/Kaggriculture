"""Check pre-deadline formal games of the other final agents; no private code access."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import kg

def main():
    rows=[]
    for sid,name in [(56688411,'Agricola'),(56720657,'american gothic')]:
        d=kg.web('POST',kg.LIST_EPISODES_URL,6,json={'submissionId':sid}).json()
        (HERE/f'raw_episodes_{sid}.json').write_text(json.dumps(d))
        games=[]
        for e in d.get('episodes') or []:
            if e.get('state')!='COMPLETED' or e.get('type')!='EPISODE_TYPE_PUBLIC':
                continue
            a=e.get('agents') or []
            me=next((g for g in a if g.get('submissionId')==sid),None)
            if me is None or len(a)!=2:
                continue
            opp=next(g for g in a if g is not me)
            games.append({'id':e['id'],'end_utc':e['endTime'],
                          'margin':(me.get('reward') or 0)-(opp.get('reward') or 0),
                          'score':me.get('updatedScore')})
        games.sort(key=lambda g:g['end_utc'])
        before=[g for g in games if g['end_utc']<'2026-09-30T23:59:00']
        row={'name':name,'submission':sid,'all_n':len(games),'predeadline_n':len(before),
             'predeadline_wins':sum(g['margin']>0 for g in before),
             'predeadline_losses':sum(g['margin']<0 for g in before),
             'first_formal_ny':datetime.fromisoformat(games[0]['end_utc'].replace('Z','+00:00')).astimezone(ZoneInfo('America/New_York')).isoformat(),
             'last_predeadline':before[-1] if before else None}
        rows.append(row)
        print(json.dumps(row,ensure_ascii=False),flush=True)
    (HERE/'earlier_versions_summary.json').write_text(json.dumps({'checked_utc':datetime.now(timezone.utc).isoformat(),'agents':rows},ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':
    main()
