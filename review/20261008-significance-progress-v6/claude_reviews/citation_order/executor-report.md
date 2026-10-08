# r4 executor report — cmaverse-citation-order-repair-20261007-r4

Executor: claude / surface:41 (FC5DB919-47A7-4A8F-9A46-1182958CE532). Supervisor: codex / surface:40.
Pack finalized_at 2026-10-07T13:33:03Z; completion_nonce 8e366f7a2e3d4659b4d7ba059a433ac7.

## 结论

OFFLINE_PASS_NATIVE_PENDING. The r3 P2-1 is closed in an independent successor copy: the old 22 citationIDs now require an exact relative order **and** story membership (across all 9 stories). A same-story swap of two old citations is now blocked without relying on the snapshot equality check against the frozen native. Every existing gate is kept; the 29 shared checks give identical values. This only proves the file semantics. It does not stand in for the native Refresh, the save-and-reopen, or the final PDF, which must be proven by an independent execution receipt.

IMPL = `/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1/limited_followup_20261006_v1/paper_closeout_after_numerical_v1/final_closeout_execution_20261007_v2/minimal_final_execution_20261007_v3/claude_citation_order_repair_r4/implementation`

## 代码与测试 SHA-256

| 文件 (IMPL/) | sha256 |
|---|---|
| verify_post_refresh_bibliography_successor.py（修补后） | 360fa653dfd130f03d494722676e713d2f74e86a5a8f6d4349c5641b5dae9620 |
| input_guards.py（逐字节=输入，未改） | 1edec6fdbc11e0858e45c228f8463d6a71c1ab787419dbdb983a46f17db34c68 |
| .orig_successor.py（逐字节=输入 pin，对照用） | 4faffc181aef02628d7355394076ed1d3a9a61906025af7de6c62236711fab22 |
| test_citation_order.py | 3f5e9300c3438cd293eeba030d7fabc4106dbcc007982831b54671a346632919 |
| mutation_and_superset_check.py | b29d415881445294a2ae5cac68f28a7d6e67d1789dce0ae6b0224bed04ab5cca |
| SOURCE_DIFF.patch（diff -u 原→新，139 行，+95/−1） | 7e3654216224e07bcb6ab1acb2584aa0eca31409bf534e088daa6c2e451a5c4d |
| unittest_run2.log（11/11 OK） | bfc97a8c66cfa33ea1bdb7e8cfc8904dfd63c72061adb5829ffdbb741ebf97fd |
| mutation_check_v1/SUMMARY.json | 85c044b3997663f1234d91035fae10ff839796324c70004d1e8ad81b78523e0a |
| test_runs_v1/20261007T215248/NATIVE_IDENTITY.json | 08c2e876c060bd544558894eabe6d95eab85f33a57a07897d35105f5be14aa16 |

The input pins were rechecked after the work and are unchanged. Codex successor 4faffc18…, input_guards 1edec6fd…. Frozen native f2582b30…, ino 159415029, nlink 2, mtime 1791315660 before and after.

## 精确变更（全部在 IMPL 副本内）

1. New `old_citation_order(old_fields, new_fields)`. Old sequence = `[(story, citationID)]` in the extractor's fixed order: stories sorted by name, then by ordinal within each story. The candidate side keeps only old IDs, so where Wang is inserted does not matter. It also requires the old IDs to be unique. It returns ok / both sequences / first_difference_index.
2. New check `original_22_citation_ids_relative_order_and_story_exact` = `len(old_fields)==22 and order.ok`.
3. New `swap_citation_fields(blobs, audit, a, b)`. It works in memory on the real candidate's story XML. It swaps the whole instrText and display text of two top-level CSL_CITATION complex fields, which can sit in different stories. It fails closed if a target is not unique. It never writes a DOCX.
4. New built-in negative control `old_citation_swap_detected_by_order_predicate`, with two cases:
   - within_document_story (ydGrzFR0↔XadNs3oS): it must show that the reparsed IDs are an exact swap, the swapped fields carry their full original semantics, base compare has 0 violations, **and** `id_keyed_original_22_fields_exact` stays True. That proves the gap is real. Only the new predicate rejects.
   - cross_document_footnotes (ydGrzFR0↔hE2u8elZ): the new predicate rejects, and the ID-keyed story check also rejects.
   - Output goes to `OLD_CITATION_SWAP_NEGATIVE.json`. RESULT.json gains `old_citation_order` and `citation_swap_negative_control_file`.
5. The `implementation_and_review` string now says "Codex … + Claude r4 old-22 citation order patch / pending supervisor review". The 1 removed line is the original version of this string.

Unchanged: input_guards, strict_absolute_path, require_distinct_candidate, output-directory rules, pins, all 29 original checks, the deletion and reorder negative controls, and status/exit-code semantics.

## 真实正负例（final_file_semantics）

Run directory `IMPL/test_runs_v1/20261007T215248/`. Each case has a `.log` and an output subdirectory.

| 用例 | 候选 | 结果 |
|---|---|---|
| 正：独立同 SHA 副本 | inputs/independent_native_copy.docx（f2582b30…，ino≠原生） | rc=0，violations=[]，31 checks；ORDER=True，SWAP 负控=True |
| 拒：同路径原生 | 冻结原生本体 | rc=1 FINAL_MODE_REQUIRES_DISTINCT_CANDIDATE，无输出 |
| 拒：Codex 既有硬链接 | codex_checker_takeover_v1/…/guard_test_inputs_v1/native_hardlink_to_reference.docx | rc=1 同上 |
| 负：story 内交换，**原版** | inputs/swap_within_document.docx（3b244d23…） | rc=2，violations 仅 `all_fields_instruction_and_display_equal_genuine_native`；`original_22_full_citation_fields_exact`=True（缺口复现） |
| 负：story 内交换，修补版 | 同上 | rc=2，violations=snapshot + ORDER + SWAP 负控；first_difference_index=0 |
| 负：跨 story 交换，修补版 | inputs/swap_cross_document_footnotes.docx（f492b62a…） | rc=2，含 ORDER 与 original_22_full_citation_fields_exact |
| 变异体：ORDER 谓词恒真 | swap_within_document.docx | ORDER 漏报=True；SWAP 负控=False 进 violations → mutant killed |
| 超集 | 独立副本，原版 vs 修补版 | 29 ⊂ 31，新增恰为 2 项，共有 29 项取值逐项相同 |

Why the SWAP control also fails on the swapped mutant: the built-in control assumes the candidate is a good draft. Swapping the same pair again on an already-swapped draft restores the order, so the control fails by construction. That is an extra fail-closed violation. Run 1, `test_runs_v1/20261007T214857_run1_wrong_test_expectation/`, failed because my test had not anticipated this. The checker was not at fault, and the fix was to the test assertion only.

Synthetic cases (9 stories, 18 old IDs):
- identity, and Wang inserted at any of the 19 positions: all pass;
- a within-story swap in each of the 9 stories: all rejected, first_difference_index exact;
- a swap for each of the 36 story pairs: all rejected;
- moving a citation to another story while keeping the relative order: rejected;
- missing, extra, or duplicate IDs: rejected.

Real mother → frozen native: the order holds. 22 entries = 19 in document.xml + 3 in footnotes.xml.

## 运行命令

```
cd "$IMPL"   # 见上方绝对路径
/usr/bin/python3 test_citation_order.py               # 11 tests，写 test_runs_v1/<时间戳>/
/usr/bin/python3 mutation_and_superset_check.py       # 写 mutation_check_v1/（须为新目录）
/usr/bin/python3 verify_post_refresh_bibliography_successor.py --candidate <绝对路径> \
  --candidate-sha256 <sha> --mode final_file_semantics --out "$IMPL/<新子目录>"
```

## 剩余观察（不在本次范围，未修）

- P3: the order is defined over the extractor's story concatenation order. Moving body citations relative to footnote citations, as long as their positions in the reading flow stay the same, has no meaning in this order, and the story membership check already covers it.
- P3: the order of the 3 footnote citations depends on their ordinal within footnotes.xml, which is not necessarily the footnote number order. The same holds for both the old and new draft, and it matches the mother → native comparison.
- The r3 P2-2, P3-1 to P3-4, and the run.py:117 wiring are not addressed here. `smoke_fixture/` is an early fixture_only smoke run (rc=0) and is kept as evidence.
- I did not touch the inputs, the formal draft, root, other Claude directories, or shared skills. I did not touch Word, Zotero, NLM, tickets, or the UI. I ran no statistics.
