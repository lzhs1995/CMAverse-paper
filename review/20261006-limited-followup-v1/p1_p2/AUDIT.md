# P1/P2 冻结 worker 交付

状态：代码已写，**未执行R、未通过原生selftest、未提交模型作业**。父协调在原RStudio执行并保留回执。

## 已核源码与目标量

runtime/CMAverse_source_install/R/est.gformula.R：先对干预预测概率取总体均值，logit分支（约404行）计算 `log(EY1m/(1-EY1m))-log(EY0m/(1-EY0m))`。
estinf.R 的 gformula_effect_summary 将前六项取指数；gformula_delta_cde_summary 对两个M状态的指数值相减。因此本次Delta是**边际受控OR之差**，不是风险差、也不是直接回归交互系数。
prepare会核已加载CMAverse est.gformula函数体与本地源码完全相同。未满足时禁止执行，不伪称核过实际安装版本。

## 固定范围

仅031/041；复用原complete-case、23项列顺序、原1000个抽样索引和种子。修订只删dwm_begin，不重新选样本。旧1000直接读取grids及cmest_full，不重估。200为技术检查，之后固定1000；不按p值晋级。
修订bootstrap严格调用原make_shared_cmest，按≤50次分片保留原生grid/diagnostics，失败不补抽。FUNCTION返回不是独立R进程终态。
全簇LOO仅计算确定性结果方程CDE，保持原公式删dwm及删除簇后样本自己的标准化总体；分期同理，只另外删掉在该期恒定的period_fe。其他秩/收敛失败原样保留。LOO是影响诊断，不等同bootstrap或确认检验。

## 原生调用顺序（父协调执行）

```r
source(file.path(s,'limited_followup_20261006_v1/p1_p2/p1_p2_frozen_worker.R'))
saveRDS(p12_self_test(),file.path(runroot,'SELFTEST.rds'))
o <- p12_prepare('FEAS_031',file.path(runroot,'FEAS_031'))
p12_equivalence(o,native_progress)
# 冻结的顺序：1:50、51:100、101:150、151:200；每段只调用一次。
p12_run_chunk(o,1L,50L,native_progress)
# 200次后核技术与失败，写TECHNICAL_REVIEW.rds(list(passed=TRUE,证据引用))，与p无关。
# 然后按相同50步长推进201:1000，不重跑已完成分片。
p12_point_batch(o,periods=TRUE,progress=native_progress)
p12_point_batch(o,cluster_start=1L,cluster_count=50L,progress=native_progress)
# 逐批覆盖sort(unique(o$cluster))全部簇；有失败仍记录该簇，不换簇。
result <- p12_collect(o,200L)  # 最终1000L；不会自行改变推断或删失败。
```

041独立destination，完全同流程。prepare只执行一次，接续读INPUTS.rds。

## LOO等价门禁

原点估计、固定bootstrap 1/17/200的结果方程与保存原生Delta核差<1e-8；修订前两个字典序簇删除样本通过完整原生桥（两个identity draws）核确定性CDE。桥的两个identity draws仅用于等价，不进入统计推断。全量LOO不重拟无关中介模型。

## 必须由原生测试核清的未决项

- 实际旧RDS顶层reg.output$yreg、effect.pe、delta_cde$effect.pe结构与worker预期是否吻合；若不符只做结构适配。
- prepare严格identical原登记行、索引和种子；检查原索引属性是否一致，不得为了通过而取消内容比对。
- 原公式是否恰与原cmest输出相同，无隐藏权重/特殊选项。原worker无casecontrol或weights，本代码只支持该无权重合同。
- chunk间点估计是否一致，p12_collect诊断结构是否与桥实际一致；不得以某分片成功覆盖此前失败。
- EQUIVALENCE的两次原生bridge可能因仅两次bootstrap无法汇总CI，但必须已经捕获合法bootstrap_t0；捕获点值不构成推断通过。
- 尚未在此worker自动生成正式p/CI表；collect输出全部配对draw，交父协调按冻结推断规则汇总。无效draw不被静默排除。
- 本次删dwm并不证明其余22项全部为处理前混杂变量，仍需要时间属性审查结论。

该目录不修改P3、原worker、旧结果或任意共享队列。
