# Opening (days 0-6), 92 DSM games (submission 56518845)

## 1a. Day 0 tape (steps 0-23). `n` = games whose full action (farmer+hands+market) equals the modal one

| step | n | market orders | farmer / hand1..4 | tile changes (x,y) (n if <92) |
|---|---|---|---|---|
| 0 | 92 | BUY_ANIMAL COW 1, BUY_PROD WHEAT 5 | PASS |  |
| 1 | 92 | SELL WHEAT 1, HIRE x4, BUY_ANIMAL COW 1, BUY_ANIMAL SHEEP 3 | PICKUP COW |  |
| 2 | 92 | SELL WHEAT 1 | BUILD_PASTURE / PICKUP SHEEP / PICKUP SHEEP / PICKUP COW / PICKUP SHEEP | PASTURE@4,4 |
| 3 | 92 | SELL WHEAT 1, BUY_PROD WHEAT 1 | PLACE COW / NORTH / NORTH / NORTH / WEST | COW@4,4 |
| 4 | 92 | SELL WHEAT 1, BUY_PROD WHEAT 1 | PICKUP WHEAT / WEST / WEST / NORTH / BUILD_PASTURE | PASTURE@3,4 |
| 5 | 92 | SELL WHEAT 1, BUY_PROD WHEAT 1 | FEED / BUILD_PASTURE / WEST / NORTH / PLACE SHEEP | PASTURE@4,3; SHEEP@3,4 |
| 6 | 92 | BUY_SEED MELON 2, BUY_PROD WHEAT 1 | WEST / PLACE SHEEP / BUILD_PASTURE / PASS / CARE | PASTURE@2,4; SHEEP@4,3 |
| 7 | 92 | (none) | FEED / CARE / PLACE SHEEP / WEST / WEST | SHEEP@2,4 |
| 8 | 92 | BUY_SEED MELON 2 | WEST / SOUTH / WEST / BUILD_PASTURE / WEST | PASTURE@4,2 |
| 9 | 92 | (none) | FEED / PICKUP WHEAT / NORTH / PLACE COW / NORTH | COW@4,2 |
| 10 | 92 | (none) | CARE / CARE / PLANT MELON / NORTH / PASS | MELON@1,3 |
| 11 | 92 | BUY_SEED MELON 2 | WEST / NORTH / WATER / PLANT MELON / NORTH | MELON@4,1 |
| 12 | 92 | BUY_SEED WHEAT 2 | PLANT MELON / FEED / NORTH / WATER / NORTH | MELON@1,4 |
| 13 | 56 | SELL WHEAT 1, BUY_SEED WHEAT 2 | WATER / NORTH / PLANT MELON / WEST / PLANT WHEAT | MELON@1,2; WHEAT@1,1 |
| 14 | 92 | BUY_SEED WHEAT 1 | PASS / WEST / WATER / PLANT MELON / WATER | MELON@3,1 |
| 15 | 92 | BUY_SEED WHEAT 1 | PASS / PLANT MELON / NORTH / WATER / NORTH | MELON@3,2 |
| 16 | 92 | BUY_SEED WHEAT 1 | PASS / WATER / WEST / WEST / PLANT WHEAT | WHEAT@1,0 |
| 17 | 92 | BUY_SEED WHEAT 1 | PASS / WEST / PLANT WHEAT / PLANT WHEAT / WATER | WHEAT@0,1; WHEAT@2,1 |
| 18 | 92 | BUY_SEED WHEAT 1 | PASS / PLANT WHEAT / WATER / WATER / WEST | WHEAT@2,2 |
| 19 | 92 | BUY_SEED WHEAT 1 | WEST / WATER / SOUTH / NORTH / PLANT WHEAT | WHEAT@0,0 |
| 20 | 91 | BUY_SEED WHEAT 1 | PLANT WHEAT / WEST / PLANT WHEAT / PLANT WHEAT / WATER | WHEAT@0,2; WHEAT@0,4; WHEAT@2,0 (91) |
| 21 | 91 | BUY_SEED WHEAT 1 | WATER / SOUTH / WATER / WATER / PASS |  |
| 22 | 68 | (none) | SOUTH / WEST / SOUTH / SOUTH / SOUTH |  |
| 23 | 92 | (none) | SOUTH / SOUTH / SOUTH / SOUTH / SOUTH |  |

Market variants on day 0: step 13: [["SELL", "WHEAT", 1], ["BUY_SEED", "WHEAT", 2]] x56; [["SELL", "WHEAT", 1], ["BUY_SEED", "WHEAT", 5]] x36

## 1b. Executed purchases/sales per day, days 0-6 (median units per game (p10-p90), @h = median hour of the executed units)

| day | seed WHEAT | seed MELON | seed STRAWBERRY | seed CARROT | seed TOMATO | COW | SHEEP | GOOSE | wheat(feed) | HIRE | SELL WHEAT | SELL FERTILIZER | SELL WOOL |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 10 (9-10) @h13 | 6 @h8 |  |  |  | 2 @h0 | 3 @h1 |  | 9 @h0 | 4 @h1 | 5 @h3 |  |  |
| 1 | 0 | 4 @h10 |  |  |  |  |  |  | 6 (3-6) @h6 | 4 (2-9) @h0 | 0 | 5 @h10 |  |
| 2 |  |  | 4 (3-4) @h11 |  |  |  |  |  | 3 (3-4) @h4 | 6 (6-8) @h0 | 1 (0-1) @h0 | 5 @h10 |  |
| 3 |  |  | 6 @h9 |  |  |  |  |  |  | 6 @h0 | 5 (5-7) @h1 | 5 @h9 |  |
| 4 |  |  | 1 (0-2) @h10 |  |  |  |  |  |  | 6 (4-6) @h0 | 1 (0-3) @h0 | 5 @h11 |  |
| 5 |  |  |  |  |  |  |  |  | 2 (0-2) @h0 | 6 @h0 | 0 | 5 @h9 |  |
| 6 | 5 (1-17) @h13 |  | 10 (0-12) @h6 | 0 | 0 | 5 (2-6) @h10 | 0 (0-4) | 2 (0-4) @h11 | 7 (2-12) @h0 | 8 @h0 | 3 (1-5) @h1 | 5 (4-5) @h7 | 18 (16-18) @h5 |

## 1c. Tile events days 0-6 (events seen in >=5 games; harvest = one-time crop removed)

| day | tile | event | games | median hour | hour range |
|---|---|---|---|---|---|
| 0 | (4,4) | PASTURE | 92/92 | 2.0 | 2-2 |
| 0 | (4,4) | COW | 92/92 | 3.0 | 3-3 |
| 0 | (3,4) | PASTURE | 92/92 | 4.0 | 4-4 |
| 0 | (3,4) | SHEEP | 92/92 | 5.0 | 5-5 |
| 0 | (4,3) | PASTURE | 92/92 | 5.0 | 5-5 |
| 0 | (2,4) | PASTURE | 92/92 | 6.0 | 6-6 |
| 0 | (4,3) | SHEEP | 92/92 | 6.0 | 6-6 |
| 0 | (2,4) | SHEEP | 92/92 | 7.0 | 7-7 |
| 0 | (4,2) | PASTURE | 92/92 | 8.0 | 8-8 |
| 0 | (4,2) | COW | 92/92 | 9.0 | 9-9 |
| 0 | (1,3) | MELON | 92/92 | 10.0 | 10-10 |
| 0 | (4,1) | MELON | 92/92 | 11.0 | 11-11 |
| 0 | (1,4) | MELON | 92/92 | 12.0 | 12-12 |
| 0 | (1,1) | WHEAT | 92/92 | 13.0 | 13-13 |
| 0 | (1,2) | MELON | 92/92 | 13.0 | 13-13 |
| 0 | (3,1) | MELON | 92/92 | 14.0 | 14-14 |
| 0 | (3,2) | MELON | 92/92 | 15.0 | 15-15 |
| 0 | (1,0) | WHEAT | 92/92 | 16.0 | 16-16 |
| 0 | (0,1) | WHEAT | 92/92 | 17.0 | 17-17 |
| 0 | (2,1) | WHEAT | 92/92 | 17.0 | 17-17 |
| 0 | (2,2) | WHEAT | 92/92 | 18.0 | 18-18 |
| 0 | (0,0) | WHEAT | 92/92 | 19.0 | 19-19 |
| 0 | (0,2) | WHEAT | 92/92 | 20.0 | 20-20 |
| 0 | (0,4) | WHEAT | 92/92 | 20.0 | 20-20 |
| 0 | (2,0) | WHEAT | 91/92 | 20 | 20-20 |
| 1 | (4,0) | MELON | 92/92 | 14.0 | 11-15 |
| 1 | (3,3) | MELON | 86/92 | 16.0 | 12-21 |
| 1 | (2,3) | MELON | 92/92 | 18.0 | 14-22 |
| 1 | (3,0) | MELON | 92/92 | 17.0 | 14-18 |
| 1 | (0,3) | WHEAT | 58/92 | 21.0 | 17-22 |
| 2 | (0,4) | harvest WHEAT | 92/92 | 13.0 | 10-14 |
| 2 | (0,4) | STRAWBERRY | 92/92 | 14.0 | 11-15 |
| 2 | (1,0) | harvest WHEAT | 92/92 | 12.0 | 11-14 |
| 2 | (1,1) | harvest WHEAT | 91/92 | 17 | 11-21 |
| 2 | (2,2) | harvest WHEAT | 92/92 | 15.0 | 11-17 |
| 2 | (1,1) | STRAWBERRY | 90/92 | 18.0 | 12-18 |
| 2 | (0,0) | harvest WHEAT | 92/92 | 15.0 | 15-18 |
| 2 | (0,0) | STRAWBERRY | 80/92 | 16.0 | 16-19 |
| 2 | (0,3) | STRAWBERRY | 33/92 | 17 | 17-21 |
| 2 | (0,1) | harvest WHEAT | 54/92 | 21.0 | 19-21 |
| 2 | (1,0) | WHEAT | 11/92 | 21 | 19-21 |
| 2 | (0,1) | STRAWBERRY | 53/92 | 22 | 22-22 |
| 3 | (0,3) | STRAWBERRY | 59/92 | 9 | 7-9 |
| 3 | (0,3) | harvest WHEAT | 58/92 | 8.0 | 8-8 |
| 3 | (2,1) | harvest WHEAT | 92/92 | 11.0 | 8-16 |
| 3 | (2,2) | STRAWBERRY | 80/92 | 22.0 | 8-22 |
| 3 | (0,2) | harvest WHEAT | 91/92 | 13 | 9-15 |
| 3 | (0,2) | STRAWBERRY | 92/92 | 14.0 | 10-16 |
| 3 | (2,0) | STRAWBERRY | 92/92 | 12.0 | 10-13 |
| 3 | (2,0) | harvest WHEAT | 91/92 | 11 | 11-12 |
| 3 | (0,1) | harvest WHEAT | 38/92 | 14.0 | 12-18 |
| 3 | (2,1) | STRAWBERRY | 92/92 | 19.5 | 13-21 |
| 3 | (1,0) | STRAWBERRY | 80/92 | 15.0 | 15-19 |
| 3 | (0,0) | STRAWBERRY | 9/92 | 18 | 17-19 |
| 3 | (0,1) | STRAWBERRY | 38/92 | 22.0 | 19-22 |
| 4 | (1,0) | harvest WHEAT | 11/92 | 11 | 11-12 |
| 4 | (1,0) | STRAWBERRY | 11/92 | 12 | 12-16 |
| 4 | (2,2) | STRAWBERRY | 12/92 | 20.5 | 19-22 |
| 6 | (5,4) | PASTURE | 92/92 | 9.0 | 8-9 |
| 6 | (5,1) | STRAWBERRY | 56/92 | 9.0 | 9-10 |
| 6 | (5,4) | COW | 69/92 | 10 | 9-10 |
| 6 | (5,1) | WHEAT | 29/92 | 10 | 10-10 |
| 6 | (5,4) | SHEEP | 23/92 | 10 | 10-10 |
| 6 | (5,0) | WHEAT | 18/92 | 12.0 | 11-12 |
| 6 | (5,0) | STRAWBERRY | 64/92 | 21.0 | 11-22 |
| 6 | (6,1) | WHEAT | 70/92 | 12.0 | 11-13 |
| 6 | (5,3) | PASTURE | 92/92 | 14.0 | 12-15 |
| 6 | (6,1) | STRAWBERRY | 22/92 | 12.0 | 12-12 |
| 6 | (6,4) | PASTURE | 66/92 | 12.0 | 12-15 |
| 6 | (6,4) | COOP | 26/92 | 12.0 | 12-12 |
| 6 | (5,3) | COW | 92/92 | 15.0 | 13-16 |
| 6 | (6,4) | SHEEP | 11/92 | 13 | 13-13 |
| 6 | (6,4) | GOOSE | 26/92 | 13.0 | 13-13 |
| 6 | (6,4) | COW | 55/92 | 13 | 13-17 |
| 6 | (7,0) | WHEAT | 24/92 | 15.5 | 13-16 |
| 6 | (7,1) | STRAWBERRY | 60/92 | 13.0 | 13-16 |
| 6 | (5,2) | PASTURE | 78/92 | 19.0 | 14-22 |
| 6 | (6,3) | PASTURE | 59/92 | 14 | 14-16 |
| 6 | (6,3) | COOP | 33/92 | 14 | 14-16 |
| 6 | (7,1) | WHEAT | 32/92 | 16.0 | 14-16 |
| 6 | (7,4) | PASTURE | 46/92 | 16.0 | 14-18 |
| 6 | (7,4) | COOP | 46/92 | 16.0 | 14-17 |
| 6 | (5,2) | COW | 78/92 | 20.0 | 15-23 |
| 6 | (6,0) | STRAWBERRY | 52/92 | 21.0 | 15-22 |
| 6 | (6,3) | SHEEP | 23/92 | 15 | 15-15 |
| 6 | (6,3) | GOOSE | 33/92 | 15 | 15-17 |
| 6 | (6,3) | COW | 36/92 | 16.0 | 15-17 |
| 6 | (7,0) | STRAWBERRY | 66/92 | 22.0 | 15-22 |
| 6 | (7,4) | SHEEP | 23/92 | 15 | 15-17 |
| 6 | (7,4) | GOOSE | 46/92 | 17.0 | 15-18 |
| 6 | (7,3) | STRAWBERRY | 53/92 | 16 | 16-21 |
| 6 | (8,0) | WHEAT | 18/92 | 19.0 | 16-22 |
| 6 | (8,1) | STRAWBERRY | 62/92 | 16.0 | 16-19 |
| 6 | (8,4) | PASTURE | 29/92 | 19 | 16-21 |
| 6 | (7,4) | COW | 23/92 | 18 | 17-19 |
| 6 | (8,1) | WHEAT | 23/92 | 19 | 17-19 |
| 6 | (8,4) | SHEEP | 9/92 | 17 | 17-22 |
| 6 | (9,1) | WHEAT | 85/92 | 17 | 17-22 |
| 6 | (6,2) | COOP | 18/92 | 18.0 | 18-18 |
| 6 | (7,2) | WHEAT | 67/92 | 18 | 18-19 |
| 6 | (7,2) | STRAWBERRY | 23/92 | 18 | 18-20 |
| 6 | (8,0) | STRAWBERRY | 67/92 | 19 | 18-21 |
| 6 | (8,4) | COOP | 28/92 | 20.0 | 18-20 |
| 6 | (6,2) | PASTURE | 29/92 | 20 | 19-22 |
| 6 | (6,2) | GOOSE | 18/92 | 19.0 | 19-19 |
| 6 | (8,1) | TOMATO | 5/92 | 19 | 19-19 |
| 6 | (8,3) | WHEAT | 31/92 | 19 | 19-22 |
| 6 | (8,4) | GOOSE | 28/92 | 21.0 | 19-21 |
| 6 | (8,4) | COW | 20/92 | 20.0 | 19-21 |
| 6 | (9,0) | WHEAT | 30/92 | 21.0 | 19-22 |
| 6 | (9,3) | WHEAT | 30/92 | 21.0 | 19-22 |
| 6 | (6,2) | COW | 21/92 | 20 | 20-23 |
| 6 | (7,3) | WHEAT | 24/92 | 22.0 | 20-22 |
| 6 | (8,2) | STRAWBERRY | 53/92 | 21 | 20-22 |
| 6 | (8,3) | PASTURE | 9/92 | 21 | 20-22 |
| 6 | (9,0) | STRAWBERRY | 52/92 | 20.0 | 20-22 |
| 6 | (9,3) | STRAWBERRY | 11/92 | 21 | 20-22 |
| 6 | (6,2) | SHEEP | 8/92 | 21.0 | 21-21 |
| 6 | (8,2) | WHEAT | 28/92 | 21.0 | 21-21 |
| 6 | (9,2) | WHEAT | 10/92 | 21.0 | 21-21 |
| 6 | (9,2) | STRAWBERRY | 5/92 | 21 | 21-21 |
| 6 | (9,4) | WHEAT | 14/92 | 21.5 | 21-22 |
| 6 | (8,3) | COW | 5/92 | 22 | 22-23 |

## 1d. Modal layout at the end of days 0, 1, 2, 3, 5, 6 (after the end-of-day refresh)

Legend: w wheat, m melon, s strawberry, c carrot, t tomato, C cow, S sheep, G goose, o/p empty coop/pasture, x weed, . empty, # locked. Number = % of games with that modal content.

End of day 0:
```
w100 w100 w 99 .100 .100 #100 #100 #100 #100 #100
w100 w100 w100 m100 m100 #100 #100 #100 #100 #100
w100 m100 w100 m100 C100 #100 #100 #100 #100 #100
.100 m100 .100 . 99 S100 #100 #100 #100 #100 #100
w100 m100 S100 S100 C100 #100 #100 #100 #100 #100
```
End of day 1:
```
w100 w100 w 99 m100 m100 #100 #100 #100 #100 #100
w100 w100 w100 m100 m100 #100 #100 #100 #100 #100
w100 m100 w100 m100 C100 #100 #100 #100 #100 #100
w 63 m100 m100 m 93 S100 #100 #100 #100 #100 #100
w100 m100 S100 S100 C100 #100 #100 #100 #100 #100
```
End of day 2:
```
s 87 . 87 w 99 m100 m100 #100 #100 #100 #100 #100
s 58 s 98 w100 m100 m100 #100 #100 #100 #100 #100
w 99 m100 .100 m100 C100 #100 #100 #100 #100 #100
w 63 m100 m100 m 93 S100 #100 #100 #100 #100 #100
s100 m100 S100 S100 C100 #100 #100 #100 #100 #100
```
End of day 3:
```
s 97 s 88 s100 m100 m100 #100 #100 #100 #100 #100
s 99 s100 s100 m100 m100 #100 #100 #100 #100 #100
s100 m100 s 87 m100 C100 #100 #100 #100 #100 #100
s100 m100 m100 m 93 S100 #100 #100 #100 #100 #100
s100 m100 S100 S100 C100 #100 #100 #100 #100 #100
```
End of day 5:
```
s100 s100 s100 m100 m100 #100 #100 #100 #100 #100
s100 s100 s100 m100 m100 #100 #100 #100 #100 #100
s100 m100 s100 m100 C100 #100 #100 #100 #100 #100
s100 m100 m100 m 93 S100 #100 #100 #100 #100 #100
s100 m100 S100 S100 C100 #100 #100 #100 #100 #100
```
End of day 6:
```
s100 s100 s100 m100 m100 s 70 s 57 s 72 s 73 s 57
s100 s100 s100 m100 m100 s 61 w 76 s 65 s 67 w 92
s100 m100 s100 m100 C100 C 85 . 47 w 73 s 58 . 84
s100 m100 m100 m 93 S100 C100 C 39 s 58 . 54 . 54
s100 m100 S100 S100 C100 C 75 C 60 G 50 . 38 . 84
#100 #100 #100 #100 #100 #100 #100 #100 #100 #100
#100 #100 #100 #100 #100 #100 #100 #100 #100 #100
#100 #100 #100 #100 #100 #100 #100 #100 #100 #100
#100 #100 #100 #100 #100 #100 #100 #100 #100 #100
#100 #100 #100 #100 #100 #100 #100 #100 #100 #100
```

## 1e. What drives the divergence

Step 24 (day 1 hour 0) always sends 8 HIRE orders; the number that executes is set by the $0-9 left after the day-0 wheat-seed loop (hire costs 1,1,2,3). Games with the same number of step-24 hires keep much more similar day-1 plans:

| hires executed at step 24 | games | money at step 24 | day-1 full-action agreement within group (steps 24-47) | total day-1 hires: games |
|---|---|---|---|---|
| 0 | 6 | 0-0 | 67% | 8:6 |
| 1 | 24 | 1-1 | 56% | 2:10, 9:14 |
| 2 | 10 | 2-3 | 78% | 3:10 |
| 3 | 25 | 4-6 | 92% | 4:25 |
| 4 | 27 | 7-9 | 39% | 4:27 |

Agreement over all 92 games on steps 24-47: 29%.

Money differences on day 0 come only from the wheat round trips of steps 0-6, whose prices move with the opponent's wheat orders in the same steps (shared market, lockstep):

| opponent wheat units bought at step 0 | games | DSM paid for its 5 wheat at step 0 | DSM net wheat cash steps 0-6 | median money step 24 | money at step 24: games |
|---|---|---|---|---|---|
| 0 | 9 | 133 | -133 | 8 | 6:1, 7:3, 8:5 |
| 1-5 | 40 | 136 | -135 | 6 | 2:3, 3:5, 4:3, 5:1, 6:18, 7:3, 8:7 |
| 6-10 | 12 | 140 | -140 | 1 | 0:3, 1:7, 4:1, 9:1 |
| >10 | 31 | 150 | -150 | 1 | 0:3, 1:17, 2:1, 3:1, 5:1, 7:7, 9:1 |

Step 13 variant: `SELL WHEAT 1, BUY_SEED WHEAT 2` in 56 games, `... BUY_SEED WHEAT 5` in 36. Money at step 13: 41-65 vs 37-60 (overlapping); wheat seeds executed on day 0: {9: 17, 10: 38, 11: 1} vs {8: 1, 9: 6, 10: 29}. Only the batching differs; the day-0 wheat total is the same (9-10, as many as cash allows).

Weeds on DSM's farm at the end of days 0-5 (sum over games): {0: 1, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}; effective DIGs days 0-5: {1: 1}. Weeds are too rare to explain the day-1 divergence.
