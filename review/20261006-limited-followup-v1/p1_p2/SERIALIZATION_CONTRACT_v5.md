# P1/P2纯对象持久化修复

静态根因：as.formula默认env=parent.frame()；在p12_prepare内创建oldformula时捕获了整个局部求值环境。该环境含e、se、dat、inp、mm、1000个索引以及最终obj自引用。RDS会序列化该闭包图，导致88MB临时对象；读回得到新的局部环境引用，严格identical(x,readRDS(tmp))失败。这个错误不是模型数值不同。

最小修复：唯一模型公式在构造时明确env=baseenv()，并断言其环境。所有列均由data=dat传入，公式不依赖局部自定义函数，因此移除局部环境不改变设计矩阵定义。保留p12_write原严格identical，不改成all.equal忽略环境，不改变模型/数值/索引校验。

另加写入前tmp不存在门禁，防止再次尝试覆盖失败证据。旧88MB INPUTS.rds.tmp保持原位，SHA见JSON；旧worker保存在before_serialization_v5.R。

原生验证：重source当前worker；先p12_serialization_self_test()（纯对象序列化/设计矩阵，不拟合）；原FEAS_031目录有失败证据，不复用。以新且不存在的FEAS_031_prepare_v5目录调用p12_prepare('FEAS_031', new_destination)，将再次通过完整来源/原索引/点值/CDE门禁并执行严格RDS读回。通过后记录input bytes及SHA，后续执行使用返回对象中的destination。禁止删除旧失败目录以伪装首次成功。

本次未执行R/未重估；上述运行结果必须由supervisor在原生会话实核。
