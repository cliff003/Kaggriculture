"""Team 42 gold agent for Kaggriculture: an adaptive scheduler after DSM's play.

Layers (state is rebuilt from the observation every step; memory only keeps plans):
  model    parse the observation into S
  plan     daily targets: land, animals, crops, hires, purchases
  jobs     per-tile bundles of ordered ops for today
  routes   load-balanced petals around the shed, nearest-neighbour + 2-opt inside each petal
  execute  one action per unit per step, checked against the observation
  market   DSM-style sales, order slots, purchases
"""
import math
import os

DEBUG = False

N = 10
TPD = 24
SHED = ((4, 4), (5, 4), (4, 5), (5, 5))
SHED_SET = frozenset(SHED)
LAND_ORDER = ("NE", "SW", "SE")
LAND_PRICE = (1000, 2000, 4000)
MOVES = {(1, 0): "EAST", (-1, 0): "WEST", (0, 1): "SOUTH", (0, -1): "NORTH"}
LAST_STEP = 718  # last step whose actions the engine executes

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
BUILD_OP = {"COOP": "BUILD_COOP", "PASTURE": "BUILD_PASTURE"}
PRODUCTS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER")
BASE = {"WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120, "MELON": 250, "EGG": 50,
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

OP_VALUE = 25.0   # rough value of one unit-turn, charged when an op only buys a little extra yield

# op priorities (lower = more important)
P_CRIT = 0     # dies / escapes tonight otherwise
P_WIN = 1      # one-day window: product lost to a cap or to decay otherwise
P_YIELD = 2    # adds yield today (window watering, fertilizer on the right day, production-day feed)
P_HARV = 3     # harvest that can wait
P_PLANT = 4    # plant, build, place, dig
P_LOW = 5      # collect fertilizer, value-based feed and care on non-production days
P_OPT = 6      # optional watering


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
    """Engine market_price with the default parameters."""
    base, T, bf, bt, af, at = MARKET_PARAMS[item]
    if inv < I0:
        p = base + bt * base / _shape(bf, T, T) * _shape(bf, I0 - inv, T)
    else:
        p = base - at * base / _shape(af, T, T) * _shape(af, inv - I0, T)
    return max(1, int(round(p)))


def fib(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def quad_of(x, y):
    return ("N" if y < 5 else "S") + ("W" if x < 5 else "E")


def dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def shed_dist(p):
    return min(abs(p[0] - x) + abs(p[1] - y) for x, y in SHED)


def nearest_shed(p):
    return min(SHED, key=lambda s: abs(p[0] - s[0]) + abs(p[1] - s[1]))


def step_toward(p, t):
    dx, dy = t[0] - p[0], t[1] - p[1]
    if abs(dx) >= abs(dy) and dx:
        return MOVES[(1 if dx > 0 else -1, 0)]
    if dy:
        return MOVES[(0, 1 if dy > 0 else -1)]
    if dx:
        return MOVES[(1 if dx > 0 else -1, 0)]
    return "PASS"


def _g(o, k, d=None):
    try:
        v = o[k]
    except Exception:
        v = getattr(o, k, d)
    return d if v is None else v


# ------------------------------------------------------------------------------------------------ model

class S:
    pass


def parse(obs):
    s = S()
    s.me = int(_g(obs, "player", 0))
    s.step = int(_g(obs, "step", 0))
    s.day, s.hour = s.step // TPD, s.step % TPD
    farms = _g(obs, "farms")
    f = farms[s.me]
    s.money = float(_g(f, "money", 0))
    s.tiles = _g(f, "tiles")
    s.units = [tuple(_g(f, "farmer"))] + [tuple(h) for h in (_g(f, "hands", []) or [])]
    s.quads = list(_g(f, "unlocked_quadrants", ["NW"]))
    s.hires_today = int(_g(f, "hires_today", 0))
    o = farms[1 - s.me]
    s.opp_money = float(_g(o, "money", 0))
    s.opp_tiles = _g(o, "tiles")
    priv = _g(obs, "private", {})
    s.shed = {k: int(v) for k, v in dict(_g(priv, "shed", {})).items() if int(v) > 0}
    s.seeds = {k: int(v) for k, v in dict(_g(priv, "seeds", {})).items() if int(v) > 0}
    s.invs = [{k: int(v) for k, v in dict(i).items() if int(v) > 0} for i in (_g(priv, "inventories", [{}]) or [{}])]
    while len(s.invs) < len(s.units):
        s.invs.append({})
    m = _g(obs, "market", {})
    s.prices = {k: int(v) for k, v in dict(_g(m, "prices", {})).items()}
    s.minv = {k: int(v) for k, v in dict(_g(m, "inventory", {})).items()}
    s.shops = list(_g(_g(obs, "town", {}), "unlocked_shops", []) or [])
    return s


def tile_at(s, xy):
    return s.tiles[xy[1]][xy[0]]


def is_dict(t):
    return t is not None and t != "LOCKED"


def unlocked(s, xy):
    return quad_of(*xy) in s.quads


# ------------------------------------------------------------------------------------------------ timing
# All rules below follow kaggriculture.py: WATER bonus 431-444, HARVEST 446-473, decay 752-766,
# ongoing production 786-802, animals 805-833.

def last_prod_age(crop):
    """Ongoing crop: age whose night produces the last (max_yield-th) unit."""
    c = CROPS[crop]
    return c["first"] - 1 + c["interval"] * (c["maxy"] - 1)


def prod_tonight_crop(crop, age):
    c = CROPS[crop]
    if not c["ongoing"]:
        return False
    k = age - (c["first"] - 1)
    return k >= 0 and k % c["interval"] == 0 and k // c["interval"] + 1 <= c["maxy"]


def animal_prod_tonight(animal, age):
    a = ANIMALS[animal]
    k = age + 1 - a["first"]
    return k >= 0 and k % a["interval"] == 0


def animal_last_night(animal, placed_day, last_day=28):
    """Last production night (day index whose end-of-day refresh produces) <= last_day."""
    a = ANIMALS[animal]
    first_night = placed_day + a["first"] - 1
    if first_night > last_day:
        return None
    return first_night + ((last_day - first_night) // a["interval"]) * a["interval"]


def plant_deadline(crop):
    """Last day on which planting still pays off fully."""
    return {"WHEAT": 27, "CARROT": 26, "TOMATO": 18, "STRAWBERRY": 13, "MELON": 1}[crop]


# ------------------------------------------------------------------------------------------------ jobs
# A job lists the ops one unit runs on one tile today, in order, each with a priority. Jobs are
# stateless: they are rebuilt from the tile as it is now, so a half-done job simply shrinks.

class Job:
    __slots__ = ("xy", "ops", "prio", "wheat", "fert", "fert_gain", "animal", "seed", "kind")

    def __init__(self, xy, kind):
        self.xy = xy
        self.ops = []
        self.prio = 9
        self.wheat = 0
        self.fert = 0
        self.fert_gain = 0
        self.animal = None
        self.seed = None
        self.kind = kind

    def add(self, op, arg, prio):
        self.ops.append((op, arg, prio))
        if prio < self.prio:
            self.prio = prio
        if op == "FEED":
            self.wheat += 1
        elif op == "FERTILIZE":
            self.fert += 1
        elif op == "COLLECT_FERTILIZER":
            self.fert_gain += 1
        elif op == "PLACE":
            self.animal = arg
        elif op == "PLANT":
            self.seed = arg

    def dur(self):
        return len(self.ops)


class Policy:
    """Daily knobs the job rules need; filled by the planner."""

    def __init__(self, day):
        self.day = day
        self.fert_ok = day >= 10              # use fertilizer on crops
        self.fert_value = 40.0                # opportunity value of one fertilizer
        self.prices = {}
        self.targets = {}                     # (x, y) -> crop or animal the tile should hold next
        self.wheat_age3 = True                # fertilized wheat harvested at age 3 (5 units)
        self.feed_ratio = {"COW": 2.0, "SHEEP": 1.0, "GOOSE": 0.0}
        self.last_feed_day = 28
        self.early_harvest = set()            # tiles whose one-time crop should come off today
        self.melon_hold = False
        self.wheat_a3 = None                  # wheat tiles allowed to come off at age 3 today (None = all)

    def price(self, item):
        return self.prices.get(item, BASE[item])


def replant_ops(job, pol, xy, hour, prio=P_PLANT):
    tgt = pol.targets.get(xy)
    if tgt in CROPS:
        if pol.day <= plant_deadline(tgt) and hour <= 22:
            job.add("PLANT", tgt, prio)
            job.add("WATER", None, P_CRIT)
    elif tgt in ANIMALS:
        job.add(BUILD_OP[ANIMALS[tgt]["struct"]], None, prio)
        job.add("PLACE", tgt, prio)


def one_time_path(crop, age, y, watered, fu, day, fert_now, age3):
    """Yield path of a one-time crop when every window day is watered: (harvest age, units)."""
    c = CROPS[crop]
    ws = (c["maxday"] + 1) // 2
    a, d, tot = age, day, y
    while True:
        if ws <= a <= c["maxday"] and not (a == age and watered):
            f = fu >= d or (fert_now and d <= day + 2)
            tot = min(c["maxy"], tot + (2 if f else 1))
        if a >= c["first"] and (tot >= c["maxy"] or a >= c["maxday"]
                                or (crop == "WHEAT" and age3 and a >= 3 and tot >= 5)):
            return a, tot
        a += 1
        d += 1


def crop_job(t, xy, pol, hour, fert_in_hand=None):
    """Ops for a plant tile. fert_in_hand: None = planning (assume fertilizer can be brought when the
    policy wants it), otherwise the executing unit's fertilizer count."""
    day = pol.day
    crop = t["crop"]
    c = CROPS[crop]
    age = day - int(t["planted_day"])
    y = int(t["yield_units"])
    watered = bool(t["watered_today"])
    cu = int(t["consecutive_unwatered"])
    fu = int(t["fertilized_until_day"])
    must_w = (not watered) and cu >= 1
    job = Job(xy, "crop")
    can_fert = pol.fert_ok and (fert_in_hand is None or fert_in_hand > 0)
    price = pol.price(crop)
    if not c["ongoing"]:
        ws = (c["maxday"] + 1) // 2
        maxy, maxday = c["maxy"], c["maxday"]
        fert_active = fu >= day
        in_win = ws <= age <= maxday and y < maxy
        fert_now = False
        if in_win and not watered and not fert_active and can_fert and crop != "MELON":
            a0, u0 = one_time_path(crop, age, y, watered, fu, day, False, pol.wheat_age3)
            a1, u1 = one_time_path(crop, age, y, watered, fu, day, True, pol.wheat_age3)
            if (u1 - u0) * price + (a0 - a1) * 30 > pol.fert_value:
                fert_now = True
        bonus = 0
        if in_win and not watered:
            bonus = 2 if (fert_active or fert_now) else 1
        y_after = min(maxy, y + bonus)
        harvest = False
        h_prio = P_HARV
        if age >= c["first"] and y_after > 0:
            if age >= maxday:
                harvest, h_prio = True, P_WIN          # decays from tomorrow 00:00
            elif y_after >= maxy:
                harvest = not (crop == "MELON" and pol.melon_hold)
                h_prio = P_WIN if crop == "MELON" and age >= maxday - 1 else P_HARV
            elif crop == "WHEAT" and pol.wheat_age3 and age >= 3 and y_after >= 5                     and (pol.wheat_a3 is None or xy in pol.wheat_a3):
                harvest = True
            elif day >= 29 or xy in pol.early_harvest:
                harvest, h_prio = True, P_WIN
        if fert_now:
            job.add("FERTILIZE", None, P_YIELD)
        if not watered and (in_win or must_w):
            if must_w:
                wp = P_CRIT
            elif crop == "MELON":
                wp = P_WIN if in_win else P_YIELD
            else:
                wp = P_YIELD
            job.add("WATER", None, wp)
        if harvest:
            if crop == "MELON":
                job.kind = "melon"
                h_prio = P_WIN
            job.add("HARVEST", None, h_prio)
            if not (crop == "MELON" and hour < 14):
                replant_ops(job, pol, xy, hour + len(job.ops))
        return job
    # ongoing crop (tomato, strawberry)
    maxy = c["maxy"]
    last = last_prod_age(crop)
    final = age > last
    prod = prod_tonight_crop(crop, age)
    fert_active = fu >= day
    fert_now = False
    if prod and not fert_active and can_fert:
        nights = sum(1 for k in range(3) if prod_tonight_crop(crop, age + k))
        fert_now = nights * price > pol.fert_value
    doubled = prod and (fert_active or fert_now)
    tonight = (2 if doubled else 1) if prod else 0
    if y > 0 and age >= c["first"]:
        if final or day >= 29:
            job.add("HARVEST", None, P_WIN)
        elif y + tonight > maxy:
            job.add("HARVEST", None, P_WIN)
        elif y >= 2:
            job.add("HARVEST", None, P_HARV)     # sell early; the tile is visited for water anyway
    if final:
        if pol.targets.get(xy) is not None and pol.targets.get(xy) != "KEEP":
            job.add("DIG", None, P_PLANT)
            replant_ops(job, pol, xy, hour + len(job.ops))
        return job
    if fert_now:
        job.add("FERTILIZE", None, P_WIN)
    if not watered:
        if must_w:
            job.add("WATER", None, P_CRIT)
        elif doubled:
            job.add("WATER", None, P_WIN)      # a watered, fertilized production night pays one more unit
        else:
            # daily watering keeps a long-lived plant one missed day away from dying
            job.add("WATER", None, P_YIELD)
    return job


def animal_job(t, xy, pol, wheat_in_hand=None):
    day = pol.day
    animal = t["animal"]
    a = ANIMALS[animal]
    age = day - int(t["placed_day"])
    y = int(t["yield_units"])
    fed = bool(t["fed_today"])
    cared = bool(t["cared_today"])
    cuf = int(t["consecutive_unfed"])
    pend = int(t.get("pending_care_bonus", 0) or 0)
    held = a["held"]
    job = Job(xy, "animal")
    last = animal_last_night(animal, int(t["placed_day"]), pol.last_feed_day)
    releasing = last is None or day > last
    prod = animal_prod_tonight(animal, age) and not releasing
    ratio = pol.price(a["product"]) / max(1.0, pol.price("WHEAT"))
    feed = False
    fprio = P_LOW
    if not fed and not releasing and day < 29:
        if cuf >= 1:
            feed, fprio = True, P_CRIT
        elif prod:
            feed, fprio = True, P_WIN
        elif animal == "COW" and age in (0, a["first"] - 2):
            feed = False       # first production is capped at 6: two spare days of care
        elif animal == "GOOSE" or ratio >= pol.feed_ratio.get(animal, 1.0):
            feed, fprio = True, (P_WIN if animal != "GOOSE" else P_YIELD)
    care = False
    if not cared and not releasing and day < 29 and (feed or fed):
        care = not (last is not None and day == last)   # no production after tonight's
    tonight = (1 + (pend if (feed or fed) else 0)) if prod else 0
    if y > 0:
        escaping = releasing and cuf >= 1
        if y + tonight > held or escaping or day >= 29:
            job.add("HARVEST", None, P_WIN)
        elif y >= {"GOOSE": 3, "COW": 3, "SHEEP": 4}[animal]:
            job.add("HARVEST", None, P_WIN if day < 10 else P_HARV)
    if feed:
        job.add("FEED", None, fprio)
    if care:
        job.add("CARE", None, fprio if fprio > P_CRIT else P_YIELD)
    if t.get("fertilizer_available"):
        job.add("COLLECT_FERTILIZER", None, P_HARV)
    return job


def tile_job(s, xy, pol, hour=None, fert_in_hand=None):
    """Job for one tile as it is now (None when nothing to do)."""
    t = s.tiles[xy[1]][xy[0]]
    hour = s.hour if hour is None else hour
    if t == "LOCKED":
        return None
    if t is None:
        tgt = pol.targets.get(xy)
        if tgt is None or tgt == "KEEP":
            return None
        job = Job(xy, "empty")
        replant_ops(job, pol, xy, hour)
        return job if job.ops else None
    kind = t.get("kind")
    if kind == "PLANT":
        job = crop_job(t, xy, pol, hour, fert_in_hand)
        return job if job.ops else None
    if kind == "WEED":
        tgt = pol.targets.get(xy)
        if tgt is None or tgt == "KEEP":
            return None
        job = Job(xy, "weed")
        job.add("DIG", None, P_PLANT)
        replant_ops(job, pol, xy, hour + 1)
        return job
    if t.get("animal"):
        job = animal_job(t, xy, pol)
        return job if job.ops else None
    if kind in ("COOP", "PASTURE"):
        tgt = pol.targets.get(xy)
        if tgt in ANIMALS and ANIMALS[tgt]["struct"] == kind:
            job = Job(xy, "place")
            job.add("PLACE", tgt, P_PLANT)
            return job
        if tgt in CROPS:
            job = Job(xy, "dig")
            job.add("DIG", None, P_PLANT)
            replant_ops(job, pol, xy, hour + 1)
            return job
    return None


def build_jobs(s, pol):
    jobs = {}
    for y in range(N):
        for x in range(N):
            j = tile_job(s, (x, y), pol)
            if j is not None:
                jobs[(x, y)] = j
    return jobs


# ------------------------------------------------------------------------------------------------ routes
# Petals: jobs sorted by angle around the shed centre, cut into contiguous arcs whose load matches each
# unit's remaining turns; inside an arc the order is nearest-neighbour from the unit, then 2-opt.

class Stop:
    __slots__ = ("kind", "xy", "pick", "place", "wait", "must")

    def __init__(self, kind, xy=None, pick=None, place=None, must=False):
        self.kind = kind            # "T" tile job, "S" shed visit (PLACE deliveries, then PICKUPs)
        self.xy = xy
        self.pick = dict(pick or {})
        self.place = dict(place or {})    # item -> n (n < 0: everything of that item carried)
        self.wait = 0
        self.must = must            # end-of-day unload that rebalancing keeps


def angle(xy):
    return math.atan2(xy[1] - 4.5, xy[0] - 4.5)


def path_len(start, seq):
    t, p = 0, start
    for xy in seq:
        t += abs(p[0] - xy[0]) + abs(p[1] - xy[1])
        p = xy
    return t


def two_opt(start, seq):
    n = len(seq)
    if n < 3:
        return list(seq)
    pts = [start] + list(seq)
    improved, it = True, 0
    while improved and it < 12:
        improved = False
        it += 1
        for i in range(1, n):
            for j in range(i + 1, n + 1):
                a, b, c = pts[i - 1], pts[i], pts[j]
                d = pts[j + 1] if j < n else None
                old = abs(a[0] - b[0]) + abs(a[1] - b[1]) + (abs(c[0] - d[0]) + abs(c[1] - d[1]) if d else 0)
                new = abs(a[0] - c[0]) + abs(a[1] - c[1]) + (abs(b[0] - d[0]) + abs(b[1] - d[1]) if d else 0)
                if new < old:
                    pts[i:j + 1] = pts[i:j + 1][::-1]
                    improved = True
    return pts[1:]


def order_tiles(start, tiles):
    rest = list(tiles)
    seq = []
    p = start
    while rest:
        k = min(range(len(rest)), key=lambda i: (abs(p[0] - rest[i][0]) + abs(p[1] - rest[i][1]), shed_dist(rest[i])))
        p = rest.pop(k)
        seq.append(p)
    return two_opt(start, seq)


def route_needs(seq, jobs):
    """Wheat to carry, largest fertilizer shortfall along the route, animals to place."""
    wheat = 0
    bal, short = 0, 0
    animals = {}
    for xy in seq:
        j = jobs.get(xy)
        if j is None:
            continue
        wheat += j.wheat
        bal -= j.fert
        if -bal > short:
            short = -bal
        bal += j.fert_gain
        if j.animal:
            animals[j.animal] = animals.get(j.animal, 0) + 1
    return wheat, short, animals


def route_time(u, seq, jobs):
    t = path_len(u["pos"], seq) + sum(jobs[xy].dur() for xy in seq if xy in jobs)
    w, f, an = route_needs(seq, jobs)
    inv = u.get("inv", {})
    picks = (1 if w > inv.get("WHEAT", 0) else 0) + (1 if f > inv.get("FERTILIZER", 0) else 0) + len(an)
    if picks and u["pos"] not in SHED_SET:
        t += shed_dist(u["pos"]) + shed_dist(seq[0]) if seq else 0
    return t + picks


def trim_jobs(jobs, capacity):
    """Leave out whole jobs whose most important op is of low priority (farthest from the shed first)
    until the load fits the crew's turns. Left-out jobs stay unowned; idle units pick them up."""
    def load():
        return sum(j.dur() + 1.7 for j in jobs.values())
    total = load()
    for level in (P_OPT, P_LOW, P_PLANT):
        if total <= capacity:
            break
        for xy in sorted([xy for xy, j in jobs.items() if j.prio >= level], key=lambda q: -shed_dist(q)):
            total -= jobs[xy].dur() + 1.7
            del jobs[xy]
            if total <= capacity:
                break
    return jobs, 99


def petal_plan(units, jobs):
    """units: dicts idx, pos, cap (turns left today), inv. Returns {idx: [tile xy, ...]}."""
    out = {u["idx"]: [] for u in units}
    items = list(jobs.values())
    K = len(units)
    if not items or K == 0:
        return out
    items.sort(key=lambda j: angle(j.xy))
    n = len(items)
    if n > 1:
        angs = [angle(j.xy) for j in items]
        best, cut = -1.0, 0
        for i in range(n):
            g = (angs[(i + 1) % n] - angs[i]) % (2 * math.pi)
            if g > best:
                best, cut = g, (i + 1) % n
        items = items[cut:] + items[:cut]
    a0 = angle(items[0].xy)
    us = sorted(units, key=lambda u: ((angle(u["pos"]) - a0 + 0.35) % (2 * math.pi), u["idx"]))
    load = [j.dur() + 1.3 for j in items]
    total = sum(load)
    caps = [max(1.0, u["cap"] - 2.0) for u in us]
    ctot = sum(caps)
    arcs = [[] for _ in us]
    k, acc = 0, 0.0
    share = total * caps[0] / ctot
    for j, ld in zip(items, load):
        if k < K - 1 and acc + ld / 2 > share:
            k += 1
            acc = 0.0
            share = total * caps[k] / ctot
        arcs[k].append(j.xy)
        acc += ld
    seqs = [order_tiles(u["pos"], arc) for u, arc in zip(us, arcs)]
    over = [route_time(u, sq, jobs) - u["cap"] for u, sq in zip(us, seqs)]
    for _ in range(4 * K):
        i = max(range(K), key=lambda q: over[q])
        if over[i] <= 0 or not arcs[i]:
            break
        best = None
        for nb, front in (((i - 1) % K, True), ((i + 1) % K, False)):
            if nb == i or not arcs[i]:
                continue
            xy = arcs[i][0] if front else arcs[i][-1]
            a_i = [p for p in arcs[i] if p != xy]
            a_n = arcs[nb] + [xy] if front else [xy] + arcs[nb]
            s_i = order_tiles(us[i]["pos"], a_i)
            s_n = order_tiles(us[nb]["pos"], a_n)
            o_i = route_time(us[i], s_i, jobs) - us[i]["cap"]
            o_n = route_time(us[nb], s_n, jobs) - us[nb]["cap"]
            m = max(o_i, o_n)
            if m < max(over[i], over[nb]) and (best is None or m < best[0]):
                best = (m, nb, a_i, a_n, s_i, s_n, o_i, o_n)
        if best is None:
            break
        _, nb, a_i, a_n, s_i, s_n, o_i, o_n = best
        arcs[i], arcs[nb], seqs[i], seqs[nb], over[i], over[nb] = a_i, a_n, s_i, s_n, o_i, o_n
    for u, sq in zip(us, seqs):
        out[u["idx"]] = tiered(u["pos"], sq, jobs)
    return out


def tiered(start, seq, jobs):
    """Animals first (morning, near the shed: feed, care, collect the fertilizer the crops need), then
    urgent crop tiles, then the other crop tiles; nearest-neighbour + 2-opt inside each group."""
    mel = [xy for xy in seq if jobs.get(xy) is not None and jobs[xy].kind == "melon"]
    an = [xy for xy in seq if jobs.get(xy) is not None and jobs[xy].kind in ("animal", "place")]
    taken = set(an) | set(mel)
    rest = [xy for xy in seq if xy not in taken]
    a = [xy for xy in rest if urgent(jobs.get(xy))]
    b = [xy for xy in rest if not urgent(jobs.get(xy))]
    out, p = [], start
    for grp in (mel, an, a, b):
        if grp:
            o = order_tiles(p, grp)
            out += o
            p = o[-1]
    return out


def make_stops(u, seq, jobs, shed_avail, delivery=None):
    """Turn an ordered tile list into stops: a shed stop first for the supplies the route needs."""
    wheat, fert, animals = route_needs(seq, jobs)
    inv = u.get("inv", {})
    pick = {}
    w = max(0, wheat - inv.get("WHEAT", 0))
    if w:
        k = min(w, shed_avail.get("WHEAT", 0))
        if k > 0:
            pick["WHEAT"] = k
            shed_avail["WHEAT"] -= k
    f = max(0, fert - inv.get("FERTILIZER", 0))
    if f:
        k = min(f, shed_avail.get("FERTILIZER", 0))
        if k > 0:
            pick["FERTILIZER"] = k
            shed_avail["FERTILIZER"] -= k
    for a, n in animals.items():
        k = min(max(0, n - inv.get(a, 0)), shed_avail.get(a, 0))
        if k > 0:
            pick[a] = k
            shed_avail[a] -= k
    stops = []
    if pick:
        stops.append(Stop("S", pick=pick))
    for xy in seq:
        stops.append(Stop("T", xy))
    return stops


# ------------------------------------------------------------------------------------------------ execute

CHAIN_OPS = frozenset(("HARVEST", "DIG", "PLANT", "BUILD_COOP", "BUILD_PASTURE", "PLACE"))


class Ctx:
    """Book-keeping for one step: shed stock after this step's pickups and placements, seeds left."""

    def __init__(self, s):
        self.shed_left = dict(s.shed)
        self.room = 100 - sum(s.shed.values())
        self.seed_left = dict(s.seeds)
        self.placed = {}
        self.picked = {}


def usable_ops(job, inv, ctx, t, max_prio=99):
    """Ops of a job this unit can run now, in order (drops ops that lack supplies or were trimmed)."""
    out = []
    has_wheat = inv.get("WHEAT", 0) > 0
    fed = bool(t.get("fed_today")) if isinstance(t, dict) else False
    for op, arg, pr in job.ops:
        ok = pr <= max_prio
        if op == "FEED" and not has_wheat:
            ok = False
        elif op == "CARE" and not (fed or (has_wheat and any(o[0] == "FEED" for o in job.ops))):
            ok = False
        elif op == "FERTILIZE" and inv.get("FERTILIZER", 0) <= 0:
            ok = False
        elif op == "PLACE" and inv.get(arg, 0) <= 0:
            ok = False
        if ok:
            out.append((op, arg, pr))
        elif op in CHAIN_OPS:
            break     # later ops (replant, water the new seedling) depend on this one
    return out


def unit_act(s, mem, pol, u, ctx):
    pos = s.units[u]
    inv = s.invs[u] if u < len(s.invs) else {}
    stops = mem["routes"].get(u)
    if stops is not None and s.day < 29:
        prem = inv.get("MILK", 0) + inv.get("WOOL", 0) + inv.get("MELON", 0)
        if s.day < 10:
            prem += 3 * inv.get("FERTILIZER", 0)
        sd = shed_dist(pos)
        if (prem >= 3 or inv.get("MELON", 0) >= 1) and sd <= (4 if inv.get("MELON", 0) else 2)                 and not (stops and stops[0].kind == "S"):
            nxt = next((st.xy for st in stops if st.kind == "T"), None)
            if nxt is None or shed_dist(nxt) > sd or inv.get("MELON", 0):
                stops.insert(0, Stop("S", place={"MELON": -1, "MILK": -1, "WOOL": -1, "STRAWBERRY": -1, "EGG": -1,
                                                 "FERTILIZER": -1 if s.day < 10 else 0}))
    guard = 0
    while stops and guard < 12:
        guard += 1
        st = stops[0]
        if st.kind == "S":
            if pos not in SHED_SET:
                return [step_toward(pos, nearest_shed(pos))]
            if st.place and not st.pick:
                carried = sum(v for v in inv.values() if v > 0)
                later = [x for x in stops[1:] if x.kind == "T"]
                jobs_now = mem.get("jobs", {})
                needs = any(jobs_now.get(x.xy) is not None and (jobs_now[x.xy].wheat or jobs_now[x.xy].fert)
                            for x in later)
                if carried and carried <= ctx.room and not needs:
                    stops.pop(0)
                    ctx.room -= carried
                    for k2, v2 in inv.items():
                        if v2 > 0:
                            ctx.placed[k2] = ctx.placed.get(k2, 0) + v2
                    return ["DROP"]
            for item in list(st.place):
                n = inv.get(item, 0) if st.place[item] < 0 else min(st.place[item], inv.get(item, 0))
                k = min(n, ctx.room)
                del st.place[item]
                if k > 0:
                    ctx.room -= k
                    ctx.placed[item] = ctx.placed.get(item, 0) + k
                    return ["PLACE", item, k]
            for item in list(st.pick):
                k = min(st.pick[item], ctx.shed_left.get(item, 0))
                if k > 0:
                    del st.pick[item]
                    ctx.shed_left[item] -= k
                    ctx.room += k
                    ctx.picked[item] = ctx.picked.get(item, 0) + k
                    return ["PICKUP", item, k]
                if st.wait < mem.get("pick_wait", 2) and item in mem.get("pending_buys", ()):
                    st.wait += 1
                    return ["PASS"]
                del st.pick[item]
            stops.pop(0)
            continue
        xy = st.xy
        t = s.tiles[xy[1]][xy[0]]
        hour_at = s.hour + dist(pos, xy)
        job = tile_job(s, xy, pol, hour_at, fert_in_hand=inv.get("FERTILIZER", 0))
        ops = usable_ops(job, inv, ctx, t, mem.get("max_prio", 99)) if job is not None else []
        if not ops:
            stops.pop(0)
            mem["owner"].pop(xy, None)
            continue
        if pos != xy:
            return [step_toward(pos, xy)]
        turns_left = 24 - s.hour
        if len(ops) > turns_left:
            crit = [o for o in ops if o[2] == P_CRIT and o[0] not in CHAIN_OPS]
            if crit and ops[0][2] != P_CRIT:
                ops = crit
        op, arg, _ = ops[0]
        if op == "PLANT":
            if ctx.seed_left.get(arg, 0) <= 0 or s.hour > 22:
                st.wait += 1
                if st.wait > 30 or s.hour > 22:
                    stops.pop(0)
                    mem["owner"].pop(xy, None)
                elif len(stops) > 1:
                    stops.append(stops.pop(0))
                else:
                    return ["PASS"]
                continue
            ctx.seed_left[arg] -= 1
        mem["started"][u] = xy
        return [op] if arg is None else [op, arg]
    return None


def route_eta(pos, stops, jobs):
    """Turns needed for the stops, in order; returns the list of finish times."""
    t, p, out = 0, pos, []
    for st in stops:
        if st.kind == "S":
            q = nearest_shed(p)
            t += dist(p, q) + len(st.pick) + (1 if st.place else 0)   # one DROP delivers everything
            p = q
        else:
            j = jobs.get(st.xy)
            t += dist(p, st.xy) + (j.dur() if j is not None else 0)
            p = st.xy
        out.append(t)
    return out


def urgent(j):
    return j is not None and j.prio <= P_WIN


def rebalance_routes(s, mem, jobs):
    """A unit that cannot finish its stops today keeps the urgent ones (done first, nearest-neighbour
    order) and releases the rest to the pool, where idle units pick them up."""
    end = 21 if s.day >= 29 else 23
    left = end - s.hour + 1
    last = mem.setdefault("rebal", {})
    for u, stops in mem["routes"].items():
        if u >= len(s.units) or not stops:
            continue
        if s.step - last.get(u, -99) < 2:
            continue
        if any(st.kind == "S" and "MELON" in st.place for st in stops):
            continue
        pos = s.units[u]
        eta = route_eta(pos, stops, jobs)
        if eta[-1] <= left + 1:
            continue
        last[u] = s.step
        head = [stops.pop(0)]
        urg = [st for st in stops if st.kind == "T" and urgent(jobs.get(st.xy))]
        rest = [st for st in stops if not (st.kind == "T" and urgent(jobs.get(st.xy)))]
        order = order_tiles(pos, [st.xy for st in urg])
        by = {st.xy: st for st in urg}
        picks = [st for st in rest if st.kind == "S" and st.pick]
        unloads = [st for st in rest if st.kind == "S" and not st.pick]
        cash_run = [st for st in unloads if s.day < 10 and "FERTILIZER" in st.place]
        must = [st for st in unloads if st.must]
        unloads = [st for st in unloads if st not in cash_run and not st.must]
        new = head + picks + [by[xy] for xy in order] + cash_run[:1]
        # add back the non-urgent stops while they still fit
        for st in rest:
            if st.kind == "S":
                continue
            trial = new + [st]
            if route_eta(pos, trial + must[:1], jobs)[-1] <= left:
                new = trial
            else:
                mem["owner"].pop(st.xy, None)
        if must:
            new = new + must[:1]
        elif unloads and route_eta(pos, new + unloads[:1], jobs)[-1] <= left:
            new = new + unloads[:1]
        mem["routes"][u] = new


SELLABLE = frozenset(("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"))


UNLOAD_FROM = 14
UNLOAD_ORDER = ("MELON", "STRAWBERRY", "WOOL", "MILK", "TOMATO", "FERTILIZER", "EGG", "CARROT", "WHEAT")


def carry_at_end(s, inv, stops, jobs):
    """Goods the unit will hold when its stops are done: what it carries now, plus harvests and collected
    fertilizer, minus feeds, fertilizing, placed animals and shed deliveries along the way."""
    c = {k: v for k, v in inv.items() if v > 0}
    for st in stops:
        if st.kind == "S":
            for item, n in st.place.items():
                if item in c:
                    if n < 0:
                        del c[item]
                    elif n > 0:
                        c[item] = max(0, c[item] - n)
            for item, n in st.pick.items():
                c[item] = c.get(item, 0) + n
            continue
        j = jobs.get(st.xy)
        if j is None:
            continue
        t = tile_at(s, st.xy)
        for op, arg, pr in j.ops:
            if op == "HARVEST" and is_dict(t):
                item = t.get("crop") or ANIMALS.get(t.get("animal"), {}).get("product")
                if item:
                    c[item] = c.get(item, 0) + max(1, int(t.get("yield_units", 0) or 0))
            elif op == "COLLECT_FERTILIZER":
                c["FERTILIZER"] = c.get("FERTILIZER", 0) + 1
            elif op == "FEED" and c.get("WHEAT", 0) > 0:
                c["WHEAT"] -= 1
            elif op == "FERTILIZE" and c.get("FERTILIZER", 0) > 0:
                c["FERTILIZER"] -= 1
            elif op == "PLACE" and c.get(arg, 0) > 0:
                c[arg] -= 1
    return sum(v for v in c.values() if v > 0)


def trim_to_fit(s, mem, u, stops, jobs, left):
    """Drop the least important tile stops (never life-saving ones, never the one in progress) until the
    route with its end-of-day unload fits the turns left."""
    pos = s.units[u]
    while stops and route_eta(pos, stops, jobs)[-1] > left:
        best = None
        for i, st in enumerate(stops):
            if st.kind != "T" or (i == 0 and st.xy == pos):
                continue
            j = jobs.get(st.xy)
            pr = j.prio if j is not None else 9
            if pr <= P_CRIT:
                continue
            if best is None or (pr, i) > best[0]:
                best = ((pr, i), i)
        if best is None:
            return
        st = stops.pop(best[1])
        mem["owner"].pop(st.xy, None)


def plan_unloads(s, mem, pol):
    """From hour 15: if the goods units carry would not fit the shed at the day-end drop, the most
    loaded units closest to the shed go and PLACE their goods (sold before the drop)."""
    if s.day >= 29:
        return
    if 10 <= s.hour <= 20:
        for u, inv in enumerate(s.invs):
            n = sum(v for k, v in inv.items() if k in SELLABLE and k != "FERTILIZER")
            stops = mem["routes"].get(u, [])
            if n >= 8 and shed_dist(s.units[u]) <= 1 and not any(st.kind == "S" for st in stops[:1]):
                stops.insert(0, Stop("S", place={k: -1 for k in SELLABLE}))
                mem["routes"][u] = stops
    if s.hour < UNLOAD_FROM:
        return
    jobs = mem.get("jobs", {})
    left = 23 - s.hour + 1
    # goods that stay in the shed tonight: tomorrow's feed wheat, the fertilizer stock, waiting animals
    keep = min(s.shed.get("WHEAT", 0), feeds_tomorrow(s, pol)) + min(s.shed.get("FERTILIZER", 0), 20)
    keep += sum(s.shed.get(a, 0) for a in ANIMALS)
    proj = []
    total = keep
    for u, inv in enumerate(s.invs):
        stops = mem["routes"].get(u, [])
        if any(st.must for st in stops):
            trim_to_fit(s, mem, u, stops, jobs, left)
        n = carry_at_end(s, inv, stops, jobs)
        total += n
        if not any(st.must for st in stops):
            last = next((st.xy for st in reversed(stops) if st.kind == "T"), s.units[u])
            proj.append((n / (1.0 + 0.3 * shed_dist(last)), n, u))
    if total <= 97:
        return
    proj.sort(key=lambda q: -q[0])
    for _, n, u in proj:
        if total <= 90 or n < 6:
            break
        pos = s.units[u]
        new = list(mem["routes"].get(u, [])) + [Stop("S", place={k2: -1 for k2 in UNLOAD_ORDER}, must=True)]
        while route_eta(pos, new, jobs)[-1] > left - 1:
            best = None
            for i, st in enumerate(new):
                if st.kind != "T":
                    continue
                j = jobs.get(st.xy)
                pr = j.prio if j is not None else 9
                if pr <= P_CRIT:
                    continue
                if best is None or (pr, i) > best[0]:
                    best = ((pr, i), i)
            if best is None:
                break
            st = new.pop(best[1])
            mem["owner"].pop(st.xy, None)
        if route_eta(pos, new, jobs)[-1] > left + 1:
            continue
        mem["routes"][u] = new
        total -= n


def idle_act(s, mem, pol, u, ctx, jobs):
    """A unit without work: take the unowned or stealable job it reaches first."""
    pos = s.units[u]
    best = None
    for xy, j in jobs.items():
        if not job_ready(s, mem, j, u):
            continue
        owner = mem["owner"].get(xy)
        d = dist(pos, xy)
        if s.hour + d + j.dur() > 23:
            continue
        if owner is not None and owner != u:
            ostops = mem["routes"].get(owner, [])
            eta, p = 0, s.units[owner] if owner < len(s.units) else pos
            found = False
            for k, st in enumerate(ostops):
                if st.kind == "T":
                    eta += dist(p, st.xy)
                    if st.xy == xy:
                        found = k > 0
                        break
                    jj = jobs.get(st.xy)
                    eta += jj.dur() if jj else 1
                    p = st.xy
            if not found or eta <= d + 2:
                continue
        need_w = j.wheat > s.invs[u].get("WHEAT", 0) if u < len(s.invs) else False
        cost = d + (shed_dist(pos) + shed_dist(xy) if need_w else 0) + j.prio * 3
        if best is None or cost < best[0]:
            best = (cost, xy, owner, need_w)
    if best is None:
        return False
    _, xy, owner, need_w = best
    if owner is not None and owner != u:
        mem["routes"][owner] = [st for st in mem["routes"].get(owner, []) if not (st.kind == "T" and st.xy == xy)]
    stops = mem["routes"].setdefault(u, [])
    if need_w:
        stops.append(Stop("S", pick={"WHEAT": max(1, jobs[xy].wheat)}))
    stops.append(Stop("T", xy))
    mem["owner"][xy] = u
    mem.setdefault("inserted", {})[xy] = mem.setdefault("inserted", {}).get(xy, 0) + 1
    return True


def job_ready(s, mem, j, u=None):
    """Supplies for the job exist now (seeds in stock, animal bought, wheat in the shed or in hand)."""
    if j.seed and s.seeds.get(j.seed, 0) <= 0:
        return False
    if j.animal and j.ops and j.ops[0][0] == "PLACE":
        if s.shed.get(j.animal, 0) <= 0 and not (u is not None and s.invs[u].get(j.animal, 0) > 0):
            return False
    if j.wheat and all(o[0] in ("FEED", "CARE") for o in j.ops):
        if s.shed.get("WHEAT", 0) <= 0 and not (u is not None and s.invs[u].get("WHEAT", 0) > 0):
            return False
    return mem.setdefault("inserted", {}).get(j.xy, 0) < 3


def insert_new_jobs(s, mem, pol, jobs, nunits):
    """Cheapest insertion of jobs nobody owns (seeds or animals just arrived, new land, released feeds)."""
    routes = mem["routes"]
    free = [xy for xy, j in jobs.items() if xy not in mem["owner"] and j.prio <= P_LOW
            and any(job_ready(s, mem, j, u) for u in range(nunits))]
    if not free:
        return
    free.sort(key=lambda xy: (jobs[xy].prio, shed_dist(xy)))
    for xy in free[:20]:
        j = jobs[xy]
        best = None
        for u in range(nunits):
            if not job_ready(s, mem, j, u):
                continue
            stops = routes.setdefault(u, [])
            pos = s.units[u]
            tiles = [st.xy for st in stops if st.kind == "T"]
            pts = [pos] + tiles
            base_len = path_len(pos, tiles)
            used = base_len + sum((jobs[t].dur() if t in jobs else 1) for t in tiles)
            left = 23 - s.hour + 1 - used - j.dur()
            if left <= 0:
                continue
            # never ahead of a melon run: tiles before the last melon delivery stay first
            k0 = 0
            seen = 0
            k1 = len(pts)
            for st in stops:
                if st.kind == "T":
                    seen += 1
                elif "MELON" in st.place:
                    k0 = seen
                elif st.must:
                    k1 = seen + 1
                    break
            for k in range(k0, k1):
                a = pts[k]
                b = pts[k + 1] if k + 1 < len(pts) else None
                add = dist(a, xy) + (dist(xy, b) - dist(a, b) if b is not None else 0)
                if add > left:
                    continue
                if best is None or add < best[0]:
                    best = (add, u, k)
        if best is None:
            continue
        _, u, k = best
        stops = routes[u]
        # position k in the tile sequence -> index in stops (after k tile stops)
        idx, seen = 0, 0
        while idx < len(stops) and seen < k:
            if stops[idx].kind == "T":
                seen += 1
            idx += 1
        stops.insert(idx, Stop("T", xy))
        need = {}
        inv = s.invs[u] if u < len(s.invs) else {}
        if j.wheat and inv.get("WHEAT", 0) < j.wheat:
            need["WHEAT"] = j.wheat
        if j.animal and inv.get(j.animal, 0) < 1:
            need[j.animal] = 1
        if j.fert and inv.get("FERTILIZER", 0) < j.fert:
            need["FERTILIZER"] = j.fert
        if need:
            stops.insert(idx, Stop("S", pick=need))
        mem["owner"][xy] = u
        mem["inserted"][xy] = mem["inserted"].get(xy, 0) + 1


# ------------------------------------------------------------------------------------------------ plan

SLOTS = ((4, 4), (3, 4), (4, 3), (2, 4), (4, 2),
         (5, 4), (5, 3), (5, 2), (6, 4), (6, 3), (7, 4), (6, 2), (8, 4), (8, 3),
         (4, 5), (3, 5), (2, 5), (4, 6), (4, 7),
         (5, 5), (6, 5), (5, 6),
         (1, 3), (2, 3))
MELON_D1 = ((4, 0), (3, 0), (3, 3), (2, 3))
# planned opening: 12 melons within 4 steps of the shed tile (4, 4) so that on day 10 they reach the
# market before the opponent's; the four animals sit on the NE side, next to the later NE animal slots
RING = ((4, 4), (3, 4), (4, 3), (2, 4), (3, 3), (4, 2), (1, 4), (2, 3), (3, 2), (4, 1), (2, 2), (1, 3), (0, 4))


def make_layout_d(animals):
    lay = {}
    for xy, a in zip(((3, 4), (4, 3), (3, 3), (2, 4), (4, 2)), animals):
        lay[xy] = a
    order = sorted(((x, y) for y in range(5) for x in range(5) if (x, y) not in lay),
                   key=lambda q: (abs(q[0] - 4) + abs(q[1] - 4), -q[0]))
    for xy in order[:12]:
        lay[xy] = "MELON"
    for xy in order[12:]:
        lay[xy] = "WHEAT"
    return lay


def make_layout(melons, animals, wheat, later=0):
    """Day-0 targets: the first `melons` ring tiles, animals toward NE, wheat on the far tiles; the next
    `later` ring tiles stay empty for day-1 melons."""
    lay = {}
    for xy in RING[:melons]:
        lay[xy] = "MELON"
    for xy, a in zip(((4, 0), (3, 1), (3, 0), (2, 1), (2, 0)), animals):
        lay[xy] = a
    keep = set(RING[melons:melons + later])
    free = [(x, y) for y in range(5) for x in range(5) if (x, y) not in lay and (x, y) not in keep]
    free.sort(key=lambda q: -((q[0] - 4) ** 2 + (q[1] - 4) ** 2))
    for xy in free[:wheat]:
        lay[xy] = "WHEAT"
    return lay


LAYOUTS = {
    "A": (make_layout(12, ("COW", "SHEEP", "COW", "SHEEP"), 8), {}),
    "B": (make_layout(6, ("COW", "SHEEP", "COW", "SHEEP", "SHEEP"), 10, 4), {xy: "MELON" for xy in RING[6:10]}),
    "C": (make_layout(11, ("COW", "SHEEP", "SHEEP", "SHEEP"), 8), {}),
    "D": (make_layout_d(("SHEEP", "COW", "SHEEP", "COW")), {}),
}
LAYOUT_ID = "A"
LAYOUT0, LAYOUT1 = LAYOUTS[LAYOUT_ID]
HIRE_MIN = {0: 5, 1: 4, 2: 6, 3: 6, 4: 6, 5: 6, 6: 8, 7: 9, 8: 9, 9: 10}
# count(end of day D) = a + b x, x = demand of the product among known shops (alloc.md 3b)
FIT = {
    "STRAWBERRY": ((6, 11.1, 6.1), (9, 10.4, 6.0), (12, 11.0, 8.3), (15, 10.8, 7.9), (18, 6.9, 6.7),
                   (21, -1.3, 6.1), (24, -2.0, 3.5), (27, -2.5, 2.4)),
    "TOMATO": ((6, -0.1, 0.3), (9, 2.7, 1.8), (12, 4.5, 4.9), (15, 5.5, 5.4), (18, 9.8, 6.2),
               (21, 8.7, 4.1), (24, 6.4, 2.1), (27, 5.4, 1.3)),
    "CARROT": ((6, -0.1, 0.2), (9, -0.6, 1.1), (12, -1.2, 3.5), (15, -1.7, 3.5), (18, -1.9, 3.1),
               (21, 0.3, 3.6), (24, 4.9, 3.6), (27, 11.0, 3.0)),
}
PLANT_WINDOW = {"STRAWBERRY": (2, 13), "TOMATO": (9, 18), "CARROT": (10, 26), "WHEAT": (0, 27), "MELON": (0, 1)}


def shop_x(crop, shops):
    if crop == "STRAWBERRY":
        return sum(1 for sh in shops if sh in ("BRUNCH_SPOT", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP", "FARMERS_MARKET"))
    if crop == "TOMATO":
        return sum(1 for sh in shops if sh in ("PIZZA_SHOP", "FARMERS_MARKET"))
    if crop == "CARROT":
        return sum(2 if sh == "PET_CAFE" else 1 if sh == "FARMERS_MARKET" else 0 for sh in shops)
    return 0


def fit_count(crop, day, shops):
    pts = FIT[crop]
    x = shop_x(crop, shops)
    if day <= pts[0][0]:
        d, a, b = pts[0]
        return a + b * x
    for (d0, a0, b0), (d1, a1, b1) in zip(pts, pts[1:]):
        if d0 <= day <= d1:
            w = (day - d0) / float(d1 - d0)
            return (a0 + (a1 - a0) * w) + (b0 + (b1 - b0) * w) * x
    d, a, b = pts[-1]
    return a + b * x


WHEAT_FIT = ((6, 6.5, -0.5), (9, 17.6, 0.7), (12, 23.5, 2.3), (15, 17.2, 1.9), (18, 12.7, 1.9),
             (21, 15.8, 2.1), (24, 19.0, 2.4), (27, 15.7, 1.9))


def wheat_cap(day, shops):
    """DSM's wheat tile count (alloc.md 3b), x = shops that consume wheat; at least 12 from day 6."""
    if day < 6:
        return 12.0
    x = sum(1 for sh in shops if sh in ("BAKERY", "PIZZA_SHOP", "BRUNCH_SPOT", "ICE_CREAM_SHOP", "FARMERS_MARKET"))
    pts = WHEAT_FIT
    val = pts[-1][1] + pts[-1][2] * x
    for (d0, a0, b0), (d1, a1, b1) in zip(pts, pts[1:]):
        if d0 <= day <= d1:
            w = (day - d0) / float(d1 - d0)
            val = (a0 + (a1 - a0) * w) + (b0 + (b1 - b0) * w) * x
            break
    return max(12.0, val)


def animal_targets(s):
    yarn_inc = {3: 8, 6: 7, 9: 7, 12: 4, 15: 2}
    dairy_inc = {3: 4, 6: 4, 9: 2, 12: 1}
    sheep, cow, egg = 3.0, 5.0, 0
    for k, sh in enumerate(s.shops):
        u = 3 * (k + 1)
        if sh == "YARN_STORE":
            sheep += yarn_inc.get(u, 0)
        elif sh in ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"):
            cow += dairy_inc.get(u, 0)
        elif k < 4 and sh in ("BAKERY", "BRUNCH_SPOT"):
            egg += 1
    goose = max(2.0, 8.0 - 0.3 * (cow + sheep) + 0.8 * egg)
    return {"COW": int(round(cow)), "SHEEP": int(round(sheep)), "GOOSE": int(round(goose))}


ANIMAL_BUY_LAST = {"COW": 12, "SHEEP": 18, "GOOSE": 14}


def count_animals(s):
    c = {"COW": 0, "SHEEP": 0, "GOOSE": 0}
    for row in s.tiles:
        for t in row:
            if is_dict(t) and t.get("animal"):
                c[t["animal"]] += 1
    for a in c:
        c[a] += s.shed.get(a, 0) + sum(i.get(a, 0) for i in s.invs)
    return c


def frees_today(t, day, pol):
    """True if the crop on this tile comes off today under our rules."""
    crop = t["crop"]
    c = CROPS[crop]
    age = day - int(t["planted_day"])
    if c["ongoing"]:
        return age > last_prod_age(crop)
    a, _ = one_time_path(crop, age, int(t["yield_units"]), bool(t["watered_today"]),
                         int(t["fertilized_until_day"]), day, pol.fert_ok and crop != "MELON", pol.wheat_age3)
    return a <= age


def assign_targets(s, mem, pol):
    day = s.day
    if day == 0 and OPENING == "plan":
        return dict(LAYOUT0)
    targets = {}
    if day == 1 and OPENING == "plan":
        for xy, crop in LAYOUT1.items():
            if tile_at(s, xy) is None:
                targets[xy] = crop
    slot_set = set()
    # animals
    if day >= 6:
        want = animal_targets(s)
        have = count_animals(s)
        need = []
        waiting = []
        for a in ("COW", "SHEEP", "GOOSE"):
            n_wait = s.shed.get(a, 0) + sum(i.get(a, 0) for i in s.invs)
            waiting += [a] * n_wait
            if day <= ANIMAL_BUY_LAST[a]:
                need += [a] * max(0, want[a] - have[a])
        need = waiting + need
        for xy in SLOTS:
            if not unlocked(s, xy):
                continue
            t = tile_at(s, xy)
            if is_dict(t) and t.get("animal"):
                targets[xy] = t["animal"]
                slot_set.add(xy)
                continue
            if is_dict(t) and t.get("kind") in ("COOP", "PASTURE"):
                pick = next((a for a in need if ANIMALS[a]["struct"] == t["kind"]), None)
                if pick:
                    need.remove(pick)
                    targets[xy] = pick
                    slot_set.add(xy)
                continue
            if not need:
                continue
            if is_dict(t) and t.get("kind") == "PLANT" and CROPS[t["crop"]]["ongoing"]:
                continue          # never cut short a tomato or strawberry
            if is_dict(t) and t.get("kind") == "PLANT" and not frees_today(t, day, pol):
                continue
            targets[xy] = need.pop(0)
            slot_set.add(xy)
    else:
        for xy in SLOTS[:5]:
            t = tile_at(s, xy)
            if is_dict(t) and t.get("animal"):
                targets[xy] = t["animal"]
                slot_set.add(xy)
        if OPENING == "plan":
            for xy, a in LAYOUT0.items():
                t = tile_at(s, xy)
                if a in ANIMALS and (t is None or (is_dict(t) and t.get("kind") == ANIMALS[a]["struct"])):
                    targets[xy] = a
                    slot_set.add(xy)
    # crops
    counts = {c: 0 for c in CROPS}
    free = []
    for y in range(N):
        for x in range(N):
            xy = (x, y)
            if xy in slot_set or not unlocked(s, xy):
                continue
            t = s.tiles[y][x]
            if is_dict(t) and t.get("kind") == "PLANT":
                early = 2 <= day <= 4 and t["crop"] == "WHEAT" and day - int(t["planted_day"]) >= 2 and y < 5 and x < 5
                if early or frees_today(t, day, pol):
                    free.append(xy)
                else:
                    counts[t["crop"]] += 1
                    targets[xy] = t["crop"] if not CROPS[t["crop"]]["ongoing"] else "WHEAT"
            elif is_dict(t) and t.get("animal"):
                continue
            else:
                free.append(xy)
    desired = {}
    for crop in ("STRAWBERRY", "CARROT", "TOMATO"):
        lo, hi = PLANT_WINDOW[crop]
        if lo <= day <= hi:
            desired[crop] = max(fit_count(crop, min(27, day + 3), s.shops), 0.0)
    if 2 <= day <= 5:
        desired["STRAWBERRY"] = 10
    if day <= PLANT_WINDOW["WHEAT"][1] and not 2 <= day <= 5:
        desired["WHEAT"] = wheat_cap(day, s.shops)
    free.sort(key=lambda xy: shed_dist(xy))
    new_carrots = 0
    for xy in free:
        if day <= 1 and xy in MELON_D1 and OPENING != "plan":
            targets[xy] = "MELON"
            continue
        best, gap = None, 0.5
        for crop, want in desired.items():
            if crop == "CARROT" and new_carrots >= CARROT_PER_DAY:
                continue
            g = want - counts[crop]
            if g > gap:
                best, gap = crop, g
        if best is not None:
            targets[xy] = best
            counts[best] += 1
            if best == "CARROT":
                new_carrots += 1
    # opening: day-0 wheat on NW comes off at age 2-3 for strawberries
    if 2 <= day <= 4:
        for y in range(5):
            for x in range(5):
                t = s.tiles[y][x]
                if is_dict(t) and t.get("kind") == "PLANT" and t["crop"] == "WHEAT" \
                        and day - int(t["planted_day"]) >= 2 and targets.get((x, y)) == "STRAWBERRY":
                    pol.early_harvest.add((x, y))
    return targets


def plant_needs(s, pol, jobs):
    """Seeds wanted for today's plantings (empty target tiles and crops coming off today)."""
    need = {}
    for xy, j in jobs.items():
        if j.seed:
            need[j.seed] = need.get(j.seed, 0) + 1
    return need


def workload(jobs):
    return sum(j.dur() + 1.7 for j in jobs.values())


def hire_target(s, jobs):
    day = s.day
    units = int(math.ceil((workload(jobs) + 6) / 20.0))
    lo = HIRE_MIN.get(day, 11 if day <= 27 else 9)
    if day == 0:
        return lo
    return max(0, min(12, max(lo, units - 1)))


def new_day(s, mem):
    mem["day"] = s.day
    pol = Policy(s.day)
    pol.prices = dict(s.prices)
    pol.fert_ok = s.day >= 10
    pol.fert_value = max(8.0, s.prices.get("FERTILIZER", 100) * 0.9)
    pol.targets = assign_targets(s, mem, pol)
    # spread the wheat waves: at most WHEAT_A3_QUOTA age-3 harvests a day, the rest wait for age 4
    a3 = []
    for y in range(N):
        for x in range(N):
            t = s.tiles[y][x]
            if is_dict(t) and t.get("kind") == "PLANT" and t["crop"] == "WHEAT" and s.day - int(t["planted_day"]) == 3                     and int(t["fertilized_until_day"]) >= s.day:
                a3.append((x, y))
    a3.sort(key=shed_dist)
    pol.wheat_a3 = set(a3[:WHEAT_A3_QUOTA])
    mem["pol"] = pol
    mem["routes"] = {}
    mem["owner"] = {}
    mem["started"] = {}
    mem["inserted"] = {}
    mem["planned_units"] = 0
    jobs = build_jobs(s, pol)
    mem["hire_target"] = hire_target(s, jobs)


def add_deliveries(stops, jobs, s):
    """Shed stops that bring goods back mid-day so they can be sold: fertilizer (cash) on days 1-9,
    milk and wool from the morning milking, melons, and everything on day 29."""
    day = s.day
    if day >= 29:
        stops.append(Stop("S", place={k: -1 for k in PRODUCTS}))
        return stops
    last_animal, last_melon = -1, -1
    for k, st in enumerate(stops):
        if st.kind != "T":
            continue
        t = s.tiles[st.xy[1]][st.xy[0]]
        if is_dict(t) and t.get("animal"):
            j = jobs.get(st.xy)
            if j is not None and any(o[0] in ("HARVEST", "COLLECT_FERTILIZER") for o in j.ops):
                last_animal = k
        elif is_dict(t) and t.get("kind") == "PLANT" and t["crop"] == "MELON":
            j = jobs.get(st.xy)
            if j is not None and any(o[0] == "HARVEST" for o in j.ops):
                last_melon = k
    ins = []
    if last_animal >= 0:
        place = {"MILK": -1, "WOOL": -1}
        if day < 10:
            place["FERTILIZER"] = -1
        ins.append((last_animal + 1, place))
    if last_melon >= 0:
        ins.append((last_melon + 1, {"MELON": -1}))
    for pos, place in sorted(ins, key=lambda p: -p[0]):
        stops.insert(pos, Stop("S", place=place))
    return stops


def spawn_tiles(positions, k):
    """Where the next k hires will appear: least occupied shed tile, NWSE order (engine 533-541)."""
    occ = {t: 0 for t in SHED}
    for p in positions:
        if p in occ:
            occ[p] += 1
    out = []
    for _ in range(k):
        t = min(SHED, key=lambda q: (occ[q], SHED.index(q)))
        occ[t] += 1
        out.append(t)
    return out


def ready_copy(s, j, wheat_left):
    """The job without the ops whose supplies are missing now (and the ops chained after them)."""
    nj = Job(j.xy, j.kind)
    blocked = False
    for op, arg, pr in j.ops:
        if blocked:
            break
        if op == "PLANT" and s.seeds.get(arg, 0) <= 0:
            blocked = True
            continue
        if op == "PLACE" and s.shed.get(arg, 0) + sum(i.get(arg, 0) for i in s.invs) <= 0:
            blocked = True
            continue
        if op in ("FEED", "CARE") and wheat_left <= 0:
            continue
        nj.add(op, arg, pr)
    return nj if nj.ops else None


def melon_rush(s, units, work):
    """Ripe melons first, one trip each, each to the unit that brings it to the shed earliest: the first
    melons sold on day 10 fetch the best prices, before the opponent's reach the market."""
    mel = sorted((xy for xy, j in work.items() if j.kind == "melon"), key=shed_dist)
    out = {}
    if not mel:
        return out
    n = len(s.units)
    st = {u["idx"]: [u["pos"], 0 if u["idx"] < n else 1] for u in units}
    t0 = {i: v[1] for i, v in st.items()}
    for xy in mel:
        i = min(st, key=lambda k: (st[k][1] + dist(st[k][0], xy), k))
        p, t = st[i]
        t += dist(p, xy) + work[xy].dur() + shed_dist(xy) + 1
        st[i] = [nearest_shed(xy), t]
        out.setdefault(i, []).append(xy)
    for u in units:
        if u["idx"] in out:
            u["pos"] = st[u["idx"]][0]
            u["cap"] = max(0, u["cap"] - (st[u["idx"]][1] - t0[u["idx"]]))
    return out


def plan_all(s, mem, pol, jobs, idxs, extra=0):
    end = 21 if s.day >= 29 else 23
    units = []
    for u in idxs:
        cap = end - s.hour + 1
        units.append(dict(idx=u, pos=s.units[u], cap=cap, inv=s.invs[u] if u < len(s.invs) else {}))
    n = len(s.units)
    for k, p in enumerate(spawn_tiles(s.units, extra)):
        units.append(dict(idx=n + k, pos=p, cap=end - s.hour, inv={}))
    wheat_left = s.shed.get("WHEAT", 0) + sum(i.get("WHEAT", 0) for i in s.invs)
    work = {}
    for xy, j in jobs.items():
        nj = ready_copy(s, j, wheat_left)
        if nj is not None:
            work[xy] = nj
    capacity = sum(max(0, u["cap"] - 2) for u in units) * 0.95
    load0 = workload(work)
    work, allowed = trim_jobs(work, capacity)
    mem["max_prio"] = allowed
    if DEBUG and s.hour == 1:
        ops = {}
        for j in jobs.values():
            for op, arg, pr in j.ops:
                ops[op] = ops.get(op, 0) + 1
        print(f"[plan d{s.day}] units {len(units)} jobs {len(jobs)} load {load0:.0f} cap {capacity:.0f} allowed {allowed} ops {ops}")
    rush = melon_rush(s, units, work) if s.day >= 10 else {}
    for lst in rush.values():
        for xy in lst:
            del work[xy]
    seqs = petal_plan(units, work)
    shed_avail = dict(s.shed)
    mem["routes"] = {}
    mem["owner"] = {}

    def crit(u):
        return -sum(1 for xy in seqs[u["idx"]] if work[xy].prio == P_CRIT and work[xy].wheat)

    for u in sorted(units, key=crit):
        stops = make_stops(u, seqs[u["idx"]], work, shed_avail)
        stops = add_deliveries(stops, work, s)
        pre = []
        for xy in rush.get(u["idx"], []):
            pre += [Stop("T", xy), Stop("S", place={"MELON": -1})]
            mem["owner"][xy] = u["idx"]
        mem["routes"][u["idx"]] = pre + stops
        for xy in seqs[u["idx"]]:
            mem["owner"][xy] = u["idx"]
    mem["planned_units"] = len(s.units) + extra
    mem["plan_step"] = s.step


# ------------------------------------------------------------------------------------------------ market

LAND_DAY = (6, 9, 10)
WHEAT_A3_QUOTA = 10
CARROT_PER_DAY = 6


def projected_stock(s, ctx):
    st = dict(s.shed)
    for k, v in ctx.picked.items():
        st[k] = st.get(k, 0) - v
    for k, v in ctx.placed.items():
        st[k] = st.get(k, 0) + v
    return {k: v for k, v in st.items() if v > 0}


def carried_after(s, ctx):
    tot = {}
    for inv in s.invs:
        for k, v in inv.items():
            tot[k] = tot.get(k, 0) + v
    for k, v in ctx.picked.items():
        tot[k] = tot.get(k, 0) + v
    for k, v in ctx.placed.items():
        tot[k] = tot.get(k, 0) - v
    return tot


def feeds_tomorrow(s, pol):
    n = 0
    for row in s.tiles:
        for t in row:
            if is_dict(t) and t.get("animal"):
                last = animal_last_night(t["animal"], int(t["placed_day"]), pol.last_feed_day)
                if last is not None and s.day + 1 <= last and s.day + 1 < 29:
                    n += 1
    return n


def ticks_left(step):
    return sum(1 for t in range(step, (step // TPD) * TPD + TPD) if t % 4 == 1) or 1


def sell_orders(s, mem, pol, ctx, jobs):
    h, step, day = s.hour, s.step, s.day
    m4 = step % 4
    stock = projected_stock(s, ctx)
    total = sum(stock.values())
    carried = carried_after(s, ctx)
    last = step >= LAST_STEP
    out = {}
    feeds_left = sum(j.wheat for j in jobs.values())
    ftm = None
    for item, S in stock.items():
        if item not in BASE:
            continue
        p = s.prices.get(item, BASE[item])
        if p <= 1 and not last:
            continue
        fresh = ctx.placed.get(item, 0)
        q = 0
        if last or (day >= 29 and h >= 20):
            q = S
        elif item == "MELON":
            q = S
        elif item in ("EGG", "TOMATO", "CARROT"):
            if h >= 22 or total >= 85:
                q = S
        elif item == "WHEAT":
            if h >= 22:
                if ftm is None:
                    ftm = feeds_tomorrow(s, pol)
                q = S - max(0, ftm + 2 - carried.get("WHEAT", 0))
                if h == 23 and sum(v for k, v in carried.items() if v > 0) + total > 90:
                    q = S - max(0, min(ftm, 10) - carried.get("WHEAT", 0))
            elif h <= 2:
                q = S - max(0, feeds_left + 2 - carried.get("WHEAT", 0))
        elif item in ("STRAWBERRY", "MILK", "WOOL"):
            if item == "MILK" and p < 0.24 * BASE["MILK"]:
                q = 0
            elif fresh:
                q = min(fresh, 6) if item == "STRAWBERRY" else fresh
            elif m4 == 1 and h >= 1:
                q = min(S, max(2, int(math.ceil(S / float(ticks_left(step))))))
        elif item == "FERTILIZER":
            if day < 10:
                q = S
            else:
                keep = 0 if day >= 28 else mem.get("fert_keep", 20)
                if (h in (0, 2, 3, 7) and p >= 40) or h >= 22:
                    q = S - keep
        q = min(max(0, int(q)), S)
        if q > 0:
            out[item] = q
    # the day-end drop must fit: shed after sales + goods carried <= 100
    if h >= 22 and not last:
        after = sum(stock.values()) - sum(out.values())
        over = after + sum(v for v in carried.values() if v > 0) - 100
        if over > 0:
            if ftm is None:
                ftm = feeds_tomorrow(s, pol)
            for item in sorted(stock, key=lambda k: s.prices.get(k, 0)):
                if over <= 0:
                    break
                if item not in BASE:
                    continue
                spare = stock[item] - out.get(item, 0)
                if item == "WHEAT":
                    spare = max(0, spare - max(0, ftm - carried.get("WHEAT", 0)))
                k = min(spare, over)
                if k > 0 and s.prices.get(item, 0) > 1:
                    out[item] = out.get(item, 0) + k
                    over -= k
    orders = sorted(out.items(), key=lambda kv: (kv[0] == "FERTILIZER", -kv[1] * s.prices.get(kv[0], 0)))
    return [["SELL", k, v] for k, v in orders]


def buy_orders(s, mem, pol, ctx, jobs, cash, room):
    h, day = s.hour, s.day
    pending = set()
    wheat_have = s.shed.get("WHEAT", 0) + sum(i.get("WHEAT", 0) for i in s.invs)
    if h >= 20:
        need_w = feeds_tomorrow(s, pol) - wheat_have
    else:
        need_w = sum(j.wheat for j in jobs.values()) - wheat_have
        if h >= 2:
            unowned = sum(j.wheat for xy, j in jobs.items() if xy not in mem["owner"])
            need_w = max(need_w, unowned - s.shed.get("WHEAT", 0))
    wheat_order = None
    if need_w > 0 and day < 29:
        wp = s.prices.get("WHEAT", 25) + 2
        k = int(min(need_w + 1, cash // wp, room))
        if k > 0:
            wheat_order = ["BUY_PRODUCT", "WHEAT", k]
            cash -= k * wp
            room -= k
            pending.add("WHEAT")
    if day == 1 and h >= 1:
        k = plant_needs(s, pol, jobs).get("MELON", 0) - s.seeds.get("MELON", 0)
        k = int(min(k, cash // CROPS["MELON"]["seed"]))
        if k > 0:
            mem.setdefault("early_seeds", []).append(["BUY_SEED", "MELON", k])
            cash -= k * CROPS["MELON"]["seed"]
    hires = []
    if h <= 1 or (day < 10 and h <= 3):
        want = mem.get("hire_target", 0) - s.hires_today
        k = 0
        while want > 0:
            c = fib(s.hires_today + k)
            if cash < c:
                break
            hires.append(["HIRE"])
            cash -= c
            k += 1
            want -= 1
    reserve = 0 if day >= 10 else 20
    if h == 0:
        k0 = len(hires)
        for k in range(k0, max(k0, mem.get("hire_target", 0))):
            reserve += fib(s.hires_today + k)
    land = []
    nq = len(s.quads)
    if nq < 4 and LAND_DAY[nq - 1] <= day <= 14:
        price = LAND_PRICE[nq - 1]
        if cash >= price + reserve:
            land.append(["BUY_LAND"])
            cash -= price
    animals = []
    if day < 29:
        need_a = {}
        for xy, tgt in pol.targets.items():
            if tgt in ANIMALS:
                t = tile_at(s, xy)
                built = is_dict(t) and t.get("kind") == ANIMALS[tgt]["struct"] and not t.get("animal")
                if built or (day == 0 and t is None):
                    need_a[tgt] = need_a.get(tgt, 0) + 1
        for a, n in need_a.items():
            have = s.shed.get(a, 0) + sum(i.get(a, 0) for i in s.invs)
            k = n - have
            q = 0
            while k > 0 and cash - ANIMALS[a]["cost"] >= reserve and room > 0:
                q += 1
                cash -= ANIMALS[a]["cost"]
                room -= 1
                k -= 1
            if q:
                animals.append(["BUY_ANIMAL", a, q])
                pending.add(a)
    seeds = list(mem.pop("early_seeds", []))
    if day < 29:
        need = plant_needs(s, pol, jobs)
        for crop in ("MELON", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT"):
            k = need.get(crop, 0) - s.seeds.get(crop, 0) - sum(o[2] for o in seeds if o[1] == crop)
            if k <= 0:
                continue
            cost = CROPS[crop]["seed"]
            k = int(min(k, (cash - reserve) // cost))
            if k > 0:
                seeds.append(["BUY_SEED", crop, k])
                cash -= k * cost
    mem["pending_buys"] = pending
    return hires, land, animals, seeds, wheat_order


def market_orders(s, mem, pol, ctx, jobs):
    sells = sell_orders(s, mem, pol, ctx, jobs)
    proceeds = sum(q * s.prices.get(item, 0) * 0.85 for _, item, q in sells)
    stock = projected_stock(s, ctx)
    room = 100 - (sum(stock.values()) - sum(q for _, _, q in sells))
    hires, land, animals, seeds, wheat = buy_orders(s, mem, pol, ctx, jobs, s.money + proceeds, room)
    if s.hour == 0:
        sells = sells[:1 if wheat else 2]
        hires = hires[:8]
    out = sells + hires + land + animals + seeds
    if wheat:
        out.append(wheat)
    return out[:10]


# ------------------------------------------------------------------------------------------------ day 0

DAY0_TAPE = [
    {"farmer":["PASS"],"hands":[],"market":[["BUY_ANIMAL","COW",1],["BUY_PRODUCT","WHEAT",5]]},
    {"farmer":["PICKUP","COW",1],"hands":[],"market":[["SELL","WHEAT",1],["HIRE"],["HIRE"],["HIRE"],["HIRE"],["BUY_ANIMAL","COW",1],["BUY_ANIMAL","SHEEP",3]]},
    {"farmer":["BUILD_PASTURE"],"hands":[["PICKUP","SHEEP",1],["PICKUP","SHEEP",1],["PICKUP","COW",1],["PICKUP","SHEEP",1]],"market":[["SELL","WHEAT",1]]},
    {"farmer":["PLACE","COW",1],"hands":[["NORTH"],["NORTH"],["NORTH"],["WEST"]],"market":[["SELL","WHEAT",1],["BUY_PRODUCT","WHEAT",1]]},
    {"farmer":["PICKUP","WHEAT",3],"hands":[["WEST"],["WEST"],["NORTH"],["BUILD_PASTURE"]],"market":[["SELL","WHEAT",1],["BUY_PRODUCT","WHEAT",1]]},
    {"farmer":["FEED"],"hands":[["BUILD_PASTURE"],["WEST"],["NORTH"],["PLACE","SHEEP",1]],"market":[["SELL","WHEAT",1],["BUY_PRODUCT","WHEAT",1]]},
    {"farmer":["WEST"],"hands":[["PLACE","SHEEP",1],["BUILD_PASTURE"],["PASS"],["CARE"]],"market":[["BUY_SEED","MELON",2],["BUY_PRODUCT","WHEAT",1]]},
    {"farmer":["FEED"],"hands":[["CARE"],["PLACE","SHEEP",1],["WEST"],["WEST"]],"market":[]},
    {"farmer":["WEST"],"hands":[["SOUTH"],["WEST"],["BUILD_PASTURE"],["WEST"]],"market":[["BUY_SEED","MELON",2]]},
    {"farmer":["FEED"],"hands":[["PICKUP","WHEAT",1],["NORTH"],["PLACE","COW",1],["NORTH"]],"market":[]},
    {"farmer":["CARE"],"hands":[["CARE"],["PLANT","MELON"],["NORTH"],["PASS"]],"market":[]},
    {"farmer":["WEST"],"hands":[["NORTH"],["WATER"],["PLANT","MELON"],["NORTH"]],"market":[["BUY_SEED","MELON",2]]},
    {"farmer":["PLANT","MELON"],"hands":[["FEED"],["NORTH"],["WATER"],["NORTH"]],"market":[["BUY_SEED","WHEAT",2]]},
    {"farmer":["WATER"],"hands":[["NORTH"],["PLANT","MELON"],["WEST"],["PLANT","WHEAT"]],"market":[["SELL","WHEAT",1],["BUY_SEED","WHEAT",2]]},
    {"farmer":["PASS"],"hands":[["WEST"],["WATER"],["PLANT","MELON"],["WATER"]],"market":[["BUY_SEED","WHEAT",1]]},
    {"farmer":["PASS"],"hands":[["PLANT","MELON"],["NORTH"],["WATER"],["NORTH"]],"market":[["BUY_SEED","WHEAT",1]]},
    {"farmer":["PASS"],"hands":[["WATER"],["WEST"],["WEST"],["PLANT","WHEAT"]],"market":[["BUY_SEED","WHEAT",1]]},
    {"farmer":["PASS"],"hands":[["WEST"],["PLANT","WHEAT"],["PLANT","WHEAT"],["WATER"]],"market":[["BUY_SEED","WHEAT",1]]},
    {"farmer":["PASS"],"hands":[["PLANT","WHEAT"],["WATER"],["WATER"],["WEST"]],"market":[["BUY_SEED","WHEAT",1]]},
    {"farmer":["WEST"],"hands":[["WATER"],["SOUTH"],["NORTH"],["PLANT","WHEAT"]],"market":[["BUY_SEED","WHEAT",1]]},
    {"farmer":["PLANT","WHEAT"],"hands":[["WEST"],["PLANT","WHEAT"],["PLANT","WHEAT"],["WATER"]],"market":[["BUY_SEED","WHEAT",1]]},
    {"farmer":["WATER"],"hands":[["SOUTH"],["WATER"],["WATER"],["PASS"]],"market":[["BUY_SEED","WHEAT",1]]},
    {"farmer":["SOUTH"],"hands":[["WEST"],["SOUTH"],["SOUTH"],["SOUTH"]],"market":[]},
    {"farmer":["SOUTH"],"hands":[["SOUTH"],["SOUTH"],["SOUTH"],["SOUTH"]],"market":[]},
]


# cha22's day 0 (identical in every game): 12 melons, 2 cows, 2 sheep, 8 wheat
DAY0_TAPE_C = [
    {"farmer":["PASS"],"hands":[],"market":[["BUY_PRODUCT","WHEAT",5],["BUY_SEED","WHEAT",1]]},
    {"farmer":["NORTH"],"hands":[],"market":[["HIRE"],["HIRE"],["HIRE"],["HIRE"],["HIRE"],["BUY_ANIMAL","COW",2],["BUY_ANIMAL","SHEEP",2]]},
    {"farmer":["SOUTH"],"hands":[["PICKUP","COW"],["WEST"],["NORTH"],["NORTH"],["PICKUP","COW"]],"market":[]},
    {"farmer":["PICKUP","SHEEP"],"hands":[["NORTH"],["WEST"],["NORTH"],["NORTH"],["BUILD_PASTURE"]],"market":[]},
    {"farmer":["PICKUP","WHEAT"],"hands":[["BUILD_PASTURE"],["WEST"],["NORTH"],["NORTH"],["PLACE","COW"]],"market":[]},
    {"farmer":["NORTH"],"hands":[["PLACE","COW"],["PLANT","WHEAT"],["NORTH"],["WEST"],["CARE"]],"market":[]},
    {"farmer":["WEST"],"hands":[["NORTH"],["WATER"],["NORTH"],["WEST"],["PICKUP","SHEEP"]],"market":[["BUY_SEED","MELON",2]]},
    {"farmer":["BUILD_PASTURE"],"hands":[["NORTH"],["PASS"],["PLANT","MELON"],["PLANT","MELON"],["PICKUP","WHEAT"]],"market":[["BUY_SEED","MELON",1]]},
    {"farmer":["PLACE","SHEEP"],"hands":[["PLANT","MELON"],["PASS"],["WATER"],["WATER"],["WEST"]],"market":[]},
    {"farmer":["FEED"],"hands":[["WATER"],["PASS"],["WEST"],["NORTH"],["BUILD_PASTURE"]],"market":[["BUY_SEED","MELON",1]]},
    {"farmer":["CARE"],"hands":[["WEST"],["PASS"],["PLANT","MELON"],["WEST"],["PLACE","SHEEP"]],"market":[["BUY_SEED","MELON",2]]},
    {"farmer":["WEST"],"hands":[["PLANT","MELON"],["PASS"],["WATER"],["PLANT","MELON"],["FEED"]],"market":[["BUY_SEED","MELON",1]]},
    {"farmer":["PLANT","MELON"],"hands":[["WATER"],["PASS"],["WEST"],["WATER"],["CARE"]],"market":[["BUY_SEED","WHEAT",1]]},
    {"farmer":["WATER"],"hands":[["SOUTH"],["PASS"],["PLANT","WHEAT"],["WEST"],["WEST"]],"market":[["BUY_SEED","WHEAT",1]]},
    {"farmer":["WEST"],"hands":[["WEST"],["PASS"],["WATER"],["PLANT","WHEAT"],["WEST"]],"market":[["BUY_SEED","MELON",3]]},
    {"farmer":["PLANT","MELON"],"hands":[["PLANT","MELON"],["PASS"],["WEST"],["WATER"],["PLANT","MELON"]],"market":[["BUY_SEED","WHEAT",1]]},
    {"farmer":["WATER"],"hands":[["WATER"],["PASS"],["PLANT","WHEAT"],["WEST"],["WATER"]],"market":[["BUY_SEED","WHEAT",1]]},
    {"farmer":["PASS"],"hands":[["WEST"],["PASS"],["WATER"],["PLANT","WHEAT"],["WEST"]],"market":[["BUY_SEED","MELON",2]]},
    {"farmer":["PASS"],"hands":[["PLANT","MELON"],["PASS"],["PASS"],["WATER"],["PLANT","MELON"]],"market":[]},
    {"farmer":["PASS"],"hands":[["WATER"],["PASS"],["PASS"],["NORTH"],["WATER"]],"market":[["BUY_SEED","WHEAT",1]]},
    {"farmer":["PASS"],"hands":[["WEST"],["PASS"],["PASS"],["PLANT","WHEAT"],["NORTH"]],"market":[["BUY_SEED","WHEAT",2]]},
    {"farmer":["PASS"],"hands":[["PLANT","WHEAT"],["PASS"],["PASS"],["WATER"],["PLANT","WHEAT"]],"market":[]},
    {"farmer":["PASS"],"hands":[["WATER"],["PASS"],["PASS"],["PASS"],["WATER"]],"market":[]},
    {"farmer":["PASS"],"hands":[["PASS"],["PASS"],["PASS"],["PASS"],["PASS"]],"market":[]},
]
OPENING = "plan"


def tape_step(s, mem):
    a = (DAY0_TAPE_C if OPENING == "cha22" else DAY0_TAPE)[s.step]
    nh = len(s.units) - 1
    units = [list(a["farmer"])] + [list(x) for x in a["hands"]]
    if nh != len(a["hands"]):
        mem["tape_ok"] = False
        return None
    used = {}
    for i, act in enumerate(units):
        if act and act[0] == "PLANT":
            crop = act[1]
            if used.get(crop, 0) + 1 > s.seeds.get(crop, 0):
                units[i] = ["PASS"]
            else:
                used[crop] = used.get(crop, 0) + 1
    return {"farmer": units[0], "hands": units[1:], "market": [list(o) for o in a["market"]]}


# ------------------------------------------------------------------------------------------------ agent

MEM = {}


def new_mem():
    return {"step": -1, "day": -1, "tape_ok": True, "routes": {}, "owner": {}, "started": {},
            "planned_units": 0, "pending_buys": set(), "hire_target": 0}


def _agent(obs):
    s = parse(obs)
    mem = MEM.get(s.me)
    if mem is None or s.step == 0 or mem["step"] >= s.step:
        mem = MEM[s.me] = new_mem()
    mem["step"] = s.step
    if s.day == 0 and mem["tape_ok"] and OPENING != "plan":
        out = tape_step(s, mem)
        if out is not None:
            return out
    if mem["day"] != s.day:
        new_day(s, mem)
    pol = mem["pol"]
    pol.prices = dict(s.prices)
    if mem.get("nq", len(s.quads)) != len(s.quads):
        pol.targets = assign_targets(s, mem, pol)
    mem["nq"] = len(s.quads)
    jobs = build_jobs(s, pol)
    mem["jobs"] = jobs
    n = len(s.units)
    if s.hour == 0:
        mem["max_prio"] = 99
    elif s.hour == 1 or (s.hour == 2 and abs(n - mem["planned_units"]) >= 3) or mem.get("plan_step", -1) < 0:
        extra = 0
        if s.hour == 1:
            extra = max(0, mem.get("hire_target", 0) - s.hires_today)
            cash = s.money
            k = 0
            while k < extra and cash >= fib(s.hires_today + k):
                cash -= fib(s.hires_today + k)
                k += 1
            extra = k
        plan_all(s, mem, pol, jobs, list(range(n)), extra)
    else:
        insert_new_jobs(s, mem, pol, jobs, n)
    for u in [u for u in mem["routes"] if u >= n]:
        if s.hour >= 2 or s.hour == 0:
            for st in mem["routes"].pop(u):
                if st.kind == "T" and mem["owner"].get(st.xy) == u:
                    del mem["owner"][st.xy]
    for xy in [xy for xy, u in mem["owner"].items() if u >= n and s.hour >= 2]:
        del mem["owner"][xy]
    if s.hour >= 2:
        rebalance_routes(s, mem, jobs)
    plan_unloads(s, mem, pol)
    ctx = Ctx(s)
    acts = []
    for u in range(n):
        a = unit_act(s, mem, pol, u, ctx)
        if a is None and s.hour >= 14 and sum(v for k, v in s.invs[u].items() if k in SELLABLE) >= 3:
            mem["routes"][u] = [Stop("S", place={k: -1 for k in SELLABLE})]
            a = unit_act(s, mem, pol, u, ctx)
        if a is None and idle_act(s, mem, pol, u, ctx, jobs):
            a = unit_act(s, mem, pol, u, ctx)
        acts.append(a or ["PASS"])
    market = market_orders(s, mem, pol, ctx, jobs)
    if DEBUG and s.hour == 23 and s.day in (14, 16, 18):
        for y in range(N):
            for x in range(N):
                t = s.tiles[y][x]
                if is_dict(t) and t.get("animal") and not t.get("fed_today"):
                    j = jobs.get((x, y))
                    own = mem["owner"].get((x, y))
                    print(f"[unfed d{s.day}] {(x, y)} {t['animal']} age {s.day - t['placed_day']} cuf {t['consecutive_unfed']} "
                          f"job {[o[0] + str(o[2]) for o in j.ops] if j else None} owner {own} "
                          f"route {[(st.kind, st.xy) for st in mem['routes'].get(own, [])][:4] if own is not None else None}")
        wh = sum(i.get("WHEAT", 0) for i in s.invs)
        print(f"[unfed d{s.day}] shed wheat {s.shed.get('WHEAT', 0)} carried wheat {wh} pickups {mem.get('dbg_pick')}")
    if DEBUG and 12 <= s.day <= 20:
        pc = mem.setdefault("dbg_pickups", {})
        for u, a in enumerate(acts):
            if a and a[0] == "PICKUP":
                key = (a[1], "start" if s.hour <= 2 else "mid")
                pc[key] = pc.get(key, 0) + 1
        if s.day == 20 and s.hour == 23:
            print(f"[pickups d12-20] {sorted(pc.items())}")
    if DEBUG and s.day == -14 and s.hour >= 2:
        unowned = sum(j.wheat for xy, j in jobs.items() if xy not in mem["owner"])
        print(f"[wheat d14 h{s.hour}] money {s.money:.0f} shed_w {s.shed.get('WHEAT', 0)} carried_w {sum(i.get('WHEAT', 0) for i in s.invs)} "
              f"unowned_feeds {unowned} feeds_left {sum(j.wheat for j in jobs.values())} shed_total {sum(s.shed.values())} market {market}")
    if DEBUG and s.day == 1:
        need = plant_needs(s, pol, jobs)
        print(f"[d1 h{s.hour}] money {s.money:.0f} shed {s.shed} seeds {s.seeds} need {need} units {len(s.units)} acts {acts} market {market}")
    if DEBUG and s.hour in (0, 1, 2) and s.day in (99,):
        print(f"[mkt d{s.day} h{s.hour}] money {s.money:.0f} hires_today {s.hires_today} target {mem.get('hire_target')} units {len(s.units)} market {market}")
    if DEBUG and s.hour == 23 and 12 <= s.day <= 27:
        car = {}
        for inv in s.invs:
            for k, v in inv.items():
                car[k] = car.get(k, 0) + v
        print(f"[carry d{s.day} h{s.hour}] shed {sum(s.shed.values())} {dict(sorted(s.shed.items()))} carried {sum(car.values())} {dict(sorted(car.items()))} sells {market}")
    if DEBUG and s.hour == 23 and s.day in (-1,):
        crit = [(xy, j) for xy, j in jobs.items() if any(o[2] == P_CRIT and o[0] == "WATER" for o in j.ops)]
        for xy, j in crit:
            own = mem["owner"].get(xy)
            where = None
            if own is not None:
                for k, st in enumerate(mem["routes"].get(own, [])):
                    if st.kind == "T" and st.xy == xy:
                        where = k
            t = s.tiles[xy[1]][xy[0]]
            print(f"[miss d{s.day}] {xy} {t.get('crop')} age {s.day - t.get('planted_day', 0)} ops {[o[0] for o in j.ops]} owner {own} pos_in_route {where} "
                  f"route_len {len(mem['routes'].get(own, [])) if own is not None else None} unit_at {s.units[own] if own is not None and own < len(s.units) else None}")
        print(f"[h23 d{s.day}] routes left " + " ".join(f"{u}:{len(r)}" for u, r in sorted(mem['routes'].items()) if r))
    return {"farmer": acts[0], "hands": acts[1:], "market": market}


def agent(obs, config=None):
    if DEBUG:
        return _agent(obs)
    try:
        return _agent(obs)
    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}
