# D2/D3 新实现限定审阅

任务：`cmaverse-d2-d3-publication-review-20261007` · 执行者 surface:2596 · 2026-10-07

只读审阅。未操作 UI、锁、broker、网络；未改共享代码；未跑 R/统计/bootstrap；未重跑 D2/D3 的整套测试或验证生成器。本目录外零写入。所有探针纯内存，脚本放在 `/tmp`，不在本目录留痕。

## 结论

**有 1 项可证实的 P1 代码缺陷，无 P0。** P1 在 D2：书目域内删除整条参考文献会被当作合法「完整域刷新」接受，无任何检查阻止。我用真稿构造反例实测确认，并有正对照证明判据不是恒真。D3 的复核链与 21 处补丁精度经实跑验证成立。另有 3 项 P2（标签/绑定/审阅清单口径）。

「真实 native_saved 尚未到位」「原生布局与 PDF 质检待执行」按任务要求**不记为新增缺陷**——`INPUTS.json.state_boundaries[1]` 已声明其缺席属预期。

## 输入核验

`INPUTS.json`（`schema=CMA_BOUNDED_REVIEW_INPUTS_V1`，`source_count=29`）所列 **29/29 源的 SHA256 与 bytes 与现货逐一相符，零漂移、零缺失**。负控：拿 `INPUTS.json` 自身哈希去比 `sources[0]` 返回 False，判据非恒真。

下文 file:line 均指这些已钉版本。

---

## P1（可证实代码缺陷）

### P1-1 书目域内删除整条参考文献不被拒绝

`native_cumulative_successor_preparation_v2/bounded_field_merge_v2.py:165`

**机理：**

- `:165` 算出 `oldf=contracts.fields(request['pre_citation']['path'])` 后**从未使用**——全文 grep 仅此一次出现，只有 `newf` 进了 `:166` 的 `check_wang`。因此 preflight **没有** pre_citation↔native_saved 的字段差异比较。
- 书目是跨 25 段的单个复杂域，`units()` 把它收成一个原子单元；该单元变化后走 `field_only_scope`（`:99-116`）的 `complete_native_refreshed_field_unit` 分支。该分支只要求**域外**文本逐字不变（`:114`）且单元内存在 `fldChar`（`:115`），对域**内**显示文本不设任何约束。
- `field_review_gate_v2.py:43` 的书目检查只要求「某一条 bib display 同时含 title+王跃生+2026」，不断言其他条目仍在。
- `bounded_field_merge_v2.py:293` 的 `accepted_offline` 字段 == `native_saved` 字段是重言：`accepted_offline` 本就是 `native_saved` 的投影，证明不了原生改动本身正确。

**实测复现（纯内存，真 BASE 稿 475988 B）：**

```
bib_unit_span=(318, 343)  共 25 段，DISALLOWED 元素 NONE
删除一条完整参考文献的可见文本（67 字符：
  '郑丹丹, 狄金华, 2017. 女性家庭权力、夫妻关系与家庭代际资源分配[J]. 社会学研究, 32(1): 171-192+245.'）
→ compare_sources ACCEPTED：1 change unit，mode=complete_native_refreshed_field_unit，
  before_span=[318,343] after_span=[318,343]
```

**正对照（同一探针同一轮）：** 改普通正文段一个字 → `NON_FIELD_TEXT_CHANGED` 被拒。所以缺口是「域内删除不在管辖范围」，不是判据被削弱成恒真。

**负控（证明上面的 DISALLOWED=NONE 有区分力）：** 全文实有 3 个 `bookmarkStart`、3 个 `bookmarkEnd`、3 个 `drawing`、1 个 `sectPr`，都在改动范围之外。

**测试未覆盖：** 24 项用例里没有「域内删内容」。`test_07` 改的是域外文本，`test_09` 注入 bookmark，`test_10` 加整段——三者都不触发本缺口。

**影响：** Zotero 刷新在加入 Wang 条目的同时丢掉一条既有条目（换样式、改排序都可能触发），D2 会放行并写进累计稿。这是发布级错误。

**部分缓释（不足以降级）：** `field_review_gate_v2.py:60-62` 会把 mother→final_content 的字段差异算出来并要求与 `approved_changes` 逐字相等，所以书目变化会出现在待人工审阅的 delta 里。但那是人工逐条看 25 段书目，漏掉单条删除是现实风险；自动判据仍缺失。

**最小修复：** 用已经算出的 `oldf`——对 `instruction` 含 `ZOTERO_BIBL` 的域，要求 `newf` 的 bib display 条目集合 ⊇ `oldf` 的条目集合（允许新增 Wang），否则 `fail('BIBLIOGRAPHY_ENTRY_LOST')`；并补一条「域内删除被拒」的用例。

---

## P2

### P2-1 guard 的 lineage 模块标签写成 v2，实际是 v3

`post_merge_narrative_successor_preparation_v3/native_adapter_review_guard_v3.py:54`

`_load('cmaverse_private_lineage_gate_v2', LINEAGE)`——模块名写 `_v2`，但 `:10` 的 `LINEAGE=HERE/'all_story_lineage_gate_v3.py'` 指向 v3，`:44` 也把它纳入 pin 校验。**行为正确，只有标签误导。** 我最初据这个名字怀疑最终门禁只核旧 D2 合并，读 `:10` 后被否掉。建议改名，避免后人按名字下错结论。

### P2-2 freeze 路径单独看时，字段审阅与 content_patched 的绑定不是强制

`freeze_drafts_v3.py:45-49`

`validate_review` 在 `field_approval` 存在时就跑（`:46`）；而把 `final_content` 绑定到 `post_merge_qa.outputs.content_patched` 的检查在 `validate_lineage` 内（`all_story_lineage_gate_v3.py:17-19`），只有 `all_story_lineage_review` 存在时才跑（`:48-49`）。两者独立。

**为何只是 P2：** freeze 的产物全是 `NOT_READY_*`，不构成授权；真正的闸门是 `native_adapter_review_guard_v3.preflight`，其 `:46` 把 `all_story_lineage_review` 与 `post_merge_qa` 都列为必需，在任何 `broker.run` 前生效。且 `validate_review` 会重新 pin `mother`/`final_content` 并现算 delta（`field_review_gate_v2.py:51-64`），旧批准绑定旧 content 时会因 pin 变化失败——`post_merge_narrative_successor_preparation_v3/HANDOFF.md:55` 也明文写了这一点。

**最小修复：** 在 freeze 加一条：`final_content` 非空则 `post_merge_qa` 必须非空。

### P2-3 非 story 直通部件的「列明」与「阻断」是两档，审阅清单未区分

`bounded_field_merge_v2.py:155-164` 对 base↔native 的差异分流：story 走语义比较（`:158`），`.rels`/media/`[Content_Types].xml` 走专项检查（`:159-163`），**其余一律只记入 `changed_parts` 不阻断**。落空的是 `settings.xml`、`styles.xml`、`numbering.xml`、`docProps/*`。`:153` 的注释写「必须逐个列明并审阅」，所以这是把判断交给人工 scope review 的设计选择，不是漏检。

**但我实测否掉了自己最初的两个担心，这里如实记录：**

- **没有额外包部件混入**：mother/base/cumulative 部件集完全相同（各 27 个），四向差集全为空。
- **cumulative 的直通部件没有偏离母稿**：18 个直通部件中 8 个与母稿逐字节不同，全部产生于 base→cumulative 阶段；其中 **6 个仅是 XML 声明引号与行尾差异**（`c14n_equal=True`）。余下 3 个：`[Content_Types].xml` 与 `docProps/core.xml` 两侧 c14n 长度相等（2944/2944、863/863），差异是元素顺序与 Word 元数据（`cp:revision` 47→46、`dcterms:modified` 回退）；唯一有实质的是 `word/settings.xml` 少了 `<w:revisionView w:markup="0"/>`。
- **`revisionView` 这一项我先前的方向判断是错的**：实测母稿与 cumulative **都没有**该元素，有的是 **base**。所以从 cumulative 直通是对的，不存在「rejected 偏离母稿」。

lineage 门禁只覆盖 `word/media/`、`word/embeddings/`（`all_story_lineage_gate_v2.py:51-55`），实测 18 个直通部件中覆盖 3 个。建议把余下 15 个显式写进 scope review 清单，并注明它们属「列明待审」而非「已阻断」。

---

## 已核通过

### 1. D2 真实来源与 Wang 绑定

- `bounded_field_merge_v2.py:144-149`：`native_source_receipt` 必须 `schema=NATIVE_SAVED_SOURCE_RECEIPT_V1`、`status=NATIVE_SAVED_SOURCE_VERIFIED`；回执内的 `native_saved`/`pre_citation` 必须与 request 逐字相等；`reviewer`/`evidence` 非空且每条 evidence 过 `check()`（真字节）。合成测试无法伪造来源回执或 READY：`merge_core:234` 的 docstring 与 `prepare_scope:171` 只产出 `NOT_READY_REQUIRES_SCOPE_REVIEW`。
- `field_review_gate_v2.py:22-24`：Wang 必须精确 Zotero URI（`https?://zotero.org/(users|groups)/…/items/[A-Z0-9]{8}`）、`year==2026`、精确标题、`suppress_author is True`；`:40` 要求显示文本去空白括号后恰为 `2026`；`:42` 要求全稿恰 1 处该 URI 引文。
- 唯一脚注保留：`:103-105` 要求改动前后 `footnoteReference` 的 `local_shape` 列表完全相等（`NOTE_REFERENCE_CHANGED`），含脚注时限定单段（`MULTI_PARAGRAPH_NOTE_SCOPE_UNSUPPORTED`）。`replace_note_paragraph:200-232` 保留原脚注 run 本体而非复制，避免 Word 接受删除时连带移除引用。实测 Wang 单元 `(48,49)` 恰含 1 个 `footnoteReference`。

### 2. D2 接受/拒绝与母稿关系

`merge_core:243-244` 合并前验 `encoded(accept(cumulative))==encoded(base)` 且 `canonical(reject(cumulative))==canonical(mother)`；`:268-269` 合并后再验 `accept==native` 语义、`reject==mother` canonical。`build:281-282` 对每个 story 各自重复一遍。

保护对象：`DISALLOWED`（`:24`）含 `drawing/pict/object/bookmarkStart/bookmarkEnd/sectPr/hyperlink/sdt/fldSimple`，`:102` 只允许 `pPr`/`r` 子节点。有界性：`:128` 改动单元 ≤32、累计段数 ≤100。

### 3. D2 对象与表 6 常量已订正

`all_story_lineage_gate_v2.py:59` 钉 `(34,3,37,30)`；`freeze_drafts_v2.py:34` 钉 `(34,3,30,37)`（字段序不同但各自自洽）。上一任务发现的旧 `(31,3,27)` 不在本目录。

`table6_pdf_qa_v5.py:8` `CAPTION='表6模型5的标准化情境概率与加性交互'`、`:23` `tables[9]`。**实跑 `docx_rows(BASE)` 得 8 行、32 值**，与 `freeze_drafts_v3.py:39` 的契约一致。旧 `table23b_pdf_qa_v4.py` 已不在目录。

### 4. D3 真复核旧 D2 合并（不是复述 HANDOFF）

`post_merge_narrative_v3.py:176-189`：`oldlineage.compute(d2request)` 走完整链；`:181` 用四个真实来源重跑 `m.merge_core`；`:184-189` 剔除修订日期后与实际 tracked 产物逐字节比对（`PATCH_D2_TRACKED_REGEN_MISMATCH`）。`validate_d2_package:164-167` 要求除 `word/document.xml` 外所有部件与 cumulative 逐字节相等。`:177` 要求 `mr['pre_citation']==plan['source']`。

### 5. D3 的 21 处精确落实

源码 `BODY_EDITS` 8 键 + `range(2,10)` 8 格 + `STYLES` 5 键 = 21，与 `:64` 声明 `{8,8,5,total:21}` 一致。`:48` 硬校验 BASE `sha256==ff278c5b…`、`bytes==475988`。`:53` 要求每条字面在该段恰出现 1 次；`apply_target:91,99` 补丁前后各验文本与样式；`:153-155` 再逐条验接受投影。

**实跑 `expected_plan()` 与三份计划逐键比对：**

| 文件 | 六键匹配 | `validate_plan(approved=True)` |
|---|---|---|
| `C1_EXACT_PLAN_APPROVED.json` | 全 True | **PASS** |
| `EXACT_PLAN_NOT_READY.json` | targets False | `PLAN_EXACT_SCOPE_MISMATCH:targets` |
| `EXACT_PLAN_NOT_READY_v3_1.json` | 全 True | `PLAN_NOT_APPROVED` |

旧 NOT_READY 件的差异定位到 index 3（P182）：旧 2 处 replacements、现 3 处，措辞「因此，负向修饰不能直接写成」→「负向修饰也不能直接写成」，与源码 `BODY_EDITS[182]` 第三项一致。**已批准件是当前件，陈旧件被正确拒绝，NOT_READY 与已批准不会混用。**

### 6. 接受为精确补丁、拒绝回母稿；不把合成件冒充 native_saved

`compile_core:151-152`：`accept==desired` 语义、`reject==mother` canonical。`patch_clean`→`plain()`（`:42-45`）禁止域、脚注、图片、链接、控件、已有修订痕迹进入补丁范围。

`content_patched` 是「原生包 + 补丁后 document」的派生件。上游 `all_story_lineage_gate_v3.py:17-19` 把它绑为 `final_content`，`:22-23` 另行核实其 `fields()` 等于**真** `native_saved` 的 `fields()`，`:24` 把真来源单独记进 `actual_native_saved_provenance`。**两者分开，没有互相冒充。** `post_merge_narrative_v3.py:209-210` 再验 `content_patched` 字段 == `native_saved` 字段、`rejected_offline` 字段 == `mother` 字段。

`verify_qa:216-230` 重跑 preflight + compile_core，对四个产物逐部件比对，任何非 document 的无关部件一字节差异即 `PATCH_OUTPUT_UNRELATED_PART_CHANGED`。

### 7. 最终字段审阅绑定新 final_content；每条 runner 命令重核

`all_story_lineage_gate_v3.py:14` 调 `patch.verify_qa`（内部重跑，不信存盘 QA）；`:15-19` 验来源与三产物绑定；`:21` 要求 QA 内 checks 与现场重算逐字相等。

`native_adapter_review_guard_v3.py`：`:29` 要求 `READY_APPROVED`；`:34` 要求 manifest `FROZEN_APPROVED`；`:38` 拒重复 manifest 路径；`:44` 对 7 个模块（含自身、DELEGATE、CONTRACTS、GATE、LINEAGE、MERGE、PATCH）逐一 pin；`:46-47` 对 10 类证据、`:48` 对全部 dependency_pins 校验；`:49-50` 验 job↔request 五组路径绑定。**`:71-74` 的 `checked_run` 对每条 runner 命令重跑 `preflight`**，`:84-92` 七个委派阶段同样每次重核，`:59/:64` 拒重复配置。

### 8. freeze 只产 NOT_READY

`freeze_drafts_v3.py` 五处状态串全部以 `NOT_READY` 开头（`:53,54,67,69`）；`:32` 拒部分最终输入集（`PARTIAL_FINAL_INPUT_SET`）；`:37` 对象契约、`:39` 表 6 契约、`:41` 旧 job 预算各自硬拒。

### 9. 既有验证证据（引用落盘记录，本轮未重跑）

| 项 | 读数 |
|---|---|
| D2 `validation_20261006T164312360577Z` | `TEST_ONLY=true`、`returncode=0`、`native_calls=0`、`statistical_calls=0`；stderr 末尾 `Ran 24 tests … OK`；现货 SHA `af39b284532eebe3` 与台账一致 |
| D3 `validation_20261006T171256300802Z` | `status=OFFLINE_PREPARATION_PASS_NATIVE_NOT_READY`、`actual_native_receipt_created=false`、native/statistical/publication calls 全 0；三进程（test_suite / prepare_templates / freeze_not_ready）rc 均 0；stderr 末尾 `Ran 27 tests … OK` |
| D3 `IMMUTABLE_BEFORE/AFTER` | 各 66 条 pin 记录 / 56 唯一路径；**before↔after 零漂移；与现货零漂移** |
| D2 `MANIFEST.json` | 65 条 pin 记录 / **55 唯一路径**、`tests_passed=24`、`artifact_count=29` |

**计数口径纠正：** D3 HANDOFF 写「65 条 pins」——`references` 确为 65 条列表、`verified_references=65`，manifest 自身是第 66 条。我先前报的 66 是把 manifest 算进去了，HANDOFF 的数准确。root 裁定件的「24 测试/55 pins」与 D2 manifest 的唯一路径数一致。

---

## 不记为新增缺陷的事项

按 `verify` 要求区分：

1. **真实 `native_saved` 尚未到位** —— `INPUTS.json.state_boundaries[1]` 已声明属预期。当前仅以 TEST_ONLY 合成引文证明实现，不证明 Word/Zotero 真实通过（D3 HANDOFF:79 自述）。
2. **原生布局/几何/接受拒绝/PDF 全页质检** —— 只能在原生阶段验证，`freeze_drafts_v3.py:66` 的 `missing` 列表已逐条自述。
3. **D3 HANDOFF 的「待批准」措辞** —— 已被 `C1_EXACT_PLAN_APPROVED.json` 取代，`state_boundaries[2]` 与 HANDOFF:23 均有说明。
4. **root 当前的原生 UI 恢复代码** —— 按 `forbidden` 未读取、未触碰。

---

## 本轮覆盖与剩余限度

**逐行通读：** `bounded_field_merge_v2.py`(301 行)、`successor_contracts_v1.py`、`field_review_gate_v2.py`、`all_story_lineage_gate_v2.py`、`post_merge_narrative_v3.py`(237 行)、`all_story_lineage_gate_v3.py:1-30`、`native_adapter_review_guard_v3.py`(93 行)、`freeze_drafts_v3.py`(75 行)、D3 `HANDOFF.md`、root 裁定件。

**限度（明确声明）：**

1. `test_bounded_merge_v2.py` 读了 fixture(1-60 行) 与全部 24 个用例名，`test_post_merge_v3.py` 的 27 项**只核了名称与落盘通过记录，未逐项读实现**——因此不对它具体覆盖哪些负向场景下结论。
2. 按 `forbidden` 未重跑任何整套测试；24/27 这两个数字引用既有落盘证据，非本轮实测。
3. `all_story_lineage_gate_v3.py:30-99`、`prepare_v3_drafts.py`、`validate_preparation_v3.py`、`MERGE_REQUEST_TEMPLATE.json`、`REQUEST_TEMPLATE.json`、`PATCH_REQUEST_NOT_READY.json`、`FINAL_REQUEST_NOT_READY.json` 只核了 SHA 与计数，未逐行审阅。
4. **P1-1 的实测只证到 `compare_sources` 接受该变化**，未构造完整 request/receipt 走通 `build()` 全链（那需要真实 `native_saved` 与来源回执）。「会一路写进最终产物」是基于代码路径的推断，不是端到端实测。
5. 探针全部纯内存读取，未写任何共享目录。

## 下一步（具体可执行）

1. 修 P1-1：在 `bounded_field_merge_v2.py:165` 用已有 `oldf`，对 `ZOTERO_BIBL` 域加条目集合包含性检查，失败报 `BIBLIOGRAPHY_ENTRY_LOST`；补一条「域内删除被拒」用例。
2. 改 P2-1 的模块标签 `cmaverse_private_lineage_gate_v2` → `_v3`。
3. 补 P2-2 的 freeze 约束：`final_content` 非空 ⇒ `post_merge_qa` 非空。
4. 把 P2-3 的 15 个未阻断直通部件显式写进 scope review 清单，标注「列明待审」而非「已阻断」。
5. 上述修完再按 D3 HANDOFF 步骤 3-7 进入真实 `native_saved` 阶段。

本报告不声称原生或发布完成。

