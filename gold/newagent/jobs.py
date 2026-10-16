"""Daily maintenance jobs for the new gold agent (tile rules derived from the engine; DSM's habits as defaults).

day_jobs(tiles, day, ctx) -> list of (xy, ops, prio, value) for the tiles that already hold a crop or an animal.
Planting, building and placing come from the policy layer, not from here.

Crop ages a = day - planted_day. Engine facts used:
- one-shot crops (WHEAT, CARROT, MELON) start with yield 1; WATER on ages ws..max_yield_day (ws = (m+1)//2) adds
  +1, or +2 while fertilized (FERTILIZE covers day..day+2); after max_yield_day the yield decays, so harvest by then.
- ongoing crops (TOMATO, STRAWBERRY) produce at the end of ages first-1, first-1+interval, ... (4 times); a
  production adds +2 if watered that day and fertilized, else +1; held yield caps at 4.
- a plant dies at the end of a day that makes 2 unwatered days in a row (the planting day counts as unwatered).
- animals produce at the end of ages first-1 + k*interval: +1, plus the banked care if fed that day; care banks
  only on days with both FEED and CARE; 2 unfed days in a row = escape; fertilizer can be collected every day.
"""
CROPS = {
    "WHEAT": (2, 4, 0, 6, False),        # first_yield_day, max_yield_day, interval, max_yield, ongoing
    "CARROT": (2, 3, 0, 4, False),
    "TOMATO": (8, 8, 1, 4, True),
    "STRAWBERRY": (10, 10, 2, 4, True),
    "MELON": (10, 12, 0, 6, False),
}
ANIMALS = {"GOOSE": (4, 1, 4, "EGG"), "COW": (8, 2, 6, "MILK"), "SHEEP": (6, 3, 6, "WOOL")}
BASE = {"WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120, "MELON": 250, "EGG": 50, "MILK": 150,
        "WOOL": 200, "FERTILIZER": 60}

# priorities (lower = earlier / never dropped)
P_SAVE = 0      # the plant dies or the animal escapes tonight otherwise
P_TODAY = 1     # product lost to a cap or decay if not done today
P_YIELD = 2     # adds yield (window watering, fertilizer, production-day feed)
P_HARV = 3      # harvest that could wait
P_LOW = 4       # collect fertilizer, optional feed on a non-production day


def crop_prod_tonight(crop, age):
    f, m, iv, my, ong = CROPS[crop]
    if not ong:
        return False
    k = age + 1 - f
    return k >= 0 and k % iv == 0 and k // iv + 1 <= my


def crop_last_prod_age(crop):
    f, m, iv, my, ong = CROPS[crop]
    return f - 1 + iv * (my - 1)


def animal_prod_tonight(animal, age):
    f, iv, mh, prod = ANIMALS[animal]
    k = age + 1 - f
    return k >= 0 and k % iv == 0


def crop_ops(t, day, ctx):
    """Ops for one crop tile today, in execution order. -> (ops, prio, value) or None."""
    crop = t["crop"]
    a = day - t["planted_day"]
    f, m, iv, my, ong = CROPS[crop]
    unw = t.get("consecutive_unwatered", 0)        # 1 = not watered yesterday (or planted yesterday unwatered)
    must_water = unw >= 1
    fert_until = t.get("fertilized_until_day", -1)
    y = t.get("yield_units", 0)
    price = ctx.get("price", {}).get(crop, BASE[crop])
    use_fert = ctx.get("use_fert", True)
    ops = []
    prio = P_SAVE if must_water else 9
    value = 0.0
    if not ong:
        ws = (m + 1) // 2
        in_window = ws <= a <= m
        harvest_now = False
        fert_now = False
        if crop == "WHEAT":
            if a == 2 and fert_until < day and use_fert:
                fert_now = True
            harvest_now = a >= 4 or (a == 3 and (fert_until >= day or fert_now))
        elif crop == "CARROT":
            if a == 2 and fert_until < day and use_fert:
                fert_now = True
            harvest_now = a >= 3
        else:  # MELON
            harvest_now = a >= 10
        if fert_now:
            ops.append(["FERTILIZE", None])
            value += price * 1.0
            prio = min(prio, P_YIELD)
        if in_window and y < my:
            ops.append(["WATER", None])
            value += price * (2 if (fert_until >= day or fert_now) else 1)
            prio = min(prio, P_YIELD)
        elif must_water and not harvest_now:
            ops.append(["WATER", None])
        if harvest_now:
            ops.append(["HARVEST", None])
            est = min(my, y + (2 if (fert_until >= day or fert_now) else 1) * (1 if (in_window and y < my) else 0))
            value += price * 0.2 * est
            prio = min(prio, P_TODAY if a >= m else P_HARV)
        elif crop == "MELON" and not in_window and a % 2 == 0 and not must_water:
            pass
        if not ops:
            return None
        return ops, prio, value
    # ongoing: TOMATO / STRAWBERRY
    last = crop_last_prod_age(crop)
    prod = crop_prod_tonight(crop, a)
    if a > last:
        # finished: harvest what is held, then the tile is freed (policy replants)
        ops = []
        if y > 0:
            ops.append(["HARVEST", None])
        ops.append(["DIG", None])
        return ops, P_TODAY, price * y * 0.5 + 20
    fert_now = False
    if prod and fert_until < day and use_fert:
        fert_now = True
    # harvest: before a production would overflow the cap, or DSM's cadence (the morning after a production)
    held_after = y + (2 if prod else 0)
    harvest_now = y > 0 and (held_after > my or (a >= f and (a - (f - 1)) % max(1, iv) == (1 % max(1, iv))))
    if crop == "TOMATO":
        harvest_now = y > 0 and (held_after > my or y >= 2)
    if harvest_now:
        ops.append(["HARVEST", None])
        value += price * 0.2 * y
        prio = min(prio, P_TODAY if held_after > my else P_HARV)
    if fert_now:
        ops.append(["FERTILIZE", None])
        value += price * 1.0
        prio = min(prio, P_YIELD)
    if prod:
        ops.append(["WATER", None])
        value += price * (1 + (1 if (fert_until >= day or fert_now) else 0))
        prio = min(prio, P_YIELD)
    elif must_water:
        ops.append(["WATER", None])
    if not ops:
        return None
    return ops, prio, value


def animal_ops(t, day, ctx):
    """Ops for one animal tile today. -> list of (ops, prio, value) (separate jobs: collect / feed+care / harvest)."""
    an = t["animal"]
    f, iv, mh, prod = ANIMALS[an]
    a = day - t["placed_day"]
    y = t.get("yield_units", 0)
    unfed = t.get("consecutive_unfed", 0)
    prod_tonight = animal_prod_tonight(an, a)
    price = ctx.get("price", {})
    pp = price.get(prod, BASE[prod])
    pw = price.get("WHEAT", BASE["WHEAT"])
    last_day = ctx.get("last_feed_day", {}).get(an, 27)
    out = []
    if t.get("fertilizer_available"):
        out.append(([["COLLECT_FERTILIZER", None]], P_LOW, price.get("FERTILIZER", 30)))
    feed = False
    if day <= last_day:
        if prod_tonight:
            feed = True
        elif unfed >= 1:
            feed = True
        else:
            ratio = pp / max(1.0, pw)
            thr = {"COW": 2.0, "SHEEP": 1.5, "GOOSE": 0.0}[an]
            feed = ratio >= thr
    if feed:
        pr = P_SAVE if (unfed >= 1 and not ctx.get("release", {}).get(an)) else (P_YIELD if prod_tonight else P_LOW)
        out.append(([["FEED", None], ["CARE", None]], pr, pp * (1.0 if prod_tonight else 0.6) - pw))
    # harvest: before a production would pass the cap, or the morning after a production
    bonus = t.get("pending_care_bonus", 0)
    tonight = (1 + bonus + (1 if feed else 0)) if prod_tonight else 0
    if y > 0 and (y + tonight > mh or (an != "GOOSE" and animal_prod_tonight(an, a - 1)) or (an == "GOOSE" and y >= 3)
                  or day >= 29):
        out.append(([["HARVEST", None]], P_TODAY if y + tonight > mh else P_HARV, pp * 0.1 * y))
    return out


def day_jobs(tiles, day, ctx):
    """All maintenance jobs of the day. -> [(xy, ops, prio, value)]"""
    jobs = []
    for yy, row in enumerate(tiles):
        for xx, t in enumerate(row):
            if not isinstance(t, dict):
                continue
            if t.get("kind") == "PLANT":
                r = crop_ops(t, day, ctx)
                if r:
                    jobs.append(((xx, yy), r[0], r[1], r[2]))
            elif "animal" in t:
                for ops, pr, v in animal_ops(t, day, ctx):
                    jobs.append(((xx, yy), ops, pr, v))
    return jobs
