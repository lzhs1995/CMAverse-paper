#!/usr/bin/env python3
# 负对照：内存中变异输入（不写任何稿件），确认各判据能失败，且由预先点名的检查项命中。
import sys, json, copy
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import independent_diff_review as r
from lxml import etree as E
q, X, local = r.q, r.X, r.local

def ser(root): return E.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)

def run(new, old, mother, raw):
    r.R = {'checks': [], 'findings': []}
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        r.body_checks(new, old, mother, raw); r.tracked_checks(new, mother, raw)
    return {c['name'] for c in r.R['checks'] if not c['pass']}

def edit_doc(pp, fn, part='word/document.xml'):
    root = X(pp[part]); fn(root); pp[part] = ser(root)

def first_t(node): return next(node.iter(q('t')))

def m_d1_cell(root):  # D.1 第1数据行“估计”单元
    tbl = root.find(q('body')).findall(q('tbl'))[24]
    tc = tbl.findall(q('tr'))[1].findall(q('tc'))[3]; t = first_t(tc); t.text = t.text + '9'
def m_p104(root):
    t = first_t(root.find(q('body')).findall(q('p'))[103]); t.text = t.text + '。'
def m_p222(root):
    t = first_t(root.find(q('body')).findall(q('p'))[221]); t.text = 'X' + t.text
def m_drop_citation(root):  # 删除第一个 ZOTERO_ITEM 指令串
    for e in root.iter(q('instrText')):
        if 'ZOTERO_ITEM' in (e.text or ''): e.text = ' '; return
def m_dup_rev_id(root):
    ins = [e for e in root.iter() if local(e) == 'ins' and e.get(q('id'))]
    ins[1].set(q('id'), ins[0].get(q('id')))
def m_drop_row_del(root):  # 去掉一个行级删除标记 → 接受态多出一行
    for tp in root.iter(q('trPr')):
        d = tp.find(q('del'))
        if d is not None: tp.remove(d); return
    raise SystemExit('no row-level del found')

CASES = [
    ('D1_cell', 'content_patched', m_d1_cell, {'content_patched:tables_34_c14n_equal', 'D1:header_and_22_rows_cellwise_equal'}),
    ('P104', 'content_patched', m_p104, {'content_patched:P104_unchanged', 'content_patched:changed_paragraphs_c14n', 'content_patched:changed_paragraphs_text'}),
    ('P222_extra_change', 'accepted_offline', m_p222, {'accepted_offline:changed_paragraphs_c14n', 'accepted_offline:changed_paragraphs_text', 'projection_accept_text:word/document.xml'}),
    ('drop_citation', 'accepted_offline', m_drop_citation, {'accepted_offline:fields_all_stories_identical_order', 'accepted_offline:zotero_23_citations_1_bibliography', 'accepted_offline:changed_paragraphs_c14n'}),
    ('dup_revision_id', 'tracked_patched', m_dup_rev_id, {'tracked:revision_ids_unique_all_stories', 'tracked:diff_vs_raw_only_targets'}),
    # 首轮预测含 tracked:diff_vs_raw_only_targets 落空：该检查只比正文段落，不管表格——判据缺口已补为下列新检查
    ('drop_row_level_del', 'tracked_patched', m_drop_row_del, {'projection_accept_text:word/document.xml', 'tracked:tables_and_other_body_equal_raw'}),
]

def main():
    pack_new = {k: r.parts(r.MS / (k + '.docx')) for k in ('content_patched', 'tracked_patched', 'accepted_offline', 'rejected_offline')}
    old = {k: r.parts(r.PUB / (k + '.docx')) for k in ('content_patched', 'accepted_offline', 'rejected_offline')}
    bind = json.loads((r.MS / 'SOURCE_BINDINGS.json').read_text())
    mother = r.parts(bind['mother']['path']); raw = r.parts(bind['tracked_native_ids_fixed']['path'])
    base = run(pack_new, old, mother, raw)
    out = {'baseline_failures': sorted(base), 'cases': []}
    print('baseline failures:', sorted(base))
    for name, key, fn, predicted in CASES:
        new = copy.copy(pack_new); new[key] = dict(pack_new[key]); edit_doc(new[key], fn)
        got = run(new, old, mother, raw)
        ok = not base and predicted <= got
        out['cases'].append({'case': name, 'mutated': key, 'predicted_failures': sorted(predicted), 'actual_failures': sorted(got), 'predicted_all_hit': ok, 'extra_failures': sorted(got - predicted)})
        print(('HIT  ' if ok else 'MISS ') + name, 'predicted⊆actual' if ok else sorted(predicted - got), '| extra:', sorted(got - predicted))
    out['all_cases_hit'] = all(c['predicted_all_hit'] for c in out['cases'])
    (r.HERE / 'review_out' / 'NEGATIVE_CONTROLS.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print('all_cases_hit', out['all_cases_hit'])

if __name__ == '__main__':
    main()
