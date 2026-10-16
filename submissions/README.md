# Submission packages

Every agent we ran on the Kaggriculture ladder, plus every sealed candidate of the final v12 line, exactly as packaged. Each folder holds:

- `submission.tar.gz`: the file that was (or would have been) uploaded, byte for byte;
- `main.py`: the agent, identical to the one inside the archive (some use CRLF line endings; `.gitattributes` keeps them as they are);
- `LICENSE.txt` and `NOTICE.txt`: the upstream Apache-2.0 license and the attribution notice, including the list of our changes.

Figure 06 in [docs/history.md](../docs/history.md) shows every package on a timeline.

Status: **final** = one of the two submissions active at the end of the competition; **live** = ran on the ladder and was later replaced; **sealed** = built and tested, not uploaded; **rejected** = tested and dropped. The public agents we uploaded verbatim (cha22, rescue, morewheat, farm2945, herdsafe_race) are third-party code and are not included; Frank Yang's own planner (uploads #1 to #19 in docs/history.md) is not included either.

The hash columns are the first 12 hex digits of SHA-256 (all 34 packages rechecked on 2026-10-16).

| Version | Kaggle id | Uploaded (UTC, 2026) | Status | Change from the previous version | `submission.tar.gz` | `main.py` | Line endings |
|---|---|---|---|---|---|---|---|
| [v3](v3_own_rescue_slot/) | 56515991 | 09-24 08:00 | live | rescue (Dmitrii Gluzdov) + order-slot | `4086fc65ee1f` | `b89bf6f529ad` | LF |
| [v4](v4_own_cha22_slot/) | 56529338 | 09-24 18:47 | live | cha22 + order-slot | `e3c0899443e9` | `81bd2e3ccb6c` | LF |
| [v6](v6_own_cha22_eager_g90/) | 56537002 | 09-25 01:45 | live | + room guard, eager sell (0.3x to 0.9x base), sell ordering | `9eb384837444` | `a8a2e5a1ef57` | LF |
| [v7](v7_own_cha22_band_wheatlead/) | 56552832 | 09-25 14:22 | live | eager band 0.2x to 1.4x, wheat lead | `091983122da8` | `aa5f5b3fa2f1` | LF |
| [v6b](v6b_own_cha22_eager_noceil/) | 56554143 | 09-25 15:24 | live | v6 without the eager-sell ceiling | `d2a5a286c603` | `52201af588fb` | LF |
| [v7b](v7b_own_cha22_eager_wheatlead/) | 56554961 | 09-25 16:06 | live | v6b + wheat lead | `177fbe1007f8` | `e47e94d121b0` | LF |
| [v7c](v7c_own_cha22_eager_wheatlead_fixes/) | 56559314 | 09-25 20:03 | live | + SHEEPFEED fix, FERTMORE | `2cc0e9343bd7` | `5c3c676b6e48` | LF |
| [v8](v8_own_cha22_tick_guard10/) | 56573604 | 09-26 07:55 | live | + TICK wheat arbitrage with peer guard (10 units) | `50777390131e` | `c9eb01cb1606` | CRLF |
| [v9](v9_own_cha22_tick_trapguard/) | 56587029 | 09-26 19:12 | live | + trap guard | `d42276df5c75` | `65fc2e3d6349` | LF |
| [v10](v10_own_cha22_tick_trapguard_tomato/) | 56600500 | 09-27 06:30 | live | + V219 tomato gate for two early shops | `0888c3fd862a` | `2a30594b29b4` | CRLF |
| [v11a](v11_own_cha22_tick_trapguard_tomato_prebuy0/) |  |  | sealed | v10 + pre-buy trap extension | `7eef4c49f4d6` | `5e7dbfca840d` | CRLF |
| [v11](v11_own_cha22_tick_trapguard_tomato_prebuy0_eod_rev/) | 56623261 | 09-28 00:09 | live | v11a + end-of-day harvest deferral, rev_guard | `a9e7064cfbed` | `521b4c71381b` | CRLF |
| [V10_CarreraGT](V10_CarreraGT/) | 56633607 | 09-28 07:36 | live | v11 + 18 tomatoes (x18g), TICK from day 8 | `9e21e8d7b6d5` | `293c30c392f1` | CRLF |
| [v12](v12_own_cha22_tick_fade_resume/) |  |  | sealed | v8 + FADE, anti-fader detection, TICK resume | `75c26789ebc0` | `90423b85dd2f` | CRLF |
| [v12_1](v12_1_own_cha22_tick_fade_resume_late/) |  |  | sealed | TICK from day 13 | `dee99a58ebf8` | `97ad921ca530` | CRLF (last 2 lines LF) |
| [v12_2](v12_2_own_cha22_tick_fade_resume_late_sched/) |  |  | sealed | + scheduled fade | `1e3cd0eabb70` | `a2f8d6a44367` | LF |
| [v12_3](v12_3_own_cha22_tick_fade_resume_late_sched_trap/) |  |  | sealed | + trap guard | `90ad1c7caf86` | `beb5de584849` | LF |
| [v12_4](v12_4_own_cha22_tick_fade_resume_late_sched_trap_tomato/) |  |  | sealed | + V219 tomato gate | `0c34d50e7ee5` | `bbfba0d4ca9d` | LF |
| [v12_5](v12_5_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard/) |  |  | sealed | + FADE P&L guard | `a70def38e4eb` | `153f87fb3627` | LF |
| [v12_6](v12_6_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade/) |  |  | sealed | + GFADE (phase 1 to 3 arbitrageurs) | `e80ce8bd0528` | `440492992ba9` | LF |
| [v12_7](v12_7_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0/) |  |  | sealed | + pre-buy trap extension | `eb60c89fa673` | `12cddf931987` | LF |
| [v12_8](v12_8_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod/) |  |  | sealed | + end-of-day harvest deferral | `1e1f8d883844` | `685a2516228e` | LF |
| [v12_9](v12_9_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n/) |  |  | sealed | + fade position up to 2N | `96de0e8c6e27` | `33203aa02bdb` | LF |
| [v12_10](v12_10_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_sq/) |  |  | rejected | + squeeze layer | `ea4256226aeb` | `d628a6b0280b` | LF |
| [v12_11](v12_11_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind/) |  |  | sealed | v12_9 + fade wind-down | `f784bf69c789` | `140d0eddf04c` | LF |
| [v12_12](v12_12_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room/) |  |  | sealed | + precise warehouse room | `8a98ca4800c1` | `38a0754cd455` | LF |
| [v12_13](v12_13_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room_cap/) |  |  | sealed | + base wheat-sell cap | `ebbf9f94b00d` | `8661b7bfaadc` | LF |
| [v12_14](v12_14_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room_cap40/) |  |  | sealed | cap only against 40+ per round | `a554253bb47c` | `6c65141c82f9` | LF |
| [v12_15](v12_15_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room_cap40_x18g/) |  |  | sealed | + 18 tomatoes (x18g); uploaded as V12_AventadorSVJ | `299a09c51919` | `08a0d374aedd` | LF |
| [V12_AventadorSVJ](V12_AventadorSVJ/) | 56649860 | 09-28 18:47 | final | v12_15 renamed; main.py byte-identical, only NOTICE differs | `c67090fde7d4` | `08a0d374aedd` | LF |
| [v12_16](v12_16_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room_cap40_x18g_strawx/) |  |  | rejected | + strawberry block | `855f6a099c57` | `336d96e150fb` | LF |
| [v12_17](v12_17_own_cha22_sheep_cash_reserve/) |  |  | sealed | v12_15 + sheep cash reserve | `4a1433365ae2` | `524bc579c960` | LF |
| [v12_18](v12_18_own_cha22_cash_tomato_late/) |  |  | sealed | v12_17 + late tomato crews | `fdccf3192e7e` | `a63ac3394d27` | LF |
| [v12_19](v12_19_own_cha22_adaptive_inputs/) | 56713491 | 09-30 16:41 | final | v12_18 + layout-adaptive fertilizer | `e9f45256ee57` | `3b6a78997364` | LF |

Run any of them locally:

```bash
python tools/official_check.py submissions/v12_19_own_cha22_adaptive_inputs/main.py
```
