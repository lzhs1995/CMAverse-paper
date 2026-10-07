# 仅读取历史结果；不重估任何筛选模型。
s<-"/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1";out<-"/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1/limited_followup_20261006_v1/numerical_closeout_20261006_v1/search_audit"
dir.create(out,showWarnings=FALSE)
x<-readRDS(file.path(s,"selection_inputs_complete_v1/INPUTS.rds"))
proof<-jsonlite::read_json(file.path(s,"selection_inputs_complete_v1/SOURCE_PROOFS.json"))
plan<-readRDS(file.path(s,"feasible_sampling_v1/screen.rds"))
keep<-which(x$verified);stopifnot(length(keep)==120L,length(plan$draws)==200L)
audit<-list()
for(j in keep) {
 id<-x$meta$spec_id[j];pr<-proof[[id]]
 ep<-file.path(dirname(pr$validation$path),id,"execution_inputs.rds")
 present<-file.exists(ep);aligned<-NA
 if(present) {
  z<-readRDS(ep)
  map<-lapply(plan$clusters,function(g)which(z$sample$cluster==g))
  expected<-lapply(plan$draws,function(draw)as.integer(unlist(map[match(draw,plan$clusters)],use.names=FALSE)))
  aligned<-identical(z$actual_indices,expected)&&identical(z$replicate_seeds,plan$replicate_seeds)
  stopifnot(aligned)
 }
 mp<-pr$metrics$path
 stopifnot(file.exists(mp),digest::digest(file=mp,algo="sha256")==pr$metrics$sha256)
 m<-readRDS(mp)
 stopifnot(isTRUE(all.equal(unname(m$point$test_value),unname(c(x$point$TNIE[j],x$point$Delta_CDE[j])),tolerance=0)),
  isTRUE(all.equal(unname(m$bootstrap_test_values),unname(cbind(x$draws$TNIE[,j],x$draws$Delta_CDE[,j])),tolerance=0)))
 audit[[id]]<-data.frame(spec_id=id,execution_present=present,indices_and_seeds_match=aligned,
  execution_sha256=if(present)digest::digest(file=ep,algo="sha256")else NA_character_,
  metrics_sha256=pr$metrics$sha256)
}
write.csv(do.call(rbind,audit),file.path(out,"INDEX_AUDIT.csv"),row.names=FALSE)
pt<-c(x$point$TNIE[keep],x$point$Delta_CDE[keep])
D<-cbind(x$draws$TNIE[,keep],x$draws$Delta_CDE[,keep])
sdv<-apply(D,2,sd);stopifnot(all(sdv>0),all(is.finite(D)))
dev<-abs(sweep(D,2,pt));t0<-abs(pt)/sdv;Tn<-sweep(dev,2,sdv,"/")
raw<-(1+colSums(dev>=matrix(abs(pt),nrow(D),length(pt),byrow=TRUE)))/(nrow(D)+1)
rw<-function(cols) {
 ord<-cols[order(t0[cols],decreasing=TRUE)];p<-numeric(length(ord))
 for(k in seq_along(ord))p[k]<-(1+sum(apply(Tn[,ord[k:length(ord)],drop=FALSE],1,max)>=t0[ord[k]]))/(nrow(D)+1)
 ans<-rep(NA_real_,length(pt));ans[ord]<-cummax(p);ans
}
all<-rw(seq_along(pt));tn<-rw(1:120);de<-rw(121:240)
res<-data.frame(spec_id=rep(x$meta$spec_id[keep],2),metric=rep(c("TNIE","Delta_CDE"),each=120),
 point_test_scale=pt,se_bootstrap=sdv,p_centered=raw,p_RW_within_metric=ifelse(is.na(tn),de,tn),
 p_RW_all240=all,B=200L)
write.csv(res,file.path(out,"RW_ALL_240.csv"),row.names=FALSE)
write.csv(x$meta,file.path(out,"ALL_150_REGISTER.csv"),row.names=FALSE)
write.csv(data.frame(spec_id=x$meta$spec_id,verified=x$verified),file.path(out,"COVERAGE_150.csv"),row.names=FALSE)
saveRDS(list(input=x,point=pt,draws=D,results=res,audit=audit,plan_sha256=digest::digest(file=file.path(s,"feasible_sampling_v1/screen.rds"),algo="sha256")),file.path(out,"AUDIT.rds"))
print(res[res$spec_id%in%c("FEAS_031","FEAS_041"),]);cat("SEARCH_ARITHMETIC_AND_INDEX_AUDIT_PASS\n")

