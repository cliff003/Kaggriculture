# Kaggriculture: market layers on a public route-replay agent

**Team 42** · [Kefei Yan](https://www.kaggle.com/kefeiyan), [Frank Yang](https://www.kaggle.com/ffy208), [yirenw11](https://www.kaggle.com/yirenw11) · **#553 of 10,148 on the final leaderboard, bronze medal**

[Kaggriculture](https://www.kaggle.com/competitions/kaggriculture) is a Kaggle simulation competition. Two agents each run a 10 × 10 farm for 30 days (720 steps) and trade in one shared market, where shops that open in the town at random set the demand; the agent with more money at the end wins. Our own planner stalled at a live rating of 1014.5, so we built on the strongest public agent, [cha22](https://www.kaggle.com/code/abhinav0370/cha22-agent). We wrapped it in layers based on how the engine clears orders: our sells go first, we trade wheat around the town's meals, and we trade against other teams' arbitrage. We reached live #128 on Sep 26 and finished #553 of 10,148 on the final Bradley-Terry leaderboard, 15.3 points (46 places) below silver.

| Final submission | Kaggle id | What it is | Live rating, Oct 16 |
|---|---|---|---|
| **V12_AventadorSVJ** ([package](submissions/V12_AventadorSVJ/)) | 56649860 | cha22 plus our selling layers, fixes to the base, wheat arbitrage around the town's meals (TICK) with its guards, trading against other arbitrageurs (FADE), and 18 tomatoes in tomato-heavy worlds | 2046.0 |
| **v12_19** ([package](submissions/v12_19_own_cha22_adaptive_inputs/)) | 56713491 | V12_AventadorSVJ plus a cash reserve for sheep, tomato crews only on the last days, and a fertilizer rule that adapts to the farm layout | 2065.7 (team score) |

The final Bradley-Terry score (4499.2) uses a different scale. Packages and hashes: [submissions/README.md](submissions/README.md).

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/img/01_agent_dark.png">
  <img alt="Team 42's agent: the public cha22 route-replay agent (41 recorded routes, public reactive layers, our gated source patches) wrapped, inner to outer, by our selling layers, base fixes, TICK, FADE, the trap guard, GFADE and harvest deferral, each with its evidence." src="docs/img/01_agent_light.png">
</picture>

## Highlights

- **We chose the base by measurement.** With our first layer, cha22 beat the 21 distinct codes among the top 30 public notebooks 826 games to 14 in local games. Our own planner had lost all 2,240 of its local games against seven public-level agents.
- **Order position is worth money.** Each player sends up to 10 orders a step, and the engine clears them slot by slot, so a sell in an earlier slot gets the better prices: 20 milk sold first earn 2,802, sold second 1,962. Moving our sells first won 97 of 100 local games against the unmodified cha22.
- **The town eats after the market.** On every fourth step the town eats wheat after the orders clear. TICK buys wheat in the last slot of that step and sells it on the next. With TICK switched off, V12_AventadorSVJ lost 616 per game on 1,504 replays and 112 games flipped to losses (3 the other way); v8, the first version with TICK, took us to live #128 on Sep 26.
- **Whatever you show gets traded against.** Within half a day two teams were trading against TICK: they bought in slot 0 and sold into our last-slot buy, and v8 lost its games against them by about 17k each. A guard that checks our cash against our own orders turned both games around on replay (-16,743 to +13,919 and -17,114 to +10,419). FADE, which trades against other teams' wheat arbitrage, raised our wins in 49 games against arbitrageurs from 41 to 47 on replay.
- **Production decided the top, and every published top-25 method was learned.** Every top-25 team that published its method learned its policy from replays of strong agents. On replay, a production team (unreal, final #54) beat V12_AventadorSVJ 66 to 9, and after the deadline we won one game in three against teams ranked #31 to #507.
- **What we would do differently.** Size production to the shops from day one, and make the second final submission a genuinely different agent: ours were two versions of one base and lost the same worlds.

## Contents

[How the agent works](#how-the-agent-works) · [Results](#results) · [The gap to the top](#the-gap-to-the-top) · [Lessons](#lessons) · [How we tested](#how-we-tested) · [What did not work](#what-did-not-work) · [Repository layout](#repository-layout) · [Setup and usage](#setup-and-usage) · [Documentation](#documentation)

## How the agent works

cha22 follows 41 recorded routes (action tapes from strong past games): every game shares one opening for days 0 to 5, switches on day 6 to the route that matches the first two shops, and moves to an endgame tape on day 27. Dozens of public reactive layers adjust these actions. We left its logic in place: every addition is either a wrapper (it receives the observation and the action of the layer inside it and edits that action) or a patch inside the base source that is off unless its condition holds. Figure 01 shows the order; [docs/solution.md](docs/solution.md) has each layer with its code and evidence.

**Sell first.** Each player sends up to 10 market orders a step. The engine clears them slot by slot, so a sell in an earlier slot fills first at the better price; within one slot both players fill one unit at a time at the same price. From day 12 we move our sells ahead of hires and seed purchases. We also sell milk, strawberries and wool as they arrive, because these markets are shallow: 76 extra milk take the price from 160 to 1.

<details>
<summary><b>02 · How one market step clears</b></summary>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/img/02_order_matching_dark.png">
  <img alt="One engine step: units act, the market clears slot by slot, the town eats, the day ends. Selling 20 milk first earns 2,802 against 1,962 selling second; a real v8 turn shows its sells first and the TICK buy in slot 9." src="docs/img/02_order_matching_light.png">
</picture>
</details>

**TICK.** On every fourth step the town eats wheat after the orders clear. We buy up to 95 wheat in the last slot of that step and sell it the next step. The town removes wheat in between, so we sell back into a tighter market than the one we bought from.

**Trap guard and FADE.** Within half a day other teams traded against TICK. A sandwich trader buys in slot 0 to lift the price and sells into our last-slot buy. The trap guard works out what our own orders should have cost, stops TICK when the cash does not match, and trades back. FADE takes the other side of other teams' wheat arbitrage: it sells after their buy and buys back after their sell.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/img/03_wheat_cycle_dark.png">
  <img alt="Four wheat rounds from real games: TICK alone +9 and sandwiched -117 (live), the trap guard's counter +241 and FADE +206 (on replay)." src="docs/img/03_wheat_cycle_light.png">
</picture>

**Fixes and production patches.** Wrappers fix three things in the base's behaviour: a sheep worker that stalled for a day, fertilizer it sold instead of using, and warehouse overflow at the end of the day. Small gated patches change its tomato and fertilizer modules; each is off unless its condition holds.

## Results

| Measure | Value |
|---|---|
| Final leaderboard (Bradley-Terry, Oct 16) | **#553 of 10,148, 4499.2, bronze** |
| Medal lines | gold #30 at 5099.6; silver #507 at 4514.5 (15.3 above us); bronze #1014 at 4398.5 |
| Best recorded live rank | #128 at 2606.7, Sep 26 10:23 UTC (v8's own rating had peaked at 2679 at 09:39) |
| Around the deadline (Sep 30 23:59 UTC) | live #352 on Sep 30 15:49 and #401 on Oct 1 04:38, 112 and 82 points above the live silver line |
| End of evaluation | live #547 at 2065.7, 27.4 below the live silver line (live ratings use another scale) |

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/img/04_final_board_dark.png">
  <img alt="Final board: team 42 at #553 with 4499.2, 15.3 below the silver line at #507; learned-policy teams at the top; after the deadline we won 33% against ranks 31 to 507 and 62% against 508 to 1014." src="docs/img/04_final_board_light.png">
</picture>

- Only games in which both sides' submissions were still active at the end count, so the two weeks after the deadline decided the board: about 85% of our counted games were played then.
- On Sep 29, 72 of our 95 games were against submissions uploaded after V12_AventadorSVJ went live (Sep 28 18:47 UTC), many of them production-heavy finals; we won 20 and lost 52 of them.
- After the deadline we won 233 of 705 games (33%) against teams ranked #31 to #507 and 572 of 917 (62%) against #508 to #1014.
- The standing over time and the lessons are in [docs/postmortem.md](docs/postmortem.md); every upload and the reasons behind the last four are in [docs/history.md](docs/history.md).

<details>
<summary><b>05 · How the standing developed</b></summary>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/img/05_standing_dark.png">
  <img alt="Team 42's live rank from #128 on Sep 26 to #547 on Oct 16, still inside the silver zone on Oct 8; final board #553." src="docs/img/05_standing_light.png">
</picture>
</details>

<details>
<summary><b>06 · All 39 uploads and 34 packages on one page</b></summary>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/img/06_lineage_dark.png">
  <img alt="Lineage of all 39 uploads and 34 packages from Sep 16 to Oct 16, ending with the final pair V12_AventadorSVJ and v12_19 and the final board #553." src="docs/img/06_lineage_light.png">
</picture>
</details>

## The gap to the top

Every top-25 team that published its method learned its policy from replays of strong agents (behaviour cloning or supervised fine-tuning); at least three of them, #1, #12 and #13, then refined it with self-play PPO. Ours was a route-replay base with hand-written market layers. The teams known for market play, us included, finished between #92 and #802.

| Final rank | Team | Approach |
|---|---|---|
| 1 | M & M & P & Q | behaviour cloning, self-play PPO, heuristic patches; 10.23M-parameter Transformer ([repository](https://github.com/msdsm/kaggriculture-1st-solution)) |
| 2 | Victor @ Tufa Labs | no published method found |
| 3 | DSM | not published; played like an adaptive scheduler in our replays |
| 4 | Farmcore | behaviour cloning on executed actions, staged fine-tuning ([discussion](https://www.kaggle.com/competitions/kaggriculture/discussion/745119)) |
| 5 | 有辣条有权 | supervised fine-tuning on winners' replays ([write-up](https://www.kaggle.com/competitions/kaggriculture/writeups/its-sft-all-the-way-down)) |
| 7 | DECEM | behaviour cloning, 8.2M-parameter entity Transformer ([repository](https://github.com/Decem-Y/kaggriculture-bc)) |
| 12 | Unknown Mother-Goose | behaviour cloning, recurrent policies, PPO self-play ([repository](https://github.com/LinkinPony/kaggriculture-rl-public)) |
| 13 | MarvinTMB | behaviour cloning on two days of top replays, then self-play PPO; about 10 hours of training on one GPU ([repository](https://github.com/CarsonBurke/kaggriculture)) |
| 24 | abozten | per-unit closed-loop behaviour cloning ([write-up](https://www.kaggle.com/competitions/kaggriculture/writeups/cloning-the-best-farmer-on-one-rtx-5070)) |

A strong production team, unreal (final #54), out-earned V12_AventadorSVJ by 6.2k in eggs, 3.6k in strawberries and 3.2k in carrots per game on replay ([more](docs/postmortem.md#the-gap-to-the-top)).

<details>
<summary><b>07 · What the teams above us did differently</b></summary>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/img/07_production_gap_dark.png">
  <img alt="The top five against cha22 (tomatoes in 98% of games against 11%), unreal against our final agent (66 to 9 on replays; +6.2k eggs, +3.6k strawberries, +3.2k carrots a game) and our failed attempts to close the gap." src="docs/img/07_production_gap_light.png">
</picture>
</details>

## Lessons

1. Benchmark every public base before building on one: on Sep 24 the verbatim cha22 reached 2333 in 7 hours against 2100 for rescue in 11, and with our first layer on each, 2481 against 2181 after about 10 hours.
2. Compare live ratings at the same age and in the same window: the same rescue code, uploaded on Sep 22, froze at 2534; uploaded again on Sep 24, it reached only 2100.
3. Read lost games: the eager sellers, the sheep deadlock and the arbitrageurs were all found there.
4. Count flipped games on held-out worlds against the real field; self-play and tuning worlds mislead.
5. Only games between final submissions count: test against the final field, and make the second final submission a different agent.

## How we tested

- **Live-replay counterfactuals:** our live games re-run with the rival's recorded actions, the real seed and the real shop order. The engine reproduces server games exactly, but the rival cannot react to our changes, so market changes were also checked on reactive panels. Up to 1,572 deduplicated games.
- **Reactive panels:** 7, later 13, local opponents that react, including our emulations of eager sellers, arbitrageurs and trappers ([`research/panel/`](research/panel/)).
- **World panels:** local games with a forced shop order (a world is a seed with its sequence of shops), used to test gated patches in tomato and wool worlds.
- **Wins over money:** the final ranking counts only wins, so we counted flips (games whose winner changes) and usually dropped a change that flipped any game to a loss. Details and pitfalls: [docs/evaluation.md](docs/evaluation.md).

## What did not work

The main dead ends; the full list (68 entries) is in [docs/experiments.md](docs/experiments.md).

| Idea | Result |
|---|---|
| A scheduler written from scratch (about 60 variants) | 11.5k per game behind cha22 (local) |
| Behaviour cloning of DSM (final #3) | 0.88 action accuracy, 0 wins in local play |
| Broader production changes on cha22's recorded routes (more tomatoes or strawberries, carrot and animal swaps) | negative or flat; only four narrowly gated patches survived (the n-th hire of a day costs Fibonacci(n); land costs up to 4000) |
| Selling in the evening, as some strong teams did | -868 per game on 636 replays |
| TICK switched off; TICK's sell forced into slot 0 ahead of our milk sells | -616 and -717 per game on replay (112 and 116 flips lost) |
| A production agent from scratch (p6) | 7.9k per game behind v7c, our Sep 25 agent without TICK (local) |

## Repository layout

All 34 packages are byte-identical to what we uploaded or packaged (including two rejected candidates); every dropped idea is in [docs/experiments.md](docs/experiments.md).

```text
submissions/   all 34 packages: main.py, LICENSE.txt, NOTICE.txt, submission.tar.gz (index: submissions/README.md)
tools/         layer builders (build_submission, build_v5, add_fade, build_v8x, patch_base, ...)
               and evaluation tools (fastarena, rr, ab, cfreplay, screen, official_check, kg)
gold/          TICK, selling layers, replay counterfactuals, arenas, the trap guard and v12 packaging
research/      emulated opponents (panel/emu_*), the V10_CarreraGT line (carrera/), v12_17 to v12_19
               (live_0929/, live_0930/, rescue_0930/), audits
prod/          from-scratch production agents p1 to p6 and their tools
engine/, bc/   another scheduler line; behaviour-cloning experiments
results/       dated experiment reports, mostly in Chinese (index: results/README.md)
docs/          the write-up; docs/figures/ rebuilds every figure from docs/figures/data/
```

Not included: raw replays and episode data (`data/`), third-party public agents as stand-alone files, Frank Yang's planner source, and credentials. Scripts that read replays need that data and point to local paths.

## Setup and usage

Python 3.12; the agents themselves use only the standard library. Almost everything ran on CPUs (`tools/fastarena.py` plays about 3 games a second on 14 processes); only `bc/` used a GPU. On Windows, enable long paths or use `uv pip install`: plain pip can hit the 260-character path limit inside a dependency's test data.

```bash
pip install -r requirements.txt
```

Smoke-test a package the way Kaggle does (official `env.run` self-play, 720 steps):

```bash
python tools/official_check.py submissions/v12_19_own_cha22_adaptive_inputs/main.py
```

Play one game between two packages (about 10 seconds including the import):

```python
from kaggle_environments import make

env = make("kaggriculture", configuration={"seed": 7})
env.run(["submissions/v12_19_own_cha22_adaptive_inputs/main.py",
         "submissions/v8_own_cha22_tick_guard10/main.py"])
print([s.reward for s in env.steps[-1]])  # final money of each side
```

Importing `kaggle_environments` prints harmless OpenSpiel warnings; for batches use `tools/fastarena.py`, which loads only this environment. Packages are built with `tools/build_submission.py` and the layer scripts listed in [docs/solution.md](docs/solution.md).

Rebuild the figures with `python docs/figures/build.py` (needs Chrome; see [docs/figures/README.md](docs/figures/README.md)). Live-replay counterfactuals (`tools/cfreplay.py`, `research/carrera/ab_replay.py`) need replays downloaded with `tools/kg.py` and your own Kaggle API token.

## Documentation

| Page | Content |
|---|---|
| [docs/solution.md](docs/solution.md) | engine mechanics, the base agent, every layer with evidence |
| [docs/evaluation.md](docs/evaluation.md) | tools, emulated opponents, gates, measuring pitfalls |
| [docs/history.md](docs/history.md) | all 39 uploads and the last four decisions |
| [docs/experiments.md](docs/experiments.md) | everything that did not work, with numbers |
| [docs/postmortem.md](docs/postmortem.md) | standing over time, the gap to the top, lessons |
| [docs/changelog_0927_1016.md](docs/changelog_0927_1016.md) | Sep 27 to Oct 16, version by version |
| [submissions/README.md](submissions/README.md) | package index with Kaggle ids and SHA-256 |
| [results/README.md](results/README.md) | index of the dated experiment reports |
| [docs/figures/README.md](docs/figures/README.md) | how the figures are built and checked |

## Acknowledgements

- The base agent [cha22](https://www.kaggle.com/code/abhinav0370/cha22-agent) by Abhinav0370 and the public route-replay lineage it builds on: thomastschinkel, yhay81, destbreso, aurax7, tetsutani, prvsiyan, Dmitrii Gluzdov, Ahmed Berat Ozer and others.
- The tick arbitrage idea came from public replays of Otter Vibe.
- Public analyses we learned from: georgymamarin, destbreso, ashok205, raykkretzschmar, goodpjw2008, haideptry, leoprovorov, evgendvorkin.

## License

Our code and text are under the Apache License 2.0 ([LICENSE](LICENSE), [NOTICE](NOTICE)). Every package in `submissions/` embeds its base source with all upstream license text and attribution notices and carries its own `LICENSE.txt` and `NOTICE.txt`. Third-party code in this repository, and the fonts used in the figures, are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
