# Paired validation: rescue base (herdsafe_dmitrii, sha 4889137f) vs rescue + order-slot layer

Seeds 5000-5019, alternating seats, same opponents, local fast runner (engine kaggle-environments 1.32.7).

| Opponent | rescue base W/L/T | margin | rescue + slot W/L/T | margin |
|---|---|---|---|---|
| rescue copy | 0/0/20 | 0 | 20/0/0 | +61 |
| herdsafe_race | 3/5/12 | -11 | 16/4/0 | +49 |
| hybrid2965 | 16/4/0 | -27 | 19/1/0 | +34 |
| morewheat | 4/16/0 | -287 | 6/14/0 | -228 |
| v15stack | 10/10/0 | -280 | 10/10/0 | -232 |
| Overall points | 49.0% | | 71.0% | |

Per-seed flips (slot vs base, same seed and seat): ties -> wins 32, losses -> wins 6, wins -> losses 0.
Mean margin gain per game: rescue copy +61, herdsafe_race +61, hybrid2965 +61, morewheat +59, v15stack +48.

Official runner self-play (kaggle_environments env.run): DONE/DONE, 720 steps, 9.3 s wall.
