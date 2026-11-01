**CMAverse 因果中介论文：任务初衷、网页清单、研究结果与交付总报告**

报告日期：2026年11月1日（台北时间）。本次论文工作稿、原生文件、同版NLM终审、指定GitHub及百度交付已完成。磁盘40 GiB曾于08:06和08:10验收达标，但08:57的新复测已降至35.698 GiB，当前未保持40 GiB。原先希望找到经搜索校正支持的清晰中介或最佳机制，现有证据没有达到该研究结论。计算和交付结项、假设是否获得支持分别报告。

[47页最终PDF](https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/3ae3311ca95e5ad9cf06d57d70fff771d6b30bed/final/20261101-v3h/package/manuscript/CMAverse_V3h_final_accepted.pdf) · [Word接受稿](https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/3ae3311ca95e5ad9cf06d57d70fff771d6b30bed/final/20261101-v3h/package/manuscript/CMAverse_V3h_final_accepted.docx) · [修订对照稿](https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/3ae3311ca95e5ad9cf06d57d70fff771d6b30bed/final/20261101-v3h/package/manuscript/CMAverse_V3h_final_tracked.docx) · [完整交付ZIP](https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/3ae3311ca95e5ad9cf06d57d70fff771d6b30bed/final/20261101-v3h/CMAverse_V3h_final_20261101.zip)

**你的任务初衷**

研究收入变化是否通过本人及配偶婚姻满意度影响向父母提供的经济支持，并区分完整中介、固定状态修饰、基期状态修饰和直接关联；恢复并继承已有CMAverse/paired-mval分析、原稿、表图和来源。在ChatGPT Pro、Claude网页建议和本机核验的基础上完成有限探索、准确改稿、原生Word/PDF、NLM审读，最后交付到指定仓库。

最初的“寻找有证据的合理组合”经过多轮核查，已收束为：如实展示中介未获明确支持、031/041探索性相对评价修饰线索、P3整体未拒绝的论文工作稿。10月6日至8日的原始执行单明确要求停止追加模型、编码、切点、检验次数和显著性搜索。磁盘清理、工具修复和协调均是完成论文的辅助工作。

**实际收到的ChatGPT与Claude网页任务是什么**

以下基于本机保存的网页导出原件及既有归档，不把本轮说成重新打开了网页会话。14份网页原件已按原字节附在[来源目录](report_sources/)，含完整标题、SHA和字节数的[来源清单](report_sources/SOURCE_MANIFEST.json)；另附1份本机已批准的执行修订。

| 来源及阶段 | 原始任务内容 | 最终如何执行 |
|---|---|---|
| ChatGPT Pro，10月5日[有界探索审阅](report_sources/01_探索方案审阅与修订建议.md)及[v3定点优化](report_sources/融合方案v2_审阅与定点优化_v3.md) | 保留150项历史；审查端点编码、dwm时间属性、干预支持、效应尺度、联合不确定性和多重比较；有限增加基期修饰、有序中介、两部分金额、三波链 | 与Claude方案融合；不采用“B200数学上不可能拒绝”或用Delta法绕过联合不确定性的旧表述 |
| Claude网页融合方案[v2](report_sources/20261005_ChatGPT-Pro建议对照与融合方案_v2.md)→[v4](report_sources/20261005_astra本地执行方案_v4.md) | Step0数据/代码自检；A1—A4、B1—B4、C1—C4、D1—D2主族；S1—S4次级族；R1—R11/PO诊断；11个历史候选；理论、论文和证据交付 | v4的33行登记含条件替补及诊断，不是33个独立主假设。C3/C4实际采用经济贡献满意度，不将其改称总体婚姻满意度 |
| 用户效率要求形成的[两阶段计算修订](report_sources/TWO_STAGE_COMPUTE_AMENDMENT_v1.md) | 将原“主项立即B2000”改为全14项先B200，只有预定规则合格者精化 | 14项初筛完成；没有合格项晋级。没有再全跑14项B2000是按批准规则收尾，不是遗漏；S4仍独立完成B2000 |
| ChatGPT Pro，10月6日[限定后续方案](report_sources/01_筛选阶段复核与限定后续方案.md) | 只跟进P1=031、P2=041、P3原金额/固定封顶，核失败原因；N1保留冻结来源，六项统一校正 | 限定复核及同似然数值修复已完成；历史搜索矩阵的RW型校正完成；未递补新赢家 |
| 10月6日[数值独立复核](package/source_requests/00_数值收尾独立复核报告.md)、[论文收尾执行单](package/source_requests/01_Astra_Mac_论文收尾执行方案.md)，10月7—8日[v5/v6复核](report_sources/00_v6实质复核与分项裁定.md)、[有限接续单](report_sources/01_给Astra的Mac有限接续执行单.md) | 版本与来源统一、120输入记录/即时前驱、有限理论回溯、表10—13和正文改文；核已有Word回执及XML差异，最终PDF、同PDF两轮NLM、一次最终发布 | 下列W01—W12均有对应交付；历史失败、拒绝意见和未确认机制保留 |

早期v2中的Delta主推断、模块内校正优先、按第一段显著才做D等建议已被后继修订撤回。不能把各版提案累计相加后，称这些被替代的建议仍然欠做。

**统计工作的实际进度**

| 工作 | 已执行结果 | 当前解释 |
|---|---|---|
| 既有40基础模型、总体八链、48个有限异质性组及paired-mval资产 | 已继承与恢复，保存在代码/结果档案和来源索引；本轮未重跑 | 恢复文件、执行成功、可报告推断分别判断 |
| 原150规格和旧11候选 | 150登记中120可估、30不适用；每个可估规格2目标，共240个历史目标；旧11项B1000已单独归档 | 不是150项全部成功，也不是240份独立样本 |
| 新14主检验A/B/C/D | B200初筛完成；13项可正常列报，B1为195/200有效，低于98%门槛；合格项晋级0 | B1有诊断p但不发布正常p/q；不把不稳定当作不显著 |
| 合成零机制校准 | a=0、b=0、二者皆0，各100组，拒绝次数0/1/0；[冻结结果](report_evidence/CALIBRATION_SUMMARY.csv) | 仅所检查的数据生成过程，不能推出普遍I类错误已校准 |
| 次级S1—S4 | 四项均B2000完成；S2原始p=0.015492，BH4=0.061969；[原表](report_evidence/SECONDARY_S4.csv) | S2是收入关联的性别差异，不替代婚姻满意度机制 |
| R1—R11及辅助/稳健性结果 | 已形成226行汇总，正文附录D.5—D.9保留结果与失败；226包括组件、直接/总量和诊断 | 不是226个独立机制检验；部分金额模型仍因有效重复不足而暂缓 |
| P1/P2限定复核 | 去dwm、分期及逐簇影响检查完成；031/041分别有2939/3149个有效逐簇剔除拟合 | 点稳定和分期同号不等于独立复制或每个区间均显著 |
| P3原金额/固定99%封顶 | 同样本、同模型、同抽样下完成数值修复，两口径各2000/2000有效 | 原49次失败已经修复；整体证据仍不足 |
| N1四项及固定六项家族 | N1来源齐全；N1四项+P3两项的最终BH/BY表已固定 | 没有5%校正后拒绝，N1不报告为中介或调节 |

**研究结论究竟是什么**

| 对象与版本 | 关键结果 | 能说到什么程度 |
|---|---|---|
| FEAS_031去dwm模型 | ΔOR=−0.409351，未调整95%区间[−0.668529, −0.150173]；9879条/2939簇 | 最突出的探索性相对评价修饰线索；未为这个修订模型新增p或搜索校正 |
| FEAS_041去dwm模型 | ΔOR=−0.085496，未调整95%区间[−0.162804, −0.008187]；12564条/3149簇 | 相关操作化线索，不能当作031的独立复制 |
| 031历史B200模型 | 原始p=0.004975；同指标120项调整p=0.134328；合并240目标调整p=0.542289 | 搜索背景校正后未达5%；这些值不挂到去dwm行上 |
| 041历史B200模型 | 原始p=0.039801；120项调整p=0.631841；240目标调整p=0.915423 | 同上 |
| P3期末总体月均支持金额 | 原金额整体p=0.131934；固定99%封顶整体p=0.079960；BH6分别0.158321/0.119940 | 收敛修复完成，整体修饰未在5%获支持；不能用旧辅助5对4的p=0.035928替代 |
| 完整中介/模型化TNIE | 现有执行结果没有清晰的完整中介支持 | 不能说机制已确证，也不能说婚姻关系作用已被证明为零 |

ΔOR为两个边际OR之差，不是概率百分点。031相对位置升级中本人评分提高28.35%、配偶下降88.01%，二者可以重叠；不能改写成“本人婚姻改善”，也不能把相对评价直接等同于权力。P3是期末金额水平，封顶采用固定2,664.29840142096元/月的pmin，保留原记录。原金额与封顶是不同估计口径。

**网页收尾要求逐项对照（沿用原W编号）**

| 编号 | 原要求 | 状态 | 实质成果 | 证据 |
|---|---|---|---|---|
| W01 | 停止新增显著性搜索，保留探索及不显著结果 | 已完成并按停止规则结项 | 统计执行已冻结；本轮报告未运行R、模型或bootstrap。 | [01_Astra_Mac_论文收尾执行方案.md](report_sources/01_Astra_Mac_论文收尾执行方案.md) |
| W02 | 五种结果版本分开，去dwm结果不拼接历史p | 已完成 | 历史B200、旧B1000、去dwm候选、历史RW型校正、P3/N1各有独立来源。 | [RESULT_VERSION_TABLE.csv](package/results/RESULT_VERSION_TABLE.csv) |
| W03 | 031/041构念、样本、边际OR差和选择历史明确 | 已完成 | 正文表11列候选，表12单列历史校正；031为9879条/2939簇，041为12564条/3149簇。 | [CANDIDATE_DEFINITIONS.csv](package/results/CANDIDATE_DEFINITIONS.csv) |
| W04 | P3期末金额、原金额与固定封顶口径分开 | 已完成 | 表13/E.2报告三状态总体金额；两口径均2000/2000有效，整体p为0.131934和0.079960。 | [P3_OMNIBUS.csv](package/results/P3_OMNIBUS.csv) |
| W05 | 最终P3与冻结N1构成固定六项校正家族 | 已完成 | 六项原始p、BH6、BY6齐全，无5%拒绝。 | [SIX_TEST_FAMILY.csv](package/results/SIX_TEST_FAMILY.csv) |
| W06 | 唯一研究问题总表覆盖全部新旧结果 | 已完成 | 表10覆盖完整中介、修饰、PE与政策情景，表11—13补候选、历史校正和P3。 | [MANUSCRIPT_READING.md](package/MANUSCRIPT_READING.md) |
| W07 | 有限理论回溯，区分相对位置与绝对改善 | 已完成 | 理论矩阵有原文锚点，正文保留探索后解释及28.35%/88.01%可重叠说明。 | [THEORY_EVIDENCE_MATRIX.md](package/THEORY_EVIDENCE_MATRIX.md) |
| W08 | 旧失败、当前修复与推断暂缓分别报告 | 已完成；历史限制保留 | P3原49次失败的同目标修复已关闭；B1及其他历史低于98%的规格仍暂缓推断。 | [MANUSCRIPT_READING.md](package/MANUSCRIPT_READING.md) |
| W09 | 补前驱、120项执行输入绑定和精确结果 | 已完成既定来源交付 | 前驱/部件差异与120输入日志已归档，公开代码结果包、来源索引保持；本轮核包内81项SHA。 | [SOURCE_INDEX.json](package/provenance/SOURCE_INDEX.json) |
| W10 | 正式三稿、Zotero、页码表格和Word PDF原生验收 | 已完成 | 三稿保存/重开和双视图通过；C3真实刷新、PAGE、F5完成；47页PDF五项检查通过。 | [FINAL_NATIVE_CLOSEOUT.md](package/FINAL_NATIVE_CLOSEOUT.md) |
| W11 | 同一最终PDF两轮六主题NLM审读与逐条裁决 | 已完成 | 12个独立会话、328条原生引用、57项裁决；未决稿件问题0，母稿无需再改。 | [FINAL_NLM_REVIEW.md](package/FINAL_NLM_REVIEW.md) |
| W12 | 指定GitHub发布、公共回下载和百度独立回验 | 已完成 | GitHub原包提交76c59aa6，云验收提交3ae3311；原704云队列complete/verified。本轮公共ZIP重新下载通过。 | [PUBLICATION_VERIFICATION.json](PUBLICATION_VERIFICATION.json) |

可下载[机器可读任务台账CSV](TASK_CHECKLIST_20261101.csv)。这12组是收尾要求的归纳，不能与14个主检验、34项修稿裁决或57条终审意见混为同一个数量。

**稿件修改和审读的完成证据**

累计稿保留早期21处批准修改以及v6的表D.1尺度、pmin封顶、附录E.4引导语三处更正。后续V3h共有34项裁决：22项文字/格式实施、9项有理由保留、3项原生事项。C3两条刊名已在Zotero更新并实际Word Refresh；F2页码与F5表10/11列内容均已完成实际PDF核验。34项是全部处置，不能称为34项都修改。

三份当前V3h原生Word均有保存、关闭、重开回执；接受/拒绝视图与各自冻结参考对应。原生检查覆盖9个story、34张物理表、2956个表格单元、3项媒体、10个公式。后续C1批准移除重复脚注引文，因此最终接受稿为22个引用域、1个书目域、25条书目，拒绝视图为23/1/25；历史“23引用域”不能机械套到删除重复项后的接受稿。当前对照范围按V3h冻结合同解释，不能宣称拒绝该稿会直接回到最早初稿。

最终PDF47页，27个字体项均已嵌入；原生文稿/引文、格式、字体、全页视觉和实证对应五项验收通过。Word导出后的页面索引结构修复有单独证据，47页内容和像素保持。最终PDF SHA256：`6bde712d3564f8116dcc13ac769881104058951a753d7eba8b38cc9206cec291`。

同一PDF完成理论方法、数表、结构、语言、引文、版式六主题的两轮审读：第一轮137引用/28裁决，第二轮191引用/29裁决，共12个独立会话、328原生引用、57裁决。新确认稿件错误0、未决稿件问题0。NLM原答中的页码概括、表格抽取和检验家族误判已逐条裁决，并非把每条回答当正确意见。该轮由Codex作本地裁决（solo_self_review），不冒称新增Claude互审。

**指定GitHub是否真的上传了**

指定仓库：[lzhs1995/CMAverse-paper](https://github.com/lzhs1995/CMAverse-paper)，公开，main分支。当前论文目录：[final/20261101-v3h](https://github.com/lzhs1995/CMAverse-paper/tree/main/final/20261101-v3h)。

| 提交/证据 | 实际内容 |
|---|---|
| [76c59aa6a6922c5a66a93390f35035508c9b0844](https://github.com/lzhs1995/CMAverse-paper/commit/76c59aa6a6922c5a66a93390f35035508c9b0844) | 正式V3h、三DOCX、47页PDF、终审原答与裁决、最终ZIP；原验收记录为86个公共文件逐项回下载匹配 |
| [3ae3311ca95e5ad9cf06d57d70fff771d6b30bed](https://github.com/lzhs1995/CMAverse-paper/commit/3ae3311ca95e5ad9cf06d57d70fff771d6b30bed) | 追加百度独立回下载验收及恢复说明，冻结论文ZIP保持 |
| 本轮08:45台北时间匿名公共下载 | HTTP 200；ZIP 10,299,844字节，SHA=`cc72cdec12cf6d16ccf87de2df41bc71bf46fccc485f8e6e858373e0bdbb3095`；82成员CRC通过，81项清单SHA全部匹配本地 |
| ZIP内代码结果档案 | 244成员CRC通过，其中108份CSV、17份R源码；内嵌历史文稿仍按历史候选标记 |
| 本报告 | 包外新增系统报告、W01—W12台账、14份网页原件、1份两阶段修订和核验摘要；在仓库首页与最终目录直接链接 |

最终ZIP严格小于25,000,000字节，含文稿、聚合表、代码结果档案、理论矩阵、来源、NLM原答和裁决。百度原704队列及回执为complete/verified，最终包与恢复清单均已独立下载，82成员完整核验；[回验与恢复证据](PUBLICATION_VERIFICATION.json)、[恢复说明](CLOUD_RESTORE_GUIDE.md)已在仓库。

交付文件本机绝对路径如下：

```text
/Users/lzhs/Documents/cnm/tasks/01_R_analysis/handoff/cmaverse-successor-01a19133-20261031/continuation_20261101_v4/delivery_r2/package/manuscript/CMAverse_V3h_final_accepted.docx
/Users/lzhs/Documents/cnm/tasks/01_R_analysis/handoff/cmaverse-successor-01a19133-20261031/continuation_20261101_v4/delivery_r2/package/manuscript/CMAverse_V3h_final_tracked.docx
/Users/lzhs/Documents/cnm/tasks/01_R_analysis/handoff/cmaverse-successor-01a19133-20261031/continuation_20261101_v4/delivery_r2/package/manuscript/CMAverse_V3h_final_rejected.docx
/Users/lzhs/Documents/cnm/tasks/01_R_analysis/handoff/cmaverse-successor-01a19133-20261031/continuation_20261101_v4/delivery_r2/package/manuscript/CMAverse_V3h_final_accepted.pdf
/Users/lzhs/Documents/cnm/tasks/01_R_analysis/handoff/cmaverse-successor-01a19133-20261031/continuation_20261101_v4/delivery_r2/CMAverse_V3h_final_20261101.zip
```

**40 GiB磁盘任务与论文分别核算**

目标为实际可用空间至少42,949,672,960字节（40 GiB），按min(statvfs可用、APFS容器可用)计量，不是把全盘总占用压到40 GB。沿已批准的原100 GB思路：对可恢复归档、冷文件、终态生成缓存分范围处理，以系统独占空间和实际可用量判断；完整SHA/属性核收，下降或无收益即停止。你自行清理Telegram的贡献不记作本方完成。

| 时间（台北，11月1日） | 真实有效可用量 | 判断 |
|---|---:|---|
| 07:53原S40冷DB回件 | 41,241,878,528 B，38.409 GiB | 当时未达标；该原件保留 |
| 08:06:44本次结项复测 | 48,805,945,344 B，45.454 GiB | 达标 |
| 08:10:37本次结项复测 | 48,757,649,408 B，45.409 GiB | 再次达标 |
| 08:45:22本报告只读复测 | 44,509,995,008 B，41.453 GiB | 仍达标；本轮清理动作0 |
| 08:57:35发布后只读复测 | 38,330,372,096 B，35.698 GiB | 当前未达40 GiB，缺口4,619,300,864 B（4.302 GiB） |

空间是动态快照，不能承诺其永久不变，也不能把全卷并发变化全部归因为某次压缩。旧STOP、失败及原尝试均保留；既有修改批次已核收收尾，未因状态通知重开清理。

08:57下降的具体来源尚未核定。本轮报告/附件新增量很小，不能据全卷差值推断由某个任务造成，也不把早先达标冒充当前达标。当前需要重新恢复的容量至少4.302 GiB；后续治理应先对比新增占用与系统独占量，再只处理已确认终态的缓存或已独立云回验的具名归档，保留SHA/属性/恢复记录，最后复测两次实际可用量≥40 GiB。该补记只报告状态与下一步，不声称已执行新一轮清理，不重放原STOP批次。详见[新容量快照与剩余事项](CAPACITY_FOLLOWUP_20261101.json)。

**当前剩余事项与研究限制**

当前执行层面的剩余事项是重新恢复并复测40 GiB可用空间；论文、两轮终审、原GitHub/百度交付和本次报告发布均已有完成证据。以下科学限制不能通过把流程标为完成来消除。

1. 经完整选择背景支持的明确中介或“最佳机制”未确立。这是本轮研究答案；后继执行单明确不为跨过0.05再跑新模型。
2. 新14项B1以及R1_B1、R3_B1、R4_B1、部分R9金额间接对比等历史有效率不足，正式推断仍暂缓。P3的同目标修复不把这些历史任务变成全部成功。
3. 部分原生ER/PE、E-value适配、观测数据时序与混杂条件仍有限制；没有借“原生Word或NLM验收”提升因果识别等级。
4. 公开包不包含CFPS微观数据或全部大型模型对象；来源索引保留未重新核源和历史缺口。本轮实际重验的是冻结交付文件及公共下载，未重新估计全部历史研究。
5. 本次结项范围为CMAverse论文工作稿及对应交付，不代表完整博士论文完成。S39六文件及原19项科研限定另有原任务范围。

此前汇报的不足是未把网页任务、科研结果、原生验收和发布网址合并成一份当前报告。包内REVIEW_RESPONSE.md等原历史记录还会看到“待原生/0轮”，其日期是10月30日；后续完成证据在FINAL_NATIVE_CLOSEOUT.md、FINAL_NLM_REVIEW.md及包外PUBLICATION_VERIFICATION.json。本报告和首页入口把当前状态放在一起，历史原件不覆盖。

本批实质研究/文稿交付在11月1日上午已完成，本轮报告和入口已经发布；它们不再等待10月10日旧NLM请求。磁盘当前35.698 GiB另记为未保持目标，不能继续笼统宣称全部要求当前都已满足。详细文件身份、两轮验收引用及容量快照见[本报告核验摘要](REPORT_EVIDENCE_20261101.json)。
