# CMAverse V3j 审核纠错与研究稿交付（2026-11-02）

V3j 已完成原始评分与来源复核、28项逐段裁定、真实 Word／Zotero／PDF 验收，以及同一最终PDF的两轮六主题 NotebookLM 审查。原V3i保留作历史；不能继续把其常量表核对、合成NLM PASS或LibreOffice导出称为原生终验。

- [47页最终PDF](manuscript/CMAverse_V3j_final_accepted.pdf)
- [Word接受稿](manuscript/CMAverse_V3j_accepted.docx) · [修订稿](manuscript/CMAverse_V3j_tracked.docx) · [拒绝稿](manuscript/CMAverse_V3j_rejected.docx)
- [正文阅读稿](MANUSCRIPT_READING_V3J.md) · [逐段裁定](REVISION_COMPARISON_V3I_TO_V3J.md)
- [原AGY质量评审与优化方案](AGY_QUALITY_AUDIT_AND_OPTIMIZED_PLAN_V3J.md)
- [发表定位、中英文摘要及投稿信草案](PUBLICATION_DRAFTS_V3J.md)
- [两轮实际审查与本地裁定](review/FINAL_REVIEW_REPORT.md) · [失败请求保留说明](review/FAILED_ATTEMPTS_PUBLIC_SUMMARY.json)
- [第二轮引文样式与表头的实物核验](review/R2_T6_LOCAL_STYLE_AND_TABLE_EVIDENCE.json)
- [完整单包ZIP](CMAverse_V3j_verified_20261102.zip) · [包内文件SHA256](MANIFEST.json)

## 主要纠错

1. FEAS_031相对位置跃迁为1,559条区间记录，原342无依据。本人提高442、配偶下降1,372、两者重叠255；相对升级不能等同于绝对婚姻质量改善。
2. 新14项分为8项修饰和6项概率中介。六项逐项未调整B200区间均含0，端点范围−0.16778615至+0.31882160个百分点；不能据此证明普遍零效应、等效性或规范刚性。
3. 去dwm的新估计与保留dwm的历史搜索校正分开；delta检验的BH q与bootstrap区间分别标注来源。原模型及抽样不增加。
4. 28项修改保留2、修正21、回退5；相对V3h修改23段。34表、478行、2,956单元格内容保持；三稿保留20个正文引用域与1个书目域。

## 验收与范围

最终PDF SHA256：`ef99fcb202056bcfb1c3e559fb6b47f669f78d2b0c65dc2870003c7aab79f8d1`。两轮审查覆盖60个逐项检查，保留真实原答及152条原生来源引用记录。NLM答复中的不准确概括和“达到发表要求”等越界判断在各题ADJUDICATION中单独纠正；原答保持，不把平台PASS当作研究真理或期刊接收保证。

这是47页横向研究证据稿。投稿草案尚未实际投稿，也未按JMF／SSR当前官方版式确认完成；官方指南读取403的限制见发表草案。后续应先选定期刊，再派生主文和补充材料。

`results/`仅包含聚合结果；`code/`是本轮来源重核脚本，需要合法取得的本地冻结数据及历史文件，不能仅凭本公开包从零重建全部个体分析。未新增公开CFPS个体记录、账号凭据或整个AGY／NLM运行目录。历史原始回执保留各自当时的PENDING／失败状态；最新合并验收以本说明、最终PDF和两轮审查报告为准。

五个技能仓追加的是[经验纠错文档](SKILL_EXPERIENCE_CORRECTIONS_V3J_20261102.md)，固定提交核验见evidence/SKILL_CORRECTION_PUBLICATION.json；不代表共享代码或已安装runtime升级。
