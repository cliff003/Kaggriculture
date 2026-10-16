"""Day executor for the new gold agent: routes the units over tile jobs.

A job is one visit to one tile with an ordered list of ops ([op, arg]). The executor plans routes for all units with
parallel cheapest insertion plus local search (relocate between routes, 2-opt inside a route), then walks the routes
step by step. Resources: FEED needs wheat and FERTILIZE needs fertilizer in the unit's own inventory, PLACE of an
animal needs the animal picked up from the shed. A route that needs wheat or fertilizer beyond what the unit carries
starts with a shed stop; COLLECT_FERTILIZER on the route feeds later FERTILIZE ops of the same route.

Pure Python, no engine import: the same module goes into the agent.
"""
import collections
import random

N = 10
ACCESS = ((4, 4), (5, 4), (4, 5), (5, 5))
ANIMALS = ("GOOSE", "COW", "SHEEP")
STRUCT = {"GOOSE": "COOP", "COW": "PASTURE", "SHEEP": "PASTURE"}
MOVE_NAME = {(1, 0): "EAST", (-1, 0): "WEST", (0, 1): "SOUTH", (0, -1): "NORTH"}
BIG = 10 ** 6
LAT_W = 0.0
FERT_PICK_RADIUS = -1     # -1: fertilizer pickups anywhere (benchmark); k: only when the unit is <= k from the shed


def dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def near_access(p):
    best = None
    for a in ACCESS:
        d = dist(p, a)
        if best is None or d < best[0]:
            best = (d, a)
    return best[1]


def step_toward(p, q):
    """Move name for one step from p toward q (larger axis gap first)."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    if abs(dx) >= abs(dy) and dx:
        return "EAST" if dx > 0 else "WEST"
    if dy:
        return "SOUTH" if dy > 0 else "NORTH"
    return "EAST" if dx > 0 else "WEST"


class Job:
    __slots__ = ("jid", "xy", "ops", "earliest", "deadline", "prio", "value", "owner", "started",
                 "wheat", "fert_need", "fert_net", "animal", "dur", "op_earliest", "unit", "base_earliest", "opprio")

    def __init__(self, jid, xy, ops, earliest=0, deadline=None, prio=2, value=1.0, op_earliest=None, unit=None):
        self.jid = jid
        self.unit = unit
        self.opprio = None
        self.base_earliest = earliest
        self.xy = tuple(xy)
        self.ops = [list(o) for o in ops]
        self.op_earliest = list(op_earliest) if op_earliest else [0] * len(self.ops)
        self.earliest = earliest
        self.deadline = deadline
        self.prio = prio
        self.value = value
        self.owner = None
        self.started = False
        self.recalc()

    def recalc(self):
        w = 0
        bal = need = 0
        an = None
        e = self.base_earliest
        for i, (op, arg) in enumerate(self.ops):
            if op == "FEED":
                w += 1
            elif op == "FERTILIZE":
                bal -= 1
                need = max(need, -bal)
            elif op == "COLLECT_FERTILIZER":
                bal += 1
            elif op == "PLACE" and arg in ANIMALS:
                an = arg
            e = max(e, self.op_earliest[i] - i)
        self.wheat, self.fert_need, self.fert_net, self.animal = w, need, bal, an
        self.dur = len(self.ops)
        self.earliest = e

    def pop_op(self):
        self.ops.pop(0)
        self.op_earliest.pop(0)
        if self.opprio:
            self.opprio.pop(0)
        self.started = True
        self.recalc()


class Unit:
    __slots__ = ("idx", "pos", "inv", "route", "pick", "target")

    def __init__(self, idx, pos, inv):
        self.idx, self.pos, self.inv = idx, tuple(pos), dict(inv)
        self.route = []      # job ids in visiting order (the first one is the current target)
        self.pick = {}       # item -> count still to pick up at the shed before the route
        self.target = None


# ------------------------------------------------------------------------------------------------ route evaluation
def route_cost(u_pos, t0, inv_w, inv_f, inv_an, seq, jobs, t_end, stock_w, stock_f):
    """Time the unit needs for seq. -> (end_step, travel, wait, pick_w, pick_f, feasible).
    Shed stop at the start when the route needs more wheat/fertilizer than carried; animals are picked up with a
    detour through the nearest access tile right before their PLACE job."""
    need_w = 0
    bal = inv_f
    minbal = inv_f
    for j in seq:
        J = jobs[j]
        need_w += J.wheat
        m = bal - J.fert_need
        if m < minbal:
            minbal = m
        bal += J.fert_net
    pick_w = max(0, need_w - inv_w)
    pick_f = max(0, -minbal)
    skip_f = 0
    if pick_f and FERT_PICK_RADIUS >= 0 and dist(u_pos, near_access(u_pos)) > FERT_PICK_RADIUS:
        skip_f, pick_f = pick_f, 0
    if pick_f > stock_f:
        skip_f += pick_f - stock_f
        pick_f = stock_f
    feasible = pick_w <= stock_w
    pos, t = u_pos, t0
    travel = wait = 0
    if pick_w or pick_f:
        a = near_access(pos)
        d = dist(pos, a)
        travel += d
        t += d + (1 if pick_w else 0) + (1 if pick_f else 0)
        pos = a
    carried = dict(inv_an) if inv_an else {}
    lat = 0.0
    for j in seq:
        J = jobs[j]
        if J.animal and carried.get(J.animal, 0) <= 0:
            a = near_access(pos)
            d = dist(pos, a)
            travel += d
            t += d + 1
            pos = a
        elif J.animal:
            carried[J.animal] -= 1
        d = dist(pos, J.xy)
        travel += d
        t += d
        if t < J.earliest:
            wait += J.earliest - t
            t = J.earliest
        t += J.dur
        if skip_f and J.fert_need:
            k = min(skip_f, J.fert_need)
            t -= k
            skip_f -= k
        lat += (t - t0) * (3.0 if J.prio <= 0 else (1.5 if J.prio <= 1 else 1.0))
        if J.deadline is not None and t > J.deadline + 1:
            feasible = False
        pos = J.xy
    if t > t_end:
        feasible = False
    spare = max(0, inv_w - need_w)
    return t, travel, wait, pick_w, pick_f, feasible, spare, lat


class Planner:
    """Parallel cheapest insertion + relocate/2-opt local search over all units.
    Shed wheat/fertilizer is a global budget: a route may only pick up what the other routes leave."""

    def __init__(self, jobs, units, t_now, t_end, stock_w, stock_f, balance=0.5):
        self.jobs = jobs
        self.units = units          # list of (key, pos, t_free, inv_w, inv_f, inv_an)
        self.t_now = t_now
        self.t_end = t_end
        self.stock_w = stock_w
        self.stock_f = stock_f
        self.balance = balance
        self.pw = [0] * len(units)
        self.pf = [0] * len(units)
        self.spare_cost = 3.0
        self.lat_w = LAT_W
        self.strip_fert = True

    def cost_of(self, k, seq):
        key, pos, tf, w, f, an = self.units[k]
        sw = self.stock_w - (sum(self.pw) - self.pw[k])
        sf = self.stock_f - (sum(self.pf) - self.pf[k])
        return route_cost(pos, tf, w, f, an, seq, self.jobs, self.t_end, sw, sf)

    def val(self, res):
        end, travel, wait, pw, pf, ok, spare, lat = res
        return (travel + wait + self.balance * max(0, end - self.t_now) ** 2 / 24.0 + self.spare_cost * spare
                + self.lat_w * lat + (0 if ok else BIG))

    def set_route(self, k, res):
        self.pw[k], self.pf[k] = res[3], res[4]

    def build(self, job_ids, routes0, lo):
        """Insert job_ids into copies of routes0 (never before position lo[k]), then local search."""
        U = len(self.units)
        routes = [list(r) for r in routes0]
        cache = []
        for k in range(U):
            res = self.cost_of(k, routes[k])
            self.set_route(k, res)
            cache.append(res)
        jit = getattr(self, "jitter", 0.0)
        rng = getattr(self, "rng", None)
        order = sorted(job_ids, key=lambda j: (self.jobs[j].prio, -(self.jobs[j].fert_net > 0),
                                               self.jobs[j].fert_need > 0, self.jobs[j].earliest,
                                               -dist(self.jobs[j].xy, (4.5, 4.5))
                                               + (jit * 4 * rng.random() if jit and rng else 0)))
        dropped = self.insert_all(routes, cache, order, lo)
        routes = self.improve(routes, lo)
        if dropped:
            cache = [self.cost_of(k, routes[k]) for k in range(U)]
            dropped = self.insert_all(routes, cache, dropped, lo)
        if dropped and self.strip_fert:
            stripped = []
            for j in dropped:
                J = self.jobs[j]
                if J.fert_need > 0 and any(o[0] != "FERTILIZE" for o in J.ops):
                    keep = [i for i, o in enumerate(J.ops) if o[0] != "FERTILIZE"]
                    J.ops = [J.ops[i] for i in keep]
                    J.op_earliest = [J.op_earliest[i] for i in keep]
                    J.recalc()
                    stripped.append(j)
            if stripped:
                cache = [self.cost_of(k, routes[k]) for k in range(U)]
                again = self.insert_all(routes, cache, stripped, lo)
                dropped = [j for j in dropped if j not in stripped] + again
        return routes, dropped

    def insert_all(self, routes, cache, order, lo):
        U = len(routes)
        dropped = []
        for j in order:
            best = None
            ju = self.jobs[j].unit
            for k in range(U):
                if ju is not None and self.units[k][0] != ju:
                    continue
                seq = routes[k]
                b0 = self.val(cache[k])
                for p in range(lo[k], len(seq) + 1):
                    res = self.cost_of(k, seq[:p] + [j] + seq[p:])
                    if not res[5]:
                        continue
                    c = self.val(res) - b0
                    if best is None or c < best[0]:
                        best = (c, k, p, res)
            if best is None:
                dropped.append(j)
                continue
            _, k, p, res = best
            routes[k].insert(p, j)
            cache[k] = res
            self.set_route(k, res)
        return dropped

    def improve(self, routes, lo, rounds=3):
        U = len(routes)
        cur = []
        for k in range(U):
            res = self.cost_of(k, routes[k])
            self.set_route(k, res)
            cur.append(self.val(res))
        for _ in range(rounds):
            moved = False
            for k in range(U):
                seq = routes[k]
                n = len(seq)
                if n - lo[k] < 3:
                    continue
                improved = True
                while improved:
                    improved = False
                    for i in range(lo[k], n - 1):
                        for m in range(i + 1, n):
                            cand = seq[:i] + seq[i:m + 1][::-1] + seq[m + 1:]
                            res = self.cost_of(k, cand)
                            if res[5] and self.val(res) < cur[k] - 1e-9:
                                seq[:] = cand
                                cur[k] = self.val(res)
                                self.set_route(k, res)
                                improved = moved = True
                                break
                        if improved:
                            break
            for k in range(U):
                i = lo[k]
                while i < len(routes[k]):
                    j = routes[k][i]
                    if self.jobs[j].unit is not None:
                        i += 1
                        continue
                    src = routes[k][:i] + routes[k][i + 1:]
                    rs = self.cost_of(k, src)
                    if not rs[5]:
                        i += 1
                        continue
                    old_k = (self.pw[k], self.pf[k])
                    self.set_route(k, rs)
                    gain0 = cur[k] - self.val(rs)
                    best = None
                    for k2 in range(U):
                        if k2 == k:
                            continue
                        s2 = routes[k2]
                        for p in range(lo[k2], len(s2) + 1):
                            res = self.cost_of(k2, s2[:p] + [j] + s2[p:])
                            if not res[5]:
                                continue
                            delta = self.val(res) - cur[k2] - gain0
                            if delta < -1e-9 and (best is None or delta < best[0]):
                                best = (delta, k2, p, res)
                    if best is not None:
                        _, k2, p, res = best
                        routes[k2].insert(p, j)
                        routes[k] = src
                        cur[k2] = self.val(res)
                        self.set_route(k2, res)
                        cur[k] = self.val(rs)
                        moved = True
                    else:
                        self.pw[k], self.pf[k] = old_k
                        i += 1
            if not moved:
                break
        return routes


# ------------------------------------------------------------------------------------------------ validity
def op_valid(op, arg, tile, inv, seeds, day):
    """Would the engine apply this tile op now (light copy of _apply_unit_action's guards)?"""
    if tile == "LOCKED":
        return False
    isd = isinstance(tile, dict)
    if op == "PLANT":
        return tile is None and seeds.get(arg, 0) > 0
    if op == "WATER":
        return isd and tile.get("kind") == "PLANT" and not tile.get("watered_today")
    if op == "HARVEST":
        return isd and tile.get("yield_units", 0) > 0
    if op == "FERTILIZE":
        return isd and tile.get("kind") == "PLANT" and inv.get("FERTILIZER", 0) > 0
    if op == "DIG":
        return tile is not None and not (isd and "animal" in tile)
    if op in ("BUILD_COOP", "BUILD_PASTURE"):
        return tile is None
    if op == "FEED":
        return isd and "animal" in tile and not tile.get("fed_today") and inv.get("WHEAT", 0) > 0
    if op == "CARE":
        return isd and "animal" in tile and not tile.get("cared_today")
    if op == "COLLECT_FERTILIZER":
        return isd and "animal" in tile and bool(tile.get("fertilizer_available"))
    if op == "PLACE":
        return (isd and tile.get("kind") == STRUCT.get(arg) and "animal" not in tile and inv.get(arg, 0) > 0)
    return False


# ------------------------------------------------------------------------------------------------ executor
class Executor:
    """Keeps jobs and routes across the steps of one day."""

    def __init__(self, replan_every=4, balance=0.5, tries=6, seed=0):
        self.jobs = {}
        self.routes = {}          # unit idx -> [jid]
        self.future_routes = []   # routes planned for units that are not there yet
        self.picks = {}           # unit idx -> {item: n} pending pickups
        self.replan_every = replan_every
        self.balance = balance
        self.tries = tries
        self.rng = random.Random(seed)
        self.last_plan = None
        self.n_units_seen = 0
        self.dirty = True
        self.dropped = []
        self.hook = None
        self.full_every = 0       # full re-plan (priority order) every k steps; 0 = only the first plan
        self.last_full = -99
        self.room = None          # [shed room left this step], shared by deliveries and the hook
        self.stats = collections.Counter()

    def add_job(self, job):
        self.jobs[job.jid] = job
        self.dirty = True

    def open_jobs(self):
        return [j for j, J in self.jobs.items() if J.ops]

    def plan(self, t, t_end, units, invs, avail_w, avail_f, future=(), full=False):
        """full: re-plan every open job except each unit's current target (multi-start); otherwise repair: keep the
        routes, insert unassigned jobs, improve with relocate / 2-opt. future: [(t_avail, pos)] units to come."""
        U = len(units)
        F = len(future)
        cur = []
        for k in range(U):
            cur.append([j for j in self.routes.get(k, []) if self.jobs[j].ops])
        fut = [[j for j in (self.future_routes[i] if i < len(self.future_routes) else []) if self.jobs[j].ops]
               for i in range(F)]
        uspec = []
        for k in range(U):
            inv = invs[k]
            an = {a: inv.get(a, 0) for a in ANIMALS if inv.get(a, 0) > 0}
            uspec.append((k, tuple(units[k]), t, inv.get("WHEAT", 0), inv.get("FERTILIZER", 0), an))
        for i, (ta, pos) in enumerate(future):
            uspec.append((U + i, tuple(pos), max(t, ta), 0, 0, {}))
        if full:
            routes0 = [r[:1] for r in cur] + [[] for _ in range(F)]
        else:
            routes0 = cur + fut
        lo = [1 if (k < U and routes0[k]) else 0 for k in range(U + F)]
        assigned = set(j for r in routes0 for j in r)
        free = [j for j in self.open_jobs() if j not in assigned]
        best = None
        tries = max(1, self.tries) if full else 1
        for trial in range(tries):
            P = Planner(self.jobs, uspec, t, t_end, avail_w, avail_f, self.balance)
            P.jitter = 0.0 if trial == 0 else 1.0
            P.rng = self.rng
            routes, dropped = P.build(free, routes0, lo)
            lost = sum(self.jobs[j].value * max(1, self.jobs[j].dur) for j in dropped)
            tot = sum(P.val(P.cost_of(k, routes[k])) for k in range(len(uspec)))
            key = (lost, tot)
            if best is None or key < best[0]:
                best = (key, routes, dropped, list(P.pw), list(P.pf))
        _, routes, dropped, pw, pf = best
        self.routes = {k: routes[k] for k in range(U)}
        self.future_routes = [routes[U + i] for i in range(F)]
        self.future_pos = [tuple(p) for (_, p) in future]
        for J in self.jobs.values():
            J.owner = None
        for k in range(U):
            for j in self.routes[k]:
                self.jobs[j].owner = k
        self.picks = {}
        for k in range(U):
            need = {}
            if pw[k]:
                need["WHEAT"] = pw[k]
            if pf[k]:
                need["FERTILIZER"] = pf[k]
            self.picks[k] = need
        self.dropped = dropped
        self.stats["dropped"] += len(dropped)
        self.stats["plans_full" if full else "plans_repair"] += 1
        self.last_plan = t
        self.n_units_seen = U
        self.dirty = False

    def act(self, t, t_end, day, units, invs, tiles, shed, seeds, avail_w, avail_f, animal_avail=None, future=()):
        """One step. units: positions [farmer, hand1, ...]; invs: their inventories; tiles[y][x]; shed/seeds dicts.
        avail_w/avail_f: shed wheat/fertilizer the executor may take; future: [(t_avail, pos)] units hired but not
        yet on the farm. -> list of actions."""
        U = len(units)
        if U > self.n_units_seen and self.future_routes:
            # hands that just arrived take over the routes planned for them (same spawn tile first)
            new = list(range(self.n_units_seen, U))
            pool = list(range(len(self.future_routes)))
            fpos = getattr(self, "future_pos", [])
            for k in new:
                pick = None
                for i in pool:
                    if i < len(fpos) and fpos[i] == tuple(units[k]):
                        pick = i
                        break
                if pick is None and pool:
                    pick = pool[0]
                if pick is not None:
                    pool.remove(pick)
                    self.routes[k] = self.future_routes[pick]
            self.future_routes = [self.future_routes[i] for i in pool]
            self.future_pos = [fpos[i] for i in pool if i < len(fpos)]
            self.n_units_seen = U
        idle = any(not [j for j in self.routes.get(k, []) if self.jobs[j].ops] for k in range(U))
        if self.last_plan is None or (self.full_every and t - self.last_full >= self.full_every):
            self.plan(t, t_end, units, invs, avail_w, avail_f, future, full=True)
            self.last_full = t
        elif (self.dirty or U != self.n_units_seen or t - self.last_plan >= self.replan_every
              or (idle and self.dropped)):
            self.plan(t, t_end, units, invs, avail_w, avail_f, future, full=False)
        actions = []
        seeds_left = dict(seeds)
        stock = {"WHEAT": avail_w, "FERTILIZER": avail_f}
        if animal_avail:
            stock.update(animal_avail)
        claimed_tile = set()
        for k in range(U):
            pos = tuple(units[k])
            inv = invs[k]
            a = self._unit_action(k, pos, inv, tiles, seeds_left, stock, day, t, claimed_tile)
            actions.append(a)
            self.stats[a[0] if a[0] in ("PASS",) or a[0] in MOVE_NAME.values() else "OP"] += 1
        return actions

    def _unit_action(self, k, pos, inv, tiles, seeds_left, stock, day, t, claimed_tile):
        route = self.routes.setdefault(k, [])
        while route and not self.jobs[route[0]].ops:
            route.pop(0)
        if self.hook is not None:
            a = self.hook(k, pos, inv, route[0] if route else None)
            if a is not None:
                return a
        if route and self.jobs[route[0]].ops and self.jobs[route[0]].ops[0][0] == "DELIVER":
            J = self.jobs[route[0]]
            if pos not in ACCESS:
                return self._move(pos, near_access(pos))
            items = J.ops[0][1] or ()
            if self.room is not None and self.room[0] <= 0:
                items = ()
            for it in items:
                item, keep = (it, 0) if isinstance(it, str) else it
                n = inv.get(item, 0) - keep
                if n > 0:
                    if self.room is not None:
                        n = min(n, self.room[0])
                        self.room[0] -= n
                    self.stats["deliver"] += 1
                    return ["PLACE", item, int(n)]
            J.pop_op()
            route.pop(0)
            return self._unit_action(k, pos, inv, tiles, seeds_left, stock, day, t, claimed_tile)
        need = self.picks.get(k, {})
        # animals needed by the next job
        nxt = self.jobs[route[0]] if route else None
        if nxt is not None and nxt.animal and inv.get(nxt.animal, 0) <= 0:
            need = dict(need)
            need[nxt.animal] = 1
        if need:
            if pos in ACCESS:
                for item, n in list(need.items()):
                    have = stock.get(item, 0)
                    take = min(n, have)
                    if take > 0:
                        stock[item] = have - take
                        if item in self.picks.get(k, {}):
                            del self.picks[k][item]
                        return ["PICKUP", item, int(take)]
                    # nothing to take: give up this pickup
                    if item in self.picks.get(k, {}):
                        del self.picks[k][item]
                    self.stats["pick_none_" + item] += 1
                if nxt is not None and nxt.animal and inv.get(nxt.animal, 0) <= 0:
                    # the animal is not in the shed: hand the job back
                    self.stats["requeue_animal"] += 1
                    route.pop(0)
                    self.dirty = True
                    return self._unit_action(k, pos, inv, tiles, seeds_left, stock, day, t, claimed_tile)
            else:
                return self._move(pos, near_access(pos))
        if not route:
            self.stats["pass_noroute"] += 1
            return ["PASS"]
        J = self.jobs[route[0]]
        if pos != J.xy:
            return self._move(pos, J.xy)
        # at the tile: next valid op
        x, y = J.xy
        tile = tiles[y][x]
        while J.ops:
            op, arg = J.ops[0]
            if t < J.op_earliest[0]:
                if len(route) > 1 and J.op_earliest[0] - t > 1:
                    route.append(route.pop(0))
                    self.stats["rotate_earliest"] += 1
                    return self._unit_action(k, pos, inv, tiles, seeds_left, stock, day, t, claimed_tile)
                self.stats["pass_earliest"] += 1
                return ["PASS"]
            if op_valid(op, arg, tile, inv, seeds_left, day):
                if op == "PLANT":
                    seeds_left[arg] -= 1
                J.pop_op()
                self.stats["done_" + op] += 1
                return [op, arg] if op in ("PLANT", "PLACE") else [op]
            # invalid now: wait one step for a seed that is coming, else move on and come back later
            if op == "PLANT" and tile is None:
                if len(route) > 1:
                    route.append(route.pop(0))
                    self.stats["rotate_seed"] += 1
                    return self._unit_action(k, pos, inv, tiles, seeds_left, stock, day, t, claimed_tile)
                self.stats["pass_seed"] += 1
                return ["PASS"]
            if op == "FEED" or (op == "PLACE" and arg in ANIMALS):
                need_item = {"FEED": "WHEAT"}.get(op, arg)
                if inv.get(need_item, 0) <= 0 and self._still_needed(op, tile):
                    # resource missing: hand the job back to the planner instead of dropping the op
                    self.stats["requeue_" + op] += 1
                    route.pop(0)
                    self.dirty = True
                    return self._unit_action(k, pos, inv, tiles, seeds_left, stock, day, t, claimed_tile)
            self.stats["skip_" + op] += 1
            J.ops.pop(0)
            J.op_earliest.pop(0)
            if J.opprio:
                J.opprio.pop(0)
            J.recalc()
        route.pop(0)
        self.dirty = True
        return self._unit_action(k, pos, inv, tiles, seeds_left, stock, day, t, claimed_tile)

    @staticmethod
    def _still_needed(op, tile):
        if not isinstance(tile, dict):
            return False
        if op == "FEED":
            return "animal" in tile and not tile.get("fed_today")
        if op == "FERTILIZE":
            return tile.get("kind") == "PLANT"
        return "animal" not in tile

    @staticmethod
    def _move(p, q):
        return [step_toward(p, q)]
