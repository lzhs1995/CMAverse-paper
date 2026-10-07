# CMAverse 筛选显著性：v3 论文阶段审阅包

本包可以供网页端继续核查结果与实际改文。交付状态为 REVIEW_ONLY_NOT_FINAL；统计计算已冻结，本包不包含最终原生 PDF，也不宣布 Word/Zotero/NLM 终审完成。

请先读 RESULT_VERSIONS.md、CHANGE_PLAN.json、CONTENT_SCOPE_SUMMARY.json，再读 manuscript/accepted_offline.docx；如需审核修订及回退，可分别读 tracked_patched.docx、content_patched.docx 和 rejected_offline.docx。四稿均为原始离线参考文件，与原生任务冻结输入逐字节一致。

实际预检 PASS；冻结输入94项逐一读取并核对SHA（66项历史输入）。离线QA记录9个story、24个域（23引文＋1书目）、25条书目。8个既有段落/单元格目标、2个新增附录段落和脚注3处理均有来源绑定。字段结构存在不等于原生Zotero刷新成功；docProps的页数是历史缓存，不是本版原生页数。

SOURCE_BINDINGS.json 区分统计来源、v3稿件和预检来源。CHANGE_PLAN.json 保留原计划尚待审核的原始状态，并另列其后真实主管批准；未倒写审核历史。IMMEDIATE_PREDECESSOR_PART_DIFF.json 为四稿与即时前驱的完整部件差异，DOCX_PART_SHA256.json 为本次逐部件哈希。

EXISTING_MOTHER_BINDING.json 给出已公开母版的固定commit地址与SHA，不重复打包母版或旧11包。本包没有CFPS微观数据、研究ID、执行票据或私人应用内容；稿件原有作者编辑元数据依主管明确裁定保留，保证原件哈希一致。

FEAS_031/041仍是探索性修饰候选，未获得历史搜索校正支持的确认性机制；P3原金额/封顶整体p分别0.131934/0.079960，六项族无5%拒绝。去dwm结果不借用旧版本p。N1表保留历史四项q列和最终六项q列，论文采用最终六项列或SIX_TEST_FAMILY.csv。

RESOURCE_RECOVERY_SUMMARY.json 说明任务资源观察与安全释放问题已有真实修复记录；该记录不能替代随后原生论文验收。主任务继续负责原生任务与最终上传。打包程序没有上传；发布者需另提供固定commit及远端回下载证明。
