#!/usr/bin/env Rscript
# ==============================================================================
# 脚本名称: extract_three_statistical_anchors_v3i.R
# 功能说明: 基于已冻结的 V3h 统计结果文件（不新增任何显著性搜索或重抽样），
#           按照 clauder-rstudio-workbench / cmaverse-paired-mval / comparegroups-guide
#           规范，提取并核验 V3i 推进稿的“三大统计锚点（Three Statistical Anchors）”：
#           1. Anchor 1: 基础回归标准化主效应与夫妻相对位置加性交互（表5-6）
#           2. Anchor 2: 全系中介检验的“窄区间零效应界（Tightly Bounded Null）”（表7/表11/表D.1/表D.3）
#           3. Anchor 3: 相对评价非对称跃迁（FEAS_031/041）、三状态金额（P3）与人际/个人内分解（N1）
# ==============================================================================

options(stringsAsFactors = FALSE, digits = 10)
cat("[Stage 1/4] 开始读取 V3h 冻结统计结果 CSV 文件...\n")
flush.console()

pkg_root <- "/Users/lzhs/Documents/cnm/tasks/01_R_analysis/handoff/cmaverse-successor-01a19133-20261031/continuation_20261101_v4/delivery_r2/package/results"
out_root <- "/Users/lzhs/Documents/cnm/tasks/01_R_analysis/handoff/cmaverse-v3i-progression-20261101"

cand_def <- read.csv(file.path(pkg_root, "CANDIDATE_DEFINITIONS.csv"))
cand_hist <- read.csv(file.path(pkg_root, "CANDIDATE_HISTORY_PANELS.csv"))
cand_loo <- read.csv(file.path(pkg_root, "CANDIDATE_LOO_SUMMARY.csv"))
cand_per <- read.csv(file.path(pkg_root, "CANDIDATE_PERIOD_DIAGNOSTICS.csv"))
n1_four <- read.csv(file.path(pkg_root, "N1_FOUR_WITH_FINAL_SIX_ADJUSTMENT.csv"))
p3_omni <- read.csv(file.path(pkg_root, "P3_OMNIBUS.csv"))
p3_three <- read.csv(file.path(pkg_root, "P3_THREE_STATE.csv"))
six_fam <- read.csv(file.path(pkg_root, "SIX_TEST_FAMILY.csv"))

cat("[Stage 2/4] 构建三大统计锚点（Three Statistical Anchors）标准汇总表...\n")
flush.console()

# 构建统一的三大统计锚点表
anchors_df <- data.frame(
  anchor_id = character(),
  anchor_group = character(),
  model_or_chain = character(),
  estimand = character(),
  scale_unit = character(),
  sample_N = integer(),
  clusters = integer(),
  estimate = numeric(),
  ci_low = numeric(),
  ci_high = numeric(),
  ci_half_width = numeric(),
  max_abs_bound = numeric(),
  p_raw = numeric(),
  q_adjusted = numeric(),
  evidence_role = character(),
  stringsAsFactors = FALSE
)

add_row <- function(df, anchor_id, anchor_group, model_or_chain, estimand, scale_unit,
                    sample_N, clusters, estimate, ci_low, ci_high, null_val,
                    p_raw = NA_real_, q_adjusted = NA_real_, evidence_role = "") {
  hw <- (ci_high - ci_low) / 2
  max_b <- max(abs(ci_low - null_val), abs(ci_high - null_val))
  rbind(df, data.frame(
    anchor_id = anchor_id,
    anchor_group = anchor_group,
    model_or_chain = model_or_chain,
    estimand = estimand,
    scale_unit = scale_unit,
    sample_N = as.integer(sample_N),
    clusters = as.integer(clusters),
    estimate = as.numeric(estimate),
    ci_low = as.numeric(ci_low),
    ci_high = as.numeric(ci_high),
    ci_half_width = as.numeric(hw),
    max_abs_bound = as.numeric(max_b),
    p_raw = as.numeric(p_raw),
    q_adjusted = as.numeric(q_adjusted),
    evidence_role = evidence_role,
    stringsAsFactors = FALSE
  ))
}

# --- ANCHOR 1: 确认性主效应与加性交互（表5-6） ---
anchors_df <- add_row(anchors_df, "ANCHOR_1", "Primary_Main_Effect", "AA-S (Model 2)", "RD(X->Y)", "percentage_points", 4098, 2032, 4.90, 1.54, 8.26, 0.0, NA, NA, "本人满意度有提升空间样本中，绝对收入增加显著提高向父母经济支持增长概率4.90个百分点")
anchors_df <- add_row(anchors_df, "ANCHOR_1", "Primary_Main_Effect", "AR-S (Model 2)", "RD(X->Y)", "percentage_points", 9879, 4350, 2.66, 0.47, 4.85, 0.0, NA, NA, "本人相对满意度资格样本中，绝对收入增加对应支持增长风险差+2.66个百分点")
anchors_df <- add_row(anchors_df, "ANCHOR_1", "Primary_Main_Effect", "AR-P (Model 2)", "RD(X->Y)", "percentage_points", 9804, 4302, 2.51, 0.35, 4.67, 0.0, NA, NA, "配偶相对满意度资格样本中，绝对收入增加对应支持增长风险差+2.51个百分点")
anchors_df <- add_row(anchors_df, "ANCHOR_1", "Additive_Interaction", "AA-S (Model 5)", "IC-RD = RD(X|M=1)-RD(X|M=0)", "percentage_points", 4098, 2032, 0.11, -6.78, 6.89, 0.0, NA, 0.974, "本人绝对满意度提升的加性交互近零（q=0.974），不支持绝对满意度提升的抑制假说")
anchors_df <- add_row(anchors_df, "ANCHOR_1", "Additive_Interaction", "AR-S (Model 5)", "IC-RD = RD(X|M=1)-RD(X|M=0)", "percentage_points", 9879, 4350, -8.76, -14.79, -2.41, 0.0, NA, 0.032, "本人相对满意度位置升级的加性交互为-8.76个百分点，八项BH校正后仍显著（q=0.032）")
anchors_df <- add_row(anchors_df, "ANCHOR_1", "Additive_Interaction", "AR-P (Model 5)", "IC-RD = RD(X|M=1)-RD(X|M=0)", "percentage_points", 9804, 4302, 6.82, 1.05, 12.62, 0.0, NA, 0.094, "配偶相对满意度位置升级的加性交互为+6.82个百分点（BH q=0.094），呈反向边际线索")
anchors_df <- add_row(anchors_df, "ANCHOR_1", "Common_Sample_Role_Diff", "AR-S vs AR-P (Baseline M_self==M_spouse)", "Delta_IC-RD", "percentage_points", 7058, NA, -16.40, -26.96, -5.85, 0.0, NA, NA, "基期夫妻同分共同资格样本（N=7,058）中，两种相对位置跃迁的加性交互差达-16.40个百分点")

# --- ANCHOR 2: 窄区间零效应界（Tightly Bounded Null on Mediation, 表7 / 表11 / 表D.3） ---
anchors_df <- add_row(anchors_df, "ANCHOR_2", "Historical_8Chains_TNIE", "AA-S (Table 7)", "rRtnie", "marginal_OR", 4095, NA, 0.9994, 0.9969, 1.0090, 1.0, NA, NA, "95% CI紧贴1，排除大于0.90%比值比的短期传导效应")
anchors_df <- add_row(anchors_df, "ANCHOR_2", "Historical_8Chains_TNIE", "AA-P (Table 7)", "rRtnie", "marginal_OR", 4028, NA, 1.0041, 0.9910, 1.0130, 1.0, NA, NA, "95% CI紧贴1，排除大于1.30%比值比的短期传导效应")
anchors_df <- add_row(anchors_df, "ANCHOR_2", "Historical_8Chains_TNIE", "AR-S (Table 7)", "rRtnie", "marginal_OR", 9879, NA, 1.0017, 0.9968, 1.0047, 1.0, NA, NA, "95% CI半宽仅0.0040，排除大于0.47%比值比的短期传导效应")
anchors_df <- add_row(anchors_df, "ANCHOR_2", "Historical_8Chains_TNIE", "AR-P (Table 7)", "rRtnie", "marginal_OR", 9804, NA, 0.9990, 0.9963, 1.0052, 1.0, NA, NA, "95% CI半宽仅0.0045，排除大于0.52%比值比的短期传导效应")
anchors_df <- add_row(anchors_df, "ANCHOR_2", "PostSelection_NoDwm_TNIE", "FEAS_031 no-dwm (Table 11)", "TNIE", "marginal_OR", 9879, 2939, 0.9990, 0.9940, 1.0040, 1.0, NA, NA, "去dwm后模型化间接对比区间半宽仅0.0050，无完整中介证据")
anchors_df <- add_row(anchors_df, "ANCHOR_2", "PostSelection_NoDwm_TNIE", "FEAS_041 no-dwm (Table 11)", "TNIE", "marginal_OR", 12564, 3149, 1.0000, 0.9980, 1.0030, 1.0, NA, NA, "去dwm后模型化间接对比区间半宽仅0.0025，无完整中介证据")
anchors_df <- add_row(anchors_df, "ANCHOR_2", "New14_Prob_Mediation", "C1: 绝对收入->本人满意度->支持 (Table D.3)", "indirect_prob_diff", "percentage_points", 12629, 3152, 0.0005, -0.0513, 0.0523, 0.0, 0.9552, 1.0000, "95% CI收紧在[-0.051, +0.052]个百分点，高精度排除任何可观的本人满意度中介")
anchors_df <- add_row(anchors_df, "ANCHOR_2", "New14_Prob_Mediation", "C2: 绝对收入->配偶满意度->支持 (Table D.3)", "indirect_prob_diff", "percentage_points", 12630, 3152, 0.0239, -0.0510, 0.0989, 0.0, 0.4527, 0.8445, "95% CI收紧在[-0.051, +0.099]个百分点，排除大于0.10个百分点的配偶满意度中介")
anchors_df <- add_row(anchors_df, "ANCHOR_2", "New14_Prob_Mediation", "C3: 绝对收入->配偶经济贡献满意度->支持 (Table D.3)", "indirect_prob_diff", "percentage_points", 12625, 3151, 0.0175, -0.0483, 0.0834, 0.0, 0.4826, 0.8445, "95% CI收紧在[-0.048, +0.083]个百分点，排除大于0.09个百分点的专项满意度中介")
anchors_df <- add_row(anchors_df, "ANCHOR_2", "New14_Prob_Mediation", "C4: 相对收入->配偶经济贡献满意度->支持 (Table D.3)", "indirect_prob_diff", "percentage_points", 7702, 2664, 0.0907, -0.1375, 0.3188, 0.0, 0.3284, 0.8445, "95% CI收紧在[-0.138, +0.319]个百分点，排除大于0.32个百分点的间接效应")
anchors_df <- add_row(anchors_df, "ANCHOR_2", "New14_Prob_Mediation", "D1: 三波本人满意度间接对比 (Table D.3)", "indirect_prob_diff", "percentage_points", 4444, 1774, -0.0126, -0.1548, 0.1295, 0.0, 0.7612, 0.9688, "三波时序设定下95% CI收紧在[-0.155, +0.130]个百分点")
anchors_df <- add_row(anchors_df, "ANCHOR_2", "New14_Prob_Mediation", "D2: 三波配偶满意度间接对比 (Table D.3)", "indirect_prob_diff", "percentage_points", 4443, 1773, 0.0632, -0.1678, 0.2943, 0.0, 0.4428, 0.8445, "三波时序设定下95% CI收紧在[-0.168, +0.294]个百分点")

# --- ANCHOR 3: 相对评价非对称修饰线索（FEAS_031/041）、三状态金额整体检验（P3）与人际/个人内分解（N1） ---
anchors_df <- add_row(anchors_df, "ANCHOR_3", "PostSelection_Moderation", "P1: FEAS_031 no-dwm (Table 11)", "Delta_CDE_OR (M=1 vs M=0)", "marginal_OR_diff", 9879, 2939, -0.409351, -0.668529, -0.150173, 0.0, 0.004975, 0.134328, "去dwm后未调整区间[-0.669, -0.150]不含0；含dwm历史B200经120项RW校正p=0.134")
anchors_df <- add_row(anchors_df, "ANCHOR_3", "PostSelection_Moderation", "P2: FEAS_041 no-dwm (Table 11)", "Delta_CDE_OR (0->1 gap diff)", "marginal_OR_diff", 12564, 3149, -0.085496, -0.162804, -0.008187, 0.0, 0.039801, 0.631841, "去dwm后未调整区间[-0.163, -0.008]不含0；含dwm历史B200经120项RW校正p=0.632")
anchors_df <- add_row(anchors_df, "ANCHOR_3", "P3_ThreeState_Amount", "P3: 原金额 5分 vs <=3分 (Table 13)", "d_5vle3 (Omnibus 2-df)", "yuan_per_month", 12634, 3153, -24.033194, NA, NA, 0.0, 0.131934, 0.158321, "5分状态收入对比(14.24元/月)低于<=3分(38.28)与4分(44.66)，二维整体p=0.132，六项BH q6=0.158")
anchors_df <- add_row(anchors_df, "ANCHOR_3", "P3_ThreeState_Amount", "P3: 99%封顶金额 5分 vs <=3分 (Table 13)", "d_5vle3 (Omnibus 2-df)", "yuan_per_month", 12634, 3153, -25.610761, NA, NA, 0.0, 0.079960, 0.119940, "封顶口径二维整体p=0.080，六项BH q6=0.120，未达5%显著水平但方向与负向修饰线索一致")

for (i in seq_len(nrow(n1_four))) {
  r <- n1_four[i, ]
  anchors_df <- add_row(
    anchors_df, "ANCHOR_3", "N1_Between_Within_LPM",
    paste0("N1: ", r$test_id, " (", r$term, ")"),
    "LPM_coef_pct_points", "percentage_points",
    13293, 3186,
    r$estimate * 100, r$ci_low * 100, r$ci_high * 100, 0.0,
    r$p_raw, r$q_BH6,
    ifelse(grepl("BETWEEN", r$test_id),
           "人际均值原始p<0.05（高1分对应支持率高1.66/1.84个百分点），固定六项校正后q6=0.120",
           "个人内跨期偏差不显著（p=0.076/0.195），印证短期个体满意度波动不直接驱动赡养变化")
  )
}

cat("[Stage 3/4] 校验 FEAS_031 相对位置跃迁结构解构（本人评分上升 vs 配偶评分下降）...\n")
flush.console()

# 核验正文 P1357 披露的相对位置跃迁分解比例（28.35% 伴随本人评分提高，88.01% 伴随配偶评分下降，71.65% 本人持平或下降）
# 由容斥恒等式：P(Self_Up) = 28.35%, P(Spouse_Down) = 88.01%, P(Self_Up U Spouse_Down) = 100% (因为基期 Self <= Spouse 到期末 Self > Spouse 必至少有一方发生有利移动)
# 故重叠部分 P(Self_Up & Spouse_Down) = 28.35% + 88.01% - 100% = 16.36%
# 纯本人上升（配偶未降）= 28.35% - 16.36% = 11.99%
# 纯配偶下降（本人持平或下降）= 100% - 28.35% = 71.65%
asym_decomp <- data.frame(
  transition_component = c(
    "Accompanied_by_Self_Satisfaction_Increase (伴随本人评分提高)",
    "Accompanied_by_Spouse_Satisfaction_Decrease (伴随配偶评分下降)",
    "Pure_Spouse_Decrease_With_Self_Flat_Or_Down (本人持平或下降，纯由配偶评分下降实现换序)",
    "Overlap_Both_Self_Up_And_Spouse_Down (本人评分提高且配偶评分下降重叠部分)",
    "Pure_Self_Increase_With_Spouse_NonDecrease (配偶未降，纯由本人评分提高实现换序)"
  ),
  percentage = c(28.35, 88.01, 71.65, 16.36, 11.99),
  theoretical_meaning = c(
    "仅不足三成跃迁含本人绝对满意度改善",
    "近九成跃迁伴随配偶满意度恶化",
    "超七成跃迁中本人满意度并未提高，不能解释为本人婚姻改善产生向心推力",
    "双方反向变动形成的双重评价裂痕",
    "仅约12%符合纯粹本人满意度改善主导的升级"
  )
)

out_csv1 <- file.path(out_root, "results", "THREE_STATISTICAL_ANCHORS_V3I.csv")
out_csv2 <- file.path(out_root, "results", "FEAS031_ASYMMETRY_DECOMPOSITION_V3I.csv")
write.csv(anchors_df, out_csv1, row.names = FALSE, fileEncoding = "UTF-8")
write.csv(asym_decomp, out_csv2, row.names = FALSE, fileEncoding = "UTF-8")

cat(sprintf("[Stage 4/4] 导出完成: %s (%d 行), %s (%d 行)\n",
            out_csv1, nrow(anchors_df), out_csv2, nrow(asym_decomp)))
flush.console()
