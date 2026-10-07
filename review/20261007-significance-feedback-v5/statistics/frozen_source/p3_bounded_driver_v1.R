# P3有界原生入口：source仅定义函数。读取原PREPARED_DOMAIN_v2，不重prepare。
p3d_root <- "/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1/limited_followup_20261006_v1/p3"
p3d_legacy <- "/Users/lzhs/Documents/cnm/tasks/01_R_analysis/CMAverse_恢复工程_20260927/next_phase/PLAN13_全稿实证复核与修订_20260929/exploratory_specification_search_20261005_v1/pro_claude_v4_consensus_20261005_v1"
p3d_dest <- file.path(p3d_root,"production_B2000_v1")
p3d_manifest <- file.path(p3d_root,"BOUNDED_INPUT_MANIFEST_v1.json")
p3d_sha <- function(p)digest::digest(file=p,algo="sha256")
p3d_disk_value <- function(usage) {
  if(!is.data.frame(usage)||nrow(usage)!=1L||!("available"%in%names(usage))||
     !is.numeric(usage$available)||length(usage$available)!=1L||
     !is.finite(usage$available)||usage$available<0)
    stop("DISK_GATE_UNKNOWN: 无唯一有限available bytes；停止新增P3重复")
  free<-as.double(usage$available)
  if(free<10e9)stop(sprintf("DISK_GATE_LOW: available=%.0f < 10000000000 bytes",free))
  free
}
p3d_disk <- function() {
  if(!requireNamespace("ps",quietly=TRUE))stop("DISK_GATE_UNKNOWN: ps不可用")
  u<-tryCatch(ps::ps_disk_usage(normalizePath(p3d_root,mustWork=TRUE)),
    error=function(err)stop("DISK_GATE_UNKNOWN: ",conditionMessage(err)))
  p3d_disk_value(u)
}
p3d_check_pins <- function() {
  stopifnot(requireNamespace("digest",quietly=TRUE),requireNamespace("jsonlite",quietly=TRUE))
  m<-jsonlite::read_json(p3d_manifest,simplifyVector=TRUE)
  stopifnot(is.data.frame(m$files),nrow(m$files)>0,!anyDuplicated(m$files$path),
    all(file.exists(m$files$path)),identical(as.numeric(file.info(m$files$path)$size),as.numeric(m$files$bytes)),
    identical(unname(vapply(m$files$path,p3d_sha,character(1))),unname(m$files$sha256)))
  m
}
p3d_load <- function() {
  m<-p3d_check_pins()
  e<-new.env(parent=environment())
  # 与原native_prepare_v1相同顺序，source不调用生产模型。
  for(p in m$source_order)sys.source(p,e)
  e$PKG_DIR<-file.path(dirname(dirname(p3d_legacy)),"delivery/Claude云端分析资料_20261005_v1")
  e$OUT_DIR<-file.path(p3d_legacy,"production_two_stage_v1")
  e$load_covariates();e$check_frozen()
  sys.source(file.path(p3d_root,"p3_frozen_worker.R"),e)
  f<-readRDS(file.path(p3d_root,"PREPARED_DOMAIN_v2.rds"))
  v<-readRDS(file.path(p3d_root,"GLOBAL_DOMAIN_NATIVE_VALIDATION.rds"))
  stopifnot(v$status=="DOMAIN_AND_FIXED_DRAWS_VERIFIED",v$models_run==0L,
    v$self_test$status=="SELF_TEST_PASSED",nrow(f$data)==12634L,f$plan$B==2000L,
    identical(f$source_root,p3d_legacy),identical(f$plan,readRDS(file.path(p3d_legacy,"production_two_stage_v1/plan2000.rds"))),
    identical(f$domain$draw_sha256,v$draw_sha256))
  e$p3_domain_check(f$base_data,f$data,f$plan,f$cluster)
  list(e=e,frozen=f,manifest=m)
}
p3d_checkpoint <- function(frozen,required_min=0L) {
  p<-file.path(p3d_dest,"CHECKPOINT.rds")
  if(!file.exists(p)) {
    if(required_min>0L)stop("CHECKPOINT_MISSING")
    # 非空产物目录但无checkpoint不自动重新开始。
    if(dir.exists(p3d_dest)&&length(list.files(p3d_dest,all.files=TRUE,no..=TRUE)))stop("ORPHAN_OUTPUT_STOP")
    return(NULL)
  }
  s<-readRDS(p);n<-length(s$results)
  stopifnot(n>=required_min,n<=2000L,identical(s$plan,frozen$plan),
    length(s$identity)==1L,is.character(s$identity),!is.null(s$point))
  keys<-c("T_le3","T_4","T_5","d_5vle3","d_5v4")
  if(n>0L)for(b in seq_len(n)) {
    z<-s$results[[b]]
    stopifnot(is.list(z),identical(z$draw,as.integer(b)),
      identical(z$draw_sha256,digest::digest(frozen$plan$draws[,b],algo="sha256")))
    for(tag in c("probability","original","capped"))if(!is.null(z[[tag]]))
      stopifnot(is.numeric(z[[tag]]),identical(names(z[[tag]]),keys),all(is.finite(z[[tag]])))
    # 冷起点失败保留NULL；warm_diagnostic不得填入正式结果。
    for(tag in c("original","capped"))if(!is.null(z$diagnostics[[tag]]$warm_diagnostic))
      stopifnot(is.null(z[[tag]]))
  }
  s
}
p3d_atomic_rds <- function(x,path) {
  tmp<-paste0(path,".tmp-",Sys.getpid());stopifnot(!file.exists(tmp))
  saveRDS(x,tmp);stopifnot(file.rename(tmp,path));invisible(path)
}
p3d_review200 <- function(frozen) {
  s<-p3d_checkpoint(frozen,200L)
  # 仅验证前200索引/输出结构及失败日志；不按p或有效率决定是否继续。
  z<-s$results[1:200]
  counts<-vapply(c("probability","original","capped"),function(tag)
    sum(vapply(z,function(a)!is.null(a[[tag]]),logical(1))),integer(1))
  t<-file.path(p3d_dest,"TECHNICAL_200.rds")
  if(!file.exists(t))stop("TECHNICAL_200_MISSING: 使用原screen入口完成200阶段")
  tt<-readRDS(t)
  stopifnot(tt$completed==200L,identical(tt$identity,s$identity),identical(tt$results,z),
    tt$status=="TECHNICAL_CHECKPOINT_NOT_PVALUE_GATE")
  r<-list(passed=TRUE,identity=s$identity,B=200L,technical_only=TRUE,
    p_value_used=FALSE,validity_ratio_used_as_promotion_gate=FALSE,
    valid_counts=counts,failed_counts=200L-counts,fixed_next_B=2000L,
    primary="cold",warm_diagnostic_only=TRUE,final_inference_min_valid=.98)
  p<-file.path(p3d_dest,"TECHNICAL_REVIEW_200.rds")
  if(file.exists(p))stopifnot(identical(readRDS(p),r))else p3d_atomic_rds(r,p)
  r
}
p3d_progress <- function(stage,message,completed,native_progress,free=NA_real_) {
  a<-list(stage=stage,message=message,completed=completed,planned_B=2000L,
    pid=Sys.getpid(),updated_at=format(Sys.time(),tz="UTC",usetz=TRUE),available_bytes=free)
  p<-file.path(p3d_root,"BOUNDED_PROGRESS.json");tmp<-paste0(p,".tmp-",Sys.getpid())
  jsonlite::write_json(a,tmp,auto_unbox=TRUE,pretty=TRUE);stopifnot(file.rename(tmp,p))
  cat(a$updated_at,stage,message,"\n");flush.console()
  native_progress(stage,message);invisible(a)
}
p3d_should_yield <- function(b,through,initial,max_chunks,elapsed,max_seconds) {
  b<through&&((b-initial)>=25L*max_chunks||elapsed>=max_seconds)
}
# 每25个固定draw落盘才让出；不强杀单个拟合；同目录续原索引，失败不补抽。
p3d_run <- function(phase=c("screen","review","finish"),max_chunks=2L,max_seconds=1800,
                    native_progress=function(...)NULL) {
  phase<-match.arg(phase)
  stopfile<-file.path(p3d_root,"BOUNDED_STOPPED.rds")
  if(file.exists(stopfile))stop("PREVIOUS_FAILURE_REQUIRES_REVIEW: 保留原失败证据，禁止自动重跑")
  stopifnot(length(max_chunks)==1L,is.finite(max_chunks),max_chunks>=1L,max_chunks==floor(max_chunks),
    length(max_seconds)==1L,is.finite(max_seconds),max_seconds>0,is.function(native_progress))
  free<-p3d_disk();q<-p3d_load()
  lock<-file.path(p3d_root,"BOUNDED_DRIVER.lock")
  if(!dir.create(lock,showWarnings=FALSE))stop("P3_SINGLE_WORKER_BUSY: 不自动清理或接管锁")
  on.exit(unlink(lock,recursive=TRUE),add=TRUE)
  jsonlite::write_json(list(pid=Sys.getpid(),phase=phase,at=as.character(Sys.time())),
    file.path(lock,"OWNER.json"),auto_unbox=TRUE)
  start<-Sys.time()
  s<-p3d_checkpoint(q$frozen);initial<-if(is.null(s))0L else length(s$results)
  completed<-initial
  emit<-function(stage,message,free=NA_real_)
    p3d_progress(stage,message,completed,native_progress,free)
  tryCatch({
    emit("start",paste("P3",phase,"原固定计划；已保存",initial),free)
    if(phase=="review") {
      r<-p3d_review200(q$frozen);emit("technical_review","200技术审查通过；继续固定2000，与p值无关")
      return(invisible(r))
    }
    through<-if(phase=="screen")200L else 2000L
    if(phase=="finish")p3d_review200(q$frozen)
    if(initial>through) {
      emit("already_beyond_stage","已有结果超过本阶段；不重放");return(invisible(list(status="ALREADY_BEYOND",completed=initial)))
    }
    progress<-function(b,B) {
      # 原worker在此callback前已原子持久化checkpoint，故让出不丢已保存draw。
      completed<<-b;free<-p3d_disk()
      emit("bootstrap_checkpoint",paste("P3已保存",b,"/2000；cold主估计/warm仅诊断"),free)
      if(p3d_should_yield(b,through,initial,max_chunks,
                         as.numeric(difftime(Sys.time(),start,units="secs")),max_seconds))
        stop(structure(list(message="预算到达，已保存检查点",call=NULL),
          class=c("p3_bounded_yield","error","condition")))
    }
    q$e$p3_run(q$frozen,q$e,p3d_dest,through=through,chunk=25L,progress=progress)
    s<-p3d_checkpoint(q$frozen,through);completed<-length(s$results)
    if(through==200L)p3d_review200(q$frozen)
    if(through==2000L) {
      rr<-readRDS(file.path(p3d_dest,"RESULT.rds"))
      stopifnot(identical(rr$identity,s$identity),identical(rr$warm_used_in_primary,FALSE),
        rr$status=="FUNCTION_COMPLETED_REQUIRES_NATIVE_TERMINAL")
      for(tag in c("original","capped")) {
        test<-rr$tests[[tag]]
        stopifnot(test$B==2000L,test$n_valid==sum(complete.cases(rr$draws[[tag]])))
        if(test$n_valid<1960L)stopifnot(test$status=="WITHHELD",is.na(test$p_raw))
      }
    }
    emit("phase_complete",paste(phase,"函数完成；仍需原async终态"))
    invisible(list(status="PHASE_COMPLETE",phase=phase,completed=completed,pid=Sys.getpid()))
  },p3_bounded_yield=function(err) {
    s<-p3d_checkpoint(q$frozen);completed<-length(s$results)
    emit("resumable","预算边界已保存；续原目录下一个固定draw，不新抽样")
    invisible(list(status="RESUMABLE",phase=phase,completed=completed,pid=Sys.getpid()))
  },error=function(err) {
    p3d_atomic_rds(list(phase=phase,completed_at_last_callback=completed,
      message=conditionMessage(err),pid=Sys.getpid(),at=as.character(Sys.time()),
      automatic_retry_allowed=FALSE),stopfile)
    try(emit("STOPPED",conditionMessage(err)),silent=TRUE);stop(err)
  })
}
