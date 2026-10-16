

# ============================================================================= p5: greedy per-step dispatch
# Team 42 research, 2026-09-26. The day plan (tile uses, buys, hires) is p4's; execution no longer follows
# a whole-day route per unit. Every step each unit without a live target takes the unreserved job with
# the best value per step (travel + ops, via a shed pickup when it lacks wheat, fertilizer or the animal),
# or a shed drop when the goods it carries are worth it. Inspired by how top adaptive agents (DECEM) work:
# almost no idle steps and every urgent job taken first.
CFG.update({
    "p5_minval": 20, "p5_drop_w": 0.25, "p5_drop_late": 1.0, "p5_drop_late_hour": 20, "p5_pick_cap": 8,
    "p5_urgent": 1000, "p5_travel_w": 1.0, "p5_melon_drop": True, "p5_keep_bonus": 0.0,
    "p5_plant_value": {"STRAWBERRY": 400, "MELON": 500, "TOMATO": 250, "WHEAT": 120, "CARROT": 100},
    "p5_weed_value": 60, "p5_morning_pick": True, "p5_dist_pow": 1.5, "p5_urgent_ramp": True, "p5_opportunistic": True,
})


def _p5_value(j, S):
    """p4's job values are 'loss if skipped today'; planting and weeding need their future worth here."""
    v = j["value"]
    pv = S["cfg"]["p5_plant_value"]
    if j["kind"] == "plant" or (j["kind"] == "crop" and j.get("plant")):
        v = max(v, v - 40 + pv.get(j.get("plant"), 60))
    elif j["kind"] == "weed":
        v = max(v, S["cfg"]["p5_weed_value"])
    return v


def _p5_needs(job, inv):
    need = {}
    ops = job["ops"]
    if "FEED" in ops and inv.get("WHEAT", 0) <= 0:
        need["WHEAT"] = 1
    if "FERTILIZE" in ops and inv.get("FERTILIZER", 0) <= 0:
        need["FERTILIZER"] = 1
    if "PLACE" in ops and job.get("place") and inv.get(job["place"], 0) <= 0:
        need[job["place"]] = 1
    return need


def _p5_carry_value(V, inv):
    return sum(n * V.prices.get(it, 0) for it, n in inv.items() if it in SELLABLE or it == "FERTILIZER")


def _p5_choose(V, S, i, pos, inv, jobs, taken, shed_now, feeds_left):
    cfg = S["cfg"]
    best = None
    for p, j in jobs.items():
        if p in taken:
            continue
        need = _p5_needs(j, inv)
        val = _p5_value(j, S)
        if cfg["p5_urgent_ramp"] and j.get("urg", 0) >= 2 and val > 600:
            val = 600 + (val - 600) * min(1.0, V.hour / 18.0)
        if need:
            if any(shed_now.get(k, 0) <= 0 for k in need):
                # cannot fetch the supply: keep only the ops that need nothing
                if "FEED" in j["ops"] and "WHEAT" in need:
                    rest = [o for o in j["ops"] if o not in ("FEED", "CARE")]
                    if not rest:
                        continue
                    val *= 0.3
                elif "PLACE" in j["ops"]:
                    continue
                else:
                    val *= 0.5
                sp = None
            else:
                sp = nearest_shed(pos)
        else:
            sp = None
        d = (dist(pos, sp) + 1 + dist(sp, p)) if sp else dist(pos, p)
        score = val / (cfg["p5_travel_w"] * d + len(j["ops"]) + 1.0) ** cfg["p5_dist_pow"]
        if best is None or score > best[0]:
            best = (score, p, j, need if sp else {}, sp)
    # a shed drop competes with the jobs
    cv = _p5_carry_value(V, inv)
    if cv > 0:
        sp = nearest_shed(pos)
        w = cfg["p5_drop_late"] if (V.hour >= cfg["p5_drop_late_hour"] or V.day >= LAST_DAY) else cfg["p5_drop_w"]
        if cfg["p5_melon_drop"] and inv.get("MELON", 0) > 0:
            w = max(w, 2.0)
        dscore = cv * w / (dist(pos, sp) + 1.0) ** cfg["p5_dist_pow"]
        if best is None or dscore > best[0]:
            return {"kind": "shed", "pos": sp, "drop": True, "pickup": {}}
    if best is None:
        return None
    _, p, j, need, sp = best
    if need:
        pick = {}
        for k in need:
            if k == "WHEAT":
                pick[k] = int(min(shed_now.get(k, 0), cfg["p5_pick_cap"], max(1, feeds_left)))
            elif k == "FERTILIZER":
                pick[k] = int(min(shed_now.get(k, 0), 4))
            else:
                pick[k] = 1
        return {"kind": "shed", "pos": sp, "drop": _p5_carry_value(V, inv) > 0, "pickup": pick, "then": p}
    return {"kind": "tile", "pos": p}


def p5_execute(V, S):
    n = len(V.units)
    acts = [["PASS"] for _ in range(n)]
    seed_left = dict(V.seeds)
    shed_now = dict(V.shed)
    jobs = {j["pos"]: j for j in gen_jobs(V, S) if j["value"] >= S["cfg"]["p5_minval"] or j.get("urg", 0) >= 2}
    assign = S.setdefault("assign", {})
    taken = set()
    for i in range(n):
        a = assign.get(i)
        if a and a["kind"] == "tile" and a["pos"] in jobs:
            taken.add(a["pos"])
        if a and a["kind"] == "shed" and a.get("then"):
            taken.add(a["then"])
    feeds_total = sum(1 for j in jobs.values() if "FEED" in j["ops"])
    carriers = sum(1 for inv in V.invs[:n] if inv.get("WHEAT", 0) > 0)
    carried_w = sum(inv.get("WHEAT", 0) for inv in V.invs[:n])
    for i in range(n):
        pos = V.units[i]
        inv = V.invs[i] if i < len(V.invs) else {}
        feeds_left = max(1, min(10, feeds_total - carried_w))
        if S["cfg"]["p5_morning_pick"] and V.hour <= 3 and pos in SHED_TILES and inv.get("WHEAT", 0) <= 0                 and feeds_total > 0 and shed_now.get("WHEAT", 0) > 0 and not (assign.get(i) or {}).get("_mp"):
            share = int(min(shed_now["WHEAT"], S["cfg"]["p5_pick_cap"], max(1, (feeds_total + n - 1) // n + 1)))
            shed_now["WHEAT"] -= share
            acts[i] = ["PICKUP", "WHEAT", share]
            assign[i] = {"kind": "tile", "pos": pos, "_mp": True} if False else None
            continue
        for _try in range(3):
            a = assign.get(i)
            if a and a["kind"] == "tile" and a["pos"] not in jobs:
                taken.discard(a["pos"])
                a = None
            if a is None:
                a = _p5_choose(V, S, i, pos, inv, jobs, taken, shed_now, feeds_left)
                assign[i] = a
                if a and a["kind"] == "tile":
                    taken.add(a["pos"])
                if a and a.get("then"):
                    taken.add(a["then"])
            if a is None:
                acts[i] = ["PASS"]
                break
            if pos != a["pos"]:
                if S["cfg"]["p5_opportunistic"] and pos in jobs:
                    # do what is doable on the tile we stand on before walking on
                    ops = live_ops(V, S, i, pos, inv, seed_left, {"pos": pos, "kind": "tile", "job": jobs[pos]}, shed_now)
                    if ops and ops[0][0] not in ("DIG",):
                        op = ops[0]
                        if op[0] == "PLANT":
                            seed_left[op[1]] = seed_left.get(op[1], 0) - 1
                        acts[i] = op
                        break
                acts[i] = [step_toward(pos, a["pos"])]
                break
            if a["kind"] == "shed":
                op = None
                if a.get("drop") and not a.get("_dropped") and any(v > 0 for v in inv.values()):
                    keep = {k: v for k, v in inv.items() if k in ("WHEAT",) and a.get("pickup")}
                    if not keep:
                        op = ["DROP"]
                        a["_dropped"] = True
                        for k2, v in inv.items():
                            shed_now[k2] = shed_now.get(k2, 0) + v
                if op is None:
                    for item, k in list(a.get("pickup", {}).items()):
                        have = inv.get(item, 0) if a.get("_dropped") is not True or not a.get("drop") else 0
                        need = k - have
                        if need > 0 and shed_now.get(item, 0) > 0:
                            m = int(min(need, shed_now[item]))
                            op = ["PICKUP", item, m]
                            shed_now[item] -= m
                            a["pickup"][item] = 0
                            break
                if op is None:
                    nxt = a.get("then")
                    assign[i] = {"kind": "tile", "pos": nxt} if nxt and nxt in jobs else None
                    continue
                acts[i] = op
                break
            stop = {"pos": pos, "kind": "tile", "job": jobs[pos]}
            ops = live_ops(V, S, i, pos, inv, seed_left, stop, shed_now)
            if not ops:
                taken.discard(pos)
                jobs.pop(pos, None)
                assign[i] = None
                continue
            op = ops[0]
            if op[0] == "PLANT":
                seed_left[op[1]] = seed_left.get(op[1], 0) - 1
            elif op[0] == "PLACE" and len(op) >= 3 and op[1] not in ANIMALS:
                shed_now[op[1]] = shed_now.get(op[1], 0) + int(op[2])
            acts[i] = op
            break
    for i in list(assign):
        if i >= n:
            del assign[i]
    S["shed_proj"] = shed_now
    return acts


def _agent(V, S):
    if S["day"] != V.day:
        S["day"] = V.day
        S["routes"] = {}
        S["assign"] = {}
    if V.hour == 0:
        day_plan(V, S)
    elif V.hour in S["cfg"]["midday_hours"] and V.day <= S["cfg"]["animal_last_day"]:
        midday_buy(V, S)
    elif S.get("event") and not (S.get("race_day") == V.day and V.hour < 9):
        S["event"] = False
        replan_event(V, S)
    acts = p5_execute(V, S)
    orders = market_orders(V, S, acts)
    return {"farmer": acts[0], "hands": acts[1:], "market": orders}


def agent(obs, config=None):
    V = View(obs)
    S = STATE.get(V.me)
    if S is None or V.step == 0 or V.step <= S["last_step"]:
        S = new_state()
        STATE[V.me] = S
    S["last_step"] = V.step
    try:
        return _agent(V, S)
    except Exception as e:
        import traceback
        S.setdefault("errors", []).append(repr(e))
        S["tb"] = traceback.format_exc()
        return {"farmer": ["PASS"], "hands": [["PASS"] for _ in V.units[1:]], "market": []}
