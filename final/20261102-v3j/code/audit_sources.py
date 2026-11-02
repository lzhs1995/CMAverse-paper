#!/usr/bin/env python3
"""从冻结 CSV 自动提取完整结果与来源；不拟合或重抽样，不覆盖历史输出。"""
from pathlib import Path
import csv
import hashlib
import json
import math
import os
from datetime import datetime, timezone

TASK = Path(__file__).resolve().parents[1]
PROJECT = Path(os.environ.get("CMAVERSE_PROJECT_ROOT", "/Users/lzhs/Documents/cnm/tasks/01_R_analysis"))
R = PROJECT / "CMAverse_恢复工程_20260927"
S = R / "next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1"
H = PROJECT / "handoff/cmaverse-successor-01a19133-20261031/continuation_20261101_v4/delivery_r2/package"
B = R / "results/basic_v71/results"
OUT = TASK / "results"
EVIDENCE = TASK / "evidence"
OUT.mkdir(exist_ok=True)
EVIDENCE.mkdir(exist_ok=True)
sources, assertions, bindings = {}, [], {}


def digest(p):
    with Path(p).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


index_path = H / "provenance/SOURCE_INDEX.json"
for item in json.loads(index_path.read_text())["source_rows"]:
    for key in ("source", "historical_original_source"):
        if item.get(key):
            rec = item[key]
            bindings.setdefault(rec["path"], set()).add(rec["sha256"])


def pin(p, expected=None):
    p = Path(p)
    path = str(p)
    actual = digest(p)
    historical = sorted(bindings.get(path, set()))
    if expected:
        assert actual == expected, ("ORIGINAL_HASH_MISMATCH", path, expected, actual)
    if historical:
        assert actual in historical, ("INDEX_HASH_MISMATCH", path)
    old = sources.get(path)
    assert old is None or old["sha256"] == actual, ("SOURCE_CHANGED_DURING_READ", path)
    sources[path] = {"path": path, "bytes": p.stat().st_size, "sha256": actual,
                     "historical_expected_hashes": historical,
                     "verification": "historical_hash_match" if expected or historical else "current_bytes_pinned"}
    return sources[path]


def read(p):
    proof = pin(p)
    with Path(p).open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for number, row in enumerate(rows, 2):
        for key, value in list(row.items()):
            if key.endswith("_path") and value:
                hashkey = key[:-5] + "_sha256"
                if row.get(hashkey):
                    pin(value, row[hashkey])
        row["extracted_source_path"] = str(p)
        row["extracted_source_sha256"] = proof["sha256"]
        row["extracted_source_line"] = number
    return rows


def write(name, rows):
    assert rows
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with (OUT / name).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fields)
        writer.writeheader()
        writer.writerows(rows)
    print(name, "rows=", len(rows), flush=True)


def num(x):
    return None if x in (None, "", "NA", "NaN") else float(x)


pin(index_path)
base = read(B / "05_standardized_effects_actor_cluster.csv")
fdr = read(B / "13_bh_fdr_four_families.csv")
boot = read(B / "17_shared_actor_bootstrap_interaction_summary.csv")
samples = read(B / "02_chain_sample_summary.csv")
write("BASIC_ALL_STANDARDIZED_RESULTS_V3J.csv", base)
write("BASIC_FOUR_FDR_FAMILIES_V3J.csv", fdr)
write("BASIC_INTERACTION_BOOTSTRAP_V3J.csv", boot)
write("BASIC_CHAIN_SAMPLES_V3J.csv", samples)
write("BASIC_COMMON_RISK_ROLE_CONTRASTS_V3J.csv", read(B / "19_ar_common_risk_role_bootstrap_summary.csv"))
assert len(fdr) == 32 and len({r["chain"] for r in fdr}) == 8 and len(boot) == 8
for r in boot:
    corresponding = next(x for x in fdr if x["chain"] == r["chain"] and x["contrast"] == "IC_RD")
    assert math.isclose(float(r["delta_estimate"]), float(corresponding["estimate"]), abs_tol=1e-12)
assertions.append({"check": "basic_full_8_chains_and_4_families", "pass": True,
                   "inference_note": "FDR uses delta-method p; bootstrap intervals/p are separate columns/files, not interchangeable."})

history_path = R / "sources/extracted/v751_empirical/research/20260905_basic_regression_cmaverse_v7_4_1/cma/summary/formal_effects_all_chains_long.csv"
history = [x for x in read(history_path) if x["effect"] == "rRtnie"]
assert len({x["chain"] for x in history}) == 8
chains = []
for chain in sorted({x["chain"] for x in history}):
    group = [x for x in history if x["chain"] == chain]
    for r in group[1:]:
        for k in ("estimate", "conf_low", "conf_high", "p_value"):
            assert math.isclose(float(r[k]), float(group[0][k]), rel_tol=1e-11, abs_tol=1e-12)
    row = dict(group[0])
    row.update(duplicate_mval_rows=len(group), all_mval_values="|".join(x["mval"] for x in group),
               interpretation_scope="historical_modelized_OR; identification/algorithm limitations retained")
    chains.append(row)
write("HISTORICAL_ALL_EIGHT_TNIE_V3J.csv", chains)
assertions.append({"check": "historical_all_eight_not_selected_four", "pass": True,
                   "point_min": min(float(x["estimate"]) for x in chains),
                   "point_max": max(float(x["estimate"]) for x in chains),
                   "ci_envelope": [min(float(x["conf_low"]) for x in chains), max(float(x["conf_high"]) for x in chains)]})

primary = read(S / "pro_claude_v4_consensus_20261005_v1/probability_recovery_v1/B200_PRIMARY_SELECTION_CORRECTED.csv")
intervals = read(S / "manuscript_integration_v1/NEW14_PRIMARY_METRICS_v1.csv")
assert len(primary) == len(intervals) == 14
assert {r["test_id"] for r in primary} == {r["test_id"] for r in intervals}
for row in intervals:
    match = next(x for x in primary if x["test_id"] == row["test_id"])
    assert math.isclose(float(row["estimate"]), float(match["estimate"]), abs_tol=1e-10)
    row.update(analysis_kind="probability_mediation" if row["test_id"][0] in "CD" else "moderation",
               selection_source_path=match["extracted_source_path"], selection_source_sha256=match["extracted_source_sha256"],
               selection_source_line=match["extracted_source_line"], selection_eligible=match["eligible"],
               selection_reason=match["reason"])
    if row["analysis_kind"] == "probability_mediation":
        for native, display in (("estimate", "estimate_pp"), ("ci_low", "ci_low_pp"), ("ci_high", "ci_high_pp")):
            row[display] = 100 * float(row[native])
    row["inference_scope"] = "pointwise_unadjusted_B200; finite_sample_calibration_not_established; not_equivalence_test"
write("NEW14_COMPLETE_SPECIFICATIONS_V3J.csv", intervals)
write("NEW14_SELECTION_V3J.csv", primary)
mediation = [x for x in intervals if x["analysis_kind"] == "probability_mediation"]
assert len(mediation) == 6 and {x["test_id"] for x in mediation} == {"C1", "C2", "C3", "C4", "D1", "D2"}
write("SIX_PROBABILITY_MEDIATION_V3J.csv", mediation)
assertions.append({"check": "14_total_8_moderation_6_probability_mediation", "pass": True,
                   "probability_point_ci_envelope": [min(x["ci_low_pp"] for x in mediation), max(x["ci_high_pp"] for x in mediation)],
                   "all_six_intervals_include_zero": all(x["ci_low_pp"] <= 0 <= x["ci_high_pp"] for x in mediation),
                   "equivalence_or_simultaneous_exclusion_claim": False})

versions = read(H / "results/CANDIDATE_HISTORY_PANELS.csv")
write("CANDIDATES_ALL_VERSION_PANELS_V3J.csv", versions)
revised = []
for ident in ("FEAS_031", "FEAS_041"):
    rows = read(S / f"limited_followup_20261006_v1/p1_p2/readonly_summary_v1/{ident}_intervals.csv")
    for r in rows:
        r.update(model_version={"old": "original_with_dwm", "revised": "revised_no_dwm", "difference": "paired_revision_minus_original"}.get(r["version"], r["version"]),
                 p_raw="", adjusted_search_p="", note="No historical search-adjusted p transplanted to revised model or paired difference")
    revised.extend(rows)
write("CANDIDATES_PAIRED_INTERVALS_SEPARATE_VERSIONS_V3J.csv", revised)
assertions.append({"check": "with_dwm_and_no_dwm_inference_kept_separate", "pass": True})
for filename in ("N1_FOUR_WITH_FINAL_SIX_ADJUSTMENT.csv", "P3_THREE_STATE.csv", "P3_OMNIBUS.csv", "SIX_TEST_FAMILY.csv", "CANDIDATE_DEFINITIONS.csv", "CANDIDATE_LOO_SUMMARY.csv", "CANDIDATE_PERIOD_DIAGNOSTICS.csv"):
    write(filename.replace(".csv", "_V3J.csv"), read(H / "results" / filename))

for item in json.loads((EVIDENCE / "RECOUNT_INPUTS.json").read_text()):
    pin(item["path"], item["sha256"])
pin(TASK / "scripts/recount_feas031.R")
pin(TASK / "scripts/audit_sources.py")
rec = read(OUT / "FEAS031_RECOUNT_V3J.csv")
assert len(rec) == 6 and all(int(x["denominator"]) == 1559 for x in rec)
assertions.append({"check": "frozen_data_row_recount", "pass": True, "denominator": 1559,
                   "method": "Rscript; original_RDS_and_frozen_membership; no_model_refit"})
payload = {"at": datetime.now(timezone.utc).isoformat(), "scope": "full stated result sets; source extraction and descriptive recount; not full statistical reproduction", "checks": assertions,
           "sources": sorted(sources.values(), key=lambda x: x["path"]), "model_fits": 0, "bootstrap_runs": 0}
(EVIDENCE / "SOURCE_EXTRACTION_AUDIT.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"checks": assertions, "source_count": len(sources), "model_fits": 0, "bootstrap_runs": 0}, ensure_ascii=False, indent=2))
