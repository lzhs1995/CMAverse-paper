#!/usr/bin/env python3
"""只读核对父代理表格证据；不修改稿件，不执行原生 Word。"""
from pathlib import Path
import csv
import datetime
import hashlib
import json

C = Path(__file__).resolve().parent.parent
SOURCE = C / 'manuscript/EVIDENCE_TABLES.json'
EXPECTED_TABLES = ['CANDIDATE_DEFINITIONS.csv', 'CANDIDATE_HISTORY_PANELS.csv',
                   'P3_THREE_STATE.csv', 'P3_OMNIBUS.csv']


def pin(p):
    return dict(path=str(p), bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def read_csv(n):
    with (C / 'results' / n).open() as f:
        return list(csv.DictReader(f))


def fmt(x, d):
    return f'{float(x):.{d}f}'.replace('-', '−')


def require(condition, message):
    if not condition:
        raise AssertionError(message)


before = [pin(SOURCE)] + [pin(C / 'results' / n) for n in EXPECTED_TABLES]
e = json.loads(SOURCE.read_text())
h = read_csv('CANDIDATE_HISTORY_PANELS.csv')
d = read_csv('CANDIDATE_DEFINITIONS.csv')
ps = read_csv('P3_THREE_STATE.csv')
om = read_csv('P3_OMNIBUS.csv')
checks = []
for column, spec in [(1, 'FEAS_031'), (2, 'FEAS_041')]:
    q = next(x for x in d if x['spec_id'] == spec)
    require(e['table11'][4][column] == q['N'] + '／' + q['clusters'], 'N/cluster mismatch')
    v = next(x for x in h if x['spec_id'] == spec and x['model_version'] == 'revised_without_dwm' and x['metric'] == 'Delta_OR')
    require(e['table11'][5][column] == fmt(v['estimate'], 3), 'revised Delta_OR mismatch')
    require(e['table11'][6][column] == '[' + fmt(v['ci_lower'], 3) + '，' + fmt(v['ci_upper'], 3) + ']', 'revised CI mismatch')
    checks.append(spec + ' table11 N/clusters/revised DeltaOR/CI exact rounding')
for k, (panel, spec) in enumerate([('A_B200_SEARCH', 'FEAS_031'), ('A_B200_SEARCH', 'FEAS_041'),
                                    ('B_B1000_LEGACY', 'FEAS_031'), ('B_B1000_LEGACY', 'FEAS_041')], 1):
    v = next(x for x in h if x['panel_id'] == panel and x['spec_id'] == spec and x['metric'] in ['Delta_CDE', 'Delta_OR'])
    require(e['table12'][k][1] == fmt(v['p_raw'], 6), 'historical raw p mismatch')
    require(e['table12'][k][2] == (fmt(v['p_RW_within120'], 6) if v['p_RW_within120'] else '未计算'), 'RW within version mismatch')
    require(e['table12'][k][3] == (fmt(v['p_RW_all240'], 6) if v['p_RW_all240'] else '未计算'), 'RW all version mismatch')
    checks.append(spec + ' ' + panel + ' table12 exact p and version separation')
for i, component in [(1, 'original'), (2, 'capped')]:
    q = next(x for x in ps if x['component'] == component)
    o = next(x for x in om if x['component'] == component)
    expected = [fmt(q[k], 2) for k in ['T_le3', 'T_4', 'T_5', 'd_5vle3', 'd_5v4']] + [fmt(o['p_raw'], 3)]
    require(e['table13'][i][1:] == expected, 'P3 table13 numeric mismatch')
    checks.append(component + ' table13 three states/two differences/omnibus exact rounding')
require('历史搜索校正未显著' in e['table10'][3][2], 'table10 search caveat')
require('固定六项调整后均未显著' in e['table10'][6][2], 'table10 N1 caveat')
require('不能替代中介／修饰' in e['table10'][6][3], 'table10 association caveat')
require('不等于独立复制' in e['table10'][7][3], 'table10 replication caveat')
checks.append('table10 search/family/association/replication caveats retained')
after = [pin(SOURCE)] + [pin(C / 'results' / n) for n in EXPECTED_TABLES]
require(before == after, 'source changed during readback')
result = dict(status='PASS', created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              checks=checks, files=before, verifier=pin(Path(__file__).resolve()),
              scope='EVIDENCE_TABLES.json numeric/version readback only; not DOCX native acceptance')
output = C / 'bindings/MANUSCRIPT_TABLE_READBACK.json'
output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(status='PASS', checks=len(checks), evidence=str(output)), ensure_ascii=False))
