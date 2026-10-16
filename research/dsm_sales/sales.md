# DSM (#1): selling and harvest-timing policy, reverse-engineered from 92 live games

Team 42 research note, 2026-09-24. Research only: nothing was submitted, nothing under tools\, submissions\ or ~/.kaggle was touched.

**Data and method**
- `data\games\dsm.jsonl.gz`: 92 games, DSM won all 92. Opponents: DECEM 5, Vadim Vasilenko 2, Unknown Mother-Goose 2 (the "lineage" that shares DSM's opening, 9 games) and 83 other teams.
- Every game is replayed through kaggle-environments 1.32.7 with both recorded action tapes and the record's seed (the approach of `tools\econ.py`). **All 92 games reproduce both server rewards exactly.** The replay logs, at every step: both sheds and unit inventories, market inventory and quotes, every traded unit with its market slot, every DSM unit action with the tile it acted on, and every end-of-day drop.
- Tags: **[V92]** measured on all 92 games pooled; **[V9]** measured on the 9 lineage games only; **[E]** follows from the engine source; **[I]** my interpretation, not verified.
- Timing convention [E]: in step t the engine runs unit actions, then the market (slot by slot, both players in lockstep), then town consumption (shops when t%4 == 0, town centre when t%24 == 0), then the day end when t%24 == 23. So goods a unit DROPs or PLACEs at step t can be sold in the same step, and **m4 = 1 (t%4 == 1) is the first market after a consumption tick**. Hour h = t%24. **Stock S** = DSM's shed right before the market of the step (after its own drops of that step).
- Full tables: `tables.md` (all sections), `rules_out.md` (cross-validated rule families), `composite_out.md` (best composite rules), `trees_out.md` (decision trees).

---

## 0. The policy on one page [V92 unless tagged]

| product | when DSM sells | lot | best simple rule (Section 2.3) | fit: exact / sell-hold / corr (turn, day) |
|---|---|---|---|---|
| MELON | the step it reaches the shed (mid-day drops h7-h16, or h0 if carried overnight) | whole batch, 6 or 12 | sell everything at once | 96% / 98% / 0.83, 0.98 |
| EGG | h22 (56% of units), leftovers h23 | everything | hold all day, dump at h22-h23 | 96% / 97% / 0.76, 0.37 |
| TOMATO | h22 (40%), h0, h18 | everything | same as egg; + h0 dump when shed >= 90 | 94% / 96% / 0.62, 0.39 |
| CARROT | h22-h23, h0-h2 | median 9 | same as tomato | 88% / 89% / 0.37, 0.06 |
| WHEAT | h0-h2 (surplus over a feed reserve), h22 (clear the shed) | median 5 | h22-23 sell all; h0/h1/h2 keep n_animals, 2/3, 1/3 of n_animals | 77% / 82% / 0.48, 0.55 |
| STRAWBERRY | first market after each tick (h5, h9, ..., h21), h0 when the market is flooding | 2 per tick; 6 or 11 at h0 | see 2.3 | 78% / 83% / 0.59, 0.55 |
| MILK | first market after each tick, mostly h9-h21; morning batch as soon as it is placed | 2, or the whole fresh batch (3, 6, 9) | see 2.3 | 81% / 85% / 0.45, 0.73 |
| WOOL | first market after each tick if a yarn store consumes; fresh batch on arrival | ceil(tick consumption / 2), fresh 4 or 8 | see 2.3 | 85% / 92% / 0.73, 0.88 |
| FERTILIZER | h0 (49% of units), h2-h3, h7, h22 | the whole shed stock | hours 0,2,3,7,22,23 sell all while quote >= 40 | 69% / 71% / 0.72, 0.57 |

Headline facts:
1. **No price-threshold rule reproduces DSM.** Thresholds on price vs base, vs recent price, vs its own last sale price, and "sell back what the town consumed" all score at or below "always hold" (Section 2.2). DSM's sales are driven by **time of day, tick phase, stock, fresh drops and shed room**, with a price floor only at very low prices.
2. **Premium goods are sold on the first market after each consumption tick, in lots of 1-2.** That is where quotes peak (wool +37% at h1 vs the day mean). DSM's realised price beats the same-day mean quote by **+4% strawberry, +7% milk, +17% wool**; opponents get -4%, 0%, +3%.
3. **Daily fill-and-clear cycle at the cap.** The shed holds ~90 items after the day-end drop. On days 12-28 units carry ~84 items at h22 while the shed holds ~22 (106 > 100), so the h22 staple dump is what makes the day-end drop fit (shed ~8 at h23). Premium stock is paced through the day.
4. **Harvest is price-gated.** Given yield on the tile, cows are harvested that day in 27% of cases when the milk quote is < 0.3 base vs 93-99% when it is >= 0.7 base; sheep 24% vs 86-90%; strawberries (late game) 51% vs 88%. Yield is stored on the animal or plant instead of in a glutted market.

---

## 1. When DSM sells [V92]

| product | sale turns/game | units/game | lot median / mean / p90 / max | sale turns per selling day | units sold at h0 | units sold at m4=1 |
|---|---|---|---|---|---|---|
| WHEAT | 86 | 538 | 5 / 6.2 / 13 / 42 | 3.5 | 15% | 23% |
| CARROT | 21 | 179 | 9 / 8.3 / 13 / 32 | 2.4 | 16% | 18% |
| TOMATO | 23 | 154 | 7 / 6.7 / 11 / 32 | 1.9 | 16% | 6% |
| STRAWBERRY | 74 | 216 | 2 / 2.9 / 6 / 13 | 4.5 | 22% | 52% |
| MELON | 9 | 60 | 6 / 6.7 / 12 / 12 | 3.0 | 10% | 30% |
| EGG | 29 | 211 | 8 / 7.3 / 14 / 30 | 1.7 | 0% | 8% |
| MILK | 60 | 202 | 2 / 3.4 / 6 / 11 | 3.2 | 6% | 69% |
| WOOL | 56 | 143 | 2 / 2.5 / 6 / 12 | 3.9 | 4% | 53% |
| FERTILIZER | 74 | 243 | 2 / 3.3 / 10 / 22 | 2.6 | 49% | 8% |

DSM executes a sale on 304 of 719 action steps per game.

**By step % 4** (share of units, share of sale turns in brackets). Shop consumption happens after the market of m4 = 0 steps:

| product | m4=0 (before tick) | m4=1 (first after tick) | m4=2 | m4=3 |
|---|---|---|---|---|
| WHEAT | 26% (23%) | 23% (21%) | 35% (37%) | 16% (19%) |
| CARROT | 26% (20%) | 18% (16%) | 40% (44%) | 15% (20%) |
| TOMATO | 22% (17%) | 6% (5%) | 62% (60%) | 11% (18%) |
| STRAWBERRY | 27% (13%) | **52% (62%)** | 12% (16%) | 9% (9%) |
| MELON | 29% (33%) | 30% (22%) | 11% (12%) | 30% (33%) |
| EGG | 5% (5%) | 8% (7%) | **70% (63%)** | 17% (25%) |
| MILK | 11% (7%) | **69% (76%)** | 13% (11%) | 6% (6%) |
| WOOL | 13% (8%) | **53% (68%)** | 15% (12%) | 18% (13%) |
| FERTILIZER | **55% (29%)** | 8% (15%) | 25% (31%) | 12% (25%) |

The m4=0 share of strawberry, fertilizer and staples is mostly hour 0; the m4=2 peak of staples is hour 22.

**P(DSM sells | stock S > 0) at selected hours** (all 24 hours in `tables.md`):

| product | h0 | h1 | h2 | h5 | h9 | h13 | h17 | h21 | h22 | h23 |
|---|---|---|---|---|---|---|---|---|---|---|
| WHEAT | 0.35 | 0.33 | 0.35 | 0.10 | 0.04 | 0.12 | 0.09 | 0.09 | **0.74** | 0.38 |
| CARROT | 0.22 | 0.22 | 0.22 | 0.05 | 0.01 | 0.02 | 0.09 | 0.10 | **0.81** | **0.88** |
| TOMATO | 0.23 | 0.03 | 0.02 | 0.01 | 0.00 | 0.03 | 0.01 | 0.02 | **0.97** | **0.90** |
| STRAWBERRY | 0.34 | 0.36 | 0.07 | 0.57 | 0.69 | 0.60 | 0.80 | **0.86** | 0.13 | 0.24 |
| MELON | 0.97 | 1.00 | 1.00 | - | 1.00 | 0.86 | 1.00 | - | - | - |
| EGG | 0.00 | 0.09 | 0.14 | 0.01 | 0.00 | 0.01 | 0.01 | 0.00 | **0.96** | 0.81 |
| MILK | 0.13 | 0.39 | 0.17 | 0.29 | 0.48 | 0.44 | 0.75 | **0.85** | 0.12 | 0.19 |
| WOOL | 0.09 | 0.63 | 0.14 | 0.62 | 0.65 | 0.62 | 0.61 | 0.66 | 0.06 | 0.14 |
| FERTILIZER | 0.62 | 0.18 | 0.53 | 0.12 | 0.45 | 0.30 | 0.15 | 0.14 | **0.88** | 0.68 |

Premium sale turns by class: strawberry 8% at h0, 62% at m4=1, 6% on other steps with a fresh drop, 24% on other steps without one (mostly h14, h18); milk 3% / 76% / 12% / 8%; wool 2% / 68% / 20% / 11%. The within-day rise for strawberry and milk (h1 0.36-0.39 to h21 0.85-0.86) is the same against the lineage and against everyone else (`tables.md`, Section 2), so it is DSM's own schedule, not a reaction.

**Hour 0 (right after the day-end drop).** The h0 market runs *before* the h0 consumption tick (shops plus town centre) [E]. DSM sells at h0 for fertilizer (49% of its units), strawberry (22%, the flooding case in 2.4), wheat/carrot/tomato (15-16%, room-making, Section 4) and melons carried overnight. It almost never sells milk (6%), wool (4%) or eggs (0%) at h0; those wait for h1, after the tick.

**Within-day pacing** (share of the stock present at h0 that is sold by each hour, days 8-28):

| product | by h1 | h5 | h9 | h13 | h17 | h21 | h23 |
|---|---|---|---|---|---|---|---|
| STRAWBERRY | 0.35 | 0.45 | 0.54 | 0.63 | 0.74 | 0.81 | 0.84 |
| MILK | 0.31 | 0.37 | 0.48 | 0.59 | 0.73 | 0.84 | 0.85 |
| WOOL | 0.28 | 0.39 | 0.50 | 0.61 | 0.70 | 0.79 | 0.81 |
| EGG | 0.07 | 0.20 | 0.20 | 0.24 | 0.31 | 0.36 | 0.98 |
| TOMATO | 0.20 | 0.21 | 0.22 | 0.27 | 0.35 | 0.49 | 1.00 |
| CARROT | 0.27 | 0.41 | 0.49 | 0.62 | 0.64 | 0.69 | 0.99 |

Premium stock is run down almost linearly over the six post-tick markets; about 15-20% carries into the next day. Staples are held and cleared at h22-h23.

**Why these times pay** (quote at the hour vs the day mean, days 12-28): premium quotes saw-tooth, highest on m4=1 hours (wool h1 +36.7%, h5 +15.7%; milk h1 +11.1%, h5-h21 +4.6 to +7.4%; strawberry +3.6 to +8.3%) and lowest at h22-h23 (-4.7 to -14.8%). Staple quotes are flat (within 0.5%) with a slight high at h21-h22. Realised price / same-day mean quote: strawberry 1.040 (opponents 0.958), milk 1.068 (1.004), wool 1.169 (1.030), staples 1.00.

---

## 2. Sell or hold: fitted rules

### 2.1 The decision is mostly deterministic from public state [V9]
When both sides hold stock at an m4=1 turn, DECEM/Vadim sell in the same turn as DSM in 88% (strawberry), 82% (milk), 98% (wool) of DSM's sale turns, but in only 36%, 26%, 16% of DSM's hold turns. Against other teams the same numbers are 48/34, 56/39, 52/19. Two copies of the same code with different private sheds agree, so the rule runs mainly on market state, the clock and own stock.

### 2.2 Rule families, cross-validated (fit on even games, score on odd, and vice versa) [V92]
Decision point = (game, step, product) with S > 0. "exact" = share of points with predicted units == DSM's units. The hold baseline is high because DSM holds on most points.

| product | always hold (exact) | price >= a x base | restore market inventory after own last sale ("demand-preserving") | sell last tick's consumption at m4=1 | best time-gated rule: exact / sell-hold / corr |
|---|---|---|---|---|---|
| WHEAT | 83.0% | 82.9%, corr 0.03 | 24.2%, corr 0.05 | 63.1%, corr 0.07 | h22 lot 13: 84.2% / 84.6% / 0.22 |
| CARROT | 85.1% | 85.1%, corr 0.09 | 19.1%, corr 0.03 | 62.2%, corr -0.01 | h22-23 lot 13: 88.2% / 88.9% / 0.37 |
| TOMATO | 90.8% | 90.7%, corr 0.02 | 16.2%, corr 0.07 | 66.2%, corr -0.10 | h22-23 lot 13: 94.6% / 95.5% / 0.62 |
| STRAWBERRY | 74.2% | 74.2%, corr 0.02 | 47.2%, corr 0.08 | 68.1%, corr 0.28 | ticks h5-h21, S/(slots left+k) capped at 2: 77.0% / 81.8% / 0.23 |
| MELON | 2.5% | 96.1% (a=0.05, i.e. sell all) | 13.4% | 2.5% | sell all now: 96.1% / 97.5% / 0.83 |
| EGG | 92.1% | 91.9%, corr -0.01 | 24.2%, corr 0.09 | 70.9%, corr -0.04 | h22-23 sell all: 95.5% / 96.8% / 0.76 |
| MILK | 82.0% | 82.0%, corr 0.02 | 45.3%, corr 0.17 | 73.7%, corr 0.42 | ticks h17/h21 lot 2: 84.2% / 86.6% / 0.27 |
| WOOL | 76.1% | 75.6%, corr 0.03 | 64.4%, corr 0.28 | 76.9%, corr 0.36 | half of last tick's consumption at m4=1: 81.8% / 87.9% / 0.35 |
| FERTILIZER | 62.3% | 64.7% (a=0.45), corr 0.66 | 58.8% | n/a | hours with P(sell) >= 0.3 + price >= 0.4 base: 70.9% / 74.7% / 0.71 |

Also tested: sell while price >= (1-d) x max quote of the last 24 steps, and sell while price >= own last sale price - D (both worse than "always hold" for every product except melon); a fixed fraction ceil(f x S) at the gate hours (slightly worse than a fixed lot, e.g. strawberry 75.1% vs 76.4%). A pure price threshold always fits to "never sell", because DSM holds and sells at the same price levels: at m4=1 turns it still sells strawberries on 32% of turns when the quote is below 0.2 base (vs 57-71% at higher quotes).

### 2.3 Best simple rule: per-product composite (in-sample, few coarse parameters) [V92]
Assembled from the components in Sections 1 and 2.4; scored on the same decision points (`composite.py`). Scores on even vs odd games differ by at most 2.5 points in exact match (table in `composite_out.md`).

| product | rule | exact | sell/hold | exact on DSM's sale turns | corr per turn | per 4-step window | per day | volume vs DSM |
|---|---|---|---|---|---|---|---|---|
| MELON | sell everything as soon as it is in the shed | 96.1% | 97.5% | 98.5% | 0.83 | 0.94 | 0.98 | 1.04 |
| EGG | h22-23 (and step 718): sell all, else hold | 95.5% | 96.8% | 48.9% | 0.76 | 0.72 | 0.37 | 0.71 |
| EGG | + h0: sell all when the shed holds >= 90 | 93.2% | 94.5% | 49.0% | 0.57 | 0.69 | 0.61 | 1.11 |
| TOMATO | h22-23 sell all | 94.4% | 95.5% | 41.0% | 0.62 | 0.62 | 0.39 | 0.51 |
| TOMATO | + h0 room rule | 92.6% | 94.3% | 42.6% | 0.54 | 0.54 | 0.61 | 1.03 |
| CARROT | h22-23 sell all | 87.9% | 88.9% | 25.1% | 0.37 | 0.30 | 0.06 | 0.30 |
| CARROT | + h0 room rule | 85.5% | 87.3% | 25.3% | 0.41 | 0.52 | 0.40 | 0.71 |
| WHEAT | h22-23 sell all; h0/h1/h2 sell S minus a reserve of n_animals, 2/3 n, 1/3 n | 76.9% | 81.6% | 16.9% | 0.48 | 0.52 | 0.55 | 1.43 |
| STRAWBERRY | h0: min(S, 11 if quote >= 1.3 base else 6) if market inventory rose >= 9 in 24 steps and quote >= 0.7 base and S >= 9; m4=1 from h5: min(S, 2); fresh drop at other hours: min(fresh, 6) | 77.5% | 83.4% | 41.5% | 0.59 | 0.56 | 0.55 | 0.82 |
| MILK | fresh drop: sell it all; m4=1 at h9/h13/h17/h21: min(S, 2); nothing when quote < 0.24 base | 80.8% | 84.8% | 38.1% | 0.45 | 0.58 | 0.73 | 0.93 |
| WOOL | fresh drop: sell it all; m4=1: min(S, ceil(wool consumed at the last tick / 2)) | 84.7% | 91.5% | 58.1% | 0.73 | 0.80 | 0.88 | 1.06 |
| FERTILIZER | hours 0,2,3,7,22,23: sell all while quote >= 40 | 69.4% | 70.7% | 29.0% | 0.72 | 0.70 | 0.57 | 0.55 |

Reading: melons, eggs and tomatoes are reproduced almost exactly; wool well; strawberry, milk, wheat and carrot only in shape (exact quantity on 38-42% of DSM's strawberry and milk sale turns, 17% for wheat; day-level correlation 0.55-0.73, carrot 0.40 with the h0 room rule). Ceiling check with small decision trees on m4=1 sell/hold (`trees.py`, in-sample, features include DSM's own recent sales): depth 3 reaches 0.79 strawberry (base rate 0.62), 0.75 milk (0.51), 0.86 wool (0.63), depth 5 adds at most 3 points. So the premium decision is only ~80% predictable from simple state; DSM probably runs a planner [I].

### 2.4 Premium-good details [V92]

**Lots at m4=1 turns do not scale with stock** (share of turns):

| product | S = 1-2 | S = 3-7 | S >= 8 |
|---|---|---|---|
| STRAWBERRY | hold 21%, 1: 61%, 2: 18% | hold 33%, 1: 19%, 2: 35% | hold 47%, 2: 30%, 3: 10%, 6: 7% |
| MILK | hold 37%, 1: 45%, 2: 17% | hold 53%, 2: 17%, 6: 10%, 3: 8% | hold 45%, 2: 26%, 6: 17%, 9: 7% |
| WOOL | hold 46%, 1: 46%, 2: 8% | hold 37%, 1: 37%, 2: 14% | hold 26%, 2: 33%, 1: 22%, 8: 9%, 4: 9% |

Lots of 3, 6, 9 (milk) and 4, 8 (wool) are whole fresh batches (one cow = 3 or 6, one sheep = 4). When a unit drops a fresh batch off-tick and DSM sells, it sells exactly the dropped amount in most cases: wool 837 of 1,015 turns, milk 502 of 649, melon 528 of 537 (on m4=1 turns: wool 124 of 172, milk 364 of 476, melon 163 of 163).

**Price level.** P(sell | S > 0) at m4=1 by quote/base. Strawberry and wool drop only below 0.2 base; milk is lowest at both extremes:

| product | < 0.2 | 0.2-0.5 | 0.5-1 | 1-1.5 | >= 1.5 |
|---|---|---|---|---|---|
| STRAWBERRY | 0.32 | 0.67 | 0.71 | 0.70 | 0.57 |
| MILK | 0.41 | 0.59 | 0.57 | 0.42 | 0.40 |
| WOOL | 0.40 | 0.80 | 0.78 | 0.73 | - |

**Wool follows town demand** (wool table in `tables.md`, Section 2): at m4=1 turns where the town consumed no wool at the preceding tick (no yarn store, not the h0 town-centre tick) DSM sells on 9% of 1,341 turns; after a 2-unit tick (one yarn store) it sells on 87% of 2,085 turns, 1 unit in 65%; after a 4-unit tick 85%, mostly 1-2 units. Roughly half the consumed amount.

**Strawberry hour-0 dump** (S >= 9 at h0; dinv24 = market inventory now minus 24 steps ago):

| market trend | quote | days | P(sell at h0) |
|---|---|---|---|
| dinv24 >= 9 (flooding) | >= 0.7 base | 306 | **0.88** |
| dinv24 >= 9 | < 0.7 base | 96 | 0.21 |
| dinv24 < 9 | >= 0.7 base | 404 | 0.31 |
| dinv24 < 9 | < 0.7 base | 257 | 0.06 |

h0 lot sizes (S >= 6): 11 in 261 orders (median quote 1.56 base), 6 in 213 (1.23 base), 3 in 27 (0.71 base), 13 in 8 (1.83 base). The composite rule's "11 if quote >= 1.3 base else 6" is a simplification of this. In lineage games the opponent places the same `SELL STRAWBERRY 11` in the same h0 step in 13 of DSM's 19 such orders (others: 10 of 242) [V9].

---

## 3. Order slots and the rival [V92]

- **SELL orders come first.** The first SELL is in slot 0 on 99.3% of the 29,936 turns with a SELL order. Orders placed before a SELL in all 92 games: 304 empty `[]` placeholders, 179 BUY_PRODUCT, 110 BUY_SEED, 74 BUY_ANIMAL, 14 HIRE, 1 BUY_LAND.
- The SELL block is contiguous in 98% of turns. With two or more SELLs (11,034 turns) they are **sorted by lot value (quantity x current quote), largest first** in 80%; fertilizer goes last against every product (91-99% of pairs).
- Typical lists (game 112975969): h0 `[SELL STRAWBERRY 11, SELL FERTILIZER 8, HIRE x8]`, d10 h9 `[SELL MELON 12, BUY_PRODUCT WHEAT 35]`. From day 10 on DSM issues 8.0 HIRE orders per turn at h0, 3.6 at h1, 0.2 at h2, always after the SELLs. BUY_PRODUCT follows the last SELL in 82% of turns that have both, and is the last non-empty order in 94% of the 3,466 turns with a BUY_PRODUCT.
- **Zero-stock SELLs**: about 60 per game (FERTILIZER 1: 26, WHEAT 1: 22, CARROT 9 or 13: 6.5) are issued with nothing in the shed and fail harmlessly. DSM apparently sizes orders from a projected shed that assumes planned unit drops [I].
- **Same-turn rival sales.** Orders of both players are simultaneous, so no within-turn reaction is possible, and in lockstep both get the same quote per unit round [E]. Contested share of DSM's sale turns: lineage 46-89% (strawberry 64%, milk 57%, wool 77%), others 7-41% (strawberry 19%, milk 24%, wool 25%). The rival's SELL is also in slot 0 in 36-100% of contested turns (premium goods 66-80%). Price per unit contested vs alone: strawberry 1.02 vs 1.08 base (lineage), 1.18 vs 1.21 (others); milk 0.72 vs 0.75; wool 0.77 vs 0.79 (others).
- **No measurable reaction afterwards.** DSM never moves its SELL off slot 0. After a contested m4=1 sale it sells again at the next tick about as often as after an uncontested one (others: strawberry 0.72 vs 0.77, milk 0.64 vs 0.67, wool 0.87 vs 0.86). P(DSM sells at m4=1 | rival sold in the previous 3 steps) vs not, against other teams: strawberry 0.56 vs 0.62, milk 0.49 vs 0.52. The higher values in lineage games (wool 0.87 vs 0.28) reflect both sides running the same schedule, not a reaction [V9, I].

---

## 4. Stock levels, shed cap, endgame [V92]

**Daily fill-and-clear cycle** (mean shed contents after the day-end drop at h0; totals at h0 and h23):

| day | WHT | CAR | TOM | STR | EGG | MLK | WOL | FRT | total h0 | total h23 |
|---|---|---|---|---|---|---|---|---|---|---|
| 11 | 37.1 | 0.3 | 0 | 0 | 5.2 | 5.1 | 0 | 15.5 | 63 | 8 |
| 15 | 43.3 | 2.9 | 0.1 | 11.5 | 10.5 | 9.2 | 4.3 | 11.2 | 93 | 4 |
| 19 | 29.5 | 3.1 | 9.5 | 12.9 | 10.6 | 7.5 | 6.2 | 11.6 | 91 | 5 |
| 23 | 27.3 | 6.3 | 11.0 | 17.4 | 9.5 | 7.0 | 4.4 | 8.8 | 92 | 14 |
| 27 | 32.6 | 13.9 | 13.0 | 12.6 | 9.0 | 5.2 | 2.7 | 4.8 | 94 | 8 |
| 29 | 28.5 | 18.4 | 12.2 | 9.1 | 6.9 | 4.2 | 3.5 | 3.1 | 86 | 2 |

- The shed runs at the cap: 83 of 92 games reach 100 at some step (median max = 100), 6.7 steps per game at >= 95. Losses stay small: ~10 units per game discarded at day-end drops (wheat 4.1, carrot 1.8, tomato 1.5, strawberry 1.1, egg 1.0), 17 units in all 92 games at mid-day DROPs.
- **How the cap is managed:** (1) the h22 dump: on days 12-28 the shed holds 24 / 22 / 8 items at h21 / h22 / h23 while units carry 82-84, so without the h22 staple sale the day-end drop would overflow; after it the drop lands at ~92; (2) morning room-making: staple sales at h0 rise with fill, 0 units (fill < 60) to 6.2 (80-89) to 10.3 (95-100), which leaves room for the milk, wool and eggs PLACEd at h1-h2 [I for the motive]; (3) wheat is picked up for feed in the morning (455 units per game from the shed, 39% at h1, 22% at h2, 11% at h0); (4) milk, wool and melons are PLACEd mid-day and sold on arrival; (5) price-gated harvesting keeps unsellable milk, wool and strawberries on the farm (Section 5).
- **Endgame** (units sold per game; the last executed market is step 718 = day 29 hour 22, and no day-end drop happens after it [E]):

| window | WHT | CAR | TOM | STR | EGG | MLK | WOL | FRT | total |
|---|---|---|---|---|---|---|---|---|---|
| day 27 | 36.1 | 18.5 | 14.6 | 10.9 | 12.6 | 11.0 | 8.2 | 3.5 | 115 |
| d28 h0-2 | 25.6 | 12.5 | 1.0 | 1.2 | 0.3 | 2.0 | 1.0 | 0.7 | 44 |
| d28 h3-21 | 20.3 | 10.9 | 12.6 | 8.3 | 3.3 | 10.5 | 5.0 | 1.1 | 72 |
| d28 h22-23 | 9.2 | 6.2 | 4.9 | 0.6 | 11.2 | 0.5 | 0.2 | 2.6 | 35 |
| d29 h0-2 | 26.1 | 14.3 | 1.0 | 0.6 | 0.2 | 0.7 | 1.5 | 3.7 | 48 |
| d29 h3-12 | 1.5 | 1.8 | 0.4 | 4.8 | 0.5 | 2.3 | 1.2 | 0.6 | 13 |
| d29 h13-21 | 42.0 | 27.6 | 14.2 | 7.6 | 2.1 | 6.7 | 1.0 | 6.8 | 108 |
| d29 h22 (step 718) | 3.9 | 3.9 | 7.4 | 0.3 | 11.8 | 0.1 | 0.2 | 0.8 | 28 |

  Day 28 keeps the normal daily shape (morning room-making, paced premium sales, h22 dump); the liquidation happens on day 29. Because the day-end drop of day 29 never runs, units DROP the final harvest mid-day (h13-h21, peak h17 with 21.8 units per game) and it is sold on arrival; eggs and tomatoes keep their h22 slot, now step 718. Stranded at the end (shed plus carried, at final quotes): mean $98, median $17. Mean last sale step: wheat, carrot, fertilizer 717; tomato, egg 718; strawberry 713; milk 712; wool 638 (DSM stops feeding its sheep late in the game, per `notebook_insights.md`).

---

## 5. Harvest timing and drops [V92]

**Crops** (top (age in days, yield) at harvest):

| crop | days | harvests/game | fertilized | typical harvest |
|---|---|---|---|---|
| MELON | d10-11 | 9.9 | 0% | age 10, yield 6 in 913 of 914 harvests. 10 tiles planted on d0-d1 in 86 games (9 in 6), sold d10 (60%), d11 (29%), d12 (10%) |
| WHEAT | d0-9 | 16.3 | 0% | age 2 with 2 (76%): early feed harvest |
| WHEAT | d10-29 | 152 | 67-88% | age 3 with 5 (36-51%), age 4 with 6 (25-27%) |
| CARROT | d10-29 | 56 | 6-55% | age 3 with 3 (unfertilized max) or 4 (fertilized max); age 2 with 2 in 10-17% |
| TOMATO | d10-29 | 74 | 97-99% | every production, yield 2 (ages 8, 9, 10, 11) |
| STRAWBERRY | d10-29 | 111 | 98-99% | every production, yield 2 (ages 10, 12, 14, 16); ~10% one day late |

**Animals:**

| animal | harvests/game | yield at harvest | days between harvests | median hour |
|---|---|---|---|---|
| GOOSE | 76 | 2: 39%, 4: 36%, 3: 17%, 1: 8% | 1 day 46%, 2 days 48% | h9 |
| COW | 57 | 3: 48%, 6: 22%, 2: 19% | 2 days 72%, 4 days 9% | h4 |
| SHEEP | 34 | 4: 60%, 6: 21%, 3: 15% | 3 days 67%, 4 days 12% | h4 |

So: each production is harvested when prices are fine (cow 3 = base 1 plus 2 banked CARE days, sheep 4 = 1 plus 3; geese every 1-2 days), and yields are left to accumulate (cow 6, sheep 6) when they are not.

**Harvest is price-gated.** P(a tile with yield > 0 at h0 is harvested that day), by the product's quote at h0, days 10-28:

| tile | quote < 0.3 base | 0.3-0.7 | 0.7-1.1 | >= 1.1 |
|---|---|---|---|---|
| COW | **0.27** | 0.63 | 0.93 | 0.99 |
| SHEEP | **0.24** | 0.66 | 0.86 | 0.90 |
| STRAWBERRY | **0.53** | 0.73 | 0.85 | 0.90 |
| TOMATO | - | 0.91 | 0.87 | 0.86 |
| GOOSE | - | - | 0.61 | 0.71 |

For cows and sheep the effect holds within days 12-19 and within days 20-28 and at every level of DSM's own stock (`tables.md`, Section 5); for strawberries it appears only late (d20-28: 0.51 vs 0.88). Example: in episode 112879476 (vs ActiveMusyoku) 113-119 strawberry units sat on DSM's plants at h0 of days 22-24 while the quote was $57-89 (0.5-0.75 base) and DSM sold 2 per tick.

**Mid-day drops vs the day-end drop:**

| product | harvested/game | reaches the shed mid-day | via day-end drop | mid-day share | main mid-day drop hours |
|---|---|---|---|---|---|
| MELON | 60 | 53 | 6 | 89% | h9-h12 (sold the same step) |
| MILK | 204 | 125 | 78 | 61% | h1-h2 PLACE right after morning milking, h4-h6 |
| WOOL | 143 | 83 | 60 | 58% | h2-h6 |
| CARROT | 181 | 54 | 124 | 30% | h17-h21 |
| EGG | 212 | 52 | 159 | 25% | h2 PLACE, h19-h22 |
| STRAWBERRY | 218 | 48 | 168 | 22% | h14-h19 |
| WHEAT | 749 | 116 | 695 | 14% | h17-h21 |
| TOMATO | 156 | 21 | 133 | 14% | h19-h22 |
| FERTILIZER | (collected) | 81 | 179 | 31% | h6-h11 |

PLACE (specific items) is used in the morning (h1-h9, peak 16.9 per game at h2); full-inventory DROPs are spread over the day with an afternoon peak (h16-h22, ~4 per game per hour). Most crops ride in unit inventories until the day-end drop; day 29 is the exception (Section 4).

---

## 6. BUY_PRODUCT [V92]

- **Opening (92 of 92 games):** step 0 `[BUY_ANIMAL COW 1, BUY_PRODUCT WHEAT 5]`; step 1 `[SELL WHEAT 1, HIRE x4, BUY_ANIMAL COW 1, BUY_ANIMAL SHEEP 3]`; one `SELL WHEAT 1` + `BUY_PRODUCT WHEAT 1` pair in the same turn at steps 2-5.
- **Wheat:** bought in 92 of 92 games, 183 units per game (median 166, max 413), $6,691 per game, mean $36.6 per unit (min 21, max 48).

| days | units/game | mean price | median requested lot | median own shed wheat before the buy |
|---|---|---|---|---|
| d0-d2 | 17.6 | $28.7 | 2 | 0 |
| d3-d9 | 44.3 | $33.3 | 4 | 0 |
| d10-d12 | 79.1 | $39.1 | 10 | 4 |
| d13-d28 | 41.8 | $38.6 | 13 | 7 |

  By hour: h0 36.6, h1 41.4, h2 15.6, h9 33.8 units per game; almost nothing after h13. The single biggest order is `BUY_PRODUCT WHEAT 35` on d10 h9 (75 games, 5 more at h10), placed right behind `SELL MELON 12`: melon cash buys feed for the herd expansion. Buying is concentrated before DSM's own wheat comes on stream (d0-d12: 141 of 183 units); later DSM is a net seller of wheat (538 units sold per game).
- **Fertilizer:** bought in only 18 of 92 games, 3.5 units per game on average; DSM covers its 241 FERTILIZE actions per game with its own collection (485 COLLECT_FERTILIZER per game) and sells the shed surplus (243 units per game).

---

## 7. Re-implementation sketch [I]

```
each step t: h = t % 24, m4 = t % 4
S[x] = shed[x] + units' planned DROP/PLACE of x this step        # sell drops in the same step
fresh[x] = planned drops of x this step
SELL block in slot 0, sorted by qty * quote descending; then HIRE / BUY_SEED / BUY_ANIMAL; BUY_PRODUCT last

MELON:       sell S
EGG, TOMATO: if h in (22, 23) or t == 718: sell S;  if h == 0 and shed_total >= 90: sell S
CARROT:      same as tomato
WHEAT:       if h in (22, 23): sell S;  if h in (0, 1, 2): sell S - reserve, reserve = n_animals * (1, 2/3, 1/3)[h]
FERTILIZER:  if h in (0, 2, 3, 7, 22, 23) and quote >= 40: sell S
STRAWBERRY:  if h == 0 and inv_now - inv_24_steps_ago >= 9 and quote >= 0.7*base and S >= 9:
                 sell min(S, 11 if quote >= 1.3*base else 6)
             elif m4 == 1 and h >= 5: sell min(S, 2)
             elif fresh > 0: sell min(fresh, 6)
MILK:        if quote < 0.24*base: hold
             elif fresh > 0: sell fresh
             elif m4 == 1 and h in (9, 13, 17, 21): sell min(S, 2)
WOOL:        if fresh > 0: sell fresh
             elif m4 == 1: sell min(S, ceil(wool consumed at the last tick / 2))
HARVEST:     melon at age 10 (6); wheat age 3 (5, fertilized) or 4 (6); carrot age 3;
             tomato and strawberry every production (fertilized, 2 each);
             cow every 2 days (3), sheep every 3 days (4), geese every 1-2 days (2 or 4);
             mostly skip cows, sheep and strawberries while the quote < 0.3 base
             (DSM then harvests ~25% of eligible cows and sheep, ~50% of strawberries)
DROPS:       milk and wool PLACEd at h1-h6 right after the morning harvest and sold at once;
             melons dropped on harvest; day 29: drop everything by h21
BUY:         feed wheat only when the shed has none; one big buy after the melon sale (d10);
             no fertilizer buying
```

## 8. Limits

- Melons, eggs, tomatoes and wool are reproduced well; strawberry, milk, wheat and carrot only in shape. Any rule tested explains at most ~80% of premium sell/hold decisions and ~40% of exact strawberry and milk lot sizes. DSM very likely plans sales from projected stock and the clock rather than from a closed-form threshold [I].
- The composite rules in 2.3 are in-sample (parameters read off pooled tables); the rule families in 2.2 are cross-validated. Even/odd halves agree within 2.5 points.
- Lineage statements ([V9]) rest on 9 games. Everything else pools 92 games (about 66,000 DSM turns).
- Harvest gating: the price effect is verified; whether DSM keys on price, on projected unsold stock, or on labour priorities cannot be fully separated [I].

## Files (research\dsm_sales\)

| file | purpose |
|---|---|
| `replay_dsm.py` | exact re-simulation of the 92 games with per-step observations, slot-tagged market log, unit-action log, day-end drops; writes `cache\dsm_replay.pkl.gz` (~12 MB, 17 s) |
| `common.py` | cache loader, engine price function, town demand, per-step sold/requested/slot arrays |
| `analyze.py` | all descriptive tables: `analyze.py all > tables.md` |
| `rules.py` | rule families with even/odd cross-validation: `rules.py > rules_out.md` |
| `composite.py` | composite per-product rules and stability check: `composite.py > composite_out.md` |
| `trees.py` | numpy decision trees for the premium sell/hold ceiling: `trees_out.md` |

Run with `.venv\Scripts\python.exe research\dsm_sales\<script>.py` (analysis scripts need `cd research\dsm_sales` or that folder on the path).
