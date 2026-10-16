"""Seal the locally validated combined candidate. Never uploads."""
import gzip
import hashlib
import io
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'submissions/v12_18_own_cha22_cash_tomato_late'
SOURCE = ROOT / 'submissions/V12_AventadorSVJ'
EXPECTED_MAIN = 'a63ac3394d273b6d4e3a699e0f44febf9cb9d476774368a6245d93cfe43ebb85'


def main():
    assert not OUT.exists(), 'Never overwrite a versioned package'
    main_code = (HERE / 'prototypes/combined/main.py').read_bytes()
    assert hashlib.sha256(main_code).hexdigest() == EXPECTED_MAIN
    note = (SOURCE / 'NOTICE.txt').read_bytes() + (
        '\n\nTeam 42, 2026-09-30, local candidate v12_18: preserve cash for day-11 sheep expansion '
        'under the documented v12_17 yarn-store and price conditions. '
        'When the existing 18-tomato plan is active, use four 5/5/4/4 crop crews only on days 27-29, '
        'supply enough fertilizer for 18 plants, and split the day-27 fertilizer work into two nine-cell groups. '
        'Source modifications were evaluated locally; this package has not been uploaded.\n').encode()
    files = {'main.py': main_code, 'NOTICE.txt': note,
             'LICENSE.txt': (SOURCE / 'LICENSE.txt').read_bytes()}
    OUT.mkdir(parents=True)
    for name, data in files.items():
        (OUT / name).write_bytes(data)
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode='wb', mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode='w') as tar:
            for name, data in files.items():
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mode = 0o644
                info.mtime = 0
                tar.addfile(info, io.BytesIO(data))
    (OUT / 'submission.tar.gz').write_bytes(buffer.getvalue())
    for name in ('main.py', 'submission.tar.gz'):
        print(name, hashlib.sha256((OUT / name).read_bytes()).hexdigest())
    print(OUT)


if __name__ == '__main__':
    main()
