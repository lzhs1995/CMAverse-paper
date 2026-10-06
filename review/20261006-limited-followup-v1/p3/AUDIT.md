# P3 实现与来源核查（静态；等待 supervisor 原生验收）

## 已核事实

- `pro_claude_v4_consensus_20261005_v1/run_sensitivity_remaining_v1.R` 实际固定 B=500，`sensitivity_remaining_v1/RESULT.json` 保存 B=500，`ALL_ESTIMANDS.csv` 的 R6_B1 保存500/500。不能称旧 R6 已完成 B=2000。
- 原 R6 使用 `pmin(y1_amt, cap)` 封顶，不删行；精确 cap=2664.29840142096 元/月。
- R6_B1 是12634行、3153簇，5对≤3对比 -25.6105893622746，5对4对比 -30.3551176539399。原 B1 与 R6旧500不保证采用相同索引；新任务明确使用旧主分析 `plan2000.rds` 同时估计两者。
- `recover_probability_draws_v1.R` 在读取旧 B200 对象后断言全部失败均为 Gamma 未收敛，并仅恢复同一索引概率分量。新增 `p3_legacy_audit()` 再从RDS逐项断言 B1=195/200、5个 Gamma 失败，R6=500/500，输出失败draw和SHA。本子任务没有执行R，未将该新增核查说成已运行。

## 交付代码

`p3_frozen_worker.R` 仅定义函数，source 不读取真实数据、不运行模型。

1. `p3_prepare(e, legacy_root)`：使用原函数环境e建立原B完整案例样本，12634行断言，公式文本逐一对应旧保存对象；两版点估计必须对应原保存估计。禁止因公式环境对象不相同而误报内容变化。
2. `p3_legacy_audit(legacy_root)`：核实际RDS B、失败信息和索引关系。
3. `p3_self_test()`：零向量p=1、98%有效率边界、奇异协方差拦截、对比符号变换不变性。
4. `p3_run(frozen,e,dest,through=200L)`：技术节点；同函数through=2000L继续原检查点，不重复已完成draw；也可直接through=2000L，在200保存技术节点后继续。

每25或50次原子检查点。保存原2000簇索引及每个draw哈希；重复抽到的簇通过重复带入全部行保留乘数。两部分、两种Y和三种W采用同一draw及同一标准化总体。概率只拟合一次，Gamma失败不丢失概率。每draw保存警告、Gamma收敛/迭代/秩、正值记录及簇数、max金额。主概率/金额预测非有限时保留失败。

Gamma默认起点、Gamma(log)、maxit200与原代码一致；失败后另用该口径全样本系数作warm-start诊断，保存其收敛与似然。**诊断成功不自动替换主失败**。若决定接受数值修复，须另行冻结一致性标准及版本。

## 两个整体检验

每个Y口径保存 T(≤3)、T(4)、T(5)，两独立差值向量 d=[T(5)-T(≤3), T(5)-T(4)]。

V为同一口径有效成对draw的2×2样本协方差；Qobs=d'V^-1d；零分布Qb=(db-d)'V^-1(db-d)；p=(1+sum(Qb≥Qobs))/(1+Bvalid)。这是固定协方差的中心化bootstrap二次型，不宣称卡方或普遍校准。有效率不足98%或V奇异时p=NA、WITHHELD，不赋1，不补抽。

两个主要结果均属筛选后补充检验。6项全局BH/BY由supervisor合并N1四项后计算，本文件不缩小家族。

## 待supervisor验收

- 本子任务遵守不提交R/网络/UI：没有运行parse、self_test、真实模型或新异步任务；代码现在是待验收实现。
- 请按原加载顺序创建e并载入covariates，然后source本文件，执行self_test、legacy_audit、prepare。
- 在原生MCP提交前确认NLM裁定、磁盘与单重任务身份。`progress`回调由supervisor提供，应写stage/message/updated_at并核10GB磁盘底线。
- 初200核新worker与原成功draw一致，核失败仍记实；随后完成冻结2000，不按p决定继续。
- RDS终态字段明确是函数完成；必须另保存真实native异步终态，不能把函数返回冒充进程结束。
