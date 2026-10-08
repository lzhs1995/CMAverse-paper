# 给 ChatGPT 网页端的提示词

以下全文可直接复制：

请继续复核我的“筛选显著性”任务。请直接读取以下固定GitHub版本的实际文件；能下载ZIP时请解压核验清单，不能下载时按START_HERE读取已展开文件，并明确实际读取和未读取的范围。不要仅凭摘要宣称完成全包或模型复核。

固定内容版本：0ffd3b2f9dbbdeed2f0d7f8ec1199f61b39fbf3b
报告：https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/0ffd3b2f9dbbdeed2f0d7f8ec1199f61b39fbf3b/review/20261008-significance-progress-v6/REPORT.md
读取入口：https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/0ffd3b2f9dbbdeed2f0d7f8ec1199f61b39fbf3b/review/20261008-significance-progress-v6/START_HERE.md
数据包：https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/0ffd3b2f9dbbdeed2f0d7f8ec1199f61b39fbf3b/review/20261008-significance-progress-v6/significance_progress_part01.zip
清单：https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/0ffd3b2f9dbbdeed2f0d7f8ec1199f61b39fbf3b/review/20261008-significance-progress-v6/DELIVERY_MANIFEST.json
ZIP大小：4,861,574字节；SHA-256：220a6c8ea58b96ef42c8f12dc63a3387827ce9556bd35126c29c2a419b8622e5。

这是v6阶段反馈，不是最终论文交付。本轮47份统计及来源文件与v5逐字节相同，无新模型、bootstrap或p值；无需重复已通过的统计核验，除非发现具体矛盾。

请重点独立核查：
1. manuscript/CHANGE_LOG.md与前驱、当前稿：表D.1已分别说明Logit的OR/OR差、万元/月金额差和log1p差值；“截尾”改成固定第99百分位封顶（pmin，保留全部记录）；附录E.4仅改引导语。确认22个结果行、表内数值及单位未变，未引入新的尺度混淆。
2. native/revisions/中的真实Word接受全部、拒绝全部及保存关闭重开证据。拒绝参考应回到指定2026-10-05母稿。区分这些真实产物和离线投影。
3. 原记录更正：native/refresh_attempt/native_030.terminal.json为MACRO_RETURNED_NOT_COMPLETION，随后RESULT为SCENE_CHANGED。一次Refresh调用不能证明完整刷新、最终保存重开及书目保全通过。最终Word PDF和同PDF两轮NLM尚未完成；不要要求盲目重放已调用的操作，也不要把历史窗口状态当作当前Mac状态。
4. 研究结论是否仍准确：031/041去dwm后的ΔOR及未调整区间只支持探索；历史B=200搜索校正不能贴到去dwm后的点估计上；P3整体p=.131934/.079960；在已检查范围内未确认完整中介或最佳机制。相对满意度位置变化不等于本人婚姻幸福改善。

请给出“通过／需修正／尚无证据”逐项裁定，具体到文件和段落；仅提出对收尾有必要的最小修改及明确验收条件。原始CFPS和120份大型执行对象未重复上传，输入绑定日志不等于逐份重读。不扩大显著性搜索，不重复要求已经解决的图号、C3/C4、长表注修改。最后提供一段可直接反馈给本机Codex的执行意见。

