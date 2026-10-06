#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""私有只读域语义取证；只写新审阅目录，不改文稿、不生成批准、不操作 Word。"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import difflib
import hashlib
import io
import json
from pathlib import Path
import re
from zipfile import ZipFile
from xml.etree import ElementTree as E

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
STORY = re.compile(r"word/(document|footnotes|endnotes|header\d+|footer\d+)\.xml")
TRACKED = {"ins", "del", "moveFrom", "moveTo", "pPrChange", "rPrChange", "tblPrChange", "trPrChange", "tcPrChange", "sectPrChange"}
WANG_TITLE = "中国家庭结构百年变迁及其特征分析"


def pin(path):
    p = Path(path).resolve(strict=True)
    b = p.read_bytes()
    return {"path": str(p), "sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b)}


def compact(text):
    return re.sub(r"\s+", "", text)


def exact_year_2026(data):
    # Zotero CSL JSON 年份允许数字或等值字符串；拒绝带尾字符、浮点数或空日期。
    parts = data.get("issued", {}).get("date-parts", [])
    if not parts or not isinstance(parts[0], list) or not parts[0]:
        return False
    year = parts[0][0]
    return (type(year) is int and year == 2026) or (type(year) is str and year == "2026")


def parse_story(blob, name):
    # 独立保存域显示的逐段文本，使跨段书目删除可见，而非只核一个自相等快照。
    fields, stack, tracking = [], [], []
    paragraph, ordinal = -1, 0
    for event, el in E.iterparse(io.BytesIO(blob), events=("start", "end")):
        if not el.tag.startswith(W):
            continue
        local = el.tag[len(W):]
        if event == "start":
            if local == "p":
                paragraph += 1
            if local in TRACKED:
                tracking.append({"tag": local, "paragraph": paragraph})
            if local == "fldSimple":
                ordinal += 1
                stack.append({"kind": "simple", "instruction": el.get(W + "instr", ""), "display": "", "separated": True,
                              "story": name, "ordinal": ordinal, "start_paragraph": paragraph, "paragraph_fragments": {}})
            continue
        if local == "fldChar":
            typ = el.get(W + "fldCharType")
            if typ == "begin":
                ordinal += 1
                stack.append({"kind": "complex", "instruction": "", "display": "", "separated": False,
                              "story": name, "ordinal": ordinal, "start_paragraph": paragraph, "paragraph_fragments": {}})
            elif typ == "separate":
                if not stack or stack[-1]["kind"] != "complex":
                    raise ValueError("UNBALANCED_SEPARATE:" + name)
                stack[-1]["separated"] = True
            elif typ == "end":
                if not stack or stack[-1]["kind"] != "complex":
                    raise ValueError("UNBALANCED_END:" + name)
                fields.append(stack.pop())
            else:
                raise ValueError("UNSUPPORTED_FIELD_TYPE:" + str(typ))
        elif local == "instrText" and stack:
            stack[-1]["instruction"] += el.text or ""
        elif local in {"t", "tab", "br", "cr"}:
            value = (el.text or "") if local == "t" else ("\t" if local == "tab" else "\n")
            for field in stack:
                if field["separated"]:
                    field["display"] += value
                    key = str(paragraph)
                    field["paragraph_fragments"][key] = field["paragraph_fragments"].get(key, "") + value
        elif local == "fldSimple":
            if not stack or stack[-1]["kind"] != "simple":
                raise ValueError("UNBALANCED_SIMPLE:" + name)
            fields.append(stack.pop())
    if stack:
        raise ValueError("UNCLOSED_FIELD:" + name)
    fields.sort(key=lambda x: x["ordinal"])
    for field in fields:
        inst = field["instruction"]
        if "CSL_CITATION" in inst:
            try:
                field["csl"] = json.loads(inst[inst.index("{"):].strip())
            except (ValueError, TypeError) as exc:
                raise ValueError("INVALID_CSL_JSON:" + name) from exc
            if not isinstance(field["csl"].get("citationItems"), list):
                raise ValueError("INVALID_CITATION_ITEMS:" + name)
        if "ZOTERO_BIBL" in inst:
            field["bibliography_paragraphs"] = [{"paragraph": int(k), "text": v} for k, v in field["paragraph_fragments"].items() if v.strip()]
    return {"fields": fields, "tracked_elements": tracking}


def inventory(path):
    ref = pin(path)
    with ZipFile(path) as z:
        if len(z.namelist()) != len(set(z.namelist())):
            raise ValueError("DUPLICATE_ZIP_MEMBER")
        stories = {n: parse_story(z.read(n), n) for n in sorted(z.namelist()) if STORY.fullmatch(n)}
        package = {}
        for name in sorted(z.namelist()):
            blob = z.read(name)
            entry = {"sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob), "is_story": bool(STORY.fullmatch(name))}
            if name.endswith((".xml", ".rels")):
                try:
                    canonical = E.canonicalize(blob).encode("utf-8")
                    entry["canonical_xml_sha256"] = hashlib.sha256(canonical).hexdigest()
                except E.ParseError as exc:
                    raise ValueError("INVALID_PACKAGE_XML:" + name) from exc
            package[name] = entry
    if "word/document.xml" not in stories:
        raise ValueError("DOCUMENT_STORY_MISSING")
    if ref != pin(path):
        raise ValueError("SOURCE_CHANGED_DURING_READ")
    return {"source": ref, "stories": stories, "package": package}


def fields(inv):
    return [f for story in inv["stories"].values() for f in story["fields"]]


def citations(inv):
    return [f for f in fields(inv) if "csl" in f]


def uri_counts(inv):
    return Counter(uri for f in citations(inv) for item in f["csl"]["citationItems"] for uri in item.get("uris", []))


def bib_entries(inv):
    return [p["text"] for f in fields(inv) for p in f.get("bibliography_paragraphs", [])]


def delta_counts(before, after):
    return {"removed": dict(before - after), "added": dict(after - before)}


def item_counts(inv, exclude_uri=None):
    # 严格比较原始 CSL 成员；即使看似仅本地 ID 刷新，也不得静默认为已获批准。
    return Counter(json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                   for field in citations(inv) for item in field["csl"]["citationItems"]
                   if exclude_uri not in item.get("uris", []))


def package_delta(before, after):
    entries = []
    for name in sorted(set(before["package"]) | set(after["package"])):
        if STORY.fullmatch(name):
            continue
        old, new = before["package"].get(name), after["package"].get(name)
        changed = old != new
        entries.append({"part": name, "before": old, "after": new,
                        "change": "added" if old is None else "removed" if new is None else "changed" if changed else "unchanged",
                        "canonical_xml_equal": None if not old or not new or "canonical_xml_sha256" not in old or "canonical_xml_sha256" not in new
                        else old["canonical_xml_sha256"] == new["canonical_xml_sha256"],
                        "review_status": "PENDING_EXPLICIT_REVIEW" if changed else "BYTE_IDENTICAL"})
    return entries


def field_identity(f):
    # 保留成员、显示与属性；序号变化不冒充成员变化。
    return {"story": f["story"], "citationID": f["csl"].get("citationID"),
            "items": f["csl"]["citationItems"], "display": f["display"],
            "properties": f["csl"].get("properties", {})}


def compare(before, after, wang_uri):
    oldc, newc = citations(before), citations(after)
    old_ids, new_ids = defaultdict(list), defaultdict(list)
    for f in oldc:
        old_ids[str(f["csl"].get("citationID"))].append(field_identity(f))
    for f in newc:
        new_ids[str(f["csl"].get("citationID"))].append(field_identity(f))
    oldb, newb = bib_entries(before), bib_entries(after)
    oldbc, newbc = Counter(map(compact, oldb)), Counter(map(compact, newb))
    uris = delta_counts(uri_counts(before), uri_counts(after))
    member_deltas = delta_counts(item_counts(before), item_counts(after, exclude_uri=wang_uri))
    removed_b = oldbc - newbc
    added_b = newbc - oldbc
    wang = []
    no_uri = []
    for f in newc:
        for item in f["csl"]["citationItems"]:
            if not item.get("uris"):
                no_uri.append({"story": f["story"], "ordinal": f["ordinal"], "item": item})
            if wang_uri in item.get("uris", []):
                data = item.get("itemData", {})
                wang.append({"story": f["story"], "ordinal": f["ordinal"], "citationID": f["csl"].get("citationID"),
                             "member": item, "display": f["display"],
                             "checks": {"title_exact": data.get("title") == WANG_TITLE,
                                        "year_2026": exact_year_2026(data),
                                        "suppress_author": item.get("suppress-author") is True,
                                        "display_year_only": re.sub(r"[\s()（）]", "", f["display"]) == "2026"}})
    bib_wang = [x for x in newb if all(y in x for y in [WANG_TITLE, "王跃生", "2026"])]
    common_changed = []
    for cid in sorted(set(old_ids) & set(new_ids)):
        if old_ids[cid] != new_ids[cid]:
            common_changed.append({"citationID": cid, "before": old_ids[cid], "after": new_ids[cid]})
    warnings = []
    if uris["removed"]:
        warnings.append("旧被引 URI 出现次数减少：须逐项解释，不能默认为格式刷新")
    if set(uris["added"]) - {wang_uri}:
        warnings.append("新增非 Wang URI：须核授权和来源")
    if removed_b:
        warnings.append("旧书目逐段文本未原样保全：可能是删除或格式/段落变化，须对照真实条目")
    if len(wang) != 1 or any(not all(x["checks"].values()) for x in wang) or len(bib_wang) != 1:
        warnings.append("Wang 唯一成员/年份/抑制作者/唯一书目段检查未全部满足")
    if any(x["tracked_elements"] for x in after["stories"].values()):
        warnings.append("after 含修订元素，不是干净原生/内容稿")
    if no_uri:
        warnings.append("after 有无 URI 的 CSL 成员，必须额外确定身份")
    checks = {
        "before_has_citations": len(oldc) > 0,
        "before_has_bibliography_entries": len(oldb) > 0,
        "old_uri_occurrences_preserved": not uris["removed"],
        "only_wang_uri_added_once": uris["added"] == {wang_uri: 1},
        "wang_not_preexisting": uri_counts(before)[wang_uri] == 0,
        "old_complete_csl_members_preserved_exactly": not member_deltas["removed"] and not member_deltas["added"],
        "citation_field_count_increased_by_one": len(newc) == len(oldc) + 1,
        "old_citation_ids_preserved": not (set(old_ids) - set(new_ids)),
        "citation_ids_present_and_unique": all(k not in {"None", ""} and len(v) == 1 for k, v in new_ids.items()),
        "bibliography_field_count_unchanged": sum("bibliography_paragraphs" in f for f in fields(before)) == sum("bibliography_paragraphs" in f for f in fields(after)),
        "old_bibliography_entries_preserved_normalized": not removed_b,
        "wang_unique_and_metadata_correct": len(wang) == 1 and all(all(x["checks"].values()) for x in wang),
        "wang_bibliography_unique": len(bib_wang) == 1,
        "only_wang_bibliography_added": len(bib_wang) == 1 and added_b == Counter([compact(bib_wang[0])]),
        "no_members_without_uri": not no_uri,
        "after_has_no_tracked_elements": not any(x["tracked_elements"] for x in after["stories"].values()),
    }
    violations = [name for name, ok in checks.items() if not ok]
    nonstory = package_delta(before, after)
    return {
        "status": "BLOCKED_SEMANTIC_PRESERVATION_REVIEW" if violations else "MECHANICAL_CHECKS_CLEAR_REQUIRES_INDEPENDENT_REVIEW",
        "not_an_approval": True,
        "fail_closed_checks": checks,
        "blocking_violations": violations,
        "non_story_parts": nonstory,
        "non_story_changed_pending_review": [x["part"] for x in nonstory if x["review_status"] == "PENDING_EXPLICIT_REVIEW"],
        "citation_field_count": {"before": len(oldc), "after": len(newc)},
        "all_field_count": {"before": len(fields(before)), "after": len(fields(after))},
        "citation_member_count": {"before": sum(len(x["csl"]["citationItems"]) for x in oldc), "after": sum(len(x["csl"]["citationItems"]) for x in newc)},
        "uri_occurrence_deltas": uris,
        "complete_csl_member_deltas_excluding_added_wang": member_deltas,
        "unique_uri_count": {"before": len(uri_counts(before)), "after": len(uri_counts(after))},
        "removed_citationIDs": sorted(set(old_ids) - set(new_ids)),
        "added_citationIDs": sorted(set(new_ids) - set(old_ids)),
        "duplicate_citationIDs_after": {k: len(v) for k, v in new_ids.items() if len(v) > 1},
        "common_citation_changes": common_changed,
        "bibliography_field_count": {"before": sum("bibliography_paragraphs" in f for f in fields(before)), "after": sum("bibliography_paragraphs" in f for f in fields(after))},
        "bibliography_paragraph_count": {"before": len(oldb), "after": len(newb)},
        "bibliography_removed_normalized": dict(removed_b),
        "bibliography_added_normalized": dict(added_b),
        "bibliography_before": oldb, "bibliography_after": newb,
        "wang_occurrences": wang, "wang_bibliography_matching_paragraphs": bib_wang,
        "members_without_uri": no_uri, "warnings_for_reviewer": warnings,
        "limitations": ["格式/拆段变化可能导致逐段文本差异，需要人工对照条目与被引成员；不能把段数当文献数。",
                        "仅从文件读取无法证明真实 Word 保存/只读重开；原生来源回执由 supervisor 另核。",
                        "无差异或机械检查通过均不能自动成为 FIELD_DELTA_APPROVAL。",
                        "citationID 变化可能来自原生刷新；需用 URI、成员、位置与显示共同复核。"]
    }


def snapshot(inv):
    return [{"story": f["story"], "kind": f["kind"], "instruction": f["instruction"], "display": f["display"]} for f in fields(inv)]


def run(args):
    before, after = inventory(args.before), inventory(args.after)
    result = compare(before, after, args.wang_uri)
    result.update({"schema": "PRIVATE_FIELD_SEMANTIC_AUDIT_V1", "at": datetime.now(timezone.utc).isoformat(),
                   "stage": args.stage, "before": before["source"], "after": after["source"], "script": pin(__file__)})
    if args.native_reference:
        native = inventory(args.native_reference)
        result["native_reference"] = native["source"]
        result["final_fields_exactly_equal_native_reference"] = snapshot(native) == snapshot(after)
        if not result["final_fields_exactly_equal_native_reference"]:
            result["blocking_violations"].append("final_fields_do_not_equal_genuine_native_reference")
            result["status"] = "BLOCKED_SEMANTIC_PRESERVATION_REVIEW"
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    for name, obj in [("BEFORE_FIELD_INVENTORY.json", before), ("AFTER_FIELD_INVENTORY.json", after), ("SEMANTIC_DELTA_REVIEW_NOT_APPROVED.json", result)]:
        with (out / name).open("x") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2); f.write("\n")
    before_lines = json.dumps(snapshot(before), ensure_ascii=False, indent=2).splitlines(True)
    after_lines = json.dumps(snapshot(after), ensure_ascii=False, indent=2).splitlines(True)
    with (out / "FIELD_SNAPSHOT.diff").open("x") as f:
        f.writelines(difflib.unified_diff(before_lines, after_lines, fromfile=str(args.before), tofile=str(args.after)))
    with ZipFile(args.before) as oldz, ZipFile(args.after) as newz, (out / "NON_STORY_PARTS.diff").open("x") as diff:
        for part in result["non_story_parts"]:
            if part["review_status"] != "PENDING_EXPLICIT_REVIEW":
                continue
            name = part["part"]
            diff.write("\nPART: " + name + "\n" + json.dumps(part, ensure_ascii=False) + "\n")
            if name.endswith((".xml", ".rels")):
                old = oldz.read(name).decode("utf-8") if part["before"] else ""
                new = newz.read(name).decode("utf-8") if part["after"] else ""
                diff.writelines(difflib.unified_diff(old.replace("><", ">\n<").splitlines(True),
                                                  new.replace("><", ">\n<").splitlines(True),
                                                  fromfile="before/" + name, tofile="after/" + name))
    # 再次核源，不能使取证 JSON 与随后生成的包部件 diff 来自不同字节。
    if before["source"] != pin(args.before) or after["source"] != pin(args.after):
        raise ValueError("SOURCE_CHANGED_DURING_AUDIT")
    warnings = "\n".join("- " + x for x in result["warnings_for_reviewer"]) or "- 暂无机械异常；仍需独立语义审阅。"
    report = "# 实际字段取证（未批准）\n\n状态：" + result["status"] + "\n\n"
    report += "阶段：" + args.stage + "\n\n前：" + before["source"]["path"] + "\n\n后：" + after["source"]["path"] + "\n\n"
    report += "引文域数：" + str(result["citation_field_count"]) + "；成员数：" + str(result["citation_member_count"]) + "\n\n"
    report += "硬阻断：" + json.dumps(result["blocking_violations"], ensure_ascii=False) + "\n\n"
    report += "非 story 待逐项审阅：" + json.dumps(result["non_story_changed_pending_review"], ensure_ascii=False) + "\n\n"
    report += "需要审阅：\n\n" + warnings + "\n\n逐成员、URI、书目原文及具体差异见 JSON、FIELD_SNAPSHOT.diff、NON_STORY_PARTS.diff。本报告不生成 PASS 或批准。\n"
    with (out / "REPORT_NOT_APPROVED.md").open("x") as f:
        f.write(report)
    print(json.dumps({"status": result["status"], "report": pin(out / "REPORT_NOT_APPROVED.md"), "review": pin(out / "SEMANTIC_DELTA_REVIEW_NOT_APPROVED.json")}, ensure_ascii=False))
    return 2 if result["blocking_violations"] else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["pre_citation_to_native_saved", "mother_to_final_content"], required=True)
    parser.add_argument("--before", required=True, type=Path)
    parser.add_argument("--after", required=True, type=Path)
    parser.add_argument("--wang-uri", required=True)
    parser.add_argument("--native-reference", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if not re.fullmatch(r"https?://zotero\.org/(users|groups)/[^/]+/items/[A-Z0-9]{8}", args.wang_uri):
        parser.error("必须提供原运行核实的精确 Wang URI，不接受占位符")
    raise SystemExit(run(args))
