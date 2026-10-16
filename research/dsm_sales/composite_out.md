| product | composite rule | exact | sell/hold | exact on sell turns | corr turn | corr 4-step window | corr day | volume |
|---|---|---|---|---|---|---|---|---|
| WHEAT | hour 22-23: sell all; hours 0/1/2: sell stock above a feed reserve of n_animals, 2/3 n, 1/3 n | 76.9% | 81.6% | 16.9% | 0.48 | 0.52 | 0.55 | 1.43 |
| CARROT | hour 22-23: sell all, else hold | 87.9% | 88.9% | 25.1% | 0.37 | 0.30 | 0.06 | 0.30 |
| CARROT | hour 22-23: sell all, else hold + hour 0: sell all when the shed holds >= 90 items | 85.5% | 87.3% | 25.3% | 0.41 | 0.52 | 0.40 | 0.71 |
| TOMATO | hour 22-23: sell all, else hold | 94.4% | 95.5% | 41.0% | 0.62 | 0.62 | 0.39 | 0.51 |
| TOMATO | hour 22-23: sell all, else hold + hour 0: sell all when the shed holds >= 90 items | 92.6% | 94.3% | 42.6% | 0.54 | 0.54 | 0.61 | 1.03 |
| STRAWBERRY | h0: min(S, 11 if p>=1.3 base else 6) when market inventory rose >=9 in 24 steps, p>=0.7 base, S>=9; m4==1 from h5: min(S,2); fresh drop at other hours: min(fresh,6) | 77.5% | 83.4% | 41.5% | 0.59 | 0.56 | 0.55 | 0.82 |
| MELON | sell everything as soon as it is in the shed | 96.1% | 97.5% | 98.5% | 0.83 | 0.94 | 0.98 | 1.04 |
| EGG | hour 22-23: sell all, else hold | 95.5% | 96.8% | 48.9% | 0.76 | 0.72 | 0.37 | 0.71 |
| EGG | hour 22-23: sell all, else hold + hour 0: sell all when the shed holds >= 90 items | 93.2% | 94.5% | 49.0% | 0.57 | 0.69 | 0.61 | 1.11 |
| MILK | m4==1 at h9/13/17/21: min(S,2); a fresh drop is sold in full; nothing below 0.24 base | 80.8% | 84.8% | 38.1% | 0.45 | 0.58 | 0.73 | 0.93 |
| WOOL | m4==1: min(S, ceil(last tick consumption / 2)); a fresh drop is sold in full | 84.7% | 91.5% | 58.1% | 0.73 | 0.80 | 0.88 | 1.06 |
| FERTILIZER | hours 0,2,3,7,22,23: sell all while price >= 0.4 base | 69.4% | 70.7% | 29.0% | 0.72 | 0.70 | 0.57 | 0.55 |

Stability check: the same composite rules scored separately on even- and odd-indexed games

| product | exact even / odd | sell/hold even / odd | corr turn even / odd | corr day even / odd |
|---|---|---|---|---|
| WHEAT | 77.1% / 76.6% | 82.0% / 81.3% | 0.48 / 0.47 | 0.55 / 0.56 |
| CARROT | 87.6% / 88.1% | 88.7% / 89.1% | 0.36 / 0.38 | 0.06 / 0.05 |
| TOMATO | 94.3% / 94.4% | 95.5% / 95.5% | 0.64 / 0.61 | 0.43 / 0.34 |
| STRAWBERRY | 77.0% / 78.0% | 82.8% / 83.9% | 0.57 / 0.61 | 0.55 / 0.56 |
| MELON | 95.7% / 96.4% | 97.6% / 97.4% | 0.80 / 0.86 | 0.98 / 0.99 |
| EGG | 95.3% / 95.7% | 96.6% / 97.0% | 0.74 / 0.78 | 0.32 / 0.42 |
| MILK | 80.2% / 81.4% | 84.7% / 85.0% | 0.44 / 0.45 | 0.73 / 0.73 |
| WOOL | 85.4% / 84.1% | 92.2% / 90.9% | 0.74 / 0.72 | 0.88 / 0.88 |
| FERTILIZER | 70.6% / 68.1% | 71.9% / 69.4% | 0.74 / 0.71 | 0.61 / 0.54 |
