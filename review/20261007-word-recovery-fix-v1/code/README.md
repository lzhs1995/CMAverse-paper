# Word 过期租约的任务范围恢复（V6）

本机已授权恢复工具；默认只读。针对“本任务已经退出，但外方文稿或已识别外方权限模态导致旧票无法归还”的死锁。它不修改冻结 release 或原 broker；经真实核验后仅对目标旧票写入 status=RELEASED 及 release_proof。

## 已验证的边界

- 只有 word-zotero；NotebookLM 的远端未知状态不适用。
- 必须有真实用户授权记录，绑定过期票、当前 caller、实现哈希和期限。已有用户授权可据实记录，不再重复索取同一许可。
- 当前 caller 必须由 cmux identify 与 tree 交叉核对；不冒用原 owner。
- 完整 journal 目录集合、全部输入哈希、外层调用终态、内层 intent/result 必须对应；本任务进程组必须为空。
- Word 文档数、路径及 saved 标志必须真实可读，本任务所有已登记文稿必须关闭。外方未保存文稿原样保留。
- 观察到外方模态时，必须同时绑定完整模态指纹、真实 REQUEST 哈希/归属路径及数据库 WAITING 票。只允许 0 或 1 个有父级记录的直接 AXSheet；不遍历 sheet 的文件列表，不点击它。
- 未知计数、未知归属、Zotero 引文模态、超时、额外窗口/附属 sheet、日志改变、锁忙、活跃进程均拒绝。
- SQLite 事务及 broker/Word/焦点实际锁持有到提交；不删除或替换锁。旧 token 随 RELEASED 失效。其他票不变，FIFO 不变。
- 全局界面尚有外方模态时明确记录 global_ui_ready=false。旧票释放不等于可操作 Word，不等于原生论文验收通过。

## 使用顺序

1. 保留原失败、原 journal、原 owner 身份和原 broker。读取本任务旧票、资源映射、完整日志、实际锁 inode、当前 caller 及用户已给出的恢复授权。
2. 在新的任务恢复目录建立 AUTHORIZATION.json 与 CONTRACT.json。使用本安装位置的实现和两个观察脚本的完整路径、大小、SHA-256；不能直接重放历史契约，旧契约固定了旧实现位置和已释放票。
3. CONTRACT 的 schema 为 word-scoped-recovery-v1；必需字段包括 implementation、observer、ax_observer、authorization、lease（完整数据库行）、actor、valid_until、resource_root、resource_config、focus_lock、locks、journal_root、journal_sets、journal_paths、evidence、terminal_paths、owned_documents。特殊外层调用列入 special_launches；已核外方模态列入 foreign_dialogs。全部 journal_paths 必须等于 journal_root 下 **/*.json 的真实完整集合；evidence 应覆盖该集合及契约依赖。不能从中挑成功记录。
4. 先执行只读观察，使用新的绝对 output 目录：
   /opt/homebrew/opt/python@3.14/bin/python3.14 -B /Users/lzhs/.local/share/multi-agent-collaboration/recovery/word-scoped-v6-76e75aac8f02/resource_recovery.py --contract /绝对任务目录/CONTRACT.json --output /绝对任务目录/observe_01
5. 读取 OBSERVED_ONLY 回执和原始观察记录。门槛满足后，沿同一有效契约加 --apply，使用另一个全新 output 目录。该次会重新执行全部真实观察及锁/日志检查，不能只使用前一次观察。
6. 读取 COMMITTED.json，核数据库目标状态、其他票未变、旧 token 拒绝；按真实 caller 和 FIFO 申请后继票。任务继续完成可独立开展的工作，不把“原 owner 未回复”当成无限中止理由。
7. 若提交后回执写盘失败，读取 POST_COMMIT_ERROR.json 和数据库 release_proof，不能重复释放或谎报回滚。拒绝时保留 REFUSED.json，不删除旧输出重试。

## 验证与安装状态

源 V6 的 41 项回归、两个 AppleScript 编译、真实只读观察与真实释放已通过。安装位置另外运行相同测试；安装回执和加载回执分别保存。测试只使用临时数据库，不操作生产 Word。
安装测试命令：
/opt/homebrew/opt/python@3.14/bin/python3.14 -B /Users/lzhs/.local/share/multi-agent-collaboration/recovery/word-scoped-v6-76e75aac8f02/run_tests.py

reference_broker.py 是 hash 固定的原 broker 副本，仅供离线测试，绝不作为新的生产 broker。
不声明其他现役 Codex/Claude 已重载。测试或只读 --help 也不等于又完成一次现场释放。

