# Public notebook review for the SE planning layer (2026-09-25)

Goal of the review: find what is usable for our planned layer on top of cha22 (buy SE around day 10 to 12 with idle cash, hire extra hands, grow strawberry/tomato or animals by shop demand, own scheduler).

## 0. Files and method

- 13 notebooks pulled with `kaggle kernels pull <ref> -p gold\public\nb\<slug>`; all pulls succeeded (no fallback to `kernels output` needed).
- Embedded agents were decoded without running notebook code (ast + base64/b85 + gzip/zlib/lzma) into `gold\public\nb\<slug>\extracted\`. Every sha256 matched the value the notebook asserts.
  - Pioneers: host, donor and extra layers split into `payload_more_wheat.py`, `payload_demand_new.py`, `payload_pioneers_candidate3_layers.py`.
  - Fieldcraft: `extracted\main.py` (41 KB compact code) + `extracted\mirror_plan.py` (route data).
- cha22 reference below = `gold\public\abhinav0370__cha22-agent\from_tar\main.py` (sha 127ed3e6), line numbers from that file.

## 1. Big picture

1. Lineage. Everything except Fieldcraft, agent-lab and the selection harness is the same Tschinkel "v9/3" route-replay chassis as cha22 (identical header "Kaggriculture submission v9/3: public V39 ... RACEPX, RACE, COURIER, CARROT, HERD"). Fieldcraft replays the same yhay81/Ahmed V43 shop-pair tapes but in its own compact code with its own planning modules.
2. cha22 already contains most of what these notebooks sell as upgrades (function bodies compared by AST hash):
   - V219 prvsiyan tomato SE investment (lines 1227 to 1462) and V219SKIP crew skip (6084).
   - V233 six-sheep SE investment (1948 to 2068) plus v9/4 VE day-11 commit (3975) and VT last two days (4039).
   - Pipe16 opening port (6341, mode EarlyCycle plus OMW delayed harvest).
   - shiiin9 Layer D order search (F4, 7173 to 7257): `_cxd_candidates`/`_cxd_reorder` byte-identical to the order-book notebook.
   - EXP402 seed cap and EXP410 fertilizer guard (7260 to 7365): identical to Ahmed V56.
3. Not in cha22 and relevant: shiiin9 tomato value gate, V57 funding-order fix, Fieldcraft InputHand / SETomato7 sizing / D29 endgame crew / FEED_ECON, Pioneers FlowLayer market simulator and cash RESERVE.
4. Live scores of the repackaged "2965 / Shepherd / Pioneers / population" agents (1731 to 2291) are all below cha22 (about 2500 to 2588), so their head-to-head tables (often 1 or 2 seeds) are not evidence.

## 2. Per notebook

### 2.1 haideptry/the-2965-master-hybrid-engine (live 2214.9)
- (a) Repackage of "V59 Harvest Ledger": V56-level base + shiiin9 Layer D + cha22's own layers ported under a `_v7_` prefix (shield-milk, MPX, CXD, E402, MERGE, IG) + a feed guard `v7_hr_agent`. Cha22 derivative, nothing structural.
- (b) Claims (md cell 6): "+$274/game vs cha22 (seed 101)", "92% vs V56/V57". One seed each, contradicted by live score. The header says "keep V57 farming" and "keep all purchase and hire slots fixed", but the file has neither V57's EXP437 filter nor its seed-float trim, and `_v7_cxd_candidates` (main.py line 7102) is shiiin9's unfixed generator, so purchases can still move earlier. No new mechanic.
- (c) Low. Everything in it is either already in cha22 or in V57.

### 2.2 haideptry/the-shepherds-ledger-herd-safe-sovereign (live 2088.5)
- (a) Pipe16/V56-style base + shiiin9 Layer D and tomato gate + Dmitrii HerdSafe pieces + cha22 layers again (`_hs4_*`). Cha22 derivative.
- (b) Mechanics, all small:
  - `herdsafe_risk_feed_agent` (main.py line 7053): when the farmer picks up wheat, take up to 2 extra units if an animal on today's remaining tape feed route already has `consecutive_unfed >= 1` (keeps 2 spare in shed).
  - `opening_liquidity_agent` (7031): step-0 wheat trade BUY 8 / SELL 3.
  - `_hs4_t4_preempt_apply` (7311): sell next turn's planned MILK/WOOL/STRAWBERRY lot now with a credit ledger. Its "lead 2" branch is dead code (`_HS4_T4_OPP_PREEMPT` is never set True).
- (c) Low. The feed idea is trivial for our own scheduler (track `consecutive_unfed`).

### 2.3 hanifnoerrofiq/pioneers-of-kaggle-town (2290.9) and -candidate-2 (2129.9)
- (a) Single code cell. Host = "More Wheat" (all V56 functions + shiiin9 Layer D + shiiin9 `_cxtb_*` tomato gate + `rescue_agent`), donor = a newer tetsutani "demand-preserving" build; `agent` = host then donor `_v336_reorder`. Candidate-2 adds `FlowLayer(flow=False, reserve=True)` and `QuietOpening(6,5)`; its entry is `pioneers_candidate3_agent`.
- (b) New mechanics:
  - `_v333rxd_model_orders` / `_v336_reorder` (payload_demand_new.py lines 7376 to 7469): robust market-list ordering. Scores each permutation against 4 rival models (rival list = ours, sells first, sells last, sells reversed), takes the worst case, ties broken by the mirror model. Same funding-order hole as cha22's CXD (no V57 filter).
  - `_e343_yx_*` (payload_demand_new.py 5284 to 5455): V233 sheep variant. Day-11 commit hours 2 to 12 requires cash >= budget + 3000 + everything the tape itself still spends through day 12 (`_e343_yx_tape_cost`); days 28 to 29 feed only animals that produce tonight or have `consecutive_unfed >= 1`, skip CARE, buy no wheat on day 29, no hands on day 29 when no sheep holds wool. Cha22 VE/VT already do most of this.
  - `FlowLayer` (payload_pioneers_candidate3_layers.py, candidate-2 only): for MILK/WOOL/STRAWBERRY/MELON a 4-turn-tick simulation to season end picks a sell threshold P under 3 rival behaviours (flow, hold, mirror; score 0.5 min + 0.5 mean), with exact price curves, current drain + expected future unlocks (`_UNLOCK_E`), own and rival supply from public tiles (`_supply_schedule`: cow/sheep about 1 unit/day, strawberry 1.5 per yield at ages 10/12/14/16, melon 6 at age 10) and rival hidden stock tracked from tile-yield drops and market-inventory deltas (`_track`). Disabled in candidate-2 (flow=False).
  - `FlowLayer._reserve`: cash for tape HIRE/seed/animal/land purchases over the next 24 turns (hires priced by fib); on days 0 to 2 drops seed buys that would eat hire cash (loss in episode 112433264).
  - `QuietOpening(buy=6, sell=5)`: step-0 wheat trade chosen to maximise worst-case step-2 margin over observed rival openings.
- (c) Medium. `_supply_schedule` + `simulate` is the most complete public demand/supply projector for premium goods; reusable to price "how many strawberries / cows can this town absorb". The rest is opening/order polish.

### 2.4 nihilisticneuralnet/kaggriculture-population-robust-economy (1731.1, 51 votes)
- (a) No markdown. Comment-stripped v9-chassis agent (has v13 `_v92_*` PREDICT, V219, V233). Cell 3 `VALIDATION`: 6 ties vs "exact_2945" (behaviourally that agent) and 0 of 6 vs "cha22_2500" (mean -1772).
- (b) Nothing new.
- (c) Low.

### 2.5 hakdevelopment/kaggriculture-2887-score-fieldcraft-agent (claims 2887)
- (a) 2887.4 is a historical rating of submission 56258004 (15 Sep). Code cell 4 holds minified `main.py` + `mirror_plan.py` (base tape + per-shop-pair patches, same `_PAIRS` map as cha22 routes 100 to 128). Own compact controller, not the v9 chassis. Local test here: loses to cha22 10 W / 70 L (-1543 per game, 40 seeds x 2 seats).
- (b) The most relevant code in the whole set; each module is a small class wrapping the tape policy:
  - `SETomato7` (main.py line 422): day 18 hour 1, if money >= 5500 and `deficit_by(shops, 27) >= MIN_DEFICIT (300)`: BUY_LAND + 14 tomato seeds. At hour 2 sizes the garden: 16 tiles / 4 late hands if deficit >= 400 (or rival owns 4 quadrants and deficit >= 400), else 12 tiles / 3 hands. Tiles = SE sorted by distance from the shed. Crew: 2 on plant day, 1 per day until production, then 3 to 4 (one fewer on day +8). Buys fertilizer for all tiles on days +7 and +10. Harvest at >= 3 units; deliver at 12 carried or by hour 22; puts `SELL TOMATO 999` first whenever the shed has tomatoes.
  - `deficit_by(shops, day)` (417): town centre 1/day + 6/day per PIZZA_SHOP or FARMERS_MARKET since its unlock (uses unlock day 3(k+1)-1, one day early vs engine).
  - `InputHand` (494 to 650): days 12 to 28, hours 1 to 3, after the tape's last hire of the day, hire up to 2 extra hands that buy FERTILIZER and carry it to the tape's own WHEAT/CARROT tiles. `forecast` replays the tape to find each tile's future WATER and HARVEST steps; `gain` = extra units from waterings inside the fertilized window; `path_beam`/`plans_joint` beam-search a tile route per hand. Accept a hand only if value >= 1.5 x cost + 50 and money >= cost + 3000 (cost = fertilizer + fib(hires_today + k)), shed <= 95. `surplus` sells wheat above a 60 reserve and trims the shed to 99 at hour 23.
  - `SheepPen` (664): V233 clone (day 12, 2 yarn stores, wool >= 220, wheat <= 45, 6 sheep, reserve 3000) with `lean` (1 hand when nothing to harvest) and `endgame` (no hand when no production left); blocks the garden when it commits. `_cow_gate` (798) exists for a cow pen (3 milk shops in first 4, milk >= 150, wheat <= 45) but is not wired in.
  - D29 endgame crew (`_d29_route` 133, `plan` 239, D29 = 9): at step 696 drop the tape's HIRE/BUY buys, hire 7 + 2 hands, send farmer + 9 hands to the most valuable harvestable tiles outside SE (water in-window wheat/carrot first for +1), deliver by step 718. Gated on the garden being active.
  - FEED_ECON (`_f_feed` 838, `_f_bonus_cost` 812): skip a tape FEED (days 10 to 28, before hour 22) when bonus at stake x (product price + 5) x 1.25 < wheat price, the animal was fed yesterday and the tape feeds it tomorrow; GRAIN_OUTLET (`_f_outlet`) sells the saved wheat.
  - `plan` (221): species swaps by first shops (cow to sheep on day 6/7 with yarn stores, goose to sheep days 10 to 11, sheep to cow days 9 to 10 with 2 milk shops and no yarn). Cha22 HERD/HERD2/COWSWAP cover this.
  - `order_rows(quote=...)` (381): sorts adjacent sells by `exposure` = revenue lost if 8 rival units land first. Same idea as our v6 sell sort.
- (c) High. Weak as a whole agent, but InputHand, SETomato7 and D29 are exactly "extra hands and land on top of a tape" and they are small. Ablations below show large effects.

### 2.6 yangkuangou/kaggriculture-agent-lab-copy-replay-compare
- (a) Tutorial: stdlib wheat starter (cell 2), seat-swapped paired evaluator (cell 4), bank/price plot (cell 6).
- (b) Correct basics only (units act before the market; harvest goes to carried inventory, shed at end-of-day drop).
- (c) Low.

### 2.7 bardiabahadori/kaggriculture-agent-selection-engine-traps
- (a) Not an agent: selection harness (cell 3) + replay analysis (cell 6); author peaked at 2666 using others' agents.
- (b) Claims:
  - Traps (md cell 1): last-callable entry point; engine 1.32.6 vs 1.32.7; config defaults; module globals must be fresh per game. All valid in principle.
  - His own config check is wrong for the live server: CFG sets `townCenterSellInterval: 12`, but live replays (e.g. gold\replays\113030840.json) and the 1.32.7 JSON use 24. "starter vs pass must be [3509, 3000]" does not reproduce: 1.32.7 seed 0 gives [3421, 3000] (deterministic), his CFG gives [3443, 3000].
  - md cell 5: same agent, same production, 183,898 vs 29,521 bank because strawberry/milk prices were 236/278 vs 3/1; "premium demand 3 gave 42k, 13 gave 134k". Shop draw sets premium value.
  - "Margin below about +5000 does not move rating" is anecdotal (rating counts wins only).
- (c) Medium as a caution: extra premium production must be gated on demand. Do not copy his CFG.

### 2.8 sunil123kumar/kaggriculture-idle-workers (Pipe-16) and lynnsakurai/farmer-john-and-the-idle-seller
- (a) Pipe-16 = Tschinkel v13 + Dmitrii HybridOpening: day-0 idle hand plants a temporary wheat at (2,4), steps 2 to 6, 29, 49 to 57 rewritten. Farmer John = same + E402/E410 + opening guard `_gi_guard_opening` (main.py 6778: at step 29 build the pasture if the temp wheat is missing) + `_gi_gate_delayed_cycle`.
- (b) Claims: 318-32 vs 7 rivals; days 0 to 2 cost $50 to 100 vs rivals using idle hands. md cell 0 of Farmer John gives the seed cap formula q' = min(q, max(0, R - (S - C))) and fertilizer skip rule (F >= d+2, or predicted harvest unchanged). All already in cha22 (EarlyCycle opening, E402, E410); the guard only matters if the step-5 PLANT fails, which is near impossible in EarlyCycle.
- (c) Low. General lesson (redirect PASS actions) has little room after day 10: see section 4, tape hands PASS only 0 to 12% of actions from day 10.

### 2.9 shiiin9/your-market-list-is-an-order-book (47 votes)
- (a) Ahmed V55 byte-for-byte + 4 constants + Layer D (exact lockstep order search) + tomato gate T-B. V55 is the same lineage as cha22.
- (b) Claims and mechanics:
  - All three changes together: 191-53 to 280-0 vs 7 agents of 20 to 21 Sep, +758/game (md cell 0, cell 3 data). Layer D (md cell 4, `_cxd_reorder`) alone is described as +124 to +133/game against every opponent (md cell 11). Already in cha22 (F4) but without the funding-order filter (see 2.10).
  - Tomato gate (md cell 12; main.py 6669 to 6818: `_cxtb_their_supply`, `_cxtb_expected_revenue`, `_cxtb_qualifies`, wrapper `_v219_qualifies`). Replaces V219's "3 tomato shops and price >= 70" with a projected revenue: from day 18 drain inventory by 1 + 6 x tomato shops - 2.4 per day (+0.25 expected tomato shop at each future unlock), add 0.75 units/day per rival tomato tile from planted_day + 8 to season end, then price our 20 units/day on days 26 to 29 with the engine curve. Commit only if revenue >= 9000. Constants measured on 96 replayed games (projection error < 25 units over 8 days).
  - Verified here with the engine: TOMATO 80 units fetch 18,355 at inventory 9,600, 3,599 at 10,000, 1,653 at 10,200, 80 at 10,600. Minor: the code expects the 7th shop on day 22; engine unlocks it on day 21.
  - "Forcing the investment on regardless costs 34 wins in 119 games"; threshold picked on live games because replays favoured a lower one that then lost 6 net in the mirror.
  - Constants: `_V92_P_EVERY` 3 to 2, `V9_RACE_DEFAULT` 41 to 44, `_OR2_SLOT_MARGIN` 20 to 8, `_CA_MARGIN` -5 to -15, each worth 12 to 24 wins of 280. Cha22 has RACE 44, OR2 12, CA -20 and no `_v92` PREDICT.
- (c) High. The gate's projection is the right template for any SE crop decision, and the "forced investment loses" result is the key warning for our plan.

### 2.10 ahmedberatozer/kaggriculture-v57-funding-order-invariant and -v56-smarter-seeds-and-fertilizer
- (a) V56 = Pipe16-style base + E402 seed cap + E410 fertilizer guard (both already in cha22, identical). V57 = V56 + EXP437 + busyaprime seed-float trim + fertilizer-buy knockout after step 696.
- (b) EXP437 (V57 main.py 6955 to 6973): shiiin9's `_cxd_candidates` refills the non-sell slots with the fixed orders in order, so when a SELL moves later a HIRE/BUY_SEED/BUY_ANIMAL/BUY_LAND can move earlier than the sale that funds it and then fails silently. V57 filters any candidate that moves a fixed order earlier: 320 games, 30 better, 290 equal, 0 worse, +$9.89. V57's CXD also only runs from step 216 and only vs detected clones; cha22's runs from step 0 on every opponent. In our build the order-slot layer moves buys after sells from step 288, so the exposure is steps 0 to 287, where cash is tightest.
  - `_33_seedfloat_agent` (6877): from step 648 cap carrot/wheat seed buys to what route 2 still plants (+2 wheat hedge).
- (c) Medium. EXP437 is a 15-line drop-in for cha22 lines 7184 to 7193, and any SE layer that adds BUY_LAND/BUY_SEED/HIRE must keep the same invariant.

## 3. Engine facts that matter for the plan (checked in kaggle_environments 1.32.7 source)

1. Land order is fixed NE, SW, SE (1000/2000/4000). All 41 cha22 route tapes buy land at steps 150 and 265 (NE day 6, SW day 11 hour 1); none buys SE or plants tomatoes. An extra BUY_LAND before step 265 buys SW and turns the tape's own step-265 purchase into SE; buy after 265 or budget the order.
2. Hands vanish every night; hire cost = fib(hires_today) (1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233). Cha22 tapes hire 9 to 12 hands every day from day 10, so the first extra hand costs 55 to 144 per day, the second 89 to 233, the third 144 to 377. Three extra hands for 18 days is roughly 5k to 14k.
3. Unit actions resolve before the market each step: land, seeds and hires bought at step t are usable at t+1 (new hands spawn on shed-access tiles, (5,5) is inside SE).
4. Atomic PLANT: if a turn's PLANT requests for a crop exceed seeds in stock, every PLANT of that crop fails that turn, including the tape's own. Extra planting must reserve seeds against the tape's same-turn plants.
5. Ongoing crops (tomato, strawberry) produce at the nightly refresh whether or not watered that day. Watering only prevents death (2 consecutive dry days; the planting day counts as dry, so water on planting day) and enables the fertilizer +1. Crews can water every other day unless fertilizing (V219SKIP uses this). Strawberry yields at planted_day + 10, 12, 14, 16, so plant by day 13 for all 4 yields; tomato at +8 to +11.
6. Animals produce base 1 per cycle without feeding. Fed and cared days add a bonus consumed only on a fed production day (reset otherwise). 2 consecutive unfed days and the animal escapes. Holding caps: goose 4, cow 6, sheep 6.
7. BUY_ANIMAL lands in the shed (counts toward the 100 cap); BUY_PRODUCT only WHEAT and FERTILIZER; sales at price 1 do not raise market inventory.
8. Shops: one draw every 3 days (days 3 to 24, 8 max, uniform over 8 types with replacement). Each instance drains 1 unit per 4 steps per product (2 for single-product YARN_STORE and PET_CAFE); town centre 1 per day (live config 24). Tomato buyers: PIZZA_SHOP, FARMERS_MARKET only. Strawberry: BRUNCH_SPOT, ICE_CREAM_SHOP, SMOOTHIE_SHOP, FARMERS_MARKET.
9. Price sensitivity (engine curve): 100 units sold starting at I0 fetch strawberry 3,847 (price 1 after about 62 units), milk 6,205, wool 7,969; starting 200 below I0 they fetch 22,256 / 26,613 / 24,288. Extra premium output only pays where shops keep inventory well below I0.

## 4. Local measurements from this review (scratchpad scripts, not saved in repo)

- Fieldcraft vs cha22, seeds 1000 to 1039, both seats (80 games): 10 W / 70 L, mean -1543.
- SE usage in the same 80 games: cha22 V219 tomato commits 14, V233 sheep 4 (22.5%, matches the ~23% live estimate). Fieldcraft garden 18, pen 4, InputHand hired in 76.
- Fieldcraft ablations (same 80 games, paired against the full agent):

| variant | W/80 | margin | vs full: margin | vs full: own cash |
|---|---|---|---|---|
| full | 10 | -1543 | 0 | 0 |
| no InputHand | 10 | -3333 | -1789 | -1377 |
| no SE garden | 6 | -3318 | -1775 (only 18 games change) | -518 |
| no SheepPen | 8 | -2220 | -677 (4 games change) | +300 |

- Garden split: in the 18 firing games Fieldcraft own cash +2303 and cha22 cash -5585; in the 14 of them where cha22's V219 also committed, own +1359 and cha22 -8044. The SE tomato decision is mostly a race for one shared, thin demand pool: being in it denies a cha22 clone's V219 more than it earns.
- Cha22 tape hand PASS share from day 10: 0 to 12% (median per day), so little idle tape labour to redirect.

## 5. Ranked usable ideas for the planning layer

1. Fieldcraft `InputHand` (main.py 494 to 650): extra hands + market fertilizer on the tape's own wheat/carrot, value gate 1.5 x cost + 50, cash reserve 3000. Worth +1789 margin/game in Fieldcraft vs cha22, fires in 95% of games. Cha22 has only FERT (carried animal fertilizer from day 16). Port and A/B on cha22 first; it needs no land.
2. SE crop decision as a projected-value gate, not a shop count: shiiin9 `_cxtb_expected_revenue` (order-book main.py 6740) or Fieldcraft `deficit_by` + `SETomato7` sizing (422). Include rival tiles and a clone's V219 (day 18, same gate) in the projection; forced investment lost 34 of 119 games.
3. Reuse cha22 V219/V233 as the executor skeleton (hire after the tape's last hire of the day, new actor indices = len(hands)+1..., targets per hand, deliver by hour 22/23, `_shadow_terminal` abstain) rather than writing a new worker system; generalise targets from 10 tomato tiles / 6 sheep to a strawberry or cow plan.
4. Keep the funding-order invariant: port V57 EXP437 into cha22 `_cxd_candidates` (7184) and apply the same rule to any BUY_LAND/BUY_SEED/HIRE the planner adds; budget like `_e343_yx_tape_cost` (tape spend through tomorrow) + 3000 reserve.
5. Labour and feed economics from the engine: water ongoing crops every other day, feed only where the bonus is worth a wheat or the animal is at `consecutive_unfed == 1` (Fieldcraft `_f_feed`, E343 YX worker), and cost hires with fib(hires_today + k).
6. Fieldcraft D29 crew (`_d29_route` 133): 9 extra hands on day 29 to harvest and deliver everything by step 718; test separately as an end-game add-on (it is gated on the garden in Fieldcraft).
7. For sizing strawberry/cow expansions, Pioneers `FlowLayer._supply_schedule` + `simulate` (candidate3 layers) give a ready 3-rival-model revenue projection with exact price curves.
