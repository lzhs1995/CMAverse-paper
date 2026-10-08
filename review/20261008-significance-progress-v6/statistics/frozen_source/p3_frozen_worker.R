# P3 冻结后继；source 仅定义函数，不提交或运行模型。
# 调用者提供按原 source 顺序载入的 e，先完成 NLM 裁定及原生 self test。
p3_validate_plan <- function(plan,cluster,expected_B=2000L,expected_clusters=3212L,
                             base_cluster=cluster,expected_eligible=expected_clusters) {
  stopifnot(!anyNA(cluster),!anyNA(base_cluster),!anyNA(plan$ids),!anyDuplicated(plan$ids),
    length(plan$ids)==expected_clusters,
    identical(plan$ids,sort(unique(base_cluster))),
    length(unique(cluster))==expected_eligible,all(cluster%in%plan$ids),
    length(setdiff(plan$ids,unique(cluster)))==expected_clusters-expected_eligible,
    plan$B==expected_B,is.matrix(plan$draws),is.numeric(plan$draws),
    nrow(plan$draws)==length(plan$ids),ncol(plan$draws)==expected_B,
    !anyNA(plan$draws),all(is.finite(plan$draws)),
    all(plan$draws==floor(plan$draws)),all(plan$draws>=1L),all(plan$draws<=length(plan$ids)))
  invisible(TRUE)
}

p3_draw_rows <- function(rows_by,draw) {
  # 原全局计划允许零贡献簇；重复抽中必须带入该簇全部合格成员。
  sizes<-lengths(rows_by);members<-unlist(rows_by,use.names=FALSE)
  stopifnot(length(draw)==length(rows_by),!anyNA(draw),all(is.finite(draw)),
    all(draw==floor(draw)),all(draw>=1L),all(draw<=length(rows_by)),
    !anyDuplicated(members),setequal(members,seq_len(length(members))))
  rows<-as.integer(unlist(rows_by[draw],use.names=FALSE))
  stopifnot(length(rows)==sum(sizes[draw]))
  expected<-rep(tabulate(draw,nbins=length(rows_by)),sizes)
  stopifnot(identical(as.integer(tabulate(rows,nbins=length(members))[members]),as.integer(expected)))
  rows
}

# 只核数据/计划映射，不拟合模型；两条路径使用不同的行展开实现。
p3_domain_check <- function(base,eligible,plan,cluster,columns=c(1L,17L,200L)) {
  stopifnot(requireNamespace("digest",quietly=TRUE))
  p3_validate_plan(plan,eligible[[cluster]],base_cluster=base[[cluster]],expected_eligible=3153L)
  stopifnot(identical(plan$data_sha256,digest::digest(base,algo="sha256")),
    identical(plan$draw_sha256,digest::digest(plan$draws,algo="sha256")),
    !anyNA(base$stable_row_id),!anyDuplicated(base$stable_row_id),
    !anyNA(eligible$stable_row_id),!anyDuplicated(eligible$stable_row_id))
  map<-match(eligible$stable_row_id,base$stable_row_id)
  stopifnot(!anyNA(map),identical(eligible[[cluster]],base[[cluster]][map]))
  gi<-match(eligible[[cluster]],plan$ids)
  rows_by<-split(seq_len(nrow(eligible)),factor(gi,levels=seq_along(plan$ids)))
  zero<-plan$ids[lengths(rows_by)==0L]
  stopifnot(length(zero)==59L,setequal(zero,setdiff(plan$ids,unique(eligible[[cluster]]))))
  audit<-lapply(columns,function(b){
    stopifnot(b>=1L,b<=plan$B)
    draw<-plan$draws[,b];rows<-p3_draw_rows(rows_by,draw)
    # 独立路径：逐簇从完整数据取成员，再按已冻结资格身份筛选。
    full_rows<-unlist(lapply(draw,function(k)which(base[[cluster]]==plan$ids[k])),use.names=FALSE)
    full_ids<-base$stable_row_id[full_rows]
    full_ids<-full_ids[full_ids%in%eligible$stable_row_id]
    sub_ids<-eligible$stable_row_id[rows]
    stopifnot(identical(full_ids,sub_ids),
      identical(as.integer(table(factor(full_ids,levels=eligible$stable_row_id))),
                as.integer(table(factor(sub_ids,levels=eligible$stable_row_id)))))
    data.frame(draw=b,rows=length(rows),zero_contribution_draws=sum(lengths(rows_by)[draw]==0L),
      eligible_selections=sum(lengths(rows_by)[draw]>0L),unique_eligible_clusters=length(unique(gi[rows])),
      row_sequence_sha256=digest::digest(sub_ids,algo="sha256"),equivalent=TRUE)
  })
  list(status="DOMAIN_AND_FIXED_DRAWS_VERIFIED",base_clusters=3212L,eligible_clusters=3153L,
    zero_ids=zero,base_data_sha256=plan$data_sha256,draw_sha256=plan$draw_sha256,
    fixed_draws=do.call(rbind,audit))
}

p3_validate_native <- function(e,legacy_root,dest=NULL) {
  z<-readRDS(file.path(legacy_root,"production_two_stage_v1/prepared_data.rds"))
  plan_path<-file.path(legacy_root,"production_two_stage_v1/plan2000.rds")
  before<-digest::digest(file=plan_path,algo="sha256");plan<-readRDS(plan_path)
  sp<-e$AB_SPECS[[1L]]
  ss<-e$prepare_AB_samples(z$d,sp,e$covs_for(sp$drop),TRUE,"y1_any","y1_amt")
  e$require_sample_gate(ss$gateB)
  stopifnot(nrow(ss$B)==12634L)
  ans<-p3_domain_check(z$d,ss$B,plan,e$CLUSTER)
  stopifnot(identical(before,digest::digest(file=plan_path,algo="sha256")))
  ans$plan_file_sha256<-before;ans$self_test<-p3_self_test();ans$models_run<-0L
  if(!is.null(dest))saveRDS(ans,dest)
  ans
}

p3_prepare <- function(e, legacy_root) {
  z <- readRDS(file.path(legacy_root,"production_two_stage_v1/prepared_data.rds"))
  old <- readRDS(file.path(legacy_root,"production_two_stage_v1/B200_A1.rds"))
  r6 <- readRDS(file.path(legacy_root,"sensitivity_remaining_v1/fit_R6_B1.rds"))
  plan <- readRDS(file.path(legacy_root,"production_two_stage_v1/plan2000.rds"))
  sp <- e$AB_SPECS[[1L]]
  stopifnot(sp$x=="xa",sp$w=="w_self3",sp$drop=="self",plan$B==2000L,
            ncol(plan$draws)==2000L,old$B$boot$B==200L,r6$boot$B==500L)
  ss <- e$prepare_AB_samples(z$d,sp,e$covs_for(sp$drop),TRUE,"y1_any","y1_amt")
  e$require_sample_gate(ss$gateB)
  domain <- p3_domain_check(z$d,ss$B,plan,e$CLUSTER)
  same_formula <- function(a,b)identical(deparse(a),deparse(b))
  stopifnot(nrow(ss$B)==12634L,same_formula(ss$fA,old$fA),same_formula(ss$fB,old$fB),
            same_formula(ss$fA,r6$fA),same_formula(ss$fB,r6$fB),
            !anyDuplicated(ss$B$stable_row_id),!anyNA(ss$B$y1_amt),
            all(ss$B$y1_amt>=0),all(ss$B$y1_any==as.integer(ss$B$y1_amt>0)))
  cap <- read.csv(file.path(legacy_root,"sensitivity_remaining_v1/FIXED_CONTRASTS.csv"))$amount_cap99
  stopifnot(length(cap)==1L,abs(cap-2664.29840142096)<1e-9)
  dc <- ss$B;dc$y1_amt <- pmin(dc$y1_amt,cap)
  stopifnot(isTRUE(all.equal(e$stat_AB(ss$B,ss$fA,ss$fB,"xa","w_self3"),old$B$est,tolerance=1e-10)),
            isTRUE(all.equal(e$stat_AB(dc,ss$fA,ss$fB,"xa","w_self3"),r6$est,tolerance=1e-10)))
  frozen <- list(data=ss$B,plan=plan,fA=ss$fA,fB=ss$fB,cap=cap,cluster=e$CLUSTER,
       old=old,r6=r6,source_root=legacy_root,base_data=z$d,domain=domain)
  own <- p3_one(ss$B,frozen,e)
  keys<-c("T_Y_le3","T_Y_4","T_Y_5","d_Y","d_Y_5v4")
  stopifnot(isTRUE(all.equal(unname(own$original),unname(old$B$est[keys]),tolerance=1e-10)),
            isTRUE(all.equal(unname(own$capped),unname(r6$est[keys]),tolerance=1e-10)))
  frozen
}

p3_attempt <- function(expr) {
  warns <- character()
  a <- tryCatch(withCallingHandlers(expr,warning=function(w){warns<<-c(warns,conditionMessage(w));invokeRestart("muffleWarning")}),error=function(e)e)
  if(inherits(a,"error"))list(ok=FALSE,error=conditionMessage(a),warnings=warns)
  else list(ok=TRUE,value=a,warnings=warns)
}

p3_legacy_audit <- function(legacy_root) {
  a<-readRDS(file.path(legacy_root,"production_two_stage_v1/B200_A1.rds"))
  r<-readRDS(file.path(legacy_root,"sensitivity_remaining_v1/fit_R6_B1.rds"))
  p<-readRDS(file.path(legacy_root,"production_two_stage_v1/plan2000.rds"))
  q<-readRDS(file.path(legacy_root,"sensitivity_remaining_v1/plan500.rds"))
  stopifnot(a$B$boot$B==200L,length(a$B$boot$ok_idx)==195L,
    length(a$B$boot$fail_idx)==5L,all(a$B$boot$fail_msg=="Gamma 未收敛"),
    r$boot$B==500L,length(r$boot$ok_idx)==500L,length(r$boot$fail_idx)==0L)
  list(B1=list(B=200L,valid=195L,failed=a$B$boot$fail_idx,error=a$B$boot$fail_msg,
       draw_sha256=vapply(a$B$boot$fail_idx,function(b)digest::digest(p$draws[,b],algo="sha256"),character(1))),
       R6_B1=list(B=500L,valid=500L),
       old_first500_identical=identical(p$ids,q$ids)&&identical(p$draws[,1:500,drop=FALSE],q$draws),
       new_plan="原主检验2000固定索引；原金额与封顶共享；不假定与R6旧500相同")
}

# Gamma 起点诊断保持 family/link/样本/公式/maxit 不变；不替换失败的正式重复。
p3_gamma <- function(f,dat,start=NULL) {
  pos <- dat[dat$y1_amt>0,,drop=FALSE]
  mm <- model.matrix(f,pos)
  if(is.null(start))start <- c(log(mean(pos$y1_amt)),rep(0,ncol(mm)-1L))
  if(length(start)!=ncol(mm)||any(!is.finite(start)))stop("Gamma 起点维度错误")
  m <- glm(f,data=pos,family=Gamma(link="log"),start=start,control=glm.control(maxit=200L))
  info <- list(converged=m$converged,iterations=m$iter,rank=m$rank,columns=ncol(mm),
               logLik=as.numeric(logLik(m)),deviance=m$deviance,n_positive=nrow(pos))
  list(model=m,info=info,usable=isTRUE(m$converged)&&!anyNA(coef(m))&&all(is.finite(coef(m))))
}

p3_one <- function(dat,frozen,e,warm=NULL) {
  ll <- c("le3","4","5")
  out <- list(probability=NULL,original=NULL,capped=NULL,diagnostics=list())
  a <- p3_attempt(e$fit_logit(frozen$fA,dat))
  out$diagnostics$probability <- a[setdiff(names(a),"value")]
  if(!a$ok)return(out)
  m1 <- a$value
  cf <- lapply(ll,function(l)list(e$set_cf(dat,"xa",1,"w_self3",l),e$set_cf(dat,"xa",0,"w_self3",l)))
  pp <- p3_attempt(lapply(cf,function(q)lapply(q,function(nd)predict(m1,nd,type="response"))))
  if(!pp$ok){out$diagnostics$probability<-pp;return(out)}
  ps <- pp$value
  pack <- function(t)c(T_le3=t[1],T_4=t[2],T_5=t[3],d_5vle3=t[3]-t[1],d_5v4=t[3]-t[2])
  out$probability <- pack(vapply(ps,function(q)mean(q[[1]]-q[[2]]),numeric(1)))
  if(any(!is.finite(out$probability))){out$probability<-NULL;return(out)}
  for(tag in c("original","capped")) {
    dd <- dat;if(tag=="capped")dd$y1_amt<-pmin(dd$y1_amt,frozen$cap)
    g <- p3_attempt(p3_gamma(frozen$fB,dd))
    info <- g[setdiff(names(g),"value")]
    if(g$ok)info <- c(info,g$value$info)
    info$positive_clusters <- length(unique(dd[[frozen$cluster]][dd$y1_amt>0]))
    info$max_amount <- max(dd$y1_amt)
    out$diagnostics[[tag]] <- info
    good <- g$ok&&g$value$usable
    if(good) {
      gy <- p3_attempt(vapply(seq_along(cf),function(j){
        q<-cf[[j]];p<-ps[[j]]
        mean(p[[1]]*predict(g$value$model,q[[1]],type="response")-
             p[[2]]*predict(g$value$model,q[[2]],type="response"))
      },numeric(1)))
      if(gy$ok&&all(is.finite(gy$value)))out[[tag]]<-pack(gy$value)
      else out$diagnostics[[tag]]$prediction_error<-if(gy$ok)"nonfinite"else gy$error
    }
    if(!good&&!is.null(warm[[tag]])) {
      ww <- p3_attempt(p3_gamma(frozen$fB,dd,warm[[tag]]))
      out$diagnostics[[tag]]$warm_diagnostic <- if(ww$ok)c(list(ok=TRUE,usable=ww$value$usable,coefficients=coef(ww$value$model)),ww$value$info)else ww
      # 无论 warm-start 是否成功，正式结果保留原失败；另行裁定才能版本化修复。
    }
  }
  out
}

p3_omnibus <- function(point,mat,B=2000L) {
  ok <- complete.cases(mat)&apply(mat,1,function(z)all(is.finite(z)))
  ans <- list(B=B,n_valid=sum(ok),valid_ratio=sum(ok)/B,p_raw=NA_real_,status="WITHHELD")
  if(sum(ok)/B<.98||is.null(point)||any(!is.finite(point)))return(ans)
  jj <- c("d_5vle3","d_5v4")
  xx <- mat[ok,jj,drop=FALSE];v <- cov(xx);ans$covariance<-v
  if(any(!is.finite(v))||min(eigen(v,symmetric=TRUE,only.values=TRUE)$values)<=max(diag(v))*1e-10)return(ans)
  iv <- solve(v);t0 <- as.numeric(t(point[jj])%*%iv%*%point[jj])
  cc <- sweep(xx,2,point[jj],"-")
  tt <- rowSums((cc%*%iv)*cc)
  ans$p_raw <- (1+sum(tt>=t0))/(1+nrow(xx))
  ans$statistic <- t0;ans$bootstrap_statistics<-tt;ans$status<-"ESTIMATED_POST_SELECTION"
  ans$definition <- "Fixed covariance quadratic norm; null draws = bootstrap contrast minus original point, 2df vector; NOT chi-square calibration claim"
  ans
}

p3_run <- function(frozen,e,dest,through=2000L,chunk=25L,progress=function(b,B)NULL) {
  stopifnot(through%in%c(200L,2000L),chunk%in%c(25L,50L),requireNamespace("digest",quietly=TRUE))
  p3_domain_check(frozen$base_data,frozen$data,frozen$plan,frozen$cluster)
  dir.create(dest,recursive=TRUE,showWarnings=FALSE)
  # 合同绑定数据、全2000索引及实际函数体；已结束抽样只续算，不补抽。
  identity <- digest::digest(list(frozen$data,frozen$plan,frozen$fA,frozen$fB,frozen$cap,
    frozen$base_data,frozen$domain,body(p3_domain_check),body(p3_one),body(p3_gamma),body(p3_attempt),body(p3_run),body(p3_omnibus),body(p3_validate_plan),body(p3_draw_rows),body(e$fit_logit),body(e$set_cf)),algo="sha256")
  checkpoint <- file.path(dest,"CHECKPOINT.rds")
  if(file.exists(checkpoint)) {state<-readRDS(checkpoint);stopifnot(identical(state$identity,identity))}
  else {
    state<-list(identity=identity,results=list(),plan=frozen$plan,
       point=p3_one(frozen$data,frozen,e),warm=list(),created_at=as.character(Sys.time()))
    for(tag in c("original","capped")) {
      dd<-frozen$data;if(tag=="capped")dd$y1_amt<-pmin(dd$y1_amt,frozen$cap)
      mm<-p3_gamma(frozen$fB,dd);if(mm$usable)state$warm[[tag]]<-coef(mm$model)
    }
  }
  persist <- function(){tmp<-paste0(checkpoint,".tmp-",Sys.getpid());saveRDS(state,tmp);if(!file.rename(tmp,checkpoint))stop("检查点写入失败")}
  persist()
  gi <- match(frozen$data[[frozen$cluster]],frozen$plan$ids);stopifnot(!anyNA(gi))
  rows_by <- split(seq_len(nrow(frozen$data)),factor(gi,levels=seq_along(frozen$plan$ids)))
  if(length(state$results)<through)for(b in seq.int(length(state$results)+1L,through)) {
    rows <- p3_draw_rows(rows_by,frozen$plan$draws[,b])
    value <- if(!length(rows))list(probability=NULL,original=NULL,capped=NULL,
      diagnostics=list(sample_error="EMPTY_GLOBAL_DRAW_NO_REDRAW")) else
      p3_one(frozen$data[rows,,drop=FALSE],frozen,e,state$warm)
    value$sampling<-list(rows=length(rows),zero_contribution_draws=sum(lengths(rows_by)[frozen$plan$draws[,b]]==0L),
      eligible_selections=sum(lengths(rows_by)[frozen$plan$draws[,b]]>0L),unique_eligible_clusters=length(unique(gi[rows])))
    value$draw<-b;value$draw_sha256<-digest::digest(frozen$plan$draws[,b],algo="sha256")
    state$results[[b]]<-value
    if(b%%chunk==0L||b==200L||b==through){state$updated_at<-as.character(Sys.time());persist();progress(b,2000L)}
    if(b==200L)saveRDS(list(identity=identity,completed=b,status="TECHNICAL_CHECKPOINT_NOT_PVALUE_GATE",results=state$results[1:200]),file.path(dest,"TECHNICAL_200.rds"))
  }
  if(length(state$results)>=200L&&!file.exists(file.path(dest,"TECHNICAL_200.rds")))
    saveRDS(list(identity=identity,completed=200L,status="TECHNICAL_CHECKPOINT_NOT_PVALUE_GATE",results=state$results[1:200]),file.path(dest,"TECHNICAL_200.rds"))
  if(length(state$results)==2000L) {
    mats<-lapply(c("probability","original","capped"),function(tag){
      mm<-matrix(NA_real_,2000L,5L,dimnames=list(1:2000,c("T_le3","T_4","T_5","d_5vle3","d_5v4")))
      for(i in seq_len(2000L))if(!is.null(state$results[[i]][[tag]]))mm[i,]<-state$results[[i]][[tag]]
      mm
    });names(mats)<-c("probability","original","capped")
    tests<-lapply(c("original","capped"),function(tag)p3_omnibus(state$point[[tag]],mats[[tag]]));names(tests)<-c("original","capped")
    saveRDS(list(identity=identity,draws=mats,tests=tests,point=state$point,
      status="FUNCTION_COMPLETED_REQUIRES_NATIVE_TERMINAL",warm_used_in_primary=FALSE),file.path(dest,"RESULT.rds"))
  }
  invisible(state)
}

# 纯统计函数测试：不读取真实数据、不提交异步作业、不依赖偶然显著性。
p3_self_test <- function() {
  mat <- cbind(T_le3=rep(0,2000),T_4=rep(0,2000),T_5=rep(0,2000),
               d_5vle3=sin(seq_len(2000)),d_5v4=cos(seq_len(2000)))
  point <- setNames(rep(0,5),colnames(mat))
  a<-p3_omnibus(point,mat);stopifnot(a$p_raw==1,a$n_valid==2000L)
  fail<-mat;fail[1:41,]<-NA_real_;b<-p3_omnibus(point,fail)
  stopifnot(b$status=="WITHHELD",is.na(b$p_raw),b$n_valid==1959L)
  fail[41,]<-mat[41,];c<-p3_omnibus(point,fail);stopifnot(c$status=="ESTIMATED_POST_SELECTION")
  singular<-mat;singular[,5]<-singular[,4];d<-p3_omnibus(point,singular)
  stopifnot(d$status=="WITHHELD",is.na(d$p_raw))
  # 对比符号同时反转不改变整体二次型检验。
  point[4:5]<-c(.2,-.3);a<-p3_omnibus(point,mat)
  point[4:5]<- -point[4:5];mat[,4:5]<- -mat[,4:5]
  b<-p3_omnibus(point,mat);stopifnot(identical(a$p_raw,b$p_raw))
  # 非球协方差、开区间p；独立2x2手算逆矩阵，不用solve重写同一实现。
  t<-seq_len(2000);xx<-cbind(3*sin(t),.5*cos(t)+.2*sin(t))
  mat[,4:5]<-xx;point[4:5]<-c(2,.3);a<-p3_omnibus(point,mat)
  xc<-sweep(xx,2,colMeans(xx),'-');v11<-sum(xc[,1]^2)/1999
  v22<-sum(xc[,2]^2)/1999;v12<-sum(xc[,1]*xc[,2])/1999;det<-v11*v22-v12^2
  quad<-function(x)(v22*x[,1]^2-2*v12*x[,1]*x[,2]+v11*x[,2]^2)/det
  t0<-quad(matrix(point[4:5],nrow=1));cc<-sweep(xx,2,point[4:5],'-');tt<-quad(cc)
  manual_p<-(1+sum(tt>=t0))/2001
  stopifnot(a$p_raw>0,a$p_raw<1,abs(a$p_raw-manual_p)<1e-12,
    abs(a$statistic-t0)<1e-12,max(abs(a$bootstrap_statistics-tt))<1e-12)
  # 单位矩阵替代真实协方差必须得到不同p，防止遗漏联合协方差。
  identity_p<-(1+sum(rowSums(cc^2)>=sum(point[4:5]^2)))/2001
  stopifnot(abs(a$p_raw-identity_p)>1e-3)
  minus<-mat;minus[,4:5]<- -minus[,4:5];negative<-point;negative[4:5]<- -negative[4:5]
  stopifnot(identical(a$p_raw,p3_omnibus(negative,minus)$p_raw))
  plan<-list(ids=c('a','b'),B=2L,draws=matrix(c(1L,1L,2L,1L),nrow=2))
  p3_validate_plan(plan,c('b','a','b'),2L,2L)
  stopifnot(identical(p3_draw_rows(list(c(2L),c(1L,3L)),c(2L,2L)),c(1L,3L,1L,3L)))
  for(kind in c('extra','duplicate','fraction','range','short')) {
    bad<-plan
    if(kind=='extra')bad$ids<-c('a','c')
    if(kind=='duplicate')bad$ids<-c('a','a')
    if(kind=='fraction')bad$draws[1,1]<-1.5
    if(kind=='range')bad$draws[1,1]<-3
    if(kind=='short')bad$draws<-bad$draws[1,,drop=FALSE]
    stopifnot(inherits(try(p3_validate_plan(bad,c('b','a','b'),2L,2L),silent=TRUE),'try-error'))
  }
  # 已登记基础域的零贡献簇允许进入计划；重复权重与全空重复可精确验证。
  zp<-list(ids=c('a','b','c'),B=2L,draws=matrix(c(1L,3L,1L,3L,3L,3L),nrow=3))
  p3_validate_plan(zp,c('b','a','b'),2L,3L,c('a','b','c'),2L)
  rb<-list(2L,c(1L,3L),integer())
  stopifnot(identical(p3_draw_rows(rb,zp$draws[,1]),c(2L,2L)),
    identical(p3_draw_rows(rb,zp$draws[,2]),integer()),
    inherits(try(p3_validate_plan(zp,c('b','x'),2L,3L,c('a','b','c'),2L),silent=TRUE),'try-error'),
    inherits(try(p3_validate_plan(zp,c('b','a'),2L,3L,c('a','b','x'),2L),silent=TRUE),'try-error'))
  invisible(list(status="SELF_TEST_PASSED",checks=13L,real_data_read=FALSE,
    anisotropic_p=a$p_raw,manual_p=manual_p,identity_covariance_p=identity_p))
}
