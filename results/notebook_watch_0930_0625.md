# 9/30 06:25 UTC：新公开 notebook 与连败复盘

本轮仅查询、下载公开 notebook 并做本地固定录像重放；没有上传 Kaggle 提交。

## 当前实盘

官方榜单 06:24:45 UTC：队伍 42 排名 314，2280.1；银牌线第 509 名、2126.3，仍领先 153.8 分和 195 个名次。V12_AventadorSVJ 截至 06:21 共 247 局，122 胜 125 负，当前分 2280.2；最近 10 局 3 胜 7 负、最近 30 局 10 胜 20 负。V10_CarreraGT 截至 06:24 共 290 局，126 胜 164 负，当前分 2206.8；最近 10 局 0 胜 10 负、最近 30 局 7 胜 23 负。榜单与提交分数可能因刷新时刻不同有 0.1 左右差别。

V12 最近 30 局有 10 场至少输 5000；其中 23 个对手的提交 ID 晚于 V12 的 56649860。ID 只能证明对手版本较晚，不能证明他们用了某个公开 notebook。9/30 06:09 的精确录像拆账见 `silver_risk_0930_0610.md`：V12 最新八局中的六场败局，对手相对我们每局多得的净现金主要在番茄约 3936、草莓约 3721、鸡蛋约 2922；我们则在牛奶约多 2170、雇工少花约 1503。类别净现金含买卖，不是纯销售额。显著败局表现为高价值产出和销售的总量差，而不是单笔交易失误。

## 公开 notebook 更新

Kaggle `kernels_list(competition='kaggriculture', sort_by='dateRun')` 的最近运行记录：

| Notebook | 最近运行 UTC | 本次发现 |
|---|---|---|
| [Harvest Ledger](https://www.kaggle.com/code/haodou092/kaggriculture-harvest-ledger) | 9/30 03:07 | 新 V91，原作者称放慢资产清算以分散 V90 的同质化风险；原文自报 12 个当前录像种子只赢 5 局、平均 +899，且两种子动态试验略负。新源码 SHA `fd39dffa`，与 9/27 本地旧版不同。 |
| [Multi-Route Farming Agent](https://www.kaggle.com/code/flexonafft/kaggriculture-multi-route-farming-agent) | 9/29 16:28 | 更新到 Step1010，主要是订单重排稳定性；作者自报 2 种子 4 平和另 1 种子 2 胜，样本很小。新源码 SHA `03165654`，与 9/27 本地旧版不同。 |
| [A Song of Ice and Fire](https://www.kaggle.com/code/leoprovorov/a-song-of-ice-and-fire-fixed-flexible) | 9/29 19:06 | 新的头部策略分叉分析与可复现 agent，显示不同店铺组合和局内状态会让领先路线明显分叉；分析价值高，但不是强度保证。 |
| [X-ray your agent](https://www.kaggle.com/code/destbreso/x-ray-your-agent) | 9/29 22:58 | 增强的对局诊断工具，能看分世界胜率、雇工和动作分叉；本轮现金拆账比其一般画像更直接。 |
| [Top-10 Replay Archive](https://www.kaggle.com/code/ashok205/top10-replay-dataset-archive) | 9/29 22:43 | 数据归档，非策略 agent；适合后续验证头部打法。 |
| [What 2600+ Farms Do Differently](https://www.kaggle.com/code/georgymamarin/kaggriculture-what-2600-farms-do-differently) | 9/29 22:13 | 定时数据分析，非可直接替换的 agent。 |

Kaggle 列表的 `lastRunTime` 是 notebook 运行时间，不代表首次发布时间，更不能据此认定对手使用它。

## 相同录像上的筛查

在相同的 9/30 最新 16 条实盘录像、相同种子和座位、固定对手动作、强制保持开店序列的本地重放中：V12 赢 3/16，V91 赢 0/16，Step1010 赢 4/16。Step1010 与 V12 相比翻赢 2 局、翻输 1 局，并靠一场 +39006 的局拉高均值；它在 Rogues 和 How to Make Bread 败局仍输。把 Step1010 扩到先前保存的 30 条 V12 实盘录像，V12 赢 12/30，Step1010 赢 7、输 22、平 1；虽有 +679 的平均钱差变化，但翻赢 3 局、翻输 8 局。这个结果不支持用 Step1010 替换现役 V12。V91 的 16 局结果也不支持替换。

固定对手动作不会响应我们改变生产与卖货，且 16/30 局样本小；这些结果只用于排除明显不稳的替换，不能预测 Kaggle 新提交分数。现有候选 v12_18 在先前最近 30 条录像完全不变，不能解决这一轮连败。应优先研发分世界的番茄、草莓、鸡蛋净收益和采收/雇工时序，但每项都需过历史、近期、动态对局三层验证。保持两个现役提交，不上传未经验证的新版本。
