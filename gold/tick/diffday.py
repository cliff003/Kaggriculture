r"""Replay one live game (opponent tape) with BASE and CAND; print per-day diffs of our side.
    .venv\Scripts\python.exe gold\tick\diffday.py GAME_ID BASE.py CAND.py"""
import sys, glob, gzip, json, os
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools')
import gstat
from cfroute import tape_file
if __name__ == '__main__':
    gid, base, cand = int(sys.argv[1]), sys.argv[2], sys.argv[3]
    rec = None
    for f in sorted(glob.glob('data/games/live_*.jsonl.gz')):
        for line in gzip.open(f, 'rt', encoding='utf-8'):
            r = json.loads(line)
            if r['id'] == gid:
                rec = r; break
        if rec: break
    me = rec['teams'].index('42')
    tape = tape_file(rec, 1 - me)
    out = []
    for p in (base, cand):
        seats = (p, tape) if me == 0 else (tape, p)
        out.append(gstat.play_one((seats[0], seats[1], rec['seed'], me, rec['shops'])))
    print('opp', rec['teams'][1 - me], 'rewards base', out[0]['rewards'], 'cand', out[1]['rewards'])
    keys = ['overflow_drop', 'overflow_eod', 'escapes', 'plant_deaths', 'rot_units', 'invalid', 'min_money', 'hires', 'sell_rev', 'buy_spend']
    for d in range(30):
        a, b = out[0]['days'][me][d], out[1]['days'][me][d]
        diffs = []
        for k in keys:
            if a.get(k) != b.get(k):
                diffs.append(f"{k}: {a.get(k)} -> {b.get(k)}")
        ea, eb = a.get('end') or {}, b.get('end') or {}
        line = f"d{d:2d} money {ea.get('money')} -> {eb.get('money')}"
        if ea.get('animals') != eb.get('animals'): line += f" animals {ea.get('animals')} -> {eb.get('animals')}"
        print(line)
        for x in diffs:
            if 'sell_rev' in x or 'buy_spend' in x: continue
            print('     ', x)
