# Word 过期租约死锁修复与筛选任务接续说明

日期：2026-10-07。评审方式：solo_self_review。仓库：https://github.com/lzhs1995/CMAverse-paper

## 可直接反馈给 ChatGPT 网页端

本轮没有新增统计分析。阻碍“筛选显著性”论文原生收尾的旧 Word 租约已真实释放，并已安装可复用恢复工具。旧令牌被原 broker 拒绝，其他排队任务逐字段未变。外方未保存 Word 文稿、权限对话框和直接附属文件选择框保持原样，没有点击、保存或关闭外方窗口。

原生论文验收仍按先来先服务队列继续；释放旧票不等于最终论文验收完成。统计结果和已完成的 21 处累计改文均保持冻结，三份已完成 Claude 审阅不重派。本次没有把以往 Claude 参与记成新的协作。

## 1. 原因与实际修改

旧契约中“Unknown Word document counts and unknown remote query outcomes prevent release”要求未知状态不能当作安全。这个要求保留。导致中止的问题是把“本任务资源已空闲”与“Word 所有任务全局空闲”混为一谈，并把原 owner 未回应当作只能无限等待的条件。

已新增任务范围恢复入口：当前真实 caller 在已有用户授权范围内，核验旧任务的全部日志、进程终态、文稿归属和实际锁后，可安全释放其过期租约。不会冒用旧 owner；授权、实现哈希、票据快照、当前 caller 和有效期均绑定。生产旧 broker 和冻结 release 没有改写。

现场观察还定位了一个性能问题：权限对话框新增附属文件选择框后，旧 AX 探针使用 entire contents 遍历约 1,038 个元素，55 秒只读到约 172 项而超时。V6 仅遍历父对话框必要文本，遇直接附属 AXSheet 时保留父子归属和角色，不递归读取其文件列表。真实单次 AX 观察约 0.8 秒。此前所有超时记录保留。

## 2. 已完成的验证

| 项目 | 实际结果 |
|---|---|
| 源码回归测试 | 41 项通过 |
| 两个 AppleScript | 编译通过 |
| 现场只读 observe | 成功，前后 Word 与 AX 观察一致 |
| 现场 apply | 成功，旧票数据库状态 RELEASED |
| 原日志覆盖 | 400 份固定 JSON、24 次外层调用、31 次内部 intent |
| 锁与进程 | 持 SQLite 事务及三个实际锁到提交；旧任务进程组为空 |
| 本任务文稿 | 两份已登记文稿均关闭 |
| 外方界面 | 未保存文稿、权限模态和直接附属 sheet 保留 |
| 全队列差异 | 仅旧票的 status、release_proof 改变 |
| 旧令牌 | 原 broker require(..., allow_expired=True) 拒绝，LEASE_OWNER_MISMATCH |
| 安装后验证 | 安装位置再次运行 41 项测试，通过；--help 通过 |
| 两客户端入口 | Codex/Claude 可变 SKILL.md 已追加恢复入口，原内容保留 |
| 当前读取 | 当前 Codex 已读回；其他现役客户端是否重载未测 |

旧票编号：8bd72229-b774-46fa-89c7-3ffc829e85de。
实际恢复时 global_ui_ready=false；没有以“释放成功”冒充 Word 全局空闲。

## 3. 后续如何避免再次中止

1. 有现成用户授权时，由真实当前 caller 进入只读恢复核验，不重复索要同一许可。
2. 核验完整日志和归属；只有本任务文稿已经关闭、进程已退出、真实锁可获取时才考虑释放。
3. 外方窗口必须有精确归属和固定证据才能保留；未知计数、未知模态、活跃进程、锁忙、日志变化仍拒绝。
4. --apply 会重新观察和核验，不能复用旧观察来直接清票。旧凭据失效，后继按 FIFO 申请。
5. 继续推进不依赖 Word 的工作；不得把等待原 owner 回复作为整个任务永久中止的理由。

这不是通用的强制清锁或清队列工具，也不会解除 NLM 远端查询结果未知的限制。

## 4. 筛选任务当前状态

统计计算已完成且冻结：
- FEAS_031 去 dwm：ΔOR = −0.409351，未调整区间 [−0.668529, −0.150173]。
- FEAS_041 去 dwm：ΔOR = −0.085496，未调整区间 [−0.162804, −0.008187]。
- 上述去 dwm 版本没有新增 p，不能与历史 p 拼接。
- 历史 B=200 的同指标 120 项调整 p：0.134328 / 0.631841；合并 240 项：0.542289 / 0.915423。
- P3 原金额和封顶各 2,000 次有效，整体 p 为 0.131934 / 0.079960；六项 BH/BY 均无 5% 拒绝。
- 031/041 保留为探索性修饰线索，不是已确认的完整中介机制。
- 71.65% 的准确含义是升级记录中“本人评分未提高”，不能直接写为“只有配偶下降”。

21 处累计改文和三份 Claude 审阅已完成。最终累计稿的原生接受/拒绝、保存重开、动态字段、Word 导出 PDF、逐页检查及同一最终 PDF 的 NLM 审阅仍未完成。旧 PDF 的审核状态不能移植。

当前新票：1eb1c50a-1b71-42c7-86dd-24bd5d7c63bf；申请人为本次真实 caller。
最近一次队列检查：本任务前有 spatial 和 early2915 两票；原 grant 返回 WAIT_YOUR_TURN。没有代替其他任务领取或撤回票。

## 5. 本轮包与旧资料的关系

本轮包只包含修复代码、可独立离线运行的测试及固定 broker 测试副本、安装/释放摘要、日志和验证器。不重传旧 11 包、微观数据或论文。全量原日志与队列快照留在本机，公共摘要标明来源哈希；摘要不能替代对全部本机记录的独立审阅。

本轮公开证据是从真实本机回执提取的摘要，不声称网页端已独立重做现场释放。网页端可以复跑 41 项离线回归，核 SHA/CRC，并评估恢复规则。

已有累计论文资料：
https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/c0f6fac62dd20fa5d14c94b57d53344628290b39/review/20261007-cumulative-manuscript-v1/cumulative_review_part01.zip

旧接续状态说明（其中“仍待原 owner 释放”已被本轮事实更新）：
https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/ef1a42726a9c834170a893d4b7f00a3107a27bc7/review/20261007-followup-status-v1/PUBLICATION_FEEDBACK.md

## 6. 本机绝对地址

已安装恢复程序：
/Users/lzhs/.local/share/multi-agent-collaboration/recovery/word-scoped-v6-76e75aac8f02/resource_recovery.py

已安装完整说明：
/Users/lzhs/.local/share/multi-agent-collaboration/recovery/word-scoped-v6-76e75aac8f02/README.md

真实释放回执：
/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1/limited_followup_20261006_v1/paper_closeout_after_numerical_v1/resource_recovery_fix_20261007_v1/scoped_modal_v6/apply_01/COMMITTED.json

安装与测试回执：
/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1/limited_followup_20261006_v1/paper_closeout_after_numerical_v1/resource_recovery_fix_20261007_v1/install_v6/VALIDATED.json

原生论文剩余项继续通过合法后继租约推进；本轮修复已完成，不把修复成功写成论文最终交付全部通过。

