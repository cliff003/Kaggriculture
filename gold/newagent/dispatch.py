"""Greedy value dispatcher (alternative to executor.Executor with the same act() interface).

Every step, each unit without a live target gets one by a global greedy matching over (unit, job) pairs scored by
value per turn (travel + detour for supplies + duration), with an urgency bonus for jobs that must be done today and
are running out of time. Units top up wheat / fertilizer whenever they stand on a shed tile and open jobs need them.
No routes are planned beyond the current target, so delays and new jobs never leave a plan stale.
"""
import collections

N = 10
ACCESS = ((4, 4), (5, 4), (4, 5), (5, 5))
ANIMALS = ("GOOSE", "COW", "SHEEP")
STRUCT = {"GOOSE": "COOP", "COW": "PASTURE", "SHEEP": "PASTURE"}


def dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def near_access(p):
    return min(ACCESS, key=lambda a: (dist(p, a), ACCESS.index(a)))


def step_toward(p, q):
    dx, dy = q[0] - p[0], q[1] - p[1]
    if abs(dx) >= abs(dy) and dx:
        return "EAST" if dx > 0 else "WEST"
    if dy:
        return "SOUTH" if dy > 0 else "NORTH"
    return "EAST" if dx > 0 else "WEST"


def op_valid(op, arg, tile, inv, seeds):
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
        return isd and tile.get("kind") == STRUCT.get(arg) and "animal" not in tile and inv.get(arg, 0) > 0
    return False


class Dispatcher:
    def __init__(self, urgency=40.0, top_w=3, top_f=2, crit_slack=3, **kw):
        self.jobs = {}
        self.target = {}          # unit -> jid
        self.urgency = urgency
        self.top_w = top_w
        self.top_f = top_f
        self.crit_slack = crit_slack
        self.hook = None
        self.room = None
        self.dropped = []
        self.routes = {}
        self.stats = collections.Counter()

    def add_job(self, job):
        self.jobs[job.jid] = job

    # ------------------------------------------------------------------------------------------------ scoring
    def _cost(self, pos, inv, J, t):
        """(turns until the job is finished, travel) for a unit at pos, including a shed detour for supplies."""
        need_w = J.wheat > inv.get("WHEAT", 0)
        need_an = J.animal and inv.get(J.animal, 0) <= 0
        detour = 0
        p = pos
        if need_w or need_an:
            a = near_access(p)
            detour = dist(p, a) + 1
            p = a
        d = dist(p, J.xy)
        start = t + detour + d
        if start < J.earliest:
            start = J.earliest
        dur = J.dur - (min(J.fert_need, 0) if inv.get("FERTILIZER", 0) >= J.fert_need else 0)
        return start + dur - t, detour + d

    def _score(self, pos, inv, J, t, t_end):
        turns, travel = self._cost(pos, inv, J, t)
        if t + turns > t_end:
            return None
        v = J.value
        if J.prio <= 0:
            left = t_end - (t + turns)
            v += self.urgency * (2.0 if left <= self.crit_slack else 1.0)
        elif J.prio <= 1:
            v += self.urgency * 0.4
        return v / (turns + 0.5), turns

    # ------------------------------------------------------------------------------------------------ step
    def act(self, t, t_end, day, units, invs, tiles, shed, seeds, avail_w, avail_f, animal_avail=None, future=()):
        U = len(units)
        stock = {"WHEAT": avail_w, "FERTILIZER": avail_f}
        if animal_avail:
            stock.update(animal_avail)
        # release finished targets
        for k in list(self.target):
            jid = self.target[k]
            if k >= U or jid not in self.jobs or not self.jobs[jid].ops:
                del self.target[k]
        taken = set(self.target.values())
        free_units = [k for k in range(U) if k not in self.target]
        open_jobs = [jid for jid, J in self.jobs.items() if J.ops and jid not in taken]
        # greedy global matching
        if free_units and open_jobs:
            pairs = []
            for k in free_units:
                pos = tuple(units[k])
                inv = invs[k]
                for jid in open_jobs:
                    J = self.jobs[jid]
                    if J.unit is not None and J.unit != k:
                        continue
                    if J.wheat and inv.get("WHEAT", 0) < J.wheat and stock.get("WHEAT", 0) <= 0:
                        continue
                    if J.animal and inv.get(J.animal, 0) <= 0 and stock.get(J.animal, 0) <= 0:
                        continue
                    sc = self._score(pos, inv, J, t, t_end)
                    if sc is None:
                        continue
                    pairs.append((-sc[0], sc[1], k, jid))
            pairs.sort()
            used_u, used_j = set(), set()
            for negs, turns, k, jid in pairs:
                if k in used_u or jid in used_j:
                    continue
                self.target[k] = jid
                used_u.add(k)
                used_j.add(jid)
        self.routes = {k: [self.target[k]] for k in self.target}
        # act
        actions = []
        seeds_left = dict(seeds)
        for k in range(U):
            a = self._unit(k, tuple(units[k]), invs[k], tiles, seeds_left, stock, t)
            actions.append(a)
            self.stats[a[0] if a[0] in ("PASS", "NORTH", "SOUTH", "EAST", "WEST") else "OP"] += 1
        return actions

    def _unit(self, k, pos, inv, tiles, seeds_left, stock, t):
        jid = self.target.get(k)
        J = self.jobs.get(jid) if jid is not None else None
        if self.hook is not None:
            a = self.hook(k, pos, inv, jid)
            if a is not None:
                return a
        # top up supplies at the shed
        if pos in ACCESS:
            if J is not None and J.animal and inv.get(J.animal, 0) <= 0 and stock.get(J.animal, 0) > 0:
                stock[J.animal] -= 1
                return ["PICKUP", J.animal, 1]
            want_w = max(self.top_w, J.wheat if J is not None else 0) - inv.get("WHEAT", 0)
            if want_w > 0 and stock.get("WHEAT", 0) > 0 and self._open_need("FEED"):
                q = min(want_w, stock["WHEAT"])
                stock["WHEAT"] -= q
                return ["PICKUP", "WHEAT", int(q)]
            want_f = self.top_f - inv.get("FERTILIZER", 0)
            if want_f > 0 and stock.get("FERTILIZER", 0) > 0 and self._open_need("FERTILIZE"):
                q = min(want_f, stock["FERTILIZER"])
                stock["FERTILIZER"] -= q
                return ["PICKUP", "FERTILIZER", int(q)]
        if J is None:
            self.stats["pass_idle"] += 1
            return ["PASS"]
        if (J.wheat > inv.get("WHEAT", 0) or (J.animal and inv.get(J.animal, 0) <= 0)) and pos not in ACCESS:
            return [step_toward(pos, near_access(pos))]
        if pos != J.xy:
            return [step_toward(pos, J.xy)]
        tile = tiles[J.xy[1]][J.xy[0]]
        while J.ops:
            op, arg = J.ops[0]
            if op == "DELIVER":
                return self._deliver(k, J, pos, inv)
            if t < J.op_earliest[0]:
                if J.op_earliest[0] - t > 1:
                    del self.target[k]
                    return ["PASS"]
                return ["PASS"]
            if op_valid(op, arg, tile, inv, seeds_left):
                if op == "PLANT":
                    seeds_left[arg] -= 1
                J.pop_op()
                self.stats["done_" + op] += 1
                return [op, arg] if op in ("PLANT", "PLACE") else [op]
            if op == "PLANT" and tile is None:
                del self.target[k]
                return ["PASS"]
            if op == "FEED" and isinstance(tile, dict) and not tile.get("fed_today"):
                del self.target[k]
                return ["PASS"]
            self.stats["skip_" + op] += 1
            J.ops.pop(0)
            J.op_earliest.pop(0)
            if J.opprio:
                J.opprio.pop(0)
            J.recalc()
        del self.target[k]
        return ["PASS"]

    def _deliver(self, k, J, pos, inv):
        if pos not in ACCESS:
            return [step_toward(pos, near_access(pos))]
        for it in (J.ops[0][1] or ()):
            item, keep = (it, 0) if isinstance(it, str) else it
            n = inv.get(item, 0) - keep
            if n > 0:
                return ["PLACE", item, int(n)]
        J.pop_op()
        del self.target[k]
        return ["PASS"]

    def _open_need(self, op):
        for J in self.jobs.values():
            if J.ops and any(o[0] == op for o in J.ops):
                return True
        return False
