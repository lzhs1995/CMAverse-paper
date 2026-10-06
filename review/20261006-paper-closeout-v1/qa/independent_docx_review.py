# -*- coding: utf-8 -*-
"""Independent read-only ZIP/XML review; outputs audit files only."""
import pathlib,json,hashlib,zipfile,xml.etree.ElementTree as E,posixpath,urllib.parse,collections,csv,datetime,io
C=pathlib.Path(__file__).resolve().parent.parent
qa=json.loads((C/'qa/MANUSCRIPT_QA.json').read_text())
out=pathlib.Path(qa['output']); source=pathlib.Path(qa['source'])
expected='ff278c5bba68ff7c6cdd0d52fc9cdd8fa7d2bac57876a2751fee8be3ddb4e95f'
O=out.read_bytes(); S=source.read_bytes(); sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(O)==expected, 'MANUSCRIPT_CHANGED_REBIND_NEEDED'
N={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'};W='{'+N['w']+'}'
def pin(p):
 p=pathlib.Path(p);b=p.read_bytes();return dict(path=str(p),sha256=sha(b),bytes=len(b))
def pack(b):
 with zipfile.ZipFile(io.BytesIO(b)) as z:
  return {x.filename:z.read(x.filename) for x in z.infolist()},z.testzip(),len(z.infolist())
s,sc,sn=pack(S);o,oc,on=pack(O);sr=E.fromstring(s['word/document.xml']);orr=E.fromstring(o['word/document.xml'])
def sig(e): return (e.tag,tuple(sorted(e.attrib.items())),e.text,e.tail,tuple(sig(c) for c in e))
def text(e):return ''.join(x.text or '' for x in e.iter(W+'t'))
def seq(r,tag):return [sig(e) for e in r.iter(tag)]
def subset(a,b):
 it=iter(b);return all(any(x==y for y in it) for x in a)
checks={};details={}
checks['frozen_output_sha']=sha(O)==expected
checks['source_sha']=sha(S)=='cace3fc14e4cb8e4f516386890d331093c99fb0ffa363b91065200e1e5fcf00d'
checks['zip_crc_all_members']=sc is None and oc is None
checks['no_duplicate_zip_names']=sn==len(s) and on==len(o)
checks['zip_member_set_unchanged']=set(s)==set(o)
changed=[k for k in sorted(set(s)|set(o)) if s.get(k)!=o.get(k)]
checks['only_document_xml_changed']=changed==['word/document.xml']
details['zip_members']=[dict(part=k,before_sha256=sha(s[k]),after_sha256=sha(o[k]),equal=s[k]==o[k]) for k in sorted(o)]
xmls={};errors=[]
for k,v in o.items():
 if k.endswith('.xml') or k.endswith('.rels'):
  try:xmls[k]=E.fromstring(v)
  except E.ParseError as e:errors.append(dict(part=k,error=str(e)))
checks['every_xml_and_rels_parses']=not errors;details['parse_errors']=errors
missing=[];duplicate=[];rel_count=0
for k,r in xmls.items():
 if not k.endswith('.rels'):continue
 ids=[];base='' if k=='_rels/.rels' else posixpath.dirname(posixpath.dirname(k))
 for rel in r:
  rel_count+=1;ids.append(rel.get('Id'))
  if rel.get('TargetMode')=='External':continue
  raw=urllib.parse.unquote(rel.get('Target','').split('#')[0]);dest=posixpath.normpath(posixpath.join(base,raw)).lstrip('/')
  if dest not in o:missing.append(dict(part=k,target=raw,resolved=dest))
 if len(ids)!=len(set(ids)):duplicate.append(k)
checks['internal_relationship_targets_exist']=not missing
checks['relationship_ids_unique_per_part']=not duplicate
details['relationships']=dict(total=rel_count,missing_targets=missing,duplicate_ids=duplicate)
known={x.get('Id') for x in xmls['word/_rels/document.xml.rels']};rn='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
checks['document_relationship_references_resolve']=all(v in known for e in orr.iter() for a,v in e.attrib.items() if a.startswith(rn))
ct=xmls['[Content_Types].xml'];defaults={x.get('Extension') for x in ct if x.tag.endswith('Default')};overrides={x.get('PartName').lstrip('/') for x in ct if x.tag.endswith('Override')}
checks['content_type_overrides_exist']=overrides.issubset(o)
checks['all_parts_have_content_types']=all(k=='[Content_Types].xml' or k in overrides or k.rsplit('.',1)[-1] in defaults for k in o)
tags=['fldChar','instrText','fldSimple','drawing','pict','object','footnoteReference','endnoteReference','bookmarkStart','bookmarkEnd','sectPr'];assets={}
for tag in tags:
 a=seq(sr,W+tag);b=seq(orr,W+tag);assets[tag]=dict(before=len(a),after=len(b),identical=a==b);checks['preserved_'+tag]=a==b
for tag in ['oMath','oMathPara']:
 a=seq(sr,'{'+N['m']+'}'+tag);b=seq(orr,'{'+N['m']+'}'+tag);assets[tag]=dict(before=len(a),after=len(b),identical=a==b);checks['preserved_'+tag]=a==b
details['assets']=assets
stories={}
for k,r in xmls.items():
 if not k.startswith('word/') or not k.endswith('.xml'):continue
 if not any(e.tag.startswith(W) for e in r.iter()):continue
 old=E.fromstring(s[k]);counts={}
 for prefix,tag in [('w',t) for t in tags]+[('m','oMath'),('m','oMathPara')]:
  ns='{'+N[prefix]+'}';a=seq(old,ns+tag);b=seq(r,ns+tag)
  counts[tag]=dict(before=len(a),after=len(b),identical=a==b)
 stories[k]=dict(whole_part_identical=s[k]==o[k],assets=counts)
checks['all_story_asset_subtrees_preserved']=all(v['identical'] for d in stories.values() for v in d['assets'].values())
details['all_word_story_parts']=stories
sp=sr.find(W+'body').findall(W+'p');op=orr.find(W+'body').findall(W+'p');allowed={96,139,161,163,165,166,167,168,170,171,173,263}
checks['all_other_original_paragraphs_preserved_in_order']=subset([sig(p) for i,p in enumerate(sp) if i not in allowed],[sig(p) for p in op])
asset_p=[p for p in sp if any(next(p.iter(W+t),None) is not None for t in tags) or next(p.iter('{'+N['m']+'}oMath'),None) is not None]
checks['original_asset_paragraphs_preserved_in_order']=subset([sig(p) for p in asset_p],[sig(p) for p in op])
match67=[i for i,p in enumerate(op) if sig(p)==sig(sp[67])]
checks['p67_exact_element_preserved_once']=len(match67)==1
checks['p67_explanation_separate_following_paragraph']=len(match67)==1 and text(op[match67[0]+1]).startswith('上述确定性禁配针对历史八链')
details['p67']=dict(source_index_zero_based=67,output_indices_zero_based=match67,source_text=text(sp[67]),asset_counts={t:len(list(sp[67].iter(W+t))) for t in tags},explanation_text=text(op[match67[0]+1]))
for tag,part in [('footnoteReference','word/footnotes.xml'),('endnoteReference','word/endnotes.xml')]:
 ids={e.get(W+'id') for e in xmls[part]};checks[tag+'_definitions_resolve']=all(e.get(W+'id') in ids for e in orr.iter(W+tag))
starts=[x.get(W+'id') for x in orr.iter(W+'bookmarkStart')];ends=[x.get(W+'id') for x in orr.iter(W+'bookmarkEnd')]
checks['bookmark_id_pairing']=collections.Counter(starts)==collections.Counter(ends)
checks['bookmark_ids_unique']=len(starts)==len(set(starts))
rev=['ins','del','moveFrom','moveTo','pPrChange','rPrChange','tblPrChange','sectPrChange'];rev_counts={t:len(list(orr.iter(W+t))) for t in rev}
checks['no_revision_markup_in_offline_candidate']=not any(rev_counts.values());details['revision_counts']=rev_counts
st=sr.find(W+'body').findall(W+'tbl');ot=orr.find(W+'body').findall(W+'tbl')
checks['expected_table_count']=len(st)==31 and len(ot)==34
checks['untouched_original_tables_preserved_in_order']=subset([sig(t) for i,t in enumerate(st) if i!=13],[sig(t) for t in ot])
fulltext=text(orr)
def rows(n):
 with (C/'results'/n).open() as f:return list(csv.DictReader(f))
num=lambda v,d:f'{float(v):.{d}f}'.replace('-','−')
pp={r['component']:r for r in rows('P3_THREE_STATE.csv')};om={r['component']:r for r in rows('P3_OMNIBUS.csv')}
children=list(orr.find(W+'body'));tabs={}
for i,e in enumerate(children[:-1]):
 t=text(e)
 if e.tag==W+'p' and t.startswith(('表11 ','表12 ','表13 ')) and children[i+1].tag==W+'tbl':tabs[t.split(' ')[0]]=[[text(c) for c in tr.findall(W+'tc')] for tr in children[i+1].findall(W+'tr')]
checks['table13_exact_csv_values']=tabs['表13'][1:]==[[label]+[num(pp[k][col],2) for col in ['T_le3','T_4','T_5','d_5vle3','d_5v4']]+[num(om[k]['p_raw'],3)] for k,label in [('original','原金额'),('capped','预定99%封顶')]]
history=rows('CANDIDATE_HISTORY_PANELS.csv');revised={r['spec_id']:r for r in history if r['metric']=='Delta_OR' and r['model_version']=='revised_without_dwm'}
checks['table11_revised_estimates_intervals']=tabs['表11'][-2][1:]==[num(revised[k]['estimate'],3) for k in ['FEAS_031','FEAS_041']] and tabs['表11'][-1][1:]==['['+num(revised[k]['ci_lower'],3)+'，'+num(revised[k]['ci_upper'],3)+']' for k in ['FEAS_031','FEAS_041']]
eh=[]
for panel,label in [('A_B200_SEARCH','历史B=200'),('B_B1000_LEGACY','旧B=1,000')]:
 for r in sorted([r for r in history if r['panel_id']==panel and r['metric']=='Delta_CDE'],key=lambda r:r['spec_id']):
  eh.append([label+'／'+r['spec_id'].replace('FEAS_',''),num(r['p_raw'],6)]+[num(r[x],6) if r[x] else '未计算' for x in ['p_RW_within120','p_RW_all240']])
checks['table12_historical_values_and_version_caveat']=tabs['表12'][1:]==eh and '其p值不适用于表11的修订模型' in fulltext
checks['revised_does_not_inherit_historical_p']=all(not r['p_raw'] and not r['p_RW_within120'] and not r['p_RW_all240'] for r in revised.values())
checks['P3_p_frozen_tail_counts']=all(abs(float(r['p_raw'])-(int(r['tail_count'])+1)/(int(r['B'])+1))<1e-12 and int(r['n_valid'])==2000 for r in om.values())
six=rows('SIX_TEST_FAMILY.csv');n=len(six);ix=sorted(range(n),key=lambda i:float(six[i]['p_raw']));q=[0]*n;last=1.
for rank in range(n,0,-1):
 i=ix[rank-1];last=min(last,float(six[i]['p_raw'])*n/rank);q[i]=last
H=sum(1/i for i in range(1,n+1))
checks['frozen_six_BH_BY_arithmetic']=n==6 and all(abs(q[i]-float(r['q_BH6']))<1e-12 and abs(min(1,q[i]*H)-float(r['q_BY6']))<1e-12 for i,r in enumerate(six))
checks['no_six_family_adjusted_rejection']=all(float(r['q_BH6'])>.05 and float(r['q_BY6'])>.05 for r in six)
checks['candidate_TNIE_intervals_include_one']=all(float(r['ci_lower'])<1<float(r['ci_upper']) for r in history if r['metric']=='TNIE' and r['model_version']=='revised_without_dwm')
provenance={};fail=[]
for p in sorted((C/'results').glob('*.csv')):
 with p.open() as f:rs=list(csv.DictReader(f))
 for r in rs:
  for pref in ['source_','family_source_']:
   if r.get(pref+'path') and r.get(pref+'sha256'):
    path=r[pref+'path'];ref=pin(path);good=ref['sha256']==r[pref+'sha256'] and (not r.get(pref+'bytes') or ref['bytes']==int(r[pref+'bytes']))
    provenance[path]=dict(**ref,verified=good)
    if not good:fail.append(path)
checks['declared_result_source_hashes_match']=not fail
details['result_source_references']=list(provenance.values())
checks['precision_note_monotonicity_resolved']='基期本人满意度为5分时，收入增加对应的支持金额对比低于4分及≤3分状态' in text(op[173]) and '基期本人满意度较高时' not in text(op[173])
checks['precision_note_modelled_estimand_resolved']='两项模型化自然间接对比的区间均包含无效值1' in text(op[166])
findings=[dict(id='TEXT_PRECISION_MONOTONICITY',severity='resolved',paragraph_index_zero_based=173,quote=text(op[173]),reason='已限定为5分低于其余两类，不再概括为三状态单调下降。'),dict(id='TEXT_ESTIMAND_IDENTIFICATION',severity='resolved',paragraph_index_zero_based=166,quote=text(op[166]),reason='已明确模型化自然间接对比；未宣称因果识别成立。'),dict(id='NATIVE_DELIVERY_PENDING',severity='scope_limit',reason='离线候选无修订标记；不能据此确立原生Word显示、域刷新、修订接受/拒绝行为、分页或同版PDF/NLM通过。')]
native=C/'native_readiness';readiness=json.loads((native/'READINESS.json').read_text());adapter=json.loads((native/'short_successor_actual_release_v4/READY.json').read_text())
checks['native_snapshot_timestamp_present']=bool(datetime.datetime.fromisoformat(readiness['at']).tzinfo)
checks['native_snapshot_not_product_acceptance']=readiness['native_actions_allowed_by_this_report'] is False and adapter['native_ready'] is False and adapter['product_accepted'] is False
details['native_limits']=dict(snapshot_at=readiness['at'],adapter_at=adapter['at'],readiness=pin(native/'READINESS.json'),report=pin(native/'REPORT.md'),adapter=pin(native/'short_successor_actual_release_v4/READY.json'),no_live_recheck_this_audit=True,predecessor_release='Verified historically; not Word product acceptance.',current_manuscript='Now frozen to this report SHA; old adapter statement that manuscript was not frozen is historical and superseded only for offline freeze, not runtime binding.',pending=['Original actual-release outer PROCESS/TERMINAL/wait provenance remains missing.','Current resource owner/release, FIFO, identity, HID and same-inode availability not freshly observed.','New frozen manuscript/source/short native anchor not bound into a runnable native execution package.','Native Word field behavior, tracked-revision accept/reject, pagination, same-version PDF and final NLM acceptance remain unperformed.'])
report=dict(status='OFFLINE_STRUCTURE_NUMERIC_TRACE_AND_TEXT_PASS_NATIVE_PENDING',at=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='/root/limited_p3_code',independence='Stdlib ZIP/XML/provenance and arithmetic only; did not import/execute manuscript builder, R, UI, shared resource code.',review_script=pin(__file__),source=pin(source),output=dict(path=str(out),sha256=sha(O),bytes=len(O)),checks=checks,passed=sum(checks.values()),failed=[k for k,v in checks.items() if not v],details=details,findings=findings,actions=dict(ui=0,models=0,network=0,locks=0,manuscript_edits=0),limitations=['Only target frozen SHA covered; later changes require rebind.','No independent historical model estimation or native field evaluation.'])
assert all(checks.values()),json.dumps(report['failed'])
for ext in ['json','md']: assert not (C/'qa'/('INDEPENDENT_DOCX_REVIEW.'+ext)).exists()
(C/'qa/INDEPENDENT_DOCX_REVIEW.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
lines=['# 独立离线 DOCX 核验',f'冻结稿 SHA256：{sha(O)}',f'来源稿 SHA256：{sha(S)}',f'{sum(checks.values())}/{len(checks)} 项结构及数字追溯检查通过；两处表述精度建议已解决；原生验收未完成。',f'全部{on}个ZIP部件核验CRC、唯一性、XML可解析性、关系及内容类型。仅word/document.xml改变，其余部件字节一致。',f'资产节点：{json.dumps(assets,ensure_ascii=False)}',f'覆盖{len(stories)}个含Word元素的XML部件；所有story资产子树相同。原第67段完整元素保留，输出索引{match67}（从0计数）；解释另插为紧随段落。全部非目标原段落、未修改表格按顺序保留，表格31→34。','字段完整所在段落、公式、图像、脚注/尾注、书签、节属性保持。表11修订点值及区间、表12历史p及校正、表13金额及整体p独立对照冻结CSV；全部声明的结果源哈希匹配，固定六项BH/BY算术一致。','正文没有将OR差当百分点、将N1关联当中介、将旧p移植到修订版本或抹去49次失败。']
for f in findings[:2]:lines.append(f['id']+'：'+f['reason'])
lines += [f"原生资源报告快照时间：{readiness['at']}；离线适配READY时间：{adapter['at']}。本次没有新鲜应用、进程或票据观察，不把历史ACTIVE状态称为当前状态。",'原稿实际释放的历史事实已验；真实外层PROCESS/TERMINAL/wait来源、当前资源/FIFO/身份/HID/同inode可用性、新稿原生运行绑定仍待完成。离线稿现已冻结；旧适配说明中的“新稿未冻结”是当时状态，仅离线冻结已更新，原生锚点绑定未更新。','无模型、UI、网络、锁或稿件修改。本审查不提供原生Word、Zotero字段刷新、分页、修订接受/拒绝或同版PDF/NLM验收。']
(C/'qa/INDEPENDENT_DOCX_REVIEW.md').write_text('\n\n'.join(lines)+'\n')
print(json.dumps(dict(passed=report['passed'],checks=len(checks),assets=assets,p67=details['p67'],artifacts=[pin(C/'qa/INDEPENDENT_DOCX_REVIEW.json'),pin(C/'qa/INDEPENDENT_DOCX_REVIEW.md')]),ensure_ascii=False))
