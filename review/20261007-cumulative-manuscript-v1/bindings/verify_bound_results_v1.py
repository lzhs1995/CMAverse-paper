#!/usr/bin/env python3
"""只核冻结文件与导出算术；任何不一致立即失败，不刷新 pins，不运行 R。"""
from pathlib import Path
import csv
import datetime
import hashlib
import json
import sys
import traceback
import numpy as np

C = Path(__file__).resolve().parent.parent
BIND = C / 'bindings'
OUT = C / 'results'
L = C.parent
S = L.parent
NC = L / 'numerical_closeout_20261006_v1'
ITEMS = []
DETAILS = {}
CURRENT = 'initialization'
PIN_MAP = {}


def read_csv(p):
    with Path(p).open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def read_json(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def digest(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda: f.read(1048576), b''):
            h.update(chunk)
    return h.hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def exact(actual, expected, label):
    require(actual == expected, f'{label}: {actual!r} != {expected!r}')


def close(actual, expected, label, atol=1e-11, rtol=1e-10):
    np.testing.assert_allclose(actual, expected, rtol=rtol, atol=atol,
                               equal_nan=False, err_msg=label)


def start(name):
    global CURRENT
    CURRENT = name


def passed(detail, **values):
    ITEMS.append(dict(check_id=CURRENT, status='PASS', detail=detail))
    if values:
        DETAILS[CURRENT] = values


def mapped(rows, keys):
    result = {tuple(r[k] for k in keys): r for r in rows}
    exact(len(result), len(rows), f'duplicate keys {keys}')
    return result


def source_pin(path):
    path = str(Path(path).resolve())
    require(path in PIN_MAP, f'unpinned source: {path}')
    return PIN_MAP[path]


def adjustment(p):
    p = np.asarray(p, dtype=float)
    m = len(p)
    order = np.argsort(p, kind='stable')
    bh = np.empty(m)
    bh[order] = np.minimum(1, np.minimum.accumulate(
        (p[order] * m / np.arange(1, m + 1))[::-1])[::-1])
    by = np.minimum(1, bh * np.sum(1 / np.arange(1, m + 1)))
    return bh, by


def main():
    global PIN_MAP
    start('SOURCE_FILE_HASHES')
    pins = read_json(BIND / 'SOURCE_PINS.json')
    exact(len(pins), 288, 'frozen pin count')
    PIN_MAP = {p['path']: p for p in pins}
    exact(len(PIN_MAP), len(pins), 'pin uniqueness')
    for p in pins:
        path = Path(p['path'])
        require(path.is_file(), f'missing pinned file: {path}')
        exact(str(path.resolve()), p['path'], 'resolved source path')
        exact(path.stat().st_size, int(p['bytes']), f'source bytes {path}')
        exact(digest(path), p['sha256'], f'source hash {path}')
    passed('288 frozen source files match saved SHA256 and bytes; pins never refreshed.',
           count=len(pins), total_bytes=sum(p['bytes'] for p in pins))

    start('HISTORICAL_COVERAGE_AND_NATIVE_RECEIPT')
    coverage = read_csv(NC / 'search_audit/COVERAGE_150.csv')
    registry = read_csv(NC / 'search_audit/ALL_150_REGISTER.csv')
    index = read_csv(NC / 'search_audit/INDEX_AUDIT.csv')
    rw = read_csv(NC / 'search_audit/RW_ALL_240.csv')
    exact(len(coverage), 150, 'registered coverage')
    reg_map = mapped(registry, ['spec_id'])
    exact(len(reg_map), 150, 'registry uniqueness')
    exact({r['spec_id'] for r in coverage}, {k[0] for k in reg_map}, 'coverage ids')
    eligible = {r['spec_id'] for r in coverage if r['verified'] == 'TRUE'}
    exact(len(eligible), 120, 'estimable coverage')
    exact(len(mapped(index, ['spec_id'])), 120, 'index row count')
    exact({r['spec_id'] for r in index}, eligible, 'index coverage')
    exact(set(mapped(rw, ['spec_id', 'metric'])),
          {(s, m) for s in eligible for m in ['TNIE', 'Delta_CDE']}, '240 target coverage')
    receipt = read_json(NC / 'native/search_terminal.json')
    require(receipt.get('isError') is False, 'native search isError')
    receipt_text = '\n'.join(x.get('text', '') for x in receipt['content'])
    require('SEARCH_ARITHMETIC_AND_INDEX_AUDIT_PASS' in receipt_text, 'native search PASS absent')
    require('job_id=d128f101;' in receipt_text, 'native search job changed')
    passed('150 registered / 120 estimable / 240 B200 targets; accepted native job d128f101 retained.')

    start('ACTUAL_120_EXECUTION_INPUTS')
    proof = read_json(S / 'selection_inputs_complete_v1/SOURCE_PROOFS.json')
    actual = read_json(BIND / 'EXECUTION_INPUTS_120.json')
    actual_csv = read_csv(BIND / 'EXECUTION_INPUTS_120.csv')
    by_id = mapped(actual, ['spec_id'])
    exact(len(actual), 120, 'execution inputs count')
    exact(set(by_id), {(s,) for s in eligible}, 'execution inputs ids')
    exact(len(actual_csv), len(actual), 'execution csv coverage')
    for row, expected_json in zip(actual_csv, actual):
        for key, value in expected_json.items():
            exact(row[key], str(value), f'execution csv mirror {key}')
    audit_pin = source_pin(NC / 'search_audit/INDEX_AUDIT.csv')
    total_bytes = 0
    for r in index:
        spec = r['spec_id']
        p = proof[spec]
        expected_path = (Path(p['validation']['path']).parent / spec / 'execution_inputs.rds').resolve()
        bound = by_id[(spec,)]
        require(r['execution_present'] == r['indices_and_seeds_match'] == 'TRUE', f'old R audit {spec}')
        exact(bound['path'], str(expected_path), f'execution path {spec}')
        for key in ['bytes', 'sha256']:
            exact(bound[key], source_pin(expected_path)[key], f'execution {key} {spec}')
        exact(bound['sha256'], r['execution_sha256'], f'execution vs old audit {spec}')
        exact(bound['accepted_index_audit_path'], audit_pin['path'], f'audit path {spec}')
        exact(bound['accepted_index_audit_sha256'], audit_pin['sha256'], f'audit hash {spec}')
        exact(bound['indices_and_seeds_match_reused'], True, f'reused annotation {spec}')
        mp = source_pin(p['metrics']['path'])
        exact(bound['metrics_path'], mp['path'], f'metrics path {spec}')
        exact(bound['metrics_sha256'], mp['sha256'], f'metrics bound hash {spec}')
        exact(bound['metrics_bytes'], mp['bytes'], f'metrics bound bytes {spec}')
        exact(mp['sha256'], r['metrics_sha256'], f'metrics vs old audit {spec}')
        exact(mp['sha256'], p['metrics']['sha256'], f'metrics vs original proof {spec}')
        total_bytes += bound['bytes']
    exact(total_bytes, 197603909, '120 inputs bytes')
    passed('Fresh whole-file hashes for 120 actual execution_inputs.rds and 120 METRICS.rds; accepted R row-index/seed audit reused, not rerun.',
           files=120, bytes=total_bytes, new_R_index_audits=0)

    start('RESULT_TABLE_MANIFEST_AND_PROVENANCE')
    manifest = read_csv(OUT / 'RESULT_VERSION_TABLE.csv')
    table_names = {'CANDIDATE_DEFINITIONS.csv', 'CANDIDATE_HISTORY_PANELS.csv',
                   'CANDIDATE_PERIOD_DIAGNOSTICS.csv', 'CANDIDATE_LOO_SUMMARY.csv',
                   'P3_THREE_STATE.csv', 'P3_OMNIBUS.csv', 'SIX_TEST_FAMILY.csv',
                   'N1_FOUR_WITH_FINAL_SIX_ADJUSTMENT.csv'}
    exact({Path(r['table_path']).name for r in manifest}, table_names, 'table manifest set')
    exact(len(manifest), 8, 'table manifest rows')
    for r in manifest:
        path = Path(r['table_path'])
        exact(path.parent.resolve(), OUT.resolve(), 'result must be in assigned directory')
        exact(path.stat().st_size, int(r['bytes']), 'result bytes')
        exact(digest(path), r['sha256'], 'result SHA256')
        rows = read_csv(path)
        exact(len(rows), int(r['rows']), 'result row count')
        for row in rows:
            pin = source_pin(row['source_path'])
            exact(row['source_sha256'], pin['sha256'], 'result source hash')
            exact(int(row['source_bytes']), pin['bytes'], 'result source bytes')
            require(bool(row['source_row']), 'source row locator missing')
            if 'family_source_path' in row:
                exact(row['family_source_sha256'], source_pin(row['family_source_path'])['sha256'], 'family source hash')
            if 'transform_source' in row:
                exact(row['transform_source_sha256'], source_pin(row['transform_source'])['sha256'], 'transform source hash')
    passed('8 data tables + version table; every row has a valid pinned source path/hash/bytes and row locator.')

    start('CANDIDATE_DEFINITION_MAPPING')
    definitions = read_csv(OUT / 'CANDIDATE_DEFINITIONS.csv')
    exact({r['spec_id'] for r in definitions}, {'FEAS_031', 'FEAS_041'}, 'candidate ids')
    for r in definitions:
        q = reg_map[(r['spec_id'],)]
        for target, source in dict(a='a', astar='astar', m_low='mval0', m_high='mval1',
                                   N='n', clusters='clusters', x_code='x', m_code='m', y_code='y',
                                   adjustment_registered='adjustment', time_structure='time_structure',
                                   conditional_support_caveat='support_note').items():
            exact(r[target], q[source], f'definition registry mapping {target}')
        exact(r['x_code'], 'abs_increase', 'X definition')
        exact(r['y_code'], 'support_increase', 'Y definition')
        exact(r['m_code'], {'FEAS_031': 'self_relative_transition',
                           'FEAS_041': 'self_relative_gap_diff'}[r['spec_id']], 'M definition')
        exact(r['source_row'], r['spec_id'], 'candidate source row')
        require('not probability points' in r['scale'], 'OR difference scale caveat absent')
    passed('Both candidate codes, fixed contrasts, N/clusters, old adjustment and timing caveat match the saved registry; source transforms pinned.')

    start('HISTORICAL_B200_INDEPENDENT_ARITHMETIC')
    values_path = NC / 'search_audit/BOOTSTRAP_TEST_VALUES.csv'
    with values_path.open() as f:
        header = next(csv.reader(f))
    exact(header, [r['spec_id'] + '__' + r['metric'] for r in rw], 'draw column alignment')
    x = np.loadtxt(values_path, delimiter=',', skiprows=1)
    exact(x.shape, (200, 240), 'draw matrix shape')
    require(bool(np.isfinite(x).all()), 'nonfinite B200 draws')
    point = np.array([float(r['point_test_scale']) for r in rw])
    sd = x.std(axis=0, ddof=1)
    require(bool((sd > 0).all()), 'zero B200 SD')
    observed = np.abs(point) / sd
    centered = np.abs(x - point)
    draw_stat = centered / sd
    raw = (1 + (centered >= np.abs(point)).sum(axis=0)) / 201
    close(sd, [float(r['se_bootstrap']) for r in rw], 'B200 SD')
    close(raw, [float(r['p_centered']) for r in rw], 'B200 raw p', atol=1e-12)

    def stepdown(cols):
        order = np.asarray(cols)[np.argsort(-observed[cols], kind='stable')]
        out = np.full(len(rw), np.nan)
        previous = 0.
        for k, target in enumerate(order):
            p = (1 + np.count_nonzero(draw_stat[:, order[k:]].max(axis=1) >= observed[target])) / 201
            previous = max(previous, p)
            out[target] = previous
        return out

    all_adjusted = stepdown(np.arange(240))
    close(all_adjusted, [float(r['p_RW_all240']) for r in rw], 'RW 240', atol=1e-12)
    for metric in ['TNIE', 'Delta_CDE']:
        ids = np.array([i for i, r in enumerate(rw) if r['metric'] == metric])
        exact(len(ids), 120, 'RW within-family size')
        close(stepdown(ids)[ids], [float(rw[i]['p_RW_within_metric']) for i in ids],
              'RW within ' + metric, atol=1e-12)
    passed('Recomputed 240 SDs/raw centered p values, two 120-target RW families and all-240 RW from the 200×240 frozen matrix; no fits or new tests.',
           B=200, targets=240, minimum_all240=float(all_adjusted.min()))

    start('CANDIDATE_HISTORY_VERSION_SEPARATION')
    panels = read_csv(OUT / 'CANDIDATE_HISTORY_PANELS.csv')
    exact(len(panels), 20, 'candidate history row count')
    exact(len(mapped(panels, ['panel_id', 'spec_id', 'model_version', 'metric'])), 20, 'history uniqueness')
    rw_map = mapped(rw, ['spec_id', 'metric'])
    for r in panels:
        panel = r['panel_id']
        if panel == 'A_B200_SEARCH':
            q = rw_map[(r['spec_id'], r['metric'])]
            exact(r['B'], '200', 'search B')
            exact(r['model_version'], 'original_with_dwm', 'search model')
            pairs = dict(estimate='point_test_scale', p_raw='p_centered',
                         p_RW_within120='p_RW_within_metric', p_RW_all240='p_RW_all240')
            exact(r['estimate_scale'], 'log_OR' if r['metric'] == 'TNIE' else 'marginal_OR_difference', 'search scale')
            exact(r['ci_lower'] + r['ci_upper'], '', 'no fabricated B200 CI')
        elif panel == 'B_B1000_LEGACY':
            q = mapped(read_csv(r['source_path']), ['metric'])[(r['metric'],)]
            exact(r['B'], '1000', 'legacy B')
            exact(r['model_version'], 'original_with_dwm', 'legacy model')
            pairs = dict(estimate='estimate', ci_lower='ci_low', ci_upper='ci_high', p_raw='p_exploratory')
            exact(r['estimate_scale'], 'OR' if r['metric'] == 'TNIE' else 'marginal_OR_difference', 'legacy scale')
        else:
            require(panel in ['C_B1000_CENTERED_INTERVAL', 'D_PAIRED_CHANGE'], 'unknown history panel')
            version = {'original_with_dwm': 'old', 'revised_without_dwm': 'revised',
                       'revised_minus_original': 'paired'}[r['model_version']]
            q = mapped(read_csv(r['source_path']), ['version', 'metric'])[(version, r['metric'])]
            exact(r['B'], q['planned_B'], 'interval B')
            exact(r['inference_version'], q['interval_status'], 'interval status')
            exact(r['p_raw'], '', 'interval-only p must remain empty')
            exact(panel == 'D_PAIRED_CHANGE', version == 'paired', 'paired panel')
            expected_scale = ('OR' if version != 'paired' else 'OR_difference') if r['metric'] == 'TNIE' else 'marginal_OR_difference'
            exact(r['estimate_scale'], expected_scale, 'interval/paired scale')
            pairs = dict(estimate='estimate', ci_lower='lower', ci_upper='upper')
        for target, source in pairs.items():
            exact(r[target], q[source], f'{panel} copied {target}')
        if panel != 'A_B200_SEARCH':
            exact(r['p_RW_within120'] + r['p_RW_all240'], '', 'B200 RW must not migrate')
    passed('20 rows retain B200 log-OR TNIE, B1000 OR TNIE, OR differences and interval-only rows separately; no p transplant.')

    start('PERIOD_AND_LOO_SUMMARIES')
    periods = read_csv(OUT / 'CANDIDATE_PERIOD_DIAGNOSTICS.csv')
    exact(len(periods), 4, 'two periods each candidate')
    for r in periods:
        q = mapped(read_csv(r['source_path']), ['unit'])[(r['period'],)]
        for target, source in dict(N='n', clusters='clusters', Delta_OR='Delta_OR',
                                   Delta_probability='Delta_probability', valid='valid', formula='formula').items():
            exact(r[target], q[source], f'period {target}')
        require(float(r['Delta_OR']) < 0 and r['valid'] == 'TRUE', 'period sign/validity')
    loo = read_csv(OUT / 'CANDIDATE_LOO_SUMMARY.csv')
    exact(len(loo), 2, 'LOO candidate count')
    for r in loo:
        q = read_csv(r['source_path'])
        exact(len(q), int(reg_map[(r['spec_id'],)]['clusters']), 'full LOO coverage')
        exact(len(mapped(q, ['unit'])), len(q), 'distinct omitted clusters')
        require(all(x['valid'] == 'TRUE' for x in q), 'LOO validity')
        max_row = max(q, key=lambda x: float(x['change_fraction_revised']))
        exact(int(r['omitted_cluster_runs']), len(q), 'LOO row count')
        exact(r['max_change_unit'], max_row['unit'], 'LOO maximum cluster')
        exact(r['Delta_OR_at_max'], max_row['Delta_OR'], 'LOO maximum Delta OR')
        close(float(r['max_relative_change']), float(max_row['change_fraction_revised']), 'LOO maximum fraction')
        close(float(r['max_relative_change_percent']), 100 * float(max_row['change_fraction_revised']), 'LOO percent')
        exact(r['all_same_negative_sign'], str(all(float(x['Delta_OR']) < 0 for x in q)), 'LOO signs')
    passed('Four period diagnostics and all 2,939 + 3,149 leave-one-cluster point diagnostics reduce exactly to the saved summaries; no new per-period/LOO inference.')

    start('P3_COMPLETE_PAIRED_DRAWS_AND_DIAGNOSTICS')
    draws = read_csv(NC / 'exports/P3_ALL_6000_DRAWS.csv')
    diagnostics = read_csv(NC / 'exports/P3_ALL_6000_DIAGNOSTICS.csv')
    d_map = mapped(draws, ['draw', 'component'])
    g_map = mapped(diagnostics, ['draw', 'component'])
    expected = {(str(i), k) for i in range(1, 2001) for k in ['probability', 'original', 'capped']}
    exact(set(d_map), expected, 'P3 draw coverage')
    exact(set(g_map), expected, 'P3 diagnostic coverage')
    for i in range(1, 2001):
        same = {d_map[(str(i), k)]['draw_sha256'] for k in ['probability', 'original', 'capped']}
        exact(len(same), 1, 'P3 common draw hash')
        require(len(next(iter(same))) == 64, 'P3 draw hash length')
    for key, r in d_map.items():
        vals = np.array([float(r[k]) for k in ['T_le3', 'T_4', 'T_5', 'd_5vle3', 'd_5v4']])
        require(bool(np.isfinite(vals).all()), f'nonfinite P3 draw {key}')
        close(vals[3:], [vals[2] - vals[0], vals[2] - vals[1]], 'P3 draw differences', atol=1e-9)
        diag = g_map[key]
        exact(diag['ok'], 'TRUE', 'P3 successful draw')
        exact(diag['error'], '', 'P3 error empty')
        if key[1] != 'probability':
            exact(diag['converged'], 'TRUE', 'P3 amount converged')
            exact(diag['rank'], diag['columns'], 'P3 amount full rank')
            require(np.isfinite(float(diag['gradient'])) and float(diag['hessian_min']) > 0,
                    'P3 finite gradient / positive Hessian')
    acceptance = read_json(NC / 'exports/ACCEPTANCE.json')
    require(acceptance['status'] == 'PASS' and acceptance['draws'] == 2000 and
            acceptance['effect_rows'] == 6000 and acceptance['index_exact'] is True,
            'accepted P3 R receipt inconsistent')
    passed('All 6,000 rows finite/complete; each of 2,000 replicates shares one hash across three components; 4,000 amount fits have saved convergence/full-rank evidence. R index identity is reused from accepted receipt.')

    start('P3_POINT_DIFFERENCES_AND_OMNIBUS')
    points = mapped(read_csv(NC / 'exports/P3_POINTS.csv'), ['component'])
    tests = mapped(read_csv(NC / 'exports/P3_OMNIBUS.csv'), ['component'])
    estimates = read_csv(OUT / 'P3_THREE_STATE.csv')
    exact(len(estimates), 3, 'P3 point components')
    calculations = []
    for r in estimates:
        q = points[(r['component'],)]
        for key, value in q.items():
            exact(r[key], value, f'P3 point copied {key}')
        close([float(r['d_5vle3']), float(r['d_5v4'])],
              [float(r['T_5']) - float(r['T_le3']), float(r['T_5']) - float(r['T_4'])], 'P3 point differences')
        exact(r['unit'], 'probability' if r['component'] == 'probability' else 'yuan_per_month', 'P3 unit')
    for component in ['original', 'capped']:
        cols = ['d_5vle3', 'd_5v4']
        mat = np.array([[float(d_map[(str(i), component)][k]) for k in cols] for i in range(1, 2001)])
        point = np.array([float(points[(component,)][k]) for k in cols])
        cov = np.cov(mat, rowvar=False, ddof=1)
        require(bool((np.linalg.eigvalsh(cov) > 0).all()), 'P3 covariance positive definite')
        inv = np.linalg.inv(cov)
        statistic = float(point @ inv @ point)
        centered = mat - point
        sim = np.einsum('ij,jk,ik->i', centered, inv, centered)
        tail = int(np.count_nonzero(sim >= statistic))
        p = (1 + tail) / 2001
        q = tests[(component,)]
        close(statistic, float(q['statistic']), 'P3 quadratic statistic')
        exact(tail, int(q['tail_count']), 'P3 tail count')
        close(p, float(q['p_raw']), 'P3 omnibus p', atol=1e-12)
        exact(q['B'], q['n_valid'], 'P3 valid B')
        exact(q['B'], '2000', 'P3 fixed B')
        calculations.append(dict(component=component, covariance=cov.tolist(),
                                 statistic=statistic, tail_count=tail, p_raw=p))
    passed('Three-state differences and both centered 2-df quadratic tail counts reproduced from frozen paired draws; no new adjacent-contrast p values.', calculations=calculations)

    start('SIX_TEST_BH_BY_AND_N1_PRESERVATION')
    family = read_csv(NC / 'exports/SIX_TEST_FAMILY.csv')
    f_map = mapped(family, ['test_id'])
    n1_path = L / 'n1_n2/runtime_v2/N1_formal_v3/N1_primary_four.csv'
    n1 = mapped(read_csv(n1_path), ['test_id'])
    exact(len(family), 6, 'family denominator')
    exact(set(f_map), set(n1) | {('P3_ORIGINAL',), ('P3_CAPPED',)}, 'six family members')
    for key, q in n1.items():
        exact(f_map[key]['p_raw'], q['p_raw'], 'N1 unchanged raw p')
    for q in tests.values():
        exact(f_map[(q['test_id'],)]['p_raw'], q['p_raw'], 'family P3 raw p')
    bh, by = adjustment([float(r['p_raw']) for r in family])
    close(bh, [float(r['q_BH6']) for r in family], 'six BH', atol=1e-12)
    close(by, [float(r['q_BY6']) for r in family], 'six BY', atol=1e-12)
    n1_output = read_csv(OUT / 'N1_FOUR_WITH_FINAL_SIX_ADJUSTMENT.csv')
    exact(len(n1_output), 4, 'N1 output coverage')
    for r in n1_output:
        q = n1[(r['test_id'],)]
        for key, value in q.items():
            if key not in ['q_BH6', 'q_BY6', 'global6_status']:
                exact(r[key], value, 'N1 preserved ' + key)
        for key in ['q_BH6', 'q_BY6']:
            exact(r[key], f_map[(r['test_id'],)][key], 'N1 completed ' + key)
        exact(r['global6_status'], 'COMPLETE_USING_NUMERICAL_CLOSEOUT_P3', 'N1 completed family annotation')
    for filename, source in [('SIX_TEST_FAMILY.csv', family), ('P3_OMNIBUS.csv', list(tests.values()))]:
        original = mapped(source, ['test_id'])
        output = read_csv(OUT / filename)
        exact(len(output), len(source), 'direct table length')
        for r in output:
            for key, value in original[(r['test_id'],)].items():
                exact(r[key], value, filename + ' source value ' + key)
    passed('Six actual raw p values reproduce BH/BY; all original N1 coefficients, SE, CI, raw p and within-four q preserved. Only final six-family fields filled.',
           BH_rejections_05=int(np.count_nonzero(bh < .05)), BY_rejections_05=int(np.count_nonzero(by < .05)))

    start('SCOPE_LIMITS')
    scope = read_json(BIND / 'SCOPE.json')
    for key in ['new_models', 'new_R_index_audits', 'new_hypothesis_tests', 'microdata_copies']:
        exact(scope[key], 0, key)
    exact(scope['execution_input_files'], 120, 'scope input files')
    exact(scope['source_pin_count'], 288, 'scope pin count')
    passed('No fitting, R execution, new hypotheses, microdata copies, UI, publication, queue or broker mutation by this verifier.')


def save_outputs(status, error=None):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    report = dict(status=status, created_at=now, checks=len(ITEMS),
                  failed_check=CURRENT if status != 'PASS' else None, error=error,
                  verification='fresh file hashes and independent arithmetic from frozen CSV exports',
                  reused_evidence='accepted native R row-index/replicate-seed audits; not newly rerun',
                  limitations=['No independent model refit or new model',
                               'No general FWER or mediation-null calibration proof',
                               'No independent statistical confirmation of selected candidates',
                               'No removal of remaining covariate timing / OR noncollapsibility caveats',
                               'Word/PDF/NLM/publication acceptance outside this scope'],
                  details=DETAILS)
    (BIND / 'QA.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    with (BIND / 'QA_ITEMS.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['check_id', 'status', 'detail'])
        w.writeheader()
        w.writerows(ITEMS)
    lines = ['# 冻结统计结果与来源绑定核验', '',
             f'状态：**{status}**。UTC：{now}。核验项：{len(ITEMS)}。', '',
             '本轮独立重算冻结 CSV 的检验算术，并新鲜核对 288 个源文件的 SHA256 与字节数。',
             '120 份 execution_inputs.rds 合计 197,603,909 字节；120 份 METRICS.rds 同时与原 proof 和原 R 审计绑定。',
             '原 R 对共同簇计划、实际行索引、replicate seeds 的核验沿用已接受的 native job d128f101；本轮没有重做 R 索引审计或模型拟合。', '',
             '| 核验 | 结果 | 说明 |', '|---|---|---|']
    lines += [f"| {i['check_id']} | {i['status']} | {i['detail'].replace('|', '/')} |" for i in ITEMS]
    lines += ['', '解释边界：B200 搜索校正只属于原模型；历史 B1000 原始 p 与百分位区间单列；去 dwm 的中心化区间和配对变化没有新增 p。TNIE 的 log-OR、OR 和配对 OR 差分别标注。',
              '', 'FEAS_031/041 的原始显著修饰线索继续保留，不能视为校正后确认。P3 原金额/封顶的整体 p 分别为 0.131934032983508 / 0.079960019990005。新六项族 BH/BY 在 0.05 均无拒绝。',
              '', '分期和逐簇删除为点诊断；N1 是人际/个人内关联，不自动等于婚姻满意度中介或调节。共同抽样和算术一致性不证明一般零假设校准。',
              '', '结果表在相邻 results/，每行携带源路径、SHA256、字节数和定位键。RESULT_VERSION_TABLE.csv 固定八张内容表；OUTPUT_MANIFEST.json 固定本轮全部绑定与核验文件。',
              '', '本验收不包含 Word/PDF 原生验收、同版 NLM 终审和 GitHub 发布。']
    if error:
        lines += ['', '失败证据：', '```text', error, '```']
    (BIND / 'REPORT.md').write_text('\n'.join(lines) + '\n')
    files = sorted(set(OUT.glob('*.csv')) | {BIND / n for n in [
        'build_bound_tables_v1.py', 'verify_bound_results_v1.py', 'SOURCE_PINS.json',
        'EXECUTION_INPUTS_120.json', 'EXECUTION_INPUTS_120.csv', 'SCOPE.json',
        'QA.json', 'QA_ITEMS.csv', 'REPORT.md']})
    out_manifest = dict(status=status, created_at=now, files=[
        dict(path=str(p), bytes=p.stat().st_size, sha256=digest(p)) for p in files])
    (BIND / 'OUTPUT_MANIFEST.json').write_text(json.dumps(out_manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(status=status, checks=len(ITEMS), failed_check=report['failed_check'],
                          QA=str(BIND / 'QA.json'), REPORT=str(BIND / 'REPORT.md')), ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        error = traceback.format_exc()
        ITEMS.append(dict(check_id=CURRENT, status='FAIL', detail=error.splitlines()[-1]))
        save_outputs('FAIL', error)
        sys.exit(1)
    save_outputs('PASS')
