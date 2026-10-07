#!/usr/bin/env python3
"""Scoped Word lease recovery. Does not migrate brokers or settle NLM requests."""
from __future__ import annotations
import argparse
from contextlib import ExitStack, contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import time


class RecoveryError(RuntimeError):
    pass


def require(ok, reason):
    if not ok:
        raise RecoveryError(reason)


def pin(path):
    p = Path(path)
    require(p.is_absolute() and p.is_file() and not p.is_symlink(), 'ABSOLUTE_REGULAR_FILE_REQUIRED')
    data = p.read_bytes()
    return {'path': str(p), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


def read_pin(ref):
    require(pin(ref['path']) == ref, 'PIN_CHANGED:' + ref['path'])
    return json.loads(Path(ref['path']).read_text())


def save(path, obj):
    with Path(path).open('x') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.flush()
        os.fsync(f.fileno())


def live_identity():
    # 只读查询 caller；focused 不是执行者身份。
    a = json.loads(subprocess.check_output(['cmux', 'identify', '--json'], text=True, timeout=10))['caller']
    t = json.loads(subprocess.check_output(['cmux', 'tree', '--all', '--json', '--id-format', 'both'], text=True, timeout=10))['caller']
    require(a['surface_ref'] == t['surface_ref'] and a['workspace_ref'] == t['workspace_ref']
            and t['surface_type'] == 'terminal', 'CALLER_IDENTITY_UNKNOWN')
    return {'surface_uuid': t['surface_id'], 'workspace_uuid': t['workspace_id']}


def group_alive(pgid):
    if pgid is None:
        return False
    require(type(pgid) is int and pgid > 0, 'INVALID_PGID')
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


@contextmanager
def held_lock(ref):
    p = Path(ref['path'])
    require(p.is_absolute() and not p.is_symlink(), 'LOCK_PATH_INVALID')
    fd = os.open(p, os.O_RDWR | os.O_NOFOLLOW)
    try:
        st = os.fstat(fd)
        require(st.st_dev == ref['device'] and st.st_ino == ref['inode'], 'LOCK_IDENTITY_CHANGED')
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as ex:
            raise RecoveryError('ACTUAL_LOCK_BUSY:' + str(p)) from ex
        yield
    finally:
        os.close(fd)


def check_journals(contract, row):
    refs = contract['evidence']
    values = {ref['path']: read_pin(ref) for ref in refs}
    expected = set(values)
    # 完整目录集合校验，避免只挑已完成记录；根目录来自已审核恢复契约。
    discovered = set()
    for spec in contract['journal_sets']:
        root = Path(spec['root'])
        require(root.is_absolute() and root.is_dir(), 'JOURNAL_ROOT_INVALID')
        for pattern in spec['patterns']:
            discovered.update(str(f) for f in root.glob(pattern) if f.is_file())
    require(discovered == set(contract['journal_paths']) and discovered <= expected, 'JOURNAL_SET_CHANGED')
    terminal_paths = contract['terminal_paths']
    root = Path(contract['journal_root'])
    require(contract['journal_sets'] == [{'root': str(root), 'patterns': ['**/*.json']}], 'FULL_JOURNAL_SCOPE_REQUIRED')
    launches = {str(f) for f in (root/'launches').glob('*.json') if not f.name.endswith('.terminal.json')}
    pairs = {p: p[:-5]+'.terminal.json' for p in launches}
    for spec in contract.get('special_launches', []):
        require(spec['intent'] in discovered and spec['terminal'] in discovered, 'SPECIAL_LAUNCH_MISSING')
        pairs[spec['intent']] = spec['terminal']
        require(values[spec['terminal']].get('intent') == pin(spec['intent']), 'SPECIAL_INTENT_BINDING_CHANGED')
    require(set(pairs.values()) == set(terminal_paths), 'LAUNCH_COVERAGE_MISMATCH')
    for intent, terminal in pairs.items():
        require(terminal in values, 'PENDING_OUTER_LAUNCH')
        require(values[intent].get('ticket') == row['id'] and values[intent].get('task_id') == row['task_id'],
                'LAUNCH_OWNER_MISMATCH')
    require(len(terminal_paths) == row['invocations'] and len(set(terminal_paths)) == len(terminal_paths),
            'INVOCATION_COVERAGE_MISMATCH')
    for path in terminal_paths:
        r = values[path]
        require(r.get('ticket') == row['id'] and r.get('task_id') == row['task_id']
                and r.get('status') == 'PROCESS_EXITED' and type(r.get('exit_code')) is int
                and r.get('process_group_empty') is True, 'NONTERMINAL_INVOCATION')
        require(not group_alive(r.get('pgid')), 'OWNED_PROCESS_GROUP_ALIVE')
    intents = {p for p in discovered if p.endswith('.intent.json')}
    for path in intents:
        result_path = path[:-len('.intent.json')] + '.result.json'
        require(result_path in values and type(values[result_path].get('exit_code')) is int,
                'PENDING_NATIVE_INTENT')
    for path in discovered:
        if path.endswith('.process.json'):
            require(not group_alive(values[path].get('pgid')), 'OWNED_PROCESS_GROUP_ALIVE')
    # 由整套原始会话、契约和步骤记录提取归属，不能只信恢复调用者列出的路径。
    owned = set()
    def scan(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in ('owned', 'owned_document', 'owned_path'):
                    path = value.get('path') if isinstance(value, dict) else value
                    if isinstance(path, str) and path.endswith('.docx'):
                        require(Path(path).is_absolute(), 'OWNED_PATH_UNKNOWN')
                        owned.add(path)
                scan(value)
        elif isinstance(obj, list):
            for value in obj:
                scan(value)
    for path in discovered:
        scan(values[path])
    require(owned and owned == set(contract['owned_documents']), 'OWNED_SCOPE_INCOMPLETE')
    return {'invocations': len(terminal_paths), 'native_intents': len(intents), 'pinned_files': len(refs)}


def validate_observation(raw, contract, began):
    require(type(raw.get('observed_at')) in (int, float) and began <= raw['observed_at'] <= time.time()
            and time.time() - raw['observed_at'] <= 30, 'OBSERVATION_STALE')
    require(raw.get('read_only') is True and raw.get('complete') is True, 'OBSERVATION_UNKNOWN')
    require(type(raw.get('documents')) is int and raw['documents'] >= 0
            and type(raw.get('windows')) is int and raw['windows'] >= 0, 'WORD_COUNTS_UNKNOWN')
    docs = raw.get('document_inventory')
    require(isinstance(docs, list) and len(docs) == raw['documents'], 'DOCUMENT_INVENTORY_INCOMPLETE')
    owned = set(contract['owned_documents'])
    require(owned and all(Path(p).is_absolute() for p in owned), 'OWNED_SCOPE_REQUIRED')
    paths = []
    for d in docs:
        require(isinstance(d.get('path'), str) and Path(d['path']).is_absolute()
                and type(d.get('saved')) is bool, 'DOCUMENT_IDENTITY_UNKNOWN')
        paths.append(d['path'])
    require(len(paths) == len(set(paths)), 'DOCUMENT_IDENTITY_AMBIGUOUS')
    require(not owned.intersection(paths), 'TASK_DOCUMENT_STILL_OPEN')
    require(raw.get('zotero_dialog') is False, 'NATIVE_OPERATION_UNRESOLVED')
    foreign_modals = []
    if raw.get('modal') is not False:
        modals = raw.get('modal_inventory')
        allowances = contract.get('foreign_dialogs', [])
        require(type(raw.get('modal')) is bool and isinstance(modals, list) and modals
                and len(modals) == len(allowances), 'NATIVE_OPERATION_UNRESOLVED')
        unmatched = list(allowances)
        for modal in modals:
            matches = [a for a in unmatched if a['fingerprint'] == modal]
            require(len(matches) == 1, 'MODAL_OWNERSHIP_UNKNOWN')
            a = matches[0]
            request = read_pin(a['request'])
            require(request.get('actor_uuid') == a['waiter']['surface_uuid']
                    and a['waiter']['id'] != contract['lease']['id']
                    and a['waiter']['status'] == 'WAITING', 'FOREIGN_DIALOG_OWNER_MISMATCH')
            scope = Path(a['scope_path'])
            require(scope.is_absolute() and scope.parent == Path(a['request']['path']).parent
                    and str(scope) in modal['texts'] and not any(p in modal['texts'] for p in owned),
                    'FOREIGN_DIALOG_SCOPE_MISMATCH')
            require(modal['app'] == 'Microsoft Word' and modal['role'] == 'AXWindow'
                    and modal['subrole'] == 'AXDialog' and modal['modal'] is True
                    and modal['sheets'] in (0, 1), 'UNSUPPORTED_FOREIGN_DIALOG')
            children = modal.get('child_sheets', [])
            require(len(children) == modal['sheets'] and all(x == {'role': 'AXSheet'} for x in children),
                    'FOREIGN_SHEET_ANCESTRY_UNKNOWN')
            unmatched.remove(a)
            foreign_modals.append({'waiter_id': a['waiter']['id'], 'scope_path': str(scope),
                                   'action': 'left_untouched', 'fingerprint': modal})
    return {'owned_documents_open': 0, 'foreign_documents': docs,
            'global_documents': raw['documents'], 'global_windows': raw['windows'],
            'foreign_modals': foreign_modals, 'global_ui_ready': not bool(foreign_modals)}


def bounded_probe(argv, output):
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, start_new_session=True)
    save(output/'probe.process.json', {'pid': proc.pid, 'pgid': proc.pid, 'argv': argv, 'at': time.time()})
    try:
        stdout, stderr = proc.communicate(timeout=55)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGTERM)  # 只终止本次只读探针；不触碰 Word/Zotero。
        try:
            stdout, stderr = proc.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            stdout, stderr = proc.communicate()
        save(output/'probe.result.json', {'exit_code': 124, 'stdout': stdout, 'stderr': stderr,
                                         'remote_operation_settled': False})
        raise RecoveryError('READ_ONLY_PROBE_TIMEOUT')
    save(output/'probe.result.json', {'exit_code': proc.returncode, 'stdout': stdout, 'stderr': stderr})
    require(proc.returncode == 0 and not group_alive(proc.pid), 'READ_ONLY_PROBE_FAILED')
    return stdout


def parse_inventory(stdout):
    lines = [line.split('\t') for line in stdout.strip().splitlines()]
    require(lines and len(lines[0]) == 3 and lines[0][0] == 'WORD_INVENTORY_V2'
            and lines[-1] == ['END'], 'PROBE_PARSE_FAILED')
    docs = []
    for line in lines[1:-1]:
        require(len(line) == 3 and line[0] == 'DOC' and line[2] in ('true', 'false'), 'PROBE_PARSE_FAILED')
        docs.append({'path': line[1], 'saved': line[2] == 'true'})
    return {'documents': int(lines[0][1]), 'windows': int(lines[0][2]), 'document_inventory': docs}


def parse_ax(stdout):
    lines = [line.split('\t') for line in stdout.strip().splitlines()]
    require(lines and lines[0] == ['WORD_AX_V3'] and lines[-1] == ['END'], 'AX_PARSE_FAILED')
    require(len(lines) >= 3 and lines[1] == ['WORD_PROCESS', 'true'], 'AX_WORD_MISSING')
    windows = {}
    for line in lines[2:-1]:
        if line[0] == 'WIN':
            require(len(line) == 8 and line[1] in ('Microsoft Word', 'Zotero')
                    and line[2].isdigit() and int(line[2]) > 0
                    and line[7].isdigit() and line[6] in ('true', 'false'), 'AX_PARSE_FAILED')
            key = (line[1], line[2])
            require(key not in windows, 'AX_DUPLICATE_WINDOW')
            windows[key] = {'app': line[1], 'title': line[3], 'role': line[4], 'subrole': line[5],
                            'modal': line[6] == 'true', 'sheets': int(line[7]), 'texts': []}
        elif line[0] == 'SHEET':
            require(len(line) == 4 and (line[1], line[2]) in windows and line[3] == 'AXSheet', 'AX_SHEET_PARSE_FAILED')
            windows[(line[1], line[2])].setdefault('child_sheets', []).append({'role': 'AXSheet'})
        else:
            require(len(line) == 4 and line[0] == 'TEXT' and (line[1], line[2]) in windows, 'AX_PARSE_FAILED')
            windows[(line[1], line[2])]['texts'].append(line[3])
    for w in windows.values():
        require(len(w.get('child_sheets', [])) == w['sheets'], 'AX_SHEET_COUNT_MISMATCH')
    modals = [w for w in windows.values() if w['app'] == 'Microsoft Word'
              and (w['modal'] or w['subrole'] != 'AXStandardWindow' or w['sheets'] > 0)]
    zotero = any(w['app'] == 'Zotero' and (w['modal'] or w['subrole'] != 'AXStandardWindow'
                  or w['sheets'] > 0 or any(s in w['title'] for s in ('Citation', '引文', '文献引用')))
                 for w in windows.values())
    return {'modal': bool(modals), 'zotero_dialog': zotero, 'modal_inventory': modals,
            'ax_windows': list(windows.values())}


def word_observer(contract, output):
    script = Path(__file__).with_name('observe_word.applescript')
    ax = Path(__file__).with_name('observe_ax.applescript')
    require(pin(script) == contract['observer'] and pin(ax) == contract['ax_observer'], 'OBSERVER_CHANGED')
    def run(script, name):
        sub = output/name
        sub.mkdir()
        return bounded_probe(['/usr/bin/osascript', str(script)], sub)
    first = parse_inventory(run(script, 'inventory_before'))
    state = parse_ax(run(ax, 'accessibility_before'))
    last = parse_inventory(run(script, 'inventory_after'))
    state_after = parse_ax(run(ax, 'accessibility_after'))
    require(first == last and state == state_after, 'DOCUMENTS_CHANGED_DURING_OBSERVATION')
    return dict(last, observed_at=time.time(), read_only=True, complete=True, **state)


def _recover(contract_path, output, apply=False, *, identity=live_identity, observer=word_observer):
    """CLI uses fixed observers; injection is only an offline unit-test seam."""
    output = Path(output)
    require(output.is_absolute() and not output.exists(), 'FRESH_OUTPUT_REQUIRED')
    output.mkdir(parents=True)
    contract_ref = pin(contract_path)
    c = read_pin(contract_ref)
    require(c['schema'] == 'word-scoped-recovery-v1', 'SCHEMA_MISMATCH')
    require(pin(__file__) == c['implementation'], 'IMPLEMENTATION_CHANGED')
    require(c['lease']['resource'] == 'word-zotero', 'WORD_ONLY_NLM_QUARANTINE_UNCHANGED')
    auth = read_pin(c['authorization'])
    require(auth.get('authorized_by') == 'user' and auth.get('directive')
            and auth.get('scope') == 'expired-word-lease-recovery', 'EXPLICIT_AUTHORIZATION_REQUIRED')
    require(auth.get('ticket') == c['lease']['id'] and auth.get('actor') == c['actor']
            and auth.get('implementation') == c['implementation'] and auth.get('valid_until') == c['valid_until'],
            'AUTHORIZATION_BINDING_MISMATCH')
    require(time.time() <= c['valid_until'], 'RECOVERY_CONTRACT_EXPIRED')
    actor = identity()
    require(actor == c['actor'], 'RECOVERY_ACTOR_MISMATCH')
    save(output/'intent.json', {'contract': contract_ref, 'actor': actor, 'apply': apply, 'at': time.time()})
    db = sqlite3.connect(str(Path(c['resource_root'])/'queue.sqlite3'), timeout=10, isolation_level=None)
    db.row_factory = sqlite3.Row
    committed = False
    try:
        db.execute('BEGIN IMMEDIATE')
        found = db.execute('SELECT * FROM tickets WHERE id=?', (c['lease']['id'],)).fetchone()
        require(found is not None and dict(found) == c['lease'], 'LEASE_CHANGED')
        row = dict(found)
        require(row['status'] == 'ACTIVE' and row['expires'] <= time.time(), 'EXPIRED_ACTIVE_LEASE_REQUIRED')
        require(not group_alive(row['pgid']), 'OWNED_PROCESS_GROUP_ALIVE')
        config = dict(db.execute('SELECT * FROM resources WHERE name=?', (row['resource'],)).fetchone())
        require(config == c['resource_config'], 'RESOURCE_MAPPING_CHANGED')
        expected_paths = {str(Path(c['resource_root'])/(hashlib.sha256(row['resource'].encode()).hexdigest()+'.lock')),
                          *json.loads(config['external_locks']), c['focus_lock']}
        require(set(r['path'] for r in c['locks']) == expected_paths and len(c['locks']) == len(expected_paths),
                'LOCK_COVERAGE_MISMATCH')
        with ExitStack() as stack:
            for ref in c['locks']:
                stack.enter_context(held_lock(ref))
            require(identity() == actor, 'RECOVERY_ACTOR_CHANGED')
            for foreign in c.get('foreign_dialogs', []):
                actual = db.execute('SELECT * FROM tickets WHERE id=?', (foreign['waiter']['id'],)).fetchone()
                require(actual is not None and dict(actual) == foreign['waiter'], 'FOREIGN_WAITER_CHANGED')
            journal_summary = check_journals(c, row)
            began = time.time()
            obs = observer(c, output)
            save(output/'observation.json', obs)
            scoped = validate_observation(obs, c, began)
            # 保持所有真实锁直至事务提交；再次核日志，拒绝期间出现的新意图。
            require(check_journals(c, row) == journal_summary, 'JOURNALS_CHANGED_DURING_OBSERVATION')
            require(identity() == actor, 'RECOVERY_ACTOR_CHANGED')
            proof = {'schema': c['schema'], 'actor': actor, 'original_owner':
                     {k: row[k] for k in ['task_id', 'surface_uuid', 'workspace_uuid']},
                     'contract': contract_ref, 'observation': pin(output/'observation.json'),
                     'journal_summary': journal_summary, 'scope': scoped, 'pending': False,
                     'own_processes_empty': True, 'global_word_empty': obs['documents'] == 0,
                     'locks_held_through_commit': True, 'reconciled': True, 'at': time.time()}
            save(output/'decision.json', {'eligible': True, 'apply': apply, 'proof': proof})
            if apply:
                cur = db.execute("UPDATE tickets SET status='RELEASED',release_proof=? WHERE id=? AND status='ACTIVE' AND token=?",
                                 (json.dumps(proof, ensure_ascii=False), row['id'], row['token']))
                require(cur.rowcount == 1, 'LEASE_COMPARE_AND_SWAP_FAILED')
            db.execute('COMMIT')
            committed = True
        final = dict(db.execute('SELECT * FROM tickets WHERE id=?', (row['id'],)).fetchone())
        receipt = {'status': 'RELEASED' if apply else 'OBSERVED_ONLY', 'ticket': row['id'],
                   'actor': actor, 'database_status': final['status'], 'proof': proof}
        save(output/'COMMITTED.json', receipt)
        return receipt
    except BaseException as ex:
        if db.in_transaction:
            db.execute('ROLLBACK')
        # 提交后的回执写盘失败不能谎报回滚；数据库中的证明仍为权威。
        state = db.execute('SELECT status FROM tickets WHERE id=?', (c['lease']['id'],)).fetchone()
        try:
            save(output/('POST_COMMIT_ERROR.json' if committed else 'REFUSED.json'),
                 {'reason': str(ex), 'at': time.time(), 'committed': committed,
                  'database_status': state['status'] if state else None,
                  'released': bool(state and state['status'] == 'RELEASED')})
        except OSError:
            pass
        raise
    finally:
        db.close()


def recover(contract_path, output, apply=False, *, identity=live_identity, observer=word_observer):
    existed = Path(output).exists()
    try:
        return _recover(contract_path, output, apply, identity=identity, observer=observer)
    except BaseException as ex:
        out = Path(output)
        if not existed and out.is_dir() and not (out/'REFUSED.json').exists() and not (out/'POST_COMMIT_ERROR.json').exists():
            try:
                save(out/'REFUSED.json', {'reason': str(ex), 'at': time.time(), 'database_mutation_attempted': False})
            except OSError:
                pass
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contract', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    result = recover(args.contract, args.output, args.apply)
    print(json.dumps({'status': result['status'], 'ticket': result['ticket'], 'receipt': str(Path(args.output)/'COMMITTED.json')}))
