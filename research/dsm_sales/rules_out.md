
### WHEAT: 46213 decision points, DSM sold on 17.0% of them

| rule | exact | sell/hold | exact on sell turns | corr turn | corr 4-step window | corr day | volume | params (fold A / fold B) |
|---|---|---|---|---|---|---|---|---|
| hold (q=0) | 83.0% | 83.0% | 0.0% | nan | nan | nan | 0.00 |  /  |
| sell all now | 5.8% | 17.0% | 34.3% | 0.41 | 0.43 | 0.32 | 8.22 |  /  |
| hour gate, sell all | 84.1% | 84.6% | 11.8% | 0.20 | 0.18 | 0.18 | 0.21 | gate=[22] / gate=[22] |
| hour gate, fixed lot L | 84.2% | 84.6% | 12.6% | 0.22 | 0.19 | 0.21 | 0.18 | gate=[22], L=13 / gate=[22], L=13 |
| hour gate, median lot per hour | 83.3% | 84.6% | 6.8% | 0.20 | 0.14 | 0.15 | 0.11 | gate=[22] / gate=[22] |
| hour gate, ceil(f*S) | 84.1% | 84.6% | 11.7% | 0.20 | 0.18 | 0.18 | 0.20 | gate=[22], f=0.95 / gate=[22], f=0.95 |
| hour gate, pacing S/(slots left+k) | 84.2% | 84.6% | 12.6% | 0.22 | 0.19 | 0.21 | 0.18 | gate=[22], k=0, Lmax=13 / gate=[22], k=0, Lmax=13 |
| demand: last tick's consumption at m4=1 | 63.1% | 65.5% | 4.5% | 0.07 | 0.42 | 0.49 | 0.70 |  /  |
| demand/2 at m4=1 | 62.9% | 65.5% | 3.4% | 0.05 | 0.37 | 0.47 | 0.44 |  /  |
| restore inventory after own last sale | 24.2% | 31.4% | 21.8% | 0.05 | -0.04 | -0.05 | 3.99 |  /  |
| price >= a*base (every turn) | 82.9% | 82.9% | 0.0% | 0.03 | 0.04 | 0.08 | 0.01 | alpha=1.9 / alpha=2.0 |
| hour gate + price >= a*base | 83.0% | 83.0% | 0.0% | 0.03 | 0.05 | 0.08 | 0.00 | gate=[0, 1, 2, 22, 23], alpha=1.9 / gate=[0, 1, 2, 22, 23], alpha=1.95 |
| price >= (1-d)*max price 24 steps | 34.9% | 40.6% | 14.8% | 0.06 | -0.01 | -0.09 | 3.17 | d=0.0 / d=0.0 |
| price >= own last sale price - D | 77.5% | 77.9% | 0.1% | -0.03 | -0.06 | -0.16 | 0.68 | D=-4 / D=-4 |
| hour gate + impact cap: price >= p0 - D | 84.1% | 84.6% | 11.8% | 0.20 | 0.18 | 0.17 | 0.20 | gate=[22], D=1 / gate=[22], D=2 |

### CARROT: 13220 decision points, DSM sold on 14.9% of them

| rule | exact | sell/hold | exact on sell turns | corr turn | corr 4-step window | corr day | volume | params (fold A / fold B) |
|---|---|---|---|---|---|---|---|---|
| hold (q=0) | 85.1% | 85.1% | 0.0% | nan | nan | nan | 0.00 |  /  |
| sell all now | 9.2% | 14.9% | 61.5% | 0.35 | 0.23 | 0.17 | 7.00 |  /  |
| hour gate, sell all | 87.9% | 88.9% | 25.1% | 0.37 | 0.30 | 0.06 | 0.30 | gate=[22, 23] / gate=[22, 23] |
| hour gate, fixed lot L | 88.2% | 88.9% | 27.4% | 0.37 | 0.30 | 0.04 | 0.28 | gate=[22, 23], L=13 / gate=[22, 23], L=13 |
| hour gate, median lot per hour | 86.1% | 88.9% | 13.5% | 0.32 | 0.26 | -0.01 | 0.19 | gate=[22, 23] / gate=[22, 23] |
| hour gate, ceil(f*S) | 87.9% | 88.9% | 25.0% | 0.37 | 0.30 | 0.06 | 0.30 | gate=[22, 23], f=0.95 / gate=[22, 23], f=0.95 |
| hour gate, pacing S/(slots left+k) | 86.1% | 88.9% | 12.9% | 0.36 | 0.28 | 0.04 | 0.19 | gate=[22, 23], k=0, Lmax=13 / gate=[22, 23], k=0, Lmax=13 |
| demand: last tick's consumption at m4=1 | 62.2% | 64.2% | 1.8% | -0.01 | 0.19 | 0.11 | 0.67 |  /  |
| demand/2 at m4=1 | 62.0% | 64.2% | 0.4% | -0.02 | 0.14 | 0.10 | 0.41 |  /  |
| restore inventory after own last sale | 19.1% | 25.0% | 26.1% | 0.03 | -0.12 | -0.19 | 3.75 |  /  |
| price >= a*base (every turn) | 85.1% | 85.1% | 0.2% | 0.09 | 0.09 | 0.09 | 0.01 | alpha=2.0 / alpha=1.95 |
| hour gate + price >= a*base | 87.9% | 88.9% | 25.1% | 0.37 | 0.30 | 0.06 | 0.30 | gate=[22, 23], alpha=0.05 / gate=[22, 23], alpha=0.05 |
| price >= (1-d)*max price 24 steps | 42.8% | 46.3% | 12.4% | -0.05 | -0.19 | -0.38 | 1.85 | d=0.0 / d=0.0 |
| price >= own last sale price - D | 75.6% | 75.8% | 3.8% | -0.05 | -0.10 | -0.15 | 0.50 | D=-4 / D=-4 |
| hour gate + impact cap: price >= p0 - D | 87.9% | 88.9% | 25.0% | 0.37 | 0.30 | 0.06 | 0.30 | gate=[22, 23], D=2 / gate=[22, 23], D=3 |

### TOMATO: 22905 decision points, DSM sold on 9.2% of them

| rule | exact | sell/hold | exact on sell turns | corr turn | corr 4-step window | corr day | volume | params (fold A / fold B) |
|---|---|---|---|---|---|---|---|---|
| hold (q=0) | 90.8% | 90.8% | 0.0% | nan | nan | nan | 0.00 |  /  |
| sell all now | 5.3% | 9.2% | 57.8% | 0.16 | 0.10 | 0.67 | 14.15 |  /  |
| hour gate, sell all | 94.4% | 95.5% | 41.0% | 0.62 | 0.62 | 0.39 | 0.51 | gate=[22, 23] / gate=[22, 23] |
| hour gate, fixed lot L | 94.6% | 95.5% | 44.0% | 0.62 | 0.62 | 0.37 | 0.47 | gate=[22, 23], L=13 / gate=[22, 23], L=13 |
| hour gate, median lot per hour | 93.2% | 95.5% | 28.7% | 0.57 | 0.55 | 0.26 | 0.32 | gate=[22, 23] / gate=[22, 23] |
| hour gate, ceil(f*S) | 94.3% | 95.5% | 40.8% | 0.62 | 0.62 | 0.39 | 0.51 | gate=[22, 23], f=0.95 / gate=[22, 23], f=0.95 |
| hour gate, pacing S/(slots left+k) | 92.0% | 95.5% | 15.8% | 0.62 | 0.62 | 0.39 | 0.29 | gate=[22, 23], k=0, Lmax=13 / gate=[22, 23], k=0, Lmax=13 |
| demand: last tick's consumption at m4=1 | 66.2% | 66.6% | 0.4% | -0.10 | 0.08 | 0.38 | 0.90 |  /  |
| demand/2 at m4=1 | 66.2% | 66.6% | 0.3% | -0.10 | 0.06 | 0.33 | 0.58 |  /  |
| restore inventory after own last sale | 16.2% | 20.0% | 26.4% | 0.07 | 0.04 | 0.28 | 7.10 |  /  |
| price >= a*base (every turn) | 90.7% | 90.8% | 0.0% | 0.02 | 0.02 | 0.05 | 0.01 | alpha=2.0 / alpha=2.0 |
| hour gate + price >= a*base | 94.4% | 95.5% | 41.0% | 0.62 | 0.62 | 0.39 | 0.51 | gate=[22, 23], alpha=0.05 / gate=[22, 23], alpha=0.05 |
| price >= (1-d)*max price 24 steps | 51.1% | 53.8% | 9.1% | -0.00 | -0.09 | -0.34 | 2.36 | d=0.0 / d=0.0 |
| price >= own last sale price - D | 79.9% | 80.3% | 4.2% | 0.01 | -0.01 | -0.10 | 1.02 | D=-4 / D=-4 |
| hour gate + impact cap: price >= p0 - D | 94.3% | 95.5% | 40.8% | 0.62 | 0.62 | 0.39 | 0.51 | gate=[22, 23], D=15 / gate=[22, 23], D=8 |

### STRAWBERRY: 26337 decision points, DSM sold on 25.8% of them

| rule | exact | sell/hold | exact on sell turns | corr turn | corr 4-step window | corr day | volume | params (fold A / fold B) |
|---|---|---|---|---|---|---|---|---|
| hold (q=0) | 74.2% | 74.2% | 0.0% | nan | nan | nan | 0.00 |  /  |
| sell all now | 6.2% | 25.8% | 24.2% | 0.09 | -0.11 | -0.21 | 11.24 |  /  |
| hour gate, sell all | 69.9% | 81.8% | 8.2% | 0.19 | -0.14 | -0.25 | 2.25 | gate=[5, 9, 13, 17, 21] / gate=[5, 9, 13, 17, 21] |
| hour gate, fixed lot L | 76.4% | 81.8% | 33.4% | 0.22 | -0.27 | -0.43 | 0.53 | gate=[5, 9, 13, 17, 21], L=2 / gate=[5, 9, 13, 17, 21], L=2 |
| hour gate, median lot per hour | 76.4% | 81.8% | 33.4% | 0.22 | -0.27 | -0.43 | 0.53 | gate=[5, 9, 13, 17, 21] / gate=[5, 9, 13, 17, 21] |
| hour gate, ceil(f*S) | 75.1% | 81.8% | 28.3% | 0.20 | -0.18 | -0.30 | 0.48 | gate=[5, 9, 13, 17, 21], f=0.15 / gate=[5, 9, 13, 17, 21], f=0.15 |
| hour gate, pacing S/(slots left+k) | 77.0% | 81.8% | 35.7% | 0.23 | -0.23 | -0.40 | 0.47 | gate=[5, 9, 13, 17, 21], k=1, Lmax=2 / gate=[5, 9, 13, 17, 21], k=0, Lmax=2 |
| demand: last tick's consumption at m4=1 | 68.1% | 80.3% | 14.4% | 0.28 | 0.08 | -0.08 | 1.08 |  /  |
| demand/2 at m4=1 | 71.8% | 80.3% | 28.7% | 0.27 | 0.08 | -0.07 | 0.65 |  /  |
| restore inventory after own last sale | 47.2% | 60.6% | 14.7% | 0.08 | -0.16 | -0.24 | 3.20 |  /  |
| price >= a*base (every turn) | 74.2% | 74.2% | 0.0% | 0.02 | 0.02 | 0.03 | 0.01 | alpha=2.0 / alpha=2.0 |
| hour gate + price >= a*base | 74.2% | 74.3% | 0.0% | 0.02 | 0.02 | 0.04 | 0.00 | gate=[0, 1, 5, 9, 13, 14, 17, 21], alpha=2.0 / gate=[0, 1, 5, 9, 13, 14, 17, 18, 21], alpha=2.0 |
| price >= (1-d)*max price 24 steps | 60.4% | 64.0% | 4.6% | -0.03 | -0.21 | -0.34 | 0.36 | d=0.0 / d=0.0 |
| price >= own last sale price - D | 57.9% | 63.6% | 9.9% | -0.03 | -0.18 | -0.25 | 1.75 | D=-4 / D=-4 |
| hour gate + impact cap: price >= p0 - D | 74.7% | 81.8% | 26.6% | 0.21 | -0.13 | -0.23 | 0.80 | gate=[5, 9, 13, 17, 21], D=2 / gate=[5, 9, 13, 17, 21], D=2 |

### MELON: 843 decision points, DSM sold on 97.5% of them

| rule | exact | sell/hold | exact on sell turns | corr turn | corr 4-step window | corr day | volume | params (fold A / fold B) |
|---|---|---|---|---|---|---|---|---|
| hold (q=0) | 2.5% | 2.5% | 0.0% | nan | nan | nan | 0.00 |  /  |
| sell all now | 96.1% | 97.5% | 98.5% | 0.83 | 0.94 | 0.98 | 1.04 |  /  |
| hour gate, sell all | 96.0% | 97.4% | 98.4% | 0.82 | 0.95 | 0.99 | 1.04 | gate=[0, 1, 2, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17] / gate=[0, 1, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17] |
| hour gate, fixed lot L | 96.0% | 97.4% | 98.4% | 0.84 | 0.95 | 0.99 | 1.04 | gate=[0, 1, 2, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17], L=12 / gate=[0, 1, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17], L=12 |
| hour gate, median lot per hour | 97.4% | 97.4% | 99.9% | 0.89 | 0.96 | 0.99 | 1.02 | gate=[0, 1, 2, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17] / gate=[0, 1, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17] |
| hour gate, ceil(f*S) | 96.0% | 97.4% | 98.4% | 0.82 | 0.95 | 0.99 | 1.04 | gate=[0, 1, 2, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17], f=0.95 / gate=[0, 1, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17], f=0.95 |
| hour gate, pacing S/(slots left+k) | 0.2% | 97.4% | 0.2% | 0.19 | 0.50 | 0.96 | 0.23 | gate=[0, 1, 2, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17], k=0, Lmax=6 / gate=[0, 1, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17], k=0, Lmax=6 |
| demand: last tick's consumption at m4=1 | 2.5% | 3.1% | 0.0% | -0.02 | -0.01 | -0.03 | 0.00 |  /  |
| demand/2 at m4=1 | 2.5% | 3.1% | 0.0% | -0.02 | -0.01 | -0.03 | 0.00 |  /  |
| restore inventory after own last sale | 13.4% | 16.0% | 11.2% | 0.90 | 0.78 | 0.92 | 0.21 |  /  |
| price >= a*base (every turn) | 96.1% | 97.5% | 98.5% | 0.83 | 0.94 | 0.98 | 1.04 | alpha=0.05 / alpha=0.05 |
| hour gate + price >= a*base | 96.0% | 97.4% | 98.4% | 0.82 | 0.95 | 0.99 | 1.04 | gate=[0, 1, 2, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17], alpha=0.05 / gate=[0, 1, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17], alpha=0.05 |
| price >= (1-d)*max price 24 steps | 67.9% | 75.3% | 69.1% | 0.59 | 0.81 | 0.90 | 0.81 | d=0.3 / d=0.3 |
| price >= own last sale price - D | 85.3% | 91.3% | 87.5% | 0.69 | 0.91 | 0.97 | 0.97 | D=20 / D=20 |
| hour gate + impact cap: price >= p0 - D | 96.0% | 97.4% | 98.4% | 0.84 | 0.95 | 0.99 | 1.04 | gate=[0, 1, 2, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17], D=25 / gate=[0, 1, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17], D=25 |

### EGG: 33385 decision points, DSM sold on 7.9% of them

| rule | exact | sell/hold | exact on sell turns | corr turn | corr 4-step window | corr day | volume | params (fold A / fold B) |
|---|---|---|---|---|---|---|---|---|
| hold (q=0) | 92.1% | 92.1% | 0.0% | nan | nan | nan | 0.00 |  /  |
| sell all now | 4.8% | 7.9% | 60.1% | 0.18 | 0.16 | 0.58 | 15.38 |  /  |
| hour gate, sell all | 95.5% | 96.8% | 48.9% | 0.76 | 0.72 | 0.37 | 0.71 | gate=[22, 23] / gate=[22, 23] |
| hour gate, fixed lot L | 95.5% | 96.8% | 48.3% | 0.72 | 0.67 | 0.21 | 0.59 | gate=[22, 23], L=10 / gate=[22, 23], L=10 |
| hour gate, median lot per hour | 94.2% | 96.8% | 32.8% | 0.71 | 0.67 | 0.15 | 0.50 | gate=[22, 23] / gate=[22, 23] |
| hour gate, ceil(f*S) | 95.4% | 96.8% | 47.9% | 0.76 | 0.72 | 0.37 | 0.71 | gate=[22, 23], f=0.95 / gate=[22, 23], f=0.95 |
| hour gate, pacing S/(slots left+k) | 92.9% | 96.8% | 16.2% | 0.73 | 0.68 | 0.32 | 0.41 | gate=[22, 23], k=0, Lmax=100 / gate=[22, 23], k=0, Lmax=100 |
| demand: last tick's consumption at m4=1 | 70.9% | 71.4% | 0.3% | -0.04 | 0.14 | 0.35 | 0.76 |  /  |
| demand/2 at m4=1 | 70.9% | 71.4% | 0.1% | -0.06 | 0.12 | 0.31 | 0.49 |  /  |
| restore inventory after own last sale | 24.2% | 27.7% | 20.9% | 0.09 | 0.05 | 0.00 | 5.71 |  /  |
| price >= a*base (every turn) | 91.9% | 91.9% | 0.2% | -0.01 | -0.01 | -0.04 | 0.02 | alpha=1.25 / alpha=1.35 |
| hour gate + price >= a*base | 95.5% | 96.8% | 48.9% | 0.76 | 0.72 | 0.37 | 0.71 | gate=[22, 23], alpha=0.05 / gate=[22, 23], alpha=0.05 |
| price >= (1-d)*max price 24 steps | 38.3% | 41.1% | 26.8% | 0.08 | 0.05 | 0.18 | 6.86 | d=0.0 / d=0.0 |
| price >= own last sale price - D | 85.6% | 85.7% | 1.8% | -0.01 | -0.04 | -0.18 | 0.86 | D=-4 / D=-4 |
| hour gate + impact cap: price >= p0 - D | 95.5% | 96.8% | 48.9% | 0.76 | 0.72 | 0.37 | 0.71 | gate=[22, 23], D=5 / gate=[22, 23], D=5 |

### MILK: 30554 decision points, DSM sold on 18.0% of them

| rule | exact | sell/hold | exact on sell turns | corr turn | corr 4-step window | corr day | volume | params (fold A / fold B) |
|---|---|---|---|---|---|---|---|---|
| hold (q=0) | 82.0% | 82.0% | 0.0% | nan | nan | nan | 0.00 |  /  |
| sell all now | 7.9% | 18.0% | 43.8% | 0.16 | -0.06 | 0.01 | 9.08 |  /  |
| hour gate, sell all | 82.8% | 86.6% | 13.8% | 0.29 | 0.12 | -0.08 | 0.60 | gate=[17, 21] / gate=[17, 21] |
| hour gate, fixed lot L | 84.0% | 86.6% | 20.5% | 0.27 | 0.05 | -0.17 | 0.24 | gate=[17, 21], L=2 / gate=[17, 21], L=2 |
| hour gate, median lot per hour | 84.0% | 86.6% | 20.5% | 0.27 | 0.05 | -0.17 | 0.24 | gate=[17, 21] / gate=[17, 21] |
| hour gate, ceil(f*S) | 82.8% | 86.6% | 13.6% | 0.25 | 0.09 | -0.10 | 0.39 | gate=[17, 21], f=0.9 / gate=[17, 21], f=0.2 |
| hour gate, pacing S/(slots left+k) | 84.2% | 86.6% | 21.4% | 0.27 | 0.05 | -0.17 | 0.24 | gate=[17, 21], k=0, Lmax=2 / gate=[17, 21], k=0, Lmax=2 |
| demand: last tick's consumption at m4=1 | 73.7% | 82.9% | 24.8% | 0.42 | 0.15 | 0.23 | 1.12 |  /  |
| demand/2 at m4=1 | 74.2% | 82.9% | 27.7% | 0.40 | 0.12 | 0.21 | 0.71 |  /  |
| restore inventory after own last sale | 45.3% | 53.9% | 27.5% | 0.17 | -0.18 | -0.22 | 3.38 |  /  |
| price >= a*base (every turn) | 82.0% | 82.0% | 0.0% | 0.02 | 0.01 | 0.01 | 0.00 | alpha=1.65 / alpha=1.65 |
| hour gate + price >= a*base | 82.0% | 82.0% | 0.0% | 0.02 | 0.01 | 0.01 | 0.00 | gate=[1, 9, 13, 17, 21], alpha=1.65 / gate=[1, 9, 13, 17, 21], alpha=1.65 |
| price >= (1-d)*max price 24 steps | 65.6% | 69.1% | 4.8% | 0.02 | -0.20 | -0.38 | 0.41 | d=0.0 / d=0.0 |
| price >= own last sale price - D | 56.5% | 62.2% | 15.9% | 0.09 | -0.16 | -0.26 | 2.09 | D=-4 / D=-4 |
| hour gate + impact cap: price >= p0 - D | 83.8% | 86.6% | 19.2% | 0.22 | 0.03 | -0.22 | 0.31 | gate=[17, 21], D=3 / gate=[17, 21], D=3 |

### WOOL: 21713 decision points, DSM sold on 23.9% of them

| rule | exact | sell/hold | exact on sell turns | corr turn | corr 4-step window | corr day | volume | params (fold A / fold B) |
|---|---|---|---|---|---|---|---|---|
| hold (q=0) | 76.1% | 76.1% | 0.0% | nan | nan | nan | 0.00 |  /  |
| sell all now | 8.2% | 23.9% | 34.3% | 0.20 | 0.04 | 0.07 | 8.09 |  /  |
| hour gate, sell all | 70.1% | 82.9% | 14.6% | 0.33 | 0.05 | 0.06 | 2.17 | gate=[1, 5, 9, 13, 17, 21] / gate=[1, 5, 9, 13, 17, 21] |
| hour gate, fixed lot L | 75.9% | 82.9% | 38.9% | 0.26 | -0.38 | -0.31 | 0.42 | gate=[1, 5, 9, 13, 17, 21], L=1 / gate=[1, 5, 9, 13, 17, 21], L=1 |
| hour gate, median lot per hour | 77.0% | 82.9% | 43.4% | 0.26 | -0.25 | -0.30 | 0.47 | gate=[1, 5, 9, 13, 17, 21] / gate=[1, 5, 9, 13, 17, 21] |
| hour gate, ceil(f*S) | 76.4% | 82.9% | 40.8% | 0.29 | -0.19 | -0.18 | 0.46 | gate=[1, 5, 9, 13, 17, 21], f=0.1 / gate=[1, 5, 9, 13, 17, 21], f=0.1 |
| hour gate, pacing S/(slots left+k) | 76.9% | 82.9% | 42.9% | 0.30 | -0.16 | -0.14 | 0.54 | gate=[1, 5, 9, 13, 17, 21], k=3, Lmax=2 / gate=[1, 5, 9, 13, 17, 21], k=2, Lmax=2 |
| demand: last tick's consumption at m4=1 | 76.9% | 87.9% | 19.4% | 0.36 | 0.11 | 0.21 | 0.84 |  /  |
| demand/2 at m4=1 | 81.8% | 87.9% | 40.0% | 0.35 | 0.10 | 0.20 | 0.49 |  /  |
| restore inventory after own last sale | 64.4% | 75.7% | 22.1% | 0.28 | 0.03 | 0.05 | 1.84 |  /  |
| price >= a*base (every turn) | 75.6% | 75.8% | 0.1% | 0.03 | 0.04 | 0.07 | 0.09 | alpha=1.2 / alpha=1.25 |
| hour gate + price >= a*base | 76.4% | 84.9% | 15.8% | 0.38 | 0.24 | 0.27 | 1.28 | gate=[1, 5, 9, 13, 17, 21], alpha=0.2 / gate=[1, 5, 9, 13, 17, 21], alpha=0.2 |
| price >= (1-d)*max price 24 steps | 63.8% | 67.6% | 12.8% | 0.10 | -0.05 | -0.09 | 0.49 | d=0.0 / d=0.0 |
| price >= own last sale price - D | 72.8% | 77.6% | 24.0% | 0.17 | -0.04 | -0.07 | 0.91 | D=-4 / D=-4 |
| hour gate + impact cap: price >= p0 - D | 75.8% | 82.9% | 38.5% | 0.27 | 0.05 | -0.01 | 0.61 | gate=[1, 5, 9, 13, 17, 21], D=0 / gate=[1, 5, 9, 13, 17, 21], D=1 |

### FERTILIZER: 17935 decision points, DSM sold on 37.7% of them

| rule | exact | sell/hold | exact on sell turns | corr turn | corr 4-step window | corr day | volume | params (fold A / fold B) |
|---|---|---|---|---|---|---|---|---|
| hold (q=0) | 62.3% | 62.3% | 0.0% | nan | nan | nan | 0.00 |  /  |
| sell all now | 29.5% | 37.7% | 78.0% | 0.52 | 0.23 | 0.11 | 3.05 |  /  |
| hour gate, sell all | 67.0% | 69.9% | 45.5% | 0.73 | 0.61 | 0.37 | 1.25 | gate=[0, 2, 3, 7, 22, 23] / gate=[0, 2, 3, 7, 22, 23] |
| hour gate, fixed lot L | 67.9% | 69.9% | 47.7% | 0.73 | 0.59 | 0.33 | 1.22 | gate=[0, 2, 3, 7, 22, 23], L=14 / gate=[0, 2, 3, 7, 22, 23], L=14 |
| hour gate, median lot per hour | 61.7% | 69.9% | 31.4% | 0.69 | 0.71 | 0.48 | 0.81 | gate=[0, 2, 3, 7, 22, 23] / gate=[0, 2, 3, 7, 22, 23] |
| hour gate, ceil(f*S) | 67.0% | 69.9% | 45.5% | 0.73 | 0.61 | 0.36 | 1.25 | gate=[0, 2, 3, 7, 22, 23], f=0.95 / gate=[0, 2, 3, 7, 22, 23], f=0.95 |
| hour gate, pacing S/(slots left+k) | 58.6% | 69.9% | 23.2% | 0.61 | 0.43 | 0.16 | 0.40 | gate=[0, 2, 3, 7, 22, 23], k=0, Lmax=3 / gate=[0, 2, 3, 7, 22, 23], k=0, Lmax=13 |
| demand: last tick's consumption at m4=1 | 62.3% | 62.3% | 0.0% | nan | nan | nan | 0.00 |  /  |
| demand/2 at m4=1 | 62.3% | 62.3% | 0.0% | nan | nan | nan | 0.00 |  /  |
| restore inventory after own last sale | 58.8% | 59.3% | 2.7% | 0.00 | -0.03 | 0.02 | 0.14 |  /  |
| price >= a*base (every turn) | 64.7% | 70.1% | 54.6% | 0.66 | 0.58 | 0.44 | 0.91 | alpha=0.45 / alpha=0.45 |
| hour gate + price >= a*base | 70.9% | 74.7% | 47.3% | 0.71 | 0.67 | 0.47 | 0.78 | gate=[0, 2, 3, 7, 9, 10, 11, 12, 18, 22, 23], alpha=0.4 / gate=[0, 2, 3, 7, 9, 10, 11, 12, 13, 16, 18, 22, 23], alpha=0.4 |
| price >= (1-d)*max price 24 steps | 57.3% | 58.4% | 6.8% | -0.03 | -0.06 | -0.00 | 0.27 | d=0.02 / d=0.0 |
| price >= own last sale price - D | 62.1% | 62.2% | 1.4% | -0.03 | -0.05 | -0.05 | 0.01 | D=-4 / D=-4 |
| hour gate + impact cap: price >= p0 - D | 67.0% | 69.9% | 45.5% | 0.73 | 0.61 | 0.36 | 1.24 | gate=[0, 2, 3, 7, 22, 23], D=3 / gate=[0, 2, 3, 7, 22, 23], D=3 |
