"""汇总已完成的冻结证据与稿件改文，不进行模型估计。"""
from pathlib import Path
import json, shutil, hashlib

P=Path(__file__).resolve().parent
L=P.parent
O=L/'numerical_closeout_20261006_v1'
for d in ['review','delivery','manuscript/sources']:(P/d).mkdir(parents=True,exist_ok=True)
for n in ['00_数值收尾独立复核报告.md','01_Astra_Mac_论文收尾执行方案.md','02_论文可用改文.md']:
    shutil.copy2(Path('/Users/lzhs/Downloads')/n,P/'review'/n)
qa=json.loads((P/'qa/MANUSCRIPT_QA.json').read_text())
src=Path(qa['source'])
prev=L/'word_preparation_v1/clean_successor_v2/CMAverse_限定复核与家务核验合入_干净离线候选_非交付_结构规范化.docx'
for f in [prev,src]:shutil.copy2(f,P/'manuscript/sources'/f.name)

report='''# 筛选显著性：数值冻结后的论文与证据收尾

日期：2026-10-06。数值基线：687194000f275a73e83648e1c5362613ad8b0be4。

## 本轮裁定

ChatGPT Pro建议合理：计算可结项，031／041保留探索性修饰线索，历史搜索校正没有支持确认性机制；P3数值问题已经修复，其整体结果仍不显著。继续围绕相对评价变化作有限理论解释和论文落稿有依据，继续为跨过0.05扩搜索则没有本批任务依据。本轮未启动任何模型、R作业、新检验、bootstrap或追加分组。

本轮完成了来源补齐、分版本结果表、原稿内容修订与离线结构检查。原生Word修订/接受/拒绝分支、Zotero实际刷新、Word原生PDF逐页检查和最终同版NLM仍未完成。交付的是可供网页端继续核查的论文候选与证据，不能称论文最终交付全部通过。

## 本机实际核验范围

- 对288个冻结源文件重新核对SHA-256与字节数；120份实际execution_inputs.rds（共197,603,909字节）和120份METRICS.rds与历史proof、原R索引审计绑定一致。
- 原R对共同簇抽样、实际行索引和replicate seeds的审计沿用已接受job d128f101。本轮没有重新在R中反序列化并重做行索引验证；文件全量哈希与R内对象验证分开表述。
- 从历史200×240保存矩阵独立复算原始p、两个120项目标族及合并240项的Romano–Wolf型算术；不重拟合120规格。
- 核查P3全部6,000条保存结果、2,000组共同抽样哈希及保存诊断；独立复算两个整体检验与六项BH/BY。不再重拟合P3。
- 复核2,939＋3,149个逐簇点诊断的汇总及两个时期的点估计；不新增逐期或逐簇显著性声明。
- 产出9张带源路径、源哈希和定位键的CSV；12项来源/算术核验通过。结果表与正文证据表另有独立读回核验；最终候选另通过50项独立全story结构/内容/数值核验。
- 本轮由Codex主协调和已授权的既有代理分工，未调用Claude网页端或将旧Claude意见冒称本轮终审。

## 冻结结果与版本

| 候选 | 去dwm后ΔOR | 未调整95%区间 | 记录/簇 |
|---|---:|---|---|
| FEAS_031 | −0.409351 | [−0.668529, −0.150173] | 9,879 / 2,939 |
| FEAS_041 | −0.085496 | [−0.162804, −0.008187] | 12,564 / 3,149 |

031：本人实际收入增加，与基期本人满意度不高于配偶、期末转为本人高于配偶的相对位置状态相结合；Y为向特定父／母实际月均支持是否增加。041使用本人减配偶满意度分差的两期变化，固定0→1分；与031的资格总体不同。这里的Δ是标准化边际OR之差，不是风险比之差或概率百分点。

| 历史版本 | 031原始p | 041原始p | 031/041同指标120项调整p | 031/041合并240项调整p |
|---|---:|---:|---|---|
| B=200原模型 | 0.004975 | 0.039801 | 0.134328 / 0.631841 | 0.542289 / 0.915423 |
| 旧B=1,000精化 | 0.002997 | 0.032967 | 未计算 | 未计算 |

去dwm模型只有本轮已冻结点估计和中心化绝对偏差95%区间，没有新增p或搜索校正。上表历史p及调整值不得移植到去dwm行。150为登记规格数、120为可估规格数、240为两类目标总数，并非240份独立资料。历史RW型结果是搜索背景核查，不能宣称控制全部自适应研究或一般中介复合零假设。

| P3金额口径 | ≤3分收入对比 | 4分 | 5分 | 5减≤3 | 5减4 | 整体p |
|---|---:|---:|---:|---:|---:|---:|
| 原金额 | 38.28 | 44.66 | 14.24 | −24.03 | −30.42 | 0.131934 |
| 固定99%封顶 | 36.67 | 41.41 | 11.06 | −25.61 | −30.36 | 0.079960 |

单位元/月。两个尾部计数分别为263和159，加一规则得264/2001与160/2001。原金额和封顶金额均2,000/2,000有效，固定阈值为2,664.29840142096元/月，pmin封顶而非删除。两部分合成为逐行概率乘条件均值再平均。原金额BH q=0.158321，封顶BH q=0.119940；六项家族均未达0.05。

N1四项原始p维持0.045682、0.075915、0.030937、0.194627；最终六项BH依次为0.119940、0.119940、0.119940、0.194627。N1属于人际/个人内辅助关联，不能计作中介、收入修饰或完整个人固定效应。旧四项族q和最终六项q在CSV中分别保留。

## 本次论文改动

1. 更新唯一的研究问题总表（表10），覆盖收入关联、中介、修饰、PE、政策情景、N1和搜索边界。
2. 增加候选定义及去dwm结果表11、历史版本p表12、P3三状态及整体检验表13。旧图像与CDE资产保留。
3. 正文先说明问题、结果和含义，减少任务代号、六位小数和数值门槛；技术细节集中在附录及复现材料。
4. 讨论中的早期辅助p=0.036后紧接最终P3整体p=0.132/0.080；原局部值仍保留在历史附录。
5. 删除表E.1“NA表示推断暂缓”；保留最终六项值。明确P3失败已修复，其他历史失败没有自动修复。
6. 说明旧八链联合设定的禁配/处理后变量问题与当前不含postc的031/041固定M对比分别判断，保留当前条件支持、混杂与时序边界。
7. 讨论区分相对评价变化、绝对满意度改善、资源配置解释与已识别机制；相关理论解释是探索后的有限回溯。

只改word/document.xml，其他ZIP部件逐字节不变。字段、公式、图像、脚注引用、书签与节属性须以qa中的结构核验记录为准；这不等于Word插件刷新或实际分页验收。当前稿为干净离线候选，不伪装为原生接受修订稿。

## 有限理论回溯及比例来源

沿用许琪（2022）、郑丹丹与狄金华（2017）和Fujihara（2024）三篇本机原文。三篇PDF与三份既有摘录SHA一致，直接从PDF读回9个页段锚点；形成7条证据矩阵，逐项列出研究单位、水平/变化、本人/配偶、模型时间结构和可支持/不可支持结论。未开展新的广泛检索，也未以静态作者年份冒充动态引用。

许琪使用2014 CFPS妻子评价，不能证明夫妻评分差的变化；郑/狄使用单波家庭层面支持频率、决策权与关系质量，不能把本稿相对评分当作决策权测量；Fujihara提供固定M对比与间接效应的区别，教育研究不是婚姻机制的实质验证。资源配置取向可作为探索后提出的待检验解释。

正文28.35%/88.01%沿用前轮Pro完整实证复核第95行所报的1,559条相对位置升级记录；本轮明确核对报告来源和共同分母，没有重新逐行计数。两类可能重叠，不能合计作互斥分类，也不来自上述三篇外部文献。原报告副本及精确来源记录见review/00_前轮完整实证复核结论_比例来源.md与bindings/RELATIVE_CHANGE_DESCRIPTION_SOURCE.json。

## Pro此前缺少的两类证据

- 已补入上一增量即时前驱DOCX、数值收尾DOCX与本轮候选，并提供前驱→数值稿→本轮稿逐部件SHA对照。外部可直接打开原件检验，无需相信单一“QA通过”声明。
- 已补120份执行输入的只读文件绑定日志、原审计引用、288源pins及验证脚本。不发布约198MB执行输入原件；外部可验证日志与已冻结共同计划/结果之间的来源连接，但不能把日志阅读称为自己已读取120个RDS。

## 原生交付的实际阻碍

旧Word票据d529和另一任务的92f9票据均已真实释放。发布前14:38 UTC只读快照为ACTIVE=0、WAITING=0；另一任务实际释放时间为14:26:08 UTC，释放证据9项及87个来源pins核对通过。因此不能继续将共享资源被另一任务占用列为当前阻碍。既有恢复程序仍绑定旧执行链；旧授权代管释放外层PROCESS/TERMINAL/wait的历史回执缺口与当前资源可用性是两件事，不能伪造历史wait记录，也不能把该日志缺口误称为统计任务未完成。

已完成一份私有、只读的实际释放绑定适配及20项离线测试；没有UI、锁申请或执行入口，native_ready=false。其通过仅代表历史释放材料能被准确识别，并不证明新稿的原生操作成功。当前稿SHA已冻结；仍需将新稿与原生锚点、接受/拒绝分支及既有执行器绑定，并在执行时重新检查身份、资源队列、pending和锁。不得绕锁、强退Word/Zotero，也不得把旧PDF/NLM状态贴到新稿上。

此处遵循用户提供执行方案第6节：“发生阻塞保留PENDING并报告准确原因，不重新生成另一份看似最终的离线稿。”Office技能/Users/lzhs/.local/share/officecli-word-revision/releases/0.1.0.dev3-7b740493869c/venv/lib/python3.14/site-packages/officecli_word_revision/SKILL.md第76行要求“Serialize all Word, Zotero, and same-file OfficeCLI writes”，并明确锁超时不能作为并发写入许可。原生步骤恢复后应使用本轮冻结稿重新固定锚点、累计修订分支、真实插件刷新、Word导出PDF，并绑定同一PDF的最终NLM审阅。现阶段没有新最终PDF，不启动同版终审调用。

## 交付与验收界限

网页端现在可以核查本轮新增来源证据、结果表、理论证据矩阵及实际DOCX内容。此前旧11包和N1补充仍沿用，不要求重传。当前上传不宣称研究发现升级，也不宣称最终论文排版/原生引文已完成。

完整文件清单、大小、SHA及ZIP CRC见MANIFEST.json与PACKAGE_QA.json；下载核验回执在发布完成后另存。每包小于25,000,000字节。包内仅文稿、聚合结果、代码、来源绑定和有限文献证据，不新增微观记录、研究个人ID、大型执行对象或全文文献PDF。
'''
(P/'REPORT.md').write_text(report)

response='''# 对ChatGPT Pro逐项回应

| 建议/问题 | 本机执行与裁定 | 证据 |
|---|---|---|
| 数值结项，不扩显著性搜索 | 采纳；零新模型/R任务/抽样 | bindings/SCOPE.json、QA.json |
| 保留031/041但不确认机制 | 采纳；候选表与历史推断表分开 | results/CANDIDATE_HISTORY_PANELS.csv |
| N1来源缺口已关闭 | 采纳；只沿用冻结值，追加最终六项字段 | results/N1_FOUR_WITH_FINAL_SIX_ADJUSTMENT.csv |
| 补120输入的来源记录 | 已核120实际文件及METRICS，含hash/bytes/旧R审计引用 | bindings/EXECUTION_INPUTS_120.csv |
| 补DOCX即时前驱或差异记录 | 两个前驱原件均收入增量，前后逐部件可比 | manuscript/sources、qa/DOCX_PART_DIFF.csv |
| 候选、P3、研究问题证据表 | 已新增表11—13并更新唯一表10 | manuscript/EVIDENCE_TABLES.json |
| R6讨论不再单独突出旧显著 | 紧接最终整体结果，旧原值留附录 | manuscript/MANUSCRIPT_TEXT.md |
| P3失败状态与其他失败分开 | 已修订正文局限和附录；不扩展修复 | manuscript/TEXT_PATCHES.json |
| 删除E.1题尾NA说明 | 完成，数值不变 | qa/MANUSCRIPT_QA.json |
| 理论只围绕相对评价及资源配置 | 使用现有原文作有限回溯，不把推测当测量 | theory目录及改稿讨论 |
| 技术信息移附录 | 正文讨论/局限压缩，求解/失败细节留附录 | manuscript/TEXT_PATCHES.json |
| Word/Zotero/PDF原生及同版NLM | 尚未完成；外部占用已解除，新稿原生执行绑定/验收仍待完成 | native_readiness、ACCEPTANCE.json |

本轮可供外部复核的是实际文件/保存统计量与稿件内容；原生交付仍有明确待办。“未达到确认性机制”不等于“所有未来分析都不可能显著”，后续也不以同一资料换随机种子冒充独立确认。
'''
(P/'review/PRO_RESPONSE.md').write_text(response)

writing='''# 定点写作复核记录

范围：研究设计中历史/当前模型区别、选择后限定结果、表10—13、讨论与局限、附录E标题和补充说明。不是全文原生终审。

| 五项检查 | 原问题与具体修订 | 状态 |
|---|---|---|
| 冗余 | 原讨论重复列程序代号/失败门槛，改为收入关联—相对修饰—完整中介三类结论，详细数字保留附录 | 完成 |
| 主体与动词 | “失败暂缓”改为“P3已修复但整体未获证据”，其他历史规格单列 | 完成 |
| 句子结构 | 原局限一段混合多类长数字，压缩为时序、样本、模型、搜索四项；技术失败另入附录 | 完成 |
| 术语 | 相对满意度变化不写成绝对改善；ΔOR、百分点、元/月分别使用；N1不写成中介/调节 | 完成 |
| 数字/引文 | 原始p与历史校正、去dwm区间分表；保留既有动态域，不插伪静态引用 | 离线完成，原生刷新待办 |

最高优先级五处：表10覆盖全稿、候选推断分版本、R6与整体p同段、P3修复状态、理论构念区别。上述修改已进入实际离线DOCX，不只写成建议。

既有引文的XML与指令保留不代表插件刷新通过；公式/图片的文本导出可能只见空位，审阅这些资产请打开DOCX原件。原生表宽/分页/跨页标题等保留待验收。
'''
(P/'review/WRITING_REVIEW.md').write_text(writing)

accept={'NUMERICAL_CLOSURE':'COMPLETE_PREVIOUS_STAGE_RECONFIRMED_FROM_SAVED_RESULTS',
 'NEW_MODELS_RUN':0,'NOMINAL_EXPLORATORY_SIGNALS':'FEAS_031_AND_041_RETAINED',
 'SEARCH_ADJUSTED_MECHANISM_CONFIRMED':False,'SOURCE_BINDINGS':'PASS',
 'EVIDENCE_TABLES':'PASS','MANUSCRIPT_OFFLINE_CONTENT':'PASS',
 'MANUSCRIPT_NATIVE_QA':'PENDING','ZOTERO_NATIVE_REFRESH':'PENDING',
 'WORD_NATIVE_PDF':'PENDING','SAME_VERSION_NLM_REVIEW':'PENDING',
 'notebooklm_in_word_job':'disabled','statistics_allow_execution':False,
 'candidate':qa['output'],'candidate_sha256':qa['output_sha256'],
 'pending_reason':'External resource ownership cleared; new candidate native execution/anchor binding and inherited recovery evidence still need resolution. Native operations and final PDF/NLM acceptance have not passed.',
 'interpretation':'Publication of this review increment does not mark final native manuscript delivery complete.'}
(P/'ACCEPTANCE.json').write_text(json.dumps(accept,ensure_ascii=False,indent=2))
print('Reports, reviewer attachments and two immediate DOCX sources prepared; publication not yet asserted.')
