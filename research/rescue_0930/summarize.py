"""Summarize immutable paired evaluations without exporting private replay data."""
import hashlib
import json
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'research/carrera'))
import ab_replay

BASE = ROOT / 'submissions/V12_AventadorSVJ/main.py'
CAND = HERE / 'candidates/input_adaptive94_combined_v1/main.py'
EXPECTED = '3b6a78997364b12f0cca080ff657c31acd1cd087bcfb5f8362e41da69a137f87'


def lines(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines()]


def paired(base, cand):
    assert set(base) == set(cand), 'Incomplete paired evaluation'
    ids = sorted(base)
    return {
        'n': len(ids),
        'baseline_wins': sum(base[k]['margin'] > 0 for k in ids),
        'candidate_wins': sum(cand[k]['margin'] > 0 for k in ids),
        'flips_up': [k for k in ids if base[k]['margin'] <= 0 < cand[k]['margin']],
        'flips_down': [k for k in ids if cand[k]['margin'] <= 0 < base[k]['margin']],
        'mean_margin_change': round(statistics.mean(cand[k]['margin'] - base[k]['margin'] for k in ids), 2),
        'changed': sum(base[k]['margin'] != cand[k]['margin'] for k in ids),
        'not_done': sum(r['status'] != ['DONE', 'DONE'] for table in (base, cand) for r in table.values()),
    }


def from_raw(path, base_path, cand_path, count):
    raw = lines(path)
    key = lambda r: (r['rival'], r['seed']) if 'rival' in r else r['id']
    b = {key(r): r for r in raw if r['path'] == str(base_path)}
    c = {key(r): r for r in raw if r['path'] == str(cand_path)}
    assert len(b) == len(c) == count
    return b, c


def main():
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (BASE, CAND)}
    assert hashes[str(CAND.relative_to(ROOT))] == EXPECTED
    recs = ab_replay.tapes()
    ids = set(recs)
    assert len(ids) == 1528
    b = {r['id']: r for r in lines(ROOT / 'research/carrera/results' / (hashes[str(BASE.relative_to(ROOT))][:12] + '.jsonl')) if r['id'] in ids}
    c = {r['id']: r for r in lines(ROOT / 'research/carrera/results' / (EXPECTED[:12] + '.jsonl')) if r['id'] in ids}
    report = {'engine': '1.32.7', 'forced_shops': True, 'sha256': hashes, 'archive1528': paired(b, c)}
    for name, count in (('latest20', 20), ('holdout24', 24)):
        bb, cc = from_raw(HERE / ('input_adaptive_combined_' + name + '.jsonl'), BASE, CAND, count)
        report[name] = paired(bb, cc)
        for k in bb:
            if k in b:
                assert b[k]['margin'] == bb[k]['margin'] and c[k]['margin'] == cc[k]['margin']
            b[k], c[k] = bb[k], cc[k]
        report[name]['max_step_seconds'] = max(r['t_max'] for r in cc.values())
        report[name]['agent_errors'] = sum(sum(r['errors']) for r in cc.values())
    report['all_unique_replays'] = paired(b, c)
    report['recent300'] = json.loads((HERE / 'input_adaptive_combined_screen300_summary.json').read_text())['summaries'][1]
    report['recent300']['path'] = str(CAND.relative_to(ROOT))
    for name, file, count in (('reactive312', 'input_adaptive_panel312.jsonl', 312),
                              ('reactive_public48', 'input_adaptive_public48.jsonl', 48)):
        bb, cc = from_raw(HERE / file, BASE, CAND, count)
        report[name] = paired(bb, cc)
    bb, cc = from_raw(HERE / 'input_roi_physical112.jsonl', HERE / 'production_only/base/main.py', HERE / 'production_only/combined/main.py', 112)
    report['physical112'] = paired(bb, cc)
    official = (HERE / 'input_adaptive_combined_official.log').read_text().splitlines()[-1]
    report['official_environment'] = official
    gates = [report[n] for n in ('all_unique_replays', 'reactive312', 'reactive_public48', 'physical112')]
    report['passes_release_gate'] = (
        report['all_unique_replays']['candidate_wins'] > report['all_unique_replays']['baseline_wins']
        and all(not g['flips_down'] and not g['not_done'] for g in gates)
        and "['DONE', 'DONE']" in official and 'steps 720' in official
    )
    (HERE / 'release_summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
