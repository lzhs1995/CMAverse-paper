# Claude2审查后定点修订

旧文件副本：p3_frozen_worker.pre_claude2_review.R；SHA256 `39c3ed4c14f2dc790b02996e449b31dcd2fbf0d2cb3a0e60eb05f862d2376b90`。

已采纳：plan ids与实际样本簇双向setequal，无缺失/重复ids；draw矩阵完整2000列、每列3153项，全部为有限整数且范围1—3153。prepare与run均核验。每次抽样核重复簇全部成员及重复权重、行数等于所抽簇size之和。

未采纳“每次抽样unique簇数必须3153”的建议：有放回抽样下该断言错误，会排除合法抽样。无新增抽样。

selftest增加非球协方差、开区间p、独立2×2逆矩阵手算二次型、单位协方差负控、非平凡符号反转、簇重复权重、五种非法plan拒绝测试。Python标准库仅复算预期数学数值：p=0.7331334332833583；单位协方差错误替代p=0.5062468765617192；T0=1.1101011394030433。**未执行R或任何生产模型**。

另修复接续200后的TECHNICAL_200文件缺失时，按已完成前200条回填技术节点，不重估。

合同保持：cold主估计失败原样保留，warm仅诊断；6项全局BH/BY不缩水；无改N1来源或判定。

父协调原生调用：

```r
source(file.path(s,'limited_followup_20261006_v1/p3/p3_frozen_worker.R'))
test <- p3_self_test()
saveRDS(test,file.path(runroot,'P3_SELFTEST_POST_REVIEW.rds'))
# 再执行p3_legacy_audit与p3_prepare验证实际旧对象；selftest通过不代替实际数据门禁。
```

新校验函数体已加入运行identity。不得用旧identity检查点继续运行修改后的worker；若已经启动旧版须交父协调处理，不能绕过identity断言。
