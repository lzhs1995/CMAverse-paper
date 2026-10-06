# CMAverse最终点值与bootstrap t0的来源差异

原生第三次prepare已通过索引SHA门禁，但TNIE全量等值断言暴露了错误契约。不是提高容差可以解决的问题。

源码链条：

- runtime/CMAverse_source_install/R/estinf.R:663首先调用est.gformula.grid(indices=NULL,outReg=TRUE)，生成最终est_grid；667随后调用boot。694明确以`est_grid[[i]]$est`作为gformula_effect_summary的effect.pe，而不是boots$t0。
- shared_bootstrap_diagnostic.R:57保存当时RNG，60重新调用完整样本statistic生成t0；66—72只把这个t0在相同RNG下再次运行以保存诊断grid，并验证二者完全一致。它未回到前一次est_grid调用前的随机状态。
- est.gformula.R:240/242通过rbinom模拟中介；256通过rnorm模拟连续中介；297—298还涉及模拟中介取样。故即使数据与参数完全相同，前一次最终点值与后一次bootstrap_t0自然间接量仍可存在Monte Carlo差异。
- est.gformula.R:406固定M的CDE使用EY1m/EY0m；410 TNIE使用模拟中介的EY11/EY10。当前没有postc，固定M的CDE不需要这次中介随机抽样。

修复：最终旧点值继续取原ALL_NATIVE_EFFECTS.csv（与旧METRICS一致的原始effect.pe）；bootstrap_t0另保存old_bootstrap_t0与old_point_sources两列，不伪称其TNIE相等。只对Delta_OR维持1e-12原严格等值检查，并保留旧系数直接代入CDE的1e-8核验。重抽样TNIE仍完整读取原1000grid，不混成点值。collect输出携带两来源表。

没有删去CDE一致性校验、没有把小差异改称零、没有重估。estinf.R加入来源manifest。此次仅静态修订，原生prepare需supervisor验证。
