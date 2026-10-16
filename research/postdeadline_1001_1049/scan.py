"""Read current public kernel metadata without running or uploading notebooks."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import kg

items = kg.api().kernels_list(competition='kaggriculture', sort_by='dateRun', page_size=100)
rows = [{'ref': k.ref, 'title': k.title,
         'last_run_utc': k.last_run_time.isoformat() if k.last_run_time else None,
         'votes': k.total_votes} for k in items]
report = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'kernels': rows}
Path(__file__).with_name('latest100.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
for row in rows[:25]:
    print(json.dumps(row, ensure_ascii=False))
