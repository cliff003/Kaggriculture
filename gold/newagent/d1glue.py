

# ================================================================================================ D1: day plan + executor
# The day's work is fixed at the first step of the day (every tile job with its full op list, replanting included) and
# routed once over all units, hires of the day included. Afterwards jobs only shrink as ops are done; tiles without an
# open job get a follow-up job when their state asks for one (melon tiles freed at noon, arrived animals, new land).
EXEC = "d1"
_EXEC_SRC = None          # replaced by build.py with the source of gold/newagent/executor.py
_XNS = {}
XT_REPLAN = 4
XT_TRIES = 3
XT_LAT = 0.3
XT_FPR = 1
XT_FULL = 6
SWITCH_DAY = 0
FOLLOW_UP = True


def _xns():
    if not _XNS:
        src = _EXEC_SRC
        if src is None:
            here = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else "."
            src = open(os.path.join(here, "executor.py"), encoding="utf-8").read()
        exec(compile(src, "executor", "exec"), _XNS)
        _XNS["LAT_W"] = XT_LAT
        _XNS["FERT_PICK_RADIUS"] = XT_FPR
    return _XNS


XVAL = {P_CRIT: 60.0, P_WIN: 25.0, P_YIELD: 10.0, P_HARV: 6.0, P_PLANT: 5.0, P_LOW: 2.0, P_OPT: 1.0}
DELIVER_GOODS = ("MELON", "WOOL", "MILK", "STRAWBERRY", "TOMATO", "EGG", "CARROT")


def x_job(s, xy, j, pending_seed):
    """Executor job from a g036 tile job. pending_seed: seeds already promised to earlier PLANT ops this step."""
    X = _xns()
    ops, oe = [], []
    for (op, arg, pr) in j.ops:
        ops.append([op, arg])
        e = 0
        if op == "PLANT":
            have = s.seeds.get(arg, 0) - pending_seed.get(arg, 0)
            pending_seed[arg] = pending_seed.get(arg, 0) + 1
            if have <= 0:
                e = s.step + 1
        elif op == "PLACE" and arg in ANIMALS:
            if s.shed.get(arg, 0) <= 0 and not any(i.get(arg, 0) for i in s.invs):
                e = s.step + 2
        oe.append(e)
    prio = min(pr for (_, _, pr) in j.ops)
    value = sum(XVAL.get(pr, 1.0) for (_, _, pr) in j.ops)
    J = X["Job"](xy, xy, ops, earliest=0, prio=prio, value=value, op_earliest=oe)
    J.opprio = [pr for (_, _, pr) in j.ops]
    return J


def add_day_jobs(s, mem, ex, pol, only_idle):
    """Add a job for every tile whose g036 job has ops; only_idle: skip tiles that still have an open job."""
    pend = {}
    added = 0
    for y in range(N):
        for x in range(N):
            xy = (x, y)
            J0 = ex.jobs.get(xy)
            if only_idle and J0 is not None:
                if J0.ops:
                    continue
                t = s.tiles[y][x]
                # the tile already had its job today: follow up only when it was freed (replant) or a structure
                # waits for an animal that is now here
                if not (t is None or (is_dict(t) and t.get("kind") == "WEED")
                        or (is_dict(t) and t.get("kind") in ("COOP", "PASTURE") and not t.get("animal"))):
                    continue
            j = tile_job(s, xy, pol, s.hour)
            if j is None or not j.ops:
                continue
            if j.animal and s.shed.get(j.animal, 0) + sum(i.get(j.animal, 0) for i in s.invs) <= 0:
                # the animal is not on the farm yet: keep what can be done without it (the build)
                keep = [o for o in j.ops if not (o[0] == "PLACE" and o[1] in ANIMALS)]
                if not keep:
                    continue
                j2 = Job(xy, j.kind)
                for o in keep:
                    j2.add(*o)
                j = j2
            if only_idle and all(o[0] in ("WATER",) and o[2] >= P_YIELD for o in j.ops) and s.hour >= 1:
                # an optional watering that appeared later in the day is not worth a new trip
                if not any(o[2] <= P_WIN for o in j.ops):
                    continue
            J = x_job(s, xy, j, pend)
            if J0 is not None:
                J0.ops, J0.op_earliest, J0.prio, J0.value = J.ops, J.op_earliest, J.prio, J.value
                J0.opprio = J.opprio
                J0.recalc()
            else:
                ex.add_job(J)
            added += 1
    if added:
        ex.dirty = True
    return added


class _JV:
    """g036-style job view of an executor job, for the market code (wheat, seed, animal, ops, prio, dur)."""
    __slots__ = ("xy", "ops", "prio", "wheat", "fert", "fert_gain", "animal", "seed", "kind")

    def __init__(self, J):
        self.xy = J.xy
        pr = getattr(J, "opprio", None) or [J.prio] * len(J.ops)
        pr = pr[-len(J.ops):] if len(pr) >= len(J.ops) else [J.prio] * len(J.ops)
        self.ops = [(o[0], o[1], p) for o, p in zip(J.ops, pr)]
        self.prio = J.prio
        self.wheat = sum(1 for o in J.ops if o[0] == "FEED")
        self.fert = sum(1 for o in J.ops if o[0] == "FERTILIZE")
        self.fert_gain = sum(1 for o in J.ops if o[0] == "COLLECT_FERTILIZER")
        self.animal = next((o[1] for o in J.ops if o[0] == "PLACE" and o[1] in ANIMALS), None)
        self.seed = next((o[1] for o in J.ops if o[0] == "PLANT"), None)
        self.kind = "x"

    def dur(self):
        return len(self.ops)


def job_views(ex):
    out = {}
    for jid, J in ex.jobs.items():
        if len(jid) == 2 and J.ops:
            out[jid] = _JV(J)
    return out


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
    """Deliveries: at a shed tile a unit DROPs everything (1 turn) when the shed has room, then re-picks the wheat and
    fertilizer its route still needs; late in the day loaded units walk back to drop."""
    day, h = s.day, s.hour
    ex = mem["ex"]

    def route_needs(k):
        w = f = 0
        for jid in ex.routes.get(k, []):
            J = ex.jobs.get(jid)
            if J is not None and J.ops:
                w += J.wheat
                f += J.fert_need
        return w, f

    def hook(k, pos, inv, nxt):
        sell = {g: v for g, v in inv.items() if g in SELLABLE and v > 0}
        tot = sum(sell.values())
        if pos in SHED_SET:
            if tot <= 0 or ctx.room <= 0:
                return None
            w_need, f_need = route_needs(k)
            spare = tot - min(inv.get("WHEAT", 0), w_need) - min(inv.get("FERTILIZER", 0), f_need)
            if spare < DROP_MIN and not inv.get("MELON", 0) and h < 18 and day < 29:
                return None
            if tot <= ctx.room:
                ctx.room -= tot
                for g, v in sell.items():
                    ctx.placed[g] = ctx.placed.get(g, 0) + v
                re = {}
                if w_need and inv.get("WHEAT", 0):
                    re["WHEAT"] = min(inv["WHEAT"], w_need)
                if f_need and inv.get("FERTILIZER", 0):
                    re["FERTILIZER"] = min(inv["FERTILIZER"], f_need)
                if re:
                    ex.picks[k] = re
                return ["DROP"]
            item = max(sell, key=lambda g: sell[g] * s.prices.get(g, BASE[g]))
            q = min(sell[item], ctx.room)
            ctx.room -= q
            ctx.placed[item] = ctx.placed.get(item, 0) + q
            return ["PLACE", item, q]
        if 100 - sum(s.shed.values()) < 6:
            return None
        sd = shed_dist(pos)
        if inv.get("MELON", 0) and h <= 21:
            return [step_toward(pos, nearest_shed(pos))]
        if day >= 29 and h >= 17 and tot > 0 and sd <= 24 - h:
            return [step_toward(pos, nearest_shed(pos))]
        if h >= LATE_DROP_HOUR and tot >= LATE_DROP_MIN and sd <= min(3, 22 - h):
            return [step_toward(pos, nearest_shed(pos))]
        return None
    return hook


DELIVER_MIN = 8
DELIVER_LATE = 17
KEEP_WHEAT = 3
KEEP_FERT = 2
DROP_MIN = 3
USE_DELIVER_JOBS = False
LATE_DROP_HOUR = 17
LATE_DROP_MIN = 10


def ensure_deliveries(s, mem, ex):
    """Unit-specific DELIVER jobs (off by default: the DROP hook delivers)."""
    X = _xns()
    keep = {"WHEAT": 0 if s.day >= 29 else KEEP_WHEAT, "FERTILIZER": 0 if (s.day < 10 or s.day >= 29) else KEEP_FERT}
    goods = list(DELIVER_GOODS) + ["WHEAT", "FERTILIZER"]
    open_d = {}
    for jid, J in ex.jobs.items():
        if len(jid) == 3 and jid[0] == "D" and J.ops:
            open_d[jid[1]] = jid
    added = 0
    for k in range(len(s.units)):
        if k in open_d:
            continue
        inv = s.invs[k] if k < len(s.invs) else {}
        n = sum(max(0, inv.get(g, 0) - keep.get(g, 0)) for g in goods)
        if n <= 0:
            continue
        late = s.hour >= DELIVER_LATE or s.day >= 29
        if n < DELIVER_MIN and not late and not inv.get("MELON", 0):
            continue
        xy = nearest_shed(s.units[k])
        J = X["Job"](("D", k, s.step), xy, [["DELIVER", tuple((g, keep.get(g, 0)) for g in goods)]], earliest=0,
                     prio=P_WIN if n >= 12 or late else P_YIELD, value=2.0 * n, unit=k)
        ex.add_job(J)
        added += 1
    if added:
        ex.dirty = True


def _agent_d1(obs):
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
    fresh = mem["day"] != s.day
    if fresh:
        new_day(s, mem)
        mem["ex"] = X["Executor"](replan_every=XT_REPLAN, balance=0.5, tries=XT_TRIES)
        mem["ex"].full_every = XT_FULL
    pol = mem["pol"]
    pol.prices = dict(s.prices)
    if mem.get("nq", len(s.quads)) != len(s.quads):
        pol.targets = assign_targets(s, mem, pol)
    mem["nq"] = len(s.quads)
    ex = mem["ex"]
    if fresh:
        add_day_jobs(s, mem, ex, pol, only_idle=False)
    elif FOLLOW_UP:
        add_day_jobs(s, mem, ex, pol, only_idle=True)
    if DELIVER_MIN > 0 and USE_DELIVER_JOBS:
        ensure_deliveries(s, mem, ex)
    jobs = job_views(ex)
    mem["jobs"] = jobs
    ctx = Ctx(s)
    k = planned_hires(s, mem)
    fut = future_units(s, k)
    t_end = min(s.day * TPD + TPD, LAST_STEP + 1)
    avail_w = s.shed.get("WHEAT", 0)
    avail_f = s.shed.get("FERTILIZER", 0) if pol.fert_ok else 0
    an_av = {a: s.shed.get(a, 0) for a in ANIMALS if s.shed.get(a, 0) > 0}
    ctx.room = 100 - sum(s.shed.values())
    ex.hook = make_hook(s, mem, ctx)
    ex.room = None
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


def _agent_switch(obs):
    """g036's own per-step flow before SWITCH_DAY (cash-starved opening), the D1 day planner from then on."""
    step = int(_g(obs, "step", 0))
    if step // TPD < SWITCH_DAY:
        return _agent(obs)
    return _agent_d1(obs)


def agent(obs, config=None):
    if DEBUG:
        return _agent_switch(obs)
    try:
        return _agent_switch(obs)
    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}
