#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""实际D3产物独立完整引文/书目和接受/拒绝态核验；仅写审阅文件。"""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as E
from copy import deepcopy
from datetime import datetime,timezone
import argparse,importlib.util,json
HERE=Path(__file__).resolve().parent
P=HERE.parent
parser=argparse.ArgumentParser()
parser.add_argument("--qa",type=Path,default=P/"actual_cumulative_closeout_20261007_v1/d3_patch_pagecache_successor/POST_MERGE_QA.json")
parser.add_argument("--out",type=Path,default=HERE)
parser.add_argument("--existing-main-audit",action="store_true")
args=parser.parse_args()
out=args.out
audit_script=P/"private_actual_field_semantics_audit_v1/audit_actual_fields_readonly.py"
sp=importlib.util.spec_from_file_location("independent_final_field_audit",audit_script)
a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
qa=json.loads(args.qa.read_text())
assert qa["status"]=="OFFLINE_PATCH_LINEAGE_PASS_NATIVE_PENDING"
refs={"mother":qa["mother"],"native":qa["native_saved"],**qa["outputs"]}
for ref in refs.values():assert a.pin(ref["path"])==ref
uri="http://zotero.org/users/9676737/items/HM4KAHLB"
if not args.existing_main_audit:
 code=a.run(argparse.Namespace(stage="mother_to_final_content",before=Path(refs["mother"]["path"]),after=Path(refs["content_patched"]["path"]),native_reference=Path(refs["native"]["path"]),wang_uri=uri,out=out))
 assert code==0
result=json.loads((out/"SEMANTIC_DELTA_REVIEW_NOT_APPROVED.json").read_text())
assert result["before"]==refs["mother"] and result["after"]==refs["content_patched"]
assert result["native_reference"]==refs["native"] and not result["blocking_violations"]
inv={k:a.inventory(ref["path"]) for k,ref in refs.items() if k!="tracked_patched"}
mother,content,clean,rejected,native=[inv[k] for k in ["mother","content_patched","accepted_offline","rejected_offline","native"]]
assert a.snapshot(content)==a.snapshot(clean)==a.snapshot(native)
assert a.snapshot(rejected)==a.snapshot(mother)
oldfields={f["csl"]["citationID"]:f for f in a.citations(mother)}
newfields={f["csl"]["citationID"]:f for f in a.citations(content)}
assert len(oldfields)==22 and len(newfields)==23
assert all(all(of[k]==newfields[cid][k] for k in ["kind","instruction","display","csl"]) for cid,of in oldfields.items())
assert a.bib_entries(content)[1:]==a.bib_entries(mother)
assert a.bib_entries(content)==a.bib_entries(clean)==a.bib_entries(native)
assert a.bib_entries(rejected)==a.bib_entries(mother)
def parts(ref):
 with ZipFile(ref["path"]) as z:return {n:z.read(n) for n in z.namelist()}
blobs={k:parts(v) for k,v in refs.items()}
# 独立结构比较：展开命名空间、属性排序；仅忽略完全空的pPr/rPr/trPr。
# 不删rsid、正文、控制元素、引用、关系、样式或非空格式属性，不对段落/子节点排序。
def structural(el):
 children=[structural(c) for c in el]
 if el.tag in {a.W+"pPr",a.W+"rPr",a.W+"trPr"} and not children and not el.attrib and not el.text:return None
 return (el.tag,tuple(sorted(el.attrib.items())),el.text or "",tuple(x for x in children if x is not None),el.tail or "")
def visible_tokens(root):
 # 与字段快照并用；合并Word随保存拆分的文字run，但保留段落/表/脚注边界与显式控件。
 tokens=[];buf=""
 def emit(kind,value):
  nonlocal buf
  if kind=="text":buf+=value;return
  if buf:tokens.append(("text",buf));buf=""
  tokens.append((kind,value))
 for el in root.iter():
  if el.tag in {a.W+x for x in ["p","tr","tc","footnote","endnote"]}:emit("structure",(el.tag,tuple(sorted(el.attrib.items())) if el.tag in {a.W+"footnote",a.W+"endnote"} else None))
  elif el.tag==a.W+"t":emit("text",el.text or "")
  elif el.tag in {a.W+x for x in ["tab","br","cr","footnoteReference","endnoteReference","footnoteRef","endnoteRef"]}:emit("control",(el.tag,tuple(sorted(el.attrib.items()))))
 if buf:tokens.append(("text",buf))
 return tokens
storysets={k:{n for n in b if a.STORY.fullmatch(n)} for k,b in blobs.items()}
assert all(v==storysets["mother"] for v in storysets.values())
stories=[]
for n in sorted(storysets["mother"]):
 roots={k:E.fromstring(b[n]) for k,b in blobs.items() if k!="tracked_patched"}
 ce=visible_tokens(roots["content_patched"])==visible_tokens(roots["accepted_offline"])
 re=structural(roots["mother"])==structural(roots["rejected_offline"])
 assert ce and re,n
 for k in ["mother","content_patched","accepted_offline","rejected_offline","native"]:
  assert not inv[k]["stories"][n]["tracked_elements"],(k,n)
 stories.append({"part":n,"content_clean_visible_semantics_equal":ce,"rejected_mother_structural_equal_ignoring_only_empty_property_containers":re})
assert len(stories)==9
protected={k:{n:b for n,b in v.items() if n.startswith(("word/media/","word/embeddings/"))} for k,v in blobs.items()}
assert all(v==protected["mother"] for v in protected.values())
# D3内容稿只修改document.xml，其他包成员逐字节继承真实原生保存源。
assert set(blobs["native"])==set(blobs["content_patched"])
non_doc_equal=all(v==blobs["content_patched"][n] for n,v in blobs["native"].items() if n!="word/document.xml")
assert non_doc_equal
def txt(p):return "".join(t.text or "" for t in p.iter(a.W+"t"))
def document(label):return E.fromstring(blobs[label]["word/document.xml"])
wanted="王跃生（2026）根据2020年人口普查资料报告，城镇、乡村直系家庭占比分别为13.89%和21.48%；"
wang={}
for label in ["content_patched","accepted_offline","native"]:
 ps=[txt(p) for p in document(label).iter(a.W+"p") if txt(p).startswith("王跃生（2026）")]
 assert ps==[wanted],(label,ps)
 wang[label]=ps[0]
# 原21项范围的实际完成值：只核已批准的before/after合同，不生成新审批。
plan=json.loads(Path(qa["plan"]["path"]).read_text());assert a.pin(qa["plan"]["path"])==qa["plan"]
def locate(root,loc):
 body=root.find(a.W+"body")
 if loc["kind"]=="body_paragraph":return body.findall(a.W+"p")[loc["p"]-1]
 return body.findall(a.W+"tbl")[loc["t"]-1].findall(a.W+"tr")[loc["r"]-1].findall(a.W+"tc")[loc["c"]-1].findall(a.W+"p")[loc["p"]-1]
def sty(p):
 el=p.find(a.W+"pPr/"+a.W+"pStyle")
 return el.get(a.W+"val") if el is not None else None
for t in plan["targets"]:
 for label in ["content_patched","accepted_offline"]:
  el=locate(document(label),t["locator"]);assert txt(el)==t["after"] and sty(el)==t["after_style"],(label,t["locator"])
# 真实最终内容稿删去旧书目段文本的内存负控；不改任何DOCX。
removed="郑丹丹, 狄金华, 2017. 女性家庭权力、夫妻关系与家庭代际资源分配[J]. 社会学研究, 32(1): 171-192+245."
negroot=document("content_patched")
matches=[p for p in negroot.iter(a.W+"p") if txt(p)==removed]
assert len(matches)==1
for t in matches[0].iter(a.W+"t"):t.text=""
negative=deepcopy(content);negative["stories"]["word/document.xml"]=a.parse_story(E.tostring(negroot),"word/document.xml")
nr=a.compare(mother,negative,uri)
assert "old_bibliography_entries_preserved_normalized" in nr["blocking_violations"]
assert nr["bibliography_removed_normalized"]=={a.compact(removed):1}
assert nr["citation_field_count"]==result["citation_field_count"] and nr["citation_member_count"]==result["citation_member_count"]
# 可见年份负控：保留所有域快照，另造重复静态年份，整段断言必须识别。
duproot=document("content_patched")
p=[p for p in duproot.iter(a.W+"p") if txt(p)==wanted][0]
texts=list(p.iter(a.W+"t"));first=texts[0];first.text=(first.text or "")+"（2026）"
duplicate_visible=txt(p)
assert duplicate_visible!=wanted
negative2=deepcopy(content);negative2["stories"]["word/document.xml"]=a.parse_story(E.tostring(duproot),"word/document.xml")
assert a.snapshot(negative2)==a.snapshot(content)
# 底层真实输入再次核哈希。
for ref in refs.values():assert a.pin(ref["path"])==ref
data={"schema":"INDEPENDENT_FINAL_FIELD_REVIEW_V1","status":"INDEPENDENT_OFFLINE_SEMANTICS_CLEAR_NATIVE_PENDING","not_an_approval":True,
 "at":datetime.now(timezone.utc).isoformat(),"script":a.pin(__file__),"extractor":a.pin(audit_script),"actual_post_merge_qa":a.pin(args.qa),"sources":refs,
 "checks":{"all_22_old_citation_instructions_displays_csl_exact":True,
 "all_24_old_bibliography_entries_exact_in_order":True,"only_wang_citation_and_bibliography_added":True,
 "content_clean_native_all_field_snapshots_exact":True,"rejected_mother_all_field_snapshots_exact":True,
 "content_clean_native_bibliography_exact":True,"rejected_mother_bibliography_exact":True,
 "whole_visible_wang_paragraph_exact_single_year":True,"no_tracking_in_content_clean_rejected":True,
 "all_21_approved_targets_exact_in_content_and_clean":True,
 "native_to_content_non_document_parts_byte_equal":non_doc_equal,"media_and_embeddings_preserved":True},
 "counts":{"citation_fields":result["citation_field_count"],"members":result["citation_member_count"],"unique_uris":result["unique_uri_count"],"bibliography_entries":result["bibliography_paragraph_count"]},
 "stories":stories,"whole_wang_paragraph":wanted,
 "negative_controls":{"bibliography_removal":{"in_memory_only":True,"removed_text":removed,"removed_characters":len(removed),"blocked":True,"blocking_violations":nr["blocking_violations"],"citation_counts_and_members_unchanged":True},
 "static_duplicate_year":{"in_memory_only":True,"all_field_snapshots_unchanged":True,"whole_paragraph_comparison_blocks":True,"negative_visible_text":duplicate_visible}},
 "non_story_changed_from_mother":result["non_story_changed_pending_review"],
 "boundaries":["No model execution or modification","No Word UI/native call","No DOCX write","No approval generated","Native formatting, PDF, Word accept/reject and readonly reopen remain separate requirements"]}
def writej(name,obj):
 with (out/name).open("x") as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write("\n")
writej("INDEPENDENT_FINAL_REVIEW.json",data)
# 公共摘要不包含本机绝对路径、用户名、broker票据或会话信息。
public={"status":"离线引文、书目及接受/拒绝态核验完成；原生Word验收待另行完成",
 "scope":"CMAverse论文实际D3整合产物的文件级独立复核；不重新估计模型",
 "artifact_sha256":{k:refs[k]["sha256"] for k in ["mother","content_patched","tracked_patched","accepted_offline","rejected_offline"]},
 "counts":data["counts"],"findings":["母稿原22个引文域的完整代码、显示和CSL成员逐项保留，仅新增王跃生（2026）引文。",
 "原24条参考文献文字及顺序完整保留，新增1条后共25条。",
 "最终内容稿、接受修订稿与真实原生保存稿的全部字段快照一致。",
 "拒绝修订稿全部字段和书目回到母稿；9个正文/注释/页眉页脚部件结构一致，仅忽略完全空的属性容器。",
 "既定21项文字/标题样式修订均在内容稿和接受稿核实。",
 "内存删去一条旧书目的反例虽不改变引文域和成员数，仍被完整书目检查阻断；重复静态年份反例被整段文字检查阻断。"],
 "limitations":"这是离线文件核验，不能替代Word原生布局、接受/拒绝、只读重开和PDF验收，也不构成统计结果的新确认。"}
writej("PUBLIC_SUMMARY.json",public)
report="# 最终内容稿独立完整引文、书目与接受/拒绝态核验\n\n"
report+="状态：INDEPENDENT_OFFLINE_SEMANTICS_CLEAR_NATIVE_PENDING。无离线语义阻断；不是批准，不宣称原生验收完成。\n\n"
report+="## 核验结论\n\n"
for s in public["findings"]:report+="- "+s+"\n"
report+="\n## 核验范围与证据\n\n"
for k,ref in refs.items():report+=f"- {k}: {ref['path']}\n  SHA256: {ref['sha256']}；{ref['bytes']} bytes。\n"
report+="\n字段检查使用原完整语义审计器，另逐项核全部22旧域代码/显示/CSL、24原书目文字及顺序。接受稿与内容稿的可见文字结构及全部字段一致。拒绝稿采用独立展开命名空间树比较，仅忽略完全空pPr/rPr/trPr；保留非空属性、文字、控制、引用、关系和所有子节点顺序。\n\n"
report+="书目负控在最终内容稿内存副本删除郑丹丹/狄金华2017书目67字，域和成员数维持不变，旧书目保全检查正确阻断。重复年份负控也不改变任何字段快照，由整段可见文字比较正确阻断。未生成负控DOCX。\n\n"
report+="## 尚待原生核验\n\n"
report+="母稿到内容稿的非story差异： "+", ".join(data["non_story_changed_from_mother"])+"。实际D3内容稿除document.xml外全部包成员逐字节继承已核真实原生源。本报告不将这些元数据/样式差异自动批准；最终原生布局、PDF和只读重开由root另行执行。\n\n"
report+="未重跑模型、未调用Word UI、未写任何DOCX、未生成批准。完整计数、源SHA、9个story检查和反例结果见INDEPENDENT_FINAL_REVIEW.json；可公开摘要见PUBLIC_SUMMARY.md与PUBLIC_SUMMARY.json。\n"
with (out/"INDEPENDENT_FINAL_REVIEW.md").open("x") as f:f.write(report)
with (out/"PUBLIC_SUMMARY.md").open("x") as f:
 f.write("# CMAverse论文引文与修订文件核验说明\n\n")
 f.write(public["status"]+"。\n\n")
 for s in public["findings"]:f.write("- "+s+"\n")
 f.write("\n"+public["limitations"]+"\n")
pins=[a.pin(out/n) for n in ["INDEPENDENT_FINAL_REVIEW.json","INDEPENDENT_FINAL_REVIEW.md","PUBLIC_SUMMARY.md","PUBLIC_SUMMARY.json","SEMANTIC_DELTA_REVIEW_NOT_APPROVED.json","BEFORE_FIELD_INVENTORY.json","AFTER_FIELD_INVENTORY.json"]]+[a.pin(__file__),a.pin(audit_script)]
writej("DELIVERY_PINS.json",{"status":data["status"],"pins":pins,"sources":refs})
print(json.dumps({"status":data["status"],"report":a.pin(out/"INDEPENDENT_FINAL_REVIEW.md"),"review":a.pin(out/"INDEPENDENT_FINAL_REVIEW.json"),"public":a.pin(out/"PUBLIC_SUMMARY.md"),"delivery":a.pin(out/"DELIVERY_PINS.json")},ensure_ascii=False))
