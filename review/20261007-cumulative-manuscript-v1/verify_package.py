#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""解压后可在其他机器只读运行；不执行R、Word、网络或生成原稿。"""
import sys, json, hashlib, zipfile, importlib.util
from pathlib import Path
from xml.etree import ElementTree as E
from copy import deepcopy
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
def digest(b):return hashlib.sha256(b).hexdigest()
manifest=json.loads((ROOT/"MANIFEST.json").read_text())
assert manifest["count"]==len(manifest["files"])
names=[r["path"] for r in manifest["files"]];assert len(names)==len(set(names))
for row in manifest["files"]:
    path=(ROOT/row["path"]).resolve()
    assert path.is_relative_to(ROOT)
    b=path.read_bytes()
    assert len(b)==row["bytes"] and digest(b)==row["sha256"],row["path"]
mapping=json.loads((ROOT/"SOURCE_MAP.json").read_text())
for row in mapping["sources"]:
    b=(ROOT/row["package_path"]).read_bytes()
    assert len(b)==row["bytes"] and digest(b)==row["sha256"]
spec=importlib.util.spec_from_file_location("frozen_readonly_extractor",ROOT/"audit/audit_actual_fields_readonly.py")
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
paths={k:ROOT/v for k,v in mapping["documents"].items()}
inv={k:a.inventory(v) for k,v in paths.items() if k!="tracked_patched"}
m,c,n,acc,rej=[inv[k] for k in ("mother","content_patched","native","accepted_offline","rejected_offline")]
assert a.snapshot(c)==a.snapshot(n)==a.snapshot(acc)
assert a.snapshot(m)==a.snapshot(rej)
old={f["csl"]["citationID"]:f for f in a.citations(m)}
new={f["csl"]["citationID"]:f for f in a.citations(c)}
assert len(old)==22 and len(new)==23
assert all(all(of[k]==new[cid][k] for k in ("kind","instruction","display","csl")) for cid,of in old.items())
assert a.bib_entries(c)[1:]==a.bib_entries(m)
assert len(a.bib_entries(m))==24 and len(a.bib_entries(c))==25
assert a.bib_entries(c)==a.bib_entries(n)==a.bib_entries(acc)
assert a.bib_entries(m)==a.bib_entries(rej)
blobs={}
for label,path in paths.items():
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        blobs[label]={name:z.read(name) for name in z.namelist()}
def structural(el):
    children=[structural(ch) for ch in el]
    if el.tag in {a.W+x for x in ("pPr","rPr","trPr")} and not children and not el.attrib and not el.text:return None
    return(el.tag,tuple(sorted(el.attrib.items())),el.text or "",tuple(x for x in children if x is not None),el.tail or "")
def tokens(root):
    result=[];buf=""
    def emit(kind,value):
        nonlocal buf
        if kind=="text":buf+=value;return
        if buf:result.append(("text",buf));buf=""
        result.append((kind,value))
    for el in root.iter():
        if el.tag in {a.W+x for x in ("p","tr","tc","footnote","endnote")}:
            emit("structure",(el.tag,tuple(sorted(el.attrib.items())) if el.tag in (a.W+"footnote",a.W+"endnote") else None))
        elif el.tag==a.W+"t":emit("text",el.text or "")
        elif el.tag in {a.W+x for x in ("tab","br","cr","footnoteReference","endnoteReference","footnoteRef","endnoteRef")}:
            emit("control",(el.tag,tuple(sorted(el.attrib.items()))))
    if buf:result.append(("text",buf))
    return result
stories={k:{name for name in v if a.STORY.fullmatch(name)} for k,v in blobs.items()}
assert all(s==stories["mother"] for s in stories.values()) and len(stories["mother"])==9
for name in sorted(stories["mother"]):
    roots={k:E.fromstring(v[name]) for k,v in blobs.items() if k!="tracked_patched"}
    assert structural(roots["mother"])==structural(roots["rejected_offline"]),name
    assert tokens(roots["content_patched"])==tokens(roots["accepted_offline"]),name
    assert all(not v["stories"][name]["tracked_elements"] for v in inv.values()),name
media={k:{name:b for name,b in v.items() if name.startswith(("word/media/","word/embeddings/"))} for k,v in blobs.items()}
assert all(v==media["mother"] for v in media.values())
assert set(blobs["native"])==set(blobs["content_patched"])
assert all(b==blobs["content_patched"][name] for name,b in blobs["native"].items() if name!="word/document.xml")
def text(el):return "".join(t.text or "" for t in el.iter(a.W+"t"))
def doc(k):return E.fromstring(blobs[k]["word/document.xml"])
plan=json.loads((ROOT/"lineage/C1_EXACT_PLAN_APPROVED.json").read_text())
assert len(plan["targets"])==21
def locate(root,loc):
    body=root.find(a.W+"body")
    if loc["kind"]=="body_paragraph":return body.findall(a.W+"p")[loc["p"]-1]
    return body.findall(a.W+"tbl")[loc["t"]-1].findall(a.W+"tr")[loc["r"]-1].findall(a.W+"tc")[loc["c"]-1].findall(a.W+"p")[loc["p"]-1]
for target in plan["targets"]:
    for label in ("content_patched","accepted_offline"):
        el=locate(doc(label),target["locator"])
        st=el.find(a.W+"pPr/"+a.W+"pStyle")
        assert text(el)==target["after"]
        assert (st.get(a.W+"val") if st is not None else None)==target["after_style"]
wanted="王跃生（2026）根据2020年人口普查资料报告，城镇、乡村直系家庭占比分别为13.89%和21.48%；"
for label in ("content_patched","accepted_offline","native"):
    assert [text(p) for p in doc(label).iter(a.W+"p") if text(p).startswith("王跃生（2026）")]==[wanted]
# 反例在内存构造，不写任何Word文件。
removed="郑丹丹, 狄金华, 2017. 女性家庭权力、夫妻关系与家庭代际资源分配[J]. 社会学研究, 32(1): 171-192+245."
root=doc("content_patched");ps=[p for p in root.iter(a.W+"p") if text(p)==removed];assert len(ps)==1
for el in ps[0].iter(a.W+"t"):el.text=""
negative=deepcopy(c);negative["stories"]["word/document.xml"]=a.parse_story(E.tostring(root),"word/document.xml")
nr=a.compare(m,negative,"http://zotero.org/users/9676737/items/HM4KAHLB")
assert "old_bibliography_entries_preserved_normalized" in nr["blocking_violations"]
dup=doc("content_patched");p=[p for p in dup.iter(a.W+"p") if text(p)==wanted][0]
first=next(p.iter(a.W+"t"));first.text=(first.text or "")+"（2026）"
assert text(p)!=wanted
neg2=deepcopy(c);neg2["stories"]["word/document.xml"]=a.parse_story(E.tostring(dup),"word/document.xml")
assert a.snapshot(neg2)==a.snapshot(c)
print(json.dumps({"status":"PASS_OFFLINE_PACKAGE_AND_DOCUMENT_SEMANTICS","manifest_files":len(names),
 "source_pins":len(mapping["sources"]),"citation_fields_before":22,"citation_fields_after":23,
 "bibliography_before":24,"bibliography_after":25,"stories":9,"approved_targets":21,
 "negative_controls":2,"native_validation":"PENDING","models_executed":0},ensure_ascii=False))

