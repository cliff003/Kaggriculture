# Land purchases (92 games)

| quadrant | games | day:hour of BUY_LAND (games) | money at start of step: median (min-max) | money right before BUY_LAND executes (min/p10/med/p90/max) | median money right after | units sold earlier in the same step (per purchase) |
|---|---|---|---|---|---|---|
| NE | 92/92 | 6:05 x92 | 1974 (1748-2219) | 2780/2924/3155/3440/3608 | 2154 | WOOL 5.8 |
| SW | 92/92 | 9:01 x8, 9:03 x63, 9:05 x20, 9:07 x1 | 2058 (1283-2899) | 2020/2221/2550/2911/3369 | 546 | WOOL 2.6, FERTILIZER 0.0 |
| SE | 92/92 | 10:12 x24, 10:13 x20, 10:14 x43, 10:15 x2, 10:16 x1, 10:17 x1, 10:18 x1 | 4348 (2671-6429) | 4055/4153/4781/5536/6429 | 774 | MELON 2.5, WHEAT 0.2 |

Order lists of the purchasing step (modal):

- NE: `[["SELL", "WOOL", 6], ["BUY_LAND"]]` x92
- SW: `[["SELL", "WOOL", 4], ["BUY_LAND"]]` x63 | `[["BUY_LAND"]]` x20 | `[["BUY_LAND"], ["HIRE"], ["HIRE"]]` x8 | `[["SELL", "WOOL", 4], ["SELL", "FERTILIZER", 2], ["BUY_LAND"], ["BUY_PRODUCT", "WHEAT", 3]]` x1
- SE: `[["BUY_LAND"]]` x39 | `[["SELL", "MELON", 6], ["BUY_LAND"]]` x29 | `[["BUY_LAND"], ["BUY_SEED", "WHEAT", 1]]` x9 | `[["SELL", "MELON", 6], ["BUY_LAND"], ["BUY_SEED", "WHEAT", 1]]` x6

BUY_LAND orders that did not execute (day, hour, orders, games):

- day 9 h3: `[["SELL", "WOOL", 4], ["BUY_LAND"]]` x21
- day 9 h5: `[["BUY_LAND"]]` x1
- day 10 h12: `[["SELL", "MELON", 6], ["BUY_LAND"], ["BUY_SEED", "WHEAT", 1]]` x1
- day 10 h12: `[["SELL", "MELON", 6], ["BUY_LAND"]]` x2
- day 10 h13: `[["BUY_LAND"], ["BUY_SEED", "STRAWBERRY", 1]]` x1
- day 10 h13: `[["BUY_LAND"], ["BUY_SEED", "WHEAT", 1]]` x2
- day 10 h13: `[["BUY_LAND"]]` x2
- day 10 h14: `[["BUY_LAND"], ["BUY_SEED", "WHEAT", 1]]` x1
- day 10 h14: `[["BUY_LAND"]]` x4
- day 10 h15: `[["BUY_LAND"], ["BUY_SEED", "WHEAT", 1]]` x1
- day 10 h15: `[["BUY_LAND"]]` x1
- day 10 h16: `[["BUY_LAND"]]` x1
- day 12 h1: `[["BUY_LAND"], ["HIRE"], ["HIRE"], ["HIRE"], ["BUY_SEED", "TOMATO", 1], ["BUY_SEED", "STRAWBERRY", 1], ["BUY_PRODUCT", "WHEAT", 13]]` x1
- day 12 h1: `[["BUY_LAND"], ["HIRE"], ["HIRE"], ["HIRE"], ["BUY_SEED", "TOMATO", 1], ["BUY_SEED", "STRAWBERRY", 1]]` x1

Sales on the purchase day before the purchase step (units per game, median):

| quadrant | WOOL | MELON | MILK | WHEAT | FERTILIZER | STRAWBERRY | EGG |
|---|---|---|---|---|---|---|---|
| NE | 12 | 0 | 0 | 2.5 | 0 | 0 | 0 |
| SW | 4 | 0 | 0 | 0 | 4 | 0 | 0 |
| SE | 0 | 30 | 0 | 0 | 7 | 0 | 0 |
