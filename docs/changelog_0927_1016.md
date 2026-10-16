# Change log: Sep 27 to Oct 16

Every version built after Sep 27, why it was built, how it was evaluated and what it did live, plus the uploads and the decisions behind them. Two lines ran in parallel: the **public line** (v11 and V10_CarreraGT, without FADE) and the **ace line** (v12_5 to v12_19, with FADE). Package hashes were recomputed on Oct 16. Terms and tools are explained in [solution.md](solution.md) and [evaluation.md](evaluation.md); "replays" are live-replay counterfactuals with the real shop order forced, and the 917, 1142, 1480, 1528 and 1572-game sets are the deduplicated live replays available at different times.

## Contents

- [Summary](#summary)
- [Versions](#versions)
- [Uploads](#uploads)
- [Each version](#each-version)
- [Ideas tested and dropped](#ideas-tested-and-dropped)
- [Decisions](#decisions)
- [Tools, scripts and reports added](#tools-scripts-and-reports-added)

## Summary

- Final Bradley-Terry leaderboard: **#553 of 10,148, 4499.2, bronze medal**; the silver line (#507) was 15.3 points above.
- The two submissions active at the end: V12_AventadorSVJ (56649860, the code of v12_15) and v12_19 (56713491). V10_CarreraGT was replaced by v12_19 on Sep 30 at 16:48.
- After the v10 upload the live rank peaked at #182 (Sep 28 18:30). As the strong teams' final versions arrived and the score band compressed, it fell from #401 on Oct 1 to between #526 and #552 from Oct 11.
- The remaining gap was production (sizing the farm to the shops that open). The market layers (arbitrage, fading, sell timing) added real but small gains.

## Versions

Hashes are the first 8 hex digits of SHA-256 of `submission.tar.gz` and of the `main.py` inside it.

| Built (UTC) | Version | Change from the previous version | tar.gz | main.py | Line endings | Uploaded |
|---|---|---|---|---|---|---|
| Sep 27 09:50 | v12_5 | FADE P&L guard | a70def38 | 153f87fb | LF | no |
| Sep 27 10:58 | v12_6 | GFADE: fading arbitrage in phases 1 to 3 | e80ce8bd | 44049299 | LF | no |
| Sep 27 21:43 | v11a (`v11_own_cha22_tick_trapguard_tomato_prebuy0`) | public-line v10 + phase-3 pre-buy trap rule | 7eef4c49 | 5e7dbfca | CRLF | no |
| Sep 27 21:45 | v12_7 | v12_6 + the same trap rule | eb60c89f | 12cddf93 | LF | no |
| Sep 28 00:00 | v11 (`..._prebuy0_eod_rev`) | v11a + end-of-day harvest deferral (eod2) + rev_guard | a9e7064c | 521b4c71 | CRLF | yes, Sep 28 00:09, 56623261 |
| Sep 28 00:13 | v12_8 | + eod2 | 1e1f8d88 | 685a2516 | LF | no |
| Sep 28 00:25 | v12_9 | fade position limit from N to 2N | 96de0e8c | 33203aa0 | LF | no |
| Sep 28 02:17 | v12_10 | squeeze layer (dropped) | ea425622 | d628a6b0 | LF | no |
| Sep 28 03:57 | v12_11 | wind-down of the fade position | f784bf69 | 140d0edd | LF | no |
| Sep 28 06:00 | v12_12 | precise warehouse reservation when restocking | 8a98ca48 | 38a0754c | LF | no |
| Sep 28 06:17 | v12_13 | cap on the base's wheat sells | ebbf9f94 | 8661b7bf | LF | no |
| Sep 28 06:36 | v12_14 | cap only against arbitrageurs of 40+ per round | a554253b | 6c65141c | LF | no |
| Sep 28 07:01 | v12_15 | + the public line's x18g (18 tomatoes) | 299a09c5 | 08a0d374 | LF | as V12_AventadorSVJ |
| Sep 28 07:35 | V10_CarreraGT (research name v11x) | v11 + x18g + TICK from day 8 | 9e21e8d7 | 293c30c3 | CRLF | yes, Sep 28 07:36, 56633607 |
| Sep 28 10:36 | V12_AventadorSVJ | main.py byte-identical to v12_15; only the name in NOTICE differs | c67090fd | 08a0d374 | LF | yes, Sep 28 18:47, 56649860 |
| Sep 28 12:45 | v12_16 | strawberry block STRAWX (dropped) | 855f6a09 | 336d96e1 | LF | no |
| Sep 29 11:54 | v12_17 | cash reserve for extra sheep in wool worlds on day 11 | 4a143336 | 524bc579 | LF | no |
| Sep 30 04:49 | v12_18 | late tomato crews only on days 27 to 29; includes v12_17 | fdccf319 | a63ac339 | LF | no |
| Sep 30 15:52 | v12_19 | supplementary fertilizer loosened by farm-layout similarity | e9f45256 | 3b6a7899 | LF | yes, Sep 30 16:41, 56713491 |

## Uploads

| Submission | Uploaded (UTC) | Version | Replaced | Description as submitted | Final live rating |
|---|---|---|---|---|---|
| 56600500 | Sep 27 06:30:51 | v10 | v8 | v10: v9 + early-shop tomato investment (cha22 V219 also qualifies with two pizza / farmers-market shops open by day 9) + tick-trap guard; cha22 base by Abhinav0370, Apache-2.0, sha 127ed3e6 patched (see NOTICE) | 2494.4 (frozen) |
| 56623261 | Sep 28 00:09:32 | v11 | v9 (frozen at 2490.6) | v11: v10 + prebuy-trap guard + end-of-day harvest deferral + tick arbitrage keeps running beside plain wheat churners and pauses only for a rival trading against it; cha22 base by Abhinav0370, Apache-2.0, sha 127ed3e6 patched (see NOTICE) | 2021.5 (frozen) |
| 56633607 | Sep 28 07:36:28 | V10_CarreraGT | v10 | V10_CarreraGT: v10 + prebuy-trap guard + end-of-day harvest deferral + tick arbitrage from day 8 that keeps running beside plain wheat churners and pauses only for a rival trading against it + 18 V219 tomatoes when 4+ pizza/farmers-market shops open by day 18; cha22 base by Abhinav0370, Apache-2.0, sha 127ed3e6 patched (see NOTICE) | 2206.9 (frozen) |
| 56649860 | Sep 28 18:47:06 | V12_AventadorSVJ | v11 | V12_AventadorSVJ: v10 + prebuy-trap guard + end-of-day harvest deferral + wheat inventory management + 18 V219 tomatoes when 4+ pizza/farmers-market shops open by day 18; cha22 base by Abhinav0370, Apache-2.0, sha 127ed3e6 patched (see NOTICE) | 2046.0 |
| 56713491 | Sep 30 16:41:08 | v12_19 | V10_CarreraGT | v12_19: V12 + adaptive supplementary fertilizer tours from observed farm-layout similarity; retains cash reserve and late tomato crews. cha22-derived, Apache-2.0; see NOTICE. | 2065.7 |

The descriptions of the ace line deliberately do not name the fade layers. Every upload was downloaded again afterwards and matched the local package byte for byte.

## Each version

### v12_5 (Sep 27)

- **Change**: FADE's per-unit profit m is inferred exactly from the next step's wheat stock (both legs sit in the last order slot). If m averages -1.2 or worse over the last 4 rounds, FADE is switched off for the game and the rotating position is sold once.
- **Why**: the risk of rivals trading against FADE. Two emulated opponents were built for it, `emu_antifade` and `emu_antifade2`.
- **Evaluation**: a first version with a threshold of 0 switched FADE off wrongly in 69 of 917 replays (the public slot-0 arbitrageurs The Grower, daoviet and TK256 swing between -0.7 and +0.9), costing 25 per game and 3 flipped games; hence -1.2. On the panel, switching FADE off would cost 21.3k per game against `emu_tick0`, 1.8k against `emu_antifade` and 1.0k against `emu_antifade2`, so FADE stays net positive even against them. Official self-play passed.

### v12_6 (Sep 27)

- **Change**: GFADE. When a rival arbitrages in phases 1 to 3 (mostly the public "one step off" layer: buy 45 to 86 at `s % 4 == 3` from slot 0 or 1, sell the next step) and at least 2 of the last 4 cycles were real arbitrage, sell up to 90 in the last slot after its buy and buy back after its sell. TICK is held step by step, avoiding the scheduled-fade steps and the trap counter steps, with the same P&L switch-off.
- **Why**: phase arbitrageurs such as kyy666, len8487, emreaydin, KouFu, ZHOU HONGYI and Fabian appeared in 9 of 917 replays and 8 of the latest 389 games.
- **Evaluation**: 9 phase-arbitrage replays +1940 per game, 1 flip won (emreaydin -2526 → +263), 0 lost; kyy666 +6155, len8487 +7555. On 917 replays only 14 games changed, +19 per game, 1 flip won, 0 lost. The panel's 120 games were identical to v12_5, and the emulated phase-3 arbitrageur `emu_tick3` gave +15.7k per game. Activating after 3 of 4 cycles was worse than 2 of 4.

### v11a and v12_7 (Sep 27 evening)

- **Change**: the trap guard's pre-buy rule also counts a rival that buys 25+ at s0-1 and sells 25+ at s0 or s0+1 (except at the five scheduled-fade steps). v11a adds it to the public line (v10), v12_7 to the ace line (v12_6).
- **Why**: on the evening of Sep 27, v9 fell from 2508 to 2486. Strong teams were uploading new versions (production families such as mtmr_s1, トゲアリ, kwa and sekai013, all of which uploaded again on Sep 30), and a new trap appeared: the cha22 mirror variants kwon yong deuk and curiosity bought 73 to 90 wheat at `s % 4 == 3` from slot 0 or 1 and sold it at `s % 4 == 0` in slot 9, filling one unit at a time against our last-slot tick buy. v10 lost 11k to 18k per game to them.
- **Evaluation (v11a)**: replaying the day's 12 big losses, kwon -18258 → +23767 and curiosity -11201 → +139; the other 10 unchanged. +21k to +41k per game against `emu_prebuy0`. On 917 replays 10 games changed, +34 per game, 2 flips won (KouFu, emreaydin), 0 lost; the 144 panel games were identical.
- **Evaluation (v12_7)**: kwon +23904; on the 9 phase-arbitrage games +826 per game over v12_6 and one more flip won; +74k against `emu_prebuy0` and +76k against `emu_tick3`. On 917 replays against v12_6, 11 games changed, +9 per game, 2 flips won, 0 lost (820 wins, 89.4%); against v10, 27 flips won and 1 lost.

### v11 (uploaded Sep 28 00:09, 56623261)

- **Change**: v11a plus two layers (`research/carrera/layers/`). **eod_defer2**: at hour 23, when what the workers carry exceeds the free warehouse room, last-step harvests of animal products and of tomatoes and strawberries that are not at the end of their life become "stay" (fertilizer and one-time crops are still collected). **rev_guard**: TICK no longer stops for the whole game when a rival arbitrages in the same direction; it stops only when the rival trades against it (selling 10+ when we buy and buying 10+ back the next step, twice in the window).
- **Why**: 155 of 200 live games had end-of-day overflow, destroying 178 per game on average; and the old rule let plain peer arbitrageurs keep the tick profit to themselves.
- **Evaluation**: on 1029 live replays v10 won 870, v11a plus eod2 (cg1) 877 and v11 (cg4) 901 (against cg1: 27 flips won, 3 lost, +313 per game). On the panel of 13 opponents × 30 worlds: v10 382, cg1 383, cg4 384 wins; +16.8k per game against `emu_tick0`, +35.7k against `emu_prebuy0`, +18.9k against `emu_tick3`, 26 of 30 against `emu_antifade`, 30 of 30 against `emu_antifade2`. 399 W / 1 L in 400 games each against the live v9 and v10. Official self-play passed; the longest step took 0.05 s.
- **Live**: replaced v9. It was matched slowly, mostly against 1700 to 2000 opponents: 117 W / 8 L and 2017 at Sep 28 18:30. Replaced by V12_AventadorSVJ at 18:51, frozen at 2021.5.

### v12_8 (Sep 28 00:13)

- **Change**: eod_defer2 added unchanged as the outermost layer. rev_guard was not ported: in the ace line, peer arbitrageurs are handled by FADE (+21.5k per game against `emu_tick0`, more than rev_guard plus counter-trading's +16.8k), and with rev_guard TICK never stops, so FADE never starts.
- **Evaluation**: on 917 replays against v12_7, 476 games changed, +69 per game, 2 flips won, 0 lost, worst game -412; 822 wins in total. On the 144 panel games +20 to +110 per opponent.

### v12_9 (Sep 28 00:25)

- **Change**: the FADE and GFADE position limit grows from the rival's lot N to 2N (still within 90, the warehouse room and the feed reserve).
- **Why**: against Ilya & Yurnero (28 per round from slot 0) FADE sold only 28 and lost 119, while the public line's counter layer with a fixed 80 made +1382. Counting the loss on the rival's buy-back, the optimum is 2N.
- **Evaluation**: the latest 90 games +50 per game, 1 flip won (Ilya → +663), 0 lost; on 917 replays 98 games changed, +29 per game, no flips; +5712 per game against `emu_tick30` (v12_8 +3860, v11 +5093).

### v12_10 (Sep 28 02:17, dropped)

- **Change**: a squeeze layer. When the order list is full (10 orders) and 5+ unsold milk, strawberries or wool sit in the warehouse, they replace the smallest fertilizer, egg, carrot, tomato or melon sell.
- **Result**: the latest 90 games +81, no flips; on 917 replays ±0 per game, 4 flips won, 3 lost. Exact pricing of 1592 cases in 150 games: always squeezing -429 per game, squeezing when the rival sold at the same hour the day before -47, and even perfect hindsight only +69. An earlier estimate that "selling one step late costs 663 per game" had its sign reversed.

### v12_11 (Sep 28 03:57)

- **Change**: wind-down of the fade position. The buy-back leg runs only if another fade step follows (step ≤ 713), and the last fade step sells the whole position beyond the feed reserve into the rival's lift.
- **Why**: in the Ilya game the agent bought back 83 wheat at step 717 as usual, with no fade step left, losing 736.
- **Evaluation**: Ilya +663 → +1258. On 917 replays only 5 games changed, all better (+182 to +759), no flips. The panel (8 opponents × 24 games) had the same results as v12_9 (189 W / 3 L).

### v12_12 (Sep 28 06:00)

- **Change**: precise warehouse reservation when restocking: reserve room only for workers that the base route will unload in the next 3 steps; at hour 23, and when no route is known, reserve for everyone as before.
- **Why**: an audit of 60 games found that at restock steps the workers carried 39 items on average, so the FADE position averaged only 47 while rivals traded 60 to 90.
- **Evaluation**: Hikaru +1032 → +3975, Ilya +1258 → +2613, Joseph Ayanda -5533 → +1096 (flip won). On 917 replays +174 per game, 1 flip won, 0 lost; on the latest 186 games +249 per game, 1 flip won, 1 lost (american gothic -2357).

### v12_13 (Sep 28 06:17)

- **Change**: while the rival keeps arbitraging, the base's wheat sells (including inner layers) are capped at its own wheat (warehouse minus the fade position), except at hour 23; the GFADE reserve returns to full.
- **Why**: a step-by-step trace of the Ken_Ken_Pa game showed the base selling the FADE position as surplus wheat in phase 3 while its supply module bought it back in phase 0; only 44 of 71 restocks sold into the rival's lift. Hiding the position from the base instead cost 5k to 17k per game, hence a cap.
- **Evaluation**: Ken_Ken_Pa +11166 → +13648, Wang H2O +10198 → +12089, Hikaru +3975 → +5296. The latest 186 games +246 per game, 1 flip won, 0 lost; 917 replays +161 per game, 1 flip won, 1 lost (RangerSnow +310 → -269).

### v12_14 (Sep 28 06:36)

- **Change**: the cap applies only against rivals averaging 40+ per round.
- **Why**: v12_13 dropped from 24 W / 0 L to 22 W / 2 L against the 30-per-round `emu_tick30`, and in the 917 replays arbitrageurs of 10 to 34 per round cost 193 per game.
- **Evaluation**: `emu_tick30` back to 24 W / 0 L; no flips against v12_13 on 917 replays; against v12_11 +335 per game, 2 flips won, 1 lost, 823 wins; full panel 189 W / 3 L (v12_13: 187 W / 5 L).

### V10_CarreraGT (uploaded Sep 28 07:36, 56633607; research name v11x)

- **Change**: v11 plus two changes. **x18g** (`research/carrera/patch_x18g.py`, a patch to the embedded base source): when 4+ of the first 6 shops open by day 18 are pizza shops or farmers' markets, V219 plants 18 tomatoes (8 more tiles in rows 7 and 8), regroups the workers (2 groups of 9 tiles normally, 3 groups of 6 on days 18, 24 and 26 to 28), buys 18 seeds, fertilizes 10 tiles and brings tomatoes to the warehouse before each day ends; otherwise the code is identical to the original line by line. **TICK from day 8** instead of day 10 (`layers/params_t_fd8.py`).
- **Why**: tomatoes were the largest gap in live losses; strong mirror variants planted 18 on day 18, we planted 10.
- **Evaluation**: an ungated x18 kept the workers busy past midnight and overflow destroyed 13k of tomatoes in a test game; with delivery but no gate (x18b), worlds with 2 to 3 tomato shops lost 500 to 1100 per game while 4 shops gained 1176 and 5 shops 4335. x18g changed 43 of 531 tomato-world games (38 better, 5 worse), +130 per game, no flips; a tomato-heavy panel went 160 W / 0 L, +1391 per game. Starting TICK on day 8: +6 per game, 304 games better, 3 worse, no flips. v11x against v11 on 1142 replays: the same results (997 wins), 337 games changed (329 better, 8 worse), +67 per game; panel +65 per game. Official self-play passed.
- **Live**: replaced v10. 2457 after 2 hours; peak 2507.7 at Sep 28 11:08; 2483 at 18:30; 2435 at Sep 29 02:28; 2356 at Sep 29 15:22 (184 games, 89 W / 95 L). Replaced by v12_19 at Sep 30 16:48, frozen at 2206.9.

### v12_15 (Sep 28 07:01) and V12_AventadorSVJ (uploaded Sep 28 18:47, 56649860)

- **Change**: v12_14 plus x18g (the same patch list as the public line). rev_guard and the early TICK start conflict with FADE (tested on the ace, 1 flipped loss each), so only x18g was ported.
- **Evaluation**: on 917 replays against v12_14 +52 per game, 28 games better and 3 worse, no flips; the 412 tomato-world games +106 per game; tomato panel 160 W / 0 L, +1265 per game. Against v11x 823 against 817 wins, +355 per game, 7 flips won, 1 lost (+7000 per game in the 27 games with 40+ arbitrage rounds). Official self-play passed.
- **Packaging**: `gold/front/pack_final_ace.py` renames v12_15 to V12_AventadorSVJ; `main.py` is byte-identical and only the NOTICE differs (hence a different tar.gz hash). After the upload the package was downloaded again and matched byte for byte.
- **After upload**: on 1478 replays the ace beat the CarreraGT code by 24 flips won to 7 lost, +451 per game. The edge came from the roughly 10% of games against arbitrageurs (about +5000 per game); in the other 90% it lost about 30 per game, the cost of starting TICK on day 13.
- **Live**: 41 W / 12 L and 2423 at Sep 28 21:52. By New York day: Sep 28 63 W / 32 L (2430.2 at day end), Sep 29 55 W / 82 L (2312.8), Sep 30 35 W / 69 L (2160.2). Oct 8: 698 games, 327 W / 371 L, 2065.8; Oct 11: 932 games, 441 W / 490 L, 2054.6; final 2046.0.

### v12_16 (Sep 28 12:45, dropped)

- **Change**: STRAWX, a strawberry block. When all 4 shops opened before day 13 are strawberry shops (7% of worlds) and the south-east quadrant is not yet bought, buy it at hour 1, buy seeds, hire our own workers to plant 16 strawberries (25- and 24-plant variants were tried first), water every other day, harvest on days 25, 27 and 29 and carry the crop home in daylight.
- **Why**: in worlds with 6+ strawberry shops the harvest-day quote is 175 to 257; a marginal-revenue estimate promised about 10k net and 16 of 22 losses flipped.
- **Result**, by exact accounting on three such worlds: 25 plants watered daily by 3 to 4 workers cost 13.6k more in labour, -6k to -9.5k per game; 24 plants watered every other day by 2 workers lost a third of the plants to missed watering, -1.5k to -6.2k; 16 plants every other day with 1 worker: +703, -3835 (a win turned into a loss), +26. Land at 4000, seeds at 1600 and about 4k of labour eat the revenue (the 11th to 15th helper of a day cost 89 to 610 each).

### v12_17 (Sep 29 11:54, not uploaded)

- **Change**: on day 11 at hour 1, with two wool shops, the south-east not yet bought and the base's price conditions met, skip one FADE restock so the base has the cash to add 6 sheep early.
- **Why**: in one live game (Subramanya N) a 90-wheat FADE restock delayed the base's day-11 sheep by a day; fixed, the game went from -913 to +4847.
- **Evaluation**: 1426 replays 1195 → 1196 wins, only 2 games changed, 1 flip won, 0 lost; 1480 replays 1219 → 1220; 24 new wool worlds × 8 reacting opponents 184 → 187 wins of 192, no flipped losses. Official self-play passed. Too small to justify replacing CarreraGT on its own.

### v12_18 (Sep 30 04:49, not uploaded)

- **Change**: the four crop crews of the 18-tomato plan are hired only on days 27 to 29, keeping the two fertilizer crews on day 27 and the fertilizer for 18 plants; includes v12_17.
- **Why**: a Sep 29 diagnosis of tomato execution: Ilya & Yurnero also planted 18 and sold 142, while we sold 92 and lost 4 plants to missed watering. A prototype with four crews from day 24 (crew4_full: crews of 5, 5, 4 and 4 tiles, full fertilizer, two fertilizer crews on day 27) raised that game's harvest from 92 to 130 with no dead plants and won 42 instead of 41 of 51 tomato-world games, +4920 per game, but the 128-game reacting panel went from 128 to 127 wins (one `emu_antifade` world from +1503 to -14), failing the gate. In that counter-example tomato revenue rose by 3204 and labour by 5401, so the crews were shortened.
- **Evaluation**: 1480 replays 1219 → 1222 wins, 3 flips won, 0 lost, +193 per game; the latest 30 games of Sep 30 unchanged; the 128-game tomato panel and an independent 128-game reacting panel both stayed at 128 wins; wool worlds 184 → 187 of 192. Official self-play passed. The gain was small and the latest games never triggered it, so it was not uploaded.

### v12_19 (sealed Sep 30 15:52, uploaded 16:41, 56713491)

- **Change**: v12_18 plus layout-adaptive fertilizer. At steps 264, 272 and 280 compare the two public farm layouts and freeze the choice at step 287: if the similarity is below 0.94 all three times, loosen the base's R51 supplementary fertilizer gate (cost × 1.0 + 20, path penalty 0.75, at most two workers); with similar layouts the original rule stays. No identities, replays or seeds are hard-coded.
- **Why**: the Sep 30 audit of the risk to silver: the ace's latest 6 losses were short about 3936, 3721 and 2922 in net cash from tomatoes, strawberries and eggs, and the latest 16 opponent submissions were all newer than the ace, so the strong teams' final versions were arriving.
- **Evaluation**: 1528 replays 1239 → 1248 wins, 9 flips won, 0 lost; the latest 300 games 165 → 172; the latest 20 games 6 → 7; another 24 games 14 → 14; all 1572 deduplicated games 1259 → 1269, 10 flips won, 0 lost, +266 per game. 312 + 48 local reacting-panel games kept their results, and 112 production-only games (neither side arbitraging) were completely unchanged. Official self-play passed. The report noted that the historical gain was only 0.64 percentage points and proved nothing against current production opponents.
- **Live**: official COMPLETE at 16:48; the downloaded package matched the sealed one byte for byte. Oct 1 04:38: 93 games, 53 W / 40 L, 2153.1; Oct 8: 439 games, 215 W / 224 L, 2020.7 (low of 1998.7 on Oct 7); Oct 11: 676 games, 339 W / 336 L, 2057.2; final 2065.7, the team's counted submission. A post-deadline audit of the same games found that the latest 12 games and the 51 games of Oct 6 had exactly the same outcomes as the ace; in 3 games that were already lost and triggered the looser fertilizer gate, we earned 244 to 374 more but the rival 425 to 587 more, so the losses grew (Brayden -234 → -465, Blu3s -7191 → -7242, fufufukakaka -4129 → -4410). The mechanism was not broken down by good; a likely weakness is valuing future yield at current prices without modelling the rival's supply.

## Ideas tested and dropped

| Date | Idea | Result |
|---|---|---|
| Sep 27 | Moving the CARROT last swap day from 23 to 25 or 26 | only 2 to 5 games changed, 1 flip lost |
| Sep 27 | V233 six sheep with one wool shop | -2601 per game, 173 flips lost |
| Sep 27 | Six more sheep (SHEEPX with 2 wool shops) | -519 per game, 60 flips lost |
| Sep 27 | Skipping the 13 south-west strawberries on day 11 (strawberry demand ≤1 among the first 3 shops) | 459 games -2261 per game, 143 flips lost; -167 per game on 120 games with zero demand |
| Sep 27 | South-west strawberries replaced by tomatoes | -3k to -12k per game |
| Sep 27 | TOMX: 8 more tomatoes beside V219 with one more helper | 475 tomato-world games -580 per game, 65 flips lost |
| Sep 27 | Carrot swap layer (LK30 style) | 147 carrot worlds 115 → 67 wins |
| Sep 27 | Countering evening sellers | -178 per game, 3 flips lost |
| Sep 28 | Trap guard without flow reconstruction (`GUARD=0`) | blind to pre-buy traps; the kwon game lost 18k again |
| Sep 28 | No stop for peers, without reversal detection (cg3) | identical on replays, but only 8 of 30 against `emu_antifade` |
| Sep 28 | eod1: deferring every harvest regardless of crop | deferred carrots and wheat that die overnight, 4 flips lost |
| Sep 28 | rev_guard stopping after a single reversal | all 11 changed games got worse |
| Sep 28 | TICK's sell forced into slot 0 ahead of our milk sells | -717 per game, 116 flips lost |
| Sep 28 | TICK minimum gain 1 or 6; lots of at most 60 | +2 / -63 (3 games up, 4 down) / -192 (3 up, 15 down) |
| Sep 28 | A marginal-price floor for sales (mcap) | 0.3× throughout: -858 per game (15 up, 144 down); after day 27 only: -136 (2 up, 12 down) |
| Sep 28 | TICK from day 12 or 10 (917 replays then) | +10 and +42 per game, 1 flip lost each |
| Sep 28 | Resuming TICK after 3 quiet cycles instead of 6 | -25 per game, 1 flip lost |
| Sep 28 | Following small arbitrageurs instead of stopping (th30) | -15 per game, 2 flips lost |
| Sep 28 | Starting FADE after a single cycle (hits1) | +57 per game, but 1 flip won and 1 lost, same wins |
| Sep 28 | cap3; position limit 95 | -96 with 1 flip lost; -26 with 1 flip lost |
| Sep 28 | Delaying tick-step sells by one step | exact pricing of 3948 orders: -1179 net |
| Sep 28 | Holding milk and wool to 20:00 against evening sellers | milk rivals +2544, wool rivals +4318 |
| Sep 28 | Switching off the base's HD2 animal choice | -301 per game, 29 flips lost |
| Sep 28 | A route library from 27 replays of a strong production team (unreal), keyed by the first two shops | 59.5k per game locally against 110.5k for v11x; 16 W / 51 L on that team's intact replays |
| Sep 28 | G1a: 8 geese instead of the late strawberries on day 11 | only +0.8k to +1.0k per triggered world; no loss within 1.5k among the 96 triggered games, so nothing to flip |
| Sep 28 | G3: early rolling carrots | carrot to wheat price ratio 1.1 to 1.4 on days 12 to 20, below the 1.45 needed to break even |
| Sep 28 to 29 | A from-scratch production agent (p6) | -7.9k per game against v7c; 3 W / 70 L on the unreal replays |
| Sep 28 to 29 | p6 executing cha22's route plan / unreal's full allocation / unreal's own plan from unreal's seat | -21.2k / -18.9k / -19.1k per game (unreal itself +7.3k in those games) |
| Sep 28 to 29 | Re-picking the mid-game route with hindsight | only 10 more wins in 861 replays even with hindsight; fewer on held-out games |
| Sep 29 | Three fixes for the 18-tomato execution | -61 / +40 / -85 per game on 80 games, no flips won |
| Sep 29 | crew4_full | +4920 per game in tomato worlds, but 1 flip lost on the reacting panel |
| Sep 29 | TICK switched off on the ace | 1504 replays 1224 → 1115 wins (3 flips won, 112 lost), -616 per game |
| Sep 29 | TICK skipping after a rival's large buy (50 or 30+) the step before | no game changed in 1504: the flow shows only a step later, and TICK had already stopped in those games |
| Sep 29 | The ace with TICK from day 8, 10 or 11 (1528 replays) | 1239 → 1240 wins each, +36 / +33 / +24 per game; flat on the latest 449 |
| Sep 30 | 18-tomato gate lowered from 4 shops to 3 or 2 | -56 per game on 16 games, same wins |
| Sep 30 | 10-tomato early window widened from 24 to 21 or 18 shop-days | -194 per game, near losses worse |
| Oct 1 | Farmer John GS2's small delayed sales ported to v12_19 (after the deadline) | 20 games: 7 wins unchanged, -46.7 per game |

The complete list across the whole competition is in [experiments.md](experiments.md). The standing over time, the reasons for the fall and the lessons are in [postmortem.md](postmortem.md).

## Decisions

- **The upload plan.** From Sep 27 the planned final pair was V10_CarreraGT (public line) plus V12_AventadorSVJ (ace line); the names were chosen first, with the V10 prefix marking the public line and V12 the ace line, and the code evolved underneath them. v11 went up on Sep 28 00:09 under a working name as a deployment check while the final public version was being finished.
- **CarreraGT only 7.5 hours after v11.** It replaced v10, not v11, which kept climbing. A test version and the final version should be the same submission: server validation plus a day of live games is the check (a former #1 had advised keeping a day for it), and the games of a later-replaced submission do not count in the final Bradley-Terry fit. Uploaded before the ace, a later re-upload would only replace itself. In code it was no worse than v11 (1142 replays: identical results, 329 games better and 8 worse, +67 per game). The live silver margin then (about 140 to 190 points) was judged safe, which turned out wrong.
- **The ace on Sep 28 18:47.** It had been planned for the night of Sep 28 or the morning of Sep 29. Once final, uploading early let it settle and left time for a fix, and the exposure of the fade layers to rivals was bounded.
- **Both slots on the v12 base on Sep 30.** v12_19 was built as the silver-protection candidate and sealed with the plan to replace CarreraGT and keep V12. The same-window evidence was small: over the latest 50 games V12 won 18 and CarreraGT 15, over the latest 8 games 2 and 0; on the latest 16 games replayed, V12 won 3, CarreraGT 2, and v9, v8 and v7c 1 each; on 1478 replays the ace beat the CarreraGT code by 24 flips to 7 (+451 per game), and on 48 new games of Sep 29 by 5 to 0. The displayed ratings (2206.9 against 2192.1) were not used, since the two went live at different times against different opponents. Keeping CarreraGT as a hedge of a different style had been proposed on Sep 29 (two identical copies of the ace were rejected as pointless); choosing V12 plus an improved V12 gave the hedge up, and the Oct 1 review listed "two slots from one base are no independent insurance" as a lesson.
- **No production rewrite before the deadline.** On Sep 28 to 29 the production agent p6, executing other teams' plans and re-picking routes all came out negative or flat (see above). Our executor could not even carry out a 2770-rated player's own plan well: about 9% less output, which became about 20k per game in head-to-head play. The written conclusion on the night of Sep 28 was that no route to 2700+ existed before Sep 30. With less than a day left, only one slot to change and a restart from 600 for any broken upload, the last day went into small fixes on the ace.
- **The Bradley-Terry estimate after the deadline.** On Oct 11, counting only games whose opponent submission was still active after the deadline and using each opponent's latest rating (maximum likelihood, scale 400): V12_AventadorSVJ about 2038 (701 counted games, 48.2% won after the deadline; only 102 of its 333 games before the deadline counted), v12_19 about 2036 (657 games, 48.9%). On Oct 13, the same method over the 157 submissions of the 88 teams ranked #470 to #560 put us 66th of the 88, about 30 places and nearly 30 live points below the silver line. The final board put us 46 places below.

## Tools, scripts and reports added

| Path | Purpose |
|---|---|
| `research/carrera/build.py` | public-line builds: base package plus the layers in `layers/`, with a base hash check, a compile check and a check that the last callable is the agent |
| `research/carrera/ab_replay.py` | paired live-replay counterfactuals (forced shop order, `PYTHONHASHSEED=0`), cached by code hash, `--only-ids` |
| `research/carrera/panel.py`, `tomato_panel.py` | the 13-opponent reacting panel with alternating seats; a tomato-world panel (4+ tomato shops forced among the first 6) |
| `research/carrera/replay_econ.py`, `prod_profile.py`, `unreal_panel.py`, `unreal_econ.py` | per-trade accounting by good and by day; production profiles by world type; the panel built from a strong production team's replays and its per-good breakdown |
| `research/carrera/patch_x18.py`, `patch_x18b.py`, `patch_x18g.py`, `layers/*.py` | the 18-tomato patches; eod_defer, eod_defer2, rev_guard, parameter layers and the dropped mcap layers |
| `research/carrera/pack.py` and the audit scripts (`lostdetail.py`, `leaks.py`, `waste.py`, `eodpos.py`, `v233probe.py`, `trace_ts.py`) | deterministic packaging; audits of day-end overflow, waste, hour-23 positions, the V233 module and TICK steps |
| `research/carrera/unreal_lib/build_lib.py` | the route library built from a strong production team's replays (dropped) |
| `gold/front/pack_v11.py`, `pack_v12_5.py` to `pack_v12_16.py`, `pack_final_ace.py`, `mk_tguard.py`, `pack_tguard.py` | version-by-version builds, packaging and official checks of the ace line; the trap guard |
| `research/live_0929/`, `research/live_0930/`, `research/rescue_0930/` | v12_17 (sheep cash), the tomato execution diagnosis, v12_18 and the gate probes, v12_19 (layout-adaptive fertilizer) with its receipt |
| `prod/agents/p6`, `prod/tools`, `prod/oracle` | the from-scratch production agent p6 and the oracle tests |
| `research/notebook_0930_2032/`, `research/notebook_1008/` | scans of the public notebooks (third-party source not included) |
| `research/final_status_1001/`, `postdeadline_1001_1049/`, `forecast_1001/`, `rank_change_1001/`, `opponent_provenance_1001/`, `review_1008/`, `rating_path_1008/`, `v19_oct6_1008/`, `v19_recent_1008/` | post-deadline checks: medal status, the fall in rank, opponents' provenance, v12_19's effect |
| `results/rr_v11_vs_live_0927.md` and the reports listed in [results/README.md](../results/README.md) | the dated reports of this period |
