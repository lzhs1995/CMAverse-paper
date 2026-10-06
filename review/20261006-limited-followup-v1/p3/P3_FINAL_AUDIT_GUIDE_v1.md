# P3 最终只读独立验收

本文件及脚本仅已编写、人工静态核查。按要求未运行 R，也未读写在途生产文件。不得据此宣称最终分析或验收已通过。

脚本：
/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1/limited_followup_20261006_v1/p3/p3_final_readonly_audit_v1.R

原 P3 finish 异步作业真实完成后，由 supervisor 保存真实 native 终态证据，再在原 RStudio 会话执行：

```r
a <- new.env(parent=globalenv())
sys.source("/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1/limited_followup_20261006_v1/p3/p3_final_readonly_audit_v1.R", a)
a$p3a_run(
  native_terminal_evidence = "/真实保存的原native终态证据绝对路径",
  native_terminal_verified = TRUE
)
```

native_terminal_verified 只能在 supervisor 已核原 job_id 的真实完成状态后设为 TRUE。脚本将绑定该证据文件 SHA，但不把 RESULT 内部 FUNCTION_COMPLETED 标记当作进程/异步终态。

读取原 manifest 与 prepared 的15项冻结输入、生产 CHECKPOINT/RESULT/TECHNICAL_200/TECHNICAL_REVIEW_200、N1 四项原 CSV；不调用拟合函数。不写上述文件。输出目录固定为：
/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1/limited_followup_20261006_v1/p3/final_audit_v1
已存在则拒绝覆盖。

检查：
- 重算原 worker 定义的 identity，核原 2,000 列抽样计划、每次 draw hash、全局簇零贡献与重复簇权重、行数及合格簇计数。
- 对照 checkpoint 的全部 6,000 方程记录重建三套矩阵；保留 NULL 失败，不补抽。
- warm 诊断存在时正式结果必须 NULL；有效金额结果须 cold 收敛。固定差值与三状态点估计相符。
- 对已保存原金额/封顶金额两项2df整体统计量，以原式独立核算协方差、中心化统计量与 p 的一致性；不新增单对比 p，不更改估计器或门槛。
- 最终少于1,960有效重复、点估计不可用、奇异协方差的检验必须 WITHHELD 且 p=NA。
- 与 N1 四项组成固定六项，p.adjust(...,n=6) 计算 BH/BY；暂缓项原始 p/q 均保留 NA，分母不减少；不将这项校正表述为覆盖此前全部探索。
- 输入 SHA 前后不变；manifest 包括本验收脚本、N1 表与 native 终态证据。

输出：
- REGISTERED_SIX_BH_BY.csv：唯一固定六项汇总。
- P3_TWO_OMNIBUS.csv：两项原整体推断与描述性点估计。
- P3_POINT_ESTIMANDS_NO_NEW_P.csv：概率/原金额/封顶金额的五个点估计，无新 p。
- ALL_6000_EQUATION_DIAGNOSTICS.csv / ALL_PRIMARY_FAILURES.csv：逐 draw 哈希、失败、警告、cold/warm、正值样本/簇、秩及零贡献采样记录。
- DIAGNOSTIC_SUMMARY.csv：方程/失败类型/是否warm诊断汇总。
- INPUT_MANIFEST.csv / ACCEPTANCE.json / REPORT_DATA.json：证据与机器可读报告。

本轮没有执行 R，因此运行时验证尚待原 P3 终态后完成；若验收错误只修验收脚本，不重跑原模型。

