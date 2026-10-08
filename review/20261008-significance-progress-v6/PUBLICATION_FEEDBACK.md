# v6 已发布：给网页端的使用说明

本包现在可以直接用于 ChatGPT／Claude 网页端的阶段复核。它包含新增改文与真实原生修订证据；最终论文原生交付仍未完成。

## 固定版本地址

- 完整文件目录：https://github.com/lzhs1995/CMAverse-paper/tree/0ffd3b2f9dbbdeed2f0d7f8ec1199f61b39fbf3b/review/20261008-significance-progress-v6
- 网页读取入口：https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/0ffd3b2f9dbbdeed2f0d7f8ec1199f61b39fbf3b/review/20261008-significance-progress-v6/START_HERE.md
- 详细报告：https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/0ffd3b2f9dbbdeed2f0d7f8ec1199f61b39fbf3b/review/20261008-significance-progress-v6/REPORT.md
- 当前状态：https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/0ffd3b2f9dbbdeed2f0d7f8ec1199f61b39fbf3b/review/20261008-significance-progress-v6/STATUS.json
- ZIP直接下载：https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/0ffd3b2f9dbbdeed2f0d7f8ec1199f61b39fbf3b/review/20261008-significance-progress-v6/significance_progress_part01.zip
- 外部清单：https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/0ffd3b2f9dbbdeed2f0d7f8ec1199f61b39fbf3b/review/20261008-significance-progress-v6/DELIVERY_MANIFEST.json
- 最小改文对照：https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/0ffd3b2f9dbbdeed2f0d7f8ec1199f61b39fbf3b/review/20261008-significance-progress-v6/manuscript/CHANGE_LOG.md
- 当前全文：https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/0ffd3b2f9dbbdeed2f0d7f8ec1199f61b39fbf3b/review/20261008-significance-progress-v6/manuscript/CURRENT_TEXT.md
- 结果版本：https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/0ffd3b2f9dbbdeed2f0d7f8ec1199f61b39fbf3b/review/20261008-significance-progress-v6/results/RESULT_VERSIONS.md
- 原生接受/拒绝证据：https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/0ffd3b2f9dbbdeed2f0d7f8ec1199f61b39fbf3b/review/20261008-significance-progress-v6/native/revisions/REVISION_EVIDENCE.json

所有研究资料固定于内容提交 `0ffd3b2f9dbbdeed2f0d7f8ec1199f61b39fbf3b`。本说明、提示词与发布回下载回执在后续单独提交加入，不改变该ZIP及其研究内容。ZIP内不会包含其自身或发布后才产生的远程回执。

## 包大小和核验

单包 `significance_progress_part01.zip` 为 **4,861,574字节（约4.86MB）**，小于用户要求的25,000,000字节。共100个成员；内部99项文件大小/SHA全部匹配，ZIP与嵌套DOCX的CRC通过。

SHA-256：

```text
220a6c8ea58b96ef42c8f12dc63a3387827ce9556bd35126c29c2a419b8622e5
```

2026-10-08 08:55:24 UTC 已从固定commit匿名回下载，ZIP、清单、报告及入口均与本机字节一致。原始记录为同目录 `REMOTE_VERIFICATION.json`。这是发布完整性核验，不是最终Word或研究机制验收。

## 能反馈什么

| 范围 | 当前结论 |
|---|---|
| 显著性 | 031/041保留探索性修饰线索；尚未找到经搜索背景核查确认的最佳机制 |
| P3 | 数值问题已修复，整体p=.131934/.079960，未达到5% |
| 本轮新增 | 表D.1尺度注、封顶措辞、附录E.4引导语三处定点改文 |
| Word修订 | 接受全部、拒绝全部及各自保存关闭重开已实际完成 |
| 最终Refresh | 仅一次调用返回有证据；最终刷新及保存/书目验收未闭合 |
| 最终Word PDF与NLM | 未完成，不在本包冒充提供 |
| 统计来源 | 47份文件从v5逐字节继承；没有新模型、bootstrap或p值 |
| 双Claude | 随包历史报告可追溯；本次组包为solo_self_review，未冒称新的双Claude终审 |

原生接受副本在最终Refresh之前保存；不能将其标作完成最后引文/PDF验收的终稿。上游旧记录把宏返回写为Refresh成功，已按原始回执更正。冻结统计的版本必须分开报告。

## 如何发送

1. 给 ChatGPT 网页端复制同目录 `FOR_CHATGPT.md` 的全文。
2. 给 Claude 网页端复制同目录 `FOR_CLAUDE.md` 的全文。
3. 两份提示词均已包含可直接访问的完整固定URL，不需要你拼路径或重复上传旧包。
4. 若网页端无法下载ZIP，让它读取同一commit的展开文件，并如实说明读取边界；这不等于所有模型已重跑。

本次是用户明确要求的当前反馈。后续只有产生最终原生稿、PDF及同版NLM等新实质证据时，才再发布必要增量；不因这次整理材料重新搜索显著性。

