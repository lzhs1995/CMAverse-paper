# 给 Claude 网页端的提示词

以下全文可直接复制：

请接续我的“筛选显著性”任务，对v6阶段反馈作独立复核。请读取实际GitHub固定版本文件，报告成功下载、解析与未能核查的范围；不要把读摘要或校验文件字节称为重新拟合模型。

固定内容版本：0ffd3b2f9dbbdeed2f0d7f8ec1199f61b39fbf3b
报告：https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/0ffd3b2f9dbbdeed2f0d7f8ec1199f61b39fbf3b/review/20261008-significance-progress-v6/REPORT.md
读取入口：https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/0ffd3b2f9dbbdeed2f0d7f8ec1199f61b39fbf3b/review/20261008-significance-progress-v6/START_HERE.md
数据包：https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/0ffd3b2f9dbbdeed2f0d7f8ec1199f61b39fbf3b/review/20261008-significance-progress-v6/significance_progress_part01.zip
清单：https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/0ffd3b2f9dbbdeed2f0d7f8ec1199f61b39fbf3b/review/20261008-significance-progress-v6/DELIVERY_MANIFEST.json
ZIP大小：4,861,574字节；SHA-256：220a6c8ea58b96ef42c8f12dc63a3387827ce9556bd35126c29c2a419b8622e5。

本轮统计未变：47份统计/来源文件逐字节继承v5，没有新模型、bootstrap或p值。031/041仍是探索性线索，历史搜索校正未支持确认；P3整体p=.131934/.079960。请保留历史B=200、旧B=1000、去dwm B=1000和N1/P3六项族的版本边界，不把各版本拼成同一推断。没有依据为跨过.05继续扩搜，但也不能断言任何未来搜索都不可能改变结果。

请将本轮工作集中在：
1. 检查三处实际改文及表D.1尺度注，确认连续结局没有被泛称为OR差，封顶保留记录，22条表内结果未变。
2. 核查真实Word接受/拒绝、保存重开与独立母稿/参考的对应。已完成的是两个原生修订分支；接受副本是在最终Refresh之前保存的。
3. 检查状态报告是否忠实于回执。最终Refresh只有调用返回证据，stdout明确为MACRO_RETURNED_NOT_COMPLETION，随后SCENE_CHANGED；最后保存、23引用域/1书目域/25条书目、旧22引用/24书目完整保全、Word PDF及同PDF两轮NLM尚未闭合。不能用字段计数或candidate=reference自比较代替全书目核验，也不能凭历史票据推断当前资源所有者或要求用户处理无关文稿。
4. 评估协作效率说明：两位本机Claude曾提供有用的独审，但任务未正式派包、主管核收延迟和重复维护造成等待。待命/回调守卫不等于API故障；API暂不可用须连续至少300秒真实失败并有门槛后新失败，成功重置。本包是主管solo_self_review组包，不冒称新的双Claude终审。协作维护不应成为论文交付的额外前置。

请只列本轮仍真实存在的问题，按重要性排序，每项给文件定位、证据、最小改法和停止条件；已解决问题不重复派审。网页端不能实时操作我的Mac，执行建议应写成基于当前回执的条件步骤。无需重新要CFPS整库或重复大规模复算。最后给出可直接回传Codex的短执行单，并明确哪些研究目标达成、哪些尚未达成。

