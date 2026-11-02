#!/usr/bin/env Rscript
# 独立从四个原评分列重建相对状态、跃迁与本人/配偶差分；不拟合或重抽样。
local({
  task <- "/Users/lzhs/Documents/cnm/tasks/01_R_analysis/handoff/cmaverse-v3j-audit-20261102"
  search <- "/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1"
  e <- new.env(parent = baseenv())
  cat("读取冻结原评分与样本成员；原数据保持不变。\n"); flush.console()
  sys.source(file.path(search, "candidate_data.R"), envir = e)
  z <- e$z
  begin <- as.integer(z$self_sat_begin > z$spouse_sat_begin)
  end <- as.integer(z$self_sat_end > z$spouse_sat_end)
  rebuilt <- ifelse(is.na(begin) | is.na(end), NA_integer_,
                    ifelse(begin == 0, as.integer(end == 1), NA_integer_))
  delta_self <- z$self_sat_end - z$self_sat_begin
  delta_spouse <- z$spouse_sat_end - z$spouse_sat_begin
  same_values <- function(a,b) {
    stopifnot(length(a) == length(b), identical(is.na(a), is.na(b)))
    all(a[!is.na(a)] == b[!is.na(b)])
  }
  audit <- data.frame(
    check = c("relative_status_begin", "relative_status_end", "eligible_relative_transition", "self_score_difference", "spouse_score_difference"),
    pass = c(same_values(begin,z$self_rel_sat_status_begin), same_values(end,z$self_rel_sat_status_end),
             same_values(rebuilt,z$m_self_rel), same_values(delta_self,z$dm_self_abs), same_values(delta_spouse,z$dm_spouse_abs)),
    audited_intervals = nrow(z)
  )
  stopifnot(all(audit$pass))
  members <- readRDS(file.path(search,"feasible_population_v1/sample_membership.rds"))[["FEAS_031"]]$row_index
  rows <- members[which(rebuilt[members] == 1)]
  up <- delta_self[rows] > 0; down <- delta_spouse[rows] < 0
  count <- c(sum(up),sum(down),sum(!up & down),sum(up & down),sum(up & !down),sum(!up & !down))
  prior <- read.csv(file.path(task,"results/FEAS031_RECOUNT_V3J.csv"))
  stopifnot(nrow(prior) == length(count), all(prior$numerator == count), all(prior$denominator == length(rows)))
  write.csv(audit,file.path(task,"results/FEAS031_SCORE_REBUILD_CHECKS.csv"),row.names=FALSE)
  print(audit,row.names=FALSE)
  cat("原评分独立重建：完整案例",length(members),"；跃迁区间",length(rows),"；六个分子",paste(count,collapse=","),"\n")
  cat("与先前读取保存变量的重计全部一致；新模型0，新bootstrap0。\n")
  print(sessionInfo())
})
