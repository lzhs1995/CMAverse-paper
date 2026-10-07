# 独立数值后继：不改统计目标及历史对象。
closeout_gamma <- function(f,dat,start=NULL) {
 pos<-dat[dat$y1_amt>0,,drop=FALSE]; X<-model.matrix(f,pos); y<-pos$y1_amt
 sc<-sqrt(colMeans(X^2));sc[sc==0]<-1;Z<-sweep(X,2,sc,"/")
 if(qr(Z)$rank<ncol(Z))stop("RANK_DEFICIENT")
 if(is.null(start))start<-c(log(mean(y)),rep(0,ncol(X)-1))
 warnings<-character()
 fit<-withCallingHandlers(glm(f,data=pos,family=Gamma("log"),start=start,
  method=glm2::glm.fit2,control=glm.control(epsilon=1e-10,maxit=500)),
  warning=function(w){warnings<<-c(warnings,conditionMessage(w));invokeRestart("muffleWarning")})
 b<-coef(fit)*sc
 objective<-function(b)mean(as.vector(Z%*%b)+y*exp(-as.vector(Z%*%b)))
 for(iter in 1:100) {
  eta<-as.vector(Z%*%b);r<-y*exp(-eta)
  g<-colMeans(Z*(1-r));H<-crossprod(Z,Z*r)/nrow(Z)
  if(max(abs(g))<=1e-10)break
  step<-solve(H,g);v<-objective(b);alpha<-1
  while(alpha>2^-30) {
   nb<-b-alpha*step;nv<-objective(nb)
   if(is.finite(nv)&&nv<=v-1e-4*alpha*sum(g*step)+1e-14)break
   alpha<-alpha/2
  }
  if(alpha<=2^-30)stop("LINE_SEARCH_FAILED")
  b<-nb
 }
 eta<-as.vector(Z%*%b);r<-y*exp(-eta);g<-colMeans(Z*(1-r))
 mineig<-min(eigen(crossprod(Z,Z*r)/nrow(Z),symmetric=TRUE,only.values=TRUE)$values)
 beta<-b/sc
 stopifnot(all(is.finite(beta)),max(abs(g))<=1e-8,mineig>0)
 # 使用最小预测适配器，不伪造含旧deviance/vcov的glm对象。
 model<-structure(list(coefficients=beta,terms=delete.response(terms(fit)),
  contrasts=fit$contrasts,xlevels=fit$xlevels),class="closeout_gamma")
 list(model=model,usable=TRUE,info=list(converged=TRUE,glm2_converged=fit$converged,
  iterations=iter,scaled_gradient=max(abs(g)),hessian_min=mineig,rank=qr(Z)$rank,
  columns=ncol(Z),objective=objective(b),n_positive=nrow(Z),warnings=warnings))
}
predict.closeout_gamma<-function(object,newdata,type="response",...) {
 X<-model.matrix(object$terms,newdata,contrasts.arg=object$contrasts,xlev=object$xlevels)
 stopifnot(identical(colnames(X),names(object$coefficients)))
 eta<-as.vector(X%*%object$coefficients)
 val<-if(type=="link")eta else exp(eta)
 stopifnot(all(is.finite(val)),type=="link"||all(val>0));val
}
coef.closeout_gamma<-function(object,...)object$coefficients

closeout_load<-function() {
 source("/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1/limited_followup_20261006_v1/p3/p3_bounded_driver_v1.R",local=TRUE)
 q<-p3d_load();q$e$p3_gamma<-closeout_gamma
 q
}
closeout_validate<-function(progress) {
 q<-closeout_load();f<-q$frozen;e<-q$e
 old<-readRDS("/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1/limited_followup_20261006_v1/p3/production_B2000_v1/CHECKPOINT.rds")
 failed<-which(vapply(old$results,function(z)is.null(z$original),logical(1)))
 stopifnot(length(failed)==49L)
 ids<-c(0L,failed,1L,17L,200L);stopifnot(!anyDuplicated(ids))
 rows_by<-split(seq_len(nrow(f$data)),factor(match(f$data[[f$cluster]],f$plan$ids),levels=seq_along(f$plan$ids)))
 records<-list()
 for(k in seq_along(ids)) {
  i<-ids[k];d<-if(i==0L)f$data else f$data[e$p3_draw_rows(rows_by,f$plan$draws[,i]),,drop=FALSE]
  now<-e$p3_one(d,f,e);before<-if(i==0L)old$point else old$results[[i]]
  stopifnot(max(abs(now$probability-before$probability))<1e-10)
  for(tag in c("original","capped")) {
   dd<-d;if(tag=="capped")dd$y1_amt<-pmin(dd$y1_amt,f$cap)
   p<-dd[dd$y1_amt>0,,drop=FALSE];X<-model.matrix(f$fB,p)
   a<-closeout_gamma(f$fB,dd);b<-closeout_gamma(f$fB,dd,lm.fit(X,log(p$y1_amt))$coefficients)
   diff<-max(abs(predict(a$model,p,type="link")-predict(b$model,p,type="link")))
   # 六反事实的有限正值校验在p3_one内完成。
   stopifnot(!is.null(now[[tag]]),diff<=1e-6)
   olddiff<-if(is.null(before[[tag]]))NA_real_ else max(abs(now[[tag]]-before[[tag]]))
   if(i%in%c(0L,1L,17L,200L))stopifnot(olddiff<.01)
   records[[length(records)+1L]]<-data.frame(draw=i,component=tag,
     gradient=a$info$scaled_gradient,hessian_min=a$info$hessian_min,
     rank=a$info$rank,columns=a$info$columns,second_start_eta_diff=diff,
     old_contrast_diff=olddiff,probability_diff=max(abs(now$probability-before$probability)),passed=TRUE)
  }
  write.csv(do.call(rbind,records),"/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1/limited_followup_20261006_v1/numerical_closeout_20261006_v1/VALIDATION.csv",row.names=FALSE)
  progress("validation",paste(k,"/53固定样本完成"))
 }
 saveRDS(list(status="PASS",cases=ids,records=do.call(rbind,records),
   self_test=e$p3_self_test(),session=sessionInfo()),"/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1/limited_followup_20261006_v1/numerical_closeout_20261006_v1/VALIDATION.rds")
 cat("VALIDATION_PASS\n")
}

