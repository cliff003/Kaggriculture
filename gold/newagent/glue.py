

# ================================================================================================ new executor glue
EXEC = "new"
_EXEC_SRC = None          # replaced by build.py with the source of gold/newagent/executor.py
_XNS = {}


def _xns():
    if not _XNS:
        src = _EXEC_SRC
        if src is None:
            here = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else "."
            src = open(os.path.join(here, "executor.py"), encoding="utf-8").read()
        exec(compile(src, "executor", "exec"), _XNS)
    return _XNS


XVAL = {P_CRIT: 60.0, P_WIN: 25.0, P_YIELD: 10.0, P_HARV: 6.0, P_PLANT: 5.0, P_LOW: 2.0, P_OPT: 1.0}
DELIVER_GOODS = ("MELON", "WOOL", "MILK", "STRAWBERRY", "TOMATO", "EGG", "CARROT")
XT_REPLAN = 4
XT_TRIES = 3


def x_ops(s, j):
    ops, oe = [], []
    have_seed = dict(s.seeds)
    for (op, arg, pr) in j.ops:
        ops.append([op, arg])
        e = 0
        if op == "PLANT":
            if have_seed.get(arg, 0) <= 0:
                e = s.step + 1
            else:
                have_seed[arg] -= 1
        elif op == "PLACE" and arg in ANIMALS:
            if s.shed.get(arg, 0) <= 0 and not any(i.get(arg, 0) for i in s.invs):
                e = s.step + 2
        oe.append(e)
    prio = min(pr for (_, _, pr) in j.ops)
    value = sum(XVAL.get(pr, 1.0) for (_, _, pr) in j.ops)
    return ops, oe, prio, value


def sync_exec(s, mem, ex, jobs):
    X = _xns()
    seen = set()
    changed = False
    carried_an = {}
    for i in s.invs:
        for a in ANIMALS:
            carried_an[a] = carried_an.get(a, 0) + i.get(a, 0)
    for xy, j in jobs.items():
        if not j.ops:
            continue
        ops, oe, prio, value = x_ops(s, j)
        if j.animal and s.shed.get(j.animal, 0) + carried_an.get(j.animal, 0) <= 0:
            # the animal is not on the farm yet (the market buys it once the structure stands): keep the build,
            # schedule the PLACE later
            keep = [i for i, o in enumerate(ops) if not (o[0] == "PLACE" and o[1] in ANIMALS)]
            ops = [ops[i] for i in keep]
            oe = [oe[i] for i in keep]
            if not ops:
                if xy in ex.jobs and ex.jobs[xy].ops:
                    ex.jobs[xy].ops = []
                    ex.jobs[xy].op_earliest = []
                    ex.jobs[xy].recalc()
                seen.add(xy)
                continue
        J = ex.jobs.get(xy)
        if J is None:
            ex.add_job(X["Job"](xy, xy, ops, earliest=0, prio=prio, value=value, op_earliest=oe))
            changed = True
        else:
            if not J.ops:
                changed = True
            J.ops = ops
            J.op_earliest = oe
            J.prio = prio
            J.value = value
            J.recalc()
        seen.add(xy)
    for jid, J in ex.jobs.items():
        if len(jid) == 2 and jid not in seen and J.ops:
            J.ops = []
            J.op_earliest = []
            J.recalc()
    if changed:
        ex.dirty = True


def planned_hires(s, mem):
    want = max(0, mem.get("hire_target", 0) - s.hires_today)
    if s.hour == 0:
        want = min(want, 8)
    elif s.hour > (3 if s.day < 10 else 1):
        want = 0
    cash, k = s.money, 0
    while k < want and cash >= fib(s.hires_today + k):
        cash -= fib(s.hires_today + k)
        k += 1
    return k


def future_units(s, k):
    occ = {t: 0 for t in SHED}
    for p in s.units:
        if p in occ:
            occ[p] += 1
    out = []
    for _ in range(k):
        best = min(SHED, key=lambda q: (occ[q], SHED.index(q)))
        occ[best] += 1
        out.append((s.step + 1, best))
    return out


def make_hook(s, mem, ctx):
    day, h = s.day, s.hour

    def hook(k, pos, inv, nxt):
        if pos in SHED_SET:
            goods = [g for g in DELIVER_GOODS if inv.get(g, 0) > 0]
            if day < 10 and inv.get("FERTILIZER", 0) > 0:
                goods.append("FERTILIZER")
            n = sum(inv.get(g, 0) for g in goods)
            if goods and (n >= 3 or inv.get("MELON", 0) or h >= 18 or day >= 29) and ctx.room > 0:
                item = max(goods, key=lambda g: inv.get(g, 0) * s.prices.get(g, BASE[g]))
                q = min(inv[item], ctx.room)
                ctx.room -= q
                ctx.placed[item] = ctx.placed.get(item, 0) + q
                return ["PLACE", item, q]
            return None
        sd = shed_dist(pos)
        room = 100 - sum(s.shed.values())
        if room < 6:
            return None
        if inv.get("MELON", 0) and h <= 21:
            return [step_toward(pos, nearest_shed(pos))]
        prem = inv.get("MILK", 0) + inv.get("WOOL", 0) + inv.get("STRAWBERRY", 0)
        if day < 10:
            prem += 2 * inv.get("FERTILIZER", 0)
        if prem >= 3 and sd <= 1 and h <= 21:
            return [step_toward(pos, nearest_shed(pos))]
        tot = sum(v for g, v in inv.items() if g in DELIVER_GOODS or g == "WHEAT")
        if (day >= 29 and h >= 17 and tot > 0) or (h >= 16 and tot >= 12 and sd <= 2):
            return [step_toward(pos, nearest_shed(pos))]
        return None
    return hook


def _agent_new(obs):
    s = parse(obs)
    mem = MEM.get(s.me)
    if mem is None or s.step == 0 or mem["step"] >= s.step:
        mem = MEM[s.me] = new_mem()
    mem["step"] = s.step
    if s.day == 0 and mem["tape_ok"] and OPENING != "plan":
        out = tape_step(s, mem)
        if out is not None:
            return out
    X = _xns()
    if mem["day"] != s.day:
        new_day(s, mem)
        mem["ex"] = X["Executor"](replan_every=XT_REPLAN, balance=0.5, tries=XT_TRIES)
    pol = mem["pol"]
    pol.prices = dict(s.prices)
    if mem.get("nq", len(s.quads)) != len(s.quads):
        pol.targets = assign_targets(s, mem, pol)
    mem["nq"] = len(s.quads)
    jobs = build_jobs(s, pol)
    mem["jobs"] = jobs
    ex = mem["ex"]
    sync_exec(s, mem, ex, jobs)
    ctx = Ctx(s)
    k = planned_hires(s, mem)
    fut = future_units(s, k)
    t0 = s.day * TPD
    t_end = min(t0 + TPD, LAST_STEP + 1)
    avail_w = s.shed.get("WHEAT", 0)
    avail_f = s.shed.get("FERTILIZER", 0) if pol.fert_ok else 0
    an_av = {a: s.shed.get(a, 0) for a in ANIMALS if s.shed.get(a, 0) > 0}
    ex.hook = make_hook(s, mem, ctx)
    invs = [s.invs[u] if u < len(s.invs) else {} for u in range(len(s.units))]
    acts = ex.act(s.step, t_end, s.day, s.units, invs, s.tiles, s.shed, s.seeds, avail_w, avail_f, an_av, future=fut)
    for u, a in enumerate(acts):
        if not a:
            continue
        if a[0] == "PICKUP":
            q = int(a[2]) if len(a) > 2 else 1
            ctx.picked[a[1]] = ctx.picked.get(a[1], 0) + q
            ctx.shed_left[a[1]] = ctx.shed_left.get(a[1], 0) - q
            ctx.room += q
        elif a[0] == "PLANT":
            ctx.seed_left[a[1]] = ctx.seed_left.get(a[1], 0) - 1
    owner = {}
    for u, r in ex.routes.items():
        for jid in r:
            if len(jid) == 2 and ex.jobs[jid].ops:
                owner[jid] = u
    mem["owner"] = owner
    market = market_orders(s, mem, pol, ctx, jobs)
    return {"farmer": acts[0], "hands": acts[1:], "market": market}


def agent(obs, config=None):
    if DEBUG:
        return _agent_new(obs) if EXEC == "new" else _agent(obs)
    try:
        return _agent_new(obs) if EXEC == "new" else _agent(obs)
    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}
