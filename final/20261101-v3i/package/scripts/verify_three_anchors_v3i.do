* ==============================================================================
* Script: verify_three_anchors_v3i.do
* Purpose: Cross-verify the Three Statistical Anchors for V3i in Stata 19.5 MP
*          and produce a machine-readable Stata verification log.
* ==============================================================================
version 18.0
clear all
set more off

local basedir "/Users/lzhs/Documents/cnm/tasks/01_R_analysis/handoff/cmaverse-v3i-progression-20261101"

* 1. Load R-extracted Three Statistical Anchors table (27 rows)
import delimited using "`basedir'/results/THREE_STATISTICAL_ANCHORS_V3I.csv", varnames(1) encoding("UTF-8") clear
destring ci_low ci_high ci_half_width max_abs_bound p_raw q_adjusted, ignore("NA") replace
describe
list anchor_id anchor_group model_or_chain estimand estimate ci_low ci_high ci_half_width max_abs_bound q_adjusted, noobs abbreviate(22)

count
assert r(N) == 27

* Verify Anchor 1: AR-S additive interaction IC-RD = -8.76, q = 0.032
summarize estimate if model_or_chain == "AR-S (Model 5)"
assert abs(r(mean) - (-8.76)) < 1e-4

* Verify Anchor 2: Tightly bounded null across New 14 probability mediation chains (max_abs_bound <= 0.3188 pp)
summarize max_abs_bound if anchor_group == "New14_Prob_Mediation"
display "New14_Prob_Mediation max_abs_bound (percentage points): " %8.4f r(max)
assert r(max) <= 0.3189

* Verify Anchor 2: Historical 8 chains and Post-Selection no-dwm TNIE OR bounds
summarize ci_half_width if anchor_group == "PostSelection_NoDwm_TNIE"
display "PostSelection_NoDwm_TNIE max CI half-width (OR): " %8.4f r(max)
assert r(max) <= 0.0051

* 2. Load FEAS_031 Asymmetry Decomposition table (5 rows)
import delimited using "`basedir'/results/FEAS031_ASYMMETRY_DECOMPOSITION_V3I.csv", varnames(1) encoding("UTF-8") clear
describe
list transition_component percentage theoretical_meaning, noobs abbreviate(28)

count
assert r(N) == 5

* Verify overlap decomposition: 28.35% + 88.01% - 16.36% = 100.00%
* And disjoint partition: 71.65% (pure spouse decrease) + 16.36% (overlap) + 11.99% (pure self increase) = 100.00%
scalar pct_self_up_any = percentage[1]
scalar pct_spouse_down_any = percentage[2]
scalar pct_pure_spouse_down = percentage[3]
scalar pct_overlap = percentage[4]
scalar pct_pure_self_up = percentage[5]

scalar pct_union = scalar(pct_self_up_any) + scalar(pct_spouse_down_any) - scalar(pct_overlap)
scalar pct_partition = scalar(pct_pure_spouse_down) + scalar(pct_overlap) + scalar(pct_pure_self_up)

display "FEAS_031 Self Up Any (%): " %6.2f scalar(pct_self_up_any)
display "FEAS_031 Spouse Down Any (%): " %6.2f scalar(pct_spouse_down_any)
display "FEAS_031 Pure Spouse Down (%): " %6.2f scalar(pct_pure_spouse_down)
display "FEAS_031 Overlap (%): " %6.2f scalar(pct_overlap)
display "FEAS_031 Pure Self Up (%): " %6.2f scalar(pct_pure_self_up)
display "FEAS_031 Union (%): " %6.2f scalar(pct_union)
display "FEAS_031 Partition Sum (%): " %6.2f scalar(pct_partition)

assert abs(scalar(pct_self_up_any) - 28.35) < 1e-4
assert abs(scalar(pct_spouse_down_any) - 88.01) < 1e-4
assert abs(scalar(pct_pure_spouse_down) - 71.65) < 1e-4
assert abs(scalar(pct_overlap) - 16.36) < 1e-4
assert abs(scalar(pct_pure_self_up) - 11.99) < 1e-4
assert abs(scalar(pct_union) - 100.00) < 1e-4
assert abs(scalar(pct_partition) - 100.00) < 1e-4

display "STATA_ANCHORS_VERIFICATION_STATUS: PASS"
exit, clear
