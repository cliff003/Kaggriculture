# cha22 main.py 旋钮笔记（research\panel\cha22\main.py，7482 行）

2026-09-25 只读分析。行号指 main.py。"镜像筛选"见文末：把一个旋钮改掉的 cha22 对原版 cha22，本地 fastarena，同一种子两边座位各打一局。

先说结论：
- Kaggle 取模块里最后一个可调用对象，也就是 `ig_agent`（等于 `kaggle_agent`、`cha20_entry_agent`）。模块级的 `agent` 只是 ADV 层（第 6282 行），T62A 到 IG 这 15 层都不在里面。仓库里的 fastarena、arena、build_submission 都用"最后一个可调用对象"，没受影响；以后谁写 `ns["agent"]` 去拿 cha22 就会拿错。
- 原版对原版的镜像局基本打平：13 个种子里 11 个分数完全相同（种子 11、12 分别差 722、930，都是 player 1 赢）。所以任何一点优势都能把平局变成赢。
- 真正决定镜像胜负的是卖货时机那几层（MPX、MP、DP、EV、ADV、OR2、CXD、FX），不是预约视野。原因：牛奶、羊毛、甜瓜多数时候报价低于基准价，RACEGATE 把它们排除在 44 回合预约之外（13 局里牛奶有 28% 到 99% 的预约回合被排除，羊毛 39% 到 100%）。
- 失效的旋钮：APPLY_TIMING、FRONT_RUN_ITEMS、V9_HERD_*、_R37_ADAPTIVE、_RACE_HORIZON_*、V9_RACE_MAX/MARGIN/WINDOW/GAP（当前取值下），以及开关关着时的 _FX_LEAD_H、_OR2_SN_H。筛选里改这些分数一分不差。_R37_QUOTE 代码上有效，但被 OR2 重排覆盖，筛选也一分不差。
- 列表里没有 import 时被固化的旋钮：全部在函数体里按全局名读取，改模块全局（或 exec 出来的命名空间）就生效。例外是"读取了但层在 import 时就关了"（FRONT_RUN_ITEMS）和"同名定义两次"（_RACE_HORIZON_CLONE 第 5441 行是 8，第 5692 行重设为 9，改前一处无效）。

## 1. 旋钮总表

| knob | current | meaning | alternatives | live-at-call-time? |
|---|---|---|---|---|
| `APPLY_TIMING` | False | 第 1484 行：True 时从 step 144 起用 `_v224_sales_first` 把 SELL 挪到非 SELL 单前（并删掉数量为 0 的单）。紧接着的外层 `_ORDER_PARENT` 无条件做同样的事，函数幂等，所以开不开都一样 | 无 | 是，但失效 |
| `CROP_MIN_PRICE` | 70 | V219 番茄项目在 step 432（第 18 天）的资格线：番茄报价 ≥70；另需现金 ≥12000、只开了 NW/NE/SW、PIZZA_SHOP 加 FARMERS_MARKET ≥3 家、SE 未买、没有番茄。合格就当天买 SE 地和 10 粒番茄种子，每天雇工在 SE 两行浇水收获到第 29 天。13 局镜像里 2 局触发 | 999（关）；40 到 50（更常投资） | 是 |
| `FRONT_RUN_ITEMS` | MILK, WOOL, STRAWBERRY, MELON | 底盘 `_front_run` 的品种：按对手录像抢在对手 SELL 前一步卖。`_SETTINGS['front_run']=False`，`make_agent` 也没传 `opponent_plan`，两者在 import 时固化进 `_IMPL`，这层从不运行 | 无（得重建 `_IMPL` 并提供对手录像） | 调用时读，但层在 import 时已关，失效 |
| `V13V_SKIP_DAYS` | (19, 21, 23) | V219 番茄：这几天若所有番茄昨天都浇过水（番茄能扛 1 天旱，第 25 天前不产出），不雇工不浇水，省工钱。连续两天会被自动拦下。只在 V219 已投资时起作用 | ()（天天浇）；(19, 21) | 是（经替换后的 `_v219_request`） |
| `V9_CARROT_RATIO` | 2.0 | V9 CARROT：第 FIRST 到 LAST 天，胡萝卜报价 ≥2 倍小麦报价且小麦库存 ≥40（繁荣时 10）时，把录像的 PLANT WHEAT 改成 PLANT CARROT（受胡萝卜种子数限制），BUY_SEED WHEAT 改成 CARROT，第 24 天前把多出的胡萝卜放第 0 位卖。13 局里一次也没触发 | 1.5（更常换）；3.0；99（关） | 是 |
| `V9_CARROT_BOOM_RATIO` | 4.5 | 比值 ≥4.5 算繁荣：换种所需小麦储备降到 10，并用（现金减 1500）买小麦补到 40 | 3.0；99（永不繁荣） | 是 |
| `V9_CARROT_FIRST_DAY` | 10 | V9 CARROT 起始天 | 6 到 8；99（关） | 是 |
| `V9_CARROT_LAST_DAY` | 23 | V9 CARROT 结束天 | 26；9（关） | 是 |
| `V9_COURIER_FROM_HOUR` | 12 | V9 COURIER：从这个小时起，手上有 COURIER_ITEMS、当天剩余录像只有移动/PASS/DROP 的工人走回仓库 DROP，这批货当回合放第 0 位卖掉，不用等午夜自动入库后第二天再卖 | 6 到 8（更早送）；24（关） | 是 |
| `V9_COURIER_ITEMS` | STRAWBERRY, MILK, WOOL, MELON | 触发送货的货种 | 加 EGG、TOMATO、CARROT；()（关） | 是 |
| `V9_FERT_AGES` | (1,) | V9 FERT：工人要给这些苗龄（种下后天数）、今天没浇过、没施过肥的 FERT_CROPS 浇水时，若身上有当天录像用不到的肥料，把 WATER 换成 FERTILIZE | (1, 2)；()（关） | 是 |
| `V9_FERT_CROPS` | WHEAT, CARROT | V9 FERT 的作物 | 加 TOMATO；()（关） | 是 |
| `V9_FERT_FIRST_DAY` | 14 | V9 FERT 起始天（到 step 700） | 8；99（关） | 是 |
| `V9_HERD_MAX_EGG_SHOPS` / `_MIN_MILK` / `_MIN_MILK_SHOPS` / `_MIN_WOOL` | 1 / 150 / 3 / 150 | V9 HERD（第一次买鹅时改养羊或牛）的门槛。包装函数只返回上层动作，从不调用 `_v9_herd`（第 3180 行定义后无人调用），整层失效，功能已由 HERD2 取代 | 无（要先恢复调用） | 是，但失效 |
| `V9_RACE_DEFAULT` | 44 | R36 预约视野（step 192 到 695）：报价高于基准价、本回合没在买卖或取用的货，把录像未来 H 回合内计划卖的量现在就卖，记成债务，到期时扣掉录像的 SELL。H=min(MAX, max(DEFAULT, lead+MARGIN))，lead 不超过 WINDOW=30，30+12=42<44，所以 H 恒为 44，只有这个旋钮有效 | 36；60；4（接近 V43 老版） | 是 |
| `V9_RACE_MAX` | 48 | 视野上限，当前到不了；设成小于 44 就等于把视野设成 MAX | 40 | 是（当前失效） |
| `V9_RACE_MARGIN` | 12 | 加在观测到的对手领先回合数上；要 WINDOW+MARGIN>DEFAULT 才起作用 | 20 到 40（视野可到 48） | 是（当前失效） |
| `V9_RACE_WINDOW` | 30 | 对手卖出后，在录像前后多少回合内找我方计划卖单；也是 lead 的上限 | 40 | 是（当前失效） |
| `V9_RACE_GAP` | 3 | 我方上一批计划卖出后 3 回合内对手的卖出算补单，不算领先 | 0；10 | 是（当前失效） |
| `_ADV_BOOK` | False | ADV 提前卖的量是否记成 R36 债务。False：录像到点还会再卖一次当时的现货，等于卖得更多更早 | True | 是 |
| `_ADV_FRONT` | False | True 时重排订单：非本回合买入品的 SELL 在前，BUY_PRODUCT 和买入品的 SELL 居中，HIRE/BUY_SEED/BUY_ANIMAL/BUY_LAND 最后，并删掉空单（像我们的 order-slot 层，但会挪 BUY_PRODUCT、会合并空位） | True | 是 |
| `_ADV_FROM` | 216 | ADV 起始步（到 717，跳过 23 点和有 BUY_PRODUCT 的回合）：每回合把录像未来 LOOK 回合内计划卖的草莓、羊毛、鸡蛋、牛奶、甜瓜、胡萝卜、番茄现在卖掉，不看价格，新单放最前 | 144；999（关） | 是 |
| `_ADV_LOOK` | 3 | ADV 前瞻回合数 | 6 到 12；0（关） | 是 |
| `_ADV_PROTECT` | True | 下一回合第一张单若是 SELL，不提前这个货（保留录像自己的第 0 位卖单） | False | 是 |
| `_BD_CAP` | 64 | BUYDIP 最多挂起多少小麦 | 0（关）；128 | 是 |
| `_BD_MIN` | 8 | BUYDIP（step 24 到 689）：数量 ≥8 的 BUY_PRODUCT WHEAT，在小麦价高于近 WIN 回合均价时只买一半，其余挂起 | 999（关）；4 | 是 |
| `_BD_WIN` | 12 | 均价窗口（回合） | 4；24 | 是 |
| `_BD_DEADLINE` | 6 | 挂起的小麦在价格不高于均价或挂满 6 回合时补买（每回合最多 8，且本回合没有别的小麦买单） | 2；24 | 是 |
| `_CA_CASH` | 800 | CARROT2 补胡萝卜种子（保持 8 粒备用）需现金 ≥800+20×数量 | 0；5000 | 是 |
| `_CA_RESCUE` | True | 换种的胡萝卜若按录像会烂，≥2 天龄就提前收，并把这部分算进换种收益 | False | 是 |
| `_CA_MARGIN` | -20 | 空地上录像要种小麦时，按录像以后的到访模拟产量：胡萝卜产量×价减 20 大于 小麦产量×价减 10 加 MARGIN 就改种胡萝卜。-20 偏向胡萝卜；也控制买种 | 50（少换）；-100（几乎全换） | 是 |
| `_CA_FROM` | 10 | CARROT2 起始天 | 99（关）；6 | 是 |
| `_CA_TO` | 28 | CARROT2 结束天（买种到第 27 天） | 23；9（关） | 是 |
| `_CH_SELL` | True | CAPHARV：动物今晚会超出产量上限时，把 CARE/COLLECT_FERTILIZER 换成 HARVEST；True 时把救下的量立刻卖掉（并入已有 SELL 或放第 0 位） | False | 是 |
| `_CS_OPTIONS` | ('GOOSE',) | COWSWAP：录像第一次买牛（step FROM 到 TO）可改成的品种 | ('GOOSE', 'SHEEP')；()（`max(())` 报错被吞，等于关） | 是 |
| `_CS_RATIO` | 1.3 | COWSWAP：EV(最佳) ≥1.3×EV(牛) 才换 | 1.0；2.0 | 是 |
| `_CS_MIN_GAIN` | 600 | COWSWAP：并且 EV 增益 ≥600 | 0；2000 | 是 |
| `_CS_SHOP_RULE` | 'nomilk' | 店铺门槛。全部取值：'nomilk' 要求没有 PIZZA/ICE_CREAM/SMOOTHIE 且没有 YARN_STORE；其他任何非空字符串（如 'egg'）要求没有奶店且至少一家 BAKERY/BRUNCH_SPOT；空值（''、None、False）不看店，只看 EV | ''；'egg' | 是 |
| `_CS_FROM` | 144 | COWSWAP 窗口起点（第 6 天） | 96 | 是 |
| `_CS_TO` | 192 | COWSWAP 窗口终点 | 144（关）；240 | 是 |
| `_CXD_BUDGET` | 800 | CXD：每回合最多评估多少种 SELL 排位。SELL 可以换到 HIRE/BUY_SEED/BUY_ANIMAL/BUY_LAND 的位置上，用逐单位对撞模拟算"我减对手"，对手模型就是我方排序前的订单（`_CXD_MODELS` 为空）。超预算截断 | 0（关）；5000 | 是 |
| `_DP_HOURS` | (0, 1, 2) | DAWNPX：这些小时（step 96 到 699），对本回合没在买卖、报价 >3 且不低于近 12 回合均价的货，把录像未来 DP_H 回合计划卖量的约 3/4 现在卖，放第 0 位，不记债 | (0..5)；()（关） | 是 |
| `_DP_H` | 8 | DAWNPX 视野 | 16；4 | 是 |
| `_EV_HOURS` | (15..20) | EVENING：同 DAWNPX 的做法，15 到 20 点（step ≥ _FX_MIN_STEP） | (12..22)；()（关） | 是 |
| `_EV_H` | 8 | EVENING 视野 | 16 | 是 |
| `_FX_FLOW_MIN` | 999 | FLOWPX：对手近 8 回合（由市场库存差推算）卖某货 ≥该值、且报价不低于近 12 回合均价时，把未来 LEAD_H 回合的计划卖单全部拉到现在卖（第 0 位）。999 等于关；mirror_like 时也跳过 | 4 到 8（打开） | 是 |
| `_FX_LEAD_H` | 12 | FLOWPX 视野 | 24 | 是（FX 关着时失效） |
| `_FX_MIN_STEP` | 96 | FLOWPX 和 EVENING 的起始步 | 0；216 | 是 |
| `_HD2_OPTIONS` | ('COW', 'SHEEP') | HERD2：录像第一次买鹅时可改成的品种 | ('SHEEP',)；()（关） | 是 |
| `_HD2_RATIO` | 1.3 | HERD2：EV(最佳) ≥1.3×EV(鹅) 才换 | 1.0 | 是 |
| `_HD2_MIN_GAIN` | 600 | HERD2：并且 EV 增益 ≥600 | 0；3000 | 是 |
| `_HD2_CARE` | 0.8 | EV 模型里护理加成的兑现比例：每次产量=1+(每次上限-1)×0.8 | 1.0（偏向牛羊）；0.5 | 是 |
| `_HD2_FROM` | 192 | HERD2 窗口起点：第一次买鹅（只判定一次）要在窗口内、且还没有鸡舍才评估 | 144 | 是 |
| `_HD2_TO` | 360 | HERD2 窗口终点 | 192（关） | 是 |
| `_HD2_FUTURE` | 0.0 | EV 模型里"以后新开店"带来的需求权重，0 表示不算 | 1.0 | 是 |
| `_MA_STATE` | {prior: None, mirror_like: False} | 镜像判定，见第 3 节 | 不能直接设（step 0 重置） | 每次调用读，step 0 到 2 写 |
| `_MPX_HOURS` | 12..22 | MODELPX：step 144 到 695 的这些小时，手上有牛奶/草莓/羊毛且本回合没在卖时，用价格函数估下一回合报价（库存+对手近 4 回合平均卖量+6-城镇消耗），跌幅 >0.5 就先卖最多 3 个（第 0 位）。牛奶、草莓几乎总判会跌，等于每小时滴卖 3 个；羊毛在高价段（log 曲线）很平，基本不触发 | range(0, 24)；()（关） | 是 |
| `_MP_HOURS` | (10..13) | MIDDAY：同 DAWNPX 的做法，10 到 13 点 | (6..14) | 是 |
| `_MP_H` | 8 | MIDDAY 视野 | 16 | 是 |
| `_OR2_CAP` | 24 | ORDERPRI2：由对手地块收获变化和市场库存差估算对手可卖库存；"暴露值"=对手这批（min(CAP, 估计库存)）先成交会让我少赚多少。所有可移动 SELL 按暴露值排到订单最前 | 100；8 | 是 |
| `_OR2_SLOT_H` | 6 | step 288 到 693 订单满 10 张时，看未来 6 回合有没有牛奶/草莓/羊毛/甜瓜/鸡蛋的计划卖单，暴露值比最弱的 SELL 高 MARGIN 就替换它（退回该单的债务，给新单记债） | 0（关）；24 | 是 |
| `_OR2_SLOT_MARGIN` | 12 | 上述替换需要的暴露值优势 | 0 | 是 |
| `_OR2_SN_K` | 0 | 立即卖：>0 时，若估计对手某高价品库存 ≥K，把我方未来 SN_H 回合内的计划卖单拉到现在卖（记债，不看价格）。0 等于关 | 1 到 4 | 是 |
| `_OR2_SN_H` | 24 | 立即卖的视野 | 48 | 是（K=0 时失效） |
| `_PIPE_MODE` | 'EarlyCycle' | 每局 step 0 改写 route 0 的前 96 步（前 6 天所有人都走 route 0）。全部取值：'Original'：V9 开局 BUY 20 / SELL 15，恢复 CTRTABLE 反制表，没有额外农活；'HybridOpening'：同 Original，再加 BUY_SEED WHEAT 1、第 0 天闲置的 hand 1 在 (2,4) 种一株临时小麦、OMW（第 3 天收 3 个）；'EarlyCycle'：step 0 只 BUY 5 小麦加 1 粒种子，删掉 step 1 的小麦买卖，清空 CT_TABLE，临时小麦加 OMW；'TomatoInsteadOfCow'：EarlyCycle 开局，不做 OMW，第 1 天少买 1 头牛，在牛位种 1 株番茄；其他任意字符串：EarlyCycle 去掉 OMW。筛选：'Original'、'TomatoInsteadOfCow' 都 0-6；'HybridOpening' 与现值分数完全相同 | 'Original'；'HybridOpening'；'TomatoInsteadOfCow' | 是（每局 step 0 读） |
| `_R37_ADAPTIVE` | True | 地块相似度连续 6 回合 ≥0.9 时把 R36 视野设成 3 或 4（step 336 到 647）。紧接着 288 到 695 步被无条件设成 4，而真正的预约视野取自 `_V9_ITEM_HZ`（44），所以只剩遥测 | 无 | 是，但失效 |
| `_R37_QUOTE` | True | step 288 起，把一段连续、品种不重复的 SELL 按暴露值排序（对手批量取对手地里可见成熟产量，8 到 24）；之后 OR2 用同一个优先级作次级键把全部 SELL 重排，CXD 再排，这里只影响完全平手时的顺序（筛选 6 个种子分数全同） | False | 是，但实际被覆盖 |
| `_R51_INPUT_MAX_WORKERS` | 2 | 第 12 到 28 天 1 到 3 点，最多额外雇几人带肥料给幼小麦/胡萝卜施肥（每人价值须 ≥1.5×成本+50） | 0（关）；4 | 是 |
| `_R85_FEED` | True | 第 10 到 28 天，这次喂食的护理加成价值（(待兑加成+护理)×(产品价+5)×1.25）低于小麦价、且明天录像会喂这格时，把 FEED 改成 PASS 省小麦 | False | 是 |
| `_R85_FERT` | True | 第 6 到 28 天，本回合只有 SELL 时，把超过储备（max(14, 录像未来取用+专项工人需求)）的肥料卖掉 | False | 是 |
| `_R88_HORIZON` | True | 喂食成本模型：今天的护理若到第 29 天后才兑现，记 0（多跳过喂食） | False | 是 |
| `_R88_PHASE` | True | 喂食成本模型：明天不是产出日时，待兑护理加成记 0（多跳过喂食） | False | 是 |
| `_RACE_HORIZON_CLONE` | 9（第 5441 行写 8，第 5692 行重设为 9） | EXP283：判为克隆（双方工人位置 6 回合中 ≥4 回合相同且地块相似度 ≥0.95，step 216 到 695）时给 R36 的视野。实际预约只要 `_V9_ITEM_HZ` 存在就用它（44），这个值被忽略 | 无 | 是（每局初始化读），但失效 |
| `_RACE_HORIZON_ESCALATED` | 24 | 发现"被对手抢先"后升级用的视野 | 无 | 是，但失效 |
| `_RACE_HORIZON_MIRROR` | 24 | step 1 双方现金相差 <0.5 时用的视野。原版镜像时确实触发（race_mirror=1），但同样被忽略 | 无 | 是，但失效 |
| `_SR_HOURS` | (21, 22, 23) | SHEDROOM：这些小时估计今晚仓库（下单后）加身上货 >100-MARGIN 时，按价格从低到高卖掉多余库存（保留未来 24 回合喂食和施肥所需） | (23,)；()（关） | 是 |
| `_SR_MARGIN` | 8 | SHEDROOM 余量 | 0；30 | 是 |
| `_V219_FERTILIZE` | True | V219 番茄第 24、27 天是否买肥料施肥（还要 `_r79` 判定划算） | False | 是 |
| `_V231_CAP` | 4 | step 216 到 227，奶店 ≥2、没有毛线店、奶价不低于羊毛价、已有 ≥4 牛和 ≥2 羊时，把录像里唯一一张 1 到 2 只的 BUY_ANIMAL SHEEP 改成 COW；上限是累计改换头数 | 0（关）；8 | 是 |
| `_V44Y_REORDER_GATE` | False | V44Y：step 216 起对 2 到 6 张连续的 SELL 做全排列，用逐单位对撞模拟（假设对手订单和我方原订单相同）挑差额最大的。False 每回合都做；True 只在 RACE 判为克隆时做（原版镜像 13 局每局 480 回合里有 476 回合判为克隆，所以镜像里没差别，只对非镜像对手有影响） | True | 是 |
| `_Y_CFG` | {'yarnsheep': True, 'yarngeese': True, 'days': (8, 11)} | 按店换畜：第 8 到 11 天，数量 1 到 2（maxq）的 BUY_ANIMAL，开了毛线店时 COW 换 SHEEP（yarnsheep）、GOOSE 换 SHEEP（yarngeese），先查现金（margin 默认 100），再改写 PICKUP/PLACE/BUILD_COOP，额外产量加到已有 SELL 上（boost）。其他可用键：'nosheep' 加 'min_milk'（没有毛线店时 SHEEP 换 COW）、'nogeese'（没有蛋店时 GOOSE 换 SHEEP 或 COW）、'maxq'、'margin'、'boost'。13 局里一次也没触发 | 两项都设 False（关）；加 'nogeese': True、'days': (6, 14)、'maxq': 4 | 是 |
| `_Y_HOURS` | (21, 22) | PREGUARD：这些小时（第 1 天起，step<696），若下单后库存加身上货 >99+MARGIN，按价格从高到低分摊超出量，只给 MILK/STRAWBERRY/MELON/WOOL/TOMATO 追加 SELL（放末尾），提前一步卖掉 23 点仓库保护会甩卖的货 | (18..22)；(12..22) | 是 |
| `_Y_MARGIN` | -6 | PREGUARD 触发线：库存加货 >93 | -30（>69 就卖）；0 | 是 |

## 2. 镜像筛选

做法：在内存里 exec 两份 main.py，只改 A 份的模块全局（文件不动），A 对原版 B，tools\fastarena.py，种子 1 到 10（前 33 个改动）或 1 到 6（其余和失效检查），两边座位各一局。换座位的两局分数完全相同（游戏对座位对称），所以按种子计数。基线：原版对原版在种子 1 到 10 全部完全打平。差额=改动方减原版（每个种子平均）；"比基线多赚"=改动方分数减原版镜像时的分数，负数说明是靠压低对手赢的。样本小，只当筛选。

| 改动 | 种子 胜-负-平 | 平均差额 | 比基线多赚 |
|---|---|---|---|
| `V9_RACE_DEFAULT=36` | 5-3-2 | -30 | +16 |
| `V9_RACE_DEFAULT=60` | 5-1-4 | -4 | +9 |
| `V9_RACE_MARGIN=40` | 3-1-6 | -6 | +8 |
| `V9_RACEGATE_MARGIN=-60` | 8-2-0 | +194 | -188 |
| `_EV_HOURS=12..22` | 2-0-8 | +0 | -14 |
| `_EV_H=16` | 2-2-6 | -2 | +10 |
| `_EV_HOURS=()` | 2-8-0 | -8 | +10 |
| `_DP_HOURS=0..5` | 9-0-1 | +93 | +14 |
| `_DP_H=16` | 6-4-0 | +99 | +24 |
| `_MP_HOURS=6..14` | 10-0-0 | +358 | +166 |
| `_MP_H=16` | 10-0-0 | +338 | +113 |
| `_MPX_HOURS=0..23` | 10-0-0 | +659 | -256 |
| `_MPX_HOURS=()` | 0-10-0 | -848 | -278 |
| `_ADV_LOOK=6` | 7-3-0 | +266 | +40 |
| `_ADV_LOOK=0` | 1-9-0 | -182 | -235 |
| `_ADV_FROM=144` | 0-0-10 | +0 | +0 |
| `_ADV_PROTECT=False` | 8-2-0 | +92 | -109 |
| `_ADV_BOOK=True` | 2-6-2 | -18 | -60 |
| `_ADV_FRONT=True` | 1-9-0 | -39 | -28 |
| `_FX_FLOW_MIN=4` | 5-4-1 | +86 | +9 |
| `_FX_FLOW_MIN=4,_FX_LEAD_H=24` | 9-1-0 | +283 | -15 |
| `_FX_MIN_STEP=0` | 0-0-10 | +0 | +0 |
| `_OR2_SN_K=1` | 8-2-0 | +355 | -124 |
| `_OR2_SN_K=4,_OR2_SN_H=48` | 8-2-0 | +468 | -192 |
| `_OR2_SLOT_H=0` | 0-10-0 | -374 | -158 |
| `_OR2_CAP=100` | 1-1-8 | -6 | -4 |
| `_OR2_SLOT_MARGIN=0` | 2-1-7 | +1 | -3 |
| `_CXD_BUDGET=0` | 0-10-0 | -352 | -201 |
| `_CXD_BUDGET=5000` | 4-1-5 | +12 | +4 |
| `_V44Y_REORDER_GATE=True` | 0-0-10 | +0 | +0 |
| `_Y_MARGIN=-30` | 1-3-6 | +7 | -2 |
| `_Y_HOURS=12..22` | 2-3-5 | +2 | -3 |
| `_SR_MARGIN=30` | 3-3-0 | -7 | -84 |
| `_SR_HOURS=()` | 2-1-3 | -7 | +3 |
| `V9_COURIER_FROM_HOUR=6` | 0-0-6 | +0 | +0 |
| `V9_COURIER_FROM_HOUR=24` | 0-5-1 | -209 | -130 |
| `V9_COURIER_ITEMS+EGG,TOMATO,CARROT` | 0-0-6 | +0 | -0 |
| `_CH_SELL=False` | 2-2-2 | -31 | -18 |
| `_HD2_MIN_GAIN=0,_HD2_RATIO=1.0` | 0-0-6 | +0 | +0 |
| `_HD2_OPTIONS=()` | 0-0-6 | +0 | +0 |
| `_HD2_FUTURE=1.0` | 1-0-5 | +606 | -193 |
| `_HD2_CARE=1.0` | 0-0-6 | +0 | +0 |
| `_HD2_TO=192` | 0-0-6 | +0 | +0 |
| `_CS_SHOP_RULE=''` | 2-1-3 | -753 | +542 |
| `_CS_SHOP_RULE='egg'` | 0-0-6 | +0 | +0 |
| `_CS_OPTIONS=(GOOSE,SHEEP)` | 0-0-6 | +0 | +0 |
| `_CS_MIN_GAIN=0,_CS_RATIO=1.0` | 0-0-6 | +0 | +0 |
| `_CS_TO=144` | 0-0-6 | +0 | +0 |
| `_CA_MARGIN=50` | 1-2-3 | -324 | -230 |
| `_CA_MARGIN=-100` | 0-6-0 | -3444 | -6444 |
| `_CA_FROM=99` | 1-2-3 | -661 | -490 |
| `_CA_RESCUE=False` | 1-1-4 | -12 | +20 |
| `_CA_CASH=5000` | 0-0-6 | +0 | +0 |
| `V9_CARROT_RATIO=1.5` | 0-0-6 | +0 | +0 |
| `V9_CARROT_BOOM_RATIO=3.0` | 0-0-6 | +0 | +0 |
| `V9_CARROT_FIRST_DAY=99` | 0-0-6 | +0 | +0 |
| `V9_FERT_FIRST_DAY=8` | 4-2-0 | -3 | +26 |
| `V9_FERT_AGES=(1,2)` | 0-6-0 | -80 | -56 |
| `V9_FERT_FIRST_DAY=99` | 0-6-0 | -181 | -197 |
| `_BD_MIN=999` | 3-3-0 | -103 | -200 |
| `_BD_DEADLINE=2` | 4-1-1 | +2 | -84 |
| `_R85_FEED=False` | 0-6-0 | -1960 | -2898 |
| `_R85_FERT=False` | 0-0-6 | +0 | +0 |
| `_R88_PHASE=False` | 1-5-0 | -385 | -615 |
| `_R88_HORIZON=False` | 0-5-1 | -59 | -54 |
| `_R51_INPUT_MAX_WORKERS=0` | 1-5-0 | -701 | -666 |
| `_R51_INPUT_MAX_WORKERS=4` | 0-0-6 | +0 | +0 |
| `_V231_CAP=0` | 0-0-6 | +0 | +0 |
| `CROP_MIN_PRICE=999` | 0-1-5 | -9515 | -7558 |
| `CROP_MIN_PRICE=40` | 0-0-6 | +0 | +0 |
| `_V219_FERTILIZE=False` | 0-1-5 | -4343 | -3594 |
| `V13V_SKIP_DAYS=()` | 0-1-5 | -106 | -106 |
| `_Y_CFG=off` | 0-0-6 | +0 | +0 |
| `_Y_CFG=wide` | 2-4-0 | -5845 | -7066 |
| `_PIPE_MODE=Original` | 0-6-0 | -78 | -195 |
| `_PIPE_MODE=HybridOpening` | 0-0-6 | +0 | +0 |
| `_PIPE_MODE=TomatoInsteadOfCow` | 0-6-0 | -3869 | -3416 |
| `_R37_QUOTE=False` | 0-0-6 | +0 | +0 |
| `APPLY_TIMING=True` | 0-0-6 | +0 | +0 |
| `_R37_ADAPTIVE=False` | 0-0-6 | +0 | +0 |
| `_RACE_HORIZON_*=100` | 0-0-6 | +0 | +0 |
| `_RACE_HORIZON_*=0` | 0-0-6 | +0 | +0 |
| `V9_RACE_MAX=60` | 0-0-6 | +0 | +0 |
| `V9_RACE_WINDOW=10,GAP=0` | 0-0-6 | +0 | +0 |
| `V9_HERD_*=loose` | 0-0-6 | +0 | +0 |
| `FRONT_RUN_ITEMS=()` | 0-0-6 | +0 | +0 |
| `_FX_LEAD_H=48` | 0-0-6 | +0 | +0 |
| `_OR2_SN_H=100` | 0-0-6 | +0 | +0 |

读法：
- 卖货时机层最敏感。MODELPX 全天开 10-0、关掉 0-10；MIDDAY 小时放宽或视野 16 都是 10-0；DAWNPX 放宽 9-0-1；ADV 前瞻 6 是 7-3、关掉 1-9；OR2 立即卖打开 8-2、关掉换单 0-10；FLOWPX 打开且视野 24 是 9-1；CXD 关掉 0-10。
- 预约视野本身（V9_RACE_DEFAULT 36 或 60）只有 5-3、5-1，差额很小；RACEGATE 放宽到基准价减 60 反而 8-2。镜像里比的是"过剩"货（牛奶、羊毛、甜瓜）谁先卖。
- 不少"更早卖"的改动让自己少赚（比基线多赚为负），是靠抢在对手前面赢的。对不抢跑的对手未必划算。
- 生产类旋钮只在少数世界触发，但一触发差额很大：V219 番茄在种子 1 触发，关掉输 5.7 万，不施肥输 2.6 万；_Y_CFG 放宽 2-4，单局最多输 2.4 万；_CA_MARGIN=-100 六个种子全输，平均 -3444。
- 分数完全不变（失效或筛选种子里没触发）：APPLY_TIMING、_R37_ADAPTIVE、_RACE_HORIZON_*、V9_RACE_MAX、V9_RACE_WINDOW/GAP、V9_HERD_*、FRONT_RUN_ITEMS、_FX_LEAD_H、_OR2_SN_H（前九个是代码层面失效）；_V44Y_REORDER_GATE（镜像里克隆判定恒真）；_R37_QUOTE（被 OR2 重排覆盖）；_ADV_FROM=144、_FX_MIN_STEP=0、V9_COURIER_FROM_HOUR=6、V9_COURIER_ITEMS、_HD2_*（除 FUTURE）、_CS_*（除 SHOP_RULE=''）、_CA_CASH、V9_CARROT_*、_R85_FERT、_R51_INPUT_MAX_WORKERS=4、_V231_CAP、CROP_MIN_PRICE=40、_Y_CFG=off、_PIPE_MODE='HybridOpening'（开局 BUY 20/SELL 15 和 BUY 5 在这个价位花的钱一样，step 1 后两边都是 1042）。

## 3. `_MA_STATE`：镜像判定

- 触发：step 0 清零；step 1 记下市场小麦库存；step 2 算 fall=step 1 的库存减 step 2 的库存，也就是 step 1 双方净买入的小麦（step 1 没有城镇消耗）。fall ≥15 则 mirror_like=True。
- 对原版镜像不触发：EarlyCycle 开局在 step 1 没有任何小麦单，13 局 fall 全是 0。只有对手在 step 1 净买 ≥15 小麦时才触发。
- 触发后的变化只有两处：WB3 把 BUY_PRODUCT WHEAT 挪到第 0 位的店铺组合多一个 (PIZZA_SHOP, SMOOTHIE_SHOP)（(BRUNCH_SPOT, BRUNCH_SPOT) 和 (BAKERY, BRUNCH_SPOT) 不看 mirror_like 也会挪）；FLOWPX 跳过（本来就因 _FX_FLOW_MIN=999 关着）。
- 它是模块级的一个 dict，不分座位。Kaggle 每个 agent 各自一个进程没问题；本地若两个座位共用同一个 exec 出来的命名空间，会互相覆盖。
- 另外还有三处"镜像/克隆"判定，都已失效或只影响失效的东西：RACE 的 step 1 现金相等（race_mirror）和位置相同加相似度 ≥0.95（clone），R44 的现金变化相等（probe），R37 的地块相似度（streak）。它们最后都只改 `_R37_HORIZONS` 或 RACE 的 level，而预约视野用的是 `_V9_ITEM_HZ`。唯一还有实际用途的是 `_r37_similarity` 在 HERD2 的 EV 里：相似度 ≥0.9 时假设对手也照录像买同样的牲畜。

## 4. 最终 agent 的组装顺序（从里到外）

1. `_IMPL`（第 981 行）：`Chassis` 回放 `_router` 选的录像（前 6 天 route 0；step 144 按前两家店换路线；step 648 起 route 2）。只开 hand_align、weed_repair、sell_lead。sell_lead 被替换两次：R36 版只在 step <288 或 ≥696 把下一步的计划卖量提前一步卖；RACEPX 版在有任一货报价不高于基准价时（肥料几乎一直如此）接管，对其余报价高于基准价的货在所有 step（4 的倍数和 72 步边界前一步除外）提前一步卖；suppression 被替换成会扣 R36 债务的版本。
2. 保护壳 → step ≥718 清仓 → E182 终局规划（712 到 718，影子模拟）→ 23 点仓库保护（超 99 按价高先卖）→ V28 保护壳。
3. V219 番茄项目（V13V 通过替换 `_v219_request` 生效）→ APPLY_TIMING 壳 → step ≥144 卖单前置 → V31 壳 → V231 羊换牛。
4. R36 预约：`_r36_reserve` 是后绑定的全局名，实际调用链是 RACE 版 → RACEGATE 版（排除报价不高于基准价的货）→ 原版，视野取 `_V9_ITEM_HZ`；step ≥288 再做一次卖单前置。
5. R37（视野加报价排序、R44 探针）→ RELEASE 保护壳 → V233 六只羊项目（SL、VE、VT 通过替换 `_v233_request/_v233_worker/_v233_eligible/_v234_rescue` 生效）→ R46 → R51 施肥工 → R51 仓库 → R53 → R70 → R85 喂食/卖肥 → R95 → R97 小麦供应。
6. V9 层：COURIER → CARROT → HERD（空壳）→ FERT → OPENING（BUY 20/SELL 15）→ RACE（每回合写 `_V9_ITEM_HZ`=44）→ RACEPX（只是壳，逻辑在底盘）→ RACEGATE（只是壳）→ CTRTABLE → OVERFLOW。
7. CARROT2 → ORDERPRI2 → CAPHARV → SHEDROOM → HERD2 → COWSWAP → RACE(EXP283) → R127（优先小麦、23 点删掉浇不上水的种植）。
8. PREGUARD（`_PG_HOST`）→ V44Y 重排（`_V44Y_HOST`）→ 按店换畜（`_Y_HOST`）→ E334/E335 压缩（留空单占位）→ V11 入口 → V13V 壳 → E343 杂草补做 → ADV（模块级 `agent` 到此为止）。这几层靠"取最后一个可调用对象"串起来。
9. T62A（step ≥712 用整仓 SELL 覆盖市场单）→ PIPE 开局 → MA 镜像判定 → WB3 小麦买单前置 → FLOWPX 加 EVENING → DAWNPX → MIDDAY → BUYDIP → MODELPX → SHIELD-MILK（有奶店时补卖货凑钱）→ CXD 排位 → E410 肥料 → E402 后期种子上限 → MERGE 合并同品种单 → IG 空位回填（最外层，即导出的入口）。

## 5. 读取对手状态的层

| 层 | 读什么 | 用来做什么 | 现在是否生效 |
|---|---|---|---|
| `_router` step 2 | 对手现金、市场小麦库存 | 存进 `state['rkey']`，没人用 | 否 |
| CTRTABLE step 2 | 同上 | 认出两个已知的现金紧张公开录像，在 step 3、7、8 的指定位置跟单买卖小麦 | EarlyCycle 下 CT_TABLE 被清空，否 |
| R37 `_r37_similarity` | 双方地块作物/动物 | 连续相似就改视野；也被 R44、HERD2、RACE、V44Y 门控用 | 视野部分否；HERD2 里是 |
| R37 `_r37_quote_priority` | 对手地里可见成熟产量 | 定对手批量（8 到 24），给 SELL 排序（step ≥288），也是 OR2 的次级排序键 | 是 |
| R44 探针 | 对手现金变化 | 和我方现金变化相等时把视野设 4 | 否 |
| V9 RACE | 市场库存差减城镇消耗减我方卖出 = 对手卖出 | 算对手领先回合数，调视野 | 视野恒 44，否 |
| RACE(EXP283) | 对手农夫和工人位置、地块、step 1 现金、库存差 | 判克隆、镜像、被抢先，改视野 | 否（被 44 覆盖）；克隆标志只给关着的 V44Y 门控 |
| ORDERPRI2 | 对手地块产量减少或作物消失（收获），加库存差（卖出） | 估计对手每种货的可卖库存，按暴露值把 SELL 排到最前，订单满时换卖单（SN 关着） | 是 |
| HERD2 / COWSWAP `_hd2_ev` | 对手地里每种动物数量和放养日 | 模拟未来价格路径，算"我方存量减对手存量"的价格摆动，决定换不换品种 | 是 |
| MA | step 1 到 2 市场小麦下降量 | mirror_like，见第 3 节 | 对原版镜像不触发 |
| FLOWPX | 库存差推算的对手卖量 | 对手活跃时整段提前卖 | 否（999） |
| MODELPX | 库存差推算的对手近 4 回合卖量 | 预测下一回合降价就先卖 3 个 | 是 |
| V44Y、CXD | 不读对手，假设对手订单和我方一样 | 选对撞下差额最大的排位 | 是 |
| R127 | 不读对手，假设对手同步买小麦 | 保守估算买价 | 是 |

底盘 `_View.rival` 算了但没人用。

## 6. 其他发现

- `V9_RACEGATE_MARGIN`（不在清单里，默认 0）很关键：报价不高于 牛奶 160、羊毛 200、甜瓜 250、草莓 120、鸡蛋 50、肥料 100 的货不进 44 回合预约，也不走 RACEPX 一步提前卖。13 局镜像里肥料 100% 被排除，羊毛 39% 到 100%，甜瓜约 88%，牛奶 28% 到 99%，草莓 0% 到 58%，鸡蛋 0% 到 67%。牛奶价格在库存超过 I0 后按每单位约 2.1 元直线下跌（160 元到 1 元只隔约 76 个），所以一旦有人多卖，牛奶就长期处在"过剩"区。
- gold\candidates\fertlead 的 `_CFG` 设了 V9_RACE_DEFAULT=56、MAX=64、MARGIN=16：lead+16 最多 46<56，视野恒为 56，MAX 和 MARGIN 没有作用。
- 同名多次定义，改的时候要改最后一个：`_r36_reserve`（第 1673、3652、5504 行）、`_v233_request`（3 处）、`_v233_worker`（3 处）、`_v233_eligible`、`_v234_rescue`、`_v219_request`、`_shadow_terminal`、`_e334_compact`、`_RACE_HORIZON_CLONE`。
- EVENING、DAWNPX、MIDDAY 的注释说"一半"，代码实际是约 3/4：qty=min(库存, max(1, (3×计划量+3)//4))。
