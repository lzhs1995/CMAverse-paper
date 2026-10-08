# 三处改文差异独立复核报告（cmaverse-minimal-diff-review-20261007-r2）

执行者：Claude（surface:41，executor 1），主管：Codex surface:40
复核时间：2026-10-07 18:44–19:08 +0800（本机 `date` 实测）
任务包：`claude_minimal_diff/task-pack.json` sha256 `56224d91d262365ed8add64132dad89c7b1ddd4ec62ddfcbe8d388d4522ee6cf`，finalized_at 2026-10-07T10:44:07Z

## 结论

**OFFLINE_PASS_NATIVE_PENDING**。

依据：我写的独立脚本检查 87 项，失败 0 项；6 个负对照全部被预先点名的检查项命中。没有 P1 或 P2 缺陷，另有 4 条 P3 观察。

这是离线投影的通过，不等于原生验收。四稿均未在 Word 中打开、未刷新域、未分页，原生接受与拒绝也没有执行。

## 一、实际比较对象（运行前后各核一次，8/8 与 7/7 均未变化）

任务包 input_pins：

| 文件 | sha256 |
|---|---|
| build_minimal_manuscript_v1.py | e7535cf9f3fca1d55152e9991170e7b5c5c0327e9b09025dc0dea737851aace0 |
| manuscript_v1/content_patched.docx | e59df3f3a24ca329df68f08488db1e472b925d110b4c51506f0b68d62b7c7f1f |
| manuscript_v1/tracked_patched.docx | 5cfe672ebafa64a32bfaf37a8b1d8015f54bcbf285bec002e02e50d7f4658222 |
| manuscript_v1/accepted_offline.docx | b77fa7e5612280f943c73a4a2f8f9f3b0e0897cefa1e0bcecb9b8e06aec7e148 |
| manuscript_v1/rejected_offline.docx | 51eeb527a4da11b9429f168a418c685d8a58a2eb1d64b3482566b44d9c4304fd |
| manuscript_v1/OFFLINE_QA.json | a4f17a13ce34030324e369ba7636c8571db5aeb3b418ac2f4312fce0dd1cd7ca |
| manuscript_v1/MINIMAL_PLAN.json | 7245d7c946555bd68240ce915fb80936c8ab95172f008cdf20ea6c8c2c6ea7b2 |
| manuscript_v1/SOURCE_BINDINGS.json | 11dea10cb6163985c537de71d2dad50dee31e4283a9a816a72978c0796518a4b |

绑定的前驱与母稿（以 SOURCE_BINDINGS 为准，逐一现算一致）：

| 角色 | sha256 |
|---|---|
| 旧 content_patched（/private/tmp/cma-web-delivery-20261006/…/manuscript/） | 03603a06a527a98c8710e91bc8c5734028377d01fd44c4ce0b9e3f6269f7bc57 |
| 旧 accepted_offline | 5063b21a076d79a5037a99dc2feece9928d95eb1dd697d07da06f9989539d8bf |
| 旧 rejected_offline | f420b617893a57e2fc16eb71248fd23d43e0e601674b43a08a32a50b5040d9c1 |
| 10 月 5 日母稿 | 4f8cb6c2963c52efaf7cc1065110783ddefdc586785cce15f401d71e2787123d |
| tracked 前驱（revision_id_fix_v1/tracked_revision_ids_fixed.docx） | d25d18b9bc51aa71d37cbbc0521f4efc2356c900176870d6c5fee188fc30a89d |
| compiler post_merge_narrative_v3.py | e3d125ec74e8968cafc811bc1462313c5d1a24eea69db763514a014c39c43451 |

本次复核产物：

| 文件 | sha256 |
|---|---|
| independent_diff_review.py | ee27d01e2caa8e75f84bdd15f56fa5d7bfb7f10929df6fcb53017efe8ad9ba41 |
| negative_controls.py | d42960d2f575f085f4df74c869ec3a6e26ea6c2fc9df968dc69d465293e9c679 |
| review_out/INDEPENDENT_REVIEW_QA.json | cda5e0be5d9cb73aaaf2ddc1f509eca0bd75f4f85c83d08f3ca23cb7c4ffdd0e |
| review_out/NEGATIVE_CONTROLS.json | e2374663cb94016e5866a577b68aa216752883f821e8108c67bb905a5dfb4723 |

独立性：脚本只用 zipfile 和 lxml 6.1.1（python3.14），**没有**导入构建脚本的 `m` 或 `prev` 模块。修订元素清单、接受与拒绝投影、域解析都是我自己实现的。

## 二、命中差异位置

正文段落序号以接受态或 content 稿为准，tracked 稿内对应的序号写在括号里。

| 段 | tracked 序号 | 变化 | 核对 |
|---|---|---|---|
| P221 | 225 | 表D.1 尺度说明整段替换为 SCALE 文本 | 见三 |
| P253 | 257 | 「截尾。」改为「封顶（pmin，保留全部记录）。」 | 见三 |
| P282 | 286 | 「注：」改为「表2变量构造的完整说明如下：」，其余 1,280 字逐字不变 | 前缀替换判定为 True |

- content_patched 与旧 content、accepted_offline 与旧 accepted 相比：c14n 层和纯文本层的变化段都**恰为 [221, 253, 282]**，段数都是 309/309。
- tracked_patched 与前驱 d25d18b9 相比：变化段恰为 tracked 225/257/286。表格及其他正文元素（38 个）c14n 全等。
- 三处在 tracked 稿中接受后等于批准的新文本，拒绝后等于旧文本。
- 部件层：三组比较都只有 `word/document.xml` 变化，其余部件逐字节相同。

## 三、三处改文的语义核对

**P221（表D.1 尺度）**：与紧随其后的表D.1（第 25 表）“尺度”列逐行对照。
- FEAS_003、004、031、041 的尺度为「边际OR」和「边际OR之差（ΔOR）」，对应新文本中的“Logit 规格：TNIE 为标准化边际 OR，log 尺度检验无效值 1；Delta_CDE 为两个边际 OR 之差，无效值 0”。
- FEAS_060、091、092、093 为「万元/月」，对应“support_diff_10k 线性规格以万元／月表示”。
- FEAS_107、142、143 为「log1p(金额/10000)差」，对应“support_log1p_10k 为变换后差值，不解释为元／月或百分比”。
- 表头末列为「原始探索p」，对应“表内 p 值均为历史探索版本的未调整结果”。
- 三类尺度与表中 22 行一一吻合，没有错配。

**P253（R6）**：新口径与全稿的封顶表述一致，旧词「截尾」和这些表述矛盾。
- P176：“封顶用固定阈值 pmin 处理，没有删除大额记录”。
- P273：“封顶采用 pmin 固定阈值，不删除上尾记录”。
- P274：“封顶阈值固定为 2,664.29840142096 元／月”。
- P98、P174 和表17 使用「预定99%封顶」。
- 全稿接受态中「截尾」已无出现。P282 中的「缩尾」指收入变量，与 R6 无关。
- 我**未**读 R6 的 R 代码；“保留全部记录”的实现依据是正文 P176 和 P273 的既有表述（见六）。

**P282（E.4 起句）**：结构位置和文意都成立。
- 上一段 P281 是标题「E.4 变量构造说明」。
- P104（表2 注）末句「完整说明及已完成的敏感性核查见附录E.4」保持不变，与新起句「表2变量构造的完整说明如下」前后呼应。
- 原“注：”放在附录正文开头属于格式错位，本处修正是正确的。

## 四、保全检查（全部通过）

- **P104**：在 content 和 accepted 中 c14n 均不变。
- **34 表**：两稿都是 34/34 c14n 全等。表D.1 的表头加 22 行逐单元相同，单位集合为 {边际OR, 边际OR之差（ΔOR）, 万元/月, log1p(金额/10000)差}。P222 的规格记录数/簇数不变。
- **9 个 story**：document、footnotes、endnotes、header1–3、footer1–3。除 document.xml 外，8 个 story 逐字节相同。
- **23 引用 + 1 书目域**：正文 20 条、脚注 3 条 ZOTERO_ITEM，加 1 个 ZOTERO_BIBL，共 24 个域。所有 story 中的域指令串及其顺序与旧稿完全一致。我首次只统计 document.xml 得到 20，属于计数口径错误，已改为统计全部 story。
- **25 条书目**：「参考文献」位于 P283，其后 25 段与旧稿逐段相同，旧顺序保留。
- **目标段格式**：三处的 pPr 与首 run rPr 不变，没有丢失的域、书签、超链接、脚注引用或图形对象。
- **修订 ID**：tracked 稿所有 story 中共 11,655 个修订 ID，全部唯一。新修订为 1001742–1001744，作者 Codex，日期 2026-10-07T10:50:00Z。前驱的最大 ID 为 1001741，所以新 ID 不碰撞。总数不变，原因是三处在前驱中原有的末尾 ins（1001700/219/1001735）被新 ins 取代，并非新增。
- **接受投影 = 新内容**：我自己实现的接受投影与 accepted_offline 在 9 个 story 上的文本全部相等。
- **拒绝投影 = 母稿**：
  - 我自己实现的拒绝投影与 rejected_offline、母稿 4f8cb6c2 的文本三者相等。
  - rejected_offline 与母稿逐部件比较时，story 用 c14n，[Content_Types] 忽略 Override 次序，结果全等。
  - rejected_offline 与旧 rejected 逐部件全等；zip 字节 SHA 不同，只来自容器元数据。
- **无残留修订**：content、accepted、rejected 三稿中的修订元素数均为 0。

## 五、缺陷与观察（按严重性）

没有 P1 或 P2 缺陷。

- **O1 P3｜P221 删去了两条澄清**。旧文本有“ΔOR 不能解释为百分点”和 support_diff_10k、support_log1p_10k 的构造定义（÷10000、两期 log1p 之差），新文本已不再包含。log1p 尺度在表D.1 的“尺度”列仍然可见；“不解释为百分比”只针对 log1p 规格，没有覆盖 ΔOR。按批准计划这属于有意的重写（见 MINIMAL_PLAN 的 SCALE），所以不判为缺陷。若想保留，可在“无效值为0”后补一句“不解释为百分点”。
- **O2 P3｜斜杠风格**。正文写作「万元／月」（全角），表D.1 单元格写作「万元/月」（半角）。语义相同，属于全稿既有的混用，不是本轮引入的。
- **O3 P3｜修订日期**。新修订的日期为 10:50:00Z，而 tracked 稿的 mtime 为 10:35:09Z，即修订日期晚于文件写盘时间。它与前驱中已有的 12:00:00Z 修订同属合成时间戳。只影响 Word 修订窗格显示的时间，不影响内容。
- **O4 P3｜ID 空间重叠（既有）**。修订 ID 中的 1 和 2 与书签或批注 ID 相同。前驱中已存在同样的重叠，不是本轮引入的。

复核脚本自身的问题已在交付前修正，均为我的测量口径错误，不是稿件缺陷：
1. 首轮未处理行级 w:trPr/w:ins|del，导致投影文本不等。
2. .rels 文件未做 c14n。
3. [Content_Types] 的比较对次序敏感。
4. 引用只统计了 document.xml。
5. tracked 序号未映射到接受态序号。
6. 负对照 drop_row_level_del 暴露出 tracked 对前驱的比较不管辖表格。已补上检查 `tracked:tables_and_other_body_equal_raw`，复跑后命中。

## 六、负对照（NEGATIVE_CONTROLS.json）

在内存中变异输入，不写盘。基线失败为 0。下表的“命中”指预先点名的检查项全部失败：

| 变异 | 命中检查 |
|---|---|
| 表D.1 首行估计改一位 | tables_34_c14n_equal、D1 逐单元 |
| P104 加一字 | P104_unchanged、changed_paragraphs |
| P222 额外改动 | changed_paragraphs、projection_accept_text |
| 删一条 ZOTERO_ITEM | fields 顺序、23+1 计数 |
| 制造重复修订 ID | revision_ids_unique |
| 删一个行级删除标记 | projection_accept_text、tables_and_other_body_equal_raw |

## 七、未做事项

1. 没有任何原生操作：未打开 Word，未刷新 Zotero 或域，未分页导出 PDF，未执行原生接受或拒绝。native_calls = 0。
2. 未读 R6 的 R 代码，也未重算第 99 百分位阈值或 pmin 的实现。“保留全部记录”只与正文既有表述做了一致性核对。
3. 未重跑模型或 bootstrap，未重审旧 21 处，未做统计审查（均为任务包禁止项）。
4. 未修改四稿、原脚本、统计、现役 skill 或其他 agent 目录。只在本目录写入两个脚本、review_out/ 下两个 JSON 和本报告。

**准备可用与最终交付的区分**：四稿离线结构与三处语义复核通过，可以进入原生阶段。最终交付仍需要原生 Word 打开、接受和拒绝核对、域刷新与导出，以及相应的回执。
