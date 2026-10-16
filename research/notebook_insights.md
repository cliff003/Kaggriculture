# Kaggriculture: what the public notebooks (and the top replays) say about the strongest agents

Team 42 research note, 2026-09-24 (about 19:30 UTC). Research only: nothing was submitted.

Tags used below:
- **[V]** = verified by me: engine source (`kaggle_environments` 1.32.7), a replay re-simulation, or the rendered notebook output itself.
- **[C]** = a notebook author's claim that I did not re-test.
- **[C, output]** = a number printed by the notebook's own code in its latest run (I read the rendered output, but did not re-run it).

---

## 0. TL;DR

1. **The top teams are adaptive programs, not tape replayers, and three of the top five (plus UMG) share one lineage.** DSM, DECEM and Vadim Vasilenko open with the same two market lists in every one of their 349 seats. Unknown Mother-Goose (UMG, rank 5) matches on step 0 in 117 of 117 seats and on step 1 in 103. Their field plans agree on 43% of turns 1-47 (DSM vs Vadim), then drift below 5% after turn 300. Unrelated pairs agree on 0-3%. destbreso's x-ray labels UMG as ADAPTIVE / SCHEDULER, with the plan varying on 98% of turns even within the same shop world. [V]
2. **Verified profile of a top-5 farm (median over 547 top-5 seats on 2026-09-22):**
   - Land: NE on day 6, SW on day 9.
   - Animals: 2 cows and 3 sheep at the start, then 9 cows by day 9 and about 5 geese by day 11. Sheep stay at 3 unless YARN_STORE shows up early, in which case the farm holds about 11 sheep by day 20.
   - Crew: hands ramp 4 (day 1), 6 (day 3), 8 (day 6), 9 (day 8), 11 from day 10. Hiring costs about $5.4k a season.
   - Crops: about 157 wheat, 38 carrot, 29 strawberry, 11 melon and 11 tomato plantings.
   - Other work: about 204 FERTILIZE and 365 CARE actions. Only about 190 of the roughly 7,000-8,000 unit-turns are PASS.
   - Result: about $137.7k revenue and a final bank of about $109.8k. [V]
3. **Differences from our public base cha22 (80 self-play games, same code as the top public notebooks):** [V]
   - **Tomatoes.** The top five plant them in 98% of games and hold a median of 10 tomato tiles on days 18-20. cha22 plants them in 11% of games, with a median of 0.
   - **Geese.** The top five keep 5 geese against cha22's 3, and earn $8.0k from eggs against $4.2k.
   - **Fertilizer.** The top five run about 204 FERTILIZE actions (43-48% on wheat, 31-38% on strawberry) and buy none. cha22 runs about 117 (54% on strawberry), buys 88 units and sells 336.
   - **Idle labour.** The top five have 190 PASS unit-turns, cha22 has 471.
   - **Cash curve.** Top-five cash stays near $0 until day 9 ($261 against cha22's $2,833) and is lower on day 10 ($5.7k against $16.0k). They are ahead by day 15 and finish about $9k higher: day 25 $84.1k against $76.0k, day 28 $101.3k against $91.2k.
   - **Endgame animals.** The lineage releases its sheep after the last wool and trims cows from 9 to 6 over days 22-28. cha22 feeds 6 sheep and 7 cows to the end.
4. **Sale behaviour.** The top five sell on about 290 turns per game in tiny lots (median 2 units of a premium good for the lineage, against 4 for cha22). They put the first SELL in market slot 0 on 99.9% of sell turns and almost never place HIRE or BUY ahead of a SELL (0.06%). About 34-37% of their premium units are sold in the same turn as the opponent sells the same item. [V]
5. **DSM (rated 3071.7, rank 1) is not ahead on prices.** In its 25-1 record against Vadim, both realise the same price per unit on every product. DSM wins on volume: more wheat, carrot, tomato and egg units. It trails in cash until about day 18, then leads by $4.2k on day 28. DSM buys the SE quadrant (for $4k) in 61% of games, almost always on day 10 at hours 13-14, but it also won 49 of 49 games without SE, so SE is not the cause. [V]
6. **Market mechanics are real and exploitable at the margin.** The engine processes both players' orders slot by slot, in lockstep, one unit at a time. HIRE and BUY_LAND take a slot, and player 0 goes first. Sales at $1 do not add to market inventory. The last action that executes is at step 718. All of this is verified in the engine source. Notebook claims built on it:
   - a step-1 wheat "squeeze" and a smaller first-turn round trip (goodpjw2008);
   - opening feed denial;
   - selling fertilizer one turn before the opponent (raykkretzschmar);
   - leading sales by 1-4 turns in mirror games (several authors). [C]
7. **Shop draws depend on the seed, the day, and the number of empty tiles on both farms.** The engine consumes one RNG draw per empty unlocked tile for weeds before it picks the shop. On the same 80 seeds, cha22 self-play reproduced the original game's first two shops in only 19 games and the first three in only 5. Seeds do not pin down worlds in local tests. Steering the draw live would need the hidden 31-bit seed, so it is not practical. [V]
8. **Replay data is available.**
   - Official daily datasets: `kaggle/kaggriculture-episodes-YYYY-MM-DD`, 56 days, 38,544 top-rated games.
   - `ashok205/kaggriculture-top10-replay-archive`: 24,772 games involving each day's top-10 teams, 3.66 GB, one parquet shard per day.
   - `georgymamarin/kaggriculture-episodes`: 224,627 episodes, with 195,391 full replays and per-seat features.
   - I downloaded the 2026-09-22 top-10 shard (616 games). All 616 re-simulate locally to the exact server rewards. [V]
9. **Best live public notebooks (Code page Score = live rating).** Ahmed Berat Ozer's V38 at 2625.2 and V39 at 2621.2 lead. Next is "Master Engine V3" at 2615.2, which is byte-identical to cha22 (main.py sha256 127ed3e6). cha22 itself (2587.9) and "Multi-Route Farming Agent" (2581.7) carry the same file. Every top public notebook I opened is the same kind of agent: 13 recorded 719-step route tapes chosen from the first two shops, plus market layers. None reaches the gold line (about 2864).

---

## 1. Sources read

| # | Notebook | Kind | Live Score (Code page) | Local path under `research/notebooks/` |
|---|---|---|---|---|
| 1 | georgymamarin/kaggriculture-what-2600-farms-do-differently | analysis of the georgymamarin/kaggriculture-episodes corpus, daily rerun | none shown | `georgymamarin__kaggriculture-what-2600-farms-do-differently/` (+ `rendered_output.txt`, `output/*.log`) |
| 2 | tetsutani/demand-preserving-turn-sale-timing | agent packaging (cha22 bytes) + one self-play diagnostic | 2436.6 (updated 3 h before, still settling) | `tetsutani__demand-preserving-turn-sale-timing/` |
| 3 | destbreso/x-ray-your-agent | replay x-ray of the #1 submission at run time (UMG, 3060.8) | none shown | `destbreso__x-ray-your-agent/` (+ `rendered_output_2026-09-24.txt`) |
| 4 | leoprovorov/agent-analytics | browser replay tool + "God's Mode: Hacked Stores" agent bundle | 1853.8 | `leoprovorov__agent-analytics/` (+ `extracted/` decoded bundle incl. `shop_predictor.py`) |
| 5 | ashok205/top10-replay-dataset-archive | maintainer of the top-10 replay dataset | none shown | `ashok205__top10-replay-dataset-archive/` (+ `data/`, `analysis/`) |
| 6 | evgendvorkin/kaggriculture | rules map + analysis of three games by "the champion" (Boey) | 1862.6 (updated 2 h before) | `evgendvorkin__kaggriculture/` |
| 7 | degnonguidi/kaggriculture-utils-v1 | despite its title, a packaged copy of Ahmed Berat Ozer's V43 "Recovering Lost Harvests" agent (same title and text, pinned main.py sha256 919fc1d6) | 1582.4 (updated 1 h before) | `degnonguidi__kaggriculture-utils-v1/` |
| E1 | leoprovorov/kaggricult-man-reverse-engineering | route-map analysis (images) + MarketShock agent | 2579.4 | `leoprovorov__kaggricult-man-reverse-engineering/` |
| E2 | haideptry/demystifying-2900-meta-reflex-engine-and-bot | "2900 meta" write-up + public V39-based agent | 2387.4 | `haideptry__demystifying-2900-meta-reflex-engine-and-bot/` |
| E3 | raykkretzschmar/kaggriculture-findings-from-zero-to-top-meta | long replay diary Jul-Sep, top-team convergence, loss audits | n/a (not in top list) | `raykkretzschmar__kaggriculture-findings-from-zero-to-top-meta/` |
| E4 | goodpjw2008/kaggriculture-melon-threshold-squeeze-2749 | market-microstructure analysis + agent (peak 2749) | 2367.4 | `goodpjw2008__kaggriculture-melon-threshold-squeeze-2749/` |

- Pulled notebooks carry no cell outputs. I read the rendered outputs (`__results__.html`) in a browser for #1, #3, #5 and #6, and for the top-scored agents V38, Master Engine V3 and Multi-Route.
- Kernel lists: `research/list_votes.txt` (sorted by votes) and `research/list_score.txt` / `list_score.json` (sorted by score). The CLI prints no score column, so the scores in section 5 come from the Code page.

---

## 2. What the top agents (2800-3070) do differently

### 2.1 Verified: 616 top-10 games from 2026-09-22, re-simulated

**Method**
- Source: shard `replays_2026-09-22.parquet` of `ashok205/kaggriculture-top10-replay-archive`, which holds 616 of the 620 official episodes that day.
- Each game was replayed through the local 1.32.7 engine with market commits, hires and land purchases instrumented. All 616 reproduce the server's final banks exactly.
- Groups:
  - "top5": DSM, DECEM, Vadim Vasilenko, 吃白饭的大肥鱼 and Majkel1337 (547 seats).
  - "other top10": UMG, M & M & P & Q, Kaggledew Valley, mtmr_s1, THIRD FARM CLUB and ymg_aq (581 seats).
  - "rest": the other opponents in the shard (104 seats, mostly rated 2850-3000; these are not public agents).
- Public comparison: cha22 (our current base, byte-identical to the best public notebooks) in 80 self-play games on the first 80 seeds of the shard.
- Values are medians per seat.
- Files: `ashok205__top10-replay-dataset-archive/analysis/` (`profile_2026-09-22_with_cha22.md`, `extra_2026-09-22_with_cha22.md`, `kinship_2026-09-22.md`, JSONL raw features, scripts).

**Caveats**
- This is one day's population.
- cha22 in self-play is a mirror. Two identical sellers depress premium prices, so its price columns are biased low. The structure, production and timing columns are fair.
- Worlds (shops) differ between the cha22 runs and the originals after the first draws (see 3.7).

**Headline comparison**

| metric | top5 | other top10 | rest | cha22 self-play |
|---|---|---|---|---|
| win rate in sample | 0.62 | 0.45 | 0.16 | 0.50 (mirror) |
| final bank | 109,780 | 109,567 | 101,168 | 100,352 |
| cash end of day 9 / 10 / 12 | 261 / 5,682 / 14,540 | 861 / 7,574 / 13,823 | 656 / 9,952 / 18,096 | 2,833 / 15,974 / 18,750 |
| cash end of day 15 / 20 / 25 / 28 | 30,193 / 61,689 / 84,101 / 101,317 | 26,402 / 57,074 / 81,006 / 98,456 | 29,770 / 57,089 / 78,032 / 92,428 | 28,511 / 57,608 / 76,029 / 91,246 |
| NE / SW purchase day | 6 / 9 | 6 / 9 | 6 / 8 | 6 / 11 |
| SE bought (share, day) | 14% (DSM 61%), day 10 | 25%, day 10 | 0% | 19%, day 18 |
| cows / sheep / geese, day 5 | 2 / 3 / 0 | 2 / 3 / 0 | 2 / 3 / 0 | 4 / 2 / 0 |
| cows / sheep / geese, day 15 | 8 / 3 / 5 | 8 / 5 / 5 | 7 / 4 / 3 | 8 / 6 / 3 |
| cows / sheep / geese, day 28 | 6 / 0 / 4 | 6 / 2 / 4 | 6.5 / 2 / 3 | 7 / 6 / 2 |
| hands on day 1 / 3 / 6 / 8 / 10 / 20 | 4 / 6 / 8 / 9 / 11 / 11 | 3 / 5 / 8 / 9 / 11 / 11 | 4 / 5 / 8 / 9 / 12 / 11.5 | 3 / 5 / 7 / 8 / 11 / 11 |
| hire cost per season | 5,442 | 5,174 | 5,893 | 4,397 |
| plantings: wheat / carrot / tomato / strawberry / melon | 157 / 38 / 11 / 29 / 11 | 145 / 40 / 11 / 31 / 14 | 150 / 33 / 9 / 28 / 13 | 154 / 40 / 0 / 33 / 12 |
| tomato planted in share of games; first tomato day | 98%, day 11 | 96%, day 11 | 90%, day 12 | 11%, day 18 |
| tomato tiles on day 18-20 (median) | 10 | n/a | n/a | 0 |
| FERTILIZE / CARE / PASS unit-actions | 204 / 365 / 190 | 195 / 331 / 622 | 175 / 319 / 550 | 117 / 404 / 471 |
| fertilizer sold / bought (units) | 231 / 0 | 234 / 22 | 232 / 14 | 336 / 88 |
| wheat bought (units, average price) | 172 @ $37 | 149 | 168 | 128 @ $41 |
| revenue total | 137,691 | 138,965 | 132,032 | 128,987 |
| revenue: strawberry / milk / wheat / wool / melon | 30.9k / 20.5k / 16.2k / 14.0k / 13.6k | 30.1k / 19.6k / 16.1k / 15.9k / 15.5k | 25.5k / 16.8k / 16.4k / 15.5k / 16.4k | 28.7k / 14.4k / 14.9k / 14.4k / 14.3k |
| revenue: fertilizer / egg / tomato / carrot | 12.4k / 8.0k / 5.1k / 5.0k | 12.7k / 7.2k / 5.2k / 4.9k | 12.1k / 4.3k / 4.1k / 4.7k | 15.2k / 4.2k / 0 / 5.2k |
| realised price / base: strawberry, milk, wool, melon | 1.28, 0.70, 0.70, 0.83 | 1.26, 0.74, 0.73, 0.74 | 1.19, 0.67, 0.67, 0.80 | 1.00, 0.68, 0.58, 0.79 (mirror) |
| revenue share by days 0-10 / 11-20 / 21-26 / 27-29 | 16 / 47 / 22 / 16 % | 16 / 42 / 24 / 17 % | 21 / 43 / 21 / 15 % | 22 / 41 / 22 / 15 % |
| stranded value at the bell (mean) | $49 | $36 | $40 | $0 |
| sell turns per game | 289 | 179 | 239 | 270 |
| first SELL in slot 0 / HIRE or BUY placed before a SELL | 99.9% / 0.06% | 91.7% / 1.65% | 99.1% / 0.78% | 98.6% / 0.14% |

**Product mix by shop type** [V]. The first 3 shops are the ones unlocked by day 9. Each cell reads "shop among the first 3 / shop not among them".

| shop | product | top5 revenue share | cha22 revenue share | top5 structure | cha22 structure |
|---|---|---|---|---|---|
| YARN_STORE | wool | 26.6% / 8.3% | 30.5% / 7.5% | sheep on day 20: 11.5 / 3.8 | 12.2 / 5.5 |
| PET_CAFE | carrot | 9.7% / 2.7% | 10.4% / 3.5% | carrot plantings: 86 / 30 | 64 / 37 |
| PIZZA_SHOP | tomato | 6.9% / 3.2% | 2.4% / 0.6% | tomato plantings: 17 / 8 | 2 / 1 |
| FARMERS_MARKET | tomato | 5.5% / 3.9% | 2.7% / 0.7% | tomato plantings: 12 / 11 | 2 / 1 |
| BAKERY | egg | 9.2% / 4.9% | 4.8% / 2.0% | geese on day 20: 7.3 / 4.6 | 3.1 / 1.8 |
| BRUNCH_SPOT | egg | 7.8% / 5.2% | 3.0% / 2.7% | geese on day 20: 6.7 / 4.7 | 2.6 / 1.9 |
| SMOOTHIE_SHOP | milk | 19.5% / 14.0% | 21.7% / 13.0% | cows on day 20: 10.3 / 7.7 | 8.6 / 7.1 |
| ICE_CREAM_SHOP | milk | 19.5% / 13.8% | 21.3% / 13.2% | cows on day 20: 10.3 / 7.6 | 8.5 / 7.1 |

Reading: cha22's routes already react to the yarn, pet-cafe and dairy worlds. They barely react to tomato worlds (pizza, farmers market) or egg worlds (bakery, brunch). The top five add tomatoes and geese in exactly those worlds.

**More verified details**
- **Openings (step 0 / step 1 market lists).**
  - DSM, DECEM, Vadim (every seat) and UMG (step 0 in 117 of 117 seats, step 1 in 103 of 117): `[BUY_ANIMAL COW 1, BUY_PRODUCT WHEAT 5]` then `[SELL WHEAT 1, HIRE x4, BUY_ANIMAL COW 1, BUY_ANIMAL SHEEP 3]`.
  - Majkel1337: `[BUY_ANIMAL COW 2, BUY_ANIMAL SHEEP 2, BUY_PRODUCT WHEAT 6]` then `[HIRE x2, COW 1, SHEEP 1]`.
  - 吃白饭的大肥鱼 and THIRD FARM CLUB use one-turn openings that buy melon and wheat seeds at once.
  - cha22: `[BUY_PRODUCT WHEAT 5, BUY_SEED WHEAT 1]` then `[HIRE x5, COW 2, SHEEP 2]`.
  - No top team does a first-turn wheat round trip.
- **Fertilizer targets.** FERTILIZE actions go to wheat 43-48%, strawberry 31-38%, carrot 7-14%, tomato 8-11%, melon about 0% (all five teams alike). cha22 splits them wheat 32%, strawberry 54%, tomato 2%.
- **Crop rotation.** The top five hold 26-28 strawberry tiles on days 12-18, cut that to 9 by day 24, and switch to fast crops: about 30 wheat tiles and 10 carrot tiles on day 24. cha22 keeps 33 strawberry tiles to day 20 and 17 on day 24.
- **Endgame animal pruning.** The lineage's 3 sheep (all bought on day 0) are gone by the end of day 28, meaning they stop being fed after the last wool on day 27. Cows fall from 9 to 6 between days 22 and 28. Majkel releases its sheep too. cha22 keeps 6 sheep and 7 cows to the end. The behaviour is verified; the motive (saving wheat and labour) is my inference.
- **Sell races.**
  - Median premium lot: DSM, DECEM and Vadim 2 units; Majkel 3; top10 others 4; cha22 4; 吃白饭的大肥鱼 6.
  - Contested share (the opponent sells the same item in the same turn): 34-37% for the lineage, 27% for Majkel.
  - Inside contested turns both sides get almost the same price (DSM 0.85 against 0.84 of base), which is what lockstep predicts.
  - Majkel is the clear front-runner: 51.7k premium units sold within 4 turns before the opponent sold the same item, against 31.3k within 4 turns after.
  - Weaker agents are late: 吃白饭的大肥鱼 7.0k before against 11.4k after; rest 19.6k against 28.7k.
- **Head-to-head records in the sample.**
  - DSM: 25-1 against Vadim, 26-0 against Majkel, 6-1 against DECEM, 9-1 against UMG, 16-1 against THIRD FARM CLUB. 117 of 127 overall (92%), median margin +$6,569.
  - Vadim: 25-7 against Majkel.
  - 吃白饭的大肥鱼: 6 of 35 (it was ranked #4 on 9/24 but played poorly in this sample).
- **DSM against Vadim, why DSM wins.**
  - Realised price per unit is equal on every product: strawberry 1.19 against 1.18, milk 0.66 against 0.65, and so on.
  - DSM sells more units: wheat 503 against 431, carrot 156 against 114, tomato 98 against 78, strawberry 229 against 213 per game. Revenue is $136.3k against $129.0k.
  - Cash lead by end of day: day 10 -2.1k, day 16 -1.0k, day 18 +0.4k, day 24 +1.6k, day 28 +4.2k.
  - Against DECEM DSM trails by 3-5k until day 22 and wins by +3.9k on day 28.
  - The edge is production volume in the last 12 days, not market timing.
- **DSM's SE quadrant.**
  - Bought in 78 of 127 games, 61 of them on day 10 at hour 13-14.
  - Frequency depends on the opponent: 4/10 against UMG, 11/26 against Vadim, 12/26 against Majkel, 14/15 against mtmr_s1, 7/7 against DECEM.
  - I found no simple cash rule behind it.
  - Use from day 16 on: about 8 wheat, 4 strawberry, 3-4 tomato, 3-4 carrot tiles and 3-4 sheep, with 6-7 tiles left empty.
  - Win rate is 87% with SE and 100% (49/49) without.
  - Among other SE users, mtmr_s1 fills SE with wheat, carrot and tomato (18, 13 and 12 tiles on day 12) and M & M & P & Q builds a 7-goose coop block. cha22's SE (19% of games, day 18) holds 6 sheep and later 10 tomatoes, with 15 tiles empty.
- **Lineage test (plan agreement = farmer and hands identical in the same turn).**
  - DSM vs Vadim: 0.43 on turns 1-47, 0.16 on turns 48-143, 0.14 on turns 144-299, 0.04 on turns 300-718. Market agreement: 0.93, 0.76, 0.58, 0.33.
  - DECEM vs Vadim: 0.15, 0.03, 0.04, 0.03.
  - Unrelated pairs (for example DSM vs Majkel): 0.01-0.03.
  - Reading: a shared codebase or ancestor with a live scheduler that composes the plan per game.

### 2.2 Notebook claims about top agents (dated, attributed)

**destbreso, x-ray of #1 (UMG, submission 56489080, 3060.8 at run time)** [C, output]
- 115 ladder games, W102-L13, median margin +14,886.
- Losses were mostly against DSM (4 of 4: -3,484, -4,422, -9,260, -5,486), plus DECEM (-1,923, -741), Vadim (-471) and Boey (-5,499).
- Class: ADAPTIVE. It varies on 98.1% of turns with the first divergence at t=11, is ADAPTIVE in all 32 worlds, and is a "SCHEDULER (composes its plan per game)". Zero mirrors among its opponents.
- Macro profile:
  - second quadrant on day 6 (p10-p90: 6-6);
  - 352 CARE actions (297-428);
  - herd bought: 11 cows, 1 sheep, 6 geese;
  - fallow tiles on days 25-29: 7 (0-20);
  - $64 stranded at the bell (0-513);
  - about 324 pass-with-work unit-turns;
  - shed at cap on 1 turn;
  - 5 floor sells.
- Unit-turn split: work 45.5%, carry 5.0%, move 45.0%, idle 4.5%.

**destbreso, reference numbers** (his 2026-08-30 capture) [C]
- The #1 of that date bought its 2nd quadrant on day 5, had 7 cows and about 280 CARE actions, left 13 tiles fallow late and $442 stranded.
- Field staffing consensus (490 seasons): 4 hands to day 4, 8 by day 6, 11 by day 10, 12 from day 13, IQR 0-2 hands.
- A leader spent 53.8% of unit-turns moving and 3.8% idle; a mid-table agent 42.9% and 11.8%.
- One top-30 agent buys SE in 12% of games, always on day 18, and plants exactly 10 tomato tiles there.
- "Nothing observable differs before turn 48."

**georgymamarin, "2600+" snapshot** (Sep 23, crawl corpus) [C, output]
- 2600+ is the top 4.1% (400 of 9,851 teams).
- The 2600+ band (627 seats) and the middle band (1,725 seats, rated 1,824-1,872) are nearly identical:

  | metric | 2600+ | middle |
  |---|---|---|
  | first land day | 6 | 6 |
  | peak crew | 12 | 12 |
  | hires | 268 | 270 |
  | plantings | 239 | 239 |
  | carrot | 39 | 31 |
  | melon | 12 | 12 |
  | strawberry | 33 | 33 |
  | tomato | 0 | 0 |
  | wheat | 155 | 162 |
  | final bank | 97,553 | 97,210 |

  So the 2600 band plays the public game, and the tomato column (0) matches cha22, not the 3000+ teams.
- Record bank 220,271 (Nathael: crew 13, land on day 6, wheat-led).
- Winners' bank: 76,409 at p25, 94,486 median, 133,131 at p90.
- Top farms cross 10% of their final bank on days 12-14.
- Rank correlation with bank across 389,886 seats: wheat plantings +0.08, first land day -0.01.
- Half of all games dump wool to $1.
- The median winning bank rose from 37,002 to 99,704 over the season (+169%).

**haideptry** [C]
- The 2900 meta is "route chassis + reflex stack".
- RACE reflex: detect rival dumps from inventory deltas and pull sales forward by up to 40 turns.
- "Top private agents buy about 9 tomato seeds from about day 12 and hold 10+ tomato tiles by day 20." My data confirms this: median 11 tomato seeds and 10 tiles on days 18-20; 51% of seats hold 10 or more on day 20. [V]

**raykkretzschmar** (Aug 3 to Sep) [C]
- Early-August top-5 teams all ran variants of one plan: 8 cows / 5 sheep / 5 strawberry / 12 hands / 3 quadrants. Tapes differed on only 2-5 field turns.
- A ten-team refresh found about 8 cows, 6 sheep, 3 quadrants, 12 hands, 21 melon seeds and 44 strawberry seeds.
- On Aug 9 one field hash appeared in 144 episodes from 40 teams.
- The edge moved to market timing: c18 changed 20 field turns but 112 market turns.
- His C70 went 83-5 (+14,196 mean margin) but stalled below 3000 because the rating counts wins, and it lost the close games.

**cha22 author** (via the flexonafft copy) [C]
- The deficit against the strongest opponents is late-game conversion: "our money path leads through day 17, then loses days 18-29".
- It is not the shop draw.
- Across 11k public replays, the most robust winner-vs-loser difference is realised price per unit, +8-10%.
- My data agrees on the late-game gap. On price, the top five do realise +7-8% over "rest" on strawberry and wheat, but DSM beats Vadim with equal prices.

**evgendvorkin, Boey games** [C, output]
- Episodes 112509185, 112519767, 112531901. Banks 87,492 / 107,837 / 101,957; margins about 5k / 13k / 5.5k.
- Cash 0-400 through day 10, 6.6-9k on day 11, then +2-3k per day.
- Frequent `SELL WHEAT n` + `BUY_PRODUCT WHEAT n` pairs, frequent fertilizer sales, 9 HIREs in one turn.
- Caveat: its "PLANT counts" (wheat 27, melon 5, carrot 5-9) count only the farmer's own PLANT actions, not the hands', so they understate plantings about tenfold.

---

## 3. Mechanics and exploits

### 3.1 Market order lockstep [V: engine `_process_market`]
- Orders are processed index by index (at most 10 per player).
- In each slot, HIRE and BUY_LAND execute first, player 0 then player 1.
- SELL and BUY orders then run one unit at a time: both players are quoted at the same pre-commit inventory, then both commit. Prices refresh after each slot.
- Buys are quoted at post-buy inventory, so a buy followed by a sell nets zero against an unchanged market.
- Sales at $1 do not add inventory.
- Consequences:
  - A SELL at an earlier index than the opponent's same-item SELL gets the better prices.
  - HIRE, BUY_SEED and BUY_ANIMAL placed before your SELLs cost you slots.
  - The top five keep SELLs first in 99.9% of turns. [V]

### 3.2 First-turn wheat round trip and the "step-1 squeeze" [C: goodpjw2008, local simulations]
- When both players round-trip wheat on turn 0, the larger round trip loses; 10-15 units never lose.
- Buying 90 wheat in slot 0, selling it in slot 1 and buying your own 5 feed in slot 2 makes the rival's slot-1 `BUY 5` pay the lifted price.
- That costs a V4x-lineage rival about $50 before step 17, so it plants one melon fewer (about $1.3k final margin).
- Author's caveat: it only works against the public V4x lineage. Private top teams do not round-trip (confirmed [V]: their step 0 is `COW 1, WHEAT 5`).

### 3.3 Opening feed denial and one-turn preemption [C: raykkretzschmar, live-loss audit of his C92 at 2836.8]
- **Feed denial.** Opponents that bought 14-19 wheat before C92's slot-8 feed buy left it cash for only 4 feed units, and a sheep died on day 2. The four such losses averaged -13,606. Fix: move the existing 5-wheat buy to slot 0 on turn 0.
- **Fertilizer preemption.** In 11 losses the opponent sold fertilizer or wheat exactly one turn before C92's batch, swinging about 5,300-5,700 coins.
- **C94's fix:** sell at most 10 fertilizer one turn early and subtract that from the next sale. Result: 174-6 held-out, rank 1 in an 18-agent Bradley-Terry test (BT 1837).

### 3.4 Sale lead, reservation horizon, mirror probes, rival sniffing [C: several authors]
- Hamburger: a one-turn premium front-run in near-identical games went 6-0, +1,866.
- raykkretzschmar C45: a 2-turn debt-tracked lead. A fixed 25-turn horizon regressed.
- C68 infers the opponent's sale horizon (1-6 turns) from market inventory changes, after removing its own sales and the deterministic town drain.
- V35 R44: cash-response probes detect mirror clones and widen the lead to 4 turns.
- goodpjw2008 / sdy623: a 4-turn tape sale advance, SELL front-loading, and a reservation horizon of 24.
- cha22 carries RACE (reservation from step 192, horizon 40, margin 12).
- leoprovorov's MarketShock: a 1-2 turn lead in mirror games during steps 336-646.
- haideptry's formula: `rival_sold = inv' - inv + town_draw - own_sold`.

### 3.5 Town drain timing [V: engine]
- Shops consume after the market at every step with `step % 4 == 0` (single-product shops take 2 units).
- The town center consumes at `step % 24 == 0`.
- The top five's sales are not aligned to this cycle (25% of revenue at `step % 4 == 0`, the uniform share). [V]

### 3.6 Endgame [V: engine]
- The interpreter marks DONE while processing step 718, so the action for step 719 never executes. raykkretzschmar found this empirically.
- Unsold stock is worth $0. The top five strand a mean of $49.

### 3.7 Shop unlock RNG [V: engine `_end_of_day` + my test]
- `rng = Random(seed*1_000_003 ^ day)`. For player 0 and then player 1, each empty unlocked tile consumes one `rng.random()` (weed chance 0.005). Then, on unlock days, `rng.choice(sorted(SHOPS))` picks the shop.
- So the next shop depends on the total number of empty tiles on both farms at the end of the day.
- leoprovorov's `shop_predictor.py` (in `leoprovorov__agent-analytics/extracted/`) filters a seed posterior from the observed weed draws, but it is telemetry only. The seed is 31-bit and hidden, so live steering is impractical.
- My test: cha22 self-play on the same 80 seeds matched the original first shop in 39 of 80 games and the second in 51 of 80 (checking each position on its own). The first two shops together matched in 19 of 80, the first three in 5, and no game matched four in a row.
- Consequence for us: seed-fixed local "worlds" are not identical across agents unless their tile usage matches. Use a forced-shop tool such as `tools/forceshops.py` for controlled A/B tests.

### 3.8 Animal math [V: engine `_daily_refresh_animals`]
- A sheep placed on day 11 produces on days 17, 20, 23, 26 and 29 (5 wool harvests). Placed on day 12 it produces only 4 times.
- With daily FEED + CARE, each production pays base 1 + banked care: cow 3 (interval 2), sheep 4 (interval 3), goose 2 (interval 1).
- The first production is capped at `max_held`: 6 for cows and sheep, 4 for geese.
- An unfed animal escapes after 2 consecutive unfed days, so stopping FEED after the last useful production removes it at the next refresh. This matches the top five's day-28 sheep drop.

### 3.9 Loader trap [V: `kaggle_environments.agent.get_last_callable`]
- The entrypoint is `[v for v in env.values() if callable(v)][-1]`, the last callable in module-dict order.
- Rebinding an existing name does not move it to the end, so a helper defined after `agent` becomes the entrypoint.

### 3.10 The fourth quadrant (SE, $4k)
- raykkretzschmar's August result was broadly negative: every four-quadrant variant lost 10-0 to his C92. [C]
- In today's top-10 games SE is common: DSM 61%, mtmr_s1 87% (98 of 113 seats), M & M & P & Q 96% (48 of 50). DSM wins with or without it. [V]

---

## 4. Replay datasets we can use

| Dataset | Owner | Contents | Size / games |
|---|---|---|---|
| `kaggle/kaggriculture-episodes-index` + daily `kaggle/kaggriculture-episodes-YYYY-MM-DD` | Kaggle (official) | `manifest.csv` lists one dataset per day (ZIP of `manifest.csv` + replay JSONs, with `avg_score` / `min_score` per episode) | 56 days (2026-07-30 to 09-23), 38,544 episodes, 608-928 per day, about 21.4 GB per day. Recent days are top-rated games (median avg_score 3,019-3,085). [V: manifest downloaded] |
| `ashok205/kaggriculture-top10-replay-archive` | ashok205 | Nightly filter of the official data: full replays of every game involving that day's top-10 teams (ranked by max avg_score). Files: `replays_<date>.parquet` (zstd, one replay per row group), `episodes.parquet` (36,908 team-episode rows with date, episode_id, team_name, daily_rank, opponent, participants, scores), `top10_history.parquet` (550 rows), `processed_days.json` | 55 shards (07-30 to 09-22), 24,772 unique episodes, 3.66 GB. The 09-22 shard has 616 games (DSM 127, DECEM 69, Vadim 153, 吃白饭的大肥鱼 35, Majkel 163, UMG 117). [V: downloaded; all 616 re-simulate exactly] |
| `georgymamarin/kaggriculture-episodes` | georgymamarin | Nightly crawl of the public episode service: `episodes.csv`, `agents.csv` (ratings per seat), `teams.csv`, `episode_features.csv` (per seat: final_money, total_hires, peak_crew, first_land_day, plants_* ...), `stream_hashes.csv`, `daily_stats.csv`, monthly `replays_*.parquet` | 224,627 episodes, 195,391 with replays (87%), 65,604 submissions, 6,781 teams. Replays about 25 GB; CSVs about 115 MB. [C, output; file list V] |
| `destbreso/kaggriculture-benchmark-matchups` | destbreso | 45k recorded pairings with resolved seeds (CC0), used by his "Measure Your Agent" harness | [C, not downloaded] |
| `evgendvorkin/repley-1-mesta` | evgendvorkin | 3 replays of Boey games | [not downloaded] |
| `leoprovorov/agent-analytics-tool` | leoprovorov | Single-file HTML replay analyser: projected value, idle hands / empty tiles, per-step agreement, 64-world grid | [not downloaded] |

Practical note:
- The project venv has no pyarrow. I used a separate venv in the session scratchpad (uv + pyarrow) so the project was not touched. To reuse the scripts in `analysis/scripts/`, install pyarrow somewhere.
- The re-simulator (`resim_top.py`, `resim_extra.py`) replays both seats through the engine and logs every executed market unit. It takes about 0.8 s per game.

---

## 5. Public notebooks by live Score

Scores were read from the Code page sorted by Public Score, about 19:30 UTC on 2026-09-24. They are live and move by roughly ±30 even for identical code. The first 20 of 180 listed:

| # | Notebook | Score | Approach |
|---|---|---|---|
| 1 | ahmedberatozer/kaggriculture-v38-smarter-feed-stronger-margins | 2625.2 | V-series: 13 route tapes (yhay81 Shop Router 0909) + value-based feed skipping, protected fertilizer surplus sales, worker planning, reservation and mirror-probe layers, SE six-sheep expansion (prvsiyan V234). Local: 66.7% points against 144 records of 18 teams rated 2900+ (V37: 59.0%) [C, output] |
| 2 | ahmedberatozer/kaggriculture-v39-ready-before-the-rush | 2621.2 | V-series successor (not read in detail) |
| 3 | guruprasaathas111/kaggriculture-master-engine-v3 | 2615.2 | Text describes "Master Engine V6", but the embedded main.py is cha22 (sha256 127ed3e6) [V, output] |
| 4 | ahmedberatozer/kaggriculture-v34-observed-market-timing | 2601.6 | V-series, observed-market sale timing |
| 5 | ahmedberatozer/kaggriculture-v53-opening-signature | 2597.5 | V-series |
| 6 | ahmedberatozer/kaggriculture-v55-one-turn-market-race-edge | 2595.8 | V-series, one-turn sale race |
| 7 | abhinav0370/cha22-agent | 2587.9 | cha22 = public V39 + v9 layers (RACEPX gate, RACE reservation from step 192 with horizon 40 / margin 12, COURIER, CARROT, HERD) + queue hole-closure + late seed cap; 13 routes. Our current base |
| 8 | ahmedberatozer/kaggriculture-v41-review-candidate | 2586.4 | V-series |
| 9 | flexonafft/kaggriculture-multi-route-farming-agent | 2581.7 | cha22, byte-identical [V, output] |
| 10 | guruprasaathas111/kaggriculture-master-engine-v53e01d74d8f | 2581.0 | not read |
| 11 | leoprovorov/kaggricult-man-reverse-engineering | 2579.4 | MarketShock-M1-WR1K: frozen Seven-Turn Rescue + 1-2 turn sale lead in mirror games (steps 336-646) + day-21 watering repair |
| 12 | ahmedberatozer/kaggriculture-v31-production-and-sale-priority | 2575.6 | V-series |
| 13 | arsgorynich/kaggriculture-v43-local-confirmed | 2550.5 | V43 copy |
| 14 | ravi123a321at/177-180-fresh-top-30-v21-1-conditional-memory | 2517.1 | Kaito v21.1 copy |
| 15 | arsgorynich/herd-safe-v3-experimental-risk-aware-feed | 2513.3 | herd-safe feed layer |
| 16 | aurax7/kaggriculture-shop-router-reactive-v7 | 2510.0 | shop router + reactive layer |
| 17 | statma/kaggriculture-herd-safe-sale-window-race-ca20 | 2509.3 | herd-safe sale window race |
| 18 | nathanjacob/kaggriculture-pipe-5-terminal-boost | 2500.5 | pipe series |
| 19 | reyhanksatria/best-market-agent-high-strategy | 2497.9 | older market agent |
| 20 | ahmedberatozer/kaggriculture-v45-first-turn-wheat-round-trip | 2497.5 | V45 wheat round trip |

The notebooks I was asked to read:

| Notebook | Score | What it runs |
|---|---|---|
| tetsutani/demand-preserving-turn-sale-timing | 2436.6 | cha22 byte-identical; re-run 3 h before, so the rating is still settling |
| evgendvorkin/kaggriculture | 1862.6 | re-run 2 h before |
| leoprovorov/agent-analytics | 1853.8 | God's Mode: Hacked Stores = Farming Score V2 + shop overlay |
| degnonguidi/kaggriculture-utils-v1 | 1582.4 | V43; re-run 1 h before |

Reading:
- Every notebook in the top 20 that I opened is the same machine: a route-replay chassis plus market layers. The team README says the same about the whole top public band.
- The same cha22 file shows 2582-2615 on three settled notebooks, so a gap of 30 or less between public notebooks is noise.
- The best public score (2625) is about 240 below the gold line (2864) and about 450 below DSM (3071.7).

---

## 6. Implications for our agent

1. **Tomatoes where they pay.**
   - Plant about 10 tomato tiles from about day 11, and about 17 when PIZZA_SHOP or FARMERS_MARKET appears early.
   - Fertilize about 10% of FERTILIZE actions onto tomatoes.
   - cha22 almost never does this. Tomato is a `hinge` good (flat near base, steep above T=200) and the top teams realise 1.17-1.32× base on it.
2. **More geese, and earlier.**
   - Hold about 5 geese by day 11, and about 7 in BAKERY or BRUNCH worlds.
   - Egg revenue: $8k for the top five against $4k for cha22.
3. **Recycle fertilizer instead of selling it.**
   - About 200 FERTILIZE actions, mostly on wheat and strawberry. Never buy fertilizer.
   - cha22 buys 88 units at about $29 and sells 336 at about $45. The top five sell 231 at about $53.
4. **Reinvest the day-10 melon cash immediately** (cows to 9, geese, the SW quadrant on day 8-9, tomatoes) rather than banking it. Expect to trail on day 10-12 and lead from day 15.
5. **Rotate crops late.**
   - Pull strawberries after their 4 productions and move to wheat and carrots (about 30 wheat and 10 carrot tiles on day 24).
   - Stop feeding sheep after the last wool and trim cows in the last week.
6. **Cut idle labour** from about 470 to about 190 PASS unit-turns. Spend the freed labour on HARVEST, WATER and FERTILIZE.
7. **Keep the market hygiene we already have.**
   - SELL first in slot 0, which is our order-slot layer.
   - Trickle premium sales in 2-3 unit lots.
   - Consider sale-lead and fertilizer preemption only against mirror or V4x opponents: prices against the top five are symmetric within a turn.
8. **For evaluation:**
   - Worlds must be forced, not seeded (see 3.7).
   - The 616 re-simulated top games can serve as a benchmark, for example by replaying one seat's tape against our agent. The team's notes warn that a tape replayed against a different opponent degrades (104k fell to 54-71k), so use it to diagnose, not to score.
