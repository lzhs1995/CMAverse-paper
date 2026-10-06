# 筛选显著性：论文改文与来源补齐（2026-10-06）

本增量的统计结果已冻结，论文离线内容与来源核验完成；原生Word、Zotero刷新、最终PDF和同版NLM验收待完成。请先读取REPORT.md及ACCEPTANCE.json，再核对实际DOCX与结果表。不得把本增量称为论文原生最终交付。

## 本轮结论

- FEAS_031为优先探索候选，FEAS_041为相关操作化线索。两项去dwm后的未调整区间不含零，历史B=200搜索校正均未达5%。不拼接不同版本的点估计、区间与p。
- P3原金额整体p=0.131934，封顶整体p=0.079960；数值修复已在上一阶段完成。本轮只核查保存结果，未重跑模型。
- N1为人际/个人内辅助关联。最终六项BH/BY均未达5%；没有确认完整中介或普遍修饰机制。
- 本轮更新表10、新增表11—13、修正R6讨论和P3失败状态，删去表E.1旧NA说明；有限理论回溯没有把资源协商假说写成已识别机制。

## 在线入口（完整地址）

主报告：
https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/main/review/20261006-paper-closeout-v1/REPORT.md

给网页端的审阅顺序与范围：
https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/main/review/20261006-paper-closeout-v1/FOR_WEB_REVIEWERS.md

正文文本：
https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/main/review/20261006-paper-closeout-v1/manuscript/MANUSCRIPT_TEXT.md

完整增量包：
https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/main/review/20261006-paper-closeout-v1/paper_review_part01.zip

文件清单：
https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/main/review/20261006-paper-closeout-v1/MANIFEST.json

包验收记录：
https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/main/review/20261006-paper-closeout-v1/PACKAGE_QA.json

## 包内内容与验证

包含本轮离线DOCX及两个即时前驱、逐部件差异、9张来源明确的结果CSV、120项执行输入绑定日志、288份来源哈希记录、三篇原文的有限理论证据矩阵、复核附件、脚本和离线QA。旧11包/N1补充继续沿用，不重复上传。约198MB的120份执行输入原件不放入本增量；绑定日志不等于审阅者已读取这些RDS。

所有包必须小于25,000,000字节。精确大小、成员数和SHA见PACKAGE_QA.json；MANIFEST.json覆盖全部载荷文件，自身不做递归哈希，ZIP整体SHA由包外PACKAGE_QA.json登记。包外下载回执另行固定提交绑定。

下载包和verify_review_package.py后，用Python 3执行：

    python3 verify_review_package.py paper_review_part01.zip

该脚本验证完整CRC、每个载荷的字节数和SHA、JSON/CSV/DOCX解析，以及最新候选相对数值稿仅改变word/document.xml。它不执行R、模型或原生Word。

## 与前轮的关系

数值基线固定为687194000f275a73e83648e1c5362613ad8b0be4：
https://github.com/lzhs1995/CMAverse-paper/tree/687194000f275a73e83648e1c5362613ad8b0be4/review/20261006-numerical-closeout-v1

本轮候选SHA-256：ff278c5bba68ff7c6cdd0d52fc9cdd8fa7d2bac57876a2751fee8be3ddb4e95f。
来源/算术12项通过、正文表格9项读回通过、最终DOCX50项离线独立检查通过。它们各自有覆盖范围，均不代替动态引文刷新、实际分页或同版PDF终审。
