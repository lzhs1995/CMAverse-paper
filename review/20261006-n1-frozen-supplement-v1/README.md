# N1 冻结样本与结果对象：两文件定点补充（2026-10-06）

应 ChatGPT-Pro 的《资料验收结论与最小补充清单》补充两份已有原件，供 N1 实际样本、人际／个人内变量及协方差独立核查。两文件直接发布，无需解压；旧 11 个 ZIP 保持原位。本次未重跑 N1、未重新生成数据、未改变任何模型或统计结果。

## 下载与校验

| 文件 | 字节数 | 用途 |
|---|---:|---|
| [N1_analysis_sample.csv](https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/main/review/20261006-n1-frozen-supplement-v1/N1_analysis_sample.csv) | 1,691,651 | 正式完整案例样本、人际／个人内派生变量、成年子女与簇对应 |
| [N1_result.rds](https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/main/review/20261006-n1-frozen-supplement-v1/N1_result.rds) | 326,678 | 正式结果对象；用于在 R 中进一步检查样本、公式、来源及协方差约定 |

合计 **2,018,329 字节（2.018329 MB）**，两文件均小于 25 MB。完整来源和机器可读校验见 [MANIFEST.json](MANIFEST.json)。

```text
84b3afa1236b39dbde55ecb941f18e462af9c674fcc54fff20e5fb607016042b  N1_analysis_sample.csv
a4db351d1c8c38ac786d272d17a878ff0e405db6285c3077a3e9624bb317a0ec  N1_result.rds
```

以上大小与 SHA-256 已同本机文件实际字节、原 `n1_n2/runtime_v2/N1_formal_v3/ACCEPTANCE.json` 及网页端请求逐项核对。

## 样本与版本对应

本次 CSV 实际为 **13,293 行、19 列、5,249 个 actor、3,186 个 cl**。它是 N1 正式 actor-wave 样本，**并非**旧包中 13,092 行、98 列的 `analysis_13092.csv`。请使用本次冻结对象和已经收到的 N1 构造／估计代码进行逐项对应，不因文件同名而替换为历史上游 DTA。

这两份文件的源目录为：

```text
/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1/limited_followup_20261006_v1/n1_n2/runtime_v2/N1_formal_v3/
```

原 `ACCEPTANCE.json` 中的 `global6_status=PENDING_TWO_REGISTERED_P3_OMNIBUS` 是该冻结阶段的历史状态。随后 P3 及六项校正已经完成，见[限定复核最终报告（固定提交）](https://github.com/lzhs1995/CMAverse-paper/blob/494e4a7f58f35e1ef4039a30b076b91472c03c78/review/20261006-limited-followup-v1/REPORT.md)。本次保留原对象，不改写历史记录以追随较晚状态。

## 给 ChatGPT-Pro 与 Claude 网页端

> 你要求的两份 N1 冻结文件已补齐，文件大小和 SHA-256 与你此前验收报告中的预期值一致。请在已收到的 11 个 ZIP 基础上，加入本目录的 `N1_analysis_sample.csv` 和 `N1_result.rds`，继续核查 N1 正式完整案例、人际／个人内派生变量、actor 与簇映射、模型公式，以及实际协方差的计算约定和数值。本次没有重跑模型或更新样本。请把文件完整性、R 对象反序列化、协方差独立复算、统计解释分别报告；如果尚未实际在 R 中读取对象，请保留这一限制。无需再次索取已有历史材料。

本次补发仅完成文件及来源核验，不替代统计正确性审查，也不表示最终 Word 整合或最终同版本 NLM 全文终审已经完成。
