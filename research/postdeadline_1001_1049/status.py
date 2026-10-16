"""Freeze fresh episode metadata and leaderboard; print measured silver margin."""
import csv
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import shutil
import statistics
import sys
from zoneinfo import ZoneInfo
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import harvest

NY = ZoneInfo('America/New_York')
def summarize(ms):
    return {'n': len(ms), 'wins': sum(m['result'] == '胜' for m in ms),
            'losses': sum(m['result'] == '负' for m in ms),
            'median_opponent_score': statistics.median([m['opponent_score'] for m in ms]) if ms else None}

def main():
    result = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'agents': {}}
    snapshots = {}
    for sid in (56649860, 56713491):
        source = ROOT / f'data/episodes/{sid}.json'
        shutil.copy2(source, HERE / f'episodes_{sid}.json')
        data = json.loads(source.read_text())
        snapshots[str(sid)] = data
        names = {t['id']: t.get('teamName') for t in data['teams']}
        ms = []
        for e in data['episodes']:
            if e.get('state') != 'COMPLETED' or e.get('type') != 'EPISODE_TYPE_PUBLIC':
                continue
            agents = e.get('agents') or []
            me = next((g for g in agents if g.get('submissionId') == sid), None)
            if not me or len(agents) != 2:
                continue
            opp = next(g for g in agents if g is not me)
            margin = (me.get('reward') or 0) - (opp.get('reward') or 0)
            ms.append({'id': e['id'], 'end_utc': e['endTime'],
                       'end_ny': datetime.fromisoformat(e['endTime'].replace('Z', '+00:00')).astimezone(NY).isoformat(),
                       'result': '胜' if margin > 0 else '负' if margin < 0 else '平',
                       'margin': margin, 'score': me.get('updatedScore'),
                       'opponent_score': opp.get('initialScore') or 600,
                       'opponent_submission': opp.get('submissionId'),
                       'opponent_team': names.get(opp.get('teamId'))})
        ms.sort(key=lambda x: x['end_utc'])
        a = {'all': summarize(ms), 'last30': summarize(ms[-30:]), 'last12': summarize(ms[-12:]),
             'postdeadline': summarize([m for m in ms if m['end_utc'] >= '2026-10-01T00:00:00']),
             'since_previous_check': summarize([m for m in ms if m['end_utc'] >= '2026-10-01T04:38:45']),
             'latest': ms[-1], 'latest30': ms[-30:]}
        result['agents'][str(sid)] = a
    with zipfile.ZipFile(ROOT / 'data/lb/kaggriculture.zip') as z:
        name = z.namelist()[0]
        raw = z.read(name)
        (HERE / 'leaderboard.csv').write_bytes(raw)
        rows = sorted(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))), key=lambda r: int(r['Rank']))
    ours = next(r for r in rows if int(r['TeamId']) == 16908623)
    n = len(rows)
    cuts = {'gold': 10+n//500, 'silver': n//20, 'bronze': n//10}
    result['leaderboard'] = {'source_filename': name, 'teams': n, 'rank': int(ours['Rank']), 'score': float(ours['Score']),
                             'cuts': {k: {'rank': c, 'score': float(rows[c-1]['Score']),
                                        'buffer_score': round(float(ours['Score'])-float(rows[c-1]['Score']), 3),
                                        'buffer_rank': c-int(ours['Rank'])} for k,c in cuts.items()}}
    prev = json.loads((ROOT / 'research/notebook_0930_2032/latest100.json').read_text())
    now = json.loads((HERE / 'latest100.json').read_text())
    old = {k['ref']: k for k in prev['kernels']}
    result['public_changes'] = [k for k in now['kernels'] if k['ref'] not in old or k['last_run_utc'] != old[k['ref']]['last_run_utc']]
    (HERE / 'status_summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    for sid,a in result['agents'].items():
        print(sid, json.dumps({k:v for k,v in a.items() if k != 'latest30'}, ensure_ascii=False))
    print('Leaderboard', result['leaderboard'])
    print('Public metadata changes', result['public_changes'])

if __name__ == '__main__':
    main()
