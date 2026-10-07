本轮“筛选显著性”可以把阶段成果反馈给 ChatGPT 和 Claude 网页端。统计计算已冻结，v3 累计改文、四份 DOCX 和最小核查材料已发布，固定提交下的 33 份直接文件已经全部实际回下载并核对大小与 SHA-256。当前状态仍为 REVIEW_ONLY_NOT_FINAL：原生 Word、Zotero 刷新、最终 PDF 及同版 NLM 全文审阅尚未完成。

本说明替代此前过度简写的资源修复表述，准确区分历史资源释放、后继程序离线测试与论文原生验收。以下统计值均转录冻结结果，本轮未重新运行模型、bootstrap 或新的显著性检验。

固定提交：
c4543a09f4832698be868ebad49315a2fba722d9

建议先读取入口、结果版本及接受态全文，再按需要下载 ZIP。以下全部是固定提交的完整地址，不会随 main 后续更新而改变。

入口：
https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/c4543a09f4832698be868ebad49315a2fba722d9/review/20261007-limited-manuscript-v3/START_HERE.md

接受态全文文字副本：
https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/c4543a09f4832698be868ebad49315a2fba722d9/review/20261007-limited-manuscript-v3/MANUSCRIPT_ACCEPTED_TEXT.md

结果版本与完整数值：
https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/c4543a09f4832698be868ebad49315a2fba722d9/review/20261007-limited-manuscript-v3/RESULT_VERSIONS.md

四稿及最小证据 ZIP：
https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/c4543a09f4832698be868ebad49315a2fba722d9/review/20261007-limited-manuscript-v3/final_increment_part01.zip

交付清单：
https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/c4543a09f4832698be868ebad49315a2fba722d9/review/20261007-limited-manuscript-v3/DELIVERY_MANIFEST.json

公开验收状态：
https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/c4543a09f4832698be868ebad49315a2fba722d9/review/20261007-limited-manuscript-v3/PUBLIC_ACCEPTANCE.json

**一、这次实际交付和核验到哪一层**

本增量 ZIP 为 1,981,554 字节，约 1.98 MB，低于单文件 25,000,000 字节的要求，无需分包。ZIP SHA-256：

493ceb2f2d1c75d5d737470bb113c2884dd1d70239f7f132b282c8dedc492c59

ZIP 有 30 个成员：28 份实质材料、PUBLIC_ACCEPTANCE.json 和内部 MANIFEST.json。发布端先前已完成 ZIP 回下载、CRC 和包内清单核验。本次另行逐个回下载全部 33 份直接公开文件，于 2026-10-07 04:15:44 UTC 完成，33/33 的字节数和 SHA-256 均与发布暂存清单匹配，总计 4,276,744 字节。这次没有重复执行 ZIP 内部 CRC；两个回执的核验范围分别记录。

33 份直接文件包含 ZIP、本身另行发布的包内材料，以及阅读入口和全文文字副本；它们存在内容重复，不能计为 33 份独立的新研究证据。本轮也没有重新审计先前所有历史包。

全文文字副本来自本次 accepted_offline.docx，来源 SHA-256 为 5063b21a076d79a5037a99dc2feece9928d95eb1dd697d07da06f9989539d8bf。它方便网页端实际读全文，表格按顺序展平；格式、图形和分页仍应查 DOCX 与后续原生 PDF，不能以文字副本替代版式审阅。

**二、v3 是累计稿的有限修改，统计结果没有变化**

本轮继承已经完成的 21 项改文和既有图表、引文资产，没有重建那批修改。v3 对 8 处现有段落或单元格作限定修改，增加 2 个附录段落，并调整脚注 3。具体内容如下。

| 内容 | 本轮处理 |
|---|---|
| 图号 | 将“图 3.2”修正为“图 3”。 |
| 满意度构念 | C1/C2 对应婚姻总体满意度；C3/C4 明确为配偶对本人收入／经济贡献的满意度（QM802），不能称为婚姻总体满意度；同步方法、结果及相应表格。 |
| 表 2 长注 | 正文表注从 1,282 字缩至 332 字；完整历史变量构造和限制保留于附录 E.4，并另存原始表注，未删去问题记录。 |
| FEAS_031 的相对位置解释 | 71.65% 的升级记录中本人评分没有提高，即持平或也下降，同时配偶评分下降；不能全部简称为“只有配偶下降”，更不能说都是本人满意度提高。 |
| 脚注 3 | 将“我院”等机构自述改为中性文献说明，保留原脚注标记；该脚注原来没有动态引文域。 |

原有脚本、编码边界、失败记录和搜索历史继续保留。上述处理没有扩大分析网格、生成新 p 值或添加新引文域。关于不对称关系评价、核心家庭与父代家庭资源配置的解释仍是待检验理论，不能写成已经测量或识别了谈判权力。

**三、四份 DOCX 的用途与离线核查边界**

| 文件 | 用途 | 离线引文域 | 书目域 |
|---|---|---:|---:|
| content_patched.docx | 累计内容稿 | 23 | 1 |
| tracked_patched.docx | 累计修订稿 | 23 | 1 |
| accepted_offline.docx | 离线接受态阅读稿 | 23 | 1 |
| rejected_offline.docx | 恢复指定 2026-10-05 母稿的离线拒绝态 | 22 | 1 |

当前内容／接受态离线记录含 25 条书目；拒绝态恢复母稿状态，不能强行要求四稿引文数相同。四份公开 DOCX 与对应 v3 本机原件字节完全一致，保留普通作者／编辑元数据，没有为公开另改正文或字段。

冻结输入清单的 94 项（其中 66 项历史输入）已在发布准备阶段实际读取并逐项匹配哈希。离线 QA 覆盖 9 个正文、脚注、页眉页脚等内容部件，检查接受／拒绝投影、字段代码与显示、图像及嵌入对象。内容稿、修订稿和接受态相对即时前驱只改变 word/document.xml 与 word/footnotes.xml；拒绝態相对其即时前驱的解压部件全部不变，外层 ZIP 字节哈希不同不能解释为正文变更。

即时前驱与逐部件差异已经公开，可用于核对上轮提出的来源绑定问题。但这些是离线结构与来源证据，并不证明 Word 实际接受／拒绝操作、Zotero 原生刷新、页面布局或最终 PDF 均通过。DOCX 中缓存的页数也不能当作当前原生页数。

四稿直接地址：

https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/c4543a09f4832698be868ebad49315a2fba722d9/review/20261007-limited-manuscript-v3/manuscript/accepted_offline.docx

https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/c4543a09f4832698be868ebad49315a2fba722d9/review/20261007-limited-manuscript-v3/manuscript/content_patched.docx

https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/c4543a09f4832698be868ebad49315a2fba722d9/review/20261007-limited-manuscript-v3/manuscript/tracked_patched.docx

https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/c4543a09f4832698be868ebad49315a2fba722d9/review/20261007-limited-manuscript-v3/manuscript/rejected_offline.docx

**四、统计共识已经固定，不能把不同版本拼接**

FEAS_031 是当前最值得解释的探索性修饰候选，FEAS_041 是相关操作化的辅助线索；两者并非独立样本复制，也不能称为已经证实的完整中介或最佳机制。X 都是本人实际收入是否增加，Y 都是向特定父母的实际月均支持是否增加；M 分别为夫妻满意度相对位置升级，以及“本人减配偶满意度差”的区间变化（固定 0→1 分）。

| 候选 | N／簇数 | 去 dwm 后 ΔOR | 同版本未调整 95% 区间 |
|---|---|---:|---|
| FEAS_031 | 9,879／2,939 | −0.409351 | [−0.668529，−0.150173] |
| FEAS_041 | 12,564／3,149 | −0.085496 | [−0.162804，−0.008187] |

ΔOR 是两个边际 OR 之差，不是概率百分点或风险比之差。031 和 041 的资格总体及 M 对比不同，不能用两个 ΔOR 的绝对值之比比较社会作用大小。去 dwm 版本采用既有 B=1,000 中心化绝对偏差区间，没有相应的新 p 值或搜索校正。

| 候选 | 历史 B=200 原始 p | 历史同指标 120 项调整 p | 历史合并 240 目标调整 p |
|---|---:|---:|---:|
| FEAS_031 | 0.004975 | 0.134328 | 0.542289 |
| FEAS_041 | 0.039801 | 0.631841 | 0.915423 |

150 是登记规格数，120 是可估规格数，240 是每项含两个目标的合计，不能称为 240 个独立检验。旧 B=1,000 原始 p=0.002997／0.032967 继续保留在旧版本；不能移到去 dwm 后的行，也不能与历史 B=200 的校正值拼成一套新推断。历史搜索校正没有涵盖所有后续自适应分析，更不是假设为真或为假的概率。

分期同号、去 dwm 后仍有线索及删簇点估计稳定增加了解释价值，但不等于每个分期或每次删簇都显著。当前未获得经历史搜索背景核查支持的确认性机制；没有理由为了跨越 0.05 扩充组合或重复次数。另一方面，现有结果也不能证明未来任何新证据都必然不显著。

P3 的 49 次原金额数值失败已经在同一模型、同一既有抽样和同一统计目标下完成修复。原金额和固定 99% 封顶均为 2,000/2,000 有效；固定封顶是 pmin，不删除大额记录。

| P3 金额口径 | ≤3 分的收入金额对比 | 4 分 | 5 分 | 5−≤3 | 5−4 | 整体 p |
|---|---:|---:|---:|---:|---:|---:|
| 原金额 | 38.28 | 44.66 | 14.24 | −24.03 | −30.42 | 0.131934 |
| 固定封顶 | 36.67 | 41.41 | 11.06 | −25.61 | −30.36 | 0.079960 |

金额单位为元／月。每个状态量是该满意度状态下收入增加与未增加的标准化支持金额对比，不是满意度自身的作用。原 R6 相邻状态辅助 p≈0.0359 可保留在历史记录中，不能替代最终三状态整体检验。修复后应写“可以估计但整体未显著”，不能继续写“P3 原金额仍不可估”。

N1 是人际／个人内辅助关联，没有收入×满意度交互，也没有完整间接效应。最终六项家族由 N1 四项和 P3 两项整体检验组成，BH／BY 均未在 5% 水平拒绝。N1 数据表保留过旧四项调整列，全文及结论应使用最终六项调整列或 SIX_TEST_FAMILY.csv，不能误用旧列。

**五、资源释放 bug 的证据必须分开读**

此前“资源释放 bug 已通过 100 项测试并完成真实安全释放”的一句话过于简略，容易被读成当前原生论文已经全部完成。准确状态是：

1. 公开 RESOURCE_RECOVERY_SUMMARY.json 记录的是较早一次资源恢复：其 100 项测试通过，并有那次真实空闲观察与 RELEASED 提交记录。它证明当次旧票安全释放，不证明之后或当前全局资源空闲。
2. 后继原生执行器另有 165 项离线测试：生成／继承部分 25+75 项，收尾部分 65 项，错误和失败均为 0。本说明已实际读取两份保存 RESULT.json 和执行报告，绑定其来源哈希。这 165 项与前述旧恢复的 100 项属于不同回执，不能混成同一批，也不把二者相加宣传为互不重复的 265 项。
3. 165 项测试均没有真实 Word／AX 或队列调用，证明的是离线逻辑和故障分支覆盖；不证明本次原生运行、Zotero 刷新、PDF 或 NLM 终审通过。此次说明没有重跑这些测试。
4. 处理原则仍是把未知状态查清并保存证据，再释放原所有者资源；不能把未知文档数改成零、把未知远端结果改成成功，或把结束进程冒充真实完成。后继程序还会在刷新改变字段语义时保留证据、要求审阅，不能以 XML 可读代替原生刷新验收。

上述固定提交的 START_HERE 保留了 2026-10-07 04:05 UTC 的历史快照，当时仍在等待资源。此后主管提供了更新：2026-10-07 04:20:17 UTC 只读观察已无 ACTIVE 任务且本任务位于队首；04:20:28 UTC 本任务已真实取得新租约，进入原生执行准备。这一更新来自主管的实际操作回报，本说明的整理者没有自行查询或操作队列；获得租约仍不等于 Word、Zotero、PDF 或 NLM 已验收。公开内容不包含租约令牌。后续实时状态以新的实际回执为准。

本轮继承三份已有 Claude 审阅。此次反馈整理及离线程序检查标记为 solo_self_review，没有新增 Claude 终审，也不把继承意见冒称本轮重新执行的多方验收。

**六、现在可以审阅什么，哪些完成声明仍需等真实回执**

网页端现在可以直接审阅 v3 全文、四稿、有限改文记录和冻结结果，重点检查：相对满意度与总体满意度是否混淆；修饰是否被写成中介；正文讨论是否同时报告 P3 最终整体结果；版本表是否把 p、区间及搜索校正准确分开；理论解释有没有越过变量实际测量范围。现有历史数据及 N1 补充已具备，无需重传旧 11 包、整库或重新运行统计模型。

仍待原生执行与最终验收的工作包括：Word 实际接受／拒绝修订；Zotero 原生刷新与字段差异审阅；脚注、交叉引用、图像和书目的实际检查；原生导出 PDF 并逐页查看；最终同版 PDF 的 NLM 全文审阅及版本绑定。若任何修改导致 PDF 哈希变化，不能继续沿用旧版本的通过结论。当前公开包没有这些最终通过回执。

因此，本次可以接受为“统计结果已冻结，累计改文与证据包可供继续审阅”；尚不能接受为“论文最终原生交付全部完成”。数值收尾和内容修订已经形成可审阅成果，后续完成上述原生交付后即结束本批任务，不自动衍生新的显著性搜索。

补充来源地址：

https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/c4543a09f4832698be868ebad49315a2fba722d9/review/20261007-limited-manuscript-v3/CHANGE_PLAN.json

https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/c4543a09f4832698be868ebad49315a2fba722d9/review/20261007-limited-manuscript-v3/OFFLINE_QA_PUBLIC.json

https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/c4543a09f4832698be868ebad49315a2fba722d9/review/20261007-limited-manuscript-v3/PREFLIGHT_PUBLIC.json

https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/c4543a09f4832698be868ebad49315a2fba722d9/review/20261007-limited-manuscript-v3/DOCX_PUBLIC_BINDINGS.json

https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/c4543a09f4832698be868ebad49315a2fba722d9/review/20261007-limited-manuscript-v3/IMMEDIATE_PREDECESSOR_PART_DIFF.json

https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/c4543a09f4832698be868ebad49315a2fba722d9/review/20261007-limited-manuscript-v3/SIX_TEST_FAMILY.csv

https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/c4543a09f4832698be868ebad49315a2fba722d9/review/20261007-limited-manuscript-v3/RESOURCE_RECOVERY_SUMMARY.json
