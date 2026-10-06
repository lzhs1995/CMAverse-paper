from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
import csv,json,hashlib,copy
o=Path(__file__).resolve().parent;l=o.parent
src=next((l/'word_preparation_v1/clean_successor_v2').glob('*结构规范化.docx'))
dest=o/'manuscript';dest.mkdir(exist_ok=True)
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'};w='{'+ns['w']+'}'
with ZipFile(src) as z:
    members={i.filename:z.read(i.filename) for i in z.infolist()}
r=E.fromstring(members['word/document.xml']);ps=r.findall('w:body/w:p',ns)
def text(p):return ''.join(p.xpath('.//w:t/text()',namespaces=ns))
def replace(p,new):
    assert not p.xpath('.//w:fldChar|.//w:instrText|.//w:drawing',namespaces=ns)
    ts=p.findall('.//w:t',ns);assert ts
    ts[0].text=new
    for t in ts[1:]:t.text=''
changes=[]
updates={
96:'P3在12,634条合格记录上，以是否支持的Logit模型和正值金额的Gamma/Log模型合成总体月均金额，标准化计算逐行预测概率与条件金额之积的平均值。原金额与固定2,664.2984元/月封顶金额分别检验5分对≤3分、5分对4分组成的二维整体对比。保留原3,212簇抽样框、3,153个贡献簇及同一2,000份抽样的重复权重。原求解器出现49次原金额失败后，按预先冻结的数值修复合同验证原样本、49份失败及3份成功对照，再统一重算全部2,000份原金额与封顶结果；模型、样本、公式和目标函数均不改变，不只填补失败重复。整体检验采用中心化重复向量与其协方差构成的二次型，至少98%重复有效方可报告；该规则不等于一般统计校准已获证明。',
97:text(ps[97]).replace('暂缓项保留NA且分母仍为6','本次数值修复后六项均可估计，调整分母固定为6'),
165:text(ps[165])+' 对旧B=200筛选版本复算的Romano–Wolf型逐步最大统计量校正显示，FEAS_031在120项ΔCDE家族及全部240项目标中的校正p分别为0.134328和0.542289，FEAS_041分别为0.631841和0.915423。实际索引与种子逐规格匹配；该校正覆盖150个注册规格中120个可估计规格，不能视为全部历史选择的校准证明，也不能直接移植到去dwm后的B=1,000版本。031与041因此保留为相关操作化下的探索性修饰线索，不构成两个独立复制。',
166:'P3同似然数值修复后，原金额与封顶金额各2,000/2,000次重复有效。原金额三种满意度状态下的总体月均金额收入对比分别为38.2766、44.6611和14.2434元，二维整体检验原始p=0.131934，六项家族BH q=0.158321、BY q=0.387886。封顶金额对应对比为36.6696、41.4140和11.0588元，整体p=0.079960、BH q=0.119940、BY q=0.293853。两种整体检验均未达到0.05；修复恢复了原金额的可估计性，未提供显著整体修饰证据。',
168:text(ps[168]).replace('各项定义、区间和暂缓状态见附录E。','各项定义、区间和数值修复状态见附录E。本批结果冻结后停止扩展筛选。'),
260:'原金额5分对≤3分及5分对4分之差为−24.0332、−30.4177元/月；封顶金额对应差值为−25.6108、−30.3552元/月。旧49次失败（48次不收敛、1次拟合或预测错误）完整留档。固定验证中的53份样本、两种金额口径均通过满秩、正Hessian、梯度、两起点及有限正预测检查，随后统一应用新求解规则至原2,000份抽样。新旧概率方程重复值完全一致，所有原抽样哈希逐项匹配，原金额与封顶金额各2,000次有效。整体尾部计数分别为263与159，加一p分别为264/2001及160/2001；本轮未新增单个状态或相邻对比p值。',
264:'注：固定家族共6项，数值修复后六项均可估计；BH/BY均未在0.05水平拒绝。本表仅调整本次六项检验，不消除历史模型选择。P1/P2敏感性区间不属于本表六项家族；旧B=200搜索校正另行报告。N2只描述既有分期点，不新增检验。'
}
for i,new in updates.items():
    before=text(ps[i]);replace(ps[i],new);changes.append(dict(paragraph=i,before=before,after=new))
with (o/'exports/SIX_TEST_FAMILY.csv').open() as f:family=list(csv.DictReader(f))
table=r.findall('w:body/w:tbl',ns)[30];rows=table.findall('w:tr',ns)
assert len(rows)==7
for row,record in zip(rows[1:],family):
    cells=row.findall('w:tc',ns)
    for j,k in [(1,'p_raw'),(2,'q_BH6'),(3,'q_BY6')]:
        before=text(cells[j]);new=f"{float(record[k]):.6f}";replace(cells[j],new);changes.append(dict(table=30,before=before,after=new))
    replace(cells[4],'选择后探索')
newxml=E.tostring(r,xml_declaration=True,encoding='UTF-8',standalone=True)
out=dest/'CMAverse_数值收尾合入_离线内容候选_未原生验收.docx'
with ZipFile(out,'w',ZIP_DEFLATED) as z:
    for name,b in members.items():z.writestr(name,newxml if name=='word/document.xml' else b)
with ZipFile(out) as z:
    assert z.testzip() is None
    assert all(z.read(k)==v for k,v in members.items() if k!='word/document.xml')
    after=E.fromstring(z.read('word/document.xml'))
for query in ['.//w:instrText','.//w:drawing']:
    before=E.fromstring(members['word/document.xml']).xpath(query,namespaces=ns)
    now=after.xpath(query,namespaces=ns)
    assert [E.tostring(x) for x in before]==[E.tostring(x) for x in now]
(dest/'TEXT_PATCHES.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2))
lines=[]
for e in after.find('w:body',ns):
    if e.tag==w+'p':lines.append(text(e))
    elif e.tag==w+'tbl':
        for tr in e.findall('w:tr',ns):lines.append(' | '.join(text(c) for c in tr.findall('w:tc',ns)))
(dest/'MANUSCRIPT_TEXT.md').write_text('\n\n'.join(lines))
qa=dict(status='OFFLINE_CONTENT_PASS_NOT_NATIVE_FINAL',source=str(src),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),changed_paragraphs=list(updates),table_index=30,other_zip_parts_identical=True,field_codes_and_drawings_identical=True,native_word_pdf_nlm='PENDING_EXISTING_UI_BLOCKER')
(dest/'QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
print(json.dumps(qa,ensure_ascii=False,indent=2))
