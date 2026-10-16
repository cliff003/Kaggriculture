r"""Shared layer library for composite arena agents (team 42).

build(cfg) loads v6 (gold/arena/champ0/main.py) into a fresh namespace, applies cfg["top"] (v6 globals) and
cfg["base"] (embedded cha22 globals), and returns agent(obs, conf) = enabled layers applied to v6's action:

  fert_lead   {"lead": 3, "hours": [19, 20, 21]}   sell now what the tape sells of FERTILIZER in the next `lead` steps
  wheat_lead  {"lead": 2, "hours": [...]}          the same for WHEAT (the base's own sell-lead skips wheat)
  wheat_mm    {"q": 30, "keep": 25}                buy wheat when shops consume (step % 4 == 0), sell it next step
  premium_lead {"lead": 2, "items": [...]}         sell-lead of the tape's next `lead` steps for premium goods
"""
import os

CHAMP0 = r"/Users/cliff/Documents/coding/kaggriculture_handoff_20260927/project/gold/arena/champ0/main.py"


def _g(o, k, d=None):
    if isinstance(o, dict):
        return o.get(k, d)
    return getattr(o, k, d)


def build(cfg):
    ns = {"__name__": "composite_v6"}
    exec(compile(open(CHAMP0, encoding="utf-8").read(), CHAMP0, "exec"), ns)
    return wrap(cfg, ns)


def wrap(cfg, ns):
    """Apply cfg to a namespace holding v6 (its `agent`, `_project` and `_BASE_NS`) and return the layered agent."""
    for k, v in (cfg.get("top") or {}).items():
        ns[k] = v
    for k, v in (cfg.get("base") or {}).items():
        ns["_BASE_NS"][k] = v
    base_agent = ns["agent"]
    chassis = ns["_BASE_NS"]["_IMPL"].chassis
    force = cfg.get("force_route")
    table = cfg.get("route_table")
    late = cfg.get("late_route")
    force_from = int(cfg.get("force_from", 144))
    rules = cfg.get("route_rules") or []
    if force is not None or table or late is not None or rules:
        orig_router = chassis.router

        def router(observation, step, state, _orig=orig_router):
            r = _orig(observation, step, state)
            if late is not None and step >= 648:
                return state.get("_mid_route", r) if late == "keep" else late
            if 144 <= step < 648:
                if rules and step >= 216:
                    shops = list(_g(_g(observation, "town", {}), "unlocked_shops", []) or [])
                    if len(shops) >= 3:
                        for rule in rules:
                            if ("|".join(shops[:2]) == rule["pair"] and shops[2] not in rule.get("third_not", ())
                                    and (not rule.get("third_in") or shops[2] in rule["third_in"])):
                                state["_mid_route"] = rule["route"]
                                return rule["route"]
                if force is not None and step >= force_from:
                    r = force
                elif table:
                    key = state.get("_table_key")
                    if key is None:
                        shops = list(_g(_g(observation, "town", {}), "unlocked_shops", []) or [])[:2]
                        key = state["_table_key"] = "|".join(shops)
                    r = table.get(key, r)
                state["_mid_route"] = r
            return r
        chassis.router = router
    project = ns["_project"]
    layers = cfg.get("layers") or {}
    mm_state = {}

    def planned(route, step, item, lead):
        tape = chassis.routes.get(route) or []
        q = 0
        for t in range(step + 1, min(len(tape), step + 1 + lead)):
            a = tape[t]
            if isinstance(a, dict):
                for o in a.get("market") or []:
                    if o and o[0] == "SELL" and len(o) >= 3 and o[1] == item:
                        q += int(o[2])
        return q

    def planned_pickups(route, step, item, horizon):
        """Units of `item` the tape's units pick up from the shed in steps step+1 .. step+horizon."""
        tape = chassis.routes.get(route) or []
        q = 0
        for t in range(step + 1, min(len(tape), step + 1 + horizon)):
            a = tape[t]
            if isinstance(a, dict):
                for u in [a.get("farmer")] + list(a.get("hands") or []):
                    if isinstance(u, list) and len(u) >= 3 and u[0] == "PICKUP" and u[1] == item:
                        q += int(u[2])
        return q

    lead_debt = {}

    def lead_sell(obs, action, item, lead, hours, front, reserve_h=0, book=False):
        """Sell now what the route tape sells of `item` in the next `lead` steps. reserve_h > 0 keeps back what the
        tape's units pick up from the shed in the next reserve_h steps (feed); book=True subtracts the early sale from
        the tape's own later SELL orders, so the total sold stays the same and only the timing moves."""
        step = int(_g(obs, "step", 0))
        player = int(_g(obs, "player", 0))
        key = (player, item)
        if step == 0:
            lead_debt.pop(key, None)
        if step < 240 or step > 700:
            return action
        st = chassis.players.get(player)
        if not st or st.get("route") is None:
            return action
        market = None
        if book and lead_debt.get(key):
            due_now = sum(n for due, n in lead_debt[key] if due == step)
            lead_debt[key] = [(due, n) for due, n in lead_debt[key] if due > step]
            if due_now > 0:
                market = [list(o) for o in (action.get("market") or []) if isinstance(o, (list, tuple)) and o]
                for o in market:
                    if o[0] == "SELL" and len(o) >= 3 and o[1] == item and due_now > 0:
                        cut = min(int(o[2]), due_now)
                        o[2] = int(o[2]) - cut
                        due_now -= cut
                market = [o for o in market if not (o[0] == "SELL" and len(o) >= 3 and int(o[2]) <= 0)]
                action = dict(action)
                action["market"] = market
        if hours and step % 24 not in hours:
            return action
        plan = planned(st["route"], step, item, lead) - sum(n for due, n in lead_debt.get(key, []))
        if plan <= 0:
            return action
        shed, invs, farm = project(obs, action)
        market = [list(o) for o in (action.get("market") or []) if isinstance(o, list) and o]
        selling = sum(int(o[2]) for o in market if o[0] == "SELL" and len(o) >= 3 and o[1] == item)
        reserve = planned_pickups(st["route"], step, item, reserve_h) if reserve_h else 0
        k = min(plan, int(shed.get(item, 0)) - selling - reserve)
        if k <= 0:
            return action
        if book:
            tape = chassis.routes.get(st["route"]) or []
            left = k
            for t in range(step + 1, min(len(tape), step + 1 + lead)):
                a = tape[t]
                if isinstance(a, dict) and left > 0:
                    q = sum(int(o[2]) for o in (a.get("market") or []) if o and o[0] == "SELL" and len(o) >= 3
                            and o[1] == item)
                    take = min(q, left)
                    if take > 0:
                        lead_debt.setdefault(key, []).append((t, take))
                        left -= take
        for i, o in enumerate(market):
            if o[0] == "SELL" and o[1] == item:
                o[2] = int(o[2]) + k
                if front:
                    market.insert(0, market.pop(i))
                break
        else:
            if len(market) >= 10:
                return action
            if front:
                market.insert(0, ["SELL", item, k])
            else:
                market.append(["SELL", item, k])
        out = dict(action)
        out["market"] = market
        return out

    def wheat_mm(obs, action, q, keep):
        step = int(_g(obs, "step", 0))
        player = int(_g(obs, "player", 0))
        st = mm_state.get(player)
        if st is None or step == 0:
            st = mm_state[player] = {"held": 0, "buy_step": -9, "before": 0}
        market = [list(o) for o in (action.get("market") or []) if isinstance(o, list) and o]
        shed, invs, farm = project(obs, action)
        if st["held"] and step == st["buy_step"] + 1:
            raw = dict(_g(_g(obs, "private", {}) or {}, "shed", {}) or {})
            got = int(raw.get("WHEAT", 0)) - st["before"]
            held = max(0, min(st["held"], got))
            if held > 0:
                market.insert(0, ["SELL", "WHEAT", held])
            st["held"] = 0
        elif 264 <= step <= 688 and step % 4 == 0 and step % 24 < 20 and len(market) < 10:
            room = 100 - sum(shed.values()) - sum(int(o[2]) for o in market if o[0] == "BUY_PRODUCT" and len(o) >= 3)
            money = float(_g(_g(obs, "farms")[player], "money", 0))
            if room >= q + keep and money > 4000:
                market.append(["BUY_PRODUCT", "WHEAT", q])
                st.update(held=q, buy_step=step, before=int(shed.get("WHEAT", 0)))
        out = dict(action)
        out["market"] = market[:10]
        return out

    opp_state = {}
    product_of = {"COW": "MILK", "SHEEP": "WOOL", "GOOSE": "EGG"}

    def opp_race(obs, action, items, min_units, share):
        """Sell our shed stock of a premium good in slot 0 on the step the rival harvests a lot of it: its units
        carry the lot to its shed and sell it a few steps later, so ours reaches the book first."""
        step = int(_g(obs, "step", 0))
        player = int(_g(obs, "player", 0))
        farms = _g(obs, "farms")
        tiles = _g(farms[1 - player], "tiles")
        snap = {}
        for y, row in enumerate(tiles):
            for x, t in enumerate(row):
                if isinstance(t, dict):
                    item = t.get("crop") or product_of.get(t.get("animal"))
                    if item in items:
                        snap[(x, y)] = (item, int(t.get("yield_units", 0) or 0))
        st = opp_state.get(player)
        opp_state[player] = {"step": step, "snap": snap}
        if st is None or st["step"] != step - 1 or step < 240 or step > 710:
            return action
        harvested = {}
        for xy, (item, y0) in st["snap"].items():
            now = snap.get(xy)
            y1 = now[1] if now and now[0] == item else 0
            if y1 < y0:
                harvested[item] = harvested.get(item, 0) + (y0 - y1)
        hot = [i for i, n in harvested.items() if n >= min_units]
        if not hot:
            return action
        shed, invs, farm = project(obs, action)
        market = [list(o) for o in (action.get("market") or []) if isinstance(o, list) and o]
        for item in hot:
            selling = sum(int(o[2]) for o in market if o[0] == "SELL" and len(o) >= 3 and o[1] == item)
            k = int((int(shed.get(item, 0)) - selling) * share)
            if k <= 0:
                continue
            for i, o in enumerate(market):
                if o[0] == "SELL" and o[1] == item:
                    o[2] = int(o[2]) + k
                    market.insert(0, market.pop(i))
                    break
            else:
                if len(market) >= 10:
                    continue
                market.insert(0, ["SELL", item, k])
        out = dict(action)
        out["market"] = market[:10]
        return out

    base_price = {"WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120, "MELON": 250, "EGG": 50, "MILK": 160,
                  "WOOL": 200, "FERTILIZER": 100}

    def hold_premium(obs, action, items, floor, dump_from, min_room):
        """Drop SELL orders of `items` quoted below floor x base while the shed keeps `min_room` free slots."""
        step = int(_g(obs, "step", 0))
        if step < 240 or step >= dump_from:
            return action
        shed, invs, farm = project(obs, action)
        prices = _g(_g(obs, "market"), "prices")
        market = [list(o) for o in (action.get("market") or []) if isinstance(o, list) and o]
        room = 100 - sum(shed.values())
        keep = []
        for o in market:
            if o[0] == "SELL" and len(o) >= 3 and o[1] in items:
                px = float(prices.get(o[1], 0) if isinstance(prices, dict) else _g(prices, o[1], 0))
                n = int(o[2])
                if px < floor * base_price[o[1]] and room - n >= min_room:
                    room -= n
                    continue
            keep.append(o)
        out = dict(action)
        out["market"] = keep
        return out

    mirror_knobs = cfg.get("mirror_knobs") or {}
    mirror_sim = float(cfg.get("mirror_sim", 0.9))
    mirror_from = int(cfg.get("mirror_from", 144))
    base_ns = ns["_BASE_NS"]
    knob_default = {k: base_ns.get(k) for k in mirror_knobs}
    mirror_state = {}

    def tile_key(t):
        if not isinstance(t, dict):
            return t
        return (t.get("kind"), t.get("crop"), t.get("animal"))

    def set_mirror_knobs(obs):
        """Aggressive knobs only while the rival's farm looks like ours (a cha22-family mirror)."""
        step = int(_g(obs, "step", 0))
        player = int(_g(obs, "player", 0))
        st = mirror_state.setdefault(player, {"on": False, "last": -99})
        if step == 0:
            st.update(on=False, last=-99)
        if step >= mirror_from and step - st["last"] >= 24:
            st["last"] = step
            farms = _g(obs, "farms")
            mine, theirs = _g(farms[player], "tiles"), _g(farms[1 - player], "tiles")
            same = total = 0
            for y in range(len(mine)):
                for x in range(len(mine[y])):
                    a, b = tile_key(mine[y][x]), tile_key(theirs[y][x])
                    if a in (None, "LOCKED") and b in (None, "LOCKED"):
                        continue
                    total += 1
                    same += a == b
            st["on"] = total > 0 and same / total >= mirror_sim
        for k, v in mirror_knobs.items():
            base_ns[k] = v if st["on"] else knob_default[k]

    adapt = cfg.get("eager_adapt") or {}
    shop_items = {"BAKERY": ["EGG", "WHEAT"], "PIZZA_SHOP": ["MILK", "TOMATO", "WHEAT"],
                  "BRUNCH_SPOT": ["EGG", "WHEAT", "STRAWBERRY"], "YARN_STORE": ["WOOL"],
                  "ICE_CREAM_SHOP": ["STRAWBERRY", "MILK", "WHEAT"], "PET_CAFE": ["CARROT"],
                  "SMOOTHIE_SHOP": ["STRAWBERRY", "MILK"], "FARMERS_MARKET": ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY"]}
    adapt_state = {}

    def adapt_pre(obs):
        """Estimate the rival's sales of each premium good in the previous step (market inventory change + town
        consumption - our own sales) and set the eager band cap: race (hi_race) while the rival sold the good within
        the last `window` steps, otherwise be patient (hi_calm)."""
        step = int(_g(obs, "step", 0))
        player = int(_g(obs, "player", 0))
        st = adapt_state.setdefault(player, {"prev": None, "last": {}})
        if step == 0:
            st.update(prev=None, last={})
        market = _g(obs, "market")
        inv = _g(market, "inventory")
        items = tuple(adapt.get("items", ["MILK", "STRAWBERRY", "WOOL"]))
        pv = st["prev"]
        if pv is not None and pv["step"] == step - 1:
            for it in items:
                if pv["price"][it] <= 1:
                    continue
                rival = int(_g(inv, it, 0)) - pv["inv"][it] + pv["cons"][it] - pv["sold"][it]
                if rival >= int(adapt.get("min_units", 1)):
                    st["last"][it] = step - 1
        bands = dict(ns.get("_EAGER_BANDS") or {})
        for it in items:
            active = step - st["last"].get(it, -999) <= int(adapt.get("window", 6))
            hi = float(adapt.get("hi_race", 1.4)) if active else float(adapt.get("hi_calm", 0.9))
            bands[it] = (float(adapt.get("lo", 0.2)), hi)
        ns["_EAGER_BANDS"] = bands
        st["obs_inv"] = {it: int(_g(inv, it, 0)) for it in items}
        st["obs_price"] = {it: float(_g(_g(market, "prices"), it, 0)) for it in items}

    def adapt_post(obs, action):
        step = int(_g(obs, "step", 0))
        player = int(_g(obs, "player", 0))
        st = adapt_state.get(player)
        if st is None:
            return
        items = tuple(adapt.get("items", ["MILK", "STRAWBERRY", "WOOL"]))
        pre = project(obs, dict(action, market=[]))[0]
        orders = [o for o in (action.get("market") or []) if isinstance(o, (list, tuple)) and o][:10]
        sold = {it: 0 for it in items}
        for o in orders:
            if o[0] == "SELL" and len(o) >= 3 and o[1] in sold:
                sold[o[1]] += int(o[2])
        sold = {it: min(sold[it], int(pre.get(it, 0))) for it in items}
        shops = list(_g(_g(obs, "town", {}), "unlocked_shops", []) or [])
        cons = {}
        for it in items:
            c = 0
            if step % 4 == 0:
                for sh in shops:
                    if it in shop_items.get(sh, ()):
                        c += 2 if len(shop_items[sh]) == 1 else 1
            if step % 24 == 0:
                c += 1
            cons[it] = c
        st["prev"] = {"step": step, "inv": st.get("obs_inv", {}), "price": st.get("obs_price", {}), "sold": sold,
                      "cons": cons}

    trend = cfg.get("eager_trend") or {}
    trend_state = {}

    def trend_pre(obs):
        """Eager band cap from the market trend of each premium good: inventory falling over the last `window` steps
        (demand ahead of supply, price rising) -> patient cap hi_calm; otherwise race with cap hi_race."""
        step = int(_g(obs, "step", 0))
        player = int(_g(obs, "player", 0))
        st = trend_state.setdefault(player, {})
        if step == 0:
            st.clear()
        inv = _g(_g(obs, "market"), "inventory")
        items = tuple(trend.get("items", ["MILK", "STRAWBERRY", "WOOL"]))
        w = int(trend.get("window", 24))
        bands = dict(ns.get("_EAGER_BANDS") or {})
        for it in items:
            hist = st.setdefault(it, [])
            hist.append((step, int(_g(inv, it, 0))))
            while hist and hist[0][0] < step - w:
                hist.pop(0)
            falling = len(hist) >= 2 and hist[-1][1] - hist[0][1] < -int(trend.get("margin", 0))
            hi = float(trend.get("hi_calm", 0.9)) if falling else float(trend.get("hi_race", 1.4))
            bands[it] = (float(trend.get("lo", 0.2)), hi)
        ns["_EAGER_BANDS"] = bands

    sub = (layers or {}).get("straw_sub") or {}
    sub_state = {}
    straw_shops = ("BRUNCH_SPOT", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP", "FARMERS_MARKET")

    def tape_plants(route, t, crop):
        tape = chassis.routes.get(route) or []
        if not (0 <= t < len(tape)) or not isinstance(tape[t], dict):
            return 0
        a = tape[t]
        return sum(1 for u in [a.get("farmer")] + list(a.get("hands") or [])
                   if isinstance(u, list) and len(u) >= 2 and u[0] == "PLANT" and u[1] == crop)

    def straw_sub(obs, action, p):
        """Crop substitution (Sadettin-style): on days first..last, when the tape plants WHEAT, plant STRAWBERRY instead
        (seeds bought one step ahead from the tape's next-step plantings), up to a quota set on day `first` from the
        number of strawberry shops. Tape units that later try to PLANT on a substituted tile harvest or water it."""
        step = int(_g(obs, "step", 0))
        player = int(_g(obs, "player", 0))
        st = sub_state.setdefault(player, {})
        if step == 0 or not st:
            st.clear()
            st.update(quota=None, tiles={}, used=0)
        day, hour = step // 24, step % 24
        first, last = int(p.get("first", 10)), int(p.get("last", 13))
        farm = _g(obs, "farms")[player]
        tiles = _g(farm, "tiles")
        priv = _g(obs, "private", {}) or {}
        seeds = dict(_g(priv, "seeds", {}) or {})
        shed = dict(_g(priv, "shed", {}) or {})
        cst = chassis.players.get(player) or {}
        route = cst.get("route")
        if st["quota"] is None and day >= first:
            shops = list(_g(_g(obs, "town", {}), "unlocked_shops", []) or [])
            n = sum(1 for s in shops if s in straw_shops)
            st["quota"] = int(p.get("quota", 12)) if n >= int(p.get("min_shops", 2)) else 0
        if not st["quota"] and not st["tiles"]:
            return action
        out = dict(action)
        units = [out.get("farmer") or ["PASS"]] + list(out.get("hands") or [])
        pos = [tuple(_g(farm, "farmer"))] + [tuple(h) for h in (_g(farm, "hands", []) or [])]
        changed = False
        # 1. convert this step's tape wheat plantings while we hold spare strawberry seeds
        if first <= day <= last and st["quota"] and st["used"] < st["quota"]:
            straw_req = sum(1 for u in units if isinstance(u, list) and len(u) >= 2 and u[0] == "PLANT"
                            and u[1] == "STRAWBERRY")
            spare = int(seeds.get("STRAWBERRY", 0)) - straw_req
            for i, u in enumerate(units):
                if spare <= 0 or st["used"] >= st["quota"]:
                    break
                if isinstance(u, list) and len(u) >= 2 and u[0] == "PLANT" and u[1] == "WHEAT" and i < len(pos):
                    x, y = pos[i]
                    if tiles[y][x] is None:
                        units[i] = ["PLANT", "STRAWBERRY"]
                        st["tiles"][(x, y)] = day
                        st["used"] += 1
                        spare -= 1
                        changed = True
        # 2. tape units that come back to a substituted tile to replant it: harvest or water instead
        for i, u in enumerate(units):
            if i >= len(pos) or not (isinstance(u, list) and u and u[0] in ("PLANT", "HARVEST")):
                continue
            if pos[i] not in st["tiles"]:
                continue
            x, y = pos[i]
            t = tiles[y][x]
            if not (isinstance(t, dict) and t.get("crop") == "STRAWBERRY"):
                continue
            if int(t.get("yield_units", 0) or 0) > 0:
                units[i] = ["HARVEST"]
            elif not t.get("watered_today"):
                units[i] = ["WATER"]
            elif u[0] == "PLANT":
                units[i] = ["PASS"]
            changed = changed or units[i] != u
        if changed:
            out["farmer"] = units[0]
            out["hands"] = units[1:]
        market = [list(o) for o in (out.get("market") or []) if isinstance(o, (list, tuple)) and o]
        mchanged = False
        # 3. seeds for next step's conversions
        if first <= day <= last and st["quota"] and st["used"] < st["quota"] and route is not None and hour < 23:
            nxt = tape_plants(route, step + 1, "WHEAT")
            need_next_tape = tape_plants(route, step + 1, "STRAWBERRY")
            have = int(seeds.get("STRAWBERRY", 0)) - sum(1 for u in units if isinstance(u, list) and len(u) >= 2
                                                          and u[0] == "PLANT" and u[1] == "STRAWBERRY")
            bought = sum(int(o[2]) for o in market if o[0] == "BUY_SEED" and len(o) >= 3 and o[1] == "STRAWBERRY")
            want = min(nxt, st["quota"] - st["used"]) + need_next_tape - max(0, have) - bought
            money = float(_g(farm, "money", 0))
            if want > 0 and len(market) < 10 and money > 100 * want + 1500:
                market.append(["BUY_SEED", "STRAWBERRY", want])
                mchanged = True
        # 4. feed guard: keep the wheat the tape picks up in the next hours
        if st["tiles"] and route is not None and len(market) < 10:
            need = planned_pickups(route, step, "WHEAT", int(p.get("feed_h", 24))) + int(p.get("feed_margin", 4))
            have_w = int(shed.get("WHEAT", 0)) + sum(int(o[2]) for o in market if o[0] == "BUY_PRODUCT" and len(o) >= 3
                                                    and o[1] == "WHEAT")
            sell_w = sum(int(o[2]) for o in market if o[0] == "SELL" and len(o) >= 3 and o[1] == "WHEAT")
            short = need - (have_w - sell_w)
            if short > 0 and float(_g(farm, "money", 0)) > 40 * short + 1000:
                market.append(["BUY_PRODUCT", "WHEAT", short])
                mchanged = True
        if mchanged:
            out["market"] = market[:10]
        return out

    wsub_state = {}

    def tape_unit_action(route, t, i):
        tape = chassis.routes.get(route) or []
        if not (0 <= t < len(tape)) or not isinstance(tape[t], dict):
            return None
        a = tape[t]
        acts = [a.get("farmer")] + list(a.get("hands") or [])
        return acts[i] if i < len(acts) else None

    def wheat_sub(obs, action, p):
        """Reverse substitution (experiment B): in worlds with little strawberry demand, the tape's day-`day` STRAWBERRY
        plantings become WHEAT (the tape's strawberry seed purchase that day is cancelled). Later tape visits to those
        tiles harvest ripe wheat, water unwatered wheat, and replant an empty tile when the unit stays for its next tape
        step (so the new plant can be watered on its planting day)."""
        step = int(_g(obs, "step", 0))
        player = int(_g(obs, "player", 0))
        st = wsub_state.setdefault(player, {})
        if step == 0 or not st:
            st.clear()
            st.update(on=None, tiles={}, water_next=set())
        day = step // 24
        pday = int(p.get("day", 11))
        farm = _g(obs, "farms")[player]
        tiles = _g(farm, "tiles")
        priv = _g(obs, "private", {}) or {}
        seeds = dict(_g(priv, "seeds", {}) or {})
        route = (chassis.players.get(player) or {}).get("route")
        if st["on"] is None and day >= pday - 1:
            shops = list(_g(_g(obs, "town", {}), "unlocked_shops", []) or [])
            n = sum(1 for s in shops if s in straw_shops)
            st["on"] = n <= int(p.get("max_straw_shops", 1))
        if not st["on"]:
            return action
        out = dict(action)
        units = [out.get("farmer") or ["PASS"]] + list(out.get("hands") or [])
        pos = [tuple(_g(farm, "farmer"))] + [tuple(h) for h in (_g(farm, "hands", []) or [])]
        wheat_plants = sum(1 for u in units if isinstance(u, list) and len(u) >= 2 and u[0] == "PLANT" and u[1] == "WHEAT")
        spare = int(seeds.get("WHEAT", 0)) - wheat_plants
        changed = False
        for i, u in enumerate(units):
            if i >= len(pos) or not (isinstance(u, list) and u):
                continue
            xy = pos[i]
            x, y = xy
            t = tiles[y][x]
            if day == pday and u[0] == "PLANT" and len(u) >= 2 and u[1] == "STRAWBERRY":
                if spare > 0:
                    units[i] = ["PLANT", "WHEAT"]
                    st["tiles"][xy] = day
                    spare -= 1
                else:
                    units[i] = ["PASS"]
                changed = True
                continue
            if xy not in st["tiles"] or u[0] in ("NORTH", "SOUTH", "EAST", "WEST"):
                continue
            new = u
            if xy in st["water_next"] and isinstance(t, dict) and t.get("crop") == "WHEAT" and not t.get("watered_today"):
                new = ["WATER"]
                st["water_next"].discard(xy)
            elif isinstance(t, dict) and t.get("crop") == "WHEAT":
                age = day - int(t.get("planted_day", day))
                if age >= int(p.get("harvest_age", 3)) and int(t.get("yield_units", 0) or 0) > 0:
                    new = ["HARVEST"]
                elif not t.get("watered_today"):
                    new = ["WATER"]
                elif u[0] == "FERTILIZE" and age <= 2:
                    new = u
                else:
                    new = ["PASS"] if u[0] in ("PLANT", "HARVEST", "DIG") else u
            elif t is None and day <= int(p.get("last_plant_day", 26)):
                nxt = tape_unit_action(route, step + 1, i) if route is not None else None
                stays = isinstance(nxt, list) and nxt and nxt[0] not in ("NORTH", "SOUTH", "EAST", "WEST")
                if stays and spare > 0:
                    new = ["PLANT", "WHEAT"]
                    spare -= 1
                    st["water_next"].add(xy)
            elif isinstance(t, dict) and t.get("kind") == "WEED":
                new = ["DIG"]
            if new != u:
                units[i] = new
                changed = True
        if changed:
            out["farmer"] = units[0]
            out["hands"] = units[1:]
        market = [list(o) for o in (out.get("market") or []) if isinstance(o, (list, tuple)) and o]
        mchanged = False
        if day == pday:
            for o in market:
                if o[0] == "BUY_SEED" and len(o) >= 3 and o[1] == "STRAWBERRY":
                    o[2] = 0
                    mchanged = True
            market = [o for o in market if not (o[0] == "BUY_SEED" and len(o) >= 3 and int(o[2]) <= 0)]
        # keep a few wheat seeds in stock for conversions and replanting (seeds bought now are usable next step)
        if pday - 1 <= day <= int(p.get("last_plant_day", 26)) and len(market) < 10:
            want = int(p.get("seed_stock", 14 if day <= pday else 4)) - max(0, spare)
            if day == pday - 1 and step % 24 < 20:
                want = 0
            if want > 0 and float(_g(farm, "money", 0)) > 10 * want + 500:
                market.append(["BUY_SEED", "WHEAT", want])
                mchanged = True
        if mchanged:
            out["market"] = market[:10]
        return out

    def agent(observation, configuration=None):
        if trend:
            try:
                trend_pre(observation)
            except Exception:
                pass
        if adapt:
            try:
                adapt_pre(observation)
            except Exception:
                pass
        if mirror_knobs:
            try:
                set_mirror_knobs(observation)
            except Exception:
                pass
        action = base_agent(observation, configuration)
        for name, p in layers.items():
            if not p:
                continue
            try:
                if name == "fert_lead":
                    action = lead_sell(observation, action, "FERTILIZER", p.get("lead", 3), p.get("hours", [19, 20, 21]),
                                       p.get("front", False))
                elif name == "wheat_lead":
                    action = lead_sell(observation, action, "WHEAT", p.get("lead", 2), p.get("hours", []),
                                       p.get("front", False), p.get("reserve_h", 0), p.get("book", False))
                elif name == "bulk_lead":
                    for item in p.get("items", ["EGG", "TOMATO", "CARROT"]):
                        action = lead_sell(observation, action, item, p.get("lead", 2), p.get("hours", []),
                                           p.get("front", False))
                elif name == "premium_lead":
                    for item in p.get("items", ["MILK", "WOOL", "STRAWBERRY"]):
                        action = lead_sell(observation, action, item, p.get("lead", 2), p.get("hours", []), True)
                elif name == "wheat_mm":
                    action = wheat_mm(observation, action, p.get("q", 30), p.get("keep", 25))
                elif name == "final_dump":
                    step = int(_g(observation, "step", 0))
                    if p.get("from_step", 696) <= step <= 711:
                        shed, invs, farm = project(observation, action)
                        market = [list(o) for o in (action.get("market") or []) if isinstance(o, list) and o]
                        for item in p.get("items", ["MILK", "WOOL", "STRAWBERRY", "EGG", "TOMATO"]):
                            selling = sum(int(o[2]) for o in market if o[0] == "SELL" and len(o) >= 3 and o[1] == item)
                            k = int(shed.get(item, 0)) - selling
                            if k <= 0:
                                continue
                            for i, o in enumerate(market):
                                if o[0] == "SELL" and o[1] == item:
                                    o[2] = int(o[2]) + k
                                    market.insert(0, market.pop(i))
                                    break
                            else:
                                if len(market) < 10:
                                    market.insert(0, ["SELL", item, k])
                        action = dict(action)
                        action["market"] = market[:10]
                elif name == "hold_premium":
                    action = hold_premium(observation, action, tuple(p.get("items", ["MILK", "WOOL", "STRAWBERRY"])),
                                          p.get("floor", 0.8), p.get("dump_from", 696), p.get("min_room", 20))
                elif name == "wheat_sub":
                    action = wheat_sub(observation, action, p)
                elif name == "straw_sub":
                    action = straw_sub(observation, action, p)
                elif name == "opp_race":
                    action = opp_race(observation, action, tuple(p.get("items", ["MILK", "WOOL", "STRAWBERRY"])),
                                      p.get("min_units", 2), p.get("share", 1.0))
            except Exception:
                pass
        if adapt:
            try:
                adapt_post(observation, action)
            except Exception:
                pass
        return action

    return agent


TEMPLATE = '''r"""Composite arena agent {name}: {desc}"""
_CFG = {cfg!r}
_LAYERS = r"{layers}"
_M = {{"__name__": "composite_layers"}}
exec(compile(open(_LAYERS, encoding="utf-8").read(), _LAYERS, "exec"), _M)
_A = _M["build"](_CFG)


def agent(observation, configuration=None):
    return _A(observation, configuration)
'''


def write(path, name, desc, cfg):
    open(path, "w", encoding="utf-8").write(TEMPLATE.format(name=name, desc=desc, cfg=cfg, layers=os.path.abspath(__file__)))
