# 最小原生收尾 runner 独立审查

task_id：cmaverse-minimal-native-independent-20261007-r1
executor：surface:41 / claude，ordinal 1
审查时间：ACK 14:03:21，pack finalized 14:06:41，报告落盘 14:22 +0800（首份可执行结论在 30 分钟窗口内）
范围：只读审最小 runner 及其输入绑定，针对最终交付的关键缺口做一次有界独立审查。不重做旧正文审阅，不重跑全文 build/verify。

## 判决

**准备件可用；最终交付未完成，且当前被一个未满足的前置条件挡住。**

`initialize()` 实跑通过，111 项 pin 全部绑定成功，三个计算模块为纯文件计算。代码层没有发现会导致交付失败的 P1 缺陷。

挡住交付的是前置条件而非代码：旧票 `460c4293` 在真实队列里仍是 `ACTIVE`，`release_proof` 为 NULL。按 README 第 19 行的启动条件，它必须先真实 RELEASED。这项回执尚待 root 执行，依 pack verify 要求，不计作代码缺陷。

另有 1 条 P2 代码缺陷、1 条 P2 脆弱性、2 条 P3，均给出文件/行与最小修复。

## 输入 SHA256

| 文件 | SHA256 | 字节 |
|---|---|---|
| minimal_closeout_v2/run.py | c752cd8fddad95f28c8d008909dfaff4ece084e2e2349a2423af9db166733327 | 21162 |
| minimal_closeout_v2/check_preparation.py | 8d68104aba53759472462710eb36a0c3484ec47ad629b2872f099c299e54f043 | 3846 |
| minimal_closeout_v2/INPUT_PACKAGE.json | bd2c68021606d01d13a83a2fa99da3e154698c1262d9227dd0865dcf82cf2c45 | 49943 |
| minimal_closeout_v2/MANIFEST.json | a46c0c423d4ef0acbd9035d05f2b0718bd1c81f7f510198b57aca294ca049602 | 4750 |
| minimal_closeout_v2/PREPARATION_QA.json | 16b6f660a2d84ccf70e3b93ca0737f88fba5bb264d7b2acf311ebae5d874f867 | 5327 |
| minimal_closeout_v2/README.md | 59add5720ad98a6655a5ac4ce40032fbe4b92e577f9f52b812038e2711d6a378 | 5567 |
| minimal_closeout_v2/executor-report.md | ed135649e2646f3d757921f80e891d21d8fefad39feeaac56ed777bd5c88922c | 2984 |
| minimal_closeout_v2/HANDOFF.md | e55b35066de3e930a804bdf17191477076ca12b42ed87e10443530cbd31cceec | 1610 |
| minimal_closeout_v2/observe_ax.applescript | 9d843c7d77eb1f212313fa4b0e7c43ba8af147d17a744c7d0b626fa73ce545cb | 3057 |
| minimal_closeout_v2/observe_word.applescript | 08463932624b9bce6021765154177d7cfb9458d6182a2d6bad3143e67e52bf34 | 2437 |
| minimal_closeout_v2/INVALID_APPROVAL_TEST_ONLY.json | 9ca8dc77d1b7d2144b0ee2977e23fc6e6775298586f8bcdcf66b0e3ba83d2d12 | 93 |
| finalize_native.py | 0e8f3db94bb7b858878c2cbe0434f44a530eb73e997888dc70bc24057014ce75 | 301 行 |
| PROCESS_SOURCE_BINDING_REPORT.md | 9ee19c7f7e2b2c492f7eb047b2bf5cc8d61c60f198278e0943382a49b3aee8d5 | 60 行 |
| runtime.py（admissionfixed_v1） | 751b76db2f0c3211592d17b91b6a439da2d8e9c0ad3bab53a5c4c1ec8fde0000 | 298 行 |

## 六项 scope 逐项核验

### 1. 不重复全文 build/verify —— 确认成立

`run.py` 的 `initialize()`（58–103 行）只导入纯文件模块并核验输入，不实例化 Pipeline。`inspect` 实跑 5.66 秒、111 项 pin，无 Popen/sqlite3 调用。三个计算模块经 grep 确认不含 `subprocess` / `Popen` / `sqlite3` / `osascript`：

- `terminal_revision_cleanup_v1.py`（`compute`:27、`cleanup`:62、`signature`:16）
- `successor_contracts_v1.py`（`object_inventory`:66）
- `audit_actual_fields_readonly.py`（`inventory`:105、`snapshot`:274）

`JOB.json` 的 `statistics` 为 `{allow_execution:False, consume_manifest_only:True}`，由 run.py:65 强制；清单 `status=FROZEN_APPROVED`（run.py:66）。产出清单中 `native_calls=0`、`statistics_executed=False`、`build_or_verify_called=False`。

### 2. 修复 ID 后的 tracked 真实接受/拒绝 —— 绑定成立，原生动作待执行

`REVISION_ID_FIX_QA.json` 的改动恰为两处表格 `tblPrChange` 的 `w:id`（1001736→1001740、1001737→1001741），27 个 ZIP 成员中只有 `word/document.xml` 变化，其余 26 项 SHA 不变。全库 11655 个修订 ID 唯一。

`accept_reject_projection_equal: True` 不是空口断言：QA 带 18 行分部对照（accept 9 部 + reject 9 部），每行 `byte_identical_c14n: True`。

run.py:72–77 在 `initialize()` 里对 TRACKED 重新解压、重算全部 story 的 ID，实测通过（11655 唯一、无 None、CRC 通过）。真实原生 accept/reject 由 `revisions()`（195–225 行）执行，目前 `native_calls=0`，尚未发生。

### 3. 接受稿进入最终 Zotero/PDF —— 链路完整

`prior_phase()`（run.py:146–163）对 finalize 阶段强制 `c['candidate'] == e['outputs']['accepted']`（158 行），即 finalize 的输入必须正是 revisions 阶段产出的 accepted。`finalize()`（finalize_native.py:217–241）依次执行：打开 → 刷新前 Zotero 空闲核验 → `ZoteroRefresh` 宏一次 → 两次独立空闲观察（227–229 行）→ 保存关闭 → 重开再保存 → PDF 导出。

刷新前后用 `semantic()` 全等比较（231、233 行），覆盖九个 story 的文本、字段、媒体 SHA。PDF 以 `%PDF-` 魔数校验（238 行），并核验导出前后源文件 SHA 未变（239 行）。

### 4. 原母稿拒绝基线 —— 成立

`initialize()`（79–90 行）对 accepted/rejected 两分支都做了三重比对：cleanup 签名等于既有输出、`semantic` 等于 target、`object_inventory` 等于 target。实测产出：

- accepted：9 story / 37 对象 / 操作 `remove_terminal_paragraph_insertion_mark_keep_field_end`
- rejected：9 story / 24 对象 / 操作 `remove_extra_terminal_property_only_paragraph`

`JOB.json` 的 `source` 指向 delivery 下的当前整合稿，拒绝分支对的就是母稿基线。

### 5. 原生动作与保存重开证据 —— 判据真实可触发

每次派发前 `dispatch()`（finalize_native.py:102–123）两次核 gate、核 WORD_LOCK 与 FOCUS_LOCK 实持、读 ioreg 要求 HID 空闲 ≥8 秒，并落盘 intent/process/terminal 三联。`guarded()`（161–166 行）要求进入焦点后的即时场景等于焦点外的稳定场景，否则零动作。

保存由 AppleScript 内 `if not saved of docRef then error "SAVE_NOT_OBSERVED"` 断言（run.py:204、212；finalize_native.py:230、232），不是靠返回码推断。

HID 空闲实测：7.97 → 10.02 → 12.07 → 14.12 → 16.17 → 18.22 秒，准入阈值 8 秒可满足。`focus()`（runtime.py:177–215）的 45 秒窗口与 `dispatch` 的 `budget=min(35, remaining-6, focus_deadline-now-3)`、`word()` 的 `min_budget=31` 相容：实际需要焦点剩余 ≥34 秒，在 45 秒窗口内成立。

当前环境：Word PID 54034、zotero PID 41102，各一个进程，满足 `processes()`（runtime.py:107–117）的唯一性要求；`/Users/lzhs/.cache/wordrev` 下无 `*pending*` 残留。

### 6. 真实新票/FIFO 绑定 —— 代码成立，前置条件未满足

`row_snapshot()`（runtime.py:119–142）直接查真实 SQLite，要求本票 ACTIVE、token 匹配、无其他 ACTIVE 同资源票、前驱已 RELEASED 且有 release_proof。`history()`（finalize_native.py:42–67）按 `invocations` 核对 binding 数量，逐个验 argv 六段式、PID=PGID 唯一、进程组已空、三联齐全。阶段 invocations 预期 0/1/2 与 broker 的 `invocations+1`（resource_broker.py:168）一致，可满足。

旧四次历史只从旧票回执绑定（`predecessor()`，run.py:109–119），不混入新票 invocations，设计正确。

## 发现

### B01 阻断交付 · 前置条件未满足（不是代码缺陷）

旧票 `460c4293-0ca9-491f-9c20-6b7009d02a90` 在真实队列里的实测状态：

```
status      = ACTIVE        （README 第 19 行要求 RELEASED）
invocations = 4
release_proof = NULL        （require 非空）
```

同时它是 `word-zotero` 资源上唯一的 ACTIVE 票。这同时挡住两处：

- `run.py:112-118` `predecessor()` 要求回执 `status=='RELEASED'` 且 `release_proof` 非空，并与数据库逐字段一致。
- `runtime.py:132-136` `row_snapshot()` 要求「无其他 ACTIVE 同资源票」，旧票自身即为该冲突票。

因此新票租约按构造无法取得，三个阶段都无法 prepare。

`PROCESS_SOURCE_BINDING_REPORT.md` 第 60 行已记载同一事实：此前 cleanup 两次都在 UI 准入前失败，旧 pending 仍保留；60 秒采样显示 13 次锁均可获、HID 空闲均不足 8 秒。

但 HID 条件现已不同：本轮实测空闲可达 18.22 秒，远超 8 秒阈值。也就是说当初的失败原因（无空闲准入）当前不复存在，剩下的只是旧票的 drain + release 回执尚待 root 执行。

依 pack verify「不要把缺少尚待 root 执行的回执当代码缺陷」，B01 记为前置条件，不计缺陷。

**解除顺序**：先对旧票跑完 drain 取得真实 RELEASE 回执 → 旧票转 RELEASED → 再沿 FIFO 取新租约 → 主管按 README 第 21–32 行 schema 生成批准 JSON。

### F01 P2 · 代码缺陷：NULL release_proof 会抛 TypeError 而非判据失败

`run.py:117`：

```python
check(load_json(row['release_proof'])==e['release_proof'],'PREDECESSOR_PROOF_DB_MISMATCH')
```

`load_json`（run.py:120）是裸 `json.loads`。当数据库 `release_proof` 为 NULL 而回执文件声称 RELEASED 时，`json.loads(None)` 抛 `TypeError`，而不是给出 `PREDECESSOR_PROOF_DB_MISMATCH`。这正是旧票当前的字段形态，排障时会把一个清晰的判据失败伪装成解释器异常。

最小修复（run.py:117 前插一行）：

```python
check(row['release_proof'] is not None,'PREDECESSOR_PROOF_DB_MISSING')
```

### F02 P2 · 脆弱性：两个 pin() 的路径规范化不一致

| 位置 | 实现 | 是否 resolve |
|---|---|---|
| run.py:27-29 | `Path(p)`，只检查 absolute 且非 symlink | 否 |
| finalize_native.py:19-21 | `Path(p).resolve(strict=True)` | 是 |

两者的产出在跨阶段比较时混用：

- `finalize()`（finalize_native.py:233、241）用 **resolve 后**的路径写 `FINAL_EVIDENCE.json` 的 `final_docx`。
- `prior_phase()`（run.py:161）用 **未 resolve** 的 `c['candidate']` 与之比较：`c['candidate']==e['final_docx']`。

若操作者给 `--candidate` 或 `--binding` 传了含符号链接或 `..` 的非规范路径，drain 阶段会以 `FINAL_INPUT_UNBOUND` 失败，而真正原因是路径形态而非绑定错误。同理 `history()`（finalize_native.py:53）比较 `argv[3:]==['child','--binding',str(b)]`，其中 `b` 来自已 resolve 的 history，而 argv 里记的是操作者原始串。

实测当前无触发：111 项 pin 全部已是规范路径（resolve 后不变，0 例外；并用 `..` 构造的非规范路径做了负控，判据能检出）。属潜伏项。

最小修复（run.py:28）：

```python
p=Path(p).resolve(strict=True); check(p.is_absolute(),'ABSOLUTE_REGULAR_INPUT_REQUIRED')
```

或者在 `prepare()` 入口统一对 `--binding` / `--candidate` 做 resolve。

### F03 P3 · 冻结清单把一个无关的旧 runner 钉进了全部三个阶段

111 项 pin 里含：

```
private_native_successor_runner_20261007_v1/run.py
```

来源已定位：它是冻结 manifest（`status=FROZEN_APPROVED`，94 项 artifacts）中的一项，经 run.py:94 `sources.extend(... manifest['artifacts'])` 进入清单。不是依赖闭包引入的——我复刻 `project_module_paths()`（run.py:44-56）的真实闭包只得 10 个文件，不含该文件。

后果：`valid()`（run.py:41）在每个阶段的 prepare 与 execute 都会重核全部 pin，一旦有人改动这个与本次执行无关的 v1 旧文件，三个阶段会一律以 `PIN_CHANGED` 失败。

这是保守设计的合理代价，不建议在冻结清单上动手。仅建议在 README「准备验收与修复边界」一节补一句：111 项含 v1/run.py，执行期间该文件须保持不变。

### F04 P3 · README 第 62 行的「7项纯文件检查」与实测口径需对齐

`PREPARATION_QA.json` 记 `checks` 为 7 项、`elapsed_seconds=16.85`、`queue_access=0`、`real_lease_or_root_approval_generated=False`。我实跑 `inspect` 为 5.66 秒、111 项 pin。两者不矛盾（QA 含额外的 7 项检查），但 README 把「111 项输入按实际文件绑定」与「7项检查通过」并列，容易被读成同一次测量。建议在 README 注明两个数字各自的来源命令。

## 未核验项

- 真实原生执行全部未发生（`native_calls=0`）。本轮为只读审查，未派发任何 Word/Zotero 动作，未取租约，未生成批准。
- `accept all revisions` / `reject all revisions` 的 AppleScript 字面语义未经真机验证（需原生派发）。
- README 第 68 行称「修改页边距或表宽仍拒绝」已由实际 native DOCX 测试证明；我未复现该变异测试，仅静态核对了 `geometry()`（run.py:184-193）忽略六种 rsid 属性、保留 sectPr/tblPr/tblGrid/tcPr/trPr。
- 最终 PDF 视觉审阅与 NLM 同版未完成，`FINAL_EVIDENCE.json` 字段 `pdf_visual_review_performed=False`、`notebooklm_performed=False` 与此一致。
- 本报告不构成原生 Word 验收或 NLM 验收。

## 本轮产物

- 报告：`claude_minimal_native_independent_20261007_r1/executor-report.md`
- 实跑清单：`claude_minimal_native_independent_20261007_r1/verify/INSPECT_INVENTORY.json`（111 项 pin，status `INPUTS_INITIALIZED_NATIVE_PENDING`）

未在 artifact_root 之外写入任何文件；未触碰队列、锁、配置、共享文稿、统计与 GitHub。
