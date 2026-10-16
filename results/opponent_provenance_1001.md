# 对手是否未经实盘验证，代码从哪里来

核查日期：纽约 2026-10-01 07:10–07:23。公开对局和已公开源码只读核查，没有获取对手私有代码、运行第三方 notebook、上传或更改权限。

**不能把“我们没看到他们测试”当成“他们没有测试”。四个实际赢过我们的最终版本，在这几场胜局结束前都已完成 75–85 场正式对局；两位临近截止才上线的对手也保留了有赛前战绩的另一版本。具体代码来源仍未知，没有证据认定他们拿到了我们的私有代码。**

## 实际对局记录

从公开 EpisodeService 读取同一提交编号，排除验证游戏，只计 COMPLETED / EPISODE_TYPE_PUBLIC。下表不把不同版本的胜率合并。

| 对手 | 最近赢我们的版本 | 在赢我们前该版本已完成 | 9/30 23:59:00 UTC 前该版本已完成 |
|---|---:|---:|---:|
| Mengfei Li | 56720360 | 75 场 | 17 场 |
| Have a nice trip in USST | 56720127 | 78 场 | 23 场 |
| Agricola | 56722344 | 83 场 | 0 场 |
| american gothic | 56722063 | 85 场 | 0 场 |

该统计区分“上传决策前的经验”和“目前看到的实盘结果”。Agricola 最终版第一场完成于纽约 9/30 20:36；american gothic 第一场完成于纽约 9/30 19:59:02。后一场位于截止标注的最后一分钟边界，不能把“0 场”当成绝对没有任何截止分钟内对局。若改用 UTC 午夜切分，Mengfei 为 18 场、american gothic 为 1 场；其他两者不变，结论不变。比赛列表 API 的 deadline 当前显示 10/14，不能用这个总时间轴字段改写交接资料和官方说明的 9/30 提交截止。

官方现役列表还确认：

| 对手 | 另一个最终现役版本 | 9/30 23:59 UTC 前完成的正式对局 |
|---|---:|---:|
| Agricola | 56688411 | **196 场，149 胜 47 负** |
| american gothic | 56720657 | **15 场，15 胜 0 负** |

Agricola 这个较早版本第一场已在纽约 9/29 18:05 完成。对局记录证明团队有实盘经历，不能证明末版是旧版的小补丁、采用同一源码，或末版已充分验证。也看不到他们的私有 notebook、本地测试和已退休全部版本。

截至本次抓取，孟飞末版共 81 场有 21 负，USST 81 场有 22 负，Agricola 86 场有 28 负，american gothic 86 场有 33 负。他们也会输，单个世界金币差几万不能直接解释为全局评级跃升；总胜率含低分起步阶段，不能拿来与我们的最近胜率直接比较。

## 可核实的公开代码与测试渠道

| 渠道 | 本次核实 | 能证明什么 |
|---|---|---|
| [Rank Your Agent](https://www.kaggle.com/code/raykkretzschmar/kaggriculture-rank-your-agent/output) | 下载源码和元数据；输出页列出 main.py、submission.tar.gz；依赖公开 [Reference Agents](https://www.kaggle.com/datasets/raykkretzschmar/kaggriculture-reference-agents) | 公开渠道提供实际 agent 和本地对战资料。正文版本名与输出文件不能默认一致，需另行核验；不代表上述四队用了它 |
| [Findings from Zero to Top Meta](https://www.kaggle.com/code/raykkretzschmar/kaggriculture-findings-from-zero-to-top-meta) | 原作者明确写了从领导者公开回放提取稳定路线、双座位测试、吸收其他公开作者研究，并嵌入候选 | 从公开动作研究策略不需要获取对手私有源码；回放不是完整源代码，也不自动具有响应能力 |
| [Measure Your Agent](https://www.kaggle.com/code/destbreso/kaggriculture-measure-your-agent) | 元数据引用公开 benchmark-matchups；文档包含环境一致性、对手多样性和独立筛选/确认步骤 | 可以在线下或私有 notebook 验证，未正式上传的测试不会成为赛场提交记录。作者也报告过离线72%而实盘8/60的失败，线下不是万能 |
| [X-ray your agent](https://www.kaggle.com/competitions/kaggriculture/discussion/738563) | 作者给出公开 episode / replay 地址，研究路线、经济和同族关系 | 种植与买卖行为可被研究，不等于获取函数、条件逻辑和源码 |

下载的 Kaito Conditional Memory 文档也给出按时间分开的路线选择和外层留出，明确承认固定录像不响应改动。本次看到的是 8/6 的研究，不把 177/180 标题当成 9/30 对手群的胜率。

本次下载的四份研究说明均不在上轮“最近运行 100 篇”的截取中，说明它不是完整公开代码目录；这里找到的是其他已存在的资料，不能据此宣称发现了 9/30 新发布的强包。Code 页分数前30也重新查过，版本号与9/30 20:33 UTC快照没有变化，历史最佳公开分不能当作现役实力。

## 对我们判断的纠正

此前“别人提升了而我们验证很多仍输”的解释应更精确：我们验证了相对旧版的小改进，却没有充分证明对最终生产型对手的优势。别人的验证活动不必公开，他们也有正式赛前经验；同时有完整公开代码、公开行为和本地试验渠道可用。不需要用“拿到秘密代码”才能解释观察到的差距。

我们现在能确定的是对局记录和产销差异，不能确定四队的源码出处、是否使用强化学习、是否拿了某个公开包，或是否私下分享代码。不会据排名变化指认任何团队违规。此前源码可见性核查只对其已查范围有效，见 [可见性复盘](decline_and_visibility_1001.md)。

数据：`research/opponent_provenance_1001/opponent_history_summary.json`、`earlier_versions_summary.json`、`source_summary.json`。私有仓库只导出自有查询脚本和上述汇总，原始对局列表及第三方 notebook 保留本地。
