r"""Economic breakdown of harvested games by exact local re-simulation.

.venv\Scripts\python.exe tools\econ.py GAMES.jsonl.gz --id EPISODE_ID        one game, both sides
.venv\Scripts\python.exe tools\econ.py GAMES.jsonl.gz --team NAME [--vs]     averages over games

Both sides' recorded actions go through the real interpreter with the record's seed. Every
market transaction, hire and land purchase is logged, farms are snapshotted at the end of each
day, and the local final money is checked against the server reward.
"""
import argparse
import collections
import gzip
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kg


def _quiet_import():
    # kaggle_environments prints OpenSpiel game lists from C++ on import; silence fds 1 and 2
    sys.stdout.flush()
    sys.stderr.flush()
    saved = os.dup(1), os.dup(2)
    null = os.open(os.devnull, os.O_WRONLY)
    os.dup2(null, 1)
    os.dup2(null, 2)
    try:
        from kaggle_environments import make
        from kaggle_environments.envs.kaggriculture import kaggriculture
    finally:
        os.dup2(saved[0], 1)
        os.dup2(saved[1], 2)
        os.close(null)
    return make, kaggriculture


make, K = _quiet_import()

ITEMS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]
_CUR = {}
_orig = {"commit": K._commit_unit, "hire": K._do_hire, "land": K._do_buy_land}


def _player(farm):
    return 0 if farm is _CUR["farms"][0] else 1


def _commit(op, item, price, farm, private, market, shed_capacity=100):
    ok = _orig["commit"](op, item, price, farm, private, market, shed_capacity)
    if ok:
        _CUR["log"].append((_CUR["step"], _player(farm), op, item, price))
    return ok


def _hire(farm, private, board_size, mult=1):
    before = farm["money"]
    _orig["hire"](farm, private, board_size, mult)
    if farm["money"] != before:
        _CUR["log"].append((_CUR["step"], _player(farm), "HIRE", "", before - farm["money"]))


def _land(farm, board_size):
    before = farm["money"]
    _orig["land"](farm, board_size)
    if farm["money"] != before:
        _CUR["log"].append((_CUR["step"], _player(farm), "LAND", farm["unlocked_quadrants"][-1], before - farm["money"]))


_orig["drop_eod"] = K._drop_inventories_to_shed
_orig["unit"] = K._apply_unit_action


def _log_lost(p, carried, shed_before, shed):
    # carried units that did not reach a full shed are discarded; value them at the current price
    for item, n in carried.items():
        lost = n - (shed.get(item, 0) - shed_before.get(item, 0))
        if lost > 0:
            _CUR["log"].append((_CUR["step"], p, "LOST", item, lost * _CUR["prices"].get(item, 0)))


def _drop_eod(private, capacity):
    carried = collections.Counter()
    for inv in private["inventories"]:
        carried.update({k: v for k, v in inv.items() if v > 0})
    shed_before = dict(private["shed"])
    _orig["drop_eod"](private, capacity)
    _log_lost(0 if private is _CUR["privates"][0] else 1, carried, shed_before, private["shed"])


def _unit(farm, private, idx, action, *args, **kw):
    is_drop = isinstance(action, list) and action and action[0] == "DROP" and idx < len(private["inventories"])
    carried = {k: v for k, v in private["inventories"][idx].items() if v > 0} if is_drop else {}
    shed_before = dict(private["shed"])
    _orig["unit"](farm, private, idx, action, *args, **kw)
    if carried and not private["inventories"][idx]:  # DROP only empties the inventory when shed-adjacent
        _log_lost(_player(farm), carried, shed_before, private["shed"])


K._commit_unit, K._do_hire, K._do_buy_land = _commit, _hire, _land
K._drop_inventories_to_shed, K._apply_unit_action = _drop_eod, _unit


def load(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def tiles(farm):
    c = collections.Counter()
    for row in farm["tiles"]:
        for t in row:
            if isinstance(t, dict):
                c[t.get("animal") or t.get("crop") or t.get("kind")] += 1
    return c


def resim(rec):
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": rec["seed"]}, debug=False)
    env.reset(2)
    state = env.state
    _CUR.update(log=[], farms=state[0].observation.farms, privates=[s.observation.private for s in state],
                prices=state[0].observation.market["prices"])
    days = [[], []]
    n = len(rec["acts"][0])
    for t in range(719):
        _CUR["step"] = t
        for i in range(2):
            a = rec["acts"][i][t + 1] if t + 1 < n else None
            state[i].action = a if isinstance(a, dict) else None
        K.interpreter(state, env)
        state[0].observation.step = t + 1
        if (t + 1) % 24 == 0:
            for i in range(2):
                f = state[0].observation.farms[i]
                days[i].append({"money": f["money"], "tiles": tiles(f), "quads": len(f["unlocked_quadrants"]),
                                "shed": sum(state[i].observation.private["shed"].values())})
    out = []
    for i in range(2):
        sales = collections.defaultdict(lambda: [0, 0.0, [0.0, 0.0, 0.0]])
        spend = collections.Counter()
        lost = collections.Counter()
        land, hires = [], 0
        for step, p, op, item, price in _CUR["log"]:
            if p != i:
                continue
            if op == "LOST":
                lost[item] += price
            elif op == "SELL":
                s = sales[item]
                s[0] += 1
                s[1] += price
                s[2][min(2, step // 240)] += price
            elif op == "HIRE":
                spend["HIRE"] += price
                hires += 1
            elif op == "LAND":
                spend["LAND"] += price
                land.append(step // 24)
            else:
                spend[op.replace("BUY_", "") + ":" + item] += price
        money = state[0].observation.farms[i]["money"]
        out.append({"team": rec["teams"][i], "money": money, "server": rec["rewards"][i], "days": days[i],
                    "sales": {k: v for k, v in sales.items()}, "spend": dict(spend), "land": land, "hires": hires,
                    "lost": dict(lost)})
    return out


def show_game(rec):
    r = resim(rec)
    print(f"episode {rec['id']}  seed {rec['seed']}  shops {rec['shops']}")
    kg.table(["", r[0]["team"], r[1]["team"]],
             [["本地/服务器", f"{r[0]['money']:.0f}/{r[0]['server']:.0f}", f"{r[1]['money']:.0f}/{r[1]['server']:.0f}"],
              ["买地(天)", ",".join(map(str, r[0]["land"])), ",".join(map(str, r[1]["land"]))],
              ["雇工(人次/钱)", f"{r[0]['hires']}/{r[0]['spend'].get('HIRE', 0):.0f}", f"{r[1]['hires']}/{r[1]['spend'].get('HIRE', 0):.0f}"]])
    print()
    rows = []
    for item in ITEMS:
        cells = []
        for s in r:
            u, rev, ph = s["sales"].get(item, [0, 0.0, [0, 0, 0]])
            cells.append(f"{u} x {rev / u:.0f} = {rev:.0f} ({ph[0]:.0f}/{ph[1]:.0f}/{ph[2]:.0f})" if u else "")
        if any(cells):
            rows.append([item] + cells)
    tot = [sum(v[1] for v in s["sales"].values()) for s in r]
    rows.append(["销售合计", f"{tot[0]:.0f}", f"{tot[1]:.0f}"])
    kg.table(["卖出 件x均价=收入(0-9/10-19/20-29天)", r[0]["team"], r[1]["team"]], rows)
    print()
    keys = sorted(set(r[0]["spend"]) | set(r[1]["spend"]))
    kg.table(["支出", r[0]["team"], r[1]["team"]], [[k, f"{r[0]['spend'].get(k, 0):.0f}", f"{r[1]['spend'].get(k, 0):.0f}"] for k in keys])
    print()
    rows = []
    for d in (2, 5, 8, 11, 14, 17, 20, 23, 26, 28):
        rows.append([d] + [f"${s['days'][d]['money']:.0f} q{s['days'][d]['quads']} shed{s['days'][d]['shed']} "
                           + " ".join(f"{k[:3]}{v}" for k, v in sorted(s["days"][d]["tiles"].items())) for s in r])
    kg.table(["天", r[0]["team"], r[1]["team"]], rows)


def show_sales(rec, item):
    r = resim(rec)
    rows = collections.OrderedDict()
    for step, p, op, it, price in _CUR["log"]:
        if it != item or op not in ("SELL", "BUY_PRODUCT"):
            continue
        row = rows.setdefault(step, [[0, 0, 0], [0, 0, 0]])
        cell = row[p]
        cell[0] += 1 if op == "SELL" else -1
        cell[1] = cell[1] or price
        cell[2] = price
    print(f"episode {rec['id']} {item}  {r[0]['team']} vs {r[1]['team']}  shops {rec['shops']}")
    kg.table(["步", "天:时", r[0]["team"] + " 件@首价-末价", r[1]["team"] + " 件@首价-末价"],
             [[s, f"{s // 24}:{s % 24:02d}"] + [f"{c[0]}@{c[1]}-{c[2]}" if c[0] else "" for c in row]
              for s, row in rows.items()])


def show_team(games, team, vs):
    per = collections.defaultdict(list)
    res = collections.Counter()
    for rec in games:
        if team not in rec["teams"]:
            continue
        r = resim(rec)
        me = rec["teams"].index(team)
        for side, key in ((me, "me"), (1 - me, "opp")):
            s = r[side]
            if abs(s["money"] - s["server"]) > 0.5:
                print(f"警告 {rec['id']} 本地 {s['money']} 服务器 {s['server']}", file=sys.stderr)
            per[key].append(s)
        d = r[me]["money"] - r[1 - me]["money"]
        res["胜" if d > 0 else "负" if d < 0 else "平"] += 1
        if vs:
            print(f"{rec['id']} {r[1 - me]['team'][:20]:20s} {d:+8.0f}  me {r[me]['money']:.0f}  shops {','.join(x[:4] for x in rec['shops'])}")
    n = len(per["me"])
    print(f"{team}: {n} 局  胜 {res['胜']} 负 {res['负']} 平 {res['平']}")
    if not n:
        return
    rows = []
    for item in ITEMS + ["合计"]:
        cells = []
        for key in ("me", "opp"):
            if item == "合计":
                rev = [sum(v[1] for v in s["sales"].values()) for s in per[key]]
                cells += ["", f"{statistics.mean(rev):.0f}"]
                continue
            u = [s["sales"].get(item, [0, 0.0])[0] for s in per[key]]
            rev = [s["sales"].get(item, [0, 0.0])[1] for s in per[key]]
            cells += [f"{statistics.mean(u):.0f}", f"{statistics.mean(rev):.0f}"]
        rows.append([item] + cells)
    money = [f"{statistics.mean(s['money'] for s in per[k]):.0f}" for k in ("me", "opp")]
    rows.append(["最终钱", "", money[0], "", money[1]])
    kg.table(["每局平均", "我方件数", "我方收入", "对手件数", "对手收入"], rows)
    print()
    rows = []
    for key in ("me", "opp"):
        land = collections.Counter(len(s["land"]) for s in per[key])
        first = [s["land"][0] for s in per[key] if s["land"]]
        rows.append([key, dict(sorted(land.items())), f"{statistics.mean(first):.1f}" if first else "",
                     f"{statistics.mean(s['hires'] for s in per[key]):.0f}",
                     f"{statistics.mean(s['spend'].get('HIRE', 0) for s in per[key]):.0f}"])
    kg.table(["", "买地块数分布", "第一块地(天)", "雇工人次", "雇工花费"], rows)
    print()
    items = sorted({k for key in ("me", "opp") for s in per[key] for k in s["lost"]})
    rows = [[item] + [f"{statistics.mean(s['lost'].get(item, 0) for s in per[key]):.0f}" for key in ("me", "opp")] for item in items]
    rows.append(["合计"] + [f"{statistics.mean(sum(s['lost'].values()) for s in per[key]):.0f}" for key in ("me", "opp")])
    rows.append(["丢货局数"] + [sum(1 for s in per[key] if s["lost"]) for key in ("me", "opp")])
    kg.table(["仓库满丢货(按当时价, 每局平均)", "我方", "对手"], rows)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("games")
    p.add_argument("--id", type=int)
    p.add_argument("--team")
    p.add_argument("--vs", action="store_true", help="逐局列出对手和差距")
    p.add_argument("--sales", help="配合 --id：列出这个产品的逐步成交")
    a = p.parse_args()
    games = load(a.games)
    if a.id and a.sales:
        show_sales(next(g for g in games if g["id"] == a.id), a.sales)
    elif a.id:
        show_game(next(g for g in games if g["id"] == a.id))
    elif a.team:
        show_team(games, a.team, a.vs)


if __name__ == "__main__":
    main()
