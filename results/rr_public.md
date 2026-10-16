# 公开底子测试（2026-09-24）

| 项目 | 内容 |
|---|---|
| 候选 | Code 页按分数排的前 30 个 notebook（9/24 20:53 UTC），按 main.py 的 sha256 去重后 21 份不同代码，放在 data/public/agents/ |
| 对手 | cha22 原版（submissions/v4_public_cha22_verbatim）和 cha22 加改动（submissions/v4_own_cha22_slot） |
| 局数 | 每个底子对每个对手 40 局：seed 9000 到 9019，两边座位各一次；共 1680 局，没有出错或超时的 |
| 引擎 | 本地 fastarena（kaggle-environments 1.32.7），原始数据 results/rr_public.jsonl |
| Code 页分 | notebook 当前版本挂着的提交的分数。老 notebook 的分是早先对手弱时打的，偏高 |

## 结论

- 21 个公开底子没有一个打得过 cha22：cha22 加改动对它们合计 826 胜 14 负（98.3%），原版 825 胜 15 负。
- 最接近的是 Herd Safe v3 Experimental（40 局赢 6 局）和 Moon Counts Melons（赢 4 到 5 局）；其余最多赢 2 局。
- 和 cha22 原版逐字节相同的（sha256 127ed3e6）：GURU 的 Master Engine V3、Igor Zharov 的 Multi-Route、tetsutani 的 demand-preserving。
- 没测的：Multi-Route 第 59 版（历史最高 2767.3，8/14 跑的）和 Master Engine V3 第 3 版（2712.8，9/9 跑的），别人 notebook 的历史版本拉不下来（403）。同一时期的 Ahmed V31 到 V41 对 cha22 全是 0 胜，不值得再找。
- MarketShock 用的是数据集里的 wr1 版本，notebook 要的 wr1k 版本（sha256 12ad317e）拿不到；数据集文件最后一个函数不是 agent，按 Kaggle 的加载规则会出错，本地测试时在末尾补了入口。

## 每个底子的成绩（胜/负/平从底子这边看）

| 名次 | 底子 | Code 页分 | 对 cha22 原版 胜/负/平 | 得分率 | 平均钱差 | 对 cha22 加改动 胜/负/平 | 得分率 | 平均钱差 |
|---|---|---|---|---|---|---|---|---|
| 1 | Arsgorynich Herd Safe v3 Experimental | 2513.3 | 6/34/0 | 15% | -935 | 6/34/0 | 15% | -966 |
| 2 | prvsiyan Frontier: Moon Counts Melons | 2473.2 | 5/35/0 | 12% | -879 | 4/36/0 | 10% | -895 |
| 3 | Ahmed V53 Opening Signature | 2597.5 | 2/38/0 | 5% | -1411 | 2/38/0 | 5% | -1443 |
| 4 | Ahmed V55 One-Turn Market Race Edge | 2595.8 | 2/38/0 | 5% | -1596 | 2/38/0 | 5% | -1641 |
| 5 | Ahmed V38 Smarter Feed | 2625.2 | 0/40/0 | 0% | -5850 | 0/40/0 | 0% | -5872 |
| 6 | Ahmed V39 Ready Before the Rush；同一份代码：GURU master-engine-v53e01d74d8f（2581.0） | 2621.2 | 0/40/0 | 0% | -5452 | 0/40/0 | 0% | -5474 |
| 7 | Ahmed v34 Observed Market Timing | 2601.6 | 0/40/0 | 0% | -8641 | 0/40/0 | 0% | -8658 |
| 8 | Ahmed V41 Review Candidate | 2586.4 | 0/40/0 | 0% | -5491 | 0/40/0 | 0% | -5513 |
| 9 | Kaggricult-Man 的 MarketShock（数据集版，补了入口） | 2579.4 | 0/40/0 | 0% | -2087 | 0/40/0 | 0% | -2126 |
| 10 | Ahmed v31 Production and Sale Priority | 2575.6 | 0/40/0 | 0% | -9216 | 0/40/0 | 0% | -9233 |
| 11 | Arsgorynich V43 Local Confirmed | 2550.5 | 0/40/0 | 0% | -4566 | 0/40/0 | 0% | -4602 |
| 12 | 177/180 Fresh Top-30 v21.1 | 2517.1 | 0/40/0 | 0% | -51949 | 0/40/0 | 0% | -51952 |
| 13 | aurax7 shop_router_reactive_v7 | 2510.0 | 0/40/0 | 0% | -4356 | 0/40/0 | 0% | -4397 |
| 14 | Nathan Pipe-5 Terminal Boost | 2500.5 | 0/40/0 | 0% | -4584 | 0/40/0 | 0% | -4620 |
| 15 | best market agent - high strategy | 2497.9 | 0/40/0 | 0% | -39204 | 0/40/0 | 0% | -39207 |
| 16 | Ahmed V45 First-Turn Wheat Round Trip；同一份代码：degnonguidi cloning agent（2493.2） | 2497.5 | 0/40/0 | 0% | -4328 | 0/40/0 | 0% | -4365 |
| 17 | web3cainiao v21 Tactical Memory | 2491.7 | 0/40/0 | 0% | -53257 | 0/40/0 | 0% | -53242 |
| 18 | Nathan Pipe-7 Wheat Microstructure | 2473.7 | 0/40/0 | 0% | -4328 | 0/40/0 | 0% | -4365 |
| 19 | Ahmed V49 Funded Sale Timing；同一份代码：GURU game-theoretic-master（2468.7） | 2467.0 | 0/40/0 | 0% | -2263 | 0/40/0 | 0% | -2293 |
| 20 | nusrati 2715.6 | 2459.8 | 0/40/0 | 0% | -11794 | 0/40/0 | 0% | -11811 |
| 21 | Ahmed V36 Guarded Four-Turn Sales | 2450.4 | 0/40/0 | 0% | -7798 | 0/40/0 | 0% | -7816 |

cha22 加改动对这 21 个底子合计 826/14/0，得分率 98.3%
cha22 原版对这 21 个底子合计 825/15/0，得分率 98.2%
