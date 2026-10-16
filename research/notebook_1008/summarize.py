"""Build our own analysis of public notebook sources without running them."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NY = ZoneInfo('America/New_York')
metadata = json.loads((HERE/'metadata_summary.json').read_text())
latest = json.loads((HERE/'latest100.json').read_text())
runs = {k['ref']: k for k in latest['kernels']}

def source_text(p):
    nb = json.loads(p.read_text())
    return '\n\n'.join(''.join(c.get('source', [])) for c in nb.get('cells', []))

specs = [
    {
        'ref': 'georgymamarin/kaggriculture-what-2600-farms-do-differently',
        'old_dir': 'research/notebook_1001_0144/farm2600',
        'takeaways': [
            'Use fresh leader and middle cohorts from the same time window; compare production, labor, land timing and selling prices.',
            'Prefer within-episode margin to raw final bank, and separate shop worlds and rival strength bands.',
            'The author warns that crawler coverage changes, a single best game, shared worlds and serial matchmaking can bias conclusions.'
        ],
        'boundaries': [
            'All cell source is identical to the 10/1 saved source; the 10/7 run is a refresh, not verified new strategy code.',
            'Current rendered numerical tables were not captured by kernels pull; no new numerical production advantage is claimed.'
        ],
    },
    {
        'ref': 'destbreso/x-ray-your-agent',
        'old_dir': 'research/notebook_1001_0144/xray',
        'takeaways': [
            'Measure rating convergence by drift per played episode, delta sign reversals and episode count, rather than a per-hour slope.',
            'Distinguish global variation from variation within the same two-shop world so a shop router is not mislabeled as a fully reactive policy.',
            'Separate plan agreement from market agreement, then inspect crop output, hired labor, idle time, unsold inventory and market timing against actual rivals.'
        ],
        'boundaries': [
            'All cell source is identical to the 10/1 saved source; the 10/7 run is a refresh, not verified new strategy code.',
            'Some macro reference numbers in the text are explicitly from 8/30 or 9/10. They are not current top-agent targets.',
            'The one-point-per-episode convergence threshold is the author\'s diagnostic choice, not a medal guarantee.',
            'Matching replay actions is not proof of private source-code disclosure; the author notes deterministic early turns.'
        ],
    },
    {
        'ref': 'destbreso/how-reliable-is-the-public-leaderboard',
        'old_dir': None,
        'takeaways': [
            'Dense score bands magnify rank changes; aggregate board reliability does not make a medal-edge position safe.',
            'The author expressly distinguishes band-level retention frequencies from the probability of an individual team.'
        ],
        'boundaries': [
            'This analyzes 327 selected historical Kaggle competitions, not a fitted Kaggriculture final-ranking model.',
            'It cannot provide our individual silver probability, and some corrections require the final private board.',
            'The article flags episode-based agent competitions whose public/private boards are identical as a different case. That general remark does not verify Kaggriculture final evaluation rules.'
        ],
    },
    {
        'ref': 'kirderf/kaggriculture-leaderboard-viewer',
        'old_dir': None,
        'takeaways': [
            'Display full-board snapshots, official medal boundaries, time in each medal zone, rank/score movement and locked-submission movement.',
            'Track both the score gap and rank gap to the silver boundary while agents continue playing.'
        ],
        'boundaries': [
            'This is a dashboard, not a new competitive agent.',
            'The source contains no Bradley-Terry fitting, bootstrap or uncertainty calculation.',
            'Its default watched team is Kirderf; our TeamId16908623 and submission IDs56649860/56713491 do not occur in source.',
            'No existing rendered Team42 table or rank uncertainty result was verified. No tracker dataset was downloaded and no third-party code was executed.'
        ],
    },
    {
        'ref': 'raykkretzschmar/kaggriculture-findings-from-zero-to-top-meta',
        'old_dir': 'research/opponent_provenance_1001/sources/raykkretzschmar__kaggriculture-findings-from-zero-to-top-meta',
        'takeaways': [
            'Already public C94/C95 examples protect early feed purchases and advance a bounded portion of existing wheat/fertilizer sales while subtracting it from the next sale.',
            'Use diverse opponents, both seats and frozen held-out seeds, and optimize wins rather than the cash size of already-won matches.'
        ],
        'boundaries': [
            'Current notebook bytes are exactly identical to the copy downloaded on 10/1. C92/C94/C95 are not new this week.',
            'Its reported tournament scores are author-reported local results; reconstructed public action traces may miss original reactive branches.',
            'No proof it matches a competitor\'s current private policy or would lift our locked submission.'
        ],
    },
]

rows = []
for spec in specs:
    ref = spec['ref']
    p = next((HERE/'sources'/ref.replace('/', '__')).glob('*.ipynb'))
    last = runs.get(ref, {}).get('last_run_utc')
    if last:
        last_ny = datetime.fromisoformat(last).replace(tzinfo=timezone.utc).astimezone(NY).isoformat()
    else:
        last_ny = None
    old_dir = spec.pop('old_dir')
    old = next((ROOT/old_dir).glob('*.ipynb')) if old_dir else None
    rows.append(dict(spec,
                     url='https://www.kaggle.com/code/'+ref,
                     last_run_new_york=last_ny,
                     notebook_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                     cell_source_sha256=hashlib.sha256(source_text(p).encode()).hexdigest(),
                     previous_source=old.relative_to(ROOT).as_posix() if old else None,
                     same_cell_source_as_previous=source_text(old)==source_text(p) if old else None,
                     same_notebook_bytes_as_previous=old.read_bytes()==p.read_bytes() if old else None))

summary = {
    'checked_utc': metadata['checked_utc'],
    'checked_new_york': metadata['checked_new_york'],
    'scope': {'recent_run_list_count': 100, 'historical_code_score_list_count': 30,
              'downloaded_sources': 5, 'executed_third_party_code': False},
    'metadata_findings': {
        'runs_after_2026_10_01': [k['ref'] for k in metadata['changed_recent'] if k['last_run_utc'].startswith('2026-10')],
        'other_list_membership_change': 'evgendvorkin/kaggriculture is dated 9/30 and is not a post-deadline update.',
        'top30_version_changes': 0,
        'score_caution': metadata['caution']},
    'conclusion': 'Visible updates mainly refresh diagnostics and rankings. No verified new competitive-agent breakthrough appears in this bounded scan. Silver assessment should use the official live board and actual per-episode trend, not these notebooks\' generic retention formula or historical Code-page scores.',
    'notebooks': rows,
    'raw_public_sources': 'Kept locally under sources/; do not export third-party notebook source, raw lists or downloaded metadata.',
}
(HERE/'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'checked_new_york': summary['checked_new_york'], 'notebooks': len(rows),
                  'top30_version_changes': 0,
                  'unchanged_sources': [r['ref'] for r in rows if r['same_cell_source_as_previous'] is True]}, ensure_ascii=False))
