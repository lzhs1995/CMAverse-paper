#!/usr/bin/env python3
# 从冻结结果构建来源表；绝不调用拟合脚本或复制微观数据。
from pathlib import Path
import csv, hashlib, json, math, datetime
C=Path(__file__).resolve().parent.parent
L=C.parent
S=L.parent
NC=L/'numerical_closeout_20261006_v1'
OUT=C/'results'
BIND=C/'bindings'
OUT.mkdir(parents=True,exist_ok=True)
def rows(p):
    with Path(p).open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
pins={}
def pin(p,role='frozen_result',expected=None):
    p=Path(p).resolve()
    assert p.is_file(),p
    d=dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p),role=role)
    if expected:assert d['sha256']==expected,(p,'hash mismatch')
    pins[str(p)]=d
    return d
def provenance(p,row):
    v=pin(p)
    return dict(source_path=v['path'],source_sha256=v['sha256'],source_bytes=v['bytes'],source_row=row)
def write(name,rr):
    assert rr,name
    fields=list(dict.fromkeys(k for r in rr for k in r))
    with (OUT/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rr)
def js(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
# 先核查既有绑定，不以当前重新计算的hash替换旧hash。
for d in json.loads((NC/'SOURCE_PINS.json').read_text()):
    pin(d['path'],'previous_numerical_contract',d['sha256'])
for rel in ['search_audit/INDEX_AUDIT.csv','search_audit/AUDIT.rds','search_audit/ALL_150_REGISTER.csv','search_audit/COVERAGE_150.csv','search_audit/RW_ALL_240.csv','search_audit/BOOTSTRAP_TEST_VALUES.csv','native/search_terminal.json','native/production_terminal.json','native/validation_terminal.json','exports/ACCEPTANCE.json','exports/INDEPENDENT_ARITHMETIC.json','exports/COMPACT_RESULT.rds','exports/P3_ALL_6000_DRAWS.csv','exports/P3_ALL_6000_DIAGNOSTICS.csv','exports/P3_OLD_NEW_COMPARISON.csv','independent_arithmetic_v1.py','VALIDATION.csv']:
    pin(NC/rel,'accepted_numerical_evidence')
for rel in ['selection_inputs_complete_v1/SOURCE_PROOFS.json','selection_inputs_complete_v1/INPUTS.rds','feasible_sampling_v1/screen.rds','candidate_data.R','screening_records.R']:
    pin(S/rel,'historical_search_contract')
proof=json.loads((S/'selection_inputs_complete_v1/SOURCE_PROOFS.json').read_text())
idx=rows(NC/'search_audit/INDEX_AUDIT.csv')
assert len(idx)==120 and len({r['spec_id'] for r in idx})==120
coverage=rows(NC/'search_audit/COVERAGE_150.csv')
assert len(coverage)==150 and sum(r['verified']=='TRUE' for r in coverage)==120
assert {r['spec_id'] for r in idx}=={r['spec_id'] for r in coverage if r['verified']=='TRUE'}
inputs=[]
for r in idx:
    id=r['spec_id']; pr=proof[id]
    assert r['execution_present']=='TRUE' and r['indices_and_seeds_match']=='TRUE'
    ep=Path(pr['validation']['path']).parent/id/'execution_inputs.rds'
    e=pin(ep,'actual_execution_inputs',r['execution_sha256'])
    m=pin(pr['metrics']['path'],'accepted_metrics',r['metrics_sha256'])
    assert m['sha256']==pr['metrics']['sha256']
    inputs.append(dict(spec_id=id,**e,accepted_index_audit_path=str(NC/'search_audit/INDEX_AUDIT.csv'),accepted_index_audit_sha256=sha(NC/'search_audit/INDEX_AUDIT.csv'),indices_and_seeds_match_reused=True,verification_scope='fresh file hash binding; existing R index/seed audit reused, not rerun',metrics_path=m['path'],metrics_sha256=m['sha256'],metrics_bytes=m['bytes']))
js(BIND/'EXECUTION_INPUTS_120.json',inputs)
with (BIND/'EXECUTION_INPUTS_120.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(inputs[0]));w.writeheader();w.writerows(inputs)
# 注册行及操作定义。中文字义不反向取自论文。
regp=NC/'search_audit/ALL_150_REGISTER.csv'
regs={r['spec_id']:r for r in rows(regp)}
definition=[]
for id in ['FEAS_031','FEAS_041']:
    r=regs[id]
    d=dict(spec_id=id,x_definition='本人实际收入期末高于基期（0→1）',m_definition=('本人相对婚姻满意度位置从基期不高于配偶变为期末高于配偶；非双方满意度普遍提高' if id=='FEAS_031' else '本人减配偶的婚姻满意度分差之区间变化；固定0→1分对比'),y_definition='本人向特定父母提供的实际月均经济支持期末高于基期',a=r['a'],astar=r['astar'],m_low=r['mval0'],m_high=r['mval1'],N=r['n'],clusters=r['clusters'],scale='marginal odds-ratio difference (Delta_CDE/Delta_OR), not probability points',x_code=r['x'],m_code=r['m'],y_code=r['y'],adjustment_registered=r['adjustment'],time_structure=r['time_structure'],conditional_support_caveat=r['support_note'],transform_source=str(S/'candidate_data.R'),transform_source_sha256=sha(S/'candidate_data.R'),**provenance(regp,id))
    definition.append(d)
write('CANDIDATE_DEFINITIONS.csv',definition)
# A: B200 原模型搜索校正；B: 历史B1000；C: 同/去dwm B1000中心化区间；D: 修订减原模型。
panels=[]
rw=rows(NC/'search_audit/RW_ALL_240.csv')
for r in rw:
    if r['spec_id'] not in ['FEAS_031','FEAS_041']:continue
    panels.append(dict(panel_id='A_B200_SEARCH',spec_id=r['spec_id'],metric=r['metric'],model_version='original_with_dwm',inference_version='centered_absolute_fixed_SD_RW',B=r['B'],estimate=r['point_test_scale'],ci_lower='',ci_upper='',p_raw=r['p_centered'],p_RW_within120=r['p_RW_within_metric'],p_RW_all240=r['p_RW_all240'],estimate_scale='log_OR' if r['metric']=='TNIE' else 'marginal_OR_difference',note='原150登记/120可估/240目标；不移植到去dwm版本',**provenance(NC/'search_audit/RW_ALL_240.csv',r['spec_id']+'|'+r['metric'])))
for id in ['FEAS_031','FEAS_041']:
    p=S/f'verify_B1000_v1/{id}/METRICS.csv'
    for r in rows(p):
        panels.append(dict(panel_id='B_B1000_LEGACY',spec_id=id,metric=r['metric'],model_version='original_with_dwm',inference_version='legacy_centered_p_percentile_interval',B=r['valid'],estimate=r['estimate'],ci_lower=r['ci_low'],ci_upper=r['ci_high'],p_raw=r['p_exploratory'],p_RW_within120='',p_RW_all240='',estimate_scale='OR' if r['metric']=='TNIE' else 'marginal_OR_difference',note='原筛选后精化；非独立验证；不可与A的B200 p混写',**provenance(p,r['metric'])))
    p=L/f'p1_p2/readonly_summary_v1/{id}_intervals.csv'
    for r in rows(p):
        version=r['version']
        panels.append(dict(panel_id='D_PAIRED_CHANGE' if version=='paired' else 'C_B1000_CENTERED_INTERVAL',spec_id=id,metric=r['metric'],model_version={'old':'original_with_dwm','revised':'revised_without_dwm','paired':'revised_minus_original'}[version],inference_version=r['interval_status'],B=r['planned_B'],estimate=r['estimate'],ci_lower=r['lower'],ci_upper=r['upper'],p_raw='',p_RW_within120='',p_RW_all240='',estimate_scale='OR' if r['metric']=='TNIE' and version!='paired' else ('OR_difference' if r['metric']=='TNIE' else 'marginal_OR_difference'),note='仅既有全有效中心化区间；本轮不生成p；去dwm不证明其余控制项时间属性全部修复',**provenance(p,version+'|'+r['metric'])))
write('CANDIDATE_HISTORY_PANELS.csv',panels)
period=[];loo=[]
for id in ['FEAS_031','FEAS_041']:
    p=L/f'p1_p2/readonly_summary_v1/{id}_period.csv'
    for r in rows(p):
        period.append(dict(spec_id=id,period=r['unit'],N=r['n'],clusters=r['clusters'],Delta_OR=r['Delta_OR'],Delta_probability=r['Delta_probability'],valid=r['valid'],formula=r['formula'],note='去dwm分期点诊断；未生成分期CI/p',**provenance(p,r['unit'])))
    p=L/f'p1_p2/readonly_summary_v1/{id}_loo.csv';rr=rows(p)
    assert len(rr)==int(regs[id]['clusters']) and all(r['valid']=='TRUE' for r in rr)
    peak=max(rr,key=lambda x:float(x['change_fraction_revised']))
    loo.append(dict(spec_id=id,omitted_cluster_runs=len(rr),max_relative_change=float(peak['change_fraction_revised']),max_relative_change_percent=100*float(peak['change_fraction_revised']),max_change_unit=peak['unit'],Delta_OR_at_max=peak['Delta_OR'],all_same_negative_sign=all(float(r['Delta_OR'])<0 for r in rr),note='修订模型相对全样本点估计；不代表逐簇CI显著',**provenance(p,peak['unit'])))
write('CANDIDATE_PERIOD_DIAGNOSTICS.csv',period)
write('CANDIDATE_LOO_SUMMARY.csv',loo)
p=NC/'exports/P3_POINTS.csv'
write('P3_THREE_STATE.csv',[dict(**r,unit='probability' if r['component']=='probability' else 'yuan_per_month',estimand_note='每一W状态下收入0→1的标准化联系；差值为收入联系之差，不是满意度自身效应',**provenance(p,r['component'])) for r in rows(p)])
for name in ['P3_OMNIBUS.csv','SIX_TEST_FAMILY.csv']:
    p=NC/'exports'/name
    write(name,[dict(**r,**provenance(p,r['test_id'])) for r in rows(p)])
p=L/'n1_n2/runtime_v2/N1_formal_v3/N1_primary_four.csv';pin(p)
q={r['test_id']:r for r in rows(NC/'exports/SIX_TEST_FAMILY.csv')}
n1=[]
for r in rows(p):
    r.update({k:q[r['test_id']][k] for k in ['q_BH6','q_BY6']})
    r['global6_status']='COMPLETE_USING_NUMERICAL_CLOSEOUT_P3'
    r.update(provenance(p,r['test_id']))
    r['family_source_path']=str(NC/'exports/SIX_TEST_FAMILY.csv');r['family_source_sha256']=sha(NC/'exports/SIX_TEST_FAMILY.csv');n1.append(r)
write('N1_FOUR_WITH_FINAL_SIX_ADJUSTMENT.csv',n1)
pin(L/'p1_p2/readonly_summary_v1/ACCEPTANCE.json')
pin(L/'p1_p2/NATIVE_TERMINAL_points_v1.json')
# 所有源绑定只含路径/hash/bytes，零微观数据复制。
js(BIND/'SOURCE_PINS.json',list(pins.values()))
js(BIND/'SCOPE.json',dict(created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),new_models=0,new_R_index_audits=0,new_hypothesis_tests=0,microdata_copies=0,execution_input_files=120,execution_input_bytes=sum(x['bytes'] for x in inputs),source_pin_count=len(pins),coverage='150 registered, 120 estimable, 240 B200 targets; accepted R row-index/seed identity reused with fresh whole-file SHA256 matching',limits=['Not independent statistical confirmation','Not a general FWER calibration proof','No p-value transplanted across model or inference versions','P1/P2 remaining timing and OR noncollapsibility caveats retained']))
write('RESULT_VERSION_TABLE.csv',[dict(table_path=str(p),bytes=p.stat().st_size,sha256=sha(p),rows=len(rows(p)),numeric_origin='frozen CSV; no models; source row/hash columns embedded') for p in sorted(OUT.glob('*.csv')) if p.name!='RESULT_VERSION_TABLE.csv'])
print(json.dumps(dict(status='BUILT',tables=len(list(OUT.glob('*.csv'))),source_pins=len(pins),actual_execution_inputs=len(inputs),total_execution_input_bytes=sum(x['bytes'] for x in inputs))))

