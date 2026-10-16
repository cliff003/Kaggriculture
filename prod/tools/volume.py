r"""Relative value vs our production volume, per item, against a fixed rival schedule.
volume.py RAW.jsonl SIDE ITEM START_DAY RATE1,RATE2,...  (rate = units per day, sold at hour 6)"""
import sys, os, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mktsim

recs = mktsim.load(sys.argv[1])
side = int(sys.argv[2])
item = sys.argv[3]
d0 = int(sys.argv[4])
rates = [float(x) for x in sys.argv[5].split(",")]
end = int(sys.argv[6]) if len(sys.argv) > 6 else 29
base = []
for rec in recs:
    rival = mktsim.rival_flows(rec, side)
    o, r, *_ = mktsim.simulate(rec["shops"], rival, {}, items=[item])
    base.append(r[item])
print(f"{item} from day {d0} to {end}; rival base revenue {statistics.mean(base):.0f}")
print("rate/day  units  our_rev  avg_px  rival_loss  rel_total  rel_per_unit")
for rate in rates:
    ours_rev, loss, units = [], [], []
    for rec, b in zip(recs, base):
        rival = mktsim.rival_flows(rec, side)
        ours = {}
        acc = 0.0
        for d in range(d0, end + 1):
            acc += rate
            n = int(acc)
            acc -= n
            if n:
                ours[d * 24 + 6] = {item: n}
        o, r, ou, ru, _ = mktsim.simulate(rec["shops"], rival, ours, items=[item])
        ours_rev.append(o[item]); loss.append(b - r[item]); units.append(ou[item])
    u = statistics.mean(units); orv = statistics.mean(ours_rev); l = statistics.mean(loss)
    print(f"{rate:7.1f} {u:6.0f} {orv:8.0f} {orv/max(u,1):7.1f} {l:10.0f} {orv+l:10.0f} {(orv+l)/max(u,1):8.1f}")
