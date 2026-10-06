# 来源范围与复现边界

本次只发布限定后续新增报告、CSV、脚本、冻结规则和验收证据。不重复打包旧微观数据、RDS或整个工程。归档路径保留模块结构；报告文件位于根目录。SOURCE_MANIFEST.json是报告引用清单，FROZEN_SOURCE_MANIFEST.json是本次全部实际打包来源/字节/SHA清单。

旧完整资料：https://github.com/lzhs1995/CMAverse-paper/tree/8e9fbc04cc3bf2acf158b0f8c1b21a42e4d54bb8/review/20261006

旧微观数据包（historical_package/data/analysis_13092.csv与对应RDS）：https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/8e9fbc04cc3bf2acf158b0f8c1b21a42e4d54bb8/review/20261006/02_review_part01.zip
原抽样计划包：https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/8e9fbc04cc3bf2acf158b0f8c1b21a42e4d54bb8/review/20261006/03_review_part01.zip
旧模型资料分包：https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/8e9fbc04cc3bf2acf158b0f8c1b21a42e4d54bb8/review/20261006/02_review_part01.zip 及 https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/8e9fbc04cc3bf2acf158b0f8c1b21a42e4d54bb8/review/20261006/02_review_part02.zip

运行脚本保留原绝对路径用于来源追溯；外部复现需按旧资料恢复目录或显式重绑定根路径，不应宣称解压后无需配置即可运行。此包提供真实运行与只读验收依据，不含凭据/会话数据库。新N1逐行样本未新增发布，依据数据字典与脚本从旧授权资料重建。当前包不把未提供的私人工作区文件伪装为包含项。
