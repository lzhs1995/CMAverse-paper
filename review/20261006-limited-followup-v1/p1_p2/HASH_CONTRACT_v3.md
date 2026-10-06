# 原paired_actual_indices_sha256契约纠正

根因不是原索引变动，而是上一版把原list对象的默认序列化哈希误比对到另一种对象。原索引逐项重建identical已经通过。

原 `verify_B1000_v1/validate.R` 第20—26行明确：将actual_indices右填充到1000×max(lengths(ix))的NA_integer_矩阵；加row_lengths整数属性及representation字符串属性；最后digest(pad, algo="sha256", serialize=TRUE, serializeVersion=2)。因此list默认digest与原验收hash必然可能不同，不能当作源数据修改证据。

worker现在逐字继承该矩阵构造、两个属性与显式序列化版本2，再与原验收paired_actual_indices_sha256比较。保留原indices逐项identical、seeds、sampleSHA、registry/membershipSHA。没有换预期hash常量、没有删断言。validate.R本身加入来源manifest。

上一worker保存在p1_p2_frozen_worker.before_hash_contract_v3.R。此次未运行R/未重估；由supervisor原生prepare复核。
