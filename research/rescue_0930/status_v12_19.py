"""Read the official status of the one authorized upload. Never submit anything."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))
import kg


def main():
    api = kg.api()
    submissions = api.competition_submissions('kaggriculture', page_size=200)
    sub = next(s for s in submissions if s.ref == 56713491)
    assert sub.description.startswith('v12_19:')
    status = str(sub.status).split('.')[-1]
    active = sorted(s.id for s in api.competition_team_submissions(16908623))
    local = ROOT / 'submissions/v12_19_own_cha22_adaptive_inputs/submission.tar.gz'
    downloaded = ROOT / 'data/uploads/56713491/submission.tar.gz'
    assert local.read_bytes() == downloaded.read_bytes()
    receipt = {
        'submission_id': sub.ref, 'submitted_at_utc': sub.date.isoformat(),
        'submitted_by': sub.submitted_by, 'official_status': status,
        'public_score': sub.public_score, 'description': sub.description,
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'active_submission_ids': active,
        'server_archive_sha256': hashlib.sha256(downloaded.read_bytes()).hexdigest(),
        'server_copy_matches_local': True,
        'displaced_submission_id': 56633607 if 56713491 in active and 56633607 not in active else None,
    }
    if status == 'COMPLETE':
        assert active == [56649860, 56713491], 'Unexpected active slots; do not submit again'
    (HERE / 'submission_receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    manifest_path = HERE / 'package_manifest.json'
    manifest = json.loads(manifest_path.read_text())
    manifest.update(submitted=True, submission_id=sub.ref, submission_time_utc=receipt['submitted_at_utc'], official_status=status)
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
