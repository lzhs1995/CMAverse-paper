# P3 全局抽样域修正（等待原生验收）

父协调已采纳原基础 3212 簇抽样、子样本零贡献合同。本次只修改私有 worker，未修改任何原计划/数据，未提交生产或运行 R。

## 修正内容

- `p3_validate_plan`：原 plan IDs 与完整基础数据的排序唯一簇 IDs 严格双向一致，仍核 3212×2000 有限整数合法索引。B 子样本须全部映射其中、恰为 3153 簇。
- `p3_domain_check`：复核 plan 内 `data_sha256` 对完整基础数据及 `draw_sha256` 对全部索引；stable_row_id 唯一且逐行所属簇一致。59 个零贡献簇必须恰为基础域与 B 域之差。
- 固定第 1、17、200 列：独立从完整基础数据按簇展开后按资格行身份筛选，与 B 数据先筛后展开比较完整有序 stable_row_id 序列及逐成员重复次数。记录行数、零贡献抽取次数、合格簇抽取次数（含重复）、unique 合格簇数、序列 SHA。
- `p3_draw_rows` 允许空簇，仍逐次核验全部合格成员被抽入的精确重复权重及总行数。不要求 unique 簇数等于 3153。
- 全空重复保留 `EMPTY_GLOBAL_DRAW_NO_REDRAW` 失败，后续原索引照常，不补抽。原金额/封顶同抽样、冷起点主结果、98% 门禁及整体检验算法均不变。
- 冻结对象加入原完整基础数据及域核验证据；检查点 identity 绑定它们和新函数体。旧 identity 不兼容时明确拒绝，禁止静默续用。
- 纯合成 selftest 新增已登记零贡献、全空抽样、未知基础域/子样本簇拒绝；原 10 项测试保留，合计 13 项。

## 原生验证入口（父协调执行）

在既有原生 R 环境中 source 新 worker（仅定义函数），原依赖环境 e 保持原 source 顺序：

```r
p3_validation <- p3_validate_native(e, legacy_root,
  file.path(p3_private_dir, "GLOBAL_DOMAIN_NATIVE_VALIDATION.rds"))
print(p3_validation)
```

`legacy_root` 为原 `pro_claude_v4_consensus_20261005_v1`；`p3_private_dir` 为本目录。此入口仅读取 prepared_data/plan、构造确定性资格样本、核门禁与纯合成 selftest，不拟合真实模型；计划文件执行前后 SHA 必须完全相同。通过后父协调再运行 `p3_prepare` 的原点估计等价验收，最后自行决定生产提交。

## 已做与未做

完成 Python 静态替换检查、审阅新函数调用点。尚未执行 R 解析/selftest/真实域验证，不能将此报告称为原生 PASS。源文件历史保留 `p3_frozen_worker.pre_global_domain_fix.R`，原计划未写入。原冻结外部 manifest 仍须由父协调依既有流程验收；本入口核 plan 内数据/索引绑定及文件前后不变，不能替代外部历史 manifest 信任链。

## SHA256

- `p3_frozen_worker.R`: `667796705de9637d2e466a266e8dabbf4fcb02759ebd6c33c6a2b916bd11ffbd`
- `p3_frozen_worker.pre_global_domain_fix.R`: `c06a4c0df4b5dccffd0e7e840ee0c1a0155c2197848d3de8c71b393180731457`
