# 数值收尾导出；只读取正式终态，不重拟合。
local({
.libPaths(c("/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/runtime/library",.libPaths()))
o <- "/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1/limited_followup_20261006_v1/numerical_closeout_20261006_v1"
l <- dirname(o)
r <- readRDS(file.path(o,"production_B2000_v1/RESULT.rds"))
s <- readRDS(file.path(o,"production_B2000_v1/CHECKPOINT.rds"))
old <- readRDS(file.path(l,"p3/production_B2000_v1/CHECKPOINT.rds"))
stopifnot(length(s$results)==2000L,identical(s$plan,old$plan),!dir.exists(file.path(o,"production_B2000_v1/RUN.lock")))
dest <- file.path(o,"exports");dir.create(dest,showWarnings=FALSE)
effects<-list();diagnostics<-list();comparison<-list()
for(b in 1:2000){
 stopifnot(identical(s$results[[b]]$draw_sha256,old$results[[b]]$draw_sha256))
 for(tag in names(r$draws)){
  j<-length(effects)+1L
  effects[[j]]<-data.frame(draw=b,component=tag,draw_sha256=s$results[[b]]$draw_sha256,t(r$draws[[tag]][b,]),check.names=FALSE)
  z<-s$results[[b]]$diagnostics[[tag]]
  val<-function(k,default=NA)if(is.null(z[[k]]))default else z[[k]]
  diagnostics[[j]]<-data.frame(draw=b,component=tag,ok=val("ok"),converged=val("converged"),rank=val("rank"),columns=val("columns"),gradient=val("scaled_gradient"),hessian_min=val("hessian_min"),error=val("error",""),stringsAsFactors=FALSE)
  ov<-old$results[[b]][[tag]];nv<-s$results[[b]][[tag]]
  comparison[[j]]<-data.frame(draw=b,component=tag,old_valid=!is.null(ov),new_valid=!is.null(nv),max_abs_difference=if(!is.null(ov)&&!is.null(nv))max(abs(ov-nv))else NA)
 }
}
ef<-do.call(rbind,effects);di<-do.call(rbind,diagnostics);co<-do.call(rbind,comparison)
stopifnot(nrow(ef)==6000L,all(co$new_valid),max(co$max_abs_difference[co$component=="probability"])<1e-10)
write.csv(ef,file.path(dest,"P3_ALL_6000_DRAWS.csv"),row.names=FALSE)
write.csv(di,file.path(dest,"P3_ALL_6000_DIAGNOSTICS.csv"),row.names=FALSE)
write.csv(co,file.path(dest,"P3_OLD_NEW_COMPARISON.csv"),row.names=FALSE)
points<-do.call(rbind,lapply(names(r$draws),function(tag)data.frame(component=tag,t(r$point[[tag]]))))
write.csv(points,file.path(dest,"P3_POINTS.csv"),row.names=FALSE)
tests<-do.call(rbind,lapply(names(r$tests),function(tag){z<-r$tests[[tag]];data.frame(test_id=paste0("P3_",toupper(tag)),component=tag,n_valid=z$n_valid,B=z$B,statistic=z$statistic,tail_count=sum(z$bootstrap_statistics>=z$statistic),p_raw=z$p_raw,status=z$status)}))
n<-read.csv(file.path(l,"n1_n2/runtime_v2/N1_formal_v3/N1_primary_four.csv"))
family<-rbind(n[,c("test_id","p_raw")],tests[,c("test_id","p_raw")])
family$q_BH6<-p.adjust(family$p_raw,"BH",n=6);family$q_BY6<-p.adjust(family$p_raw,"BY",n=6)
write.csv(tests,file.path(dest,"P3_OMNIBUS.csv"),row.names=FALSE)
write.csv(family,file.path(dest,"SIX_TEST_FAMILY.csv"),row.names=FALSE)
saveRDS(list(result=r,diagnostics=di,comparison=co,family=family,plan_identity=s$identity),file.path(dest,"COMPACT_RESULT.rds"))
capture.output(sessionInfo(),file=file.path(dest,"SESSION_INFO.txt"))
jsonlite::write_json(list(status="PASS",draws=2000,effect_rows=nrow(ef),probability_max_difference=max(co$max_abs_difference[co$component=="probability"]),old_original_valid=sum(co$old_valid[co$component=="original"]),new_original_valid=sum(co$new_valid[co$component=="original"]),index_exact=TRUE,glm2_version=as.character(packageVersion("glm2"))),file.path(dest,"ACCEPTANCE.json"),auto_unbox=TRUE,pretty=TRUE)
print(tests);print(family);cat("CLOSEOUT_EXPORT_VERIFIED\n")
})
