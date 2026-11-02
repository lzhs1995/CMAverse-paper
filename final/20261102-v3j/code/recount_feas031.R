#!/usr/bin/env Rscript
# 只读取冻结数据并重计描述性构成；不拟合模型、不生成重抽样、不写原研究目录。
local({
  task <- "/Users/lzhs/Documents/cnm/tasks/01_R_analysis/handoff/cmaverse-v3j-audit-20261102"
  root <- "/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927"
  search <- file.path(root, "next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1")
  dir.create(file.path(task, "results"), showWarnings = FALSE, recursive = TRUE)
  cat("阶段：读取原候选构造与冻结样本成员\n"); flush.console()
  e <- new.env(parent = baseenv())
  sys.source(file.path(search, "candidate_data.R"), envir = e)
  members <- readRDS(file.path(search, "feasible_population_v1/sample_membership.rds"))
  specs <- read.csv(file.path(search, "feasible_population_v1/specifications.csv"))
  entry <- members[["FEAS_031"]]
  stopifnot(!is.null(entry$row_index), !anyDuplicated(entry$row_index))
  d <- e$z[entry$row_index, , drop = FALSE]
  stopifnot(!anyNA(d$m_self_rel))
  transition <- d[d$m_self_rel == 1, , drop = FALSE]
  stopifnot(!anyNA(transition$dm_self_abs), !anyNA(transition$dm_spouse_abs))
  up <- transition$dm_self_abs > 0
  down <- transition$dm_spouse_abs < 0
  count <- c(sum(up), sum(down), sum(!up & down), sum(up & down), sum(up & !down), sum(!up & !down))
  result <- data.frame(
    category = c("self_up_marginal", "spouse_down_marginal", "self_not_up_spouse_down", "self_up_spouse_down", "self_up_spouse_not_down", "neither"),
    numerator = count, denominator = nrow(transition),
    percent = 100 * count / nrow(transition),
    sample = "FEAS_031_frozen_complete_case", unit = "dyad_interval_records"
  )
  stopifnot(sum(result$numerator[3:6]) == nrow(transition), result$numerator[6] == 0)
  # 容斥只核对由微观数据所得整数；不从舍入百分比猜测分母或交集。
  stopifnot(result$numerator[1] + result$numerator[2] - result$numerator[4] == nrow(transition))
  write.csv(result, file.path(task, "results/FEAS031_RECOUNT_V3J.csv"), row.names = FALSE, na = "")
  sample <- data.frame(
    frozen_intervals = nrow(e$z), complete_case_intervals = nrow(d),
    complete_case_unique_dyads = length(unique(d$dyad_id)),
    transition_intervals = nrow(transition), transition_unique_dyads = length(unique(transition$dyad_id)),
    transition_missing_differences = sum(is.na(transition$dm_self_abs) | is.na(transition$dm_spouse_abs))
  )
  write.csv(sample, file.path(task, "results/FEAS031_SAMPLE_COUNTS_V3J.csv"), row.names = FALSE)
  cat("样本计数：\n"); print(sample, row.names = FALSE)
  cat("实际分子、分母：\n"); print(result, row.names = FALSE)
  cat("候选规格字段：", paste(names(specs), collapse = ", "), "\n")
  cat("原始评分字段：", paste(grep("sat|m_self|m_spouse|dm_", names(d), value = TRUE), collapse = ", "), "\n")
  cat("验证：整数构成穷尽且互斥；模型重估0；bootstrap重跑0。\n")
  print(sessionInfo())
})
