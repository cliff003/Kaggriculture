"""Team 42 adaptive engine for Kaggriculture.

Layers:
  parse      observation -> S (plain dicts/lists)
  plan       daily targets: land, tile layout (what each tile should hold), hires
  jobs       per-tile work needed now (water / harvest / feed / care / collect / plant / build / place / dig)
  assign     greedy unit routing with persistent targets and shed pickups
  market     sales (shed stock after this turn's unit actions) first, then purchases
"""
import math

N = 10
SHED_TILES = ((4, 4), (5, 4), (4, 5), (5, 5))
SHED_SET = frozenset(SHED_TILES)
LAND_ORDER = ("NE", "SW", "SE")
LAND_PRICE = (1000, 2000, 4000)
MOVES = {(1, 0): "EAST", (-1, 0): "WEST", (0, 1): "SOUTH", (0, -1): "NORTH"}

CROPS = {
    "WHEAT": dict(seed=10, first=2, maxday=4, interval=0, maxy=6, ongoing=False, base=25),
    "CARROT": dict(seed=20, first=2, maxday=3, interval=0, maxy=4, ongoing=False, base=35),
    "TOMATO": dict(seed=50, first=8, maxday=8, interval=1, maxy=4, ongoing=True, base=60),
    "STRAWBERRY": dict(seed=100, first=10, maxday=10, interval=2, maxy=4, ongoing=True, base=120),
    "MELON": dict(seed=80, first=10, maxday=12, interval=0, maxy=6, ongoing=False, base=250),
}
ANIMALS = {
    "GOOSE": dict(cost=300, struct="COOP", first=4, interval=1, held=4, product="EGG"),
    "COW": dict(cost=400, struct="PASTURE", first=8, interval=2, held=6, product="MILK"),
    "SHEEP": dict(cost=500, struct="PASTURE", first=6, interval=3, held=6, product="WOOL"),
}
PRODUCTS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER")
SELL_GOODS = frozenset(("CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL"))
BASE_PRICE = {"WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120, "MELON": 250, "EGG": 50,
              "MILK": 160, "WOOL": 200, "FERTILIZER": 100}
MARKET_PARAMS = {
    "WHEAT": (25, 400, "sqrt", 0.80, "log", 0.20),
    "CARROT": (35, 450, "hinge", 1.00, "sqrt", 0.70),
    "TOMATO": (60, 200, "hinge", 0.40, "sqrt", 0.60),
    "STRAWBERRY": (120, 100, "sqrt", 0.70, "linear", 1.60),
    "MELON": (250, 300, "log", 0.20, "sq", 3.60),
    "EGG": (50, 332, "hinge", 0.40, "log", 0.20),
    "MILK": (160, 122, "sqrt", 0.60, "linear", 1.60),
    "WOOL": (200, 105, "log", 0.20, "sq", 3.20),
    "FERTILIZER": (100, 200, "linear", 0.40, "linear", 0.40),
}
I0 = 10000
SHOPS = {
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}


def _shape(f, x, T):
    x = max(0.0, x)
    if f == "linear":
        return x
    if f == "sq":
        return x * x
    if f == "sqrt":
        return math.sqrt(x)
    if f == "log":
        return math.log(1.0 + x)
    if f == "hinge":
        u = x / T
        return u + 8.0 * max(0.0, u - 1.0) ** 2
    return x


def price_at(item, inv):
    base, T, bf, bt, af, at = MARKET_PARAMS[item]
    if inv < I0:
        p = base + bt * base / _shape(bf, T, T) * _shape(bf, I0 - inv, T)
    else:
        p = base - at * base / _shape(af, T, T) * _shape(af, inv - I0, T)
    return max(1, int(round(p)))


def _g(o, k, d=None):
    try:
        v = o[k]
    except Exception:
        v = getattr(o, k, d)
    return d if v is None else v


def quad_of(x, y):
    return ("N" if y < 5 else "S") + ("W" if x < 5 else "E")


def dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def step_toward(p, t):
    if p[0] != t[0]:
        return MOVES[(1 if t[0] > p[0] else -1, 0)]
    if p[1] != t[1]:
        return MOVES[(0, 1 if t[1] > p[1] else -1)]
    return "PASS"


# --------------------------------------------------------------------------------------------- parse

class S:
    pass


def parse(obs):
    s = S()
    s.me = int(_g(obs, "player", 0))
    s.step = int(_g(obs, "step", 0))
    s.day, s.hour = s.step // 24, s.step % 24
    farms = _g(obs, "farms")
    f = farms[s.me]
    s.money = float(_g(f, "money", 0))
    s.tiles = [[_tile(t) for t in row] for row in _g(f, "tiles")]
    s.units = [tuple(_g(f, "farmer"))] + [tuple(h) for h in _g(f, "hands", [])]
    s.quads = list(_g(f, "unlocked_quadrants", ["NW"]))
    s.hires_today = int(_g(f, "hires_today", 0))
    o = farms[1 - s.me]
    s.opp_tiles = [[_tile(t) for t in row] for row in _g(o, "tiles")]
    s.opp_money = float(_g(o, "money", 0))
    priv = _g(obs, "private", {})
    s.shed = {k: int(v) for k, v in dict(_g(priv, "shed", {})).items() if int(v) > 0}
    s.seeds = {k: int(v) for k, v in dict(_g(priv, "seeds", {})).items() if int(v) > 0}
    s.invs = [{k: int(v) for k, v in dict(i).items() if int(v) > 0} for i in _g(priv, "inventories", [{}])]
    while len(s.invs) < len(s.units):
        s.invs.append({})
    m = _g(obs, "market", {})
    s.prices = {k: int(v) for k, v in dict(_g(m, "prices", {})).items()}
    s.minv = {k: int(v) for k, v in dict(_g(m, "inventory", {})).items()}
    s.shops = list(_g(_g(obs, "town", {}), "unlocked_shops", []))
    return s


def _tile(t):
    if t is None or t == "LOCKED":
        return t
    try:
        return dict(t)
    except Exception:
        return {k: getattr(t, k) for k in dir(t) if not k.startswith("_")}


# ---------------------------------------------------------------------------------------------- jobs
# A job is the list of ops one unit should run on one tile right now, plus a priority class:
#   0 critical (plant or animal dies tonight otherwise), 1 normal, 2 optional.

def crop_age(t, day):
    return day - int(t.get("planted_day", day))


def window_start(crop):
    return (CROPS[crop]["maxday"] + 1) // 2


def production_tonight(t, day):
    """Ongoing crop: a scheduled production fires at the end of today."""
    c = CROPS[t["crop"]]
    if not c["ongoing"]:
        return False
    since = day + 1 - int(t["planted_day"]) - c["first"]
    return since >= 0 and since % c["interval"] == 0 and since // c["interval"] + 1 <= c["maxy"]


def plant_ops(t, s, fert_ok):
    crop = t["crop"]
    c = CROPS[crop]
    age = crop_age(t, s.day)
    y = int(t.get("yield_units", 0))
    ops, pri = [], 2
    watered = bool(t.get("watered_today"))
    unw = int(t.get("consecutive_unwatered", 0))
    fert_until = int(t.get("fertilized_until_day", -1))
    # harvest decision
    ready = False
    if y > 0 and age >= c["first"]:
        if c["ongoing"]:
            ready = True
        elif y >= c["maxy"] or age > c["maxday"] or (age == c["maxday"] and watered):
            ready = True
        elif int(t.get("max_lifespan_step", -1)) >= 0 and s.step >= int(t["max_lifespan_step"]) - 1:
            ready = True
    # watering decision (skip on a plant that will be harvested and removed now)
    # every plant is watered every day: skipping days saves little labour and a slipped schedule kills
    # plants and loses fertilizer bonuses (cha22 never has weeds this way)
    want = False
    if not watered:
        if unw >= 1:
            want, pri = True, 0
        elif not (ready and not c["ongoing"]):
            want, pri = True, 1
    if ready and not c["ongoing"] and not (want and pri == 1 and y < c["maxy"]):
        return ["HARVEST"], 1
    # fertilize: ongoing crops before their production nights; one-time crops at the window start
    if fert_ok and fert_until < s.day:
        if c["ongoing"] and production_tonight(t, s.day):
            ops.append("FERTILIZE")
        elif crop == "WHEAT" and age == window_start(crop) and y < c["maxy"] - 1:
            ops.append("FERTILIZE")
    if want:
        ops.append("WATER")
    if ready:
        ops.append("HARVEST")
        pri = min(pri, 1)
    if ops and pri == 2:
        pri = 1 if "WATER" in ops or "HARVEST" in ops else 2
    return ops, pri


def animal_ops(t, s, plan):
    ops, pri = [], 1
    if not t.get("fed_today") and plan.get("feed", True):
        ops.append("FEED")
        if int(t.get("consecutive_unfed", 0)) >= 1:
            pri = 0
    if not t.get("cared_today") and plan.get("care", True):
        ops.append("CARE")
    if t.get("fertilizer_available"):
        ops.append("COLLECT_FERTILIZER")
    if int(t.get("yield_units", 0)) > 0:
        ops.append("HARVEST")
    return ops, pri


def build_jobs(s, plan):
    jobs = {}
    targets = plan["targets"]
    fert_ok = plan.get("fertilize", True)
    for y in range(N):
        for x in range(N):
            t = s.tiles[y][x]
            if t == "LOCKED":
                continue
            tgt = targets.get((x, y))
            ops, pri = [], 2
            if t is None:
                if tgt in CROPS:
                    ops, pri = ["PLANT:" + tgt], 1
                elif tgt in ANIMALS:
                    ops, pri = ["BUILD:" + ANIMALS[tgt]["struct"]], 1
            elif t.get("kind") == "WEED":
                if tgt:
                    ops, pri = ["DIG"], 1
            elif t.get("kind") == "PLANT":
                ops, pri = plant_ops(t, s, fert_ok)
            elif t.get("animal"):
                ops, pri = animal_ops(t, s, plan)
            elif t.get("kind") in ("COOP", "PASTURE"):
                if tgt in ANIMALS and ANIMALS[tgt]["struct"] == t["kind"]:
                    ops, pri = ["PLACE:" + tgt], 1
                elif tgt is not None:
                    ops, pri = ["DIG"], 2
            if ops:
                jobs[(x, y)] = (ops, pri)
    return jobs


# -------------------------------------------------------------------------------------------- assign

def needs(op):
    """Inventory item an op consumes."""
    if op == "FEED":
        return "WHEAT"
    if op == "FERTILIZE":
        return "FERTILIZER"
    if op.startswith("PLACE:"):
        return op.split(":", 1)[1]
    return None


def assign(s, mem, plan, jobs):
    """One action per unit. Units keep a target tile until its ops are done; resource trips to the shed."""
    n = len(s.units)
    targets = mem.setdefault("unit_target", {})
    for k in list(targets):
        if k >= n:
            del targets[k]
    shed = dict(s.shed)
    seeds = dict(s.seeds)
    invs = [dict(i) for i in s.invs]
    claimed = set(v for v in targets.values() if v is not None)
    actions = [["PASS"]] * n
    remaining = 24 - s.hour
    zones = unit_zones(s, mem, jobs, n)
    feeders = sum(1 for (ops, _) in jobs.values() if "FEED" in ops)
    ferts = sum(1 for (ops, _) in jobs.values() if "FERTILIZE" in ops)
    seen = mem.setdefault("seen_day", {})
    for u in range(n):
        pos = s.units[u]
        inv = invs[u]
        tgt = targets.get(u)
        if tgt is not None and tgt not in jobs:
            claimed.discard(tgt)
            tgt = None
        # 1) a unit's first turns of the day start at the shed: the first few units take all of today's
        #    wheat (about 8 feeds each) and fertilizer (about 8 each); the rest leave empty-handed
        if pos in SHED_SET and seen.get(u) != s.day:
            item, k = zone_pickup(s, inv, shed, u, zones, jobs, plan)
            if item:
                shed[item] -= k
                inv[item] = inv.get(item, 0) + k
                actions[u] = ["PICKUP", item, k]
                continue
            seen[u] = s.day
        # 2) deliver goods during the day so they can be sold before the day-end drop overflows the shed:
        #    a unit carrying a big load (or anything late in the day) walks to the shed and unloads
        load = sum(v for k, v in inv.items() if k in SELL_GOODS or k == "WHEAT" or k == "FERTILIZER")
        keep = {"WHEAT": min(inv.get("WHEAT", 0), feeders_left(jobs, u, n)),
                "FERTILIZER": min(inv.get("FERTILIZER", 0), 2 if ferts else 0)}
        spare = load - keep["WHEAT"] - keep["FERTILIZER"]
        deliver = spare >= 12 or (s.hour >= 19 and spare >= 4)
        if deliver and s.hour < 23:
            if pos in SHED_SET:
                kinds = [k for k, v in inv.items() if v - keep.get(k, 0) > 0 and k in PRODUCTS]
                if len(kinds) == 1:
                    item = kinds[0]
                    k = inv[item] - keep.get(item, 0)
                    actions[u] = ["PLACE", item, k]
                    inv[item] -= k
                    shed[item] = shed.get(item, 0) + k
                else:
                    actions[u] = ["DROP"]
                    for k, v in list(inv.items()):
                        shed[k] = shed.get(k, 0) + v
                        inv[k] = 0
                continue
            if tgt is None or jobs.get(tgt, ([], 1))[1] > 0:
                actions[u] = [step_toward(pos, nearest_shed(pos))]
                continue
        if tgt is None:
            tgt = choose(s, u, pos, inv, jobs, claimed, remaining, shed, seeds, zones.get(u))
            targets[u] = tgt
            if tgt is not None:
                claimed.add(tgt)
        if tgt is None:
            actions[u] = ["PASS"]
            continue
        ops, pri = jobs[tgt]
        # resource missing for the next op -> fetch exactly that from the shed
        op = first_runnable(ops, inv, seeds)
        if op is None:
            need = next((needs(o) for o in ops if needs(o)), None)
            if need and shed.get(need, 0) > 0:
                if pos in SHED_SET:
                    if need in ANIMALS:
                        k = 1
                    elif need == "WHEAT":
                        k = min(shed[need], max(2, int(math.ceil(feeders / max(1, n))) + 1))
                    else:
                        k = min(shed[need], max(1, int(math.ceil(ferts / max(1, n)))))
                    shed[need] -= k
                    inv[need] = inv.get(need, 0) + k
                    actions[u] = ["PICKUP", need, k]
                else:
                    actions[u] = [step_toward(pos, nearest_shed(pos))]
                continue
            claimed.discard(tgt)
            targets[u] = None
            actions[u] = ["PASS"]
            continue
        if pos != tgt:
            actions[u] = [step_toward(pos, tgt)]
            continue
        act = op_action(op)
        if op.startswith("PLANT:"):
            crop = op.split(":", 1)[1]
            seeds[crop] = seeds.get(crop, 0) - 1
        r = needs(op)
        if r:
            inv[r] = inv.get(r, 0) - 1
        actions[u] = act
        # the tile's remaining ops are recomputed next turn; free the target when this was the last one
        if len(ops) == 1 and not op.startswith(("PLANT:", "BUILD:", "PLACE:", "DIG")):
            claimed.discard(tgt)
            targets[u] = None
    return actions


def first_runnable(ops, inv, seeds):
    for i, op in enumerate(ops):
        r = needs(op)
        if r and inv.get(r, 0) <= 0:
            if op == "FERTILIZE":
                continue  # optional: skip when not carried
            if op == "FEED" and len(ops) > i + 1:
                continue  # care / collect / harvest first; a wheat carrier feeds later
            return None
        if op.startswith("PLANT:") and seeds.get(op.split(":", 1)[1], 0) <= 0:
            continue
        return op
    return None


def op_action(op):
    if op.startswith("PLANT:"):
        return ["PLANT", op.split(":", 1)[1]]
    if op.startswith("BUILD:"):
        return ["BUILD_" + op.split(":", 1)[1]]
    if op.startswith("PLACE:"):
        return ["PLACE", op.split(":", 1)[1]]
    return [op]


def nearest_shed(pos):
    return min(SHED_TILES, key=lambda t: dist(pos, t))


def feeders_left(jobs, u, n):
    """Feeds a unit may still need to do today: an even share of the open FEED jobs, plus one."""
    open_feeds = sum(1 for (ops, _) in jobs.values() if "FEED" in ops)
    return int(math.ceil(open_feeds / max(1, n))) + 1 if open_feeds else 0


def zone_pickup(s, inv, shed, u, zones, jobs, plan):
    """Start-of-day stock for unit u: an even share (plus one) of the feeds and fertilizings in its zone."""
    q = zones.get(u)
    mates = sum(1 for v in zones.values() if v == q) or 1
    feeds = sum(1 for (x, y), (ops, _) in jobs.items() if "FEED" in ops and quad_of(x, y) == q)
    ferts = sum(1 for (x, y), (ops, _) in jobs.items() if "FERTILIZE" in ops and quad_of(x, y) == q)
    if feeds and plan.get("feed", True) and shed.get("WHEAT", 0) > 0:
        share = int(math.ceil(feeds / mates)) + 1
        if inv.get("WHEAT", 0) < share:
            return "WHEAT", min(shed["WHEAT"], share - inv.get("WHEAT", 0))
    if ferts and plan.get("fertilize", True) and shed.get("FERTILIZER", 0) > 0:
        share = int(math.ceil(ferts / mates))
        if inv.get("FERTILIZER", 0) < share:
            return "FERTILIZER", min(shed["FERTILIZER"], share - inv.get("FERTILIZER", 0))
    return None, 0


PER_CARRIER = 8
RULE_PLAN = True


def start_pickup(inv, shed, u, feeders, ferts, plan):
    """Start-of-day stock: unit u is a wheat carrier if u < ceil(feeders / 8) and a fertilizer carrier if
    u < ceil(ferts / 8); a carrier takes its 8-unit share (plus one wheat)."""
    if feeders and plan.get("feed", True) and shed.get("WHEAT", 0) > 0 and u < math.ceil(feeders / PER_CARRIER):
        share = min(PER_CARRIER, feeders - u * PER_CARRIER) + 1
        if inv.get("WHEAT", 0) < share:
            return "WHEAT", min(shed["WHEAT"], share - inv.get("WHEAT", 0))
    if ferts and plan.get("fertilize", True) and shed.get("FERTILIZER", 0) > 0 and u < math.ceil(ferts / PER_CARRIER):
        share = min(PER_CARRIER, ferts - u * PER_CARRIER)
        if inv.get("FERTILIZER", 0) < share:
            return "FERTILIZER", min(shed["FERTILIZER"], share - inv.get("FERTILIZER", 0))
    return None, 0


def pickup_need(s, u, n, inv, shed, jobs, tgt, plan, feeders, invs=None):
    """What to pick up while standing at the shed, or None."""
    # animals waiting in the shed for an empty structure
    for a in ANIMALS:
        if shed.get(a, 0) > 0 and inv.get(a, 0) == 0:
            free = sum(1 for (ops, _) in jobs.values() if ("PLACE:" + a) in ops)
            carried = sum(i.get(a, 0) for i in (invs or []))
            if free > carried:
                return a, min(shed[a], free - carried)
    # wheat for feeding: an even share of today's feeds, plus one
    if feeders and shed.get("WHEAT", 0) > 0:
        share = int(math.ceil(feeders / max(1, n))) + 1
        if inv.get("WHEAT", 0) < min(share, 2) and plan.get("feed", True):
            return "WHEAT", min(shed["WHEAT"], share - inv.get("WHEAT", 0))
    # fertilizer for fertilizing
    fert_jobs = sum(1 for (ops, _) in jobs.values() if "FERTILIZE" in ops)
    if fert_jobs and shed.get("FERTILIZER", 0) > 0 and inv.get("FERTILIZER", 0) == 0 and plan.get("fertilize", True):
        share = int(math.ceil(fert_jobs / max(1, n)))
        return "FERTILIZER", min(shed["FERTILIZER"], max(1, share))
    return None


def unit_zones(s, mem, jobs, n):
    """Quadrant per unit for today, proportional to each owned quadrant's open work (fixed at the day's
    first step with the full crew, recomputed if the crew grows)."""
    key = (s.day, n)
    if mem.get("zones_key") == key:
        return mem["zones"]
    work = {q: 0.0 for q in s.quads}
    for (x, y), (ops, _) in jobs.items():
        q = quad_of(x, y)
        if q in work:
            work[q] += len(ops) + 1
    for row_y, row in enumerate(s.tiles):
        for x, t in enumerate(row):
            q = quad_of(x, row_y)
            if q in work and isinstance(t, dict) and (t.get("animal") or t.get("kind") == "PLANT"):
                work[q] += 1.5
    total = sum(work.values()) or 1.0
    share = {q: work[q] / total * n for q in work}
    alloc = {q: int(share[q]) for q in work}
    for q in sorted(work, key=lambda q: -(share[q] - alloc[q]))[:n - sum(alloc.values())]:
        alloc[q] += 1
    # hand units to quadrants, nearest spawn tile first
    order = []
    for q in sorted(alloc, key=lambda q: -alloc[q]):
        order += [q] * alloc[q]
    corner = {"NW": (4, 4), "NE": (5, 4), "SW": (4, 5), "SE": (5, 5)}
    zones, free_units = {}, list(range(n))
    for q in order:
        u = min(free_units, key=lambda k: (dist(s.units[k], corner[q]), k))
        zones[u] = q
        free_units.remove(u)
    mem["zones_key"], mem["zones"] = key, zones
    return zones


def choose(s, u, pos, inv, jobs, claimed, remaining, shed, seeds, zone=None):
    best, best_cost = None, None
    for tile, (ops, pri) in jobs.items():
        if tile in claimed:
            continue
        runnable = first_runnable(ops, inv, seeds)
        detour = 0
        if runnable is None:
            need = next((needs(o) for o in ops if needs(o)), None)
            if not need or shed.get(need, 0) <= 0:
                continue
            sh = nearest_shed(pos)
            # a special trip for wheat or fertilizer is a last resort; animals to place are worth it
            detour = dist(pos, sh) + dist(sh, tile) - dist(pos, tile) + 1 + (0 if need in ANIMALS else 12)
        d = dist(pos, tile) + detour
        if d + len(ops) > remaining and pri > 0:
            continue
        cost = d + (0, 3, 9)[pri] - 0.5 * len(ops)
        if zone and quad_of(tile[0], tile[1]) != zone and pri > 0:
            cost += 8
        if best_cost is None or cost < best_cost:
            best, best_cost = tile, cost
    return best


# ---------------------------------------------------------------------------------------------- plan
# Temporary plan used to validate the executor; the DSM-derived plan replaces it.

def quad_tiles(q):
    x0 = 0 if q[1] == "W" else 5
    y0 = 0 if q[0] == "N" else 5
    return [(x, y) for y in range(y0, y0 + 5) for x in range(x0, x0 + 5)]


def shed_dist(xy):
    return min(dist(xy, t) for t in SHED_TILES)


# last day on which planting a crop still pays (harvest/production must land before day 29 ends)
LAST_PLANT_DAY = {"WHEAT": 25, "CARROT": 26, "TOMATO": 19, "STRAWBERRY": 15, "MELON": 1}


def desired_counts(s):
    """Target animals and crops by day (DSM averages; shop-dependent rules replace this)."""
    d = s.day
    shops = s.shops
    egg = sum(1 for x in shops if x in ("BAKERY", "BRUNCH_SPOT"))
    milk = sum(1 for x in shops if x in ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"))
    wool = sum(1 for x in shops if x == "YARN_STORE")
    tom = sum(1 for x in shops if x in ("PIZZA_SHOP", "FARMERS_MARKET"))
    car = sum(1 for x in shops if x in ("PET_CAFE", "FARMERS_MARKET"))
    animals = {"COW": 2, "SHEEP": 3, "GOOSE": 0}
    if d >= 6:
        animals = {"COW": 6, "SHEEP": 4, "GOOSE": 2}
    if d >= 9:
        animals = {"COW": 7 + min(4, milk), "SHEEP": 5 + min(4, 2 * wool), "GOOSE": 3 + min(6, 2 * egg)}
    if d >= 25:
        animals = {k: 0 for k in animals}  # no new animals late: they would not pay back
    crops = {}
    if d <= 1:
        crops["MELON"] = 10
    crops["STRAWBERRY"] = 10 if d < 6 else (18 if d < 9 else 26)
    crops["TOMATO"] = 0 if d < 9 else 6 + 3 * min(3, tom)
    crops["CARROT"] = 0 if d < 18 else 4 + 3 * min(3, car)
    return animals, crops


def make_plan_opening(s, mem):
    targets = {}
    owned = [xy for q in s.quads for xy in quad_tiles(q)]
    animals_want, crops_want = desired_counts(s)
    # current occupancy
    have_a = {a: 0 for a in ANIMALS}
    have_c = {c: 0 for c in CROPS}
    free = []
    for xy in owned:
        t = s.tiles[xy[1]][xy[0]]
        if isinstance(t, dict) and t.get("animal"):
            have_a[t["animal"]] += 1
            targets[xy] = t["animal"]
        elif isinstance(t, dict) and t.get("kind") in ("COOP", "PASTURE"):
            # empty structure: keep it for an animal of the matching kind
            kind = next((a for a in ("COW", "SHEEP", "GOOSE") if ANIMALS[a]["struct"] == t["kind"]
                         and have_a[a] < animals_want.get(a, 0)), None)
            if kind:
                have_a[kind] += 1
                targets[xy] = kind
            else:
                free.append(xy)
        elif isinstance(t, dict) and t.get("kind") == "PLANT":
            have_c[t["crop"]] += 1
            targets[xy] = t["crop"]
        else:
            free.append(xy)
    # new animal structures on the free tiles nearest the shed, only as many as the bank can stock now
    free.sort(key=lambda xy: (shed_dist(xy), xy[1], xy[0]))
    budget = s.money - animals_total(s) * (s.prices.get("WHEAT", 25) + 2)
    for a in ("COW", "SHEEP", "GOOSE"):
        waiting = s.shed.get(a, 0) + sum(i.get(a, 0) for i in s.invs)
        while have_a[a] < animals_want.get(a, 0) and free:
            if waiting > 0:
                waiting -= 1
            elif budget >= ANIMALS[a]["cost"] + 80:
                budget -= ANIMALS[a]["cost"] + 80
            else:
                break
            xy = free.pop(0)
            targets[xy] = a
            have_a[a] += 1
    # crops on the remaining free tiles, far side first for fast growers
    for c in ("MELON", "STRAWBERRY", "TOMATO", "CARROT"):
        if s.day > LAST_PLANT_DAY[c]:
            continue
        while have_c[c] < crops_want.get(c, 0) and free:
            xy = free.pop(0)
            targets[xy] = c
            have_c[c] += 1
    for xy in free:
        if s.day <= LAST_PLANT_DAY["WHEAT"]:
            targets[xy] = "WHEAT"
    land = []
    if s.day >= 6 and len(s.quads) == 1:
        land.append("NE")
    if s.day >= 9 and len(s.quads) == 2:
        land.append("SW")
    if s.day >= 10 and len(s.quads) == 3:
        land.append("SE")
    return {"targets": targets, "land": land, "hires": None, "feed": s.day < 29, "care": True, "fertilize": True,
            "fert_reserve": fert_demand(s)}


def shop_count(shops, names):
    return sum(1 for x in shops if x in names)


def rule_counts(s):
    """Target composition for the engine phase (day >= 10), from the town's shops."""
    d = s.day
    egg = shop_count(s.shops, ("BAKERY", "BRUNCH_SPOT"))
    milk = shop_count(s.shops, ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"))
    yarn = shop_count(s.shops, ("YARN_STORE",))
    tom = shop_count(s.shops, ("PIZZA_SHOP", "FARMERS_MARKET"))
    car = 2 * shop_count(s.shops, ("PET_CAFE",)) + shop_count(s.shops, ("FARMERS_MARKET",))
    straw = shop_count(s.shops, ("BRUNCH_SPOT", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP", "FARMERS_MARKET"))
    animals = {"COW": min(10, 8 + max(0, milk - 2)), "SHEEP": min(12, 6 + 3 * yarn),
               "GOOSE": min(9, 3 + 2 * egg)}
    if d > 20:
        animals = {k: 0 for k in animals}
    crops = {"STRAWBERRY": (33 if straw >= 1 else 24) if d <= 13 else 0,
             "TOMATO": min(20, 4 * tom) if d <= 18 else 0,
             "CARROT": min(15, 4 * car) if 19 <= d <= 25 else 0}
    return animals, crops


def rule_targets(s, free):
    """Free tiles -> use. Animals nearest the shed (as the bank allows), then strawberries, tomatoes,
    carrots, and wheat everywhere else while a wheat crop can still finish."""
    animals_want, crops_want = rule_counts(s)
    have_a = {a: 0 for a in ANIMALS}
    have_c = {c: 0 for c in CROPS}
    for row in s.tiles:
        for t in row:
            if isinstance(t, dict) and t.get("animal"):
                have_a[t["animal"]] += 1
            elif isinstance(t, dict) and t.get("kind") == "PLANT":
                have_c[t["crop"]] += 1
    for a in ANIMALS:
        have_a[a] += s.shed.get(a, 0) + sum(i.get(a, 0) for i in s.invs)
    out = {}
    free = list(free)
    budget = s.money - animals_total(s) * (s.prices.get("WHEAT", 25) + 2) - 500
    for a in ("GOOSE", "COW", "SHEEP"):
        while have_a[a] < animals_want.get(a, 0) and free and budget >= ANIMALS[a]["cost"] + 60:
            out[free.pop(0)] = a
            have_a[a] += 1
            budget -= ANIMALS[a]["cost"] + 60
    for c in ("STRAWBERRY", "TOMATO", "CARROT"):
        while have_c[c] < crops_want.get(c, 0) and free:
            out[free.pop(0)] = c
            have_c[c] += 1
    for xy in free:
        if s.day <= 24:
            out[xy] = "WHEAT"
        elif s.day <= 25:
            out[xy] = "CARROT"
    return out


def make_plan(s, mem):
    if s.day < 10:
        return make_plan_opening(s, mem)
    targets = {}
    owned = [xy for q in s.quads for xy in quad_tiles(q)]
    free = []
    for xy in owned:
        t = s.tiles[xy[1]][xy[0]]
        if isinstance(t, dict) and t.get("animal"):
            targets[xy] = t["animal"]
        elif isinstance(t, dict) and t.get("kind") == "PLANT":
            targets[xy] = t["crop"]
        else:
            free.append(xy)
    free.sort(key=lambda xy: (shed_dist(xy), xy[1], xy[0]))
    if mem.get("econ_day") != s.day:
        plan_tiles = rule_targets(s, free) if RULE_PLAN else economic_targets(s, free)
        # only as many new animals as the bank can stock now; the rest of those tiles get the best crop
        budget = s.money - animals_total(s) * (s.prices.get("WHEAT", 25) + 2) - 300
        waiting = {a: s.shed.get(a, 0) + sum(i.get(a, 0) for i in s.invs) for a in ANIMALS}
        refill = None if RULE_PLAN else economic_targets(s, [(-1, -1)], animals=False).get((-1, -1))
        for xy in free:
            use = plan_tiles.get(xy)
            if use in ANIMALS:
                if waiting[use] > 0:
                    waiting[use] -= 1
                elif budget >= ANIMALS[use]["cost"] + 60:
                    budget -= ANIMALS[use]["cost"] + 60
                else:
                    plan_tiles[xy] = refill
        mem["econ_day"], mem["econ_targets"], mem["refill"] = s.day, plan_tiles, refill
    plan_tiles, refill = mem["econ_targets"], mem["refill"]
    fallback = "WHEAT" if s.day <= 24 else ("CARROT" if s.day <= 25 else None)
    for xy in free:
        use = plan_tiles.get(xy, refill) or fallback
        if use is not None:
            targets[xy] = use
    land = []
    if len(s.quads) < 4 and s.day <= 20:
        land.append(LAND_ORDER[len(s.quads) - 1])
    return {"targets": targets, "land": land, "hires": None, "feed": s.day < 29, "care": True, "fertilize": True,
            "fert_reserve": fert_demand(s)}


def fert_demand(s):
    """Fertilizer wanted today and tomorrow: ongoing crops before production nights, one-time crops at the
    start of their watering window. Kept in the shed instead of being sold."""
    n = 0
    days = (s.day, s.day + 1) if s.hour <= 1 else (s.day + 1,)
    for row in s.tiles:
        for t in row:
            if not (isinstance(t, dict) and t.get("kind") == "PLANT"):
                continue
            c = CROPS[t["crop"]]
            fu = int(t.get("fertilized_until_day", -1))
            for d in days:
                if fu >= d:
                    continue
                age = d - int(t["planted_day"])
                if c["ongoing"]:
                    since = d + 1 - int(t["planted_day"]) - c["first"]
                    if since >= 0 and since % c["interval"] == 0 and since // c["interval"] + 1 <= c["maxy"]:
                        n += 1
                        break
                elif t["crop"] == "WHEAT" and age == window_start(t["crop"]):
                    n += 1
                    break
    return n


# ------------------------------------------------------------------------------------ demand-driven plan
# Each free tile goes to the use with the highest marginal value over the rest of the game, given
# town demand (current shops + expected future unlocks), the opponent's visible production and ours,
# and the market price curve. Recomputed once per day at hour 0.

# per tile: product, units per day in steady state, days until the first unit, labor turns per day,
# fertilizer used per day, purchase cost, wheat eaten per day
USES = {
    "COW": ("MILK", 1.5, 8, 5.0, 0.0, 400, 1.0),
    "SHEEP": ("WOOL", 4.0 / 3.0, 6, 5.0, 0.0, 500, 1.0),
    "GOOSE": ("EGG", 2.0, 4, 5.0, 0.0, 300, 1.0),
    "STRAWBERRY": ("STRAWBERRY", 0.5, 10, 1.5, 2.0 / 16, 100, 0.0),
    "TOMATO": ("TOMATO", 8.0 / 12.0, 8, 1.8, 2.0 / 12, 50, 0.0),
    "WHEAT": ("WHEAT", 1.5, 3, 2.0, 1.0 / 4, 10, 0.0),
    "CARROT": ("CARROT", 1.0, 2, 2.0, 0.0, 20, 0.0),
}
ANIMAL_FERT = 1.0  # every animal leaves one fertilizer per day
LABOR = 6.0        # marginal cost of a unit-turn (the 12th hand of a day costs 144 for ~22 turns)
FUTURE_SHOP_DAYS = (3, 6, 9, 12, 15, 18, 21, 24)


def demand_rates(shops):
    d = {p: (1.0 if p != "FERTILIZER" else 0.0) for p in PRODUCTS}
    for sh in shops:
        prods = SHOPS[sh]
        k = 12.0 if len(prods) == 1 else 6.0
        for p in prods:
            d[p] += k
    return d


def expected_future_demand(day, shops):
    """Average extra demand per day from shops still to unlock (uniform draw over 8 shop types)."""
    left = sum(1 for dd in FUTURE_SHOP_DAYS if dd > day)
    left = min(left, 8 - len(shops))
    extra = {p: 0.0 for p in PRODUCTS}
    for sh, prods in SHOPS.items():
        k = 12.0 if len(prods) == 1 else 6.0
        for p in prods:
            extra[p] += k / 8.0
    # a future shop is active on average for half of the remaining horizon
    return {p: v * left * 0.5 for p, v in extra.items()}


def farm_supply(tiles, day):
    sup = {p: 0.0 for p in PRODUCTS}
    for row in tiles:
        for t in row:
            if not isinstance(t, dict):
                continue
            if t.get("animal"):
                use = USES[t["animal"]]
                sup[use[0]] += use[1]
                sup["FERTILIZER"] += ANIMAL_FERT
                sup["WHEAT"] -= use[6]
            elif t.get("kind") == "PLANT" and t["crop"] in USES:
                use = USES[t["crop"]]
                sup[use[0]] += use[1]
    return sup


def avg_price(item, inv_now, net_per_day, days):
    """Mean sale price if the market drifts by net_per_day for `days` (three-point average)."""
    days = max(1.0, days)
    pts = [price_at(item, inv_now + net_per_day * days * f) for f in (0.15, 0.5, 0.85)]
    return sum(pts) / 3.0


def economic_targets(s, free_tiles, animals=True):
    """Assign free tiles by value per tile-day, one planting (or animal) at a time, with market saturation
    from both farms' production. Every tile that can still finish a crop gets one."""
    H = max(0, 28 - s.day)
    demand = demand_rates(s.shops)
    fut = expected_future_demand(s.day, s.shops)
    ours = farm_supply(s.tiles, s.day)
    opp = farm_supply(s.opp_tiles, s.day)
    fp = s.prices.get("FERTILIZER", 50)
    wp = s.prices.get("WHEAT", 30)
    out = {}
    for xy in free_tiles:
        best, best_v = None, None
        for use in USES:
            v = use_value(use, s, H, demand, fut, ours, opp, fp, wp, animals)
            if v is not None and (best_v is None or v > best_v):
                best, best_v = use, v
        if best is None:
            continue
        out[xy] = best
        prod, rate = USES[best][0], USES[best][1]
        ours[prod] += rate
        if best in ANIMALS:
            ours["FERTILIZER"] += ANIMAL_FERT
            ours["WHEAT"] -= USES[best][6]
    return out


# units per planting with fertilizer, days the tile is busy, turns of work per planting
PLANTING = {"WHEAT": (6, 4, 8), "CARROT": (4, 3, 6), "TOMATO": (8, 12, 16), "STRAWBERRY": (8, 16, 18)}


def planting_units(crop, day):
    """Units a planting made today can still deliver by the end of day 28."""
    if crop == "WHEAT":
        return 6 if day + 4 <= 28 else 0
    if crop == "CARROT":
        return 4 if day + 3 <= 28 else 0
    if crop == "TOMATO":
        return 2 * sum(1 for k in range(4) if day + 8 + k <= 28)
    if crop == "STRAWBERRY":
        return 2 * sum(1 for k in range(4) if day + 10 + 2 * k <= 28)
    return 0


def use_value(use, s, H, demand, fut, ours, opp, fp, wp, animals):
    """Value per tile-day of putting one more `use` on a free tile now (None when impossible)."""
    prod, rate = USES[use][0], USES[use][1]
    net = ours[prod] + opp[prod] - demand[prod] - fut[prod]
    horizon = max(1.0, H)
    price = avg_price(prod, s.minv.get(prod, I0), net + rate, horizon)
    # what the extra supply costs the rest of our own output of this product
    loss = ours[prod] * max(0.0, avg_price(prod, s.minv.get(prod, I0), net, horizon) - price)
    if use in ANIMALS:
        if not animals or s.day > 22:
            return None
        lag = USES[use][2]
        days = H - lag
        if days <= 0:
            return None
        gain = rate * days * price + (H - 1) * fp * 0.6 - H * wp - H * 5.0 * LABOR - ANIMALS[use]["cost"]
        return (gain - loss * days) / max(1.0, H)
    units = planting_units(use, s.day)
    if units <= 0:
        return None
    units_, busy, turns = PLANTING[use]
    gain = units * price - CROPS[use]["seed"] - (units_ / 3.0) * fp - turns * LABOR
    return (gain - loss * busy) / busy


# -------------------------------------------------------------------------------------------- market

def project_shed(s, actions):
    shed = dict(s.shed)
    for u, a in enumerate(actions):
        if a and a[0] == "PICKUP":
            shed[a[1]] = shed.get(a[1], 0) - int(a[2])
    return shed


def animals_total(s):
    """Animals that need feeding from tomorrow: on tiles, waiting in the shed, carried."""
    n = sum(1 for row in s.tiles for t in row if isinstance(t, dict) and t.get("animal"))
    n += sum(s.shed.get(a, 0) for a in ANIMALS)
    n += sum(i.get(a, 0) for i in s.invs for a in ANIMALS)
    return n


def feed_reserve(s, extra_animals=0):
    """Wheat the bank of shed + carried should hold: before the units have left (hours 0-1) today's feeds,
    afterwards tomorrow's feeds; carried leftovers come back at day end."""
    if s.hour <= 1:
        unfed = sum(1 for row in s.tiles for t in row if isinstance(t, dict) and t.get("animal") and not t.get("fed_today"))
        return unfed + extra_animals + 2
    return animals_total(s) + extra_animals + 2


def wheat_stock(s):
    return s.shed.get("WHEAT", 0) + sum(i.get("WHEAT", 0) for i in s.invs)


def sell_orders(s, plan, shed):
    orders = []
    last = s.step >= 715
    tick = s.hour == 0 or s.step % 4 == 1
    for item in PRODUCTS:
        n = shed.get(item, 0)
        if item == "WHEAT" and not last:
            n -= max(0, feed_reserve(s) - sum(i.get("WHEAT", 0) for i in s.invs))
        if item == "FERTILIZER" and not last and plan.get("fertilize", True):
            n -= plan.get("fert_reserve", 4)
        if n <= 0 or s.prices.get(item, 0) <= 1:
            continue
        if last or tick or item == "FERTILIZER":
            orders.append(["SELL", item, n])
    orders.sort(key=lambda o: -s.prices.get(o[1], 0) * o[2])
    return orders


def room_guard(s, actions, orders):
    """Hour 23: everything carried lands in the shed at day end and the overflow past 100 is discarded.
    Sell the projected excess now (shed stock, highest price first; wheat for tomorrow last)."""
    if s.hour != 23 or s.step >= 715:
        return orders
    shed = project_shed(s, actions)
    for o in orders:
        if o[0] == "SELL":
            shed[o[1]] = shed.get(o[1], 0) - int(o[2])
        elif o[0] in ("BUY_PRODUCT", "BUY_ANIMAL"):
            shed[o[1]] = shed.get(o[1], 0) + int(o[2])
    carried = sum(sum(i.values()) for i in s.invs)
    for u, a in enumerate(actions):
        if not a:
            continue
        x, y = s.units[u]
        t = s.tiles[y][x] if 0 <= y < N and 0 <= x < N else None
        if a[0] == "HARVEST" and isinstance(t, dict):
            carried += int(t.get("yield_units", 0))
        elif a[0] == "COLLECT_FERTILIZER":
            carried += 1
        elif a[0] in ("FEED", "FERTILIZE"):
            carried -= 1
        elif a[0] == "PICKUP":
            carried += int(a[2])
        elif a[0] == "PLACE" and len(a) >= 2 and a[1] not in ANIMALS:
            carried -= int(a[2]) if len(a) >= 3 else 1
    excess = sum(v for v in shed.values() if v > 0) + carried - 100
    if excess <= 0:
        return orders
    keep_wheat = animals_total(s) + 2 - sum(i.get("WHEAT", 0) for i in s.invs)
    order = sorted((p for p in PRODUCTS if p != "WHEAT"), key=lambda p: -s.prices.get(p, 0)) + ["WHEAT", "WHEAT"]
    extra = {}
    for i, p in enumerate(order):
        avail = shed.get(p, 0) - extra.get(p, 0)
        if p == "WHEAT" and i == len(order) - 2:
            avail -= max(0, keep_wheat)
        k = min(excess, max(0, avail))
        if k > 0 and s.prices.get(p, 0) > 1:
            extra[p] = extra.get(p, 0) + k
            excess -= k
        if excess <= 0:
            break
    out = [list(o) for o in orders]
    for p, k in extra.items():
        for o in out:
            if o[0] == "SELL" and o[1] == p:
                o[2] = int(o[2]) + k
                break
        else:
            out.insert(0, ["SELL", p, k])
    return out


def workload_hires(s, jobs, cap):
    """Hands to hire at hour 0. Turns per tile per day: an animal ~4.7 (feed, care, collect, harvest, walk),
    a crop ~1.5, empty tiles to plant ~3; each unit gives ~21 useful turns after leaving the shed."""
    animals = crops = 0
    for row in s.tiles:
        for t in row:
            if isinstance(t, dict) and t.get("animal"):
                animals += 1
            elif isinstance(t, dict) and t.get("kind") == "PLANT":
                crops += 1
    plant_jobs = sum(1 for ops, _ in jobs.values() if ops and ops[0].startswith(("PLANT:", "BUILD:", "PLACE:", "DIG")))
    work = animals * 5.0 + crops * 2.0 + plant_jobs * 3 + 15
    floor = 10 if len(s.quads) >= 3 else (6 if len(s.quads) == 2 else 3)
    return max(0, min(cap, max(floor, int(math.ceil(work / 19.0)) - 1)))


def buy_orders(s, plan, jobs, actions, money):
    """Purchases in priority order: feed wheat, hires, land, animals (with their feed), seeds.
    One day of feed for every animal stays in the bank."""
    orders = []
    wprice = s.prices.get("WHEAT", 25) + 2
    wheat_buy = max(0, feed_reserve(s) - wheat_stock(s)) if s.step < 700 else 0
    money -= wheat_buy * wprice
    if s.hour <= 1:
        # the day's hire target is fixed at hour 0; hires that did not fit in hour 0's ten slots follow at hour 1
        if s.hour == 0 or "hire_target" not in plan:
            want = plan.get("hires")
            if want is None:
                want = workload_hires(s, jobs, plan.get("max_hires", 12))
            plan["hire_target"] = want
        for k in range(max(0, plan["hire_target"] - s.hires_today)):
            cost = fib(s.hires_today + k)
            if money < cost:
                break
            orders.append(["HIRE"])
            money -= cost
    money -= animals_total(s) * wprice + 20
    for q in plan.get("land", []):
        i = len(s.quads) - 1
        if i < 3 and money >= LAND_PRICE[i]:
            orders.append(["BUY_LAND"])
            money -= LAND_PRICE[i]
    for a in ANIMALS:
        struct = ANIMALS[a]["struct"]
        want = 0
        for xy, (ops, _) in jobs.items():
            if ("PLACE:" + a) in ops or (("BUILD:" + struct) in ops and plan["targets"].get(xy) == a):
                want += 1
        have = s.shed.get(a, 0) + sum(i.get(a, 0) for i in s.invs)
        unit = ANIMALS[a]["cost"] + 3 * wprice
        k = min(want - have, int(max(0, money) // unit))
        if k > 0:
            orders.append(["BUY_ANIMAL", a, k])
            money -= k * unit
            wheat_buy += 2 * k
    for crop in CROPS:
        want = sum(1 for (ops, _) in jobs.values() if ("PLANT:" + crop) in ops)
        k = min(want - s.seeds.get(crop, 0), int(max(0, money) // CROPS[crop]["seed"]))
        if k > 0 and s.step < 700:
            orders.append(["BUY_SEED", crop, k])
            money -= k * CROPS[crop]["seed"]
    if wheat_buy > 0:
        orders.insert(0, ["BUY_PRODUCT", "WHEAT", wheat_buy])
    return orders


def fib(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


# --------------------------------------------------------------------------------------------- agent

MEM = {}


def agent(obs, config=None):
    s = parse(obs)
    mem = MEM.get(s.me)
    if mem is None or s.step == 0 or mem.get("step", -1) >= s.step:
        mem = MEM[s.me] = {}
    mem["step"] = s.step
    plan = make_plan(s, mem)
    if s.hour == 1 and "hire_target" in mem:
        plan["hire_target"] = mem["hire_target"]
    jobs = build_jobs(s, plan)
    actions = assign(s, mem, plan, jobs)
    shed = project_shed(s, actions)
    sells = sell_orders(s, plan, shed)
    money = s.money + sum(n * s.prices.get(item, 0) * 0.9 for _, item, n in sells)
    buys = buy_orders(s, plan, jobs, actions, money)
    if s.hour == 0 and "hire_target" in plan:
        mem["hire_target"] = plan["hire_target"]
    hires = [o for o in buys if o[0] == "HIRE"]
    rest = [o for o in buys if o[0] != "HIRE"]
    # hires first: each is one of the ten market slots and a hand hired now works from the next step
    market = room_guard(s, actions, hires + sells + rest)[:10]
    return {"farmer": actions[0], "hands": actions[1:], "market": market}
