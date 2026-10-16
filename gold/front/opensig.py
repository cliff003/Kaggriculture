r"""Opening signature (first 12 steps of unit op names) of local agents vs the opponents that beat us live.
    .venv\Scripts\python.exe gold\front\opensig.py AGENT.py [AGENT.py ...]"""
import sys, gzip, json, collections, io, contextlib
sys.path.insert(0, 'tools'); sys.path.insert(0, 'gold/front')
from classify import sig
if __name__ == '__main__':
    import fastarena
    live = {}
    for f in ('data/games/live_v8.jsonl.gz', 'data/games/live_v9.jsonl.gz'):
        for l in gzip.open(f, 'rt', encoding='utf-8'):
            r = json.loads(l)
            if '42' not in r['teams']:
                continue
            me = r['teams'].index('42')
            s = sig(r['acts'][1 - me])
            live.setdefault(s, []).append((r['teams'][1 - me], r['rewards'][me] - r['rewards'][1 - me]))
    for path in sys.argv[1:]:
        acts = []
        f = fastarena.load_agent(path)
        def rec(obs, conf=None, _f=f):
            a = _f(obs, conf)
            acts.append(a)
            return a
        g = fastarena.load_agent('research/panel/cha22/main.py')
        with contextlib.redirect_stdout(io.StringIO()):
            fastarena.run_game(rec, g, 70003, episode_steps=20)
        s = sig([None] + acts)
        hits = live.get(s, [])
        print(path, '| matches live opponents:', len(hits), hits[:8])
        print('   ', s[:150])
