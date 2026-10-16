r"""Dump unit-action differences between a team and the reference agent for chosen steps of one harvested game.
    .venv\Scripts\python.exe gold\front\unitdiff.py GAME_ID TEAM FROM TO [--ref PATH]"""
import sys, glob, gzip, json, copy, os
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools')
import fastarena, forceshops
if __name__ == '__main__':
    gid, team, lo, hi = int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    ref_path = sys.argv[6] if len(sys.argv) > 6 else 'research/panel/cha22/main.py'
    rec = None
    for p in glob.glob('gold/front/front_*.jsonl.gz'):
        for l in gzip.open(p, 'rt', encoding='utf-8'):
            if l.strip():
                r = json.loads(l)
                if r['id'] == gid: rec = r
    me = rec['teams'].index(team)
    forceshops.force(rec['shops'])
    tapes = [[rec['acts'][s][t + 1] if t + 1 < len(rec['acts'][s]) else None for t in range(719)] for s in range(2)]
    ref = fastarena.load_agent(ref_path)
    OUT = []
    PASS = {"farmer": ["PASS"], "hands": [], "market": []}
    def tape(seat):
        def f(obs, conf=None):
            t = int(obs['step'])
            a = tapes[seat][t]
            a = json.loads(json.dumps(a)) if isinstance(a, dict) else dict(PASS)
            if seat == me:
                r = ref(copy.deepcopy(obs), conf)
                if lo <= t <= hi:
                    ua = [a.get('farmer')] + list(a.get('hands') or [])
                    ur = [r.get('farmer')] + list(r.get('hands') or [])
                    pos = [tuple(obs['farms'][me]['farmer'])] + [tuple(h) for h in obs['farms'][me].get('hands', [])]
                    diff = [(i, pos[i] if i < len(pos) else None, ur[i] if i < len(ur) else None, ua[i] if i < len(ua) else None)
                            for i in range(max(len(ua), len(ur))) if (ua[i] if i < len(ua) else None) != (ur[i] if i < len(ur) else None)]
                    if diff:
                        OUT.append(f"s{t} d{t // 24}h{t % 24:02d} units {len(ua)} vs ref {len(ur)}: " + "; ".join(f"u{i}@{p} ref {x} team {y}" for i, p, x, y in diff[:6]))
                    if a.get('market') != r.get('market'):
                        OUT.append(f"      market ref {r.get('market')} team {a.get('market')}")
            return a
        return f
    fastarena.run_game(tape(0), tape(1), rec["seed"])
    print(chr(10).join(OUT))
