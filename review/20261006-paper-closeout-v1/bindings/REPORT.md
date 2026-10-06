# 冻结统计结果与来源绑定核验

状态：**PASS**。UTC：2026-10-06T14:21:56.384496+00:00。核验项：12。

本轮独立重算冻结 CSV 的检验算术，并新鲜核对 288 个源文件的 SHA256 与字节数。
120 份 execution_inputs.rds 合计 197,603,909 字节；120 份 METRICS.rds 同时与原 proof 和原 R 审计绑定。
原 R 对共同簇计划、实际行索引、replicate seeds 的核验沿用已接受的 native job d128f101；本轮没有重做 R 索引审计或模型拟合。

| 核验 | 结果 | 说明 |
|---|---|---|
| SOURCE_FILE_HASHES | PASS | 288 frozen source files match saved SHA256 and bytes; pins never refreshed. |
| HISTORICAL_COVERAGE_AND_NATIVE_RECEIPT | PASS | 150 registered / 120 estimable / 240 B200 targets; accepted native job d128f101 retained. |
| ACTUAL_120_EXECUTION_INPUTS | PASS | Fresh whole-file hashes for 120 actual execution_inputs.rds and 120 METRICS.rds; accepted R row-index/seed audit reused, not rerun. |
| RESULT_TABLE_MANIFEST_AND_PROVENANCE | PASS | 8 data tables + version table; every row has a valid pinned source path/hash/bytes and row locator. |
| CANDIDATE_DEFINITION_MAPPING | PASS | Both candidate codes, fixed contrasts, N/clusters, old adjustment and timing caveat match the saved registry; source transforms pinned. |
| HISTORICAL_B200_INDEPENDENT_ARITHMETIC | PASS | Recomputed 240 SDs/raw centered p values, two 120-target RW families and all-240 RW from the 200×240 frozen matrix; no fits or new tests. |
| CANDIDATE_HISTORY_VERSION_SEPARATION | PASS | 20 rows retain B200 log-OR TNIE, B1000 OR TNIE, OR differences and interval-only rows separately; no p transplant. |
| PERIOD_AND_LOO_SUMMARIES | PASS | Four period diagnostics and all 2,939 + 3,149 leave-one-cluster point diagnostics reduce exactly to the saved summaries; no new per-period/LOO inference. |
| P3_COMPLETE_PAIRED_DRAWS_AND_DIAGNOSTICS | PASS | All 6,000 rows finite/complete; each of 2,000 replicates shares one hash across three components; 4,000 amount fits have saved convergence/full-rank evidence. R index identity is reused from accepted receipt. |
| P3_POINT_DIFFERENCES_AND_OMNIBUS | PASS | Three-state differences and both centered 2-df quadratic tail counts reproduced from frozen paired draws; no new adjacent-contrast p values. |
| SIX_TEST_BH_BY_AND_N1_PRESERVATION | PASS | Six actual raw p values reproduce BH/BY; all original N1 coefficients, SE, CI, raw p and within-four q preserved. Only final six-family fields filled. |
| SCOPE_LIMITS | PASS | No fitting, R execution, new hypotheses, microdata copies, UI, publication, queue or broker mutation by this verifier. |

解释边界：B200 搜索校正只属于原模型；历史 B1000 原始 p 与百分位区间单列；去 dwm 的中心化区间和配对变化没有新增 p。TNIE 的 log-OR、OR 和配对 OR 差分别标注。

FEAS_031/041 的原始显著修饰线索继续保留，不能视为校正后确认。P3 原金额/封顶的整体 p 分别为 0.131934032983508 / 0.079960019990005。新六项族 BH/BY 在 0.05 均无拒绝。

分期和逐簇删除为点诊断；N1 是人际/个人内关联，不自动等于婚姻满意度中介或调节。共同抽样和算术一致性不证明一般零假设校准。

结果表在相邻 results/，每行携带源路径、SHA256、字节数和定位键。RESULT_VERSION_TABLE.csv 固定八张内容表；OUTPUT_MANIFEST.json 固定本轮全部绑定与核验文件。

本验收不包含 Word/PDF 原生验收、同版 NLM 终审和 GitHub 发布。
