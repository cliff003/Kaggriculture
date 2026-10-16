"""Read public notebook metadata. Never execute notebook content."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import kg
import watch_code

OUT = Path(__file__).resolve().parent
ny = ZoneInfo('America/New_York')
now = datetime.now(timezone.utc)
items = kg.api().kernels_list(competition='kaggriculture', sort_by='dateRun', page_size=100)
recent = [{'ref': k.ref, 'title': k.title,
           'last_run_utc': k.last_run_time.isoformat() if k.last_run_time else None,
           'votes': k.total_votes} for k in items]
top = watch_code.fetch(30, 6)
old_recent = json.loads((ROOT / 'research/postdeadline_1001_1049/latest100.json').read_text())
old_top = json.loads((ROOT / 'data/watch/code_20261001_1110.json').read_text())
old_by_ref = {k['ref']: k for k in old_recent['kernels']}
old_by_id = {k['id']: k for k in old_top['kernels']}
changed_recent = [k for k in recent if k['ref'] not in old_by_ref or
                  k['last_run_utc'] != old_by_ref[k['ref']]['last_run_utc']]
changed_top = [dict(k, previous=old_by_id.get(k['id'])) for k in top
               if k['id'] not in old_by_id or k['version'] != old_by_id[k['id']]['version']]
summary = {'checked_utc': now.isoformat(), 'checked_new_york': now.astimezone(ny).isoformat(),
           'previous_recent_check_utc': old_recent['checked_utc'],
           'recent_count': len(recent), 'changed_recent': changed_recent,
           'top30_version_changes': changed_top,
           'caution': 'Code-page scores are historical bestPublicScore, not current leaderboard skill.'}
(OUT / 'latest100.json').write_text(json.dumps({'checked_utc': now.isoformat(), 'kernels': recent}, ensure_ascii=False, indent=2)+'\n')
(OUT / 'top30.json').write_text(json.dumps({'checked_utc': now.isoformat(), 'kernels': top}, ensure_ascii=False, indent=2)+'\n')
(OUT / 'metadata_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(summary, ensure_ascii=False, indent=2))
