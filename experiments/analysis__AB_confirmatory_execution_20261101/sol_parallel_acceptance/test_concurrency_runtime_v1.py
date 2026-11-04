import importlib.util
import json
import multiprocessing
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
import concurrency_runtime_v1 as runtime

def competitor(path,queue):
    try:
        with runtime.owned_lock(Path(path),dict(token='contender')):queue.put('acquired')
    except (OSError,ValueError):queue.put('blocked')

class RuntimeTests(unittest.TestCase):
    def test_real_process_lock_exclusion_and_token_cleanup(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'lane.lock'
            with runtime.owned_lock(path,dict(token='owner')):
                queue=multiprocessing.Queue();child=multiprocessing.Process(target=competitor,args=(str(path),queue))
                child.start();child.join(20)
                self.assertEqual(child.exitcode,0);self.assertEqual(queue.get(timeout=2),'blocked')
                self.assertEqual(json.loads(path.read_text())['token'],'owner')
            self.assertFalse(path.exists())

    def test_different_snapshots_same_output_collide(self):
        root=Path.cwd()
        a=dict(id='old',entrypoint=dict(args=['--out','run/shared']))
        b=dict(id='new',entrypoint=dict(args=['--out','run/shared']))
        self.assertTrue(set(runtime.stage_keys(root,a))&set(runtime.stage_keys(root,b)))

    def test_cpu_classification_fail_closed(self):
        obj=dict(budget=dict(forward=0,backward=0),entrypoint=dict(module='unknown'))
        with self.assertRaises(ValueError):runtime.classify(obj,dict(cpu_entrypoints=[]))
        self.assertEqual(runtime.classify(obj,dict(cpu_entrypoints=['unknown'])),'cpu')
        obj['budget']['forward']=1
        self.assertEqual(runtime.classify(obj,dict(cpu_entrypoints=[])),'model')

    def test_actual_tail_and_a_config_output_binding(self):
        for name in ['B_tail_qualification_v1','A_pilot_ready_v1']:
            relative=f'analysis/AB_confirmatory_execution_20261101/{name}/config.json'
            config=ROOT/relative
            snap=dict(payload=dict(files={relative:runtime.sha(config)}))
            obj=dict(id=name,entrypoint=dict(args=['--config',relative]))
            keys=runtime.stage_keys(ROOT,obj,snap)
            self.assertIn('namespace:'+str((ROOT/json.loads(config.read_text())['output']).resolve()).casefold(),keys)
            changed=dict(obj,id='changed-review-and-contract')
            self.assertTrue(set(keys)&set(runtime.stage_keys(ROOT,changed,snap)))
            with self.assertRaises(ValueError):runtime.stage_keys(ROOT,obj,dict(payload=dict(files={})))

    def fixture(self,root):
        parent=dict(ProcessId=100,ParentProcessId=1,CreationDate='time1',CommandLine='python -m research_checks launch --snapshot old')
        child=dict(ProcessId=101,ParentProcessId=100,CreationDate='time2',CommandLine='python -m research_checks._worker --snapshot old')
        lock=root/'operations/research_worker.lock';lock.parent.mkdir()
        runtime.create(lock,dict(token='legacy',snapshot_sha256='snapshot'))
        policy=dict(retired_queue_processes=[],retired_queue_scripts=['queue_legacy.ps1'],cpu_entrypoints=['offline'],legacy_cpu=dict(processes=[parent,child],lock_sha256=runtime.sha(lock),snapshot_sha256='snapshot',token='legacy',snapshot='old',review='review'))
        return policy,{100:parent,101:child}

    def test_legacy_exact_owner_and_stale_unknown_rejection(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);policy,table=self.fixture(root)
            snap=dict(snapshot_sha256='snapshot',payload=dict(contract='contract'))
            obj=dict(id='old',budget=dict(forward=0,backward=0),entrypoint=dict(module='offline'))
            with patch.object(runtime,'verify_review',return_value=snap),patch.object(runtime,'contract',return_value=obj):
                self.assertEqual(runtime.legacy_state(root,policy,table),obj)
                with self.assertRaises(ValueError):runtime.legacy_state(root,policy,{100:table[100]})
                changed={**table,101:{**table[101],'CreationDate':'reusedPID'}}
                with self.assertRaises(ValueError):runtime.legacy_state(root,policy,changed)
                unknown={**table,102:dict(ProcessId=102,CommandLine='python -m research_checks launch --snapshot surprise')}
                with self.assertRaises(ValueError):runtime.legacy_state(root,policy,unknown)
                replacement={**table,103:dict(ProcessId=103,CommandLine='powershell -File C:/queue_legacy.ps1')}
                with self.assertRaises(ValueError):runtime.legacy_state(root,policy,replacement)
                policy['retired_queue_processes']=[table[100]]
                with self.assertRaises(ValueError):runtime.legacy_state(root,policy,table)

    def test_canonical_child_has_explicit_actual_utf8_and_verifies_before_import(self):
        source=(ROOT/'research_checks/_worker.py').read_text()
        self.assertLess(source.index('verify_review(root'),source.index('runpy.run_module('))
        source=(ROOT/'concurrency_runtime_v1.py').read_text()
        self.assertIn("f'utf8={sys.flags.utf8_mode}'",source)
        self.assertLess(source.index("verify_review(root,snapshot_path,review_path,'pre_run')"),source.index('subprocess.run(args'))

    def test_launch_child_flags_receipt_and_failed_parent_verification(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);policy=root/'policy.json'
            policy.write_text(json.dumps(dict(schema_version=1,all_future_launches_use_v1=True,cpu_entrypoints=[])))
            (root/'review.json').write_text('{}')
            approval=dict(snapshot_sha256='migration',payload=dict(files={'policy.json':runtime.sha(policy)}))
            snap=dict(snapshot_sha256='stage',payload=dict(contract='contract'))
            obj=dict(id='stage',budget=dict(forward=1,backward=0),entrypoint=dict(module='never_imported',args=['--out','output']))
            with patch.object(runtime,'verify_review',side_effect=[approval,snap,snap]) as verify,patch.object(runtime,'contract',return_value=obj),patch.object(runtime,'legacy_state',return_value=None),patch.object(runtime,'process_table',return_value={}),patch.object(runtime.subprocess,'run') as run:
                run.return_value.returncode=0
                self.assertEqual(runtime.launch(root,'snapshot','review.json','policy.json','migration','migration-review'),0)
                args=run.call_args.args[0]
                self.assertEqual(args[:6],[sys.executable,'-X',f'utf8={sys.flags.utf8_mode}','-m','research_checks._worker','--snapshot'])
                self.assertEqual(verify.call_count,3)
                self.assertEqual(len(list((root/'operations/concurrency_runtime_v1').glob('launch_*.json'))),1)
                self.assertFalse(list((root/'operations').rglob('*.lock')))
            with patch.object(runtime,'verify_review',side_effect=ValueError('bad review')),patch.object(runtime.subprocess,'run') as run:
                with self.assertRaises(ValueError):runtime.launch(root,'snapshot','review.json','policy.json','migration','migration-review')
                run.assert_not_called()

if __name__=='__main__':unittest.main()
