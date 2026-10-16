# What did not work

Every idea we tested and dropped, with the number that decided it. "Replays" are live-replay counterfactuals, "panel" and "local" are games against local opponents that react (see [evaluation.md](evaluation.md)). A "flip" is a game whose winner changes. The final ranking only counts wins, so a change that added money but flipped a game to a loss was usually dropped.

## Contents

- [New engines instead of the replay base](#new-engines-instead-of-the-replay-base)
- [Copying the top teams](#copying-the-top-teams)
- [Production changes on the cha22 routes](#production-changes-on-the-cha22-routes)
- [Selling and timing](#selling-and-timing)
- [Arbitrage and counter-arbitrage parameters](#arbitrage-and-counter-arbitrage-parameters)
- [Bounds and dead ends](#bounds-and-dead-ends)

## New engines instead of the replay base

| Idea | Result |
|---|---|
| An adaptive scheduler in the style of DSM (final #3), written from scratch (Sep 24 to 25, about 60 variants) | The best was still 11.5k per game behind cha22. Taking over from the same day-10 state it lost 12k; following cha22's own daily layout it lost 21.7k. The gap is execution and selling, not the plan |
| From-scratch production agents p3, p4, p5 (Sep 26 to 27) | p3b -20.4k per game against v8; p4 -12.2k against v7c in a fair comparison without TICK, -9.4k after an automatic search; production targets read from DECEM's replays -13.8k to -20k (DECEM had switched to behaviour cloning about Sep 21, so these were the outputs of a cloned model) |
| Tape for the first D days, then our own engine | Lost for every D (switching on day 16: -6.9k; on day 26: -2.6k). On the same farm the tape earned 0.6k to 1k more per day |
| From-scratch production agent p6 (p4 plus parameters tuned by hill climbing on Kaggle, Sep 28 to 29) | The best configuration was still 7.9k per game behind v7c (baseline -9.1k), and 3 W / 70 L on replays of a strong production team's games. Execution was the problem: about 18 crop tasks per game that had to be done before night were still undone at hour 23, and tiles 5+ steps from the warehouse were missed 10 times as often as those within 3 |
| p6 executing someone else's plan: cha22's tape layout / a strong production team's full allocation / that team's own plan from its own seat | -21.2k / -18.9k / -19.1k per game; in the last case the team itself had been +7.3k in the same games. The same plan, executed worse, costs 20k |

## Copying the top teams

| Idea | Result |
|---|---|
| Grafting the then-leading team's (DSM) recorded actions onto the cha22 chassis | -29.8k per game; -15.8k even with each world's own DSM replay. Its strength is adapting to the game, so its recorded actions cannot be replayed onto another chassis; other teams copied it by closed-loop behaviour cloning instead (abozten, final #24; Unknown Mother-Goose, final #12) |
| Behaviour cloning of DSM (GPU training) | 0.88 action accuracy, but 0 wins in play against cha22 and v9 (its money ended at one sixth of the opponent's) |
| Copying top routes (then #11 and #29 on the live board) | The top 7 adapt, so their routes cannot be replayed as tapes; several gold teams copied them by behaviour cloning instead. The shop-prefix tape tree of #29 lost 7.5k per game against v8 and only matched v8 when all of the first 4 shops matched |
| A route library from a top production team's 27 replays, keyed by the first two shops, on the rescue chassis | 59.5k per game locally against 110.5k for V10_CarreraGT; 16 W / 51 L on replays of that team's games |
| Copying the evening sellers (milk held to 20:00, as Justin Yang, Arman and the Vadim family do) | 636 replays -868 per game, 88 flips lost, 1 won; -647 even on v7c without TICK. We sold at better prices, but the rival's morning lot sold even higher, and holding stock took the room TICK needed |
| Copying Gatswei's late carrots (wheat to carrots on days 20 to 26) | v8's own 51 games: 38 → 27 and 30 wins |
| Copying LK30's carrot swap at planting time | 147 carrot worlds 115 → 67 wins: less wheat starves the sheep, and the swap eats the tape's own carrot seeds |
| Copying the tomatoes of dodsters (then #66) | see the tomato row below |
| Porting Farmer John GS2's small delayed sales to v12_19 (Oct 1, after the deadline) | 20 games: 7 wins unchanged, -46.7 per game |

## Production changes on the cha22 routes

| Idea | Result |
|---|---|
| Route tables (switch the mid-game route by the first two shops) | 80 W / 16 L against our own champion, but 263 → 148 wins of 280 against the reacting cha22 family |
| Choosing the day-6 route by simulation; forcing one route in non-wool worlds | within noise |
| Re-picking the mid-game route with hindsight | even choosing the best route after the fact gained only 10 wins in 861 replays; fewer on held-out games |
| Tomatoes on the cha22 routes (copying dodsters, wheat to tomato, V219 for 1 or 2 tomato shops, 15 tomatoes in the south-east) | all lost: swapping 5 strawberry tiles for tomatoes -3193 per game on 413 replays (wins 394 → 229); wheat to tomato -2.8k to -7k per game; 15 tomatoes 148 → 69 wins of 148 locally |
| More tomatoes beside V219 with one more helper (TOMX); south-west strawberries replaced by tomatoes | 475 tomato-world replays -580 per game, 65 flips lost; -3k to -12k per game |
| Plain relaxation of the V219 gate to 2 shops (without the early-opening condition) | 722 replays 633 → 620 wins, 18 flips lost (the gated version became v10) |
| Lowering the 18-tomato gate from 4 shops to 3 or 2; widening the 10-tomato early window from 24 to 21 or 18 shop-days | -56 per game on 16 games, no wins gained; -194 per game, with near losses getting worse |
| Three ways to fix the 18-tomato execution | -61 / +40 / -85 per game on 80 games, no flips won |
| Four tomato crews from day 24 (crew4_full) | +4920 per game in tomato worlds, but one panel game flipped to a loss (the crews cost 5401 for 3204 more revenue); shortened to days 27 to 29 it became v12_18 |
| Strawberry for wheat in strawberry-scarce worlds | 191 replays 177 → 103 wins |
| Wheat for strawberries / strawberries for wheat in same-family games | wheat to strawberries lost all 120 games (-9k per game); strawberries to wheat let the rival earn 14k more. Only goods the rival does not produce can be added |
| Strawberry expansion in the south-east; a 16-plant strawberry block on day 13 (v12_16; the 24- and 25-plant variants lost 1.5k to 9.5k per game) | 80 games 72 → 50 to 58 wins; the block's three triggered worlds +703, -3835, +26. Land at 4000, seeds at 1600 and helpers from the 11th hire of the day on (89 to 610 each) eat the revenue |
| Skipping the 13 south-west strawberries on day 11 in low-strawberry worlds | 459 replays -2261 per game, 143 flips lost; -167 per game even where demand was zero |
| Late strawberries replaced by 8 geese in low-strawberry worlds (G1a) | only +0.8k to +1.0k per triggered world; no loss within 1.5k among the 96 triggered games, so nothing to flip |
| Early rolling carrots (G3); moving the CARROT last swap day from 23 to 25 or 26; looser CARROT gates | carrot to wheat price ratio 1.1 to 1.4 on days 12 to 20, below the 1.45 needed to break even; 2 to 5 games change with 1 flipped loss |
| Price-based carrot swap (ported from the rescue lineage) | 607 replays, wins unchanged; it rarely triggers |
| Six more sheep (SHEEPX with 2 or 3 wool shops); V233 sheep with one wool shop | -519 per game, 60 flips lost; -2601 per game, 173 flips lost |
| Geese instead of sheep in egg worlds | flat on average |
| Late geese, sheep or cows | land, Fibonacci helpers and 1 wheat a day per animal are never recovered |
| Switching off the base's HD2 animal choice | -301 per game, 29 flips lost |
| Relaxing the R51 fertilizer helper | more money but fewer wins: 353 against 376 of 420 locally, 366 against 367 of 413 replays |
| Workers picking up extra fertilizer for FERTMORE (`--extra 2`) | it takes fertilizer the route needs later; large losses |
| Stop feeding low-value animals | -7k per game: the market is shared, and producing less raises the rival's prices |

## Selling and timing

| Idea | Result |
|---|---|
| Selling all high-value goods on arrival at any time (early version of eager sell) | 0 W / 6 L, -2.0k per game; the price band and the time window turned it into v6's eager sell |
| Eager band 0.2× to 1.4× (v7); floors 0.4 or 0.5; floor 0.2 against the mirror family | 0.2 sold too early against steady rivals (420 fresh worlds: v6b 365, v7 300 wins); +23 and +6 per game but 1 and 5 fewer wins; 0.2 only helped against our own old versions (-130 to -175 per game against others) |
| Batched eager selling at high prices | 316 replays: 5 to 7 fewer wins |
| Eager sell for eggs, carrots and tomatoes too | +13 per game, no flips |
| Eager sell or order-slot from day 6, 8 or 10 | identical games: cha22 already sells on arrival on those days (day 6 was neutral apart from replay distortion) |
| Holding goods until the next morning or longer | -15k to -88k per game: the goods never sell |
| Holding milk and wool until 20:00 against evening sellers (90 games, exact pricing) | milk: us -31, rival +2544; wool: us -1893, rival +4318. Our early sales had been holding down their evening price |
| Countering evening sellers | it misfired against mirrors (the tape sells strawberries in the afternoon too); -178 per game against the others, 3 flips lost |
| Selling fertilizer early at 19:00 to 21:00 | won in self-play, hurt against the family (14 W / 26 L against emu_eager) |
| Wheat lead of 3 steps | clearly worse (27 W / 13 L against cha22; 38 W / 2 L with 2 steps) |
| Following the rival's sales | -561 per game |
| Racing the rival for melons on day 10 | both sides' workers reach the north-west melons at the same step; nothing to win |
| Wool drip (selling half a meal at a time in surplus) | -0.4k to -1.8k per game against mirrors, +0.7k against Vadim |
| A marginal-price floor for all sales (mcap) | 0.3× throughout: -858 per game (15 games better, 144 worse); only after day 27: -136 |
| Fertilizer sandwich, fertilizer shorting, sales capped by marginal price, stopping feed in the last days | sandwich smoke tests -3.9k to -10.5k per game; we sell fertilizer as it comes, so there is no stock to short; caps -375 to -1714 per game; the tape already stops feeding |
| Oracle reordering of our orders | -4k to -12k per game |
| Squeezing premium sells into a full order list at the tick (v12_10); delaying tick-step sells until after the town has eaten | -429 per game (rivals are blocked by hiring in that slot too, so waiting one step is better); -154 per game and +1024 for the rival (mirrors sell in the same step) |

## Arbitrage and counter-arbitrage parameters

| Idea | Result |
|---|---|
| TICK without the peer guard | buying high and selling low: -3k to -11k per game against slot-0 arbitrageurs |
| TICK's sell forced into slot 0 ahead of our milk sells | it pushed our milk sales back: -451 per game (Sep 26); retested on Sep 28: -717 per game, 116 flips lost |
| TICK switched off | 11 of 13 narrow losses got worse; retested on the ace (Sep 29): 1504 replays 1224 → 1115 wins (3 flips won, 112 lost), -616 per game |
| TICK starting earlier: day 6 or 8 on v8 (default day 10); days 8, 10, 11 or 12 on the ace (default day 13) | on v8 +4 per game with no flips (it barely triggers early); on the ace, days 8, 10, 11: 1239 → 1240 wins of 1528 each, flat on the latest 449; days 10 and 12 cost one flipped game each in the 917-replay set |
| TICK minimum gain 1 or 6; lots of at most 60 | +2 / -63 (3 games up, 4 down) / -192 (3 up, 15 down) |
| Skipping TICK after a rival's large buy (50 or 30+) the step before | no game changed in 1504 replays: the flow is only visible a step later, and TICK had already stopped in those games |
| Turning off the flow reconstruction in the trap guard (`GUARD=0`) | blind to pre-buy traps; the kwon game lost 18k again |
| rev_guard stopping after a single reversed round; stopping without recognising reversals (cg3) | the 11 changed games all got worse; identical on replays, but only 8 wins of 30 against the emulated anti-fader |
| Following small arbitrageurs instead of stopping (mirror, th30) | 49 arbitrage replays 41 → 43 wins but 2 flips lost; -15 per game and 2 flips lost |
| FADE parameters: starting after a single cycle, resuming after 3 cycles instead of 6, blind first round of the scheduled fade, position floor 80 or ceiling 95, cap3 | money up or down by small amounts, but each flipped 1 or 2 games to losses or changed only 2 games; the original parameters stayed |
| Only resuming TICK, without FADE (v8r) | 60 W / 0 L against v8, but 2 fewer wins on live replays |
| A defence-only trap guard (v8b) | turned Sho Saga into +28 only and left lumen at -3501; the counter-trading guard became v9 |

## Bounds and dead ends

| Idea | Result |
|---|---|
| Knowing the rival's same-step orders in advance (a theoretical upper bound for order placement) | +46 per game (standard error 126): not worth chasing |
| "God's mode": steering the shop draw through the number of empty tiles | the hidden seed cannot be inferred, so the draw cannot be steered |
