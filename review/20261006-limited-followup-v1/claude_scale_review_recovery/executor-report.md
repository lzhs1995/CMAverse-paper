# FEAS_031 / FEAS_041 定义与实际尺度独立审查

任务 `cmaverse-limited-scale-review-recovery-20261006`｜执行者 surface:41｜只读审查，未提交 R 作业、未拟合模型、未改共享输入。

本报告每条结论都给文件路径+行号或对象字段。结论分三类：**已证实**（本轮实测）、**待核**（需原生 R 会话或监督方裁定）、**不下结论**（证据不足，不猜）。

---

## 0. 输入身份（本轮实测 SHA256）

| 对象 | SHA256 | 字节 |
|---|---|---|
| `feasible_population_v1/specifications.csv` | `9ed331391d5359a707692e9ff5ce849ef63e11f87d926368c889ca347a79ddd3` | 80519 |
| `verify_B1000_v1/worker.R` | `e04e40ff4b6b868c0ad0c464987fda1174eeb961d15718148806a2aaa0a6bd83` | 105 行 |
| `candidate_data.R` | `802a91bb456de0a1…` | 1629 |
| `baseline_adjustment.R` | `0d9f91af5036ca29…` | 740 |
| `screening_records.R` | `3738309998390d96…` | 3107 |
| `shared_bootstrap_diagnostic.R` | `feaba1da5e407bb9…` | 122 行 |
| `limited_followup_20261006_v1/p1_p2/p1_p2_frozen_worker.R` | `e3b648d26be10c70…` | 12039 |

抽样计划钉子一致（**已证实**）：`feasible_sampling_v1/RESULT.json` 的 `registry_sha256` / `membership_sha256` 与现时文件逐字节相同，`worker.R:32-33` 的断言当前可通过。

---

## 1. 核心结论：比值尺度是**优势比（OR）**，不是风险比（RR）

**已证实。** 判据在 CMAverse 实现里，不在列名里。

`runtime/CMAverse_source_install/R/est.gformula.R:403-410`：

```r
## output effects on the odds ratio scale for logistic regressions
if (is_glm_yreg && family_yreg$family %in% c("binomial","quasibinomial") &&
    family_yreg$link == "logit") {
  logRRcde  <- log(EY1m/(1-EY1m)) - log(EY0m/(1-EY0m))
  ...
  logRRtnie <- log(EY11/(1-EY11)) - log(EY10/(1-EY10))
  ## otherwise on the risk ratio scale
} else {
  logRRcde  <- log(EY1m) - log(EY0m)        # :413-417 才是真 log-RR
```

FEAS_031 与 FEAS_041 的 `yreg` 均为 `logistic`（specifications.csv），所以**走 :404-410 的 OR 分支**。`est.gformula.R` 源码注释自己说清楚了（`:403` "odds ratio scale"），但变量名叫 `logRR*`，下游一路沿用「R=ratio」：

- `estinf.R:401-407` 命名 `Rcde/Rpnde/Rtnde/Rpnie/Rtnie/Rte`
- `estinf.R:396-398` 对前 6 列取 `exp()`，与 `screening_records.R:37` 的注释一致
- 注册表 `outcome_scale = 'ratio_log_for_testing'`（50 个比值规格全同一值）
- `METRICS.csv` 发表为 `test_scale = log_ratio`

**本机实测版本同一性**：`est.gformula.R` 在 4 个源码树中逐字节相同（`7762e13d056ae857`，21560 B）；在原生 R 里 `identical(body(est.gformula_source), body(asNamespace('CMAverse')$est.gformula))` 返回 **TRUE**，即 `p1_p2_frozen_worker.R:36` 的断言当前可通过，装载的就是这份实现。（注意 `sources/software/CMAverse-mval-grid-mac/.../00_pkg_src` 那棵树的 `estinf.R`/`cmest.R` 不同且缺 `cmest-sanitize.R`，不是现役；别用它核对。）

### 为什么必须改口径说明，而不只是改个名字

1. **TNIE 作为 OR 不可崩缩（non-collapsible）**，其数值随协变量集合变化，与 RR 的解释不同；现在文稿口径词是「比值」，读者会按 RR 读。
2. `Delta_CDE` 是**两个 OR 之差**（`screening_records.R:51`：`Delta_CDE = b[['Rcde']] - a[['Rcde']]`，两侧已在 `:40` 取 exp），零假设是 0；而 TNIE 的零假设是 1。两个量在同一张表里、同一个 `ratio_*` 词族下，零值不同。
3. 命名在两代之间已经不一致：`p1_p2_frozen_worker.R:10` 把同一量正确写成 **`Delta_OR`**，而上游 `METRICS.csv` 对同样的规格写 `Delta_CDE` / `ratio_difference`。

**P1/P2 建议（口径）**：注册表 `outcome_scale` 对 50 个比值规格细分为 `odds_ratio_log`（logit 结局）与 `risk_ratio_log`（其他非连续结局）两值；表头与文稿把 TNIE 写成「自然间接效应（OR 标度）」，`Delta_OR` 写成「受控直接效应的 OR 之差（零值 0）」。**不要**把 `Delta_OR` 和 TNIE 并列在同一个「比值」列里不加零值标注。

---

## 2. 阻断项：P1/P2 的 `p12_prepare()` 当前**无法运行**（两个独立原因）

**已证实。** 两条都在 `p1_p2_frozen_worker.R` 里，不是环境问题。

### 2.1 路径深了一层

`:23` 计算 `olddir <- file.path(p12_s,'verify_B1000_v1',id)`，`:24` 读 `olddir/execution_inputs.rds`。

实测：产物实际在 **`verify_B1000_v1/<id>/<id>/`**（嵌套两层），因为 `verify_B1000_v1/FEAS_031/driver.R:14` 把 `destination` 传成 `file.path(control,'FEAS_031')`，而 `control` 本身已是 `verify_B1000_v1/FEAS_031`。

```
ABSENT   verify_B1000_v1/FEAS_031/execution_inputs.rds          ← p12 算出的路径
PRESENT  verify_B1000_v1/FEAS_031/FEAS_031/execution_inputs.rds  15638765 B
PRESENT  verify_B1000_v1/FEAS_041/FEAS_041/execution_inputs.rds  21007158 B
```

`grids/` 同理，各 1003 个文件（`bootstrap_01…1000` + `bootstrap_t0` + 两个 `point_*`）。

附带澄清：`:39` 的 `sprintf('bootstrap_%02d.rds', b)` 对 b>99 **没有问题**——`%02d` 是最小宽度，写入侧 `shared_bootstrap_diagnostic.R:79` 用同一个格式串，实测 `bootstrap_1000.rds` 两侧一致、文件存在。这一条不是缺陷。

### 2.2 `cmest_full.rds` 全树不存在

`:37` 读 `olddir/cmest_full.rds`，`:38/:45/:46` 依赖它的 `effect.pe`、`delta_cde$effect.pe`、`reg.output$yreg`。

实测：`verify_B1000_v1` 下 `cmest_full.rds` 命中 **0**（非空对照：同一 `find` 语法下 `execution_inputs.rds` 命中 11）。两个 spec 更深一层也没有。

它**曾经存在**并被读过：`verify_B1000_v1/validate.R` 读 `cmest_full.rds` 并记录

- FEAS_031：`full_object_bytes = 148129491`，`full_object_sha256 = aa653f385e70689206082650d6acb40d43019d2abd52bb02c66ae303f3892800`
- FEAS_041：`full_object_bytes = 183476518`，`full_object_sha256 = 50dd5d5a0d79b43c…`

树内无任何 `rm`/`unlink` 语句命中；当前磁盘 `875Gi/926Gi`、**仅剩 13Gi（99%）**。两份对象合计约 316 MB。删除者与时点**不下结论**（无台账），但「曾完整存在且通过校验」是已证实的。

### 2.3 哪些字段还能救回来，哪些不能

| p12 需要的字段 | 可恢复 | 来源（实测） |
|---|---|---|
| `inputs`（`actual_indices`/`replicate_seeds`/`sample`/`spec`） | ✅ | 深一层的 `execution_inputs.rds` |
| `old_point['Delta_OR']` | ✅ **精确** | `grids/bootstrap_t0.rds` 经 `p12_metric` 得 `-0.407543877675273`，与 `METRICS.csv` 的 `Delta_CDE` 逐位相同 |
| `old_point['TNIE']` | ✅ **精确** | `METRICS.rds$point$effect['TNIE']` = `0.999271478272025`，等于 `exp(point$test_value['TNIE'])` |
| `old_formula`（yreg 公式） | ⚠️ **仅 RHS 项集** | 由 `grids/*.rds` 的系数名重建：26 个词干 = `X, M, X:M` + 23 项控制（实测 FEAS_031 yreg 模型 28 个系数、rank 28、nobs 9879） |
| `old$reg.output` 全对象 / `effect.se` / `effect.pval` | ❌ | `METRICS.rds` 只有 `point` 与 `bootstrap_test_values`（1000×2）；全文件搜 `formula`/`reg.output` 命中 **FALSE**。`ALL_NATIVE_EFFECTS.csv` 另存了 17×2 条 native 效应，可作部分替代 |

**关键陷阱（已证实）**：`p12_metric(bootstrap_t0)` 的 TNIE = `0.999422286830433`，**不等于**发表值 `0.999271478272025`。原因见 §3——`validate.R` 的 TNIE 取自 native `effect.pe`，而 `bootstrap_t0` 是另一次带自己种子的重算。若 P1/P2 用 t0 重建 `old_point['TNIE']`，配对基线就和已发表表格不一致。`Delta_OR` 不受影响（两处逐位相同）。

**P1/P2 最小实现建议**

1. `:23` 改 `olddir <- file.path(p12_s,'verify_B1000_v1',id,id)`，并加 `stopifnot(file.exists(file.path(olddir,'execution_inputs.rds')))`。
2. 删掉对 `cmest_full.rds` 的依赖，改为显式三源：`old_point['TNIE']` ← `METRICS.rds$point$effect['TNIE']`；`old_point['Delta_OR']` ← `METRICS.rds$point$effect['Delta_CDE']`（同一量，见 §1 命名）；`old_formula` ← 由 `covars` + `X*M` 重建，并**断言**重建公式的 `model.matrix` 列名集合与 `grids/bootstrap_t0.rds` 的 yreg 系数名集合相等。这比读回原公式更强：它同时验证了列构造。
3. `p12_metric:9` 的 `length(grid[[1]]$est)>=6L` 太弱——实测 `est` **无 names**（`names(est) present? FALSE`），`est[5]`/`est[1]` 是纯位置索引。移植 `screening_records.R:39` 的真断言 `identical(effect_names[1:6], c('Rcde','Rpnde','Rtnde','Rpnie','Rtnie','Rte'))`，否则效应顺序一变就静默取错列。
4. 验收闸门：`p12_equivalence` 的 `checks[[1]]` 现在拿 `fast` 比 `old_point['Delta_OR']`，在 §2.3 替换源之后这条仍成立且有鉴别力（两值独立来源）；建议**保留**并把容差 `1e-8` 写进 `EQUIVALENCE.rds`（已写）同时记录两侧数值，便于复核。

---

## 3. FEAS_031 的 TNIE 点估计**不稳定于模拟种子**

**已证实。** 同一规格、同一数据，四次独立计算 TNIE：

| 来源 | FEAS_031 | FEAS_041 |
|---|---|---|
| native `effect.pe`（发表值） | 0.999271478272025 | 1.00039756153135 |
| `bootstrap_t0` 网格 | 0.999422286830433 | 1.00039756526310 |
| `point_75112346` | 0.999958986281993 | 1.00039758863627 |
| `point_75112347` | 1.000187652354040 | 1.00039760127102 |

（后两个种子来自 `shared_bootstrap_diagnostic.R:104`，`for (extra_seed in c(75112346L,75112347L))`。）

- FEAS_031：种子间极差 `9.16e-04`，而 `|估计值 − 1| = 7.29e-04` → **极差/效应 = 1.258**，且四个值**不在 1 的同一侧**（0.9993、0.9994、0.99996、1.00019）。即在当前模拟分辨率下，这个中介效应的**方向不被数据确定**。极差/bootstrap SE = 0.407。
- FEAS_041：极差 `3.97e-08`，极差/效应 ≈ 0.000，四值同侧。无此问题。

两者差异与 `mreg` 有关（031 为 `logistic`，041 为 `linear`），`estimation='imputation'` 下中介需被模拟抽取——**机制待核**，请在原生会话用同一 spec 改变 `mreg` 做一次对照后再写入文稿。

对结论的影响有限但必须披露：FEAS_031 的 `p_exploratory(TNIE) = 0.743`，本来就不显著，所以**不改变任何显著性判定**；但已发表表格把点估计写到 `0.999271478272025` 这个精度，而第 4 位小数就被种子噪声吞掉。

**建议**：对 `mreg='logistic'` 的比值规格（注册表计数：`(logistic, logistic)` 30 个），点估计报告精度降到噪声量级以上，或在 worker 里对点估计做 K 次重复取平均并保存 K 个值；不要只凭一次 `effect.pe`。

---

## 4. 两个 spec 走了**不同的准入闸门**

**已证实。**

- `verify_B1000_v1/FEAS_031/driver.R:13` → `worker.R`，其 `:22-23` 断言 `spec_id %in% support$specifications` **且** `identical(support$any_probability_outside_001_099, FALSE)`
- `verify_B1000_v1/FEAS_041/driver.R:13` → `worker_continuous.R`，其 `:22` **只**断言 `spec_id %in% support$specifications`

FEAS_041 的 `support_evidence` 指向 `continuousM_adjudication_v2/RESULT.json`，该文件**没有** `any_probability_outside_001_099` 这个键（字节级 grep 命中 0；非空对照：FEAS_031 的 `binary_expanded_support_v1/RESULT.json` 命中 1）。它改用另一套判据：`max_mean_tail = 0.000662139671811243`、`max_individual_tail = 0.0270459311436912`，并自记 `causal_identification_verified: false`、`review_mode: 'solo_self_review_with_prior_Claude_report'`、`preregistered_threshold: false`。

即：**FEAS_041 的端点概率界从未按 031 的口径验证过**，它过的是尾概率口径。两者都写进同一张 B1000 结果表时，必须注明准入判据不同；否则「同族同口径」是未经验证的声明。三个 `ADMISSION.json` 的 `sha_match` 本轮实测全部为 True，所以这不是篡改，是**两条闸门本身不同**。

---

## 5. M 条件支持：FEAS_046 镜像**未被覆盖**，且镜像不是简单取负

**已证实。** `diagnose_relative_bootstrap_support_v1.R:18`：

```r
reg <- reg[reg$m=='self_relative_gap_diff',]; stopifnot(nrow(reg)==15L)
```

只覆盖 15 个 self-gap 规格。实测该目录 15 个 per-spec CSV，`FEAS_041` 在内、`FEAS_046` **不在**（spouse-gap 同样 15 个规格全部无诊断）。

常见反驳是「`dm_spouse_rel = -dm_self_rel`（`20260904_basic_mechanism_v6.R:394`），镜像自动成立」。**这个推理在本脚本里不成立**：支持区间在 `:33` 构造为

```r
base <- z$self_sat_begin[idx] - z$spouse_sat_begin[idx]; lo <- -4-base; hi <- 4-base
```

`base` 用的是 **self − spouse**。对 spouse 镜像，正确的基线是 `spouse_sat_begin - self_sat_begin = -base`，于是 `lo' = -4+base`、`hi' = 4+base`。除 `base=0` 外 `[lo,hi] ≠ [lo',hi']`。所以 M 取负、mval 取负（FEAS_046 的 `mval1=-1`，与 FEAS_041 的 `mval1=1` 对称）之后，**落界判定并不自动镜像**。

041/046 其余镜像属性**已证实一致**：同样本（`sample_sha256` 均 `fb71bce2db3c…`）、同 `equivalent_m_family='relative_gap_sign_pair'`、同 n=12564/3149 簇。

**建议**：把 `:18` 的过滤改成 `m %in% c('self_relative_gap_diff','spouse_relative_gap_diff')`、断言 `nrow==30`，并在 `:33` 按 spec 的 `m` 选择 `base` 的符号；或者显式给出「镜像等价」的证明再豁免。**不建议**按 `-dm_self_rel` 直接豁免。

---

## 6. 23 项控制的时间属性：`_begin` 后缀**不是**可靠判据

**已证实。** `baseline_adjustment.R:2-7` 的 23 项中，19 项带 `_begin`，另 4 项是 `period_fe`、`baseline_support_ihs`、`baseline_actor_income_ihs`、`baseline_partner_income_ihs`（后三者由期初值构造，如 `20260904_basic_mechanism_v6.R:399`：`baseline_support_ihs = asinh(support_real_begin)`）。

但权威说明指出 `dwm_begin` **含区间之后的信息**——`pro_claude_v4_consensus_20261005_v1/NLM_ANSWER.md:107`：

> 控制变量 `COV23` 中的 `dwm_begin` 包含了 2016–2022 年四波累计支持（含区间之后的信息），**必须从主设定中剔除**（形成 22 个协变量的 `COV22`），仅在 R1 历史定义对照中使用

即带 `_begin` 后缀的变量可以携带后处理信息。**待核**：除 `dwm_begin` 外，是否还有其他 `_begin` 项隐含跨波累计（`lifetime_begin`、`total_debts_begin` 是我认为最该先查的两项，但本轮**没有**查到其构造源码，不下结论）。

### 一条超出本任务 scope 但必须上报的事实

注册表 150 个规格的 `adjustment` 列**全部**是 `fixed23_baseline`（实测分布 `{'fixed23_baseline': 150}`），`time_structure` 全部是 `concurrent_two_year_changes`。也就是说 **dwm 污染覆盖整个 150 规格族，不只是 P1/P2 这两个**。本任务只授权审查 031/041；但「去 dwm 修订」若只对 2 个规格做，剩余 148 个已发表的 B200/B1000 数值仍带同一污染。这属于监督方的范围裁定，我只报告计数。

---

## 7. 抽样与配对（已证实，无缺陷）

- `freeze_sampling_plan.R:23`：`draws <- replicate(B, sample(clusters, length(clusters), replace=TRUE))`，`clusters` 是**全局 3212 簇**（`:14` 断言），screen/verify 两条独立流（种子 202610052/202610053，`:35` 断言两者不相等）。
- 因此每个 spec 的每次抽样行数**随机变动**，这是设计而非缺陷：`mapping_validation.csv` 实测 FEAS_031 verify `min_n=9490 / max_n=10236`（n=9879），FEAS_041 `12137/13010`（n=12564）。
- 重复抽中同簇时全部成员重复带入（`worker.R:43` 的 `unlist(map[match(...)])`；`p12_self_test:138-139` 对此有合成断言）。
- `p12_prepare:29-33` 逐项重建索引并断言 `identical(idx, inp$actual_indices)` 与 `identical(plan$replicate_seeds, inp$replicate_seeds)`——**这是原 draw 配对的正确做法**，修好 §2 的路径后这条闸门有效。
- `repeat_diagnostics.csv` 两个 spec 均 1000 行、`valid=1000`、`grids` 1000 个 bootstrap 文件齐全、无缺失无非有限值（实测 `missing=0 nonfinite=0`）。

---

## 8. 待核清单（需原生 R 会话或监督方裁定）

1. `cmest_full.rds`（031/041 各一份，共约 316 MB）是否需要重建？重建等于重跑 B1000，与「不重跑旧 B1000」冲突；我的建议是**不重建**，按 §2.3 换源。请裁定。
2. §3 的 MC 噪声机制（`mreg='logistic'` 是否为根因）需一次对照实验确认。
3. §6 中除 `dwm_begin` 外其他 `_begin` 项的真实时间跨度，需回到 predata/问卷波次核。
4. §4 两条准入闸门的差异是否接受；若接受，结果表需注明。
5. §6 末尾的族范围问题（148 个其他规格）。

## 9. 本轮未做

未运行 R 模型、未 source 任何生产脚本进入拟合、未改共享代码/数据/原结果、未调用 UI/NLM/GitHub、未扩规格、未换种子、未重发旧 callback。两次只读 R 探针仅用于读取 RDS 结构与比对 `est.gformula` 函数体，未拟合、未写盘到共享目录。所有写入限于本 artifact root。
