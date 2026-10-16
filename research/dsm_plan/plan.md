# DSM production plan, reverse-engineered from 92 live games

Team 42 research note, 2026-09-24. Research only: nothing was submitted, nothing under `tools/`, `submissions/` or `~/.kaggle` was touched.

**Data.** `data\games\dsm.jsonl.gz`: 92 games, all played by one DSM submission (56518845, rated about 3068), against 73 different opponents (DECEM 5, Kaggledew Valley 4, Majkel1337 3, ...). DSM won 92 of 92. Median final bank $110.2k against $90.9k; median margin +$20.6k.

**Method.** Every game is replayed through the real engine (kaggle-environments 1.32.7), the same way `tools\econ.py` does it, with hooks that log each DSM unit action together with the tile before and after it, every executed market unit, hire and land purchase of both sides, and the full tile grid at the end of every day. The local final money equals the server reward in 92 of 92 games, so every number below is exact, not estimated.

**Tags.** `[92/92]` = true in every game; `[n/92]` = true in n games; "fit" = least-squares fit over the 92 games (R² and RMSE given). "End of day d" = the grid after the end-of-day refresh of day d (weeds, escapes and productions already applied). Coordinates are `(x, y)`, `tiles[y][x]`; the shed-access tiles are (4,4), (5,4), (4,5), (5,5).

**Reproduce.** `.venv\Scripts\python.exe research\dsm_plan\run_all.py` (about 1.5 minutes). It rebuilds `cache\` and every table in `out\`. Section `n` of this note is produced by the script named in its heading.

---

## 0. The plan on one page

| # | Rule | Support |
|---|---|---|
| 1 | **Day 0 is a fixed tape**: 2 cows + 3 sheep on pastures next to the shed, 4 hands hired at step 1, 6 melons and 9-10 wheat planted in NW, cash spent down to $0-9. | [92/92] identical apart from the step-13 seed batching (56/36), one move at step 22 (68/24) and one game at steps 20-21 |
| 2 | **Days 1-5 finish NW**: 4 more melons on day 1 (10 in total), the 9-10 day-0 wheat tiles harvested at age 2-3 on days 2-3 and replanted with 10 strawberries. NW at the end of day 5 = 10 strawberry, 10 melon, 2 cow, 3 sheep. 5-6 hands a day, all fertilizer sold. | same NW grid in 86/92; same composition in 86/92 |
| 3 | **Land on cash events**: NE on day 6 hour 5 (first wool), SW on day 9 hours 1-7 (second wool), SE on day 10 hours 12-18 (first melon harvest). All three quadrants every game. | [92/92] |
| 4 | **Animals go next to the shed** and total about 23 by day 12 (p10-p90 21-26), split by shop demand. Sheep = 3 + about 8/7/7/4/2 per YARN_STORE unlocked on day 3/6/9/12/15 (R² 0.97). Cows = 5 + about 4/4/2/1 per PIZZA/ICE_CREAM/SMOOTHIE unlocked on day 3/6/9/12 (R² 0.92). Geese fill the rest, with more for BAKERY/BRUNCH. After day 12 only a few animals are bought (a cow on day 15 or 18 in 6-7 games, extra sheep for a late yarn store). | fits over 92 |
| 5 | **Crops go on the periphery**. Strawberries peak around day 14 at `13.1 + 8.7 x` (x = #BRUNCH+#ICE+#SMOOTHIE+#FM among shops 1-4, R² 0.90). Tomatoes peak around day 19 at `13.9 + 7.2 x` (x = #PIZZA+#FM among shops 1-4, R² 0.70). Wheat is the filler at 20-31 tiles. Carrots take over from day 19 and peak around day 26 (about +8 tiles per PET_CAFE). Melons only on days 0-1. | fits over 92 |
| 6 | **Labour**: 4-6 hands on days 0-5, 8 on day 6, 9 on days 7-8, 10 on day 9, then 11-12 a day (8 HIREs at hour 0, the rest at hour 1). About 299 hires and $6.8k a season. | [92/92] |
| 7 | **Cash**: spent down to about $0 every day until day 10, then only accumulates. No reserve is kept. | median daily minimum $0-107 on days 0-10 (day 5: $380) |
| 8 | **Fertilizer**: collected from every animal every day (97-100%); FERTILIZE wheat and carrot once at age 2 (before watering), tomato at ages 7 and 10, strawberry at ages 9 and 13. Melon never. About half is used (241 a game) and half sold (243 a game, $13.0k). Never bought (3.5 units a game). | 92 games |
| 9 | **Animal care**: FEED and CARE on the same animal-day (98%). Always fed on its production days; on other days fed only when product price / wheat price is above about 2-3. Feeding stops after the last production that can still be sold: cows and geese last fed on day 27, sheep on day 26. | 92 games |
| 10 | **Stop dates**: last strawberry seed bought on day 13 (median), last tomato seed on day 18, last carrot seed on day 26, last wheat seed on day 27. Everything is sold by step 718; about $400 of stock is left unsold at base prices. | [92/92] |

---

## 1. Opening (`opening.py` -> `out\opening.md`, `out\opening_steps.md`)

### 1a. Day 0: the exact tape (steps 0-23)

`n` = games whose full action (farmer + hands + market) equals the modal one. Hands appear one step after the HIRE; hired hands spawn on (5,4), (4,5), (5,5), (4,4).

| step | n | market orders (sent) | farmer / hand1 / hand2 / hand3 / hand4 | tile changes |
|---|---|---|---|---|
| 0 | 92 | BUY_ANIMAL COW 1, BUY_PRODUCT WHEAT 5 | PASS | |
| 1 | 92 | SELL WHEAT 1, HIRE x4, BUY_ANIMAL COW 1, BUY_ANIMAL SHEEP 3 | PICKUP COW | |
| 2 | 92 | SELL WHEAT 1 | BUILD_PASTURE / PICKUP SHEEP / PICKUP SHEEP / PICKUP COW / PICKUP SHEEP | pasture (4,4) |
| 3 | 92 | SELL WHEAT 1, BUY_PRODUCT WHEAT 1 | PLACE COW / N / N / N / W | cow (4,4) |
| 4 | 92 | SELL WHEAT 1, BUY_PRODUCT WHEAT 1 | PICKUP WHEAT 3 / W / W / N / BUILD_PASTURE | pasture (3,4) |
| 5 | 92 | SELL WHEAT 1, BUY_PRODUCT WHEAT 1 | FEED / BUILD_PASTURE / W / N / PLACE SHEEP | pasture (4,3), sheep (3,4) |
| 6 | 92 | BUY_SEED MELON 2, BUY_PRODUCT WHEAT 1 | W / PLACE SHEEP / BUILD_PASTURE / PASS / CARE | sheep (4,3), pasture (2,4) |
| 7 | 92 | - | FEED / CARE / PLACE SHEEP / W / W | sheep (2,4) |
| 8 | 92 | BUY_SEED MELON 2 | W / S / W / BUILD_PASTURE / W | pasture (4,2) |
| 9 | 92 | - | FEED / PICKUP WHEAT / N / PLACE COW / N | cow (4,2) |
| 10 | 92 | - | CARE / CARE / PLANT MELON / N / PASS | melon (1,3) |
| 11 | 92 | BUY_SEED MELON 2 | W / N / WATER / PLANT MELON / N | melon (4,1) |
| 12 | 92 | BUY_SEED WHEAT 2 | PLANT MELON / FEED / N / WATER / N | melon (1,4) |
| 13 | 56 | SELL WHEAT 1, BUY_SEED WHEAT 2 (36 games: WHEAT 5) | WATER / N / PLANT MELON / W / PLANT WHEAT | melon (1,2), wheat (1,1) |
| 14 | 92 | BUY_SEED WHEAT 1 | PASS / W / WATER / PLANT MELON / WATER | melon (3,1) |
| 15 | 92 | BUY_SEED WHEAT 1 | PASS / PLANT MELON / N / WATER / N | melon (3,2) |
| 16 | 92 | BUY_SEED WHEAT 1 | PASS / WATER / W / W / PLANT WHEAT | wheat (1,0) |
| 17 | 92 | BUY_SEED WHEAT 1 | PASS / W / PLANT WHEAT / PLANT WHEAT / WATER | wheat (0,1), (2,1) |
| 18 | 92 | BUY_SEED WHEAT 1 | PASS / PLANT WHEAT / WATER / WATER / W | wheat (2,2) |
| 19 | 92 | BUY_SEED WHEAT 1 | W / WATER / S / N / PLANT WHEAT | wheat (0,0) |
| 20 | 91 | BUY_SEED WHEAT 1 | PLANT WHEAT / W / PLANT WHEAT / PLANT WHEAT / WATER | wheat (0,2), (0,4), (2,0) [91] |
| 21 | 91 | BUY_SEED WHEAT 1 | WATER / S / WATER / WATER / PASS | |
| 22 | 68 | - | S / W / S / S / S (24 games: S x5) | |
| 23 | 92 | - | S x5 | |

Notes [92/92]:
- The 1-unit wheat seed orders of steps 14-21 execute only while cash is at least $10. The executed share per step is 1.0, 1.0, 0.9, 0.6, 0.6, 0.4, 0.0 and none at step 21, so 9-10 wheat seeds are bought on day 0 (8-11), for 9 wheat tiles.
- Cash on day 0: $3000, then $2450-2467 after step 0, $570-589 after step 1, and $0-9 at the end of the day.
- Four of the 5 animals are fed on day 0. The cow on (4,2), placed at step 9, is not fed; it survives because a new animal starts with `consecutive_unfed = 0`.

### 1b. Days 1-6, per day

Medians over games (p10-p90), `@h` = median hour of the executed units. Tile events list the games that show them.

| day | hires | seeds / animals bought | feed wheat bought; sales | tile events |
|---|---|---|---|---|
| 1 | 4 (2-9) @h0, more @h2 after a fertilizer sale | melon 4 @h10 | wheat 6 (3-6); fertilizer 5 sold | melon (4,0) h14 [92], (3,0) h17 [92], (3,3) h16 [86], (2,3) h18 [92]; wheat (0,3) h21 [58] |
| 2 | 6 (6-8) @h0 | strawberry 4 (3-4) @h11 | wheat 3; fertilizer 5 | wheat harvested at age 2 on (1,0) h12, (0,4) h13, (2,2) h15, (0,0) h15, (1,1) h17 [91], (0,1) h21 [54]; strawberry (0,4) h14 [92], (0,0) h16 [80], (1,1) h18 [90], (0,1) h22 [53], (0,3) h17 [33] |
| 3 | 6 @h0 | strawberry 6 @h9 | wheat 5 sold; fertilizer 5 | wheat harvested at age 3 on (0,3) h8 [58], (2,0) h11, (2,1) h11, (0,2) h13, (0,1) h14 [38]; strawberry (0,3) h9 [59], (2,0) h12, (0,2) h14, (1,0) h15 [80], (2,1) h19, (2,2) h22 [80], (0,1) h22 [38] |
| 4 | 6 (4-6) @h0 | strawberry 1 (0-2) | fertilizer 5 | last strawberry on (1,0) [11] or (2,2) [12]; otherwise feed/care/collect only |
| 5 | 6 @h0 | - | wheat 2; fertilizer 5 | none; cash rises to about $840 |
| 6 | 8 @h0 | cow 5 (2-6) @h10, sheep 0 (0-4), goose 2 (0-4) @h11, strawberry 10 (0-12) @h6, wheat 5 (1-17) @h13 | wheat 7 (2-12); **wool 18 sold** (6 at h3, 6 at h5, 6 at h6) | **NE bought h5** [92]; pasture (5,4) h9 [92], pasture + cow (5,3) h14 [92], (5,2) pasture/cow [78], (6,4) pasture [66] or coop [26], (6,3), (7,4); strawberries on NE rows 0-1; wheat (9,1) [85], (6,1) [70], (7,2) [67] |

The full per-step modal market list for steps 0-150, with the second most common list, executed units per step and tile changes, is in `out\opening_steps.md`.

### 1c. Layout at the end of days 0, 2, 5 and 6 (modal tile; the number is the % of games with that tile)

Legend: w wheat, m melon, s strawberry, C cow, S sheep, G goose, . empty, # locked.

```
end of day 0 (90/92 identical)   end of day 2                          end of day 5 (86/92 identical)
w w w . .                        s87 .87 w99 m   m                     s s s m m
w w w m m                        s58 s98 w   m   m                     s s s m m
w m w m C                        w99 m   .   m   C                     s m s m C
. m . . S                        w63 m   m   m93 S                     s m m m S
w m S S C                        s   m   S   S   C                     s m S S C
```

End of day 6, NE quadrant (x = 5-9, y = 0-4), modal content and share:

```
s70 s57 s72 s73 s57
s61 w76 s65 s67 w92
C85 .47 w73 s58 .84
C100 C39 s58 .54 .54
C75 C60 G50 .38 .84
```

(The empty NE tiles on day 6 are filled on day 7: at the end of day 7 only 0.7 tiles are empty on the whole farm.)

### 1d. What the divergence depends on

1. **Step 13, the only day-0 market variant, does not matter.** 56 games send `SELL WHEAT 1, BUY_SEED WHEAT 2`, 36 send `... BUY_SEED WHEAT 5`. It is not explained by DSM's cash (range $41-65 against $37-60), the opponent's cash, the wheat price or inventory, the seat, or seed or episode parity; it is probably internal search noise. Both variants end day 0 with the same 9-10 wheat seeds.
2. **From step 24 on, the divergence is cash-driven.** DSM spends every dollar on day 0 (one wheat seed per step while cash is at least $10), which leaves a residual of $0-9. At step 24 it always sends 8 HIREs; with costs of 1, 1, 2 and 3, the residual buys 0-4 hands:

   | hires executed at step 24 | games | cash at step 24 | day-1 action agreement within the group | total day-1 hires (games) |
   |---|---|---|---|---|
   | 0 | 6 | $0 | 67% | 8 (6) |
   | 1 | 24 | $1 | 56% | 2 (10), 9 (14) |
   | 2 | 10 | $2-3 | 78% | 3 (10) |
   | 3 | 25 | $4-6 | 92% | 4 (25) |
   | 4 | 27 | $7-9 | 39% | 4 (27) |

   Across all 92 games the day-1 agreement is only 29%. More hands are hired at hour 2 once the collected fertilizer is sold. That sale price also depends on the opponent's fertilizer sales.
3. **The opponent moves DSM's cash through the shared wheat market.** DSM's 5 wheat at step 0 cost $133 when the opponent buys no wheat at step 0 (9 games; median cash left at step 24: $8), $136 when it buys 1-5 (40 games; $6), $140 for 6-10 (12 games; $1) and $150 for more than 10 (31 games; $1). The later one-unit wheat round trips (steps 1-6) net to about $0.
4. **Weeds do not matter.** Only one weed appears on DSM's farm by the end of day 5 across all 92 games.
5. **Shops do not matter until day 6.** The first shop is visible from day 3, but the NW plan is the same whatever it is (86/92 identical grids at the end of day 5). From day 6 on, the NE composition depends on shops 1-2 (section 3).

---

## 2. Land (`land.py` -> `out\land.md`)

| quadrant | games | when (day:hour, games) | cash at the start of that step | cash right before BUY_LAND executes (min / p10 / median / p90 / max) | cash right after (median) | what funded it |
|---|---|---|---|---|---|---|
| NE ($1000) | 92/92 | 6:05 x92 | $1974 (1748-2219) | 2780 / 2924 / 3155 / 3440 / 3608 | $2154 | first wool: 3 sheep x 6 wool; `SELL WOOL 6` in slot 0 of the same step [92/92] |
| SW ($2000) | 92/92 | 9:01 x8, 9:03 x63, 9:05 x20, 9:07 x1 | $2058 (1283-2899) | 2020 / 2221 / 2550 / 2911 / 3369 | $546 | second wool (`SELL WOOL 4, BUY_LAND` in 63 games) |
| SE ($4000) | 92/92 | 10:12 x24, 10:13 x20, 10:14 x43, 10:15-18 x5 | $4348 (2671-6429) | 4055 / 4153 / 4781 / 5536 / 6429 | $774 | first melon harvest: about 30 melons sold on day 10 before the purchase |

Rules:
- Each purchase is tied to a harvest event and fires as soon as cash, including sales earlier in the same step, covers the price. No reserve is kept: the minimum left after SW is $20 and after SE $55.
- When it fails it retries 1-2 hours later. `[SELL WOOL 4, BUY_LAND]` at day 9 hour 3 failed in 21 games because the wool did not raise enough cash; they bought at hour 5 or 7. The first SE attempt is on day 10 at hours 12-14 and succeeds at once in 83/92; the other 9 retry and succeed 1-4 hours later.
- This submission buys SE in 92/92 games. The 61% SE rate quoted in `research\notebook_insights.md` came from the 09-22 sample.

---

## 3. Tile allocation vs town shops (`alloc.py` -> `out\alloc.md`, per game: `out\alloc_per_game.csv`)

Shop k (k = 0..7) unlocks at the end of day 3k+2, so during day D the first D//3 shops are known. The per-game CSV lists the counts of every tile type at the end of days 6, 9, ..., 27, the shops known then, the quadrants and the cash.

### 3a. Mean tile counts (all 92 games)

| end of day | cow | sheep | goose | wheat | carrot | tomato | strawberry | melon | weed | empty | animals |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 2.0 | 3.0 | 0 | 0 | 0 | 0 | 10.0 | 9.9 | 0 | 0.1 | 5.0 |
| 6 | 6.3 | 4.1 | 1.6 | 5.9 | 0.1 | 0.1 | 17.0 | 9.9 | 0 | 4.9 | 12.0 |
| 9 | 9.2 | 5.3 | 4.4 | 18.8 | 0.5 | 4.1 | 19.3 | 9.9 | 0.1 | 3.3 | 18.8 |
| 12 | 9.5 | 6.5 | 7.1 | 29.2 | 3.4 | 9.9 | 27.7 | 0 | 0.5 | 6.2 | 23.1 |
| 15 | 9.4 | 6.7 | 7.1 | 23.2 | 4.1 | 13.1 | 30.4 | 0 | 0.8 | 4.9 | 23.3 |
| 18 | 9.2 | 6.6 | 7.1 | 20.0 | 3.9 | 20.1 | 26.5 | 0 | 1.0 | 5.2 | 22.9 |
| 21 | 8.6 | 6.2 | 7.0 | 25.2 | 8.5 | 16.5 | 19.7 | 0 | 1.8 | 5.9 | 21.9 |
| 24 | 8.1 | 5.6 | 6.8 | 31.4 | 15.1 | 10.9 | 11.6 | 0 | 2.7 | 7.2 | 20.5 |
| 27 | 7.2 | 4.0 | 6.5 | 25.2 | 19.5 | 8.3 | 6.6 | 0 | 5.1 | 16.3 | 17.7 |
| 28 | 6.7 | 0.8 | 5.7 | 13.3 | 9.4 | 7.4 | 5.5 | 0 | 7.5 | 37.9 | 13.1 |

### 3b. Animals: the herd depends on WHEN the relevant shop unlocked

Fit: `peak herd over days 6-15 = b0 + sum of inc(u) over the relevant shops unlocked on day u`.

| animal | b0 (no relevant shop) | inc(u=3) | inc(6) | inc(9) | inc(12) | inc(15) | R² | RMSE |
|---|---|---|---|---|---|---|---|---|
| sheep (YARN_STORE) | 3.0 | +8.0 | +6.6 | +6.9 | +4.2 | +2.0 | 0.97 | 0.7 |
| cow (PIZZA, ICE_CREAM, SMOOTHIE) | 5.2 | +4.2 | +4.1 | +2.1 | +0.8 | -0.1 | 0.92 | 0.9 |
| goose (BAKERY, BRUNCH) | 5.1 | +4.0 | +3.0 | +2.3 | -0.8 | +0.1 | 0.56 | 2.3 |

Cross-checks:
- **Sheep** (peak over days 6-18): exactly 3 in the 33 games that never get a yarn store and in the 7 whose first yarn store comes on day 21 or 24. When the first yarn store comes on day 3 the peak is 10-12 sheep; day 6, 9-11; day 9, 9-10; day 12, 7-10; day 15, 4-6; day 18, 3-5. A second yarn store adds 6-9 more if it comes by day 9, 2-6 if it comes on day 12-15, and about 1 on day 18.
- **Cows** by the number of dairy shops among shops 1-2 (known on day 6) and whether shop 3 is dairy: (0,0) 5.9 [22 games], (0,1) 7.1 [15], (1,0) 9.4 [22], (1,1) 11.7 [17], (2,0) 13.0 [7], (2,1) 16.3 [9].
- **Total animals is nearly fixed**: 18.8 at day 9 (sd 1.7) and 23.1 at day 12 (sd 2.3; p10/p50/p90 21/22/26). Geese are the remainder: `geese(12) = 16.0 - 0.60 x (cows + sheep) + 0.8 x #egg shops` (R² 0.77, RMSE 1.7), against R² 0.36 for egg shops alone. The goose share of the animals is 0.22 with 0 egg shops among the first 4, 0.31 with 1, 0.44 with 2 and 0.48 with 3. In a multi-shop regression PET_CAFE also raises geese (+2.6 at day 9): nothing else competes for the animal slots in those worlds.
- **Purchase timing** [92/92]: cows, sheep and geese are bought one or two at a time, a few hours before they are placed (median lag 6-7 steps, p90 8-10). The last cow is bought on day 9 (median), the last sheep on day 8 and the last goose on day 11. Later animal buys are extra sheep for a second yarn store (days 12-21) and a few cows on days 12-18.
- **Herd decline** follows the product price, not a fixed date (see 7d). With 0 dairy shops among the first 6 (4 games), cows go 5.2 (peak), then 2.0 on day 21 and 0.8 on day 27 (milk price $21 on day 15). With 1 dairy shop (15 games): 7.5, 4.8, 2.3. With 3 or more (46 games): 11.5, 11.2, 10.0. Sheep without any yarn store among the first 6 (40 games) stay at 3 until day 21, then fall to 2.3 on day 24 and 0.7 on day 27 (wool $17 on day 15).
- **The opponent's herd does not matter**: adding the opponent's count 3 days earlier changes R² by at most 0.01 for sheep and cows, and by 0.06-0.1 for geese.

### 3c. Crops: peak size vs demand

| crop | mean peak tiles | median peak day | best fit (x = demand from shops 1..K) | R² | RMSE |
|---|---|---|---|---|---|
| strawberry | 30.6 | 14 | 13.1 + 8.7 x, x = #BRU+#ICE+#SMO+#FM among shops 1-4 | 0.90 | 2.8 |
| tomato | 21.7 | 19 | 13.9 + 7.2 x, x = #PIZZA+#FM among shops 1-4 | 0.70 | 4.1 |
| carrot | 24.2 | 26 | 12.9 + 4.0 x, x = 2 x #PET + #FM among all 8 shops | 0.56 | 6.3 |
| wheat | 36.4 | 22 | about constant (R² at most 0.17): the filler crop | 0.17 | 5.5 |

One-variable fits at every checkpoint, `count(end of day D) = a + b x`, where x = demand of the product from the first D//3 shops (cell: `a + b x (R²)`):

| type | x | day 6 | day 9 | day 12 | day 15 | day 18 | day 21 | day 24 | day 27 |
|---|---|---|---|---|---|---|---|---|---|
| cow | #PIZZA+#ICE+#SMOOTHIE | 4.8+2.0x (0.78) | 5.5+3.0x (0.83) | 4.8+2.9x (0.69) | 4.5+2.4x (0.56) | 3.6+2.3x (0.53) | 2.4+2.2x (0.60) | 1.5+2.1x (0.63) | -0.4+2.4x (0.76) |
| sheep | 2 x #YARN | 3.0+2.0x (0.92) | 3.0+2.7x (0.82) | 3.0+3.2x (0.92) | 3.0+2.8x (0.85) | 2.9+2.4x (0.82) | 2.7+2.0x (0.73) | 2.1+1.7x (0.66) | 0.0+2.0x (0.72) |
| goose | #BAKERY+#BRUNCH | 0.8+1.7x (0.44) | 2.8+2.3x (0.42) | 5.0+2.2x (0.36) | 5.0+1.8x (0.29) | 4.5+1.7x (0.27) | 4.3+1.5x (0.26) | 4.1+1.3x (0.24) | 3.9+1.3x (0.24) |
| wheat | #BAK+#PIZ+#BRU+#ICE+#FM | 6.5-0.5x (0.01) | 17.6+0.7x (0.04) | 23.5+2.3x (0.21) | 17.2+1.9x (0.15) | 12.7+1.9x (0.16) | 15.8+2.1x (0.13) | 19.0+2.4x (0.14) | 15.7+1.9x (0.13) |
| carrot | 2 x #PET + #FM | -0.1+0.2x (0.14) | -0.6+1.1x (0.23) | -1.2+3.5x (0.63) | -1.7+3.5x (0.70) | -1.9+3.1x (0.63) | 0.3+3.6x (0.52) | 4.9+3.6x (0.41) | 11.0+3.0x (0.48) |
| tomato | #PIZZA+#FM | -0.1+0.3x (0.23) | 2.7+1.8x (0.23) | 4.5+4.9x (0.52) | 5.5+5.4x (0.53) | 9.8+6.2x (0.57) | 8.7+4.1x (0.54) | 6.4+2.1x (0.40) | 5.4+1.3x (0.38) |
| strawberry | #BRU+#ICE+#SMO+#FM | 11.1+6.1x (0.79) | 10.4+6.0x (0.79) | 11.0+8.3x (0.89) | 10.8+7.9x (0.85) | 6.9+6.7x (0.68) | -1.3+6.1x (0.61) | -2.0+3.5x (0.54) | -2.5+2.4x (0.49) |

Multi-shop regression at the end of day 12, `count = b0 + sum over shop types of b x (#instances among shops 1-4)`:

| type | b0 | BAK | BRU | FM | ICE | PET | PIZ | SMO | YARN | R² |
|---|---|---|---|---|---|---|---|---|---|---|
| cow | 3.0 | +0.0 | +0.5 | +0.9 | +3.2 | +0.2 | +3.3 | +3.6 | +0.4 | 0.72 |
| sheep | 2.1 | +0.5 | +0.3 | +0.4 | +0.2 | +0.3 | -0.1 | +0.2 | +6.5 | 0.93 |
| goose | 2.5 | +3.7 | +2.3 | +1.3 | +0.2 | +2.6 | +0.5 | +0.3 | -0.9 | 0.64 |
| wheat | 9.7 | +7.3 | +4.9 | +4.5 | +6.1 | +1.8 | +5.5 | +3.8 | +4.8 | 0.43 |
| carrot | 1.4 | -0.8 | -0.1 | -0.2 | -1.1 | +8.5 | -0.5 | -0.1 | -0.1 | 0.79 |
| tomato | 3.1 | +1.8 | -0.8 | +2.5 | -1.2 | +1.3 | +7.3 | -0.6 | +2.0 | 0.80 |
| strawberry | 9.3 | +1.1 | +9.0 | +8.1 | +9.1 | +0.5 | +0.0 | +9.2 | +0.1 | 0.90 |

The same regressions at days 9, 18 and 24 are in `out\alloc.md`.

### 3d. Layout pattern

- **Animals form a compact block around the shed; crops fill the rest.** Measured from the nearest shed-access tile at the end of day 15: distance 0 holds 3.8 animals out of 4 tiles, distance 1 holds 6.9 of 8, distance 2 holds 7.2 of 12 and distance 3 holds 3.6 of 16. Nothing beyond distance 4 is an animal.
- **The far SE corner ((8,7), (9,7), (8,8), (9,8), (7,9), (8,9), (9,9)) is often left empty** (each tile empty in 35-86% of games from day 12 on). The farm carries 5-9 empty tiles on days 12-26.

Share of games (%) in which a tile holds an animal, end of day 18 (the shed is between (4,4) and (5,5)):
```
  0   0   0   0   0 |  0   0   0   0   0
  0   0   0   0  10 | 18   0   0   0   0
  0   0   0   4  99 | 90  85  12   0   0
  0  98  92   8 100 | 95  98  32  59   0
  0   0 100 100 100 |100 100  98  96   5
 ---------------------------------------
  0   4  96 100 100 | 83  54   3   3   1
  0   0   7   1 100 | 45  13   0   0   0
  0   0   0   0 100 | 11   3   0   0   0
  0   0   0   0   5 |  0   0   0   0   0
  0   0   0   0   1 |  0   0   0   0   0
```
Modal content per tile, end of day 12 and day 21 (A = any animal; number = % of games):
```
day 12                                                 day 21
s100 s100 s100 s 98 s 86 | s 90 s 82 s 84 s 82 s 62    t 68 t 49 w 88 s 99 s 89 | s 87 s 79 s 82 s 74 s 61
s100 s100 s100 w 49 w 58 | s 64 w 65 s 74 s 67 w 78    t 78 t 95 w 45 s 42 s 40 | s 64 s 37 s 70 s 65 w 71
s100 w 66 s100 w 67 A100 | A 97 A 93 w 50 s 68 w 58    w 46 t 84 w 68 w 40 A 98 | A 89 A 66 s 42 s 59 w 48
s100 A 98 A 92 w 93 A100 | A100 A100 s 58 A 63 w 77    w 68 A 98 A 92 w 91 A 98 | A 93 A 95 s 54 A 52 w 63
s100 w100 A100 A100 A100 | A100 A100 A100 A 99 w 89    t 97 w 98 A100 A100 A100 | A100 A 99 A 93 A 82 w 70
w100 w 99 A 93 A100 A100 | A 77 w 55 w 97 w 97 w 98    w100 w 97 A 92 A 93 A 99 | A 83 A 55 w 93 w 93 w 87
t 92 w 46 w 84 w 67 A100 | A 35 w 57 w 45 t 51 w 63    c 38 t 63 w 58 t 76 A100 | A 43 t 35 t 47 t 63 w 43
t 97 t 64 w 89 w 50 A100 | w 34 w 77 w 68 . 35 . 59    c 41 t 62 w 57 t 54 A100 | s 44 w 32 w 32 t 41 . 68
t 82 t 57 w 47 s 62 s 72 | s 57 w 58 w 39 . 52 . 80    t 41 t 47 s 42 s 74 s 75 | s 73 w 39 w 32 . 42 . 67
t 89 t 72 w 50 s 68 s 64 | s 64 w 41 . 52 . 66 . 86    t 28 t 61 s 35 s 78 s 73 | s 66 w 29 t 29 . 45 . 74
```
Which animal sits where (end of day 15; % of games):

| tiles | animal |
|---|---|
| (4,2), (4,4), (5,2), (5,3), (3,5) | cows: C99, C100, C89, C96, C100 (the pastures of days 0, 6 and 9) |
| (2,4), (3,4), (4,3) | sheep: S100 (the day-0 pastures) |
| (1,3), (2,3), (2,5), (4,6), (4,7) | geese: G82, G92, G75, G70, G74 (coops on the old melon tiles and in SW column 4) |
| (6,2)-(8,4), (4,5), (5,5), (5,4) | mixed, set by the shops |

By quadrant (mean tiles per game):

| end of day | quadrant | cow | sheep | goose | wheat | carrot | tomato | strawberry | empty+weed |
|---|---|---|---|---|---|---|---|---|---|
| 12 | NW | 2.0 | 3.3 | 1.8 | 4.5 | 0.7 | 0.3 | 12.4 | 0.1 |
| 12 | NE | 5.4 | 1.8 | 1.9 | 5.7 | 0.1 | 0.8 | 8.5 | 0.7 |
| 12 | SW | 1.8 | 0.6 | 2.7 | 8.4 | 1.1 | 6.7 | 3.6 | 0.2 |
| 12 | SE | 0.3 | 0.7 | 0.8 | 10.6 | 1.6 | 2.2 | 3.1 | 5.7 |
| 24 | NW | 1.9 | 3.1 | 1.7 | 6.3 | 2.8 | 5.9 | 2.6 | 0.4 |
| 24 | NE | 4.3 | 1.1 | 1.7 | 11.7 | 1.7 | 0.9 | 1.3 | 2.0 |
| 24 | SW | 1.6 | 0.6 | 2.6 | 5.7 | 6.7 | 1.9 | 4.0 | 1.8 |
| 24 | SE | 0.4 | 0.8 | 0.8 | 7.6 | 3.8 | 2.1 | 3.8 | 5.7 |

The modal use sequence of every one of the 100 tiles is in `out\tile_sequences.md` (`sequences.py`). Typical sequences:
- NW (1,1): `w0 s2 t18` [81/92]; (0,4): `w0 s2 t18` [88]; (0,0): `w0 s2 t18` [59].
- NW (3,0): `m1 s11` [42] or `m1 s11 w27` [40]. The melon tiles (1,3) `m0 oG10` [73] and (2,3) `m1 oG11` [85] become goose coops.
- NE (5,0): `s6 w22..25` [22]; (9,1): `w6..24` [20].
- SW (4,6) `oG9` [64]; (3,5) `pC9` [76]; (0,6) `t9 c20 c23 c26` [13]; (4,8) `w9 s12` [39].

---

## 4. Planting and buying schedule (`schedule.py` -> `out\schedule.md`)

### 4a. Seeds and animals bought per day

Cell: mean units per game [games buying] h<median hour>. Days 0-5 are in 1b.

| day | wheat seed | carrot seed | tomato seed | strawberry seed | cow | sheep | goose |
|---|---|---|---|---|---|---|---|
| 6 | 7.1 [92] h13 | 0.1 [1] | 0.1 [6] | 6.9 [69] h6 | 4.4 [92] h10 | 1.1 [23] h10 | 1.6 [53] h11 |
| 7 | 2.5 [78] h14 | 0.3 [3] | 0.0 [4] | 0.4 [31] h13 | 0.6 [52] h12 | 0.1 [10] | 0.3 [25] h12 |
| 8 | 4.2 [89] h14 | 0.0 [1] | 0.1 [7] | 0.1 [10] | 0.5 [37] h6 | 0.7 [23] h7 | 0.0 [1] |
| 9 | 15.0 [92] h14 | 0.2 [3] | 4.1 [84] h15 | 1.4 [43] h15 | 1.7 [92] h0 | 0.4 [15] h9 | 2.5 [75] h8 |
| 10 | 10.5 [92] h17 | 2.1 [26] h15 | 2.2 [64] h16 | 3.1 [59] h15 | 0.2 [8] | 0.6 [15] h10 | 1.8 [83] h10 |
| 11 | 12.0 [92] h14 | 1.2 [18] h16 | 3.7 [89] h13 | 2.5 [90] h11 | - | 0.0 [1] | 0.9 [84] h8 |
| 12 | 9.7 [92] h15 | 1.6 [23] h16 | 4.6 [86] h15 | 3.8 [68] h12 | 0.2 [12] h1 | 0.6 [14] h1 | - |
| 13 | 9.0 [92] h14 | 1.9 [26] h15 | 2.5 [83] h15 | 0.3 [26] h11 | - | - | - |
| 14 | 6.6 [92] h15 | 1.4 [18] h16 | 0.2 [20] h15 | - | - | - | - |
| 15 | 7.5 [92] h15 | 1.0 [12] h16 | 2.4 [77] h15 | 1.6 [43] h9 | 0.1 [7] h1 | 0.3 [10] h1 | - |
| 16 | 6.4 [92] h14 | 1.8 [24] h15 | 1.4 [67] h15 | - | - | - | - |
| 17 | 5.8 [92] h15 | 0.9 [13] h15 | 0.6 [42] h15 | - | - | - | - |
| 18 | 6.0 [92] h15 | 1.3 [19] h16 | 2.0 [72] h15 | - | 0.1 [6] h1 | 0.1 [5] h1 | - |
| 19 | 7.0 [92] h15 | 3.5 [43] h15 | 0.1 [8] | - | - | 0.0 [1] | - |
| 20 | 7.2 [92] h15 | 2.9 [42] h15 | 0.0 [2] | - | - | - | - |
| 21 | 7.1 [91] h15 | 4.5 [50] h15 | 0.0 [2] | - | - | 0.0 [2] | - |
| 22 | 7.3 [90] h14 | 4.2 [53] h15 | 0.0 [3] | - | - | - | - |
| 23 | 9.8 [92] h14 | 5.3 [63] h14 | 0.0 [3] | - | - | - | - |
| 24 | 8.4 [92] h13 | 6.8 [72] h14 | 0.0 [3] | - | - | - | - |
| 25 | 7.2 [92] h13 | 7.0 [79] h14 | 0.0 [1] | - | - | - | - |
| 26 | 6.3 [91] h12 | 9.9 [90] h12 | - | - | - | - | - |
| 27 | 3.2 [89] h12 | - | - | - | - | - | - |
| 28 | 0.1 [7] | - | - | - | - | - | - |

- Seeds are bought in the afternoon, one or a few at a time, just before planting. The median lag from purchase to PLANT is 16 steps for wheat, 10 for carrot, 7 for strawberry and 5 for melon. Tomato seeds are the exception: they are stocked ahead (4.8-6.3 seeds in stock on days 12-17, median lag 28 steps) and 1.7 per game are never planted.
- Season plantings per game (p10/median/p90): wheat 138/178/212, carrot 18/48/113, tomato 14/21/34, strawberry 20/30/42, melon 10/10/10.
- Last planting (median day:hour): strawberry 15:11, tomato 19:20, carrot 27:11, wheat 27:21.

### 4b. Cohorts (plantings per game by planting day)

| crop | cohorts |
|---|---|
| melon | d0 6.0, d1 3.9 (NW only). Never again. |
| strawberry | d2 3.8, d3 5.9, d4 0.3 (NW) / d6 7.0, d7 0.6 (NE) / d9 1.6, d10 2.4, d11 2.2, d12 3.8, d13 1.3 (SW, SE, NW melon tiles) / d15 1.6 |
| tomato | d9 4.0 (SW column 0) / d10-d17 0.6-2.4 a day (SW, SE) / **d18 4.3, d19 1.7 (80% in NW, on the tiles of the day-2/3 strawberries)** |
| carrot | d10-d18 1.0-1.8 a day / d19 2.3, d20 3.4, d21 3.5, d22 4.3, d23 5.3, d24 6.2, d25 7.6, **d26 9.6**, d27 2.8 |
| wheat | d0 9 / d6 5.9, d7 2.3, d8 4.4 (NE) / d9 13.0 (SW) / d10-d27 5-11 a day everywhere |

### 4c. Crop lifecycles (all plantings, all games)

| crop | plantings | how the tile is freed | harvest |
|---|---|---|---|
| wheat | 16,053 | harvest 97% | age 2: 18%, yield 2.1, 6% fertilized (21% of these in the opening, 22% on days 28-29, the rest mid-game); **age 3: 47%, yield 4.6, 81% fertilized; age 4: 35%, yield 5.4, 83% fertilized** |
| carrot | 5,324 | harvest 97% | age 2: 21%, yield 2.4; **age 3: 79%, yield 3.4** (45% fertilized) |
| melon | 914 | harvest 100% | age 10, yield 6.0, never fertilized |
| tomato | 2,082 | dug after the 4th production (dig 47%, alive at the end 42%) | harvested at ages 8, 9, 10 and 11; 7 units per plant (median); removed at age 11 (p10-p90 11-12) |
| strawberry | 2,826 | dug after the 4th production (58%; 27% alive at the end) | harvested at ages 10, 12, 14 and 16 (sometimes a day later); 8 units per plant (median); removed at age 16 (15-17) |

### 4d. What replaces what (all games; "days freed" = when the old crop left)

| days freed | crop that left | next use of the tile |
|---|---|---|
| 0-5 | wheat (opening) | strawberry 98-99% |
| 6-17 | wheat | wheat 69-80%, then tomato, strawberry, carrot |
| 9-11 | melon | wheat 49%, strawberry 22%, goose coop 18%, carrot 8% (median 9 h later) |
| 18-20 | strawberry | **tomato 50%**, wheat 39%, carrot 12% |
| 18-26 | tomato | carrot 50-59%, wheat 28-47% |
| 21-26 | strawberry | wheat 83% (days 21-23), carrot 72% (days 24-26) |
| 12-26 | carrot | carrot 60-76% |
| 27-29 | wheat, carrot | nothing (86-90%) |

Replanting is immediate: the median gap between the harvest or DIG and the next PLANT on that tile is 1 step. Melon tiles are the exception (9 h).

---

## 5. Hires (`hires.py` -> `out\hires.md`)

| day | hires (mean; p10-p90) | hour of executed hires | cost $ | units acting (farmer + hands) |
|---|---|---|---|---|
| 0 | 4.0 (4-4) | h1 | 7 | 5 from step 2 |
| 1 | 4.7 (2-9) | h0 53%, h2 47% | 22 | 3-10 |
| 2 | 6.3 (6-8) | h0 87% | 25 | 7 |
| 3 | 6.0 | h0 | 20 | 7 |
| 4 | 5.4 (4-6) | h0 | 16 | 6-7 |
| 5 | 6.0 | h0 | 20 | 7 |
| 6 | 8.0 | h0 | 54 | 9 |
| 7 | 8.8 (8-9) | h0 81%, h2 14% | 80 | 9-10 |
| 8 | 9.0 | h0 87%, h1 11% | 88 | 10 |
| 9 | 10.1 (10-11) | h0 79%, h1 20% | 153 | 11 |
| 10 | 12.1 (11-13) | h0 66%, h1 34% | 435 | 13 |
| 11-27 | 11.1-12.0 (11-12) | h0 about 68%, h1 about 30% | 250-370 | 12-13 |
| 28 | 10.9 | h0 74% | 222 | 12 |
| 29 | 10.0 | h0 80% | 146 | 11 |

- Season: 299 hires (p10 291, p90 305), $6.8k. On days 10-28: 12 hires on 1016 game-days, 11 on 679, 13-14 on 41, 10 on 12.
- **Order pattern**: hour 0 = `[SELL a, (SELL b), HIRE x8]`: exactly 8 HIREs at hour 0 in all 1748 game-days of days 10-28. Hour 1 = `[SELL, (SELL), HIRE x3-4]`. On days 1-9 the hires are cash-limited (see 1d): the HIREs execute only as far as cash, including sales in earlier slots of the same step, allows. The unfilled ones are re-sent at hours 1-2.
- The number of hires does not track the workload (correlation with animals 0.24, with crop tiles -0.09). It is a near-constant 11-12 a day, where the 12th hire costs $144.
- Labour mix (share of unit-turns): days 0-4: 40% moves, 29% PASS. Days 5-9: 47% moves, 10% PASS. From day 10: 37-44% moves, PASS 0.1-0.7%, no-effect actions about 0.3%. The rest is WATER 18-19%, HARVEST 6-13%, FEED 3-7%, CARE 3-7%, COLLECT 6-8% and FERTILIZE 3-5%.

---

## 6. Fertilizer (`fert.py` -> `out\fert.md`)

| day | animals | collected | FERTILIZE on wheat / carrot / tomato / strawberry | sold (avg price) | bought |
|---|---|---|---|---|---|
| 1-6 | 5 | 5 (100%) | 0 | about 5 a day ($99 falling to $89) | 0 |
| 7-9 | 12-14 | 12-14 (99-100%) | 0 | 10-12 a day ($86-78) | 0 |
| 10 | 18.8 | 18.8 | 2.7 / - / - / 0.1 | 7.8 ($75) | - |
| 11-15 | 21-23 | 99% | 4.7-7.9 / 0-0.1 / 0-0.6 / 0.4-7.5 | 12-16 a day ($71-50) | 0-1.7 |
| 16-20 | 22.5-23.3 | 97-99% | 4.6-5.4 / 0.1-0.6 / 1.8-3.4 / 3.2-6.0 | 9-10.7 ($46-30) | 0-0.2 |
| 21-25 | 20.5-22.4 | 97-98% | 6.9-8.4 / 1.0-2.3 / 2.0-4.1 / 1.9-5.6 | 3.8-9.1 ($27-15) | 0-0.5 |
| 26-28 | 17.7-19.1 | 97-98% | 5.6-7.1 / 3.5-5.2 / 2.1-2.5 / 0.8-1.7 | 3.5-4.4 ($14-12) | 0 |
| 29 | 13.1 | 77% | 0 | 11.9 ($9) | 0 |

- Season per game: **482 collected**. **241 FERTILIZE**: wheat 117 (48%), strawberry 65 (27%), tomato 34 (14%), carrot 25 (10%), melon 0. **243 sold for $12,990.** **3.5 bought** (18 of 92 games buy any).
- The shed holds only 3-15 fertilizer at hour 0. Hands collect it in the morning (median hour 6), carry it and use it on crops in the afternoon (FERTILIZE median hour 15). Only 6 PICKUP FERTILIZER a game.
- **Crop age when fertilized** (effective FERTILIZE only):

| crop | age distribution | fertilized before that day's WATER | reading |
|---|---|---|---|
| wheat | age 2: 79%, age 3: 10%, age 1: 8% | 98% | once, on the first day of the bonus window (ages 2-4). Must precede WATER, because the bonus is added at WATER time. |
| carrot | age 2: 81%, age 1: 15% | 96% | once, window ages 2-3 |
| tomato | age 7: 44%, age 10: 29%, ages 6/8/9: 8% each | 84% | twice (ages 7 and 10) so all 4 productions (end of ages 7-10) are doubled |
| strawberry | age 9: 37%, age 13: 22%, age 12: 11%, age 15: 12%, age 8: 7% | 88% | twice (ages 9 and 13), covering productions at the end of ages 9, 11, 13 and 15 |

- **Share of plantings that get fertilizer**: wheat planted on days 0-9 30%, days 10-19 74%, days 20-29 81% (always once). Carrot planted days 10-19 16%, days 20-29 53%. Tomato 93-98% (1x 33-46%, 2x 52-60%). Strawberry planted days 0-9 99% (2x 65%, 3x 30%), days 10-19 85%. Melon 0%.
- **Priority**: early fertilizer (days 1-9, price about $80-100) is all sold. From day 10 fertilizer goes first to strawberries and tomatoes on their production windows and to wheat at age 2; carrots get the leftovers late in the game.

---

## 7. Animal care (`animals.py` -> `out\animals.md`)

### 7a. Coverage per animal-day (% of alive animals that got the action that day)

| days | cow fed / cared / fert collected | sheep fed / cared / fert | goose fed / cared / fert |
|---|---|---|---|
| 1-5 | 100/100/100 (day 2: 9% fed, 100% cared) | 89-100 / 100 / 100 | - |
| 7-13 | 36-97 / 50-96 / 81-99 | 85-100 / 85-100 / 86-100 | 44-97 / 44-99 / 43-99 (new geese) |
| 14-15 | 87-93 / 87-93 / 99 | 72-98 / 72-98 / 95-99 | 93-97 / 92-96 / 99-100 |
| 16-26 | alternating: 46-63% on even days, 78-87% on odd days / same / 97-100 | 51-97 / 49-90 / 96-100 | 80-93 / 78-93 / 95-99 |
| 27 | 80 / 79 / 98 | **16 / 15** / 97 | 81 / 72 / 95 |
| 28 | **20 / 20** / 99 | **5 / 5** / 97 | **27 / 19** / 96 |

- **COLLECT_FERTILIZER: every animal, every day** (97-100%).
- **FEED and CARE go together**: 98% of animal-days with either have both (days 7-26). Order: FEED first (CARE comes before FEED in only 10%). Feeding is a morning job: FEED median hour 7 (goose 9), CARE 9, COLLECT 6, animal HARVEST 5-9.
- **Feeding is value-based** (7d below), which is why cows show the alternating pattern: most cows are placed on day 6, so their production days are the odd days.

### 7b. Endgame release

Last FEED day per animal (% of animals):

| animal | d≤25 | d26 | d27 | d28 |
|---|---|---|---|---|
| cow | 26% | 5% | **54%** | 15% |
| sheep | 42% | **47%** | 8% | 3% |
| goose | 8% | 11% | **56%** | 25% |

The last productions that can still be harvested and sold are at the end of day 27 for cows placed on day 0 or day 6 (interval 2), at the end of day 26 for sheep placed on day 0 (interval 3; the next one would be at the end of day 29) and at the end of day 28 for geese. DSM feeds through the last useful production day and then lets the animal escape. Escapes per game on day 28: sheep 3.25, goose 0.80, cow 0.52. Escapes during days 18-27 (cows 2.2, sheep 2.9 per game) are the price-driven releases of 3b and 7d.

### 7c. Harvest cadence and yield

| animal | first harvest | units at first harvest | days between harvests | units per harvest |
|---|---|---|---|---|
| cow | age 8 (100%) | 5.9 (capped at 6 by the banked care) | 2 d: 72%, 4 d: 9%, 3 d: 7% | 2.8 (2-day gap), 4.6 (4-day gap); 2.9-3.3 by period |
| sheep | age 6 (100%) | 5.9 | 3 d: 67%, 4 d: 12%, 2 d: 10% | 3.8 (max 4 = 1 + 3 care days) |
| goose | age 4 (88%), 5 (12%) | 3.1 | 1 d: 46%, 2 d: 48% | 1.8 (1-day gap), 3.6 (2-day gap); 2.5-3.0 by period |

### 7d. Value-based feed skipping (days 10-27; % fed; prices at hour 6 of the day)

| animal | day type | price ratio <1 | 1-1.5 | 1.5-2 | 2-3 | 3-4 | ≥4 |
|---|---|---|---|---|---|---|---|
| cow | production day | 86% | 96% | 98% | 99% | 100% | 100% |
| cow | non-production day | **2%** | **7%** | **28%** | 66% | 85% | 92% |
| sheep | production day | 69% | 93% | 96% | 99% | 100% | 100% |
| sheep | non-production day | 43% | 60% | 61% | 83% | 88% | 94% |
| goose | every day is a production day | 77% | 88% | 88% | 84% | - | - |

Price ratio = milk (cow) / wool (sheep) / egg (goose) price divided by the wheat price. A production day is a day whose end-of-day refresh adds yield: for cows every 2nd day from age 7, for sheep every 3rd day from age 5, for geese daily from age 3.

Reading:
- On a production day, feeding is needed to cash in the banked care, so it is always done (unless the product is nearly worthless).
- On a non-production day, one feed banks exactly +1 unit for the next production, so DSM feeds only if the product is worth more than about 2-3 wheat.
- A kept sheep can skip at most one of the two non-production days in each 3-day cycle (2 unfed days in a row = escape), so about 50% is the floor for a sheep that is kept. The 43% at ratio <1 includes sheep that are being released.
- The 12% of unfed geese is not explained by the price ratio or the number of eggs held.

---

## 8. Other rules (`misc.py` -> `out\misc.md`)

**Cash** (median over games):

| end of day | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 15 | 20 | 25 | 29 (final) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DSM | 6 | 3 | 9 | 18 | 433 | 836 | 34 | 75 | 2,166 | 230 | 2,082 | 5,406 | 7,788 | 26,613 | 61,602 | 84,412 | 110,228 |
| opponent | 16 | 82 | 184 | 194 | 548 | 780 | 622 | 384 | 1,278 | 1,554 | 11,302 | 14,356 | 17,326 | 28,281 | 53,616 | 71,600 | 90,866 |

- Until day 10, DSM's lowest cash of each day is a few dollars (median $0-107; day 5, an idle day, $380): every dollar goes into land, animals, seeds and hands.
- It trails the opponent by about $9-10k on days 10-12, passes it on day 16 and finishes about $20k ahead. From day 11 on, cash hardly dips: the median daily minimum is within $0-222 of the previous day's close.

**Wheat economy** (per game): 176 seeds bought, 749 wheat harvested, 389 fed, 183 bought (49.6 of them on day 10, when the melon cash arrives and the herd has grown to 19-21 animals before the own wheat comes in), 538 sold (at 1.44x base, about $36).

**Sales** (per game):

| product | units | revenue | price / base | revenue days 0-9 / 10-19 / 20-29 | median lot |
|---|---|---|---|---|---|
| strawberry | 216 | $30,889 | 1.19 | 0 / 17,085 / 13,804 | 2 |
| milk | 202 | $23,794 | 0.74 | 2,237 / 13,122 / 8,435 | 2 |
| wool | 143 | $21,775 | 0.76 | 5,519 / 9,085 / 7,171 | 2 |
| wheat | 538 | $19,341 | 1.44 | 570 / 7,407 / 11,365 | 5 |
| fertilizer | 243 | $12,990 | 0.53 | 5,460 / 6,275 / 1,255 | 2 |
| melon | 60 | $12,467 | 0.84 | 0 / 12,467 / 0 | 6 |
| tomato | 154 | $10,877 | 1.18 | 0 / 1,237 / 9,641 | 7 |
| egg | 211 | $9,898 | 0.94 | 0 / 4,251 / 5,647 | 8 |
| carrot | 179 | $7,825 | 1.25 | 0 / 1,145 / 6,679 | 9 |
| **total** | | **$149,857** | | | |

**Market list mechanics** [92/92]:
- The first non-empty order is a SELL on 99.4% of turns with a sale.
- 17% of non-empty lists contain empty placeholder orders `[]`. They mostly push `BUY_PRODUCT WHEAT` back: 32% of all wheat buy orders are in a padded list, 62% of those at slots 7-9. The buy then executes after the opponent's earlier-slot orders (lockstep by slot index).
- DSM sells on 304 turns a game.

**Daily rhythm** (days 10-27, median hour of effective actions): PICKUP WHEAT 1 → cow/sheep HARVEST 5-6 → COLLECT_FERTILIZER 6 → FEED 7 → CARE 9 → goose HARVEST 9 → wheat HARVEST 13 → PLANT 15, FERTILIZE 15, carrot HARVEST 15 → WATER 16, strawberry HARVEST 16 → DIG 17, tomato HARVEST 17. In short: animals in the morning, crops in the afternoon.

**Stop rules** (median day:hour of the last event per game):
- Last purchase: melon seed 1:11, sheep 8:12, cow 9:00, goose 11:08, strawberry seed 13:13, tomato seed 18:17, wheat (feed) 23:12, carrot seed 26:15, wheat seed 27:15.
- Last effective action: PLANT 27:22, CARE 28:19, FEED 28:20, FERTILIZE 28:22, WATER 29:14, COLLECT_FERTILIZER 29:19.
- The last SELL is at step 718 in 92/92 games. Unsold stock at the end is about 1 fertilizer, 1 milk and a few units of other goods: about $400 at base prices, less at the real end-of-game prices.

---

## 9. Caveats and open points

- One DSM submission, 92 games against 73 opponents. The rules are what this submission does. The 2026-09-22 sample in `notebook_insights.md`, possibly an older DSM submission, bought SE in only 61% of games.
- The allocation rules are fits, not DSM's code. DSM is clearly an optimiser: purchases are just in time, feeding depends on prices, and herd sizes shrink as the relevant shop unlocks later. It probably scores marginal value per tile against a demand model. The fits reproduce the counts well for sheep (R² 0.97), cows (0.92), strawberries (0.90) and tomatoes (0.70), less well for geese (0.77 only with the remainder model) and carrots (0.56).
- Not explained: the step-13 batching variant (1d) and the 12% of unfed goose-days (7d).
- The hand routing (which unit walks where) was not analysed. The unit-level day-0 tape in 1a is exact; after day 0 only the tile outcomes are reported.
