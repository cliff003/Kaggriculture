# 9/25 最新公开 notebook 本地对打（UTC 15:10 前后）

做法：`gold/tools/fetch_public.py` 下载 notebook 输出里作者实际提交的文件；输出里没有 agent 的，从 notebook 源码里的压缩串解码（2965 混合引擎：base64 + gzip；Ahmed V57：b85 + zlib，按它自带的 sha256 校验通过）。fieldcraft 的提交包里还有 mirror_plan.py，本地测试用 `full/agent_wrap.py` 把包目录加进 sys.path。每组 20 个世界（gold/arena/famworlds.json 前 20 个），座位交替。数字是新 agent 的胜-负（平均差）。

| notebook | 实盘分（Code 页） | 对 v7（b14_feed4） | 对 v6 | 对 v4 |
|---|---|---|---|---|
| haideptry/the-2965-master-hybrid-engine | 2214.9 | 1-19（-2728） | | |
| ahmedberatozer/kaggriculture-v57-funding-order-invariant | | 5-15（-2323） | 3-17（-1305） | 3-17（-1487） |
| ahmedberatozer/kaggriculture-v56-smarter-seeds-and-fertilizer | | 4-16（-2362） | | |
| arsgorynich/order-book-v3-response-improvement | 2419.6 | 4-16（-2448） | 4-16（-1368） | 2-18（-1614） |
| statma/kaggriculture-herd-safe-sale-window-race-ca25 | 2332.3 | 6-14（-2236） | 5-15（-1162） | 3-17（-1411） |
| hanifnoerrofiq/pioneers-of-kaggle-town（candidate-2 结果相同） | 2290.9 / 2129.9 | 5-15（-2348） | 5-15（-1234） | 5-15（-1231） |
| haideptry/the-shepherds-ledger-herd-safe-sovereign | 2088.5 | 5-15（-2365） | | |
| yasutakababa/kaggriculture-late-purchase-v16-submit | | 3-17（-2054） | | |
| hakdevelopment/kaggriculture-2887-score-fieldcraft-agent | 不在前 212 | 2-18（-3917） | | |
| nihilisticneuralnet/kaggriculture-population-robust-economy | 1731.1 | 0-20（-3181） | | |
| yangkuangou/kaggriculture-agent-lab-copy-replay-compare | | 入门教程，只有种小麦的小例子，没测 | | |

结论：没有一个能打过我们在跑的任何一个版本（v4、v6、v7）。标题里的 2965、2887 不是它们的实盘分。除 fieldcraft 和 population-robust-economy 外，都是 cha22 同族衍生（Metav4、Pipe、订单簿估值等卖货层）。

注意：本地对打主要比的是卖货时机，v6 在本地大胜 v4，实盘却暂时落后，所以这些数字只说明"它们不比我们强"，不说明能赢多少分。
