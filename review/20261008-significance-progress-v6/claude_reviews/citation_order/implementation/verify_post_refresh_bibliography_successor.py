#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""最终 Refresh 后独立书目保全验收；只读 DOCX，不声称执行过原生 Refresh。"""
import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from xml.etree import ElementTree as ET
from zipfile import ZipFile

sys.dont_write_bytecode = True
from input_guards import strict_absolute_path, require_distinct_candidate

HERE = strict_absolute_path(__file__).parent
BASE = Path('/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1/limited_followup_20261006_v1/paper_closeout_after_numerical_v1')
EXTRACTOR = BASE / "private_actual_field_semantics_audit_v1/audit_actual_fields_readonly.py"
EXTRACTOR_SHA = "cc5e1d594c51b98230ecfe6ea396d0c37ae6fab200c722a7bbdd558f28b11d45"
MOTHER = BASE.parents[2] / "delivery/current_recovered_manuscript_20261005_v1/CMAverse_基础回归与八链结果恢复后_当前整合稿.docx"
MOTHER_SHA = "4f8cb6c2963c52efaf7cc1065110783ddefdc586785cce15f401d71e2787123d"
NATIVE = BASE / "native_readiness/native_citation_after_release_v5/native_saved_year_fixed.docx"
NATIVE_SHA = "f2582b306d164858d79e3441b5d7bb4dbd4bb776a54820c9c64d4dc1ce60831b"
WANG_URI = "http://zotero.org/users/9676737/items/HM4KAHLB"
REAL_OLD_ENTRY = "郑丹丹, 狄金华, 2017. 女性家庭权力、夫妻关系与家庭代际资源分配[J]. 社会学研究, 32(1): 171-192+245."


def ref(path, expected=None):
    p = strict_absolute_path(path)
    data = p.read_bytes()
    result = {"path": str(p), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    if expected is not None and result["sha256"] != expected:
        raise ValueError("PIN_MISMATCH:" + str(p))
    return result


def semantic_field(field):
    # 不将刷新产生的成员、指令或显示差异自动当成无害元数据。
    return {k: field[k] for k in ("story", "kind", "instruction", "display", "csl")}


def old_citation_order(old_fields, new_fields):
    # 旧 citationID 键控比较对顺序不敏感；此处按抽取器的 9 story 固定次序（story 名排序、story 内序号）
    # 比较旧 ID 的相对顺序与所在 story。新增引文（Wang）不参与，其插入位置不影响本谓词。
    old_seq = [(f["story"], f["csl"].get("citationID")) for f in old_fields]
    old_ids = {cid for _, cid in old_seq}
    new_seq = [(f["story"], f["csl"].get("citationID")) for f in new_fields if f["csl"].get("citationID") in old_ids]
    first_diff = next((i for i, (a, b) in enumerate(zip(old_seq, new_seq)) if a != b), None)
    if first_diff is None and len(old_seq) != len(new_seq):
        first_diff = min(len(old_seq), len(new_seq))
    return {"ok": len(old_ids) == len(old_seq) and old_seq == new_seq, "old_sequence": old_seq,
            "candidate_old_id_sequence": new_seq, "first_difference_index": first_diff}


def swap_citation_fields(blobs, audit, a, b):
    # 内存反例：交换两条真实旧引文域的完整指令与显示文本（可跨 story），不写出 DOCX。
    trees = {name: ET.fromstring(blob) for name, blob in blobs.items()}
    spans = {}
    for name, tree in trees.items():
        depth, current = 0, None
        for el in tree.iter():
            local = el.tag[len(audit.W):] if el.tag.startswith(audit.W) else None
            if local == "fldChar":
                typ = el.get(audit.W + "fldCharType")
                if typ == "begin":
                    depth += 1
                    if depth == 1:
                        current = {"story": name, "instr": [], "disp": [], "separated": False}
                elif typ == "separate" and depth == 1:
                    current["separated"] = True
                elif typ == "end":
                    if depth == 1 and "CSL_CITATION" in "".join(x.text or "" for x in current["instr"]):
                        inst = "".join(x.text or "" for x in current["instr"])
                        cid = json.loads(inst[inst.index("{"):].strip()).get("citationID")
                        spans.setdefault(cid, []).append(current)
                    depth -= 1
            elif depth == 1 and local == "instrText" and not current["separated"]:
                current["instr"].append(el)
            elif depth == 1 and local == "t" and current["separated"]:
                current["disp"].append(el)
    if len(spans.get(a, [])) != 1 or len(spans.get(b, [])) != 1 or not spans[a][0]["disp"] or not spans[b][0]["disp"]:
        raise ValueError("SWAP_TARGET_NOT_UNIQUE:" + str(a) + "," + str(b))
    sa, sb = spans[a][0], spans[b][0]
    texts = {k: ("".join(x.text or "" for x in s["instr"]), "".join(x.text or "" for x in s["disp"])) for k, s in (("a", sa), ("b", sb))}
    for span, (inst, disp) in ((sa, texts["b"]), (sb, texts["a"])):
        for group, value in ((span["instr"], inst), (span["disp"], disp)):
            group[0].text = value
            for extra in group[1:]:
                extra.text = ""
    return {name: ET.tostring(tree) for name, tree in trees.items()}, {sa["story"], sb["story"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--candidate-sha256", required=True)
    parser.add_argument("--mode", choices=("fixture_only", "final_file_semantics"), required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    candidate = strict_absolute_path(args.candidate)
    out = strict_absolute_path(args.out, kind="directory", allow_missing=True)
    same_reference = require_distinct_candidate(candidate, NATIVE, args.mode)
    if out == HERE or HERE not in out.parents or out.exists():
        raise ValueError("OUTPUT_MUST_BE_NEW_CHILD_OF_EXCLUSIVE_DIRECTORY")
    refs = {
        "extractor": ref(EXTRACTOR, EXTRACTOR_SHA),
        "mother": ref(MOTHER, MOTHER_SHA),
        "native_reference": ref(NATIVE, NATIVE_SHA),
        "candidate": ref(candidate, args.candidate_sha256),
        "verifier": ref(__file__),
        "input_guards": ref(HERE / "input_guards.py"),
    }
    spec = importlib.util.spec_from_file_location("readonly_full_field_audit", EXTRACTOR)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    before, native, after = map(audit.inventory, (MOTHER, NATIVE, candidate))
    result = audit.compare(before, after, WANG_URI)
    old_entries, native_entries, final_entries = map(audit.bib_entries, (before, native, after))
    old_fields, new_fields = map(audit.citations, (before, after))
    new_by_id = {f["csl"].get("citationID"): f for f in new_fields}
    old_field_differences = []
    for old in old_fields:
        cid = old["csl"].get("citationID")
        new = new_by_id.get(cid)
        if new is None or semantic_field(old) != semantic_field(new):
            old_field_differences.append({"citationID": cid, "before": semantic_field(old),
                                          "after": semantic_field(new) if new is not None else None})
    checks = dict(result["fail_closed_checks"])
    checks.update({
        "source_mother_has_24_full_bibliography_entries": len(old_entries) == 24,
        "genuine_native_has_25_full_bibliography_entries": len(native_entries) == 25,
        "candidate_has_25_full_bibliography_entries": len(final_entries) == 25,
        "original_24_entries_exact_and_ordered": final_entries[1:] == old_entries,
        "candidate_full_25_entries_exactly_equal_native": final_entries == native_entries,
        "original_22_full_citation_fields_exact": len(old_fields) == 22 and not old_field_differences,
        "candidate_23_citation_fields": len(new_fields) == 23,
        "all_fields_instruction_and_display_equal_genuine_native": audit.snapshot(after) == audit.snapshot(native),
        "all_nine_story_parts_retained": len(before["stories"]) == 9 and set(before["stories"]) == set(after["stories"]),
    })
    order = old_citation_order(old_fields, new_fields)
    checks["original_22_citation_ids_relative_order_and_story_exact"] = len(old_fields) == 22 and order["ok"]

    # 旧引文交换负控：先在真实候选上交换两条旧引文（story 内与跨 story 各一），只在内存中重解析。
    with ZipFile(candidate) as z:
        story_blobs = {n: z.read(n) for n in after["stories"]}
    swap_controls = {}
    for label, pair in (("within_document_story", (old_fields[0]["csl"]["citationID"], old_fields[1]["csl"]["citationID"])),
                        ("cross_document_footnotes", (old_fields[0]["csl"]["citationID"], old_fields[-1]["csl"]["citationID"]))):
        control = {"pair": list(pair), "mutated_docx_written": False, "pass": False}
        try:
            mutated, touched = swap_citation_fields(story_blobs, audit, *pair)
            swapped = copy.deepcopy(after)
            for name in touched:
                swapped["stories"][name] = audit.parse_story(mutated[name], name)
        except ValueError as exc:
            control["error"] = str(exc)
            swap_controls[label] = control
            continue
        sw_fields = audit.citations(swapped)
        sw_by_id = {f["csl"].get("citationID"): f for f in sw_fields}
        sw_order = old_citation_order(old_fields, sw_fields)
        positions = [[f["csl"].get("citationID") for f in new_fields].index(cid) for cid in pair]
        expected = [f["csl"].get("citationID") for f in new_fields]
        expected[positions[0]], expected[positions[1]] = expected[positions[1]], expected[positions[0]]
        id_keyed_same_story = all(semantic_field(old)["story"] == sw_by_id[old["csl"]["citationID"]]["story"] for old in old_fields)
        control.update({
            "touched_stories": sorted(touched),
            "reparsed_id_sequence_is_exact_swap": [f["csl"].get("citationID") for f in sw_fields] == expected,
            "swapped_fields_carry_full_original_semantics": all(
                {k: v for k, v in semantic_field(sw_by_id[cid]).items() if k != "story"}
                == {k: v for k, v in semantic_field(new_by_id[cid]).items() if k != "story"} for cid in pair),
            "base_compare_has_no_violations": not audit.compare(before, swapped, WANG_URI)["blocking_violations"],
            "id_keyed_original_22_fields_exact": not [o for o in old_fields if semantic_field(o) != semantic_field(sw_by_id[o["csl"]["citationID"]])],
            "id_keyed_story_unchanged": id_keyed_same_story,
            "order_predicate_rejects": not sw_order["ok"],
            "order_first_difference_index": sw_order["first_difference_index"],
        })
        # story 内交换：键控检查须仍全过（证明缺口真实存在），仅新谓词拒绝；跨 story：键控 story 检查也应拒绝。
        gap_shape = (control["base_compare_has_no_violations"] and control["id_keyed_original_22_fields_exact"]) if label.startswith("within") \
            else (not control["id_keyed_story_unchanged"] and not control["id_keyed_original_22_fields_exact"])
        control["pass"] = (control["reparsed_id_sequence_is_exact_swap"] and control["swapped_fields_carry_full_original_semantics"]
                           and control["order_predicate_rejects"] and gap_shape)
        swap_controls[label] = control
    checks["old_citation_swap_detected_by_order_predicate"] = len(swap_controls) == 2 and all(c["pass"] for c in swap_controls.values())

    # 实际旧文献删除负测：只改内存中的真实候选内容，不写出、更不修改 DOCX。
    with ZipFile(candidate) as z:
        tree = ET.fromstring(z.read("word/document.xml"))
    matched = []
    for paragraph in tree.iter(audit.W + "p"):
        if "".join(t.text or "" for t in paragraph.iter(audit.W + "t")) == REAL_OLD_ENTRY:
            matched.append(paragraph)
    negative = {"target": REAL_OLD_ENTRY, "matched_real_paragraph_count": len(matched), "mutated_docx_written": False}
    if len(matched) == 1:
        for t in matched[0].iter(audit.W + "t"):
            t.text = ""
        altered = copy.deepcopy(after)
        altered["stories"]["word/document.xml"] = audit.parse_story(ET.tostring(tree), "word/document.xml")
        neg_result = audit.compare(before, altered, WANG_URI)
        negative.update({
            "triggered_violation": "old_bibliography_entries_preserved_normalized" in neg_result["blocking_violations"],
            "exact_removed_map": neg_result["bibliography_removed_normalized"] == {audit.compact(REAL_OLD_ENTRY): 1},
            "citation_fields_and_members_unchanged": [semantic_field(f) for f in audit.citations(after)] == [semantic_field(f) for f in audit.citations(altered)],
            "all_citation_count_checks_still_pass": neg_result["fail_closed_checks"]["citation_field_count_increased_by_one"],
            "bibliography_entries_lost": len(final_entries) - len(audit.bib_entries(altered)),
            "negative_result": neg_result,
        })
    negative["pass"] = all(negative.get(k) is True for k in ("triggered_violation", "exact_removed_map",
                                                           "citation_fields_and_members_unchanged", "all_citation_count_checks_still_pass")) and negative.get("bibliography_entries_lost") == 1
    checks["real_old_entry_deletion_detected_while_citations_unchanged"] = negative["pass"]
    # 纯重排负控：只交换两条真实旧书目文本，集合/计数/引文保持不变。
    reordered = copy.deepcopy(after)
    bibliographies = [f for f in audit.fields(reordered) if "bibliography_paragraphs" in f]
    reorder = {"mutated_docx_written": False, "pass": False}
    if len(bibliographies) == 1 and len(bibliographies[0]["bibliography_paragraphs"]) == 25:
        entries = bibliographies[0]["bibliography_paragraphs"]
        entries[1]["text"], entries[2]["text"] = entries[2]["text"], entries[1]["text"]
        reordered_entries = audit.bib_entries(reordered)
        reordered_result = audit.compare(before, reordered, WANG_URI)
        reorder_checks = {
            "candidate_has_25_full_bibliography_entries": len(reordered_entries) == 25,
            "original_24_entries_exact_and_ordered": reordered_entries[1:] == old_entries,
            "candidate_full_25_entries_exactly_equal_native": reordered_entries == native_entries,
        }
        reorder.update({
            "entry_counter_unchanged": Counter(reordered_entries) == Counter(final_entries),
            "citation_fields_unchanged": [semantic_field(f) for f in audit.citations(after)] == [semantic_field(f) for f in audit.citations(reordered)],
            "base_compare_has_no_violations": not reordered_result["blocking_violations"],
            "exact_order_predicates": reorder_checks,
            "triggered_order_violations": [k for k, v in reorder_checks.items() if not v],
        })
        reorder["pass"] = (reorder["entry_counter_unchanged"] and reorder["citation_fields_unchanged"]
                            and reorder["base_compare_has_no_violations"]
                            and reorder_checks["candidate_has_25_full_bibliography_entries"]
                            and not reorder_checks["original_24_entries_exact_and_ordered"]
                            and not reorder_checks["candidate_full_25_entries_exactly_equal_native"])
    checks["pure_reorder_detected_while_entry_counter_and_citations_unchanged"] = reorder["pass"]
    checks["final_mode_uses_distinct_file_identity"] = args.mode != "final_file_semantics" or not same_reference
    inputs_unchanged = all(ref(r["path"]) == r for r in refs.values())
    checks["all_inputs_byte_identical_after_read_and_negative_test"] = inputs_unchanged
    violations = [key for key, ok in checks.items() if not ok]
    result.update({
        "schema": "FINAL_REFRESH_FULL_BIBLIOGRAPHY_FILE_AUDIT_CODEX_SUCCESSOR_V1",
        "implementation_and_review": "Codex independent implementation + Claude r4 old-22 citation order patch / pending supervisor review",
        "same_reference_file_identity": same_reference,
        "tautological_checks_in_this_mode": ["candidate_full_25_entries_exactly_equal_native", "all_fields_instruction_and_display_equal_genuine_native"] if same_reference else [],
        "at": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "status": ("FIXTURE_FILE_SEMANTICS_PASS_NOT_FINAL" if args.mode == "fixture_only" else "FINAL_FILE_SEMANTICS_PASS_REQUIRES_ROOT_NATIVE_EVENT_BINDING") if not violations else "FILE_SEMANTICS_REQUIRES_EXPLICIT_REVIEW",
        "not_an_approval": True,
        "native_refresh_performed_by_this_script": False,
        "native_refresh_evidence_verified": False,
        "final_pdf_certified": False,
        "source_refs": refs,
        "fail_closed_checks": checks,
        "blocking_violations": violations,
        "old_full_field_differences": old_field_differences,
        "native_to_candidate_non_story_parts": audit.package_delta(native, after),
        "native_to_candidate_metadata_requires_explicit_review": [x["part"] for x in audit.package_delta(native, after) if x["review_status"] == "PENDING_EXPLICIT_REVIEW"],
        "negative_control_file": str(out / "REAL_OLD_ENTRY_DELETION_NEGATIVE.json"),
        "reorder_negative_control_file": str(out / "PURE_REORDER_NEGATIVE.json"),
        "old_citation_order": order,
        "citation_swap_negative_control_file": str(out / "OLD_CITATION_SWAP_NEGATIVE.json"),
        "limitations": result["limitations"] + ["本项仅证明文件语义。必须由 root 另绑定实际最终 Zotero Refresh、保存重开与最终 PDF 证据。",
            "原生 Refresh 若变更 CSL 元数据、引文指令/显示或完整书目条目，必须审阅差异；不能仅凭域/段数相同判定保全。",
            "fixture_only 使用历史真实原生稿验证检查器，绝不替代最终累计稿 Refresh 后验收。"],
    })
    out.mkdir(parents=True, exist_ok=False)
    payloads = {
        "RESULT.json": result,
        "REAL_OLD_ENTRY_DELETION_NEGATIVE.json": negative,
        "PURE_REORDER_NEGATIVE.json": reorder,
        "OLD_CITATION_SWAP_NEGATIVE.json": swap_controls,
        "FULL_BIBLIOGRAPHY_ENTRIES.json": {"mother_24": old_entries, "native_25": native_entries, "candidate": final_entries},
        "CANDIDATE_FIELD_INVENTORY.json": after,
        "INPUTS_SHA256.json": refs,
    }
    for name, payload in payloads.items():
        with (out / name).open("x", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2); fh.write("\n")
    print(json.dumps({"status": result["status"], "checks": len(checks), "violations": violations,
                      "negative_control_pass": negative["pass"], "out": str(out)}, ensure_ascii=False))
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())

