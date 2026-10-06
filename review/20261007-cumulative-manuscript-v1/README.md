# CMAverse 累计论文修改与核验证据（2026-10-07）

状态：离线累计稿及来源核验已完成，可进行网页版内容复核；最终原生Word/PDF/同版NLM待完成。
统计冻结，无新模型或p值。当前裁定见REPORT.md；可转发说明见WEB_FEEDBACK.md。

阅读顺序：WEB_FEEDBACK.md → REPORT.md → EVIDENCE_TABLES.md → MANUSCRIPT_TEXT.md → 本次ZIP中的稿件原件和audit/lineage证据。
本目录全部payload文件同包提供；哈希清单MANIFEST.json明确排除自身。SOURCE_MAP将本机原件映射到包内路径。
一个ZIP；构建脚本实测小于25,000,000字节才允许发布。不要与旧包同名覆盖解压。

解压后执行：python3 verify_package.py
该脚本只读校验，不运行原R脚本或任何native任务。code和audit中原审阅脚本仅供溯源；其中历史绝对路径保留，便携入口才用于其他机器。

本包提供母稿、即时前驱和逐部件差异，以及120项执行输入日志；不再次上传微观数据或大型RDS。既有统计包保持原位。
不提供最新PDF的原因和后续验收范围见WEB_FEEDBACK.md。历史原生引文来源成功不能替代累计稿原生终验。
