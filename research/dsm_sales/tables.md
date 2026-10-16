## 1. When DSM sells

| product | sale turns/game | units/game | lot median | lot mean | lot p90 | lot max | sale turns per selling day | units sold at hour 0 | units dropped by a unit in the same turn |
|---|---|---|---|---|---|---|---|---|---|
| WHEAT | 86 | 538 | 5 | 6.2 | 13 | 42 | 3.5 | 15% | 8% |
| CARROT | 21 | 179 | 9 | 8.3 | 13 | 32 | 2.4 | 16% | 15% |
| TOMATO | 23 | 154 | 7 | 6.7 | 11 | 32 | 1.9 | 16% | 3% |
| STRAWBERRY | 74 | 216 | 2 | 2.9 | 6 | 13 | 4.5 | 22% | 13% |
| MELON | 9 | 60 | 6 | 6.7 | 12 | 12 | 3.0 | 10% | 87% |
| EGG | 29 | 211 | 8 | 7.3 | 14 | 30 | 1.7 | 0% | 5% |
| MILK | 60 | 202 | 2 | 3.4 | 6 | 11 | 3.2 | 6% | 27% |
| WOOL | 56 | 143 | 2 | 2.5 | 6 | 12 | 3.9 | 4% | 42% |
| FERTILIZER | 74 | 243 | 2 | 3.3 | 10 | 22 | 2.6 | 49% | 6% |

Turns with at least one executed sale: 304 per game (of 719 action steps).

Share of sold units by hour of day (hours with >=4% shown):

| product | hour:share% of units |
|---|---|
| WHEAT | h0:15 h1:15 h2:12 h7:4 h22:12 |
| CARROT | h0:16 h1:11 h2:8 h10:6 h18:5 h19:4 h20:4 h22:17 h23:6 |
| TOMATO | h0:16 h14:6 h18:11 h22:40 h23:5 |
| STRAWBERRY | h0:22 h1:11 h5:9 h9:9 h13:9 h14:5 h17:8 h21:7 |
| MELON | h0:10 h7:9 h9:20 h10:10 h11:20 h12:10 h13:9 h16:9 |
| EGG | h1:6 h2:8 h3:5 h22:56 h23:5 |
| MILK | h0:6 h1:16 h2:6 h5:8 h9:10 h13:10 h17:13 h21:14 |
| WOOL | h1:13 h2:5 h3:12 h4:7 h5:11 h6:6 h9:8 h13:7 h17:6 h21:9 |
| FERTILIZER | h0:49 h2:10 h22:8 |

Share of sold units (and of sale turns) by step % 4. Town shops consume at the end of every step with step % 4 == 0 (after the market), so step % 4 == 1 is the first turn after a consumption tick:

| product | m4=0 (sells before the tick) | m4=1 (first turn after tick) | m4=2 | m4=3 |
|---|---|---|---|---|
| WHEAT | 26% (23%) | 23% (21%) | 35% (37%) | 16% (19%) |
| CARROT | 26% (20%) | 18% (16%) | 40% (44%) | 15% (20%) |
| TOMATO | 22% (17%) | 6% (5%) | 62% (60%) | 11% (18%) |
| STRAWBERRY | 27% (13%) | 52% (62%) | 12% (16%) | 9% (9%) |
| MELON | 29% (33%) | 30% (22%) | 11% (12%) | 30% (33%) |
| EGG | 5% (5%) | 8% (7%) | 70% (63%) | 17% (25%) |
| MILK | 11% (7%) | 69% (76%) | 13% (11%) | 6% (6%) |
| WOOL | 13% (8%) | 53% (68%) | 15% (12%) | 18% (13%) |
| FERTILIZER | 55% (29%) | 8% (15%) | 25% (31%) | 12% (25%) |

P(DSM sells | stock S > 0) by hour of day:

| prod | h0 | h1 | h2 | h3 | h4 | h5 | h6 | h7 | h8 | h9 | h10 | h11 | h12 | h13 | h14 | h15 | h16 | h17 | h18 | h19 | h20 | h21 | h22 | h23 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| WHT | 0.35 | 0.33 | 0.35 | 0.06 | 0.04 | 0.10 | 0.12 | 0.20 | 0.11 | 0.04 | 0.11 | 0.07 | 0.07 | 0.12 | 0.09 | 0.11 | 0.13 | 0.09 | 0.17 | 0.19 | 0.18 | 0.09 | 0.74 | 0.38 |
| CAR | 0.22 | 0.22 | 0.22 | 0.03 | 0.02 | 0.05 | 0.06 | 0.05 | 0.04 | 0.01 | 0.25 | 0.03 | 0.03 | 0.02 | 0.07 | 0.09 | 0.14 | 0.09 | 0.17 | 0.16 | 0.17 | 0.10 | 0.81 | 0.88 |
| TOM | 0.23 | 0.03 | 0.02 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.01 | 0.00 | 0.05 | 0.01 | 0.01 | 0.03 | 0.09 | 0.05 | 0.06 | 0.01 | 0.24 | 0.07 | 0.05 | 0.02 | 0.97 | 0.90 |
| STR | 0.34 | 0.36 | 0.07 | 0.02 | 0.01 | 0.57 | 0.02 | 0.01 | 0.03 | 0.69 | 0.13 | 0.11 | 0.07 | 0.60 | 0.42 | 0.16 | 0.14 | 0.80 | 0.30 | 0.16 | 0.11 | 0.86 | 0.13 | 0.24 |
| MEL | 0.97 | 1.00 | 1.00 | - | - | - | - | 1.00 | - | 1.00 | 1.00 | 1.00 | 0.99 | 0.86 | 0.85 | 1.00 | 0.98 | 1.00 | - | - | - | - | - | - |
| EGG | 0.00 | 0.09 | 0.14 | 0.06 | 0.01 | 0.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | 0.02 | 0.01 | 0.01 | 0.02 | 0.06 | 0.05 | 0.01 | 0.04 | 0.03 | 0.02 | 0.00 | 0.96 | 0.81 |
| MLK | 0.13 | 0.39 | 0.17 | 0.03 | 0.08 | 0.29 | 0.10 | 0.04 | 0.02 | 0.48 | 0.01 | 0.03 | 0.01 | 0.44 | 0.06 | 0.02 | 0.01 | 0.75 | 0.03 | 0.02 | 0.02 | 0.85 | 0.12 | 0.19 |
| WOL | 0.09 | 0.63 | 0.14 | 0.28 | 0.17 | 0.62 | 0.14 | 0.12 | 0.03 | 0.65 | 0.06 | 0.04 | 0.03 | 0.62 | 0.21 | 0.07 | 0.04 | 0.61 | 0.06 | 0.02 | 0.01 | 0.66 | 0.06 | 0.14 |
| FRT | 0.62 | 0.18 | 0.53 | 0.65 | 0.06 | 0.12 | 0.20 | 0.51 | 0.16 | 0.45 | 0.35 | 0.43 | 0.45 | 0.30 | 0.24 | 0.12 | 0.27 | 0.15 | 0.34 | 0.22 | 0.25 | 0.14 | 0.88 | 0.68 |

Sold units by sale component (a unit counts once, first matching column from the left):

| product | hour 0 (after day-end drop, before h0 tick) | m4=1 (first turn after a tick) | same-turn fresh drop, other hours | hours 22-23 | other |
|---|---|---|---|---|---|
| WHEAT | 15% | 23% | 8% | 13% | 41% |
| CARROT | 16% | 18% | 16% | 20% | 31% |
| TOMATO | 16% | 6% | 6% | 42% | 30% |
| STRAWBERRY | 22% | 52% | 10% | 3% | 12% |
| MELON | 10% | 30% | 59% | 0% | 2% |
| EGG | 0% | 8% | 11% | 56% | 24% |
| MILK | 6% | 69% | 17% | 2% | 5% |
| WOOL | 4% | 53% | 36% | 2% | 5% |
| FERTILIZER | 49% | 8% | 7% | 8% | 28% |

Share of the stock present at hour 0 that is sold during that day (cumulative, days 8-28, days with >= 4 units at hour 0):

| product | days | by h1 | by h5 | by h9 | by h13 | by h17 | by h21 | by h23 |
|---|---|---|---|---|---|---|---|---|
| WHEAT | 1860 | 0.18 | 0.29 | 0.37 | 0.42 | 0.46 | 0.50 | 0.59 |
| CARROT | 620 | 0.27 | 0.41 | 0.49 | 0.62 | 0.64 | 0.69 | 0.99 |
| TOMATO | 871 | 0.20 | 0.21 | 0.22 | 0.27 | 0.35 | 0.49 | 1.00 |
| STRAWBERRY | 1421 | 0.35 | 0.45 | 0.54 | 0.63 | 0.74 | 0.81 | 0.84 |
| MELON | 94 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| EGG | 1334 | 0.07 | 0.20 | 0.20 | 0.24 | 0.31 | 0.36 | 0.98 |
| MILK | 1029 | 0.31 | 0.37 | 0.48 | 0.59 | 0.73 | 0.84 | 0.85 |
| WOOL | 798 | 0.28 | 0.39 | 0.50 | 0.61 | 0.70 | 0.79 | 0.81 |
| FERTILIZER | 1630 | 0.65 | 0.78 | 0.78 | 0.78 | 0.78 | 0.79 | 0.90 |

Realised price: DSM vs the same-day mean quote (all units, 92 games):

| product | DSM price / base | DSM price / same-day mean quote | opponent price / same-day mean quote |
|---|---|---|---|
| WHEAT | 1.44 | 1.002 | 1.005 |
| CARROT | 1.25 | 1.000 | 0.992 |
| TOMATO | 1.18 | 1.000 | 1.001 |
| STRAWBERRY | 1.19 | 1.040 | 0.958 |
| MELON | 0.84 | 1.012 | 1.032 |
| EGG | 0.94 | 0.998 | 1.001 |
| MILK | 0.74 | 1.068 | 1.004 |
| WOOL | 0.76 | 1.169 | 1.030 |
| FERTILIZER | 0.53 | 1.024 | 1.026 |

Intraday quote profile, days 12-28 (quote at the start of the hour vs the day mean, %):

| product | h0 | h1 | h2 | h5 | h9 | h13 | h17 | h20 | h21 | h22 | h23 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| WHEAT | +1.0 | +0.7 | +0.3 | +0.1 | +0.1 | +0.3 | +0.4 | -0.2 | +0.2 | -0.1 | -0.7 |
| CARROT | -0.3 | -0.1 | -0.3 | -0.1 | +0.0 | +0.1 | +0.4 | +0.2 | +0.5 | +0.5 | +0.1 |
| TOMATO | -0.3 | -0.4 | -0.5 | -0.2 | +0.1 | +0.4 | +0.5 | +0.2 | +0.5 | +0.5 | -0.4 |
| STRAWBERRY | -1.0 | +3.6 | -3.0 | +3.9 | +5.7 | +8.3 | +6.4 | -3.5 | +4.5 | -4.7 | -6.1 |
| MELON | +0.4 | +0.7 | +0.4 | +0.2 | +0.0 | -0.1 | -0.1 | -0.2 | -0.3 | -0.4 | -0.5 |
| EGG | -0.1 | +0.2 | -0.1 | -0.2 | +0.0 | +0.2 | +0.3 | +0.2 | +0.3 | +0.3 | -0.7 |
| MILK | +3.1 | +11.1 | +0.2 | +4.6 | +6.7 | +6.0 | +7.4 | -3.9 | +5.6 | -5.8 | -7.2 |
| WOOL | +0.5 | +36.7 | +10.0 | +15.7 | +6.4 | +5.3 | +4.3 | -8.5 | +4.3 | -12.9 | -14.8 |
| FERTILIZER | +8.6 | +3.4 | +1.3 | -0.1 | -0.3 | -0.5 | -0.6 | -0.9 | -1.2 | -1.4 | -3.4 |

## 2. Premium goods: lot sizes and the hour-0 strawberry decision

STRAWBERRY, first turn after a tick (m4=1): rows = stock S (16 = 16+), columns = units sold

| S \ sold | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 44 | 311 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2 | 150 | 258 | 164 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3 | 108 | 193 | 101 | 28 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 4 | 204 | 124 | 197 | 26 | 67 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 5 | 92 | 82 | 180 | 19 | 6 | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 6 | 300 | 56 | 219 | 19 | 1 | 22 | 40 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 7 | 117 | 32 | 188 | 12 | 1 | 0 | 45 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| 8 | 360 | 23 | 161 | 39 | 1 | 0 | 82 | 0 | 12 | 0 | 0 | 0 | 0 | 0 |
| 9 | 106 | 13 | 139 | 26 | 0 | 0 | 19 | 0 | 3 | 4 | 0 | 0 | 0 | 0 |
| 10 | 162 | 8 | 128 | 46 | 0 | 0 | 25 | 0 | 4 | 0 | 13 | 0 | 0 | 0 |
| 11 | 82 | 2 | 106 | 32 | 0 | 0 | 14 | 0 | 2 | 0 | 0 | 8 | 0 | 0 |
| 12 | 128 | 6 | 91 | 33 | 0 | 0 | 26 | 0 | 3 | 0 | 0 | 5 | 6 | 0 |
| 13 | 107 | 4 | 78 | 31 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 5 | 0 | 9 |
| 14 | 100 | 1 | 68 | 33 | 0 | 0 | 12 | 0 | 1 | 0 | 0 | 2 | 0 | 3 |
| 15 | 89 | 1 | 52 | 12 | 0 | 0 | 9 | 0 | 1 | 0 | 0 | 2 | 0 | 4 |
| 16 | 490 | 0 | 213 | 97 | 0 | 0 | 56 | 0 | 3 | 0 | 0 | 7 | 0 | 16 |

STRAWBERRY, hour 0: rows = stock S (16 = 16+), columns = units sold

| S \ sold | 0 | 2 | 3 | 4 | 5 | 6 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2 | 26 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3 | 17 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 4 | 46 | 1 | 8 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 5 | 23 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 6 | 88 | 1 | 1 | 0 | 0 | 19 | 0 | 0 | 0 | 0 | 0 | 0 |
| 7 | 44 | 0 | 0 | 0 | 0 | 14 | 0 | 0 | 0 | 0 | 0 | 0 |
| 8 | 134 | 0 | 5 | 0 | 0 | 37 | 2 | 0 | 0 | 0 | 0 | 0 |
| 9 | 44 | 0 | 1 | 0 | 0 | 8 | 0 | 4 | 0 | 0 | 0 | 0 |
| 10 | 80 | 0 | 4 | 0 | 0 | 28 | 0 | 0 | 18 | 0 | 0 | 0 |
| 11 | 36 | 0 | 1 | 0 | 0 | 5 | 0 | 0 | 0 | 10 | 0 | 0 |
| 12 | 85 | 0 | 2 | 0 | 0 | 30 | 0 | 0 | 0 | 36 | 1 | 0 |
| 13 | 48 | 0 | 2 | 0 | 0 | 10 | 0 | 0 | 0 | 11 | 0 | 0 |
| 14 | 57 | 0 | 3 | 0 | 0 | 13 | 0 | 0 | 0 | 37 | 0 | 0 |
| 15 | 44 | 0 | 1 | 0 | 0 | 3 | 0 | 0 | 0 | 14 | 0 | 1 |
| 16 | 238 | 0 | 7 | 0 | 0 | 46 | 0 | 0 | 0 | 130 | 0 | 5 |

MILK, first turn after a tick (m4=1): rows = stock S (16 = 16+), columns = units sold

| S \ sold | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 145 | 295 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2 | 267 | 205 | 193 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3 | 1006 | 169 | 182 | 403 | 0 | 0 | 0 | 0 | 0 | 0 |
| 4 | 385 | 112 | 173 | 3 | 118 | 0 | 0 | 0 | 0 | 0 |
| 5 | 233 | 56 | 143 | 3 | 0 | 76 | 0 | 0 | 0 | 0 |
| 6 | 915 | 62 | 227 | 17 | 0 | 4 | 437 | 0 | 0 | 0 |
| 7 | 173 | 17 | 140 | 1 | 0 | 0 | 52 | 12 | 0 | 0 |
| 8 | 244 | 21 | 124 | 0 | 0 | 2 | 78 | 0 | 26 | 0 |
| 9 | 284 | 12 | 125 | 1 | 0 | 0 | 81 | 0 | 0 | 47 |
| 10 | 91 | 6 | 79 | 0 | 0 | 0 | 41 | 0 | 0 | 21 |
| 11 | 76 | 8 | 52 | 0 | 0 | 0 | 27 | 0 | 0 | 8 |
| 12 | 93 | 10 | 49 | 0 | 0 | 0 | 39 | 0 | 0 | 30 |
| 13 | 30 | 3 | 27 | 0 | 0 | 0 | 21 | 0 | 0 | 4 |
| 14 | 34 | 6 | 19 | 0 | 0 | 0 | 19 | 0 | 0 | 1 |
| 15 | 24 | 1 | 21 | 0 | 0 | 0 | 16 | 0 | 0 | 14 |
| 16 | 39 | 0 | 31 | 0 | 0 | 0 | 29 | 0 | 0 | 15 |

WOOL, first turn after a tick (m4=1): rows = stock S (16 = 16+), columns = units sold

| S \ sold | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 298 | 327 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2 | 348 | 318 | 110 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3 | 291 | 329 | 72 | 27 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 4 | 416 | 314 | 98 | 0 | 103 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 5 | 149 | 209 | 63 | 0 | 30 | 25 | 0 | 0 | 0 | 0 | 0 | 0 |
| 6 | 171 | 168 | 112 | 0 | 18 | 0 | 116 | 0 | 0 | 0 | 0 | 0 |
| 7 | 70 | 99 | 75 | 0 | 22 | 0 | 1 | 7 | 0 | 0 | 0 | 0 |
| 8 | 168 | 96 | 99 | 0 | 33 | 0 | 2 | 0 | 37 | 0 | 0 | 0 |
| 9 | 27 | 49 | 42 | 0 | 9 | 0 | 0 | 0 | 5 | 0 | 0 | 0 |
| 10 | 41 | 37 | 67 | 0 | 18 | 0 | 1 | 0 | 12 | 1 | 0 | 0 |
| 11 | 6 | 25 | 31 | 0 | 13 | 0 | 1 | 0 | 4 | 0 | 3 | 0 |
| 12 | 34 | 25 | 47 | 0 | 11 | 0 | 0 | 1 | 12 | 0 | 0 | 2 |
| 13 | 3 | 9 | 21 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 |
| 14 | 1 | 7 | 22 | 0 | 5 | 0 | 0 | 0 | 8 | 0 | 0 | 1 |
| 15 | 4 | 7 | 14 | 0 | 3 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| 16 | 22 | 3 | 48 | 0 | 13 | 0 | 3 | 0 | 27 | 0 | 0 | 2 |

Units sold at first-turn-after-tick steps (m4=1), by stock band (share of turns):

| product | stock S | turns | units sold: share of turns (9 = 9+) |
|---|---|---|---|
| STRAWBERRY | 1-2 | 927 | 0:21%, 1:61%, 2:18% |
| STRAWBERRY | 3-7 | 2498 | 0:33%, 1:19%, 2:35%, 3:4%, 4:3%, 6:3% |
| STRAWBERRY | 8+ | 3433 | 0:47%, 2:30%, 3:10%, 6:7%, 9:2% |
| MILK | 1-2 | 1105 | 0:37%, 1:45%, 2:17% |
| MILK | 3-7 | 5119 | 0:53%, 1:8%, 2:17%, 3:8%, 4:2%, 6:10% |
| MILK | 8+ | 2029 | 0:45%, 1:3%, 2:26%, 6:17%, 9:7% |
| WOOL | 1-2 | 1401 | 0:46%, 1:46%, 2:8% |
| WOOL | 3-7 | 2985 | 0:37%, 1:37%, 2:14%, 4:6%, 6:4% |
| WOOL | 8+ | 1188 | 0:26%, 1:22%, 2:33%, 4:9%, 8:9% |

P(sell | S > 0) at first-turn-after-tick steps, by quote / base price:

| product | <0.2 | 0.2-0.5 | 0.5-1 | 1-1.5 | >=1.5 |
|---|---|---|---|---|---|
| STRAWBERRY | 0.32 (n=914) | 0.67 (n=1279) | 0.71 (n=1399) | 0.70 (n=1468) | 0.57 (n=1798) |
| MILK | 0.41 (n=1563) | 0.59 (n=2492) | 0.57 (n=2189) | 0.42 (n=1811) | 0.40 (n=198) |
| WOOL | 0.40 (n=2147) | 0.80 (n=1424) | 0.78 (n=1203) | 0.73 (n=800) | - |

Turns where DSM's own units dropped fresh goods of the product into the shed in the same step:

| product | fresh-drop turns at m4=1 | fresh-drop turns at other steps |
|---|---|---|
| WHEAT | 358: P(sell) 0.44, sold exactly the fresh amount 22 of 157 | 1036: P(sell) 0.73, sold exactly the fresh amount 132 of 757 |
| CARROT | 213: P(sell) 0.30, sold exactly the fresh amount 31 of 63 | 568: P(sell) 0.52, sold exactly the fresh amount 128 of 295 |
| TOMATO | 141: P(sell) 0.04, sold exactly the fresh amount 0 of 5 | 436: P(sell) 0.35, sold exactly the fresh amount 33 of 151 |
| STRAWBERRY | 203: P(sell) 0.68, sold exactly the fresh amount 38 of 139 | 632: P(sell) 0.64, sold exactly the fresh amount 184 of 403 |
| MELON | 176: P(sell) 0.93, sold exactly the fresh amount 163 of 163 | 540: P(sell) 0.99, sold exactly the fresh amount 528 of 537 |
| EGG | 217: P(sell) 0.01, sold exactly the fresh amount 1 of 2 | 1096: P(sell) 0.24, sold exactly the fresh amount 57 of 267 |
| MILK | 753: P(sell) 0.63, sold exactly the fresh amount 364 of 476 | 1684: P(sell) 0.39, sold exactly the fresh amount 502 of 649 |
| WOOL | 182: P(sell) 0.95, sold exactly the fresh amount 124 of 172 | 1327: P(sell) 0.76, sold exactly the fresh amount 837 of 1015 |
| FERTILIZER | 1285: P(sell) 0.22, sold exactly the fresh amount 63 of 278 | 3475: P(sell) 0.26, sold exactly the fresh amount 431 of 893 |

Premium sale turns by class (share of DSM's sale turns):

| product | sale turns | hour 0 | m4=1 | other step, fresh drop | other step, no fresh drop | main hours of the last class |
|---|---|---|---|---|---|---|
| STRAWBERRY | 6787 | 8% | 62% | 6% | 24% | h14, h18, h23, h10 |
| MILK | 5510 | 3% | 76% | 12% | 8% | h23, h22, h14, h3 |
| WOOL | 5198 | 2% | 68% | 20% | 11% | h14, h23, h15, h10 |

Wool at m4=1 (S > 0): units sold vs wool consumed by the town at the tick just before (0 = no yarn store and not the h0 town-centre tick):

| consumed at last tick | turns | P(sell) | sold 0 | sold 1 | sold 2 | sold 3 | sold 4 | sold 5 | sold 6 | sold 7 | sold 8 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 1341 | 0.09 | 91% | 2% | 1% | 0% | 0% | 1% | 4% | 0% | 0% |
| 1 | 291 | 0.58 | 42% | 54% | 1% | 0% | 3% | 0% | 0% | 0% | 0% |
| 2 | 2085 | 0.87 | 13% | 65% | 17% | 0% | 2% | 0% | 2% | 0% | 0% |
| 3 | 482 | 0.68 | 32% | 36% | 16% | 1% | 11% | 0% | 3% | 0% | 2% |
| 4 | 983 | 0.85 | 15% | 27% | 39% | 1% | 13% | 1% | 1% | 0% | 3% |
| 5 | 237 | 0.64 | 36% | 5% | 22% | 3% | 14% | 0% | 3% | 0% | 16% |
| 6 | 155 | 0.69 | 31% | 14% | 25% | 1% | 5% | 1% | 2% | 1% | 21% |

P(DSM sells | S > 0) by hour, lineage opponents vs others (the within-day schedule is DSM's own):

| product | opponents | h0 | h1 | h5 | h9 | h13 | h17 | h21 | h22 |
|---|---|---|---|---|---|---|---|---|---|
| STRAWBERRY | lineage | 0.33 | 0.44 | 0.67 | 0.77 | 0.71 | 0.93 | 0.92 | 0.20 |
| STRAWBERRY | others | 0.35 | 0.35 | 0.55 | 0.68 | 0.59 | 0.78 | 0.86 | 0.12 |
| MILK | lineage | 0.10 | 0.40 | 0.35 | 0.52 | 0.42 | 0.75 | 0.81 | 0.13 |
| MILK | others | 0.13 | 0.38 | 0.28 | 0.47 | 0.44 | 0.75 | 0.85 | 0.12 |
| WOOL | lineage | 0.04 | 0.62 | 0.53 | 0.59 | 0.60 | 0.57 | 0.68 | 0.06 |
| WOOL | others | 0.10 | 0.64 | 0.63 | 0.66 | 0.63 | 0.61 | 0.66 | 0.06 |

Strawberry hour-0 lot sizes (S >= 6): count and median quote/base

| requested lot | orders | median quote/base |
|---|---|---|
| 2 | 1 | 0.25 |
| 3 | 27 | 0.71 |
| 6 | 213 | 1.23 |
| 11 | 261 | 1.56 |
| 13 | 8 | 1.83 |

| opponents | DSM SELL STRAWBERRY 11 at h0 | opponent also SELL STRAWBERRY 11 that step |
|---|---|---|
| lineage | 19 | 13 |
| others | 242 | 10 |

Strawberry hour-0 sale vs market trend (S >= 9): dinv24 = market inventory now minus 24 steps ago

| trend | price | days | P(sell at h0) |
|---|---|---|---|
| dinv24 >= 9 | price >= 0.7 base | 306 | 0.88 |
| dinv24 >= 9 | price < 0.7 base | 96 | 0.21 |
| dinv24 < 9 | price >= 0.7 base | 404 | 0.31 |
| dinv24 < 9 | price < 0.7 base | 257 | 0.06 |

Lineage check: sell decisions at m4=1 when both sides hold stock

| product | opponent | turns | P(DSM sells) | P(opp sells | DSM sells) | P(opp sells | DSM holds) |
|---|---|---|---|---|---|
| STRAWBERRY | DECEM/Vadim | 474 | 0.67 | 0.88 | 0.36 |
| STRAWBERRY | other | 2835 | 0.60 | 0.48 | 0.34 |
| MILK | DECEM/Vadim | 501 | 0.48 | 0.82 | 0.26 |
| MILK | other | 3353 | 0.52 | 0.56 | 0.39 |
| WOOL | DECEM/Vadim | 461 | 0.67 | 0.98 | 0.16 |
| WOOL | other | 2464 | 0.67 | 0.52 | 0.19 |

## 3. Order-slot layout and the opponent

Turns with at least one SELL order: 29936 (325/game).

| slot of first SELL | turns | share |
|---|---|---|
| 0 | 29738 | 99% |
| 1 | 80 | 0% |
| 2 | 27 | 0% |
| 3+ | 91 | 0% |

| order placed before the first SELL | count (all games) |
|---|---|
| EMPTY | 304 |
| BUY_PRODUCT | 179 |
| BUY_SEED | 110 |
| BUY_ANIMAL | 74 |
| HIRE | 14 |
| BUY_LAND | 1 |

| SELL orders in a turn | turns |
|---|---|
| 1 | 18902 |
| 2 | 8012 |
| 3 | 1998 |
| 4+ | 1024 |

SELL block contiguous (no other order between SELLs): 98% of SELL turns.

| order of SELLs when >= 2 | turns |
|---|---|
| descending qty x price | 8874 |
| other | 2160 |

| BUY_PRODUCT position in turns that also SELL | count |
|---|---|
| after last SELL | 2050 |
| between | 267 |
| before first SELL | 179 |

Turns with a BUY_PRODUCT order: 3466; the BUY_PRODUCT is the last non-empty order in 94%.

Mean HIRE orders per turn from day 10 on: h0: 8.0, h1: 3.6, h2: 0.2.

| SELL orders issued with zero stock (fail harmlessly), per game |
|---|
| FERTILIZER 26.2, WHEAT 21.8, CARROT 6.5, MILK 1.9, EGG 1.7, WOOL 0.7, STRAWBERRY 0.3, TOMATO 0.0 |

Contested sales (opponent sells the same product in the same turn) and reaction:

| opponents | product | DSM sale turns contested | DSM price/base contested | alone | opp SELL also in slot 0 | P(DSM sells at m4=1 | opp sold in previous 3 steps) yes / no |
|---|---|---|---|---|---|---|
| lineage (DECEM, Vadim, UMG) | WHEAT | 57% | 1.18 | 1.35 | 59% | 0.17 / 0.05 |
| lineage (DECEM, Vadim, UMG) | CARROT | 46% | 1.11 | 1.17 | 55% | 0.07 / 0.02 |
| lineage (DECEM, Vadim, UMG) | TOMATO | 59% | 1.02 | 1.00 | 60% | 0.04 / 0.01 |
| lineage (DECEM, Vadim, UMG) | STRAWBERRY | 64% | 1.02 | 1.08 | 73% | 0.79 / 0.52 |
| lineage (DECEM, Vadim, UMG) | MELON | 89% | 0.87 | 0.91 | 100% | 1.00 / 1.00 |
| lineage (DECEM, Vadim, UMG) | EGG | 64% | 0.87 | 0.87 | 51% | 0.02 / 0.01 |
| lineage (DECEM, Vadim, UMG) | MILK | 57% | 0.67 | 0.60 | 67% | 0.60 / 0.47 |
| lineage (DECEM, Vadim, UMG) | WOOL | 77% | 0.59 | 0.64 | 66% | 0.87 / 0.28 |
| lineage (DECEM, Vadim, UMG) | FERTILIZER | 66% | 0.58 | 0.48 | 71% | 0.48 / 0.12 |
| others | WHEAT | 18% | 1.32 | 1.49 | 65% | 0.18 / 0.12 |
| others | CARROT | 18% | 1.19 | 1.29 | 66% | 0.18 / 0.09 |
| others | TOMATO | 7% | 1.08 | 1.20 | 57% | 0.03 / 0.01 |
| others | STRAWBERRY | 19% | 1.18 | 1.21 | 80% | 0.56 / 0.62 |
| others | MELON | 41% | 0.93 | 0.75 | 99% | 0.89 / 0.96 |
| others | EGG | 12% | 0.90 | 0.95 | 36% | 0.06 / 0.02 |
| others | MILK | 24% | 0.72 | 0.75 | 78% | 0.49 / 0.52 |
| others | WOOL | 25% | 0.77 | 0.79 | 74% | 0.74 / 0.60 |
| others | FERTILIZER | 29% | 0.55 | 0.52 | 70% | 0.32 / 0.17 |

After DSM sold at a tick turn (m4=1): does it sell again at the next tick, contested vs alone?

| product | opponents | P(sell next tick) after contested sale | after uncontested sale |
|---|---|---|---|
| STRAWBERRY | lineage | 0.86 (n=301) | 0.75 (n=83) |
| STRAWBERRY | others | 0.72 (n=597) | 0.77 (n=2350) |
| MILK | lineage | 0.60 (n=184) | 0.74 (n=114) |
| MILK | others | 0.64 (n=707) | 0.67 (n=2218) |
| WOOL | lineage | 0.90 (n=283) | 0.69 (n=55) |
| WOOL | others | 0.87 (n=679) | 0.86 (n=1856) |

## 4. Stock levels, shed cap, endgame

Max shed fill per game: median 100; 83 of 92 games reach 100 at some step; steps with shed >= 95: 6.7 per game.

| units lost at the day-end drop (shed full), per game |
|---|
| WHEAT 4.1, CARROT 1.8, TOMATO 1.5, STRAWBERRY 1.1, EGG 1.0, FERTILIZER 0.6, MILK 0.2, WOOL 0.0 |

Units lost by mid-day DROPs into a full shed: 17 in all 92 games. Days 12-28, mean shed / carried items: h21 24 / 82, h22 22 / 84, h23 8 / 84.

Last sale step per game (mean): WHEAT 717, CARROT 717, TOMATO 718, STRAWBERRY 713, MELON 288, EGG 718, MILK 712, WOOL 638, FERTILIZER 717.

| day | WHT | CAR | TOM | STR | MEL | EGG | MLK | WOL | FRT | total at h0 | total at h23 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 6.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 7 | 2 |
| 9 | 19.3 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 3.8 | 23 | 2 |
| 11 | 37.1 | 0.3 | 0.0 | 0.0 | 0.1 | 5.2 | 5.1 | 0.0 | 15.5 | 63 | 8 |
| 13 | 47.0 | 1.3 | 0.0 | 6.6 | 0.1 | 4.2 | 5.3 | 6.6 | 11.7 | 83 | 5 |
| 15 | 43.3 | 2.9 | 0.1 | 11.5 | 0.0 | 10.5 | 9.2 | 4.3 | 11.2 | 93 | 4 |
| 17 | 35.7 | 4.7 | 0.3 | 14.2 | 0.0 | 11.8 | 6.8 | 4.7 | 10.0 | 88 | 5 |
| 19 | 29.5 | 3.1 | 9.5 | 12.9 | 0.0 | 10.6 | 7.5 | 6.2 | 11.6 | 91 | 5 |
| 21 | 26.4 | 4.1 | 16.7 | 11.0 | 0.0 | 9.4 | 7.9 | 3.6 | 9.9 | 89 | 9 |
| 23 | 27.3 | 6.3 | 11.0 | 17.4 | 0.0 | 9.5 | 7.0 | 4.4 | 8.8 | 92 | 14 |
| 25 | 34.7 | 11.5 | 7.9 | 13.4 | 0.0 | 8.4 | 6.2 | 5.4 | 5.2 | 93 | 9 |
| 27 | 32.6 | 13.9 | 13.0 | 12.6 | 0.0 | 9.0 | 5.2 | 2.7 | 4.8 | 94 | 8 |
| 28 | 28.6 | 15.7 | 15.0 | 12.0 | 0.0 | 7.0 | 4.3 | 4.3 | 4.0 | 91 | 14 |
| 29 | 28.5 | 18.4 | 12.2 | 9.1 | 0.0 | 6.9 | 4.2 | 3.5 | 3.1 | 86 | 2 |

Morning room-making: DSM units sold at hour 0 vs shed fill before the market (days 10-28):

| hour | shed fill | days | units sold (all) | of which wheat/carrot/tomato/egg |
|---|---|---|---|---|
| h0 | 0-59 | 205 | 11.3 | 0.0 |
| h0 | 60-79 | 306 | 14.1 | 2.3 |
| h0 | 80-89 | 486 | 15.8 | 6.2 |
| h0 | 90-94 | 329 | 17.2 | 7.9 |
| h0 | 95-100 | 422 | 18.2 | 10.3 |
| h1 | 0-59 | 669 | 7.1 | 4.1 |
| h1 | 60-79 | 918 | 10.3 | 6.1 |
| h1 | 80-89 | 142 | 9.5 | 5.4 |
| h2 | 0-59 | 1119 | 5.2 | 3.3 |
| h2 | 60-79 | 550 | 9.2 | 6.3 |
| h2 | 80-89 | 68 | 10.8 | 7.9 |
| h22 | 0-59 | 1726 | 14.3 | 13.0 |

Endgame: units sold per game by window (last market step is 718 = day 29 hour 22):

| window | WHT | CAR | TOM | STR | MEL | EGG | MLK | WOL | FRT | total |
|---|---|---|---|---|---|---|---|---|---|---|
| day 27 | 36.1 | 18.5 | 14.6 | 10.9 | 0.0 | 12.6 | 11.0 | 8.2 | 3.5 | 115 |
| d28 h0-2 | 25.6 | 12.5 | 1.0 | 1.2 | 0.0 | 0.3 | 2.0 | 1.0 | 0.7 | 44 |
| d28 h3-21 | 20.3 | 10.9 | 12.6 | 8.3 | 0.0 | 3.3 | 10.5 | 5.0 | 1.1 | 72 |
| d28 h22-23 | 9.2 | 6.2 | 4.9 | 0.6 | 0.0 | 11.2 | 0.5 | 0.2 | 2.6 | 35 |
| d29 h0-2 | 26.1 | 14.3 | 1.0 | 0.6 | 0.0 | 0.2 | 0.7 | 1.5 | 3.7 | 48 |
| d29 h3-12 | 1.5 | 1.8 | 0.4 | 4.8 | 0.0 | 0.5 | 2.3 | 1.2 | 0.6 | 13 |
| d29 h13-21 | 42.0 | 27.6 | 14.2 | 7.6 | 0.0 | 2.1 | 6.7 | 1.0 | 6.8 | 108 |
| d29 h22 (step 718) | 3.9 | 3.9 | 7.4 | 0.3 | 0.0 | 11.8 | 0.1 | 0.2 | 0.8 | 28 |

Day 29 mid-day drops into the shed (units/game by hour): h2:2.2 h3:0.1 h4:0.0 h10:0.1 h11:0.7 h12:0.8 h13:2.9 h14:4.8 h15:7.9 h16:13.0 h17:21.8 h18:18.4 h19:19.2 h20:11.3 h21:7.8 h22:3.1

Stranded at the end (shed + carried, valued at final quotes): mean $98, median $17, max $1662.

## 5. Harvest timing and drops

| crop | days | harvests/game | fertilized | top (age in days, yield) at harvest |
|---|---|---|---|---|
| WHEAT | d0-9 | 16.3 | 0% | (2,2) 76%, (3,3) 24% |
| WHEAT | d10-19 | 68.2 | 67% | (3,5) 36%, (4,6) 25%, (2,2) 12%, (3,3) 11% |
| WHEAT | d20-26 | 52.0 | 88% | (3,5) 51%, (4,6) 27%, (4,5) 6%, (2,2) 4% |
| WHEAT | d27-29 | 32.2 | 74% | (3,5) 36%, (4,6) 26%, (2,2) 16%, (4,5) 5% |
| CARROT | d0-9 | 0.1 | 0% | (2,2) 83%, (3,3) 17% |
| CARROT | d10-19 | 9.9 | 6% | (3,3) 76%, (2,2) 17%, (3,4) 5%, (3,2) 1% |
| CARROT | d20-26 | 21.3 | 46% | (3,3) 44%, (3,4) 35%, (2,2) 10%, (2,3) 10% |
| CARROT | d27-29 | 25.1 | 55% | (3,4) 47%, (3,3) 29%, (2,2) 16%, (2,3) 8% |
| TOMATO | d10-19 | 14.6 | 97% | (8,2) 36%, (9,2) 25%, (10,2) 18%, (8,1) 6% |
| TOMATO | d20-26 | 39.0 | 99% | (8,2) 22%, (11,2) 21%, (10,2) 18%, (9,2) 17% |
| TOMATO | d27-29 | 20.5 | 99% | (10,2) 28%, (11,2) 24%, (9,2) 20%, (8,2) 6% |
| STRAWBERRY | d10-19 | 55.7 | 99% | (10,2) 29%, (12,2) 27%, (16,2) 15%, (14,2) 15% |
| STRAWBERRY | d20-26 | 44.4 | 98% | (14,2) 22%, (16,2) 20%, (10,2) 16%, (12,2) 15% |
| STRAWBERRY | d27-29 | 11.0 | 99% | (16,2) 45%, (14,2) 15%, (15,2) 11%, (12,2) 9% |
| MELON | d10-19 | 9.9 | 0% | (10,6) 100%, (11,6) 0% |

| animal | harvests/game | yield at harvest | days between harvests | median hour |
|---|---|---|---|---|
| GOOSE | 76 | 1:8%, 2:39%, 3:17%, 4:36% | 1d:46%, 2d:48%, 3d:5% | 9 |
| COW | 57 | 2:19%, 3:48%, 4:7%, 5:3%, 6:22% | 1d:4%, 2d:72%, 3d:7%, 4d:9%, 5d:3% | 4 |
| SHEEP | 34 | 3:15%, 4:60%, 5:2%, 6:21% | 2d:10%, 3d:67%, 4d:12%, 5d:6% | 4 |

P(tile harvested that day | yield > 0 at hour 0), by the product's quote at hour 0 (days 10-28):

| tile | quote < 0.3 base | 0.3-0.7 | 0.7-1.1 | >= 1.1 |
|---|---|---|---|---|
| GOOSE | - | - | 0.61 (n=9340) | 0.71 (n=1053) |
| COW | 0.27 (n=2893) | 0.63 (n=2628) | 0.93 (n=1034) | 0.99 (n=1399) |
| SHEEP | 0.24 (n=2533) | 0.66 (n=793) | 0.86 (n=770) | 0.90 (n=813) |
| TOMATO | - | 0.91 (n=99) | 0.87 (n=1793) | 0.86 (n=5398) |
| STRAWBERRY | 0.53 (n=1216) | 0.73 (n=1761) | 0.85 (n=1149) | 0.90 (n=7888) |

Same statistic split by game phase and by DSM's own shed stock of the product at hour 0 (checks that the price effect is not just a late-game effect):

| tile | days | quote/base | own stock 0 | 1-5 | 6+ |
|---|---|---|---|---|---|
| COW | d12-19 | <0.3 | 0.21 (n=99) | 0.15 (n=222) | 0.13 (n=262) |
| COW | d12-19 | 0.3-0.7 | 0.89 (n=200) | 0.81 (n=175) | 0.54 (n=396) |
| COW | d12-19 | >=0.7 | 1.00 (n=633) | 0.98 (n=198) | 0.98 (n=654) |
| COW | d20-28 | <0.3 | 0.42 (n=353) | 0.33 (n=879) | 0.24 (n=1078) |
| COW | d20-28 | 0.3-0.7 | 0.72 (n=219) | 0.66 (n=602) | 0.55 (n=1036) |
| COW | d20-28 | >=0.7 | 0.91 (n=82) | 0.93 (n=205) | 0.91 (n=477) |
| SHEEP | d12-19 | <0.3 | 0.15 (n=220) | 0.13 (n=433) | 0.19 (n=213) |
| SHEEP | d12-19 | 0.3-0.7 | 0.68 (n=222) | 0.70 (n=74) | 0.57 (n=70) |
| SHEEP | d12-19 | >=0.7 | 0.89 (n=408) | 0.89 (n=154) | 0.88 (n=382) |
| SHEEP | d20-28 | <0.3 | 0.11 (n=565) | 0.41 (n=549) | 0.34 (n=553) |
| SHEEP | d20-28 | 0.3-0.7 | 0.75 (n=130) | 0.74 (n=84) | 0.57 (n=213) |
| SHEEP | d20-28 | >=0.7 | 0.90 (n=222) | 0.80 (n=120) | 0.85 (n=297) |
| STRAWBERRY | d12-19 | <0.3 | - | - | 0.90 (n=40) |
| STRAWBERRY | d12-19 | 0.3-0.7 | - | 0.97 (n=29) | 0.90 (n=127) |
| STRAWBERRY | d12-19 | >=0.7 | 0.88 (n=349) | 0.89 (n=238) | 0.91 (n=4887) |
| STRAWBERRY | d20-28 | <0.3 | 0.71 (n=24) | 0.57 (n=117) | 0.51 (n=1032) |
| STRAWBERRY | d20-28 | 0.3-0.7 | - | 0.98 (n=47) | 0.71 (n=1555) |
| STRAWBERRY | d20-28 | >=0.7 | - | 0.91 (n=295) | 0.88 (n=3265) |

Melon: tiles planted per game 9 tiles in 6 games, 10 tiles in 86 games; planted on days d0:552, d1:362; harvested on days d10:552, d11:361, d12:1; units sold on days d10:3300, d11:1614, d12:564, d13:6.

| product | harvested/game | dropped mid-day (DROP/PLACE)/game | day-end drop/game | mid-day share | main mid-day drop hours |
|---|---|---|---|---|---|
| WHEAT | 749 | 116 | 695 | 14% | h17 h18 h19 h21 |
| CARROT | 181 | 54 | 124 | 30% | h17 h18 h19 h21 |
| TOMATO | 156 | 21 | 133 | 14% | h19 h20 h21 h22 |
| STRAWBERRY | 218 | 48 | 168 | 22% | h14 h15 h18 h19 |
| MELON | 60 | 53 | 6 | 89% | h9 h10 h11 h12 |
| EGG | 212 | 52 | 159 | 25% | h2 h19 h21 h22 |
| MILK | 204 | 125 | 78 | 61% | h1 h2 h4 h6 |
| WOOL | 143 | 83 | 60 | 58% | h2 h3 h4 h6 |
| FERTILIZER | 0 | 81 | 179 | 31% | h6 h9 h10 h11 |

| mid-day shed deposits per game by hour | DROP | PLACE |
|---|---|---|
| h1 | 2.2 | 5.4 |
| h2 | 7.5 | 16.9 |
| h3 | 2.8 | 1.3 |
| h4 | 2.6 | 3.1 |
| h5 | 2.0 | 3.3 |
| h6 | 2.7 | 9.4 |
| h7 | 3.0 | 1.1 |
| h8 | 1.3 | 3.6 |
| h9 | 2.3 | 6.9 |
| h10 | 1.6 | 5.5 |
| h11 | 2.8 | 4.8 |
| h12 | 1.9 | 1.8 |
| h13 | 2.2 | 1.5 |
| h14 | 1.7 | 0.6 |
| h15 | 2.3 | 1.3 |
| h16 | 3.5 | 0.6 |
| h17 | 4.0 | 1.1 |
| h18 | 3.9 | 0.1 |
| h19 | 4.8 | 0.1 |
| h20 | 3.9 | 0.1 |
| h21 | 4.1 | 0.2 |
| h22 | 3.5 | 0.0 |
| h23 | 2.4 | 0.0 |

| item picked up from the shed | units/game | main hours (share) |
|---|---|---|
| WHEAT | 455.5 | h1 39%, h2 22%, h0 11%, h3 9% |
| FERTILIZER | 19.3 | h2 54%, h1 30%, h3 12%, h4 1% |
| COW | 11.4 | h1 18%, h7 13%, h2 11%, h11 9% |
| GOOSE | 7.5 | h12 19%, h9 16%, h10 12%, h13 12% |
| SHEEP | 7.0 | h2 56%, h13 8%, h7 7%, h11 6% |

DSM unit actions per game: WATER 1287, NORTH 848, SOUTH 777, WEST 774, EAST 657, HARVEST 592, COLLECT_FERTILIZER 485, CARE 394, FEED 391, PASS 325, PLANT 296, FERTILIZE 241, PICKUP 197, PLACE 93, DROP 69, DIG 45, BUILD_PASTURE 17, BUILD_COOP 7.

## 6. BUY_PRODUCT

**WHEAT**: bought in 92/92 games; 182.8 units/game (median 166, max 413); $6691/game; mean unit price $36.6 (min 21, max 48).

| day | units/game |
|---|---|
| 0 | 9.0 |
| 1 | 5.4 |
| 2 | 3.2 |
| 5 | 2.0 |
| 6 | 7.3 |
| 7 | 13.7 |
| 8 | 16.9 |
| 9 | 4.3 |
| 10 | 49.6 |
| 11 | 8.5 |
| 12 | 21.0 |
| 13 | 0.7 |
| 14 | 2.0 |
| 15 | 1.6 |
| 16 | 0.7 |
| 17 | 3.5 |
| 18 | 1.0 |
| 19 | 5.9 |
| 20 | 2.2 |
| 21 | 7.8 |
| 22 | 3.1 |
| 23 | 4.7 |
| 24 | 1.3 |
| 25 | 1.5 |
| 26 | 1.7 |
| 27 | 2.8 |
| 28 | 1.2 |

| hour | units/game |
|---|---|
| 0 | 36.6 |
| 1 | 41.4 |
| 2 | 15.6 |
| 3 | 8.6 |
| 4 | 5.0 |
| 5 | 5.5 |
| 6 | 11.1 |
| 7 | 2.4 |
| 8 | 8.1 |
| 9 | 33.8 |
| 10 | 6.3 |
| 11 | 2.9 |
| 12 | 2.5 |
| 13 | 1.0 |
| 17 | 0.6 |

| (day, hour) | units/game |
|---|---|
| (10, 9) | 33.1 |
| (8, 1) | 13.1 |
| (12, 1) | 9.6 |
| (10, 0) | 8.0 |
| (0, 0) | 5.0 |
| (6, 0) | 4.9 |
| (10, 2) | 4.8 |
| (21, 0) | 3.8 |

| requested lot | orders |
|---|---|
| 1 | 461 |
| 2 | 751 |
| 3 | 391 |
| 4 | 254 |
| 5 | 505 |
| 6 | 123 |
| 7 | 113 |
| 8 | 110 |
| 9 | 20 |
| 10 | 40 |
| 11 | 34 |
| 13 | 342 |
| 16 | 108 |
| 32 | 28 |
| 35 | 80 |

| slot of BUY_PRODUCT | orders |
|---|---|
| 0 | 471 |
| 1 | 958 |
| 2 | 460 |
| 3 | 121 |
| 4 | 142 |
| 5 | 237 |
| 6 | 284 |
| 7 | 306 |
| 8 | 374 |
| 9 | 712 |

| days | units/game | mean price | median requested lot | median own stock before the buy |
|---|---|---|---|---|
| d0-2 | 17.6 | 28.7 | 2 | 0 |
| d3-9 | 44.3 | 33.3 | 4 | 0 |
| d10-12 | 79.1 | 39.1 | 10 | 4 |
| d13-28 | 41.8 | 38.6 | 13 | 7 |

**FERTILIZER**: bought in 18/92 games; 3.5 units/game (median 0, max 58); $191/game; mean unit price $54.0 (min 16, max 89).

| day | units/game |
|---|---|
| 12 | 1.7 |

| hour | units/game |
|---|---|
| 1 | 1.2 |
| 16 | 0.7 |

| (day, hour) | units/game |
|---|---|
| (12, 16) | 0.5 |
| (21, 1) | 0.5 |
| (15, 1) | 0.3 |
| (12, 17) | 0.2 |
| (12, 12) | 0.2 |
| (12, 14) | 0.2 |
| (19, 1) | 0.2 |
| (12, 15) | 0.1 |

| requested lot | orders |
|---|---|
| 2 | 47 |
| 5 | 21 |

| slot of BUY_PRODUCT | orders |
|---|---|
| 0 | 34 |
| 1 | 46 |
| 2 | 31 |
| 3 | 30 |
| 4 | 25 |
| 5 | 16 |
| 6 | 5 |
| 7 | 16 |
| 9 | 1 |

| days | units/game | mean price | median requested lot | median own stock before the buy |
|---|---|---|---|---|
| d0-2 | 0.0 | - | 12 | 0 |
| d3-9 | 0.0 | 79.7 | 4 | 0 |
| d10-12 | 2.1 | 66.0 | 5 | 0 |
| d13-28 | 1.4 | 34.4 | 5 | 0 |

