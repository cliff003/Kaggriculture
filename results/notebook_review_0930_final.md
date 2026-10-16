# 9/30 最后公开 notebook 更新核查

查询截至 **2026-10-01 01:44:27 UTC**。官方 Kaggle 最近运行列表复查了 100 篇，下载并阅读其中较新的源码、说明及选定构建输出。运行时间不等于首次发布时间，也不能证明代码或实力提高。本轮没有执行 notebook 单元，没有上传或改动现役提交；下载的 agent 经静态检查后，仅在本地重放中运行。

结论：**有值得借的诊断方法和状态分支思路，没有发现更稳的整包替换证据。** 小量延后卖货已单独移植到 v12_19 做初筛，没有获得额外胜场，暂不采用。交接资料规定的提交截止为 9/30 23:59 UTC，已经过去；本报告用于复盘和后续研发，不作为新提交建议。

## 最新版本读到了什么

下表时间均为 2026-09-30 UTC，来自官方最近运行记录。

| Notebook | 运行时间 | 实际核查与借鉴价值 |
|---|---|---|
| [Ice and Fire: Final Update](https://www.kaggle.com/code/leoprovorov/a-song-of-ice-and-fire-final-update) | 23:15 | 把固定路线、按商店选择的路线、局内状态反应分开。前两家店形成 64 个组合；同组合内仍出现分叉，才值得寻找现金、布局、工人载货等条件。只看获胜录像会有偏差，不能直接复制某一步的动作。最终源内 main 载荷与 15:31 下载版字节一致，SHA `020be9d5`；说明中的 MarketShock 新名称不能替代实际输出核查。 |
| [X-ray your agent](https://www.kaggle.com/code/destbreso/x-ray-your-agent) | 23:01 | 优先借它的商店组合 × 对手强度/家族诊断，以及大额卖出后双方同商品的价格低谷分析。数量 × 跌价只是损失规模的近似，不能直接算作对手造成的现金转移。雇工按工作、搬运、移动、空闲拆开，避免把所有走路都当浪费；评级按新增对局的变化与方向判断，不能只按小时涨跌。 |
| [What 2600+ Farms Do Differently](https://www.kaggle.com/code/georgymamarin/kaggriculture-what-2600-farms-do-differently) | 22:06 | 适合借生产规模、雇工、买地的画像，并检查数据覆盖。最佳一局并非平均表现，钱多也不等于胜率高。其排除“由终局现金计算的拐点日”很重要，这类指标会把结果泄漏成决策依据。 |
| [Anhad Autonomous Agent](https://www.kaggle.com/code/anhadmahajan06/kaggriculture-autonomous-ai-farming-agent) | 21:31 | 与 17:53 版逐行比较，仅第 91 步小麦禁售价格阈值由 31 降至 15，以及对应统计值变化。晚期种子限购与无效施肥跳过函数和我们底子完全一致，不能当成缺失的新能力。作者少量种子自报 100% 不能证明实战更强。 |
| [Farmer John and the Wheat Seller](https://www.kaggle.com/code/lynnsakurai/farmer-john-and-the-wheat-seller) | 17:19 | 新 GS2 只延后少量胡萝卜、番茄、草莓及动物产品，不动小麦和肥料；最多 8 个，结合已知商店消耗、价格增量、仓库余量和可见产能。比全面压货条件更窄，值得隔离验证；本轮移植结果不支持采用。 |
| [Multi-Route Farming Agent](https://www.kaggle.com/code/flexonafft/kaggriculture-multi-route-farming-agent) | 16:57 | 实际输出 SHA `919fc1d6`，与已保存的 V43 完全一致。早晨报告测过的 Step1010 是另一份代码，不能把其结果套到这次输出。 |
| [Harvest Ledger](https://www.kaggle.com/code/haodou092/kaggriculture-harvest-ledger) | 15:56 | 说明写 V94 空间镜像门控，但源内固定载荷及输出 SHA `531a423a`，均与 9/28 保存版一致。新说明和重新运行不构成新代码证据；作者面板数字也不是我们的验证。 |

另外，19:12 的 [Evgen Version 31](https://www.kaggle.com/code/evgendvorkin/kaggriculture-version-31-26-09-bronze-going-up) 的两项晚期修复也已在我们的底子中。18:10 的 [Beginner Friendly](https://www.kaggle.com/code/farhanabidtech786/kaggriculture-beginner-friendly) 输出与旧 Reyhan Market agent 字节相同。

[God's Mode](https://www.kaggle.com/code/leoprovorov/god-s-mode-hacked-stores) 的空地改变开店随机数研究可以解释为何本地 A/B 必须固定商店序列。但操纵开店还涉及隐藏种子推断与对手受益；作者给出的一个商店组合中，四场原本获胜的基线反而全部翻输。它目前是机制研究，不能据此采用线上开店控制。

## 同一批 20 场录像初筛

使用 9/30 研发期间已保存的 `research/rescue_0930/latest20.jsonl.gz`，**不是 10/1 新采实盘**。引擎 1.32.7，原座位、种子、完整开店序列相同，对手动作固定。全部运行完成且 agent 错误数为 0。所有变化均相对已上传的 **v12_19** 计算。

| 实际测试代码 | main SHA 前缀 | 胜场 / 20 | 翻赢 / 翻输 | 平均钱差变化 |
|---|---|---:|---:|---:|
| v12_19 | `3b6a7899` | 7 | 0 / 0 | 0 |
| V12_AventadorSVJ | `08a0d374` | 6 | 0 / 1 | -303 |
| Harvest Ledger 15:56 | `531a423a` | 7 | 2 / 2 | +6013 |
| Ice and Fire 最终载荷 | `020be9d5` | 7 | 2 / 2 | +6141 |
| Farmer John GS2 整包 | `2f6da44d` | 4 | 2 / 5 | +5360 |
| Multi-Route 实际 V43 | `919fc1d6` | 3 | 2 / 6 | +12286 |
| Anhad 21:31 | `85734f96` | 4 | 0 / 3 | -3384 |
| Anhad 17:53，历史对照 | `061e2e78` | 4 | 0 / 3 | -3359 |
| Evgen 19:12 | `150b3159` | 4 | 0 / 3 | -3359 |
| Beginner Friendly | `d39dba50` | 0 | 0 / 7 | -40664 |

Multi-Route 的大钱差增量和较低胜场再次说明，少数大胜可以拉高平均值，最终比赛仍按胜负计分。Harvest 和 Ice and Fire 各有两场原来的胜局变负，不能解释为无代价升级。

这 20 场也是 v12_19 研发期间看过的样本，**不是独立留出集**。固定对手不会响应新生产和卖货；这里只做排除明显不稳方案的初筛，不能预测提交分或证明我们全场优于这些公开 agent。

## GS2 单独移植的结果

只把 Farmer John 的小量延后卖货层加到冻结 v12_19，保留所有原有入口与其他层。原型在 `research/notebook_0930_2032/probes/shop_settlement_v1/main.py`，SHA `5fa11955`；构建脚本记录来源与 Apache-2.0 声明。没有改封存包。

| 比较 | 胜场 | 翻赢 / 翻输 | 平均钱差变化 | 决定 |
|---|---:|---:|---:|---|
| v12_19 加 GS2，相对 v12_19 | 7 → 7 | 0 / 0 | -46.70 | 不采用，不扩大测试，不打包 |

20 场动作/结果均有变化但没有多赢。等待商店消耗不保证净收益，尤其对手会在这段时间卖同种货；现有模块不值得直接叠加。

## 最值得沿用的研究顺序

1. **先定位败局集中在哪些组合。** 前两家商店 × 对手生产家族，逐格记录胜场、钱差与样本数；再将销量差与成交价差分开。不能拿全场平均掩盖某类对手，也不能把仅一两场的格子做成固定路线。
2. **再找第 6 到 10 天的投入条件。** 在同商店组合内，对比现金、可见农场布局、工人载货和既有生产规模，确认何时应追加鸡蛋、草莓或番茄能力。先补可见的执行缺口，追加劳动、饲料、运输、仓库代价都计入净现金。不能只按店数或固定步数加人加种。
3. **按对局评价最终两个版本。** 新版评级仍需看样本数、每场变化和对手家族；只看几小时的涨跌不足以判断新版本失效。最终两个已确认提交仍是 56649860 与 56713491，本轮没有改变它们。

可复核汇总在 `research/notebook_0930_2032/summary.json`，完整 SHA、逐项同代码核查和初筛结果均已记录。第三方 notebook、agent 与原始录像只保留本地，不导出到 GitHub。
