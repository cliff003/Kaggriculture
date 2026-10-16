"""Seal the validated adaptive-input candidate. Never upload or replace a live agent."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'submissions/v12_19_own_cha22_adaptive_inputs'
SOURCE = ROOT / 'submissions/v12_18_own_cha22_cash_tomato_late'
EXPECTED = '3b6a78997364b12f0cca080ff657c31acd1cd087bcfb5f8362e41da69a137f87'


def main():
    report = json.loads((HERE / 'release_summary.json').read_text())
    assert report['passes_release_gate'], 'Validation gate failed'
    assert not OUT.exists(), 'Never overwrite a versioned package'
    code = (HERE / 'candidates/input_adaptive94_combined_v1/main.py').read_bytes()
    assert hashlib.sha256(code).hexdigest() == EXPECTED
    note = (SOURCE / 'NOTICE.txt').read_bytes() + (
        '\nTeam 42, 2026-09-30, local candidate v12_19: retain the v12_18 cash-reserve and late '
        'tomato-crew changes. For the existing R51 supplementary fertilizer tours, observe public '
        'farm-layout similarity at steps 264, 272 and 280. At step 287 freeze the decision: only '
        'when all three similarities are below 0.94, use a gross-benefit gate of 1.0 times input '
        'cost plus 20 and a path penalty of 0.75 times fertilizer cost. Otherwise keep the '
        'original 1.5 times cost plus 50 and 1.5 path penalty. Keep the original two-worker '
        'limit and complete upstream entry chain. No opponent identities, replay IDs, seeds or '
        'future shops are used. This package has not been uploaded.\n'
    ).encode()
    files = {'main.py': code, 'LICENSE.txt': (SOURCE / 'LICENSE.txt').read_bytes(), 'NOTICE.txt': note}
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode='wb', mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode='w') as tar:
            for name, data in files.items():
                info = tarfile.TarInfo(name)
                info.size = len(data); info.mode = 0o644; info.mtime = 0
                tar.addfile(info, io.BytesIO(data))
    blob = buffer.getvalue()
    with tarfile.open(fileobj=io.BytesIO(blob), mode='r:gz') as tar:
        assert {m.name for m in tar.getmembers()} == set(files)
        for name, data in files.items():
            assert tar.extractfile(name).read() == data
    OUT.mkdir(parents=True)
    for name, data in files.items():
        (OUT / name).write_bytes(data)
    (OUT / 'submission.tar.gz').write_bytes(blob)
    manifest = {
        'main_sha256': EXPECTED, 'archive_sha256': hashlib.sha256(blob).hexdigest(),
        'path': str(OUT.relative_to(ROOT)), 'submitted': False,
        'would_displace': 'V10_CarreraGT (56633607)',
    }
    (HERE / 'package_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
