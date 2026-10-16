r"""Build v12_16: v12_15 plus the STRAWX layer (a strawberry block in the south-east quadrant in strawberry-rich worlds).

    .venv/bin/python gold/front/pack_v12_16.py [OUT_DIR] [MIN_STR4=4] [CASH=9000] [HANDS=1] [PLANT_HANDS=4] [HARVEST_HANDS=3]

9/28 audit (scratchpad strawpot.py / strawgate.py): in worlds with 6+ strawberry shops the strawberry quote on the late
harvest days is 175-257 (base 120), and the three unlocked quadrants are full from day 12 on. The base never buys the
south-east quadrant unless V219 (tomatoes, 4+ tomato shops) or V233 (sheep, 2+ yarn stores) does. STRAWX: on day 13
hour 0, with the quadrant still locked, at least MIN_STR4 strawberry shops (smoothie / ice cream / brunch / farmers
market) among the four shops open and enough cash, it buys the quadrant and 16 strawberry seeds at hour 1, hires its own
hands (after the route's hires), plants and waters 16 cells next to the shed the same day, waters each cell every other day (a
strawberry only weeds after two unwatered days; hires cost fib(n) of the day's hire count, so every extra hand is dear),
harvests on days 25, 27 and 29 (loads small enough to be carried to the shed the same day: the day-end deposit serves
our hands last, so anything they still carry is what overflows) and carries the fruit to the shed when there is room. Gate 4 of 4 because 3-of-4 worlds often end with 5 or fewer strawberry shops, where the block loses money. V219 / V233 stay off by their own rules once the quadrant is
unlocked. FADE's restock keeps room for what the crew carries. Marginal-revenue estimate on 163 live replays: +18k gross,
+10k net per game, 16 of 22 losses flippable.
"""
import hashlib
import io
import os
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(ROOT, "submissions", "v12_15_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room_cap40_x18g")
TAG = "v12_16"

LAYER = r'''

# ---------------------------------------------------------------------------
# Team 42 STRAWX layer (__TAG__): strawberry block in the south-east quadrant in strawberry-rich worlds (gold/front/pack_v12_16.py).
_SW_CFG = __CFG__
_SW_TILES = [(x, 5) for x in range(6, 10)] + [(x, 6) for x in range(9, 5, -1)] + [(x, 7) for x in range(6, 10)] + \
            [(x, 8) for x in range(9, 5, -1)]   # 16 cells (x 6-9, rows 5-8) next to the shed; one hand waters half of them a day
_SW_STR_SHOPS = ("SMOOTHIE_SHOP", "ICE_CREAM_SHOP", "BRUNCH_SPOT", "FARMERS_MARKET")
_SW_HARVEST_DAYS = (25, 27, 29)   # small loads that the crew can carry to the shed the same day (the day-end deposit puts our hands last)
_SW_SHED = ((4, 4), (5, 4), (4, 5), (5, 5))
_SW_STATE = {}
_STRAWX_CARRY = {}
_SW_REPORT = {"armed": 0, "bought": 0, "hires": 0, "hire_short": 0, "plants": 0, "waters": 0, "harvests": 0, "drops": 0, "drop_waits": 0}


def _sw_state(seat, step):
    st = _SW_STATE.get(seat)
    if st is None or step <= st["step"]:
        st = _SW_STATE[seat] = {"step": -1, "armed": False, "bought": False, "day": -1, "workers": [], "pending": None,
                                "cursor": {}, "done": {}}
        _STRAWX_CARRY[seat] = 0
    st["step"] = step
    return st


def _sw_move_toward(pos, target):
    x, y = pos
    tx, ty = target
    if x < tx:
        return ["EAST"]
    if x > tx:
        return ["WEST"]
    if y < ty:
        return ["SOUTH"]
    if y > ty:
        return ["NORTH"]
    return None


def _sw_hand_plan(obs, seat, st, idx, tiles, day, hour, shed_room):
    """One hand's action for this step. Planting day: plant + water every tile of its chunk. Other days: water the tiles
    whose turn it is (each tile every other day; a strawberry only weeds after two unwatered days). Harvest days: harvest
    every tile with fruit, plus the day's watering. Then carry the fruit to the shed when there is room."""
    farm = obs["farms"][seat]
    hands = farm["hands"]
    if idx - 1 >= len(hands):
        return ["PASS"]
    pos = tuple(hands[idx - 1])
    invs = obs["private"]["inventories"]
    inv = invs[idx] if idx < len(invs) else {}
    carried = int(inv.get("STRAWBERRY", 0))
    cur = st["cursor"].setdefault(idx, 0)
    plant_day = day == st["plant_day"]
    harvest_day = day in _SW_HARVEST_DAYS
    while cur < len(tiles):
        i, (tx, ty) = tiles[cur]
        tile = farm["tiles"][ty][tx]
        is_plant = isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "STRAWBERRY"
        due = (i < len(_SW_TILES) // 2) == (day % 2 == 0)   # first half on even days, second half on odd days: each cell every other day, neighbours together
        need = None
        if plant_day:
            if tile is None and int(obs["private"]["seeds"].get("STRAWBERRY", 0)) > 0 and hour <= 21:   # a plant must be watered the same day
                need = "PLANT"
            elif is_plant and not tile.get("watered_today"):
                need = "WATER"
        elif is_plant:
            if harvest_day and int(tile.get("yield_units", 0)) > 0:
                need = "HARVEST"
            elif due and not tile.get("watered_today") and day < 29:   # nothing grows after the last day
                need = "WATER"
        if need is None:
            cur += 1
            continue
        st["cursor"][idx] = cur
        mv = _sw_move_toward(pos, (tx, ty))
        if mv is not None:
            return mv
        if need == "PLANT":
            _SW_REPORT["plants"] += 1
            return ["PLANT", "STRAWBERRY"]
        if need == "WATER":
            _SW_REPORT["waters"] += 1
            return ["WATER"]
        _SW_REPORT["harvests"] += 1
        return ["HARVEST"]
    st["cursor"][idx] = cur
    if carried > 0 and hour <= 22:
        if pos in _SW_SHED:
            if shed_room >= carried:
                _SW_REPORT["drops"] += 1
                return ["DROP"]
            _SW_REPORT["drop_waits"] += 1
            return ["PASS"]
        return _sw_move_toward(pos, (5, 5)) or ["PASS"]
    return ["PASS"]


def _strawx(obs, action):
    step = int(obs["step"])
    day, hour = divmod(step, 24)
    seat = int(obs["player"])
    st = _sw_state(seat, step)
    if not isinstance(action, dict) or step >= 718:
        return action
    farm = obs["farms"][seat]
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, (list, tuple))]
    live = [o for o in market if o]
    commands = [list(action.get("farmer") or ["PASS"])] + [list(c) for c in (action.get("hands") or [])]
    while len(commands) < 1 + len(farm["hands"]):
        commands.append(["PASS"])
    changed = False
    shops = list(obs["town"]["unlocked_shops"])
    # day-13 hour-0 decision
    if not st["armed"] and not st["bought"] and day == _SW_CFG["DAY"] and hour == 0:
        se_locked = farm["tiles"][7][7] == "LOCKED" and set(farm["unlocked_quadrants"]) == {"NW", "NE", "SW"}
        n_str = sum(1 for s in shops[:4] if s in _SW_STR_SHOPS)
        cash = float(farm.get("money", 0))
        if se_locked and n_str >= _SW_CFG["MIN_STR4"] and cash >= _SW_CFG["CASH"] + 4000 + 100 * len(_SW_TILES):
            st["armed"] = True
            _SW_REPORT["armed"] += 1
    if st["armed"] and not st["bought"] and day == _SW_CFG["DAY"] and hour >= 1:
        k = _SW_CFG["PLANT_HANDS"]
        if len(live) + 2 + k <= 10:
            hires_before = sum(1 for o in live if o[0] == "HIRE")
            market = live + [["BUY_LAND"], ["BUY_SEED", "STRAWBERRY", len(_SW_TILES)]] + [["HIRE"]] * k
            st["bought"] = True
            st["plant_day"] = day
            st["pending"] = (len(farm["hands"]) + hires_before, k, step)
            st["day"] = day
            _SW_REPORT["bought"] += 1
            _SW_REPORT["hires"] += k
            changed = True
    if st["bought"]:
        # daily hires (the hands are dismissed every night): hour 1, after the route's hour-0 hires; the hands hired at
        # step s exist from step s + 1, so a pending hire is resolved one step later
        if st["day"] != day:
            st["day"], st["workers"], st["pending"], st["cursor"] = day, [], None, {}
        if st["pending"] is not None and st["pending"][2] < step:
            n0, k, _ = st["pending"]
            st["pending"] = None
            got = len(farm["hands"]) - n0
            if got < k:
                _SW_REPORT["hire_short"] += 1
            got = max(0, min(k, got))
            st["workers"] = list(range(len(farm["hands"]) - got + 1, len(farm["hands"]) + 1))   # unit indices (0 = farmer)
        elif st["pending"] is None and not st["workers"] and day > st["plant_day"] and day <= 29 and 1 <= hour <= 3:
            k = _SW_CFG["HARVEST_HANDS"] if day in _SW_HARVEST_DAYS else _SW_CFG["HANDS"]
            if len(live) + k <= 10:
                hires_before = sum(1 for o in live if o[0] == "HIRE")
                market = live + [["HIRE"]] * k
                st["pending"] = (len(farm["hands"]) + hires_before, k, step)
                _SW_REPORT["hires"] += k
                changed = True
        if st["workers"]:
            k = len(st["workers"])
            all_tiles = list(enumerate(_SW_TILES))
            if day == st["plant_day"] or day in _SW_HARVEST_DAYS:
                todo = all_tiles
            else:
                todo = [(i, t) for i, t in all_tiles if (i < len(_SW_TILES) // 2) == (day % 2 == 0)]
            sz = (len(todo) + k - 1) // k
            try:
                pshed = _project(obs, dict(action, market=live))[0]
                shed_total = sum(int(v) for v in pshed.values() if int(v) > 0)
            except Exception:
                shed_total = sum(int(v) for v in obs["private"]["shed"].values() if int(v) > 0)
            room = 100 - shed_total - 3
            for j, idx in enumerate(st["workers"]):
                if idx < len(commands):
                    commands[idx] = _sw_hand_plan(obs, seat, st, idx, todo[j * sz:(j + 1) * sz], day, hour, room)
                    if commands[idx] == ["DROP"]:
                        room -= int((obs["private"]["inventories"][idx] if idx < len(obs["private"]["inventories"]) else {}).get("STRAWBERRY", 0))
                    changed = True
        invs = obs["private"]["inventories"]
        _STRAWX_CARRY[seat] = sum(int(v) for idx in st["workers"] if idx < len(invs) for v in invs[idx].values() if int(v) > 0)
    if not changed:
        return action
    out = dict(action)
    out["farmer"], out["hands"], out["market"] = commands[0], commands[1:], market[:10]
    return out


_PRE_STRAWX_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    action = _PRE_STRAWX_AGENT(observation, configuration)
    try:
        return _strawx(observation, action)
    except Exception:
        return action
'''

EDITS = [
    # FADE's restock reserve keeps room for what the strawberry crew carries
    ('        return int(min(carried_all, reserve))\n',
     '        return int(min(carried_all, reserve + int(globals().get("_STRAWX_CARRY", {}).get(seat, 0))))   # v12_16: the strawberry crew\'s load\n'),
]


def main():
    args = [x for x in sys.argv[1:] if "=" not in x]
    kv = dict(x.split("=", 1) for x in sys.argv[1:] if "=" in x)
    cfg = {"DAY": 13, "MIN_STR4": int(kv.get("MIN_STR4", 4)), "CASH": int(kv.get("CASH", 9000)), "HANDS": int(kv.get("HANDS", 1)),
           "PLANT_HANDS": int(kv.get("PLANT_HANDS", 4)), "HARVEST_HANDS": int(kv.get("HARVEST_HANDS", 3))}
    out_dir = args[0] if args else os.path.join(
        ROOT, "submissions", "v12_16_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room_cap40_x18g_strawx")
    raw = open(os.path.join(SRC, "main.py"), "rb").read()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8").replace("\r\n", "\n")
    assert "_STRAWX" not in s
    for old, new in EDITS:
        assert s.count(old) == 1, old[:60]
        s = s.replace(old, new)
    s = s.rstrip("\n") + "\n" + LAYER.replace("__CFG__", repr(cfg)).replace("__TAG__", TAG)
    compile(s, "main.py", "exec")
    ns = {"__name__": "cand_check"}
    exec(compile(s, "main.py", "exec"), ns)
    last = [v for v in ns.values() if callable(v)][-1]
    assert getattr(last, "__name__", "") == "agent", last
    main = (s.replace("\n", "\r\n") if crlf else s).encode("utf-8")
    assert b"C:\\Users" not in main and b"/Users/cliff/" not in main
    notice = open(os.path.join(SRC, "NOTICE.txt"), "rb").read()
    h, rest = notice.split(b"\n\n", 1)
    h = h + (f" In {TAG} a strawberry block layer buys the south-east quadrant on day 13 in strawberry-rich worlds (all of the first four shops "
             f"are smoothie / ice cream / brunch / farmers market), plants 16 strawberries with its own hired hands, waters them every other day and "
             f"harvests on days 25, 27 and 29.").encode()
    notice = h + b"\n\n" + rest
    lic = open(os.path.join(SRC, "LICENSE.txt"), "rb").read()
    os.makedirs(out_dir, exist_ok=True)
    members = [("main.py", main), ("LICENSE.txt", lic), ("NOTICE.txt", notice)]
    for n, d in members:
        open(os.path.join(out_dir, n), "wb").write(d)
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for n, d in members:
            info = tarfile.TarInfo(n)
            info.size = len(d)
            info.mode = 0o644
            info.mtime = 0
            tar.addfile(info, io.BytesIO(d))
    open(os.path.join(out_dir, "submission.tar.gz"), "wb").write(buf.getvalue())
    print("out", out_dir, "cfg", cfg)
    print("main.py", hashlib.sha256(main).hexdigest())
    print("tar.gz", hashlib.sha256(buf.getvalue()).hexdigest())


if __name__ == "__main__":
    main()
