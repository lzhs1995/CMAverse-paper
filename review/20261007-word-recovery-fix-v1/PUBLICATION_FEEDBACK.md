# 给 ChatGPT 网页端的本轮交付说明

过期 Word 租约的恢复 bug 已修复、真实执行并安装，修复资料已上传。统计结果保持冻结。当前可以在线审阅修复和已有累计论文内容；最终原生 Word/PDF/NLM 验收尚未完成。

本轮资料固定提交：
1ba43a43745ba68d1456e97cd4e86d12c2f39d1d

详细报告（纯文本）：
https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/1ba43a43745ba68d1456e97cd4e86d12c2f39d1d/review/20261007-word-recovery-fix-v1/REPORT.md

完整增量 ZIP：
https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/1ba43a43745ba68d1456e97cd4e86d12c2f39d1d/review/20261007-word-recovery-fix-v1/word_recovery_fix_part01.zip

ZIP 为 30,759 字节，共 17 文件；低于单包 25,000,000 字节限制。
SHA-256：
4b6721e32e2c9848bdf051435d0b0d946bed0f47ed3dd37e92f25ea0e97a8d37

## 实际完成的事项

- 同一 V6 实现通过 41 项回归，两个 AppleScript 编译通过。
- 原票已真实 RELEASED；旧 token 在原 broker 中被拒绝。
- 全队列只改变原票 status 和 release_proof；外方未保存稿、权限模态、附属 sheet 原样保留；global_ui_ready=false。
- 可复用工具已安装，两个可变技能入口已更新；在安装目录再次运行 41 项测试和 --help 通过。其他现役客户端重载未测。
- 从解压包运行 verify_package.py --tests，16 项大小/SHA清单、CRC及 41 项测试通过。
- 该提交的全部 21 个新增/修改文件，已经从固定 raw 地址 HTTP 200 回下载；每个文件与本地逐字节一致。

核验脚本应在 ZIP 独立解压目录运行。仓库目录额外放有发布回执，不能把整个仓库文件集合当成 ZIP 的 manifest 集合。

## 请网页端审什么

请先读取 REPORT.md，再解压本轮 ZIP。重点评估：任务范围恢复是否明确区分旧任务空闲与 Word 全局空闲；未知观察和 NLM 未知是否继续拒绝；是否保留 FIFO、实际锁、完整日志和旧令牌失效。

公共 RELEASE_SUMMARY 和 INSTALLATION_SUMMARY 是真实本机回执的最小摘要，并含原件哈希；本包未复制全队列和外方凭据。不要将摘要审阅写成已独立观察现场 Word 或已逐一读取本机全部 400 份日志。

不需要重跑统计、重传旧包或重新生成 N1。031/041 仍是探索性修饰，P3 整体 p 为 0.131934/0.079960；此前历史选择校正没有支持确认性机制。

累计论文资料继续用：
https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/c0f6fac62dd20fa5d14c94b57d53344628290b39/review/20261007-cumulative-manuscript-v1/cumulative_review_part01.zip

## 仍待完成的论文步骤

2026-10-07 00:25:38 UTC 的只读队列核查显示，旧票已 RELEASED，本任务后继票仍排在 spatial、early2915 两票之后。没有跳队，也没有动外方窗口。

待后继票合法取得资源后，继续最终累计稿原生接受/拒绝、保存重开与字段检查、Word PDF 导出及逐页检查、同版 NLM 终审。已有 21 处改文和 3 份 Claude 审阅不重跑。本轮由 Codex 完成 solo_self_review，不将历史 Claude 审阅冒充本次修复审阅。

本地完整报告：
/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1/limited_followup_20261006_v1/paper_closeout_after_numerical_v1/resource_recovery_fix_20261007_v1/delivery_v6/REPORT.md

本地 ZIP：
/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1/limited_followup_20261006_v1/paper_closeout_after_numerical_v1/resource_recovery_fix_20261007_v1/delivery_v6/word_recovery_fix_part01.zip

本地安装验收：
/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1/limited_followup_20261006_v1/paper_closeout_after_numerical_v1/resource_recovery_fix_20261007_v1/install_v6/VALIDATED.json
