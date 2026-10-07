# 最终书目保全检查器与发布可复核性 — 有界只读审查

任务：`cmaverse-final-bibliography-delivery-20261007-r1` · executor surface:2596 · 开工 2026-10-07T14:33:13+0800

**结论先行：核心四问全部「会查、会拒」，无可证实 P0/P1。** 4 条 P2 全部与「判据覆盖的边界」有关，不是判据失效。最终原生/PDF/NLM 仍未完成，本报告不声称任何 Refresh 通过。

## 0. 本次读到的来源（包内无 SHA pin，以下为我的现测读数）

任务包 `source_entries` 只有 `path`+`exists` 两键，**没有 sha256/bytes**，所以无法做「包钉值 vs 现测」比对；下表是我自己算的，方法为 `hashlib.sha256(Path(p).read_bytes())`。

| 文件 | bytes | sha256(前16) |
|---|---|---|
| `final_nlm_and_bibliography_preflight_v1/verify_post_refresh_bibliography.py` | 9144 | `5e7ffa44612ca0f8` |
| `private_actual_field_semantics_audit_v1/audit_actual_fields_readonly.py` | 19222 | `cc5e1d594c51b982` |
| MOTHER `delivery/current_recovered_manuscript_20261005_v1/…当前整合稿.docx` | 496516 | `4f8cb6c2963c52ef` |
| NATIVE `native_readiness/native_citation_after_release_v5/native_saved_year_fixed.docx` | 545513 | `f2582b306d164858` |
| `private_native_successor_runner_20261007_v3_preparation/minimal_closeout_v2/README.md` | 5567 | `59add5720ad98a66` |

检查器内硬编码的三个 SHA（`EXTRACTOR_SHA` / `MOTHER_SHA` / `NATIVE_SHA`，`:20`/`:22`/`:24`）与我现测**逐位相符**，`ref()`（`:33-34`）会在不符时抛 `PIN_MISMATCH`。

**执行边界（必须说明）：** 我**没有运行**该检查器。`:55-56` 要求 `--out` 必须是检查器自身目录 `final_nlm_and_bibliography_preflight_v1/` 下的新子目录，而我的写允许根只有 artifact_root（marker `artifact_root` 实测、`executor-availability.json` 的 `protected_paths` 覆盖其父目录）。运行它会在我的写范围外、且落在 protected_paths 内建目录。因此我**用检查器自己的 `main()` 逐行逻辑 + extractor 的真实函数在内存中复算**了全部 25 条判据与负测。下文凡标「复算」者均非产品自身判决，命令交由 root 执行（§4）。

## 1. 核心四问：都查了，且真删会被拒

| scope 要求 | 代码位置 | 复算结果 |
|---|---|---|
| 23 动态引用域 | `verify_post_refresh_bibliography.py:87` `candidate_23_citation_fields` | NATIVE 实测 23 个含 CSL 的域（母稿 22）→ True |
| 25 完整条目 | `:82` `genuine_native_has_25…`、`:83` `candidate_has_25…` | 实测 25 → True |
| 旧 24 保全 | `:81` `source_mother_has_24…`、`:84` `original_24_entries_exact_and_ordered` = `final_entries[1:] == old_entries` | 母稿实测 24；`native_entries[1:] == old_entries` → **True** |
| 真删旧书目负向反例被拒 | `:92-116` | **负测 pass=True**（详见下） |

**「下标 1 起」这一假定是对的，不是缺陷。** 我原先怀疑按拼音排序「王跃生」不该排第 0 位。实测否掉：书目中文条目只有 3 条（王跃生 W / 许琪 X / 郑丹丹 Z，拼音升序），其后才是拉丁条目 A→Y，**Wang 实测位于下标 0**，故 `final_entries[1:]` 恰为旧 24 条。补充集合层核验：`Counter(old) - Counter(native) == {}`，`native - old` 恰 1 条。

**正对照（同一轮）：** 未变异候选（`fixture_only`，候选=真实原生稿）→ 25 条判据**全过**，`blocking_violations = []`。证明判据没被削弱成恒假。

**负测复算（真实删除「郑丹丹, 狄金华, 2017」）：**

```
matched_real_paragraph_count          = 1     （须==1，否则整块跳过）
triggered_violation                   = True  （old_bibliography_entries_preserved_normalized）
exact_removed_map                     = True
citation_fields_and_members_unchanged = True
all_citation_count_checks_still_pass  = True
bibliography_entries_lost             = 1
negative['pass']                      = True
变异后 status                          = BLOCKED_SEMANTIC_PRESERVATION_REVIEW
```

**三点额外变异（我加的，不在检查器内）：**

1. **段落级整段移除 `w:p`**（原生刷新删条目的真实形态，非清空 `w:t`）→ 抓到，`removed_normalized` 命中该条，条目 25→24。
2. **删拉丁条目「Yazawa A, Shiba K, Inoue Y…」**（非硬编码那条）→ 也抓到。说明删除检测走 `compare()` 的归一化 Counter 差集（`audit:186`/`:189`/`:234`），**不限于 `REAL_OLD_ENTRY` 一条**。
3. **纯重排**（互换两条旧条目文本，集合不变、顺序变）→ 见 P2-1。

**负测跳过时 fail-closed 成立：** 若 `matched != 1`，`:100` 的 if 不进入，`triggered_violation` 等键缺失，`:114` 的 `negative.get(k) is True` 对 `None` 为 False → `negative["pass"]=False` → `:116` 判据失败 → 进 `violations`。空转不会伪装成通过。

**诚实性声明齐备：** `not_an_approval: True`、`native_refresh_performed_by_this_script: False`、`native_refresh_evidence_verified: False`、`final_pdf_certified: False`（`:125-128`），且 `:136-138` 明文写「必须由 root 另绑定实际最终 Zotero Refresh、保存重开与最终 PDF 证据」。

## 2. 四条 P2（均为覆盖边界，非判据失效）

### P2-1 内建负测证不了「顺序敏感」

**复现：** 把旧条目「郑丹丹…2017」与「Yazawa A…2022」的逐段文本互换（集合不变、顺序变）。

```
compare() blocking_violations            = []        ← 零违规
candidate_has_25_full_bibliography_entries = True
original_24_entries_exact_and_ordered      = False   ← 只有这条抓到
```

**机理：** `compare()` 的 `old_bibliography_entries_preserved_normalized`（`audit:234`）判据是 `Counter` 差集 `removed_b`，对重排恒为空。顺序只由检查器自己的 `:84` 位置相等式管辖。而内建负测的 4 个断言（`:107-110`）**全部只读 `neg_result`（即 `compare()` 的输出）**，所以它证明的是「删除被 compare 抓到」，**不证明 `:84` 的顺序敏感性**。

**影响：** 有界。重排仍会被 `:84` 拒，最终判据集不漏。但「负测通过」不能被读成「顺序保全已被测到」——这正是我报告里必须区分的两层。

**最小修复：** 在 `:92-116` 增一个重排变异体，断言 `final_entries[1:] != old_entries`（即 `:84` 为 False）且 `compare()` 仍零违规，把两层差异钉成显式证据。

### P2-2 `fixture_only` 下 2 条跨稿判据自比恒真

`--mode fixture_only` 的推荐候选就是 `NATIVE` 本身（`native_saved_year_fixed.docx`）。实测 `candidate 路径 == NATIVE 路径 → True`，于是：

- `:85` `candidate_full_25_entries_exactly_equal_native`
- `:88` `all_fields_instruction_and_display_equal_genuine_native`

两条左右同源，**按构造不可能失败**。报告里的「25 条判据全过」在 fixture 模式下实际有效判据是 23 条。

**影响：** 不产生错误放行（状态串已是 `FIXTURE_FILE_SEMANTICS_PASS_NOT_FINAL`），但会高估 fixture 轮的证据强度。

**最小修复：** 在 `RESULT.json` 加 `tautological_checks_in_this_mode: [...]`，fixture 模式下显式列出这 2 条，令读者不把 25/25 当跨稿一致性证据。

### P2-3 `--mode` 只改状态串，不改任何判据

`:124` 的三目只在 `status` 字符串上分叉；`checks` 构造（`:79-118`）与 `--mode` 完全无关。因此用 `fixture_only` 的候选（=NATIVE）配 `--mode final_file_semantics` 跑，会得到 `FINAL_FILE_SEMANTICS_PASS_REQUIRES_ROOT_NATIVE_EVENT_BINDING` 这一更强的状态串，而实际证据仍是自比。

**影响：** 这是**误读风险**而非放行缺陷（状态串末尾已写 `REQUIRES_ROOT_NATIVE_EVENT_BINDING`，且 `native_refresh_evidence_verified` 恒 False）。

**最小修复：** `final_file_semantics` 模式下加前置断言：候选 realpath ≠ `NATIVE` realpath，否则 `raise ValueError('FINAL_MODE_REQUIRES_DISTINCT_CANDIDATE')`。

### P2-4 verifier 自身无期望 pin

`:62` `"verifier": ref(__file__)` 未传 `expected`，只记录不校验。`:117` 的 `all_inputs_byte_identical_after_read_and_negative_test` 能发现**运行期间**被改，但不能证明跑的是被批准那一版。

**最小修复：** 由 root 在批准件里钉 verifier 的 sha256（现测 `5e7ffa44612ca0f8…`，9144 B），而不是在脚本内自钉（自钉在逻辑上无效）。

## 3. 发布准备：review-only 与最终原生交付的区分

**区分明确，未发现把 review-only 冒充最终交付的地方。** 实测状态串：

| 文件 | 关键字段 |
|---|---|
| `publication_preparation_v1/PENDING_ACCEPTANCE.json` | `status=PENDING_FINAL_RECEIPTS`、`review_mode=solo_self_review`、`final_pdf=null`、`final_docx=null`、`gates=[]` |
| `review_ready_v1/PUBLIC_ACCEPTANCE.json` | `status=REVIEW_ONLY_NOT_FINAL`、`native_or_nlm_verified_by_packager=false` |
| `review_local_verification_v1/VERIFICATION.json` | `status=PASS` 但 `delivery_status=REVIEW_ONLY_NOT_FINAL`、`native_or_statistical_revalidation_performed=false` |
| `RENDER_NEGATIVE_CHECK_v2.json` | `network_calls=0`、`UI_calls=0`、`NLM_queries=0`、`local_cannot_claim_remote_upload=true` |
| `minimal_closeout_v2/README.md` | 「最终论文原生验收、PDF 视觉和 NLM 尚未完成，不得将本准备件写成最终交付通过」 |

注意 `review_local_verification_v1/VERIFICATION.json` 的 `status=PASS` 与 `delivery_status=REVIEW_ONLY_NOT_FINAL` 并存——两字段语义不同层（打包完整性 vs 交付阶段），现写法正确，但建议 root 在对外摘要里只引 `delivery_status`，避免 `PASS` 被单独摘出。

**最终应包含、但尚未生成的最小证据**（来自 `FINAL_ACCEPTANCE_TEMPLATE.json`，6 个 gate 的 `evidence.path/bytes/sha256` 全 null、`reviewed_by_root` 全 false）：

1. `native_word_zotero` — 实际 Zotero Refresh + 保存重开回执
2. `format` — 格式核验回执
3. `pdf_fonts` — 字体嵌入回执
4. `pdf_visual` — 最终 PDF 视觉审阅（README 明载由主管完成）
5. `empirical_adjudication` — 实证裁定
6. `nlm_final_same_pdf` — 与最终 PDF **同版** NLM 回执

外加模板顶层 `final_pdf` / `final_docx` 的 `path/bytes/sha256` 三元组，以及 `minimal_closeout_v2/README.md` 所列前置：旧票 `460c4293-0ca9-491f-9c20-6b7009d02a90` 的真实 `RELEASE.json` → 真实 FIFO 新租约 → root 批准 JSON（`statistics_executed:false`、`build_or_verify_allowed:false`）→ 三阶段 binding 产出 `REVISION_EVIDENCE.json` / `FINAL_EVIDENCE.json` / `DRAIN.json` / `RELEASE.json`。

## 4. 给 root 的最短可运行验收命令

**（A）fixture 自检**（证明检查器本身没坏；`--out` 必须是检查器目录下**尚不存在**的新子目录）：

```bash
rtk proxy /opt/homebrew/opt/python@3.14/bin/python3.14 -B \
  "/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1/limited_followup_20261006_v1/paper_closeout_after_numerical_v1/final_nlm_and_bibliography_preflight_v1/verify_post_refresh_bibliography.py" \
  --candidate "/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1/limited_followup_20261006_v1/paper_closeout_after_numerical_v1/native_readiness/native_citation_after_release_v5/native_saved_year_fixed.docx" \
  --candidate-sha256 f2582b306d164858d79e3441b5d7bb4dbd4bb776a54820c9c64d4dc1ce60831b \
  --mode fixture_only \
  --out "/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1/limited_followup_20261006_v1/paper_closeout_after_numerical_v1/final_nlm_and_bibliography_preflight_v1/fixture_selfcheck_$(date -u +%Y%m%dT%H%M%SZ)"
```

预期：`rc=0`，`status=FIXTURE_FILE_SEMANTICS_PASS_NOT_FINAL`，`violations=[]`，`negative_control_pass=true`，`checks=25`。

**（B）最终稿验收**（`final_refreshed.docx` 由 `minimal_closeout_v2` finalize 阶段产出后）：把 `--candidate` 换成该文件绝对路径、`--candidate-sha256` 换成其现测 sha256、`--mode final_file_semantics`、`--out` 换一个新目录。

预期 `status=FINAL_FILE_SEMANTICS_PASS_REQUIRES_ROOT_NATIVE_EVENT_BINDING`。**该状态串不是交付通过**：仍须补 §3 的 6 个 gate。

现测候选 sha256 的命令：`rtk proxy shasum -a 256 "<final_refreshed.docx 绝对路径>"`

## 5. 本次已读覆盖与剩余限度

**逐行通读：** `verify_post_refresh_bibliography.py`（159 行，全文）、`audit_actual_fields_readonly.py`（339 行，全文）、`minimal_closeout_v2/README.md`（全文）、`PENDING_ACCEPTANCE.json`、`FINAL_ACCEPTANCE_TEMPLATE.json`、`review_ready_v1/PUBLIC_ACCEPTANCE.json`、`review_local_verification_v1/VERIFICATION.json`、`RENDER_NEGATIVE_CHECK_v2.json`。

**实际运行（只读、内存内变异、未写任何 DOCX）：** 3 个 `/tmp` 探针，调用产品 extractor 的真实 `inventory`/`compare`/`bib_entries`/`citations`/`parse_story`/`snapshot`/`compact` 函数；1 次正对照 + 4 次变异（清空 `w:t`、移除 `w:p`、删拉丁条目、纯重排）。全部输入在读后现测 SHA 不变。

**剩余限度（不记为缺陷）：**

1. 我**未执行** `verify_post_refresh_bibliography.py` 本体（写范围所限，§0）。§1 的判据结论是用它自己逻辑的复算，可能与真实运行在 I/O 路径、`out.mkdir` 排他、`ref()` 二次核源上有差异。**命令 §4-A 可由 root 一次性消除此限度。**
2. `final_closeout_execution_20261007_v2/publication_preparation_v1/` 下仍有未逐行读的部件（`pack_increment.py`、`prepare_public_content.py`、`root_publish_v3.py`、`review_v3_stage_preparation_v1/`、`TEST_ONLY_validation_v1/` 的 9+ 用例目录）。scope 限定只审「区分 review-only/最终」与「缺哪些最小证据」，§3 已据状态件回答；逐行审这些生成器超出本次有界范围。
3. 本报告**不**声称最终 Refresh 通过、不声称最终 PDF/NLM 完成、不声称任何 gate 已满足。`native_refresh_evidence_verified` 与 6 个 gate 的 `reviewed_by_root` 实测全为 false。
4. 任务包 `source_entries` 无 SHA/bytes pin，§0 表格是我的现测值而非「包钉值已核」。

## 6. 守约自核（实测，非印象）

- 开工 `2026-10-07T14:33:13+0800`（epoch 1791354793，`date +%z` 现测 `+0800`）。
- 写入范围：仅本文件（artifact_root 内），与 marker `artifact_root` 一致；探针全在 `/tmp`，未在被审目录建任何文件。
- 未触碰 Word/Zotero/GUI/NLM/网络/队列/锁/配置/共享文稿/统计/GitHub；未改任何检查器；未启动模型或 bootstrap；未切换会话或模型。
- 变异全部在内存 `copy.deepcopy` 上进行，`mutated_docx_written` 等价为 False。
- 提交时刻见回调回执 `recorded_at_epoch`；30 分钟期限以该值为准，我不在此预先声称。

