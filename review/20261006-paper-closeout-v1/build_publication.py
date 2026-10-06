#!/usr/bin/env python3
"""组装论文收尾的明确文件清单；不覆盖历史发布、不运行统计模型。"""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import shutil
import zipfile

P = Path(__file__).resolve().parent
OUT = P / 'delivery' / 'review_payload'
OUT.mkdir(parents=True, exist_ok=True)
BASE = 'https://raw.githubusercontent.com/lzhs1995/CMAverse-paper/main/review/20261006-paper-closeout-v1/'

readme = '''# 筛选显著性：论文改文与来源补齐（2026-10-06）

本增量的统计结果已冻结，论文离线内容与来源核验完成；原生Word、Zotero刷新、最终PDF和同版NLM验收待完成。请先读取REPORT.md及ACCEPTANCE.json，再核对实际DOCX与结果表。不得把本增量称为论文原生最终交付。

## 本轮结论

- FEAS_031为优先探索候选，FEAS_041为相关操作化线索。两项去dwm后的未调整区间不含零，历史B=200搜索校正均未达5%。不拼接不同版本的点估计、区间与p。
- P3原金额整体p=0.131934，封顶整体p=0.079960；数值修复已在上一阶段完成。本轮只核查保存结果，未重跑模型。
- N1为人际/个人内辅助关联。最终六项BH/BY均未达5%；没有确认完整中介或普遍修饰机制。
- 本轮更新表10、新增表11—13、修正R6讨论和P3失败状态，删去表E.1旧NA说明；有限理论回溯没有把资源协商假说写成已识别机制。

## 在线入口（完整地址）

主报告：
''' + BASE + '''REPORT.md

给网页端的审阅顺序与范围：
''' + BASE + '''FOR_WEB_REVIEWERS.md

正文文本：
''' + BASE + '''manuscript/MANUSCRIPT_TEXT.md

完整增量包：
''' + BASE + '''paper_review_part01.zip

文件清单：
''' + BASE + '''MANIFEST.json

包验收记录：
''' + BASE + '''PACKAGE_QA.json

## 包内内容与验证

包含本轮离线DOCX及两个即时前驱、逐部件差异、9张来源明确的结果CSV、120项执行输入绑定日志、288份来源哈希记录、三篇原文的有限理论证据矩阵、复核附件、脚本和离线QA。旧11包/N1补充继续沿用，不重复上传。约198MB的120份执行输入原件不放入本增量；绑定日志不等于审阅者已读取这些RDS。

所有包必须小于25,000,000字节。精确大小、成员数和SHA见PACKAGE_QA.json；MANIFEST.json覆盖全部载荷文件，自身不做递归哈希，ZIP整体SHA由包外PACKAGE_QA.json登记。包外下载回执另行固定提交绑定。

下载包和verify_review_package.py后，用Python 3执行：

    python3 verify_review_package.py paper_review_part01.zip

该脚本验证完整CRC、每个载荷的字节数和SHA、JSON/CSV/DOCX解析，以及最新候选相对数值稿仅改变word/document.xml。它不执行R、模型或原生Word。

## 与前轮的关系

数值基线固定为687194000f275a73e83648e1c5362613ad8b0be4：
https://github.com/lzhs1995/CMAverse-paper/tree/687194000f275a73e83648e1c5362613ad8b0be4/review/20261006-numerical-closeout-v1

本轮候选SHA-256：ff278c5bba68ff7c6cdd0d52fc9cdd8fa7d2bac57876a2751fee8be3ddb4e95f。
来源/算术12项通过、正文表格9项读回通过、最终DOCX50项离线独立检查通过。它们各自有覆盖范围，均不代替动态引文刷新、实际分页或同版PDF终审。
'''

reviewers = '''# 请ChatGPT网页端审阅本轮新增论文与来源材料

任务仍为CMAverse“筛选显著性”。本轮没有新增模型、编码网格、bootstrap或研究假设p值。请沿用已经验收的旧11包、N1冻结文件及数值收尾增量；先下载本包并核验清单，再审阅正文和证据。

## 建议读取顺序

1. README.md、REPORT.md、ACCEPTANCE.json、PACKAGE_QA.json。
2. manuscript/MANUSCRIPT_TEXT.md与实际离线DOCX；文本不能展示全部公式和图片。
3. manuscript/sources内的两个即时前驱、qa/DOCX_PART_DIFF.csv、TEXT_PATCHES.json及独立DOCX核验记录。此前“缺即时前驱”已补齐。
4. results目录9张CSV、bindings/EXECUTION_INPUTS_120.csv、SOURCE_PINS.json及SCOPE.json。此前“缺120项输入来源绑定”已补齐，实际198MB执行对象未重传。
5. theory内证据矩阵、原文页段定位及边界；review/PRO_RESPONSE.md逐项说明如何处理上轮建议。

## 希望本轮回答的问题

- 表10是否真正覆盖完整中介、选择后修饰线索、PE、政策情景和N1，而非只总结旧八链？
- 候选定义、去dwm点估计/区间、历史B=200及B=1000原始p、历史搜索校正是否严格分版本？
- R6辅助p是否与最终P3整体p=.132/.080一起解释？P3修复是否与其他历史失败清楚区分？
- 理论文字是否准确区分夫妻相对评价变化、绝对满意度改善、收入效应修饰、满意度自身关联与完整中介？
- 若仍有问题，请给出现稿段落/表格定位、证据文件、替换文字，并区分统计错误、解释问题和原生版式待验收。

## 已知边界，避免重复索取或误验收

- 031/041仍是探索性候选；未发现搜索校正支持的确认性机制。当前去dwm结果没有新p或新搜索校正，不能移植旧p。
- 28.35%本人提高、88.01%配偶下降引用前轮Pro报告的1,559条共同分母，本轮绑定报告原文与SHA，未重新逐行计数；两类可重叠。
- 三篇原文直接核读9个PDF页段，形成7项证据矩阵；不是广泛系统综述，也没有新增原生Zotero引文。
- 120项来源文件已在本机重新哈希；R内实际索引/种子验证引用历史已接受job d128f101。不得把本轮哈希核对写成新R重跑。
- 50项DOCX离线通过不代表原生修订接受/拒绝、Zotero实际刷新、Word导出PDF或最终同版NLM通过。这些仍为PENDING，参阅native_readiness/CURRENT_STATUS.json。
- 本批统计计算结束。请勿为了跨过0.05继续增加组合、缩检验族、改单侧、换种子或追加B。原生交付恢复与统计判断分开。

## 复核程序的可执行范围

verify_review_package.py可仅用本包独立执行，完成文件级验证。其他脚本保留研究机绝对路径和冻结输入哈希，作用是公开产生结果/核验的代码；模型级重跑或288源文件重新绑定需要相应历史文件及原目录映射。本增量并非声称包含所有上游数据的独立环境镜像。
'''
(P/'README.md').write_text(readme, encoding='utf-8')
(P/'FOR_WEB_REVIEWERS.md').write_text(reviewers, encoding='utf-8')

files = [P/n for n in ['README.md', 'FOR_WEB_REVIEWERS.md', 'REPORT.md', 'ACCEPTANCE.json',
                           'verify_review_package.py', 'build_publication.py',
                           'build_paper_candidate.py', 'prepare_reports.py']]
for folder in ['bindings', 'results', 'review', 'theory', 'manuscript']:
    files += [f for f in (P/folder).rglob('*') if f.is_file() and '__pycache__' not in f.parts]
for n in ['DOCX_PART_DIFF.csv', 'FORMAT_CONTRACT.json', 'MANUSCRIPT_QA.json',
          'INDEPENDENT_DOCX_REVIEW.json', 'INDEPENDENT_DOCX_REVIEW.md', 'independent_docx_review.py']:
    files.append(P/'qa'/n)
files.append(P/'native_readiness/CURRENT_STATUS.json')
for f in files:
    target = OUT / f.relative_to(P)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(f, target)
expected = {str(f.relative_to(P)) for f in files}
actual = {str(f.relative_to(OUT)) for f in OUT.rglob('*') if f.is_file()}
assert actual - expected <= {'MANIFEST.json'}, 'unexpected staged file'
# 目录内嵌清单也属于载荷；仅排除顶层清单自身。
entries = [{'path': str(f.relative_to(OUT)), 'bytes': f.stat().st_size,
            'sha256': hashlib.sha256(f.read_bytes()).hexdigest()}
           for f in sorted(OUT.rglob('*')) if f.is_file() and f != OUT/'MANIFEST.json']
manifest = {'schema': 1, 'task': 'CMAverse significance screening paper closeout',
            'created_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'self_excluded': ['MANIFEST.json'], 'file_count': len(entries), 'files': entries}
(OUT/'MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
package = P/'delivery/paper_review_part01.zip'
with zipfile.ZipFile(package, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for f in sorted(OUT.rglob('*')):
        if f.is_file():
            z.write(f, str(f.relative_to(OUT)))
assert package.stat().st_size < 25_000_000, 'split package before publication'
spec = importlib.util.spec_from_file_location('verifier', P/'verify_review_package.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)
qa = verifier.verify(package)
(P/'delivery/PACKAGE_QA.json').write_text(json.dumps(qa, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
shutil.copy2(OUT/'MANIFEST.json', P/'delivery/MANIFEST.json')
print(json.dumps(qa, ensure_ascii=False, indent=2))
