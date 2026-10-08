#!/usr/bin/env python3
# 独立只读审阅：不导入构建脚本的 m/prev 模块，只用 zipfile+lxml 自行解析四稿及绑定前驱/母稿。
# 输出仅写入本目录 review_out/；任何输入文件只读。
import sys, json, hashlib, re
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
V3 = HERE.parent
MS = V3 / 'manuscript_v1'
PUB = Path('/private/tmp/cma-web-delivery-20261006/review/20261007-significance-feedback-v5/manuscript')
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(n): return '{%s}%s' % (W, n)

# 任务包 input_pins 与 SOURCE_BINDINGS 中的前驱期望值（逐字抄自两文件，运行时再与文件内容互核）
PACK = HERE / 'task-pack.json'
STORY = re.compile(r'word/(document|footnotes|endnotes|comments|header\d*|footer\d*)\.xml')
# 修订类元素（自建清单，不复用构建脚本 TRACK_NAMES）
REV = {'ins','del','moveFrom','moveTo','rPrChange','pPrChange','sectPrChange','tblPrChange',
       'tblGridChange','trPrChange','tcPrChange','numberingChange','cellIns','cellDel','cellMerge',
       'moveFromRangeStart','moveFromRangeEnd','moveToRangeStart','moveToRangeEnd',
       'customXmlInsRangeStart','customXmlInsRangeEnd','customXmlDelRangeStart','customXmlDelRangeEnd',
       'customXmlMoveFromRangeStart','customXmlMoveFromRangeEnd','customXmlMoveToRangeStart','customXmlMoveToRangeEnd'}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def parts(p):
    with ZipFile(p) as z: return {n: z.read(n) for n in z.namelist()}
def X(b): return E.fromstring(b)
def c14n(n): return E.tostring(n, method='c14n')
def local(e): return E.QName(e).localname if isinstance(e.tag, str) else None

def ptext(p, mode='raw'):
    # mode: raw=全部 w:t；accept=跳过 del/moveFrom；reject=跳过 ins/moveTo 且计入 delText
    out = []
    for e in p.iter():
        ln = local(e)
        if ln not in ('t', 'delText', 'tab', 'br'): continue
        anc = {local(a) for a in e.iterancestors()}
        if mode == 'accept' and anc & {'del', 'moveFrom'}: continue
        if mode == 'reject' and anc & {'ins', 'moveTo'}: continue
        if row_dropped(e, mode): continue
        if ln == 't': out.append(e.text or '')
        elif ln == 'delText':
            if mode == 'reject': out.append(e.text or '')
        elif ln == 'tab': out.append('\t')
    return ''.join(out)

def row_dropped(e, mode):
    # 修订一：行级修订（w:trPr/w:ins|del）——首轮遗漏导致整表插入/删除被误计
    kind = 'del' if mode == 'accept' else 'ins' if mode == 'reject' else None
    if kind is None: return False
    for a in ([e] if local(e) == 'tr' else []) + [a for a in e.iterancestors() if local(a) == 'tr']:
        tp = a.find(q('trPr'))
        if tp is not None and tp.find(q(kind)) is not None: return True
    return False

def mark(p, kind):
    # 段落标记本身是否被插入/删除（w:pPr/w:rPr/w:ins|del）
    rp = p.find(q('pPr') + '/' + q('rPr'))
    return rp is not None and rp.find(q(kind)) is not None

def story_text(root, mode):
    # 以段落为单位拼接；段落标记被删(接受)或被插(拒绝)时与下一段合并
    segs = []; buf = ''
    for p in root.iter(q('p')):
        if row_dropped(p, mode): continue
        buf += ptext(p, mode)
        merge = (mode == 'accept' and mark(p, 'del')) or (mode == 'reject' and mark(p, 'ins'))
        if not merge: segs.append(buf); buf = ''
    if buf: segs.append(buf)
    return segs

def body_items(root):
    b = root.find(q('body'))
    return b.findall(q('p')), b.findall(q('tbl'))

def fields(root):
    # 复杂域指令串 + 简单域指令串（按出现顺序）
    out = []; cur = None
    for e in root.iter():
        ln = local(e)
        if ln == 'fldSimple': out.append(('simple', e.get(q('instr')).strip()))
        elif ln == 'fldChar':
            t = e.get(q('fldCharType'))
            if t == 'begin': cur = []
            elif t == 'separate' and cur is not None: out.append(('complex', ''.join(cur).strip())); cur = None
            elif t == 'end' and cur is not None: out.append(('complex', ''.join(cur).strip())); cur = None
        elif ln in ('instrText', 'delInstrText') and cur is not None: cur.append(e.text or '')
    return out

def rev_ids(pp):
    ids = []; ann = []
    for k, b in pp.items():
        if not STORY.fullmatch(k): continue
        for e in X(b).iter():
            ln = local(e)
            if ln in REV and e.get(q('id')) is not None: ids.append((k, ln, e.get(q('id'))))
            elif ln in ('bookmarkStart', 'commentRangeStart', 'commentReference') and e.get(q('id')) is not None:
                ann.append((k, ln, e.get(q('id'))))
    return ids, ann

R = {'checks': [], 'findings': []}
def check(name, ok, **detail):
    R['checks'].append({'name': name, 'pass': bool(ok), **detail})
    print(('PASS ' if ok else 'FAIL ') + name, json.dumps(detail, ensure_ascii=False)[:300])
    return ok

def main():
    pack = json.loads(PACK.read_text())
    # 1. 输入钉
    for e in pack['input_pins']:
        h = sha(e['path']); check('pin:' + Path(e['path']).name, h == e['sha256'], sha256=h)
    bind = json.loads((MS / 'SOURCE_BINDINGS.json').read_text())
    for k, e in bind.items():
        h = sha(e['path']); check('binding:' + k, h == e['sha256'], sha256=h, path=e['path'])
    R['input_sha256'] = {Path(e['path']).name: e['sha256'] for e in pack['input_pins']}
    R['binding_sha256'] = {k: e['sha256'] for k, e in bind.items()}

    new = {k: parts(MS / (k + '.docx')) for k in ('content_patched', 'tracked_patched', 'accepted_offline', 'rejected_offline')}
    old = {k: parts(PUB / (k + '.docx')) for k in ('content_patched', 'accepted_offline', 'rejected_offline')}
    mother = parts(bind['mother']['path']); raw = parts(bind['tracked_native_ids_fixed']['path'])

    # 2. 部件级：只 document.xml 变化
    for a, b, label in [(new['content_patched'], old['content_patched'], 'content_vs_old_content'),
                        (new['accepted_offline'], old['accepted_offline'], 'accepted_vs_old_accepted'),
                        (new['tracked_patched'], raw, 'tracked_vs_raw_predecessor')]:
        diff = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
        check('parts_changed:' + label, diff == ['word/document.xml'] and set(a) == set(b), changed=diff)
    # 拒绝投影 = 母稿 / 旧拒绝投影（逐部件 c14n 比较 story，其余逐字节）
    for ref, label in [(mother, 'rejected_vs_mother'), (old['rejected_offline'], 'rejected_vs_old_rejected')]:
        a = new['rejected_offline']; diff = []
        for k in sorted(set(a) | set(ref)):
            if k not in a or k not in ref: diff.append(k); continue
            if a[k] == ref[k]: continue
            # 修订二：.rels 也是 XML（首轮只认 .xml 后缀）；[Content_Types] 的 Override 顺序在 OPC 中无语义
            if k.endswith(('.xml', '.rels')):
                if c14n(X(a[k])) == c14n(X(ref[k])): continue
                if k == '[Content_Types].xml' and sorted(map(c14n, X(a[k]))) == sorted(map(c14n, X(ref[k]))): continue
            diff.append(k)
        check('parts_equal:' + label, not diff, differing=diff)
    R['zip_level'] = {'rejected_offline_bytes_identical_to_old_rejected': sha(MS / 'rejected_offline.docx') == sha(PUB / 'rejected_offline.docx')}
    return new, old, mother, raw

TARGETS = [221, 253, 282]
def body_checks(new, old, mother, raw):
    D = lambda pp: X(pp['word/document.xml'])
    for a_key, b_key in [('content_patched', 'content_patched'), ('accepted_offline', 'accepted_offline')]:
        ar, br = D(new[a_key]), D(old[b_key])
        ap, at = body_items(ar); bp, bt = body_items(br)
        check(a_key + ':paragraph_count', len(ap) == len(bp), new=len(ap), old=len(bp))
        canon = [i for i, (x, y) in enumerate(zip(ap, bp), 1) if c14n(x) != c14n(y)]
        textd = [i for i, (x, y) in enumerate(zip(ap, bp), 1) if ptext(x) != ptext(y)]
        check(a_key + ':changed_paragraphs_c14n', canon == TARGETS, changed=canon)
        check(a_key + ':changed_paragraphs_text', textd == TARGETS, changed=textd)
        check(a_key + ':P104_unchanged', c14n(ap[103]) == c14n(bp[103]))
        check(a_key + ':tables_34_c14n_equal', len(at) == len(bt) == 34 and all(c14n(x) == c14n(y) for x, y in zip(at, bt)), n=len(at))
        # 正文其余元素（sectPr 等）
        rest = lambda r: [c14n(e) for e in r.find(q('body')) if local(e) not in ('p', 'tbl')]
        check(a_key + ':body_other_elements_equal', rest(ar) == rest(br))
        # 三处段落：pPr 与首 run rPr 保持、无域/书签/超链接丢失
        for i in TARGETS:
            x, y = ap[i - 1], bp[i - 1]
            ppr = lambda p: c14n(p.find(q('pPr'))) if p.find(q('pPr')) is not None else b''
            rpr = lambda p: [c14n(r) for r in p.iter(q('rPr')) if r.getparent().tag == q('r')][:1]
            kinds = lambda p: sorted(local(e) for e in p.iter() if local(e) in ('fldChar', 'fldSimple', 'instrText', 'bookmarkStart', 'hyperlink', 'commentRangeStart', 'footnoteReference', 'endnoteReference', 'drawing', 'object'))
            check(f'{a_key}:P{i}_pPr_kept', ppr(x) == ppr(y))
            check(f'{a_key}:P{i}_first_rPr_kept', rpr(x) == rpr(y))
            check(f'{a_key}:P{i}_no_lost_inline_objects', kinds(x) == kinds(y), new=kinds(x), old=kinds(y))
        # 域与书目
        # 修订三：引用分布在正文+脚注等全部 story（首轮只数 document.xml，得 20）
        sks = sorted(k for k in new[a_key] if STORY.fullmatch(k))
        fn = [(k,) + f for k in sks for f in fields(X(new[a_key][k]))]
        fo = [(k,) + f for k in sks for f in fields(X(old[b_key][k]))]
        check(a_key + ':fields_all_stories_identical_order', fn == fo, n=len(fn))
        cites = [f for f in fn if 'ADDIN ZOTERO_ITEM' in f[2]]; bibs = [f for f in fn if 'ADDIN ZOTERO_BIBL' in f[2]]
        check(a_key + ':zotero_23_citations_1_bibliography', len(cites) == 23 and len(bibs) == 1, cites=len(cites), bibl=len(bibs), all_fields=len(fn),
              by_story={k: sum(1 for f in cites if f[0] == k) for k in sks if any(f[0] == k for f in cites)})
        hp = [i for i, p in enumerate(ap, 1) if ptext(p) == '参考文献']
        bib_new = [ptext(p) for p in ap[hp[0]:hp[0] + 25]] if hp else []
        bib_old = [ptext(p) for p in bp[hp[0]:hp[0] + 25]] if hp else []
        check(a_key + ':bibliography_25_same_order', len(hp) == 1 and bib_new == bib_old and len(ap) - hp[0] >= 25, heading_p=hp, tail_paragraphs=len(ap) - (hp[0] if hp else 0))
        R.setdefault('texts', {})[a_key] = {i: {'before': ptext(bp[i - 1]), 'after': ptext(ap[i - 1])} for i in TARGETS}
    # D.1 = 第25表；逐行逐单元
    ct, oc = body_items(D(new['content_patched']))[1][24], body_items(D(old['content_patched']))[1][24]
    rows = lambda t: [[ptext(tc) for tc in tr.findall(q('tc'))] for tr in t.findall(q('tr'))]
    rn, ro = rows(ct), rows(oc)
    check('D1:header_and_22_rows_cellwise_equal', rn == ro and len(rn) == 23 and rn[0][2] == '尺度', rows=len(rn) - 1)
    R['D1_units'] = sorted({r[2] for r in rn[1:]}); R['D1_rows'] = rn
    # 九个 story 部件：除 document.xml 外逐字节
    sk = sorted(k for k in new['content_patched'] if STORY.fullmatch(k))
    check('stories_9_nonbody_bytes_equal', len(sk) == 9 and all(new['content_patched'][k] == old['content_patched'][k] for k in sk if k != 'word/document.xml'), stories=sk)
    return sk

def tracked_checks(new, mother, raw):
    tr = new['tracked_patched']
    ids, ann = rev_ids(tr)
    vals = [i[2] for i in ids]
    dup = sorted({v for v in vals if vals.count(v) > 1}) if len(vals) != len(set(vals)) else []
    check('tracked:revision_ids_unique_all_stories', not dup, count=len(vals), unique=len(set(vals)), dup=dup[:10])
    rids, _ = rev_ids(raw); R['revision_counts'] = {'tracked_patched': len(vals), 'raw_predecessor': len(rids), 'new': len(vals) - len(rids)}
    R['revision_ids_overlapping_annotation_ids'] = len(set(vals) & {a[2] for a in ann})
    # 新增修订只落在三处
    tp, _ = body_items(X(tr['word/document.xml'])); rp, _ = body_items(X(raw['word/document.xml']))
    canon = [i for i, (x, y) in enumerate(zip(tp, rp), 1) if c14n(x) != c14n(y)]
    # 修订四：tracked 稿含被删段落，正文序号与接受态不同；按“接受态段落序号”映射后再判定
    amap = []; k = 0
    for i, p in enumerate(tp, 1):
        if not (mark(p, 'del') and not ptext(p, 'accept')): k += 1
        amap.append(k)
    mapped = [amap[i - 1] for i in canon]
    check('tracked:diff_vs_raw_only_targets', len(tp) == len(rp) and len(canon) == 3, tracked_index=canon, accepted_index_by_mark=mapped)
    cp, _ = body_items(X(new['content_patched']['word/document.xml']))
    want = [ptext(cp[i - 1]) for i in TARGETS]
    got = [ptext(tp[i - 1], 'accept') for i in canon]
    check('tracked:changed_paragraphs_accept_to_approved_targets', got == want)
    old_txt = [R['texts']['content_patched'][i]['before'] for i in TARGETS]
    check('tracked:changed_paragraphs_reject_to_old_targets', [ptext(tp[i - 1], 'reject') for i in canon] == [ptext(rp[i - 1], 'reject') for i in canon] and [ptext(rp[i - 1], 'accept') for i in canon] == old_txt)
    R['tracked_target_index'] = dict(zip(map(str, TARGETS), canon))
    # 修订五（负对照 drop_row_level_del 暴露）：tracked 对前驱的表格与其他正文元素此前不在管辖内
    tt = X(tr['word/document.xml']).find(q('body')); rt = X(raw['word/document.xml']).find(q('body'))
    nonp = lambda b: [c14n(e) for e in b if local(e) != 'p']
    check('tracked:tables_and_other_body_equal_raw', nonp(tt) == nonp(rt), n=len(nonp(tt)))
    newids = sorted({e.get(q('id')) for i in canon for e in tp[i - 1].iter() if local(e) in REV} - {e.get(q('id')) for i in canon for e in rp[i - 1].iter() if local(e) in REV}, key=int)
    R['new_revision_ids_in_targets'] = newids
    meta = sorted({(e.get(q('author')), e.get(q('date'))) for i in canon for e in tp[i - 1].iter() if local(e) in ('ins', 'del') and e.get(q('id')) in newids})
    R['new_revision_author_date'] = meta
    # 自建接受/拒绝文本投影 vs 离线投影 vs 母稿
    for k in sorted(k for k in tr if STORY.fullmatch(k)):
        t = X(tr[k])
        acc = story_text(t, 'accept'); rej = story_text(t, 'reject')
        ao = story_text(X(new['accepted_offline'][k]), 'raw'); ro = story_text(X(new['rejected_offline'][k]), 'raw')
        mo = story_text(X(mother[k]), 'raw') if k in mother else None
        check('projection_accept_text:' + k, acc == ao, n=len(acc))
        check('projection_reject_text:' + k, rej == ro and rej == mo, n=len(rej))
    # 接受态目标段 = 批准新文本
    ap, _ = body_items(X(new['accepted_offline']['word/document.xml']))
    cp, _ = body_items(X(new['content_patched']['word/document.xml']))
    for i in TARGETS:
        check(f'accepted_P{i}_equals_content_P{i}', ptext(ap[i - 1]) == ptext(cp[i - 1]))
    # 已修订稿中无残留修订：content/accepted/rejected
    for label in ('content_patched', 'accepted_offline', 'rejected_offline'):
        n = sum(1 for k, b in new[label].items() if STORY.fullmatch(k) for e in X(b).iter() if local(e) in REV)
        check(label + ':no_residual_revisions', n == 0, n=n)

def semantic_scan(new):
    # P253 口径一致性：全稿中“截尾/封顶/pmin/第99百分位”出现位置（接受态）
    ap, at = body_items(X(new['content_patched']['word/document.xml']))
    hits = []
    for i, p in enumerate(ap, 1):
        s = ptext(p)
        for kw in ('截尾', '封顶', 'pmin', '第99百分位', '99百分位', '缩尾', 'winsor'):
            if kw in s: hits.append({'p': i, 'kw': kw, 'ctx': s[max(0, s.find(kw) - 40): s.find(kw) + 40]})
    for j, t in enumerate(at, 1):
        s = ptext(t)
        for kw in ('截尾', '封顶', 'pmin', '99百分位', '缩尾'):
            if kw in s: hits.append({'tbl': j, 'kw': kw, 'ctx': s[max(0, s.find(kw) - 40): s.find(kw) + 40]})
    R['p253_keyword_hits'] = hits
    # P282 起句与 E.4 标题、P104 指引
    R['p281_heading'] = ptext(ap[280]); R['p104_pointer_has_E4'] = '附录E.4' in ptext(ap[103])
    R['p221_prev_heading'] = ptext(ap[219])

if __name__ == '__main__':
    new, old, mother, raw = main()
    body_checks(new, old, mother, raw)
    tracked_checks(new, mother, raw)
    semantic_scan(new)
    R['n_checks'] = len(R['checks']); R['n_fail'] = sum(1 for c in R['checks'] if not c['pass'])
    out = HERE / 'review_out'; out.mkdir(exist_ok=True)
    (out / 'INDEPENDENT_REVIEW_QA.json').write_text(json.dumps(R, ensure_ascii=False, indent=2) + '\n')
    print('n_checks', R['n_checks'], 'n_fail', R['n_fail'])
