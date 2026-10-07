import copy
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import resource_recovery as r

LEGACY = Path('/Users/lzhs/.local/share/multi-agent-collaboration/releases/0.1.2-callback138-0996f3030702/source/scripts')
sys.path.insert(0, str(LEGACY))
from resource_broker import Broker, ResourceBusy


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.b = Broker(self.root)
        self.addCleanup(self.b.db.close)
        self.ext = self.root/'word.lock'; self.ext.touch()
        self.focus = self.root/'focus.lock'; self.focus.touch()
        self.b.configure('word-zotero', [str(self.ext)])
        self.actor = {'workspace_uuid':'22222222-2222-4222-8222-222222222222', 'surface_uuid':'33333333-3333-4333-8333-333333333333'}
        t = self.b.request('word-zotero','old-task','44444444-4444-4444-8444-444444444444','55555555-5555-4555-8555-555555555555')
        self.lease = self.b.grant(t['id'])
        self.b.db.execute('UPDATE tickets SET expires=?,invocations=1 WHERE id=?',(time.time()-1,t['id']))
        self.lease = self.b.get(t['id'])
        self.waiter = self.b.request('word-zotero','next',self.actor['workspace_uuid'],self.actor['surface_uuid'])
        self.j = self.root/'journal'; (self.j/'launches').mkdir(parents=True)
        r.save(self.j/'launches/a.json', {'ticket':t['id'],'task_id':'old-task'})
        r.save(self.j/'launches/a.terminal.json', {'ticket':t['id'],'task_id':'old-task','status':'PROCESS_EXITED','exit_code':1,'process_group_empty':True,'pgid':None})
        r.save(self.j/'SESSION.json', {'owned_document':'/task/owned.docx'})
        self.c = {'schema':'word-scoped-recovery-v1','implementation':r.pin(r.__file__), 'observer':r.pin(Path(r.__file__).with_name('observe_word.applescript')),
                  'lease':self.lease, 'actor':self.actor,'valid_until':time.time()+300,'resource_root':str(self.root),
                  'resource_config':dict(self.b.db.execute('SELECT * FROM resources').fetchone()),'focus_lock':str(self.focus),
                  'locks':[], 'journal_root':str(self.j),'journal_sets':[{'root':str(self.j),'patterns':['**/*.json']}],
                  'special_launches':[], 'terminal_paths':[str(self.j/'launches/a.terminal.json')], 'owned_documents':['/task/owned.docx']}
        for p in (self.b.lock_path('word-zotero'),self.ext,self.focus):
            st=p.stat(); self.c['locks'].append({'path':str(p),'device':st.st_dev,'inode':st.st_ino})
        self.refresh()

    def refresh(self):
        self.c['journal_paths']=sorted(str(f) for f in self.j.rglob('*.json'))
        self.c['evidence']=[r.pin(p) for p in self.c['journal_paths']]

    def invoke(self, obs=None, apply=True, identity=None):
        auth=self.root/'authorization.json'
        auth.write_text(json.dumps({'authorized_by':'user','directive':'Fix scoped expired Word release', 'scope':'expired-word-lease-recovery',
                                   'ticket':self.lease['id'],'actor':self.actor,'implementation':self.c['implementation'],'valid_until':self.c['valid_until']}))
        self.c['authorization']=r.pin(auth)
        contract=self.root/'contract.json'; contract.write_text(json.dumps(self.c))
        def observer(c,out):
            raw={'observed_at':time.time(),'read_only':True,'complete':True,'documents':1,'windows':1,'modal':False,'zotero_dialog':False,
                 'document_inventory':[{'path':'/foreign/unsaved.docx','saved':False}]}
            if callable(obs):return obs(raw)
            raw.update(obs or {});return raw
        return r.recover(contract,self.root/'output',apply,identity=identity or (lambda:self.actor),observer=observer)

    def test_foreign_unsaved_doc_release_and_old_token_fenced_fifo_preserved(self):
        before=self.b.get(self.waiter['id'])
        result=self.invoke()
        self.assertEqual(result['status'],'RELEASED')
        self.assertFalse(result['proof']['global_word_empty'])
        self.assertEqual(self.b.get(self.waiter['id']),before)
        with self.assertRaises(ResourceBusy):self.b.require(self.lease['id'],self.lease['token'])
        self.assertEqual(self.b.grant(self.waiter['id'])['status'],'ACTIVE')

    def test_observe_only_never_mutates(self):
        self.invoke(apply=False);self.assertEqual(self.b.get(self.lease['id']),self.lease)

    def test_unknown_and_boolean_counts_rejected(self):
        for value in (None,True,'UNKNOWN'):
            with self.subTest(value=value):
                raw={'observed_at':time.time(),'read_only':True,'complete':True,'documents':value,'windows':0}
                with self.assertRaisesRegex(r.RecoveryError,'COUNTS_UNKNOWN'):r.validate_observation(raw,self.c,time.time()-1)

    def test_owned_document_open(self):
        with self.assertRaisesRegex(r.RecoveryError,'TASK_DOCUMENT_STILL_OPEN'):
            self.invoke({'document_inventory':[{'path':'/task/owned.docx','saved':True}]})

    def foreign_setup(self):
        request=self.root/'REQUEST.json'
        r.save(request,{'actor_uuid':self.waiter['surface_uuid']})
        scope=str(self.root/'preserved')
        modal={'app':'Microsoft Word','title':'授與檔案存取權','role':'AXWindow',
               'subrole':'AXDialog','modal':True,'sheets':0,'texts':[scope]}
        self.c['foreign_dialogs']=[{'fingerprint':copy.deepcopy(modal),'request':r.pin(request),
                                  'waiter':self.waiter,'scope_path':scope}]
        return {'modal':True,'modal_inventory':[modal]}

    def test_foreign_modal_scoped_release_preserves_waiter(self):
        obs=self.foreign_setup()
        result=self.invoke(obs)
        self.assertFalse(result['proof']['scope']['global_ui_ready'])
        self.assertEqual(self.b.get(self.waiter['id']),self.waiter)
        self.assertEqual(result['proof']['scope']['foreign_modals'][0]['action'],'left_untouched')


    def test_foreign_sheet_inherits_verified_parent_scope(self):
        obs=self.foreign_setup()
        for modal in [obs['modal_inventory'][0],self.c['foreign_dialogs'][0]['fingerprint']]:
            modal['sheets']=1;modal['child_sheets']=[{'role':'AXSheet'}]
        result=self.invoke(obs)
        self.assertFalse(result['proof']['scope']['global_ui_ready'])
        self.assertEqual(self.b.get(self.waiter['id']),self.waiter)

    def test_foreign_sheet_missing_ancestry_rejected(self):
        obs=self.foreign_setup()
        for modal in [obs['modal_inventory'][0],self.c['foreign_dialogs'][0]['fingerprint']]:modal['sheets']=1
        with self.assertRaisesRegex(r.RecoveryError,'SHEET_ANCESTRY'):self.invoke(obs)

    def test_foreign_sheet_with_changed_parent_rejected(self):
        obs=self.foreign_setup()
        obs['modal_inventory'][0]['sheets']=1
        obs['modal_inventory'][0]['child_sheets']=[{'role':'AXSheet'}]
        with self.assertRaisesRegex(r.RecoveryError,'OWNERSHIP_UNKNOWN'):self.invoke(obs)

    def test_unknown_modal_owner(self):
        obs=self.foreign_setup();obs['modal_inventory'][0]['title']='changed'
        with self.assertRaisesRegex(r.RecoveryError,'OWNERSHIP_UNKNOWN'):self.invoke(obs)

    def test_foreign_actor_mismatch(self):
        obs=self.foreign_setup()
        path=self.root/'REQUEST.json';path.write_text(json.dumps({'actor_uuid':'other'}))
        self.c['foreign_dialogs'][0]['request']=r.pin(path)
        with self.assertRaisesRegex(r.RecoveryError,'OWNER_MISMATCH'):self.invoke(obs)

    def test_foreign_waiter_changed(self):
        obs=self.foreign_setup()
        self.b.db.execute("UPDATE tickets SET task_id='other' WHERE id=?",(self.waiter['id'],))
        with self.assertRaisesRegex(r.RecoveryError,'FOREIGN_WAITER_CHANGED'):self.invoke(obs)

    def test_foreign_scope_mismatch(self):
        obs=self.foreign_setup();self.c['foreign_dialogs'][0]['scope_path']='/another/preserved'
        with self.assertRaisesRegex(r.RecoveryError,'SCOPE_MISMATCH'):self.invoke(obs)

    def test_zotero_modal_not_recoverable(self):
        obs=self.foreign_setup();obs['zotero_dialog']=True
        with self.assertRaisesRegex(r.RecoveryError,'UNRESOLVED'):self.invoke(obs)

    def test_extra_modal_not_recoverable(self):
        obs=self.foreign_setup();obs['modal_inventory'].append(copy.deepcopy(obs['modal_inventory'][0]))
        with self.assertRaisesRegex(r.RecoveryError,'UNRESOLVED'):self.invoke(obs)

    def test_missing_modal_inventory(self):
        obs=self.foreign_setup();obs['modal_inventory']=[]
        with self.assertRaisesRegex(r.RecoveryError,'UNRESOLVED'):self.invoke(obs)

    def test_foreign_request_changes_during_observation(self):
        obs=self.foreign_setup()
        def observer(raw):
            (self.root/'REQUEST.json').write_text('{}');raw.update(obs);return raw
        with self.assertRaisesRegex(r.RecoveryError,'PIN_CHANGED'):self.invoke(observer)

    def test_modal(self):
        with self.assertRaisesRegex(r.RecoveryError,'UNRESOLVED'):self.invoke({'modal':True})

    def test_stale(self):
        with self.assertRaisesRegex(r.RecoveryError,'STALE'):self.invoke({'observed_at':0})

    def test_unknown_inventory(self):
        with self.assertRaisesRegex(r.RecoveryError,'INCOMPLETE'):self.invoke({'document_inventory':[]})

    def test_wrong_actor(self):
        with self.assertRaisesRegex(r.RecoveryError,'ACTOR_MISMATCH'):self.invoke(identity=lambda:{})

    def test_changed_lease(self):
        self.b.db.execute('UPDATE tickets SET invocations=2 WHERE id=?',(self.lease['id'],))
        with self.assertRaisesRegex(r.RecoveryError,'LEASE_CHANGED'):self.invoke()

    def test_unexpired(self):
        self.c['lease']['expires']=time.time()+100
        self.b.db.execute('UPDATE tickets SET expires=? WHERE id=?',(self.c['lease']['expires'],self.lease['id']))
        with self.assertRaisesRegex(r.RecoveryError,'EXPIRED_ACTIVE'):self.invoke()

    def test_nlm_never_recovered(self):
        self.c['lease']['resource']='nlm-account:test'
        with self.assertRaisesRegex(r.RecoveryError,'WORD_ONLY'):self.invoke()

    def test_real_lock_busy(self):
        with self.ext.open('r+') as f:
            fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
            with self.assertRaisesRegex(r.RecoveryError,'LOCK_BUSY'):self.invoke()

    def test_actual_process_alive(self):
        proc=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)'],start_new_session=True)
        self.addCleanup(lambda:(proc.terminate(),proc.wait()))
        p=self.j/'active.process.json';r.save(p,{'pgid':proc.pid});self.refresh()
        with self.assertRaisesRegex(r.RecoveryError,'PROCESS_GROUP_ALIVE'):self.invoke()

    def test_pending_inner_intent(self):
        r.save(self.j/'unfinished.intent.json',{'argv':[]});self.refresh()
        with self.assertRaisesRegex(r.RecoveryError,'PENDING_NATIVE'):self.invoke()

    def test_pending_outer_launch(self):
        r.save(self.j/'launches/b.json',{'ticket':self.lease['id'],'task_id':'old-task'});self.refresh()
        with self.assertRaisesRegex(r.RecoveryError,'COVERAGE'):self.invoke()

    def test_owned_scope_cannot_omit_a_document(self):
        r.save(self.j/'other.json',{'owned':{'path':'/task/second.docx'}});self.refresh()
        with self.assertRaisesRegex(r.RecoveryError,'SCOPE_INCOMPLETE'):self.invoke()

    def test_journal_mutation_during_observation(self):
        def obs(raw):
            r.save(self.j/'late.intent.json',{});return raw
        with self.assertRaisesRegex(r.RecoveryError,'SET_CHANGED'):self.invoke(obs)
        self.assertEqual(self.b.get(self.lease['id'])['status'],'ACTIVE')

    def test_locks_remain_held_during_observation(self):
        def obs(raw):
            for ref in self.c['locks']:
                with self.assertRaisesRegex(r.RecoveryError,'LOCK_BUSY'):
                    with r.held_lock(ref):pass
            return raw
        self.invoke(obs)

    def test_postcommit_receipt_failure_is_truthful(self):
        real=r.save
        def save(path,obj):
            if Path(path).name=='COMMITTED.json':raise OSError('simulated disk error')
            return real(path,obj)
        with patch.object(r,'save',side_effect=save):
            with self.assertRaises(OSError):self.invoke()
        self.assertEqual(self.b.get(self.lease['id'])['status'],'RELEASED')
        err=json.loads((self.root/'output/POST_COMMIT_ERROR.json').read_text())
        self.assertTrue(err['released']);self.assertTrue(err['committed'])

    def test_replay_refused(self):
        self.invoke()
        with self.assertRaisesRegex(r.RecoveryError,'FRESH_OUTPUT'):self.invoke()

class ObserverTests(unittest.TestCase):

    def test_sheet_count_must_match_direct_children(self):
        bad='WORD_AX_V3\nWORD_PROCESS\ttrue\nWIN\tMicrosoft Word\t1\tDialog\tAXWindow\tAXDialog\ttrue\t1\nEND'
        with self.assertRaisesRegex(r.RecoveryError,'SHEET_COUNT'):r.parse_ax(bad)
    def test_sheet_needs_observed_parent(self):
        with self.assertRaisesRegex(r.RecoveryError,'SHEET_PARSE'):
            r.parse_ax('WORD_AX_V3\nWORD_PROCESS\ttrue\nSHEET\tMicrosoft Word\t1\tAXSheet\nEND')
    def test_word_zero_windows_zotero_main_window(self):
        parsed=r.parse_ax('WORD_AX_V3\nWORD_PROCESS\ttrue\nWIN\tZotero\t1\tLibrary\tAXWindow\tAXStandardWindow\tfalse\t0\nEND')
        self.assertFalse(parsed['modal']);self.assertFalse(parsed['zotero_dialog'])
    def test_word_process_observation_required(self):
        with self.assertRaisesRegex(r.RecoveryError,'AX_WORD_MISSING'):r.parse_ax('WORD_AX_V3\nEND')
    def test_changed_ax_inventory(self):
        with tempfile.TemporaryDirectory() as d:
            c={'observer':r.pin(Path(r.__file__).with_name('observe_word.applescript')),
               'ax_observer':r.pin(Path(r.__file__).with_name('observe_ax.applescript'))}
            a='WORD_INVENTORY_V2\t0\t0\nEND'
            b='WORD_AX_V3\nWORD_PROCESS\ttrue\nEND'
            last='WORD_AX_V3\nWORD_PROCESS\ttrue\nWIN\tMicrosoft Word\t1\tDialog\tAXWindow\tAXDialog\ttrue\t0\nEND'
            with patch.object(r,'bounded_probe',side_effect=[a,b,a,last]):
                with self.assertRaisesRegex(r.RecoveryError,'CHANGED'):r.word_observer(c,Path(d))

    def test_inventory_parser(self):
        raw=r.parse_inventory('WORD_INVENTORY_V2\t1\t1\nDOC\t/foreign/a.docx\tfalse\nEND\n')
        self.assertEqual(raw['documents'],1)
        self.assertFalse(raw['document_inventory'][0]['saved'])
    def test_truncated_output(self):
        with self.assertRaises(r.RecoveryError):r.parse_inventory('WORD_INVENTORY_V2\t0\t0')
    def test_invalid_boolean(self):
        with self.assertRaises(r.RecoveryError):r.parse_inventory('WORD_INVENTORY_V2\t1\t1\nDOC\t/a\tunknown\nEND')
    def test_split_observer_and_changed_inventory(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)
            c={'observer':r.pin(Path(r.__file__).with_name('observe_word.applescript')),
               'ax_observer':r.pin(Path(r.__file__).with_name('observe_ax.applescript'))}
            a='WORD_INVENTORY_V2\t0\t0\nEND'
            with patch.object(r,'bounded_probe',side_effect=[a,'WORD_AX_V3\nWORD_PROCESS\ttrue\nEND',a,'WORD_AX_V3\nWORD_PROCESS\ttrue\nEND']):
                obs=r.word_observer(c,out)
            self.assertFalse(obs['modal']);self.assertTrue(obs['complete'])
        with tempfile.TemporaryDirectory() as d:
            with patch.object(r,'bounded_probe',side_effect=[a,'WORD_AX_V3\nWORD_PROCESS\ttrue\nEND','WORD_INVENTORY_V2\t0\t1\nEND','WORD_AX_V3\nWORD_PROCESS\ttrue\nEND']):
                with self.assertRaisesRegex(r.RecoveryError,'CHANGED'):r.word_observer(c,Path(d))

if __name__=='__main__':unittest.main(verbosity=2)
