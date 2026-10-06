#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""仅构建累计离线审阅包；不执行模型、Word或历史生成脚本。"""
from pathlib import Path
import csv, hashlib, json, shutil, zipfile, re, sys
from datetime import datetime, timezone
from xml.etree import ElementTree as E
HERE=Path(__file__).resolve().parent
P=HERE.parent
A=P/"actual_cumulative_closeout_20261007_v1"
PAY=HERE/"payload"
assert not PAY.exists(), "输出已存在，禁止覆盖已冻结交付"
PAY.mkdir(parents=True)
sources=[]
def sha(b): return hashlib.sha256(b).hexdigest()
def write(rel,b):
    if isinstance(b,str): b=b.encode()
    f=PAY/rel; f.parent.mkdir(parents=True,exist_ok=True); f.write_bytes(b)
def js(rel,v): write(rel,json.dumps(v,ensure_ascii=False,indent=2)+"\n")
def take(path,rel,expected=None):
    path=Path(path); b=path.read_bytes()
    if expected:
        assert len(b)==expected["bytes"] and sha(b)==expected["sha256"],str(path)
    write(rel,b)
    sources.append({"source":str(path),"package_path":rel,"bytes":len(b),"sha256":sha(b)})
audit_dir=P/"private_final_content_field_audit_20261007_v1"
audit=json.loads((audit_dir/"INDEPENDENT_FINAL_REVIEW.json").read_text())
docmap={}
for key,ref in audit["sources"].items():
    rel=("manuscript/" if key not in ("mother","native") else "predecessors/")+key+".docx"
    take(ref["path"],rel,ref); docmap[key]=rel
for name in ["tracked.docx","accepted_offline.docx","rejected_offline.docx"]:
    take(A/"d2_merge_prooferr_successor"/name,"predecessors/d2_"+name)
take(P/"manuscript/CMAverse_论文收尾合入_离线候选_原生验收待完成.docx","predecessors/pre_citation.docx")
take(P/"native_cumulative_v1/CMAverse_论文收尾累计修订_离线候选_原生验收待完成.docx","predecessors/cumulative_before_citation.docx")
for f in sorted((P/"results").glob("*.csv")):take(f,"results/"+f.name)
assert len(list((PAY/"results").glob("*.csv")))==9
for f in sorted((P/"delivery/review_payload/bindings").iterdir()):
    if f.is_file():take(f,"bindings/"+f.name)
for f in sorted((P/"delivery/review_payload/theory").iterdir()):
    if f.is_file():take(f,"theory/"+f.name)
for f in sorted(audit_dir.iterdir()):
    if f.is_file() and f.suffix in (".json",".md",".diff",".py"):take(f,"audit/"+f.name)
take(P/"private_actual_field_semantics_audit_v1/audit_actual_fields_readonly.py","audit/audit_actual_fields_readonly.py")
for name in ["FINAL_FIELD_DELTA_REVIEW_v1.json","FINAL_FIELD_DELTA_APPROVAL_v1.json",
             "FINAL_ALL_STORY_LINEAGE_REVIEW_v1.json","FINAL_DRAFT_GENERATION_RECEIPT.json",
             "NON_STORY_DELTAS_READONLY.json","MERGE_SCOPE_PROOFERR_SUCCESSOR_APPROVED.json",
             "ROOT_PAGECACHE_SUCCESSOR_REVIEW.json"]:
    take(A/name,"lineage/"+name)
for sub,name in [("d2_merge_prooferr_successor","MERGE_QA.json"),
                 ("d3_patch_pagecache_successor","POST_MERGE_QA.json"),
                 ("final_lineage_pagecache_v1","LINEAGE_REVIEW_DRAFT.json"),
                 ("final_lineage_pagecache_v1","SCHEMA_VALIDATION.json"),
                 ("final_native_drafts_reviewed_v1","GENERATION_RECEIPT.json"),
                 ("final_native_drafts_reviewed_v1","FIELD_REVIEW_VALIDATION.json"),
                 ("final_native_drafts_reviewed_v1","LINEAGE_REVIEW_VALIDATION.json")]:
    take(A/sub/name,"lineage/"+name)
plan=P/"post_merge_narrative_successor_preparation_v3/C1_EXACT_PLAN_APPROVED.json"
assert sha(plan.read_bytes())=="d3c9bfbc45f20576e56364d972a4c951d4e2166ed680c759cb1af71964219686"
take(plan,"lineage/C1_EXACT_PLAN_APPROVED.json")
for sub in ["claude_narrative_review_20261007","claude_native_review_20261007","claude_publication_review_20261007"]:
    take(P/sub/"executor-report.md","reviews/"+sub+".md")
take(P/"review/ROOT_CURRENT_ADJUDICATION_20261007_v2.md","REPORT.md")
for name in ["CLAUDE_ROOT_ADJUDICATION_20261007.md","CLAUDE_NATIVE_ROOT_ADJUDICATION_20261007.md"]:
    take(P/"review"/name,"reviews/historical_"+name)
# 审阅脚本只归档，不导入会触发合稿/模型的历史脚本。
take(__file__,"code/build_increment.py")
take(HERE/"verify_package.py","verify_package.py")
js("SOURCE_MAP.json",{"sources":sources,"documents":docmap,"notes":"source是本机原始绝对路径；package_path用于跨环境复核。未重新拟合模型。"})
# 即时前驱和关键来源完整包部件差异，补足网页版来源核验。
diff=[]
def zparts(rel):
    with zipfile.ZipFile(PAY/rel) as z:
        assert z.testzip() is None
        return {n:z.read(n) for n in z.namelist()}
pairs=[("d2_accepted_to_content","predecessors/d2_accepted_offline.docx",docmap["content_patched"]),
       ("d2_tracked_to_tracked","predecessors/d2_tracked.docx",docmap["tracked_patched"]),
       ("native_to_content",docmap["native"],docmap["content_patched"]),
       ("mother_to_rejected",docmap["mother"],docmap["rejected_offline"])]
for label,old,new in pairs:
    x,y=zparts(old),zparts(new)
    for part in sorted(set(x)|set(y)):
        bx,by=x.get(part),y.get(part)
        diff.append({"comparison":label,"part":part,"same_bytes":bx==by,
                     "before_bytes":len(bx) if bx is not None else None,
                     "after_bytes":len(by) if by is not None else None,
                     "before_sha256":sha(bx) if bx is not None else None,
                     "after_sha256":sha(by) if by is not None else None})
with (PAY/"lineage/DOCX_PART_DIFF.csv").open("w") as f:
    w=csv.DictWriter(f,fieldnames=list(diff[0]));w.writeheader();w.writerows(diff)
# 原内容稿逐块导出，包含表格、脚注、公式文本；不是版面或动态域的替代品。
W="{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M="{http://schemas.openxmlformats.org/officeDocument/2006/math}"
parts=zparts(docmap["content_patched"])
def visible(el):
    texts=[]
    for t in el.iter():
        if t.tag in (W+"t",M+"t"):texts.append(t.text or "")
        elif t.tag==W+"tab":texts.append(" ")
        elif t.tag in (W+"br",W+"cr"):texts.append("\n")
    return "".join(texts)
lines=["# 累计离线内容稿全文（2026-10-07）","",
       "来源 content_patched.docx；SHA256："+sha((PAY/docmap["content_patched"]).read_bytes()),
       "本文件按DOCX实际块顺序导出正文、表格与注释。公式为文本投影，图像另附。不是原生PDF或版式验收。",""]
counts={"body_paragraphs":0,"physical_tables":0,"footnotes":0,"endnotes":0,"images":0}
body=E.fromstring(parts["word/document.xml"]).find(W+"body")
for node in body:
    if node.tag==W+"p":
        counts["body_paragraphs"]+=1
        s=visible(node)
        if s:lines += [s,""]
    elif node.tag==W+"tbl":
        counts["physical_tables"]+=1
        lines += [f"【DOCX实体表 {counts['physical_tables']}；非论文题注编号】",""]
        rows=[]
        for row in node.findall(W+"tr"):
            rows.append([visible(c).replace("|","\\|").replace("\n","<br>") for c in row.findall(W+"tc")])
        if rows:
            n=max(map(len,rows))
            rows=[r+[""]*(n-len(r)) for r in rows]
            lines += ["| "+" | ".join(rows[0])+" |","| "+" | ".join(["---"]*n)+" |"]
            lines += ["| "+" | ".join(r)+" |" for r in rows[1:]]
            lines += [""]
for part,tag,label in [("word/footnotes.xml","footnote","脚注"),("word/endnotes.xml","endnote","尾注")]:
    if part not in parts:continue
    lines += ["## "+label,""]
    for node in E.fromstring(parts[part]).findall(W+tag):
        ident=int(node.get(W+"id"))
        if ident<1:continue
        counts[tag+"s"]+=1
        lines += [f"{label}{ident}："+visible(node),""]
for part,b in parts.items():
    if part.startswith("word/media/"):
        write("manuscript/images/"+Path(part).name,b);counts["images"]+=1
write("MANUSCRIPT_TEXT.md","\n".join(lines))
js("manuscript/TEXT_EXTRACTION.json",{"source_sha256":sha((PAY/docmap["content_patched"]).read_bytes()),"counts":counts,"status":"TEXT_EXPORT_ONLY_NATIVE_LAYOUT_PENDING"})
# 三组在线证据表均从冻结CSV读取，未生成新的推断值。
tablelines=["# 冻结证据表","", "下列值直接来自本轮继承的九张CSV。OR差、概率差及元/月单位不可互换；历史p与去dwm后估计分版报告。",""]
for file in sorted((PAY/"results").glob("*.csv")):
    rows=list(csv.reader(file.open()))
    tablelines += ["## "+file.name,""]
    tablelines += ["| "+" | ".join(c.replace("|","\\|") for c in rows[0])+" |","| "+" | ".join(["---"]*len(rows[0]))+" |"]
    tablelines += ["| "+" | ".join(c.replace("|","\\|").replace("\n","<br>") for c in r)+" |" for r in rows[1:]]
    tablelines += [""]
write("EVIDENCE_TABLES.md","\n".join(tablelines))
feedback="""# 给 ChatGPT Pro / Claude 网页端：累计稿增量复核说明

本次提交的是“筛选显著性”的论文累计改文及来源补齐，不是新增统计分析。上一轮数值收尾已接受，所有模型、bootstrap及规格网格保持冻结。

## 已完成与共识

1. FEAS_031为重点探索性修饰候选，041为相关操作化支持。去dwm后ΔOR分别为−0.409351、−0.085496，未调整区间不含零；本版本没有新的p。历史B200的120项校正p分别为0.134328、0.631841；240目标校正分别为0.542289、0.915423。各版本分栏保留，不拼接。
2. P3原金额和固定99%封顶各2000/2000有效，整体p为0.131934和0.079960。49次原数值失败已经修复。N1是辅助关联，最终六项家族没有BH/BY 5%拒绝。
3. 本批未找到经历史搜索核查支持的确认性机制。停止本批计算，转入准确的探索性论述；不扩大组合、不增B、不另挑检验族。
4. 表10、旧R6辅助显著与最终整体结果、P3已修复状态、六项表标题及尺度说明已改。继上轮离线稿，本次再落实21项批准改动：8处正文、8个表格单元、5项标题样式。
5. 王跃生（2026）引文和书目已真实经过Word/Zotero刷新保存，并合入累计稿；这不代表之后的累计稿已完成原生接受/拒绝。
6. 三份Claude审阅已经完成。旧D2程序存在“域内删除旧书目可被放行”的缺口，本次未修改冻结旧程序；实际产物通过另一套完整保全核验及删除反例。不得把这两种状态混为一谈。

## 本次可独立核验的材料

- manuscript/content_patched.docx：累计内容稿，便于直接阅读。
- manuscript/tracked_patched.docx：累计修订稿。
- manuscript/accepted_offline.docx 与 rejected_offline.docx：离线接受/拒绝投影，均未冒称原生Word验收。
- predecessors/：母稿、真实原生引文来源、D2即时前驱和引用更新前稿。提供全文原件与DOCX逐部件差异，关闭此前即时前驱缺口。
- SOURCE_MAP.json：原始绝对路径、包内路径、大小及SHA的映射。
- bindings/EXECUTION_INPUTS_120.csv/.json：120项执行输入只读绑定日志。大型执行RDS不重复上传，日志沿用已保存本机核验，本次未重读120个大对象。
- results/：9张冻结结果CSV；EVIDENCE_TABLES.md供在线直接读取。
- audit/、lineage/：完整域及书目核验、9个story检查、21项目标、部件差异与原生准备状态。
- theory/：有限原文锚点矩阵。不是新系统综述，不把资源协商解释写成已测量机制。
- reviews/：三份Claude原报告及历史裁定；当前结论以REPORT.md为准，原报告的早期状态不覆盖后继事实。
- MANUSCRIPT_TEXT.md：实际累计内容稿全文、表格、注释文本导出；图片另附，不代替PDF排版。
- verify_package.py：跨环境只读核验包内哈希、引文保全、目标修改和反例。仅Python标准库，不调用R、Word或网络。

## 解释上的两处澄清

“71.65%本人评分未提高”不能直接改成“71.65%只有配偶下降”；28.35%本人提高与88.01%配偶下降可重叠。
本批停止搜索，不等于证明未来任何三期研究问题必不显著；极端金额与收入的比值也不足以直接断定填报错误。

## 请网页端本轮重点复核

请先读取README、REPORT、EVIDENCE_TABLES和MANUSCRIPT_TEXT；需要原件时解压本次ZIP并执行只读核验。重点检查表10是否覆盖全稿、正文/讨论是否同步最终P3、OR尺度与证据版本是否清晰、理论解释是否超出变量测量、引文及即时前驱是否可绑定。无需重跑统计或再次索取旧11包/N1原件。

## 尚未完成

累计稿的原生Word接受/拒绝、原生保存重开后的字段/版式核验、Word导出最终PDF、最终同一PDF的NLM终审仍待完成。当前包无新最终PDF，也无伪造的READY或终审通过回执。

原因是共享Word/Zotero旧任务租约已过期，需真实空闲后归还并接续；最后原生观察含另一份未保存文稿，本次未重新观察或触碰其修改。资料已具备内容复核条件，不能因此写成论文最终交付已全部通过。

本次仅新增交付整理自检，标记solo_self_review；三份Claude原审阅按原范围引用。
"""
write("WEB_FEEDBACK.md",feedback)
write("README.md","""# CMAverse 累计论文修改与核验证据（2026-10-07）

状态：离线累计稿及来源核验已完成，可进行网页版内容复核；最终原生Word/PDF/同版NLM待完成。
统计冻结，无新模型或p值。当前裁定见REPORT.md；可转发说明见WEB_FEEDBACK.md。

阅读顺序：WEB_FEEDBACK.md → REPORT.md → EVIDENCE_TABLES.md → MANUSCRIPT_TEXT.md → 本次ZIP中的稿件原件和audit/lineage证据。
本目录全部payload文件同包提供；哈希清单MANIFEST.json明确排除自身。SOURCE_MAP将本机原件映射到包内路径。
一个ZIP；构建脚本实测小于25,000,000字节才允许发布。不要与旧包同名覆盖解压。

解压后执行：python3 verify_package.py
该脚本只读校验，不运行原R脚本或任何native任务。code和audit中原审阅脚本仅供溯源；其中历史绝对路径保留，便携入口才用于其他机器。

本包提供母稿、即时前驱和逐部件差异，以及120项执行输入日志；不再次上传微观数据或大型RDS。既有统计包保持原位。
不提供最新PDF的原因和后续验收范围见WEB_FEEDBACK.md。历史原生引文来源成功不能替代累计稿原生终验。
""")
# 输出强凭证特征检查，只记录命中位置，不打印内容。
hits=[]
patterns=[rb"gh[pousr]_[A-Za-z0-9]{25,}",rb"github_pat_[A-Za-z0-9_]{30,}",rb"sk-[A-Za-z0-9_-]{25,}",rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"]
for f in PAY.rglob("*"):
    if f.is_file() and f.suffix in (".json",".md",".py",".csv",".diff"):
        if any(re.search(p,f.read_bytes()) for p in patterns):hits.append(str(f.relative_to(PAY)))
assert not hits, "检测到需核实的凭证特征："+repr(hits)
js("PUBLICATION_SCOPE.json",{"at":datetime.now(timezone.utc).isoformat(),
 "status":"OFFLINE_CUMULATIVE_REVIEW_READY_NATIVE_PENDING","review_mode":"solo_self_review",
 "model_calls":0,"native_calls":0,"source_files_copied":len(sources),
 "credential_pattern_hits":hits,"native_ready":False,"final_pdf_present":False,"final_nlm_review":False,
 "prior_logs_not_reexecuted":["120 execution_inputs","statistical models","D2/D3 generators"]})
manifest=[]
for f in sorted(PAY.rglob("*")):
    if f.is_file():manifest.append({"path":str(f.relative_to(PAY)),"bytes":f.stat().st_size,"sha256":sha(f.read_bytes())})
js("MANIFEST.json",{"schema":"CMA_CUMULATIVE_REVIEW_MANIFEST_V1","excludes":["MANIFEST.json"],
                   "count":len(manifest),"files":manifest})
archive=HERE/"cumulative_review_part01.zip"
with zipfile.ZipFile(archive,"x",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for f in sorted(PAY.rglob("*")):
        if f.is_file():z.write(f,str(f.relative_to(PAY)))
assert archive.stat().st_size<25000000
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(manifest)+1
    for row in manifest:
        b=z.read(row["path"]);assert len(b)==row["bytes"] and sha(b)==row["sha256"]
receipt={"archive":str(archive),"bytes":archive.stat().st_size,"sha256":sha(archive.read_bytes()),
         "members":len(manifest)+1,"manifest_verified_members":len(manifest),"crc":"PASS",
         "native_status":"PENDING","model_calls":0}
(HERE/"BUILD_RECEIPT.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(receipt,ensure_ascii=False))

