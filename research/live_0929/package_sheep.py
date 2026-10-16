"""Seal the validated local cash-reserve candidate. Does not upload anything."""
import gzip
import hashlib
import io
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'submissions/v12_17_own_cha22_sheep_cash_reserve'
SOURCE = ROOT / 'submissions/V12_AventadorSVJ'


def main():
    assert not OUT.exists(), 'Never overwrite a versioned package'
    main_code = (HERE / 'prototypes/sheep_cash/main.py').read_bytes()
    assert hashlib.sha256(main_code).hexdigest() == '524bc579c960902ab24b199ea1d319352c0aea3ac39450dc294dc0186ee18a58'
    note = (SOURCE / 'NOTICE.txt').read_bytes() + (
        '\n\nTeam 42, 2026-09-29, v12_17: preserve cash for the existing day-11 six-sheep expansion. '
        'Skip the single phase-1 FADE restock at day 11 hour 1 when at least two yarn stores are open, '
        'the south-east quadrant is still locked, wool is at least 220 and wheat at most 45. '
        'The production plan and all other market steps are unchanged. Local candidate only.\n').encode()
    files = {'main.py': main_code, 'NOTICE.txt': note, 'LICENSE.txt': (SOURCE / 'LICENSE.txt').read_bytes()}
    OUT.mkdir(parents=True)
    for name, data in files.items():
        (OUT / name).write_bytes(data)
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode='wb', mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode='w') as tar:
            for name, data in files.items():
                info = tarfile.TarInfo(name)
                info.size = len(data); info.mode = 0o644; info.mtime = 0
                tar.addfile(info, io.BytesIO(data))
    (OUT / 'submission.tar.gz').write_bytes(buffer.getvalue())
    for name in ('main.py', 'submission.tar.gz'):
        print(name, hashlib.sha256((OUT / name).read_bytes()).hexdigest())
    print(OUT)


if __name__ == '__main__':
    main()
