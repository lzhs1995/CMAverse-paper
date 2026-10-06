"""论文收尾：仅消费冻结CSV、保留源DOCX部件；不启动统计模型或原生UI。"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
import csv, json, hashlib, copy, re

P=Path(__file__).resolve().parent
L=P.parent
O=L/'numerical_closeout_20261006_v1'
SRC=O/'manuscript/CMAverse_数值收尾合入_离线内容候选_未原生验收.docx'
PREV=L/'word_preparation_v1/clean_successor_v2/CMAverse_限定复核与家务核验合入_干净离线候选_非交付_结构规范化.docx'
OUT=P/'manuscript/CMAverse_论文收尾合入_离线候选_原生验收待完成.docx'
N={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W='{'+N['w']+'}'
def sha(b): return hashlib.sha256(b).hexdigest()
def dump(path,value): path.write_text(json.dumps(value,ensure_ascii=False,indent=2))
def rows(name):
    with (P/'results'/name).open(encoding='utf-8-sig') as f: return list(csv.DictReader(f))
def txt(e): return ''.join(e.xpath('.//w:t/text()',namespaces=N))
def el(tag,**attrs): return E.Element(W+tag,{W+k:str(v) for k,v in attrs.items()})
def put(parent,tag,**attrs):
    x=parent.find(W+tag)
    if x is None: x=el(tag);parent.append(x)
    for k,v in attrs.items(): x.set(W+k,str(v))
    return x
assert sha(SRC.read_bytes())=='cace3fc14e4cb8e4f516386890d331093c99fb0ffa363b91065200e1e5fcf00d'
assert sha(PREV.read_bytes())=='b0eec6b7af348f289928c961b1e89ca51d9389e50f529d2a4b738bee91bdce91'
with ZipFile(SRC) as z: members={i.filename:z.read(i.filename) for i in z.infolist()}
root=E.fromstring(members['word/document.xml'])
body=root.find('w:body',N);ps=body.findall('w:p',N);tables=body.findall('w:tbl',N)
assert len(ps)==291 and len(tables)==31
original=copy.deepcopy(root)
assert not root.xpath('.//w:ins|.//w:del|.//w:rPrChange|.//w:pPrChange',namespaces=N)
contract={'source_sha256':sha(SRC.read_bytes()),'mode':'offline_content_candidate',
 'body_size_half_points':21,'table_size_half_points':21,
 'evidence':'source body paragraph165 and table13/table30 explicit w:sz=21',
 'table_fonts':{'eastAsia':'SimSun','ascii':'Times New Roman','hAnsi':'Times New Roman','cs':'Times New Roman'},
 'table_alignment':'han-left-nonhan-right','indent_length_and_char_units':0,
 'format_master':str(SRC),'native_autofit_and_pagination':'PENDING',
 'changed_tables':'table10 updated; tables11-13 added; tableE.1 values retained'}
dump(P/'qa/FORMAT_CONTRACT.json',contract)
changes=[]
def replace(p,new):
    assert not p.xpath('.//w:fldChar|.//w:instrText|.//w:drawing|.//w:footnoteReference|.//w:bookmarkStart',namespaces=N)
    ts=p.findall('.//w:t',N);assert ts
    ts[0].text=new
    for t in ts[1:]: t.text=''
def update(i,new):
    changes.append({'kind':'paragraph','source_direct_index':i,'before':txt(ps[i]),'after':new})
    replace(ps[i],new)
def paragraph(text,caption=False):
    p=copy.deepcopy(ps[162] if caption else ps[165])
    p.attrib.clear()
    replace(p,text)
    # 新建段落去掉复制产生的标识，保持原稿段落与字体格式。
    return p
def after(anchor,elements):
    for e in elements: anchor.addnext(e);anchor=e
def num(v,d=3): return f'{float(v):.{d}f}'.replace('-','−')

history=rows('CANDIDATE_HISTORY_PANELS.csv')
defs={r['spec_id']:r for r in rows('CANDIDATE_DEFINITIONS.csv')}
revised={r['spec_id']:r for r in history if r['metric']=='Delta_OR' and r['model_version']=='revised_without_dwm'}
historical=[r for r in history if r['metric']=='Delta_CDE' and r['panel_id'] in ('A_B200_SEARCH','B_B1000_LEGACY')]
p3={r['component']:r for r in rows('P3_THREE_STATE.csv')}
omni={r['component']:r for r in rows('P3_OMNIBUS.csv')}
assert set(revised)=={'FEAS_031','FEAS_041'}
assert all(not r['p_raw'] and not r['p_RW_within120'] and not r['p_RW_all240'] for r in revised.values())
assert abs(float(omni['original']['p_raw'])-264/2001)<1e-12
assert abs(float(omni['capped']['p_raw'])-160/2001)<1e-12

after(ps[67],[paragraph('上述确定性禁配针对历史八链的联合设定。后续031／041采用不同的调整结构，其固定M对比须按各自模型判断支持与识别条件，见限定复核。')])
update(96,'三状态金额复核在12,634条合格记录上，将是否支持的Logit模型与正值金额的Gamma/Log模型合成总体月均金额。分别在基期本人满意度≤3分、4分和5分状态下，比较收入增加与未增加的标准化金额；再对“5分减≤3分”与“5分减4分”组成的二维向量进行整体检验。原金额与预定99%封顶金额并列报告。原金额的数值失败已在同一样本、模型和2,000份整簇抽样下修复；技术验证及检验规则见附录E。')
update(139,txt(ps[139]).replace('相对链固定M存在','历史相对链固定M存在').replace('该问题目前主要由表6的关联性情境对比提供线索。','该问题由表6的关联性情境对比及后文限定复核分别提供线索。'))
update(161,'表10汇总基础回归、历史八链、系统探索及选择后限定复核，分别回答收入关联、完整中介、收入联系的修饰、效应消除比例和政策情景问题。未获明确证据、仍属探索性线索与目前无法可靠量化，代表不同的证据状态。')
update(163,'新增14项均已完成B=200初筛，没有合格规格达到预设精化条件。历史11项B=1,000、次级和登记敏感性结果另列于附录D。早期R6_B1的5分对4分金额差异保留为辅助结果；最终金额修饰结论依据下节原金额与封顶金额的三状态整体检验。')
update(165,'限定复核保留了两条与夫妻相对婚姻评价有关的探索性线索。删除跨波累计的父辈支持变量后，相对位置跃迁候选与分差变化候选的固定状态CDE差分别为−0.409和−0.085，未调整95%区间均不含零（表11）。这些差值处于边际OR尺度，不能解释为支持概率下降的百分点。两项模型化自然间接对比的区间均包含无效值1，未提供明确的完整中介证据。')
update(166,'三状态金额复核恢复了原金额的可估计性，但没有提供预设5%水平下的整体修饰证据。基期本人满意度为5分时，收入增加对应的支持金额对比低于4分及≤3分状态；原金额与预定99%封顶口径的整体p分别为0.132和0.080（表13）。两者各有2,000次有效重复，固定六项家族调整后亦未显著。该结果描述不同满意度状态下的收入联系，不能解读为提高满意度使支持金额减少。')
update(167,'本人—波次辅助分析使用13,293条记录，涉及5,249名成年子女和3,186簇。本人及配偶满意度的人际均值每高1分，支持发生概率分别高1.66和1.84个百分点，原始p分别为0.046和0.031；两项个人内偏差未达到5%水平。固定六项家族调整后，四项满意度关联均未显著（附录E表E.1）。人际均值差异不表示同一个人满意度提高后的作用，也不能替代中介或修饰检验。')
update(168,'既有分期结果中，女儿减儿子的收入概率对比点差，在2018—2020年和2020—2022年分别为9.23和0.17个百分点。这些结果仅作描述，没有新增跨期差异检验。综合结果保留了相对评价变化的有限修饰线索，尚不足以确认完整中介或普遍修饰机制。')
update(170,'本文考察收入变化、本人及配偶婚姻评价与向上代际经济支持之间的联系。基础回归在部分资格总体中呈现收入—支持的正向关联，但两两关联不能证明完整传导机制。系统探索与限定复核没有提供明确的完整中介证据；相对婚姻评价的两种操作化保留了负向修饰线索，历史搜索校正后均未显著。新14项没有合格规格达到预设精化条件。现有结果未支持普遍的婚姻满意度机制，也不能解释为夫妻关系与代际支持完全无关。')
update(171,'收入关联、满意度关联和机制检验应分别回答。女儿与儿子的收入—支持关联曾在次级分析中出现差异，但调整后及分期结果不足以支持稳定的性别差异。早期封顶金额模型在5分对4分的辅助对比中得到原始p=0.036；最终原金额与封顶金额的三状态整体p分别为0.132和0.080，均未达到预设5%水平。因此，辅助局部结果不能替代整体结论，也不能作为搜索校正后的确认性发现。各历史对比及其区间保留于附录D。')
update(173,'当前结论有四项边界。第一，同期变化与回溯窗口重叠，收入、婚姻评价和支持行为的完整时序尚未确立。第二，资格限定、完整案例与稳定配偶选择限制外推；家庭关联簇也未必涵盖全部依赖。第三，历史模型的联合支持和尺度问题须按具体设定判断；当前031／041没有采用旧八链的处理后变量模型，但仍依赖其自身的支持和混杂控制假设。P3原金额的49次数值失败已在同一模型与抽样下修复，其他历史失败状态仍按附录记录保留。第四，系统搜索及后续复核反复使用同一资料，稳定性检查与批内多重校正不能提供独立样本确认。')
update(263,'表E.1 固定六项检验的原始p与BH/BY调整')

table10=[
 ['对应问题','待检验预期／量化目标','现有证据','结论'],
 ['RQ1、RQ2.1','收入作用与不经焦点M的部分','基础回归部分资格总体呈正向关联；历史直接与总对比接近','保留收入—支持关联；尚未可靠识别因果分解或单一资源机制'],
 ['RQ2.2','本人负向、配偶正向中介','历史间接OR区间含1；系统探索及限定复核未发现明确完整中介','完整中介尚未获支持，不证明传导为零；支持范围与时序限制仍在'],
 ['RQ2.4','本人抑制、配偶促进的修饰','031／041去dwm后未调整区间不含0，历史搜索校正未显著；P3整体p为0.132／0.080','相对评价变化保留探索性修饰线索，未确认普遍满意度机制'],
 ['RQ2.3及RQ2.5的PE','中介／交互贡献与效应消除比例','历史ER／比例尺度不一致，部分总对比分母接近无效值','贡献份额与PE不可可靠量化；不等于理论假设已遭否定'],
 ['RQ2.5情景','满意度提升促进支持增长','历史四项净变化约0.8—1.4个百分点，区间均含0','条件预测不支持政策收益量化，不能说明实际政策无效'],
 ['辅助关联','本人／配偶满意度的人际及个人内关联','N1两项人际关联原始p<0.05，固定六项调整后均未显著','可作婚姻关系背景关联，不能替代中介／修饰，也不是完整个人固定效应'],
 ['探索性边界','组间差异、追加规格与分期稳定性','历史40项有效直接比较未见明确差异、8项暂缓；新14项零晋级；女儿差异主要见于前期','保留搜索与失败记录；分期点方向或单簇稳定不等于独立复制']
]
def make_table(data,widths=None):
    # 沿用已审阅的表E.1样式，给新增/更新的每个单元格显式字体和零缩进。
    t=copy.deepcopy(tables[30])
    for row in t.findall('w:tr',N): t.remove(row)
    grid=t.find('w:tblGrid',N)
    if grid is None: grid=el('tblGrid');t.insert(1,grid)
    for c in list(grid): grid.remove(c)
    if widths is None: widths=[9000//len(data[0])]*len(data[0])
    for width in widths: grid.append(el('gridCol',w=width))
    props=t.find('w:tblPr',N);put(props,'tblW',w=0,type='auto')
    put(props,'tblLayout',type='autofit')
    templates=tables[30].findall('w:tr',N)
    for i,values in enumerate(data):
        row=el('tr')
        rp=el('trPr')
        if i==0:rp.append(el('tblHeader'))
        row.append(rp)
        for j,value in enumerate(values):
            cell=copy.deepcopy(templates[0 if i==0 else 1].findall('w:tc',N)[min(j,4)])
            cell.attrib.clear()
            cp=cell.find('w:tcPr',N);put(cp,'tcW',w=0,type='auto')
            for p in cell.findall('w:p',N)[1:]:cell.remove(p)
            p=cell.find('w:p',N);p.attrib.clear();replace(p,value)
            pp=put(p,'pPr');put(pp,'ind',left=0,right=0,firstLine=0,hanging=0,firstLineChars=0,hangingChars=0,leftChars=0,rightChars=0)
            put(pp,'jc',val='left' if re.search(r'[\u3400-\u9fff]',value) else 'right')
            put(pp,'keepNext',val='1' if i==0 else '0')
            for run in p.findall('w:r',N):
                rpr=put(run,'rPr');f=put(rpr,'rFonts',**contract['table_fonts'])
                for a in list(f.attrib):
                    if 'Theme' in a:del f.attrib[a]
                put(rpr,'sz',val=21);put(rpr,'szCs',val=21)
            row.append(cell)
        t.append(row)
    return t
new10=make_table(table10)
changes.append({'kind':'table','source_table_index':13,'before':[[txt(c) for c in r.findall('w:tc',N)] for r in tables[13].findall('w:tr',N)],'after':table10})
tables[13].getparent().replace(tables[13],new10)
candidate=[
 ['项目','相对位置跃迁（FEAS_031）','分差变化（FEAS_041）'],
 ['收入X及支持Y','X：本人实际收入增加；Y：向特定父／母实际月均支持增加','X、Y同031'],
 ['相对评价M','基期本人≤配偶，期末本人>配偶记1，否则0；固定0→1','本人减配偶满意度分差的两期变化；固定0→1分'],
 ['资格总体','基期本人不高于配偶，且双方两期评分可用','完整案例且基期分差加0和1均在[−4，4]；排除61条端点不合法记录'],
 ['记录／簇',f"{defs['FEAS_031']['N']}／{defs['FEAS_031']['clusters']}",f"{defs['FEAS_041']['N']}／{defs['FEAS_041']['clusters']}"],
 ['去dwm后ΔOR',num(revised['FEAS_031']['estimate']),num(revised['FEAS_041']['estimate'])],
 ['未调整95%区间']+[f"[{num(revised[k]['ci_lower'])}，{num(revised[k]['ci_upper'])}]" for k in ['FEAS_031','FEAS_041']]
]
hist_table=[['版本／候选','原始p','同指标120项调整p','合并240项目标调整p']]
for panel,label in [('A_B200_SEARCH','历史B=200'),('B_B1000_LEGACY','旧B=1,000')]:
    for r in sorted([r for r in historical if r['panel_id']==panel],key=lambda r:r['spec_id']):
        hist_table.append([label+'／'+r['spec_id'].replace('FEAS_',''),num(r['p_raw'],6),num(r['p_RW_within120'],6) if r['p_RW_within120'] else '未计算',num(r['p_RW_all240'],6) if r['p_RW_all240'] else '未计算'])
extra165=[
 paragraph('表11 两项探索性候选的实际定义与去dwm后结果',True),make_table(candidate,[1400,3800,3800]),
 paragraph('注：记录为亲子二元组—区间。两个候选的资格总体不同，不能按ΔOR绝对大小比较社会作用强弱。区间采用B=1,000的中心化绝对偏差规则；本版本未计算新p或搜索校正。'),
 paragraph('两个时期的点估计均为负，逐簇删除也未显示某一个簇主导结果；这些检查检验点估计的稳定性，不表示每个时期或每次删簇后均显著。两种操作化使用同一资料，不能视为两个独立复制。'),
 paragraph('候选均来自系统搜索。在历史B=200版本中，考虑120项同指标对比后，031与041的调整p分别为0.134和0.632；合并两种目标后进一步增大（表12）。这项补充核查利用保存重复之间的相关性，但不涵盖全部后续自适应分析。历史校正与去dwm后的模型分开报告，不拼接为同一套推断。'),
 paragraph('表12 候选的历史原始p与历史搜索校正（ΔCDE）',True),make_table(hist_table),
 paragraph('注：历史B=200对应150个登记规格中的120个可估规格，每项有间接效应和ΔCDE两个目标；240个目标不等于240个独立检验。旧B=1,000来自筛选后精化，未另作搜索校正。此表所有模型均保留原dwm调整；其p值不适用于表11的修订模型。')
]
after(ps[165],extra165)
p3tab=[['金额口径','≤3分','4分','5分','5分减≤3分','5分减4分','整体p']]
for key,label in [('original','原金额'),('capped','预定99%封顶')]:
    p3tab.append([label]+[num(p3[key][k],2) for k in ['T_le3','T_4','T_5','d_5vle3','d_5v4']]+[num(omni[key]['p_raw'],3)])
after(ps[166],[paragraph('表13 三种基期满意度状态下的收入金额对比与整体检验',True),make_table(p3tab),
 paragraph('注：金额单位为元／月。各状态的数值为收入增加与未增加的标准化总体金额对比；两个差值共同构成预先登记的整体检验，不另加局部显著性星号。封顶用固定阈值pmin处理，没有删除大额记录。')])

theory='相对婚姻评价与婚姻质量改善是不同构念。相对位置跃迁记录中，约28.35%伴随本人评分提高、88.01%伴随配偶评分下降，两类可以重叠。因此，负向修饰不能直接写成“婚姻越幸福越不支持父母”。一种待检验的解释是，夫妻关系评价的不对称变化与核心家庭、父代家庭之间的资源配置取向有关。本研究没有直接测量资源协商与控制过程，不能由相对评分差确认权力或谈判机制。关联、收入联系的修饰和完整中介回答不同问题，也不要求同时出现。'
after(ps[171],[paragraph(theory)])
after(ps[173],[paragraph('本研究未发现经本次搜索背景核查后可确认的完整婚姻满意度中介或普遍修饰机制。少数相对评价变化组合保留了方向一致的探索性线索，但它们不等同于绝对婚姻质量改善，也不足以支持一般性的治理收益。当前结果未支持“收入改善普遍通过满意度提升促进父母支持”的强命题；夫妻关系与代际资源配置是否存在更广泛或长期的联系，仍需其他证据检验。')])

after(ps[255],[paragraph('尺度说明：本轮固定M的CDE由不含postc的结局Logit模型标准化获得；041的Gaussian中介模型影响自然间接效应的模拟，不自动使固定M的ΔOR无效。OR具有不可崩缩性，尺度差异须与实际编码或数值故障区分。当前没有postc不证明现实中不存在处理后混杂。')])
after(ps[257],[paragraph('逐簇删除导致的最大相对点变化分别为3.616%和8.016%，均低于本轮预定25%诊断阈值；该阈值只用于影响诊断，不构成新的显著性检验。历史搜索校正使用中心化重复、固定bootstrap标准差、逐步最大统计量和加一尾计数，仅作为已发生筛选的背景核查。')])
after(ps[259],[paragraph('复核使用原3,212簇抽样框，其中3,153簇在P3有贡献，重复抽中簇的权重完整保留。封顶阈值固定为2,664.29840142096元／月；两部分合成为mean(p_i×mu_i)，不采用两个均值相乘。旧原金额重复有效率为97.55%，低于预定98%门槛；同似然修复保持样本、公式、Gamma/Log模型与抽样索引不变。数值路径采用更严格的步长控制并在同一目标上精化；目标函数、梯度、Hessian和两起点一致性诊断列于随附技术记录。'),paragraph('历史推断缺失另行保留：新14项B1仅195/200次有效，敏感性R4_B1、R3_B1、R9_C1、R9_C3、R9_D1、R9_D2未达98%有效比例而暂缓正式p与区间；三波金额中介仅373/500与311/500。P3修复没有覆盖这些历史规格，不能将其计作已证实不显著。')])
changes.append({'kind':'inserted_blocks','after_source_paragraphs':[67,165,166,171,173,255,257,259],'new_table_captions':['表11','表12','表13']})

newxml=E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
with ZipFile(OUT,'w',ZIP_DEFLATED) as z:
    for name,b in members.items():z.writestr(name,newxml if name=='word/document.xml' else b)
with ZipFile(OUT) as z:
    assert z.testzip() is None
    assert all(z.read(k)==v for k,v in members.items() if k!='word/document.xml')
    out_members={i.filename:z.read(i.filename) for i in z.infolist()}
for query in ['.//w:instrText','.//w:fldChar','.//w:drawing','.//w:footnoteReference','.//w:bookmarkStart','.//w:bookmarkEnd','.//w:sectPr']:
    assert [E.tostring(x) for x in original.xpath(query,namespaces=N)]==[E.tostring(x) for x in root.xpath(query,namespaces=N)],query
assert not root.xpath('.//w:ins|.//w:del|.//w:rPrChange|.//w:pPrChange',namespaces=N)
assert 'NA表示推断暂缓' not in txt(root)
assert len(root.findall('w:body/w:tbl',N))==34

def text_export(r):
    lines=[]
    for e in r.find('w:body',N):
        if e.tag==W+'p':lines.append(txt(e))
        elif e.tag==W+'tbl':
            data=[[txt(c) for c in tr.findall('w:tc',N)] for tr in e.findall('w:tr',N)]
            for i,record in enumerate(data):
                lines.append('| '+' | '.join(x.replace('|','／').replace('\n',' ') for x in record)+' |')
                if i==0:lines.append('| '+' | '.join(['---']*len(record))+' |')
            lines.append('')
    return '\n\n'.join(lines)
(P/'manuscript/MANUSCRIPT_TEXT.md').write_text(text_export(root))
dump(P/'manuscript/TEXT_PATCHES.json',changes)
dump(P/'manuscript/EVIDENCE_TABLES.json',{'table10':table10,'table11':candidate,'table12':hist_table,'table13':p3tab})

# 对上一增量的直接前驱和本轮前驱均给出逐部件记录，原件另行打包。
part_rows=[]
for label,a,b in [('prior_increment',PREV,SRC),('this_increment',SRC,OUT)]:
    with ZipFile(a) as z: aa={i.filename:z.read(i.filename) for i in z.infolist()}
    with ZipFile(b) as z: bb={i.filename:z.read(i.filename) for i in z.infolist()}
    for k in sorted(set(aa)|set(bb)):
        part_rows.append({'comparison':label,'part':k,'before_sha256':sha(aa[k]) if k in aa else '', 'after_sha256':sha(bb[k]) if k in bb else '', 'equal':aa.get(k)==bb.get(k)})
with (P/'qa/DOCX_PART_DIFF.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(part_rows[0]));w.writeheader();w.writerows(part_rows)
consumed=[SRC,PREV]+[P/'results'/n for n in ['CANDIDATE_DEFINITIONS.csv','CANDIDATE_HISTORY_PANELS.csv','P3_THREE_STATE.csv','P3_OMNIBUS.csv']]
dump(P/'manuscript/analysis_manifest.json',{'allow_execution':False,'files':[{'path':str(f),'bytes':f.stat().st_size,'sha256':sha(f.read_bytes())} for f in consumed]})
qa={'status':'OFFLINE_CONTENT_PASS_NATIVE_PENDING','source':str(SRC),'source_sha256':sha(SRC.read_bytes()),'output':str(OUT),'output_sha256':sha(OUT.read_bytes()),'only_changed_zip_part':'word/document.xml','all_other_parts_identical':True,
 'fields_drawings_bookmarks_sections_identical':True,'revision_elements':0,'tables_before':31,'tables_after':34,'source_paragraph_changes':[c['source_direct_index'] for c in changes if c['kind']=='paragraph'],
 'numeric_sources':'frozen CSV only; no models or new p values','native_word_pdf_zotero_nlm':'NOT_COMPLETED',
 'limitations':'OOXML integrity does not establish native field refresh, accepted/rejected revision behavior, pagination or final same-PDF NLM review.'}
dump(P/'qa/MANUSCRIPT_QA.json',qa)
print(json.dumps(qa,ensure_ascii=False,indent=2))
