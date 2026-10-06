# 原生收尾只读审阅：旧票 drain / Zotero RunJS / 累计合并 / Word-PDF-NLM

任务：`cmaverse-paper-native-closeout-review-20261007` · 执行者 surface:2596 · 2026-10-07

本审阅只读。未操作 UI、锁、broker 队列、共享 DOCX 或 GitHub；未改共享代码；未跑模型。下文「已运行」只指 root 原会话留下的真实终态文件，不是我执行的。

以下路径均相对 `paper_closeout_after_numerical_v1/`；`RUN` = `native_readiness/short_successor_actual_release_v4/`。

## 结论

**有 P0，两项。** 旧票 drain 本身执行正确、按设计失败闭合；但 `word-zotero` 资源当前对所有其他任务死锁，且仓内没有任何现成脚本能解开它（P0-1）。`NATIVE_NEXT.md` §1 写于 drain 之前，其「从 06_suppress 接续」的路线已被 drain 物理作废（P0-2）。P1 四项，P2 三项。

| 对象 | 准备就绪 | 原生已运行 | 证据验收 |
|---|---|---|---|
| 旧票 drain（`RUN/expired_owner_drain_v1`） | 是 | **是**，16:17:18–16:17:29Z，exit 2 | 部分：Word 侧 4/6 达标；Zotero 两项 UNKNOWN；票未释放 |
| Zotero RunJS 观察（`RUN/zotero_runjs_observer_preparation_v1`） | 是（仅 payload + 合同） | 否 | 否 |
| Wang 原生引文 | 是 | 部分（01–04 + 宏），**已被 drain 取消** | 否 |
| 域感知累计合并 | 仅方案 | 否 | 否；尚无代码 |
| Word build/verify | 入口已 pin | 否；无 READY job | 否 |
| NLM 两轮 | 是（自报 15 项离线测试 PASS，我未复跑） | 否 | 否 |

## 输入 SHA256（前 16 位）

| 文件 | 字节 | SHA |
|---|---:|---|
| `native_cumulative_v1/NATIVE_NEXT.md` | 11072 | `ccb5b89d367c7ede` |
| `native_cumulative_v1/NATIVE_OBJECT_INVENTORY.json` | 17428 | `4e39c739ed44a932` |
| `nlm_readiness/README.md` | 8226 | `a0bb72a390ece40f` |
| `RUN/expired_owner_drain_v1/run.py` | 16288 | `7a63f982341ec157`（= CONTRACT pin） |
| `RUN/expired_owner_drain_v1/launch.py` | 1419 | `470ab754f33e9f16`（= CONTRACT pin） |
| `RUN/expired_owner_drain_v1/CONTRACT.json` | 4692 | `26a9a033572c16cc` |
| `RUN/expired_owner_drain_v1/DRAIN.json` | 766 | `b4baae2a696d02cf` |
| `RUN/expired_owner_drain_v1/EXECUTION_INTENT.json` | 8592 | `7d876c8049287376` |
| `RUN/expired_owner_drain_v1/HANDOFF.md` | 1574 | `fd5cc6724047137c` |
| `RUN/zotero_runjs_observer_preparation_v1/CONTRACT.json` | 3959 | `0484fa7848dcbe4b` |
| `RUN/zotero_runjs_observer_preparation_v1/READ_ONLY_RUNTIME.js` | 453 | `d1739af84f7bd834`（= 合同 pin） |
| `RUN/zotero_runjs_observer_preparation_v1/HANDOFF.md` | 2096 | `21186bd023c80b25` |
| `…/runJS.js.source.txt` | 3495 | `91485c6c4fed693f` |
| `…/keyboardHandler.mjs.source.txt` | 13248 | `ab16f48c4c1d0eaf` |
| `…/citationDialog.js.source.txt` | 102138 | `0b6dfb2768627834` |
| `resource_broker.py`（callback138） | 13776 | `27039b5941598825`（= CONTRACT pin） |

drain 目录共 98 个文件，逐个 SHA 已在审阅时列出；这里只列判据用到的文件。

---

## P0

### P0-1 `word-zotero` 资源全局死锁，仓内无可执行的解锁路径

**事实（已证实）：**

- `RUN/LEASE.json`：票 `062b2677…` `status=ACTIVE`，`expires` = 2026-10-06T15:38:45Z。drain 于 16:17:18Z 才开始，**租约过期 39 分钟后才收尾**。
- `resource_broker.py:130-133`：`grant()` 只要该资源存在任何 `status='ACTIVE'` 的行就拒绝，过期时报 `EXPIRED_LEASE_NEEDS_RECONCILIATION`。因此**所有其他任务**对 `word-zotero` 的 grant 都被挡住，与 Word/Zotero 共享串行资源的论文其余原生步骤一起停摆。
- 唯一出口是 `release(…, reconcile=True)`（`:180-220`）。它要求 `proof.observed_receipt` 指向一份 SHA 匹配的文件，其 `task_id` 等于行的 task_id，且对 `resources.release_requirements` 的**每一个键**做 `type()` 与值的严格相等（`:196-198`）。
- 现有唯一 receipt `DRAIN.json` 的 `zotero_current_doc`、`zotero_current_window` 都是 `null`，`unmet` 正是这两项，因此不可用于 release。
- `run.py:168` 在 `EXECUTION_INTENT.json` 已存在时拒绝再跑（`DRAIN_ALREADY_ATTEMPTED`），这是正确的一次性设计。RunJS 准备件 `HANDOFF.md` 第 12 步明确写「此处不编写或执行 release」。
- **结论：目前没有任何一份代码能产出六零 receipt 并调用 release。** RunJS 只交付了 payload 和合同，缺把它和 Word 复核、release 串起来的执行件。

**待核（我不碰 broker 库，未读取）：** `resources.release_requirements` 的真实值是否恰好等于 `run.py:16` 的 `REQ`（6 个键，`documents=0, windows=0, modal=False, pending=False, zotero_current_doc=False, zotero_current_window=False`）。若库中键集或类型不同，后继 receipt 会在 `:197` 报 `NATIVE_RELEASE_CONDITION_FAILED`。

**最小修正：** 在 `RUN/` 下新增**一个**任务内一次性后继件（不改 run.py，不复用 DRAIN.json），由 root 原 owner 执行一次：

1. 同 `identity()` / `verify_history()` / 三把同 inode 锁 / `focus()` HID≥8 的门禁（直接 import `run` 模块的这些函数，保持 pin）。
2. 按 RunJS 合同打开 Run JavaScript 窗，运行 pinned `READ_ONLY_RUNTIME.js`，从 `textarea#result` 读回原文。nonce、pid、initialized、profile、`at` 全部严格匹配，`currentDoc`、`currentWindow` 必须是 JSON 布尔。
3. 同一锁窗口内重新读 Word `count of documents/windows`、AX modal、全 cache pending。
4. 写**新** receipt（含 `task_id` 与 6 键），pin 后才调用 `b.release(TICKET, token, proof, reconcile=True)`。
5. 先用任务内假 broker/假 Word 夹具离线测：六零 → release；任一键 null/True/类型不符 → 不 release 且保票。

### P0-2 `NATIVE_NEXT.md` §1 的 Wang 接续路线已被 drain 作废

**事实（已证实）：**

- `NATIVE_NEXT.md` mtime 16:04:59Z，drain 在 16:17:18Z 执行，**前者早 12 分钟**。§1 要求按 `RUN` 最新 `NATIVE_RUNTIME.json` 判断下一步，并「原剩余顺序为 `06_suppress → 07_accept → … → 11_reopen`」。
- drain 实际做了两件不可逆的事：`cancel_bound_dialog.terminal.json` 记 `ONE_ESCAPE_SENT_NOT_COMPLETION`；源码 `keyboardHandler.mjs:108-110` Escape 派发 `dialog-cancelled`，`citationDialog.js:185-190` `cancel()` 调用 `io.cancel()` 和 `window.close()`。随后 `dialog_gone` 返回 `0`，`close_owned_no_save` 后 documents=0。
- `RUN/NATIVE_RUNTIME.json` 仍是 `CITATION_STAGED` / `ITEM_VERIFIED_AX_PENDING`，`result_identity=null`、`bubble_identity=null`。这是 drain 之前的状态，**已不描述任何现存的对话框或文档**。
- 不受影响的是：owned 文档关闭前后磁盘 SHA 都是 `ff278c5b…`（`DRAIN.json.owned_disk`，`run.py:206` 断言），与 `NATIVE_NEXT` 的「当前接受内容目标」同 SHA，前引文稿完好。

**风险：** 有人按 §1 字面「接续 06_suppress」，会对一个已关闭的文档和已取消的对话框发动作。

**最小修正：** 不改原文件。在 `native_cumulative_v1/` 新增一份 `NATIVE_NEXT_SUPERSEDED_BY_DRAIN.json`，钉住 DRAIN.json SHA，写明「Wang 引文需在 P0-1 释放后以**新票**、新 owned 副本从 01_open 重新开始；旧 06–11 不可接续」。新 grant 按 drain HANDOFF 建议用 `ttl=7200`：这次过期正是 600s 级租约覆盖不了 01→04+宏+恢复三轮的实际时长。

---

## P1

### P1-1 RunJS 的 Cmd-R 触发路径未被源码证明

`runJS.js:73-94` 的 `keypress` 监听器挂在父 `window` 上；`:119` 加载后 `codeEditor.focus()` 把焦点放进 `iframe#editor-code`（`runJS.html:22-27`）的 Ace 编辑器。从 pinned 源码看不出子 iframe 的 keypress 会到达父窗口监听器，`ace.html` 不在 pinned 源中。HANDOFF 第 4 步依赖 Cmd-R。

**建议：** 改为 AX 按下 nav 中的 Run 按钮（`runJS.html:8`，`onclick="run()"`），这条路径源码可证。无论哪种触发方式，成败只认 `#result` 内 nonce 匹配的 JSON；Cmd-R 无反应应记为「未运行」，不能记为失败或成功。Cmd-W 同理，关闭后必须实观窗口消失（HANDOFF 已要求）。

### P1-2 Ace 自动配对可能改写手打的代码

payload 含 `{ ( [ "` 共数十处。若 Ace 开启 behaviours，逐键输入可能插入多余的闭合符，导致语法错误。这一失败是**闭合**的：`run()` 的 `catch` 把异常写进 `#result`（`:28-33`），nonce 不会出现，票照样保留，代价只是浪费一次尝试。

**建议：** 用一次粘贴事件写入 pinned 字节，而非逐键输入；HANDOFF 已排除 AXSetValue，这一点正确。

### P1-3 currentDoc 仍为 true 时没有预定分支

HANDOFF 自己写明「Citation Dialog 消失不能单独保证 `Integration.currentDoc` 已清空」。若 RunJS 读回 `currentDoc:true`，当前合同既不允许重启 Zotero，也没有别的清理动作，票只能继续保留，P0-1 的死锁就会一直持续。

**建议：** 后继件运行前写定分支：`currentDoc` 或 `currentWindow` 为 true 时，只间隔一次再观察；仍为 true 就停止，向用户请求是否授权正常退出 Zotero（非强退）。不得改租期或伪造六零。

### P1-4 `DRAIN.json` 中的 `modal:false` 是空集上的真

`run.py:200-201`：Word 窗口数为 0，`flags` 为空列表，`all(...)` 恒真，modal 记为 false。Zotero 侧窗口因 RDP 不可用完全没有观察，`:205` 的 Zotero 窗口覆盖逻辑没有执行。所以 `modal:false` 只说明「Word 无窗口」。

**建议：** 后继件必须用 RunJS 返回的 `windows` 列表重算 modal：排除本次 `zotero:run-js` 窗，只要还存在未关闭的 `commonDialog.xhtml` 或 `citationDialog.xhtml` 就记 true。不得沿用 DRAIN.json 的值。

---

## P2

- **P2-1** drain `CONTRACT.json` 仍是 `status: PREPARED_NOT_EXECUTED`，`HANDOFF.md` 标题仍是「离线准备」，但目录内已有完整执行终态。建议另写 EXECUTED 回执，不改已被 pin 的原件。另外 `CONTRACT.argv` 是 `rtk proxy … launch.py`，`OUTER_INTENT.argv` 是 launch.py 派生的 `python3 -B run.py`，两者都是真实步骤，并不矛盾，但回执里应写明这层父子关系。
- **P2-2** `nlm_readiness/README.md:13` 说「既有授权允许本地规划 80→86」，没有引用授权记录的路径或 SHA。`allocate --apply` 会改共享账本，执行前应把授权出处钉进 manifest。
- **P2-3** NLM 两轮被**传递阻塞**：它需要五项 native freeze 共用一个最终 PDF SHA → 需要 Word build/verify → 需要 `word-zotero` 资源 → 卡在 P0-1。README 对此已自述「准备完成，尚未提交」，这里只是把依赖链显式写出。

---

## 已核通过（PASS）

**drain 执行（`RUN/expired_owner_drain_v1`）：**

1. pin：`run.py`、`launch.py`、broker 现货 SHA 都等于 `CONTRACT.json` pin；`run.py:170` 和 `launch.py:10` 都先验 pin 再动作。
2. 身份：`owner_initial` / `owner_launcher` / `owner_before_cancel` 的 caller surface `2A2CDBE8…`、workspace `26E665BA…` 都与 `run.py:9-10` 一致。
3. 历史：`launches/` 下 9 个 intent、9 个 terminal；`EXECUTION_INTENT.history` 有 18 个 pin（9 对），与 `verify_history()` 的 `len(intents)==row['invocations']` 一致。
4. 锁：三把锁按 inode+dev 身份 `flock` 后，`LOCKS_RELEASED_INNER` / `LOCKS_RELEASED` 按内到外的顺序落盘。
5. HID 准入：cancel 184.7s，close 8.4s，observe 9.8s，都 ≥ 8s；focus 持有 0.86s、1.30s、0.40s。
6. Escape 语义：源码证明 Escape 走 `cancel()` 而不是 `accept()`（`keyboardHandler.mjs:108-110`，`citationDialog.js:185-190`），不会意外插入引文。对话框身份由 AXRole、AXDescription 和检索框精确标题三重绑定（`run.py:185`）。
7. 只发一次 Escape，确认 `dialog_gone=0` 之后才关闭 owned 文档，`saving no`；Word PID 54034 前后不变；磁盘 SHA 前后不变（`:206`）。
8. RDP 判据：`zotero_unix_sockets` 的 lsof 显示 pid 8452 只持有匿名 socket。cache 下另有 8 个 `rdp.sock` 文件，属于其他历史 debugger 进程，被 `run.py:154` 按 pid 归属正确排除。没有因为文件存在就去连接，也没有探测 19876。
9. 失败闭合：`unmet` 非空 → `UNKNOWN_OR_OCCUPIED_TICKET_PRESERVED`，`FAILURE.json` 写 `ticket_release_not_claimed: true`，外层 `returncode=2`、`process_group_empty=true`。`EXECUTION_INTENT` 记录 `native_macro_runs=0`、`saves=0`。

**其他：**

10. RunJS payload 是只读表达式（只读属性加 `JSON.stringify`），nonce 已固定；`run()` 对字符串结果原样写入 `textContent`（`runJS.js:41-42`），读回无需 varDump 解析。
11. `NATIVE_NEXT` 的对象数可复现：inventory 源 SHA 与现货 `ff278c5b…` 一致；34 张实体表、3 个 drawing、37 个对象、30 个带题注的数据表；`tables[9]` 题注为「表6 模型5的标准化情境概率与加性交互」，9 行 × 9 格。
12. `NATIVE_NEXT` 点名的四处硬编码都真实存在：`freeze_drafts_v2.py:32` `(31,3,27)`；`native_adapter_successor_v1.py:79,81` `31/3/34`；`table23b_pdf_qa_v4.py:8` 旧题注「表2.3B…」，`:23` `tables[9]`；`compile_cumulative_v1.py:41-46` `protected()` 拒绝 `fldChar/instrText`，所以累计编译器确实无法承载实时域。
13. `wordrev` PATH 陷阱：`~/.local/bin/wordrev` 是 196 B 的 shell 包装，指向 `~/.codex/skills/…/word_revision_pipeline.py`（70933 B）；pinned release 的 pipeline 是 72877 B。`NATIVE_NEXT` 第 4 节的警告成立。

---

## 下一步（按顺序，均由 root 原 owner 执行）

1. 只读核 `resources.release_requirements['word-zotero']` 的 6 个键和类型是否等于 `run.py:16` 的 `REQ`。
2. 在 `RUN/` 新增一次性后继件（RunJS 观察 + Word 复核 + 新 receipt + reconcile release），先跑离线夹具，再按 P1-1/P1-2/P1-3/P1-4 的约束原生执行一次。
3. 释放成功后，写 `NATIVE_NEXT_SUPERSEDED_BY_DRAIN.json`；以新票、`ttl=7200`、新 owned 副本，从 `01_open` 重开 Wang 引文。
4. 取得原生保存稿后，再写域感知合并（目前没有代码），然后按 `NATIVE_NEXT` 第 3–5 节更新 37/30 合同并做 build/verify，最后进入 NLM。

本报告不声称任何原生步骤已完成。
