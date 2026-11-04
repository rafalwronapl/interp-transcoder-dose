import hashlib,multiprocessing,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
import concurrency_runtime_v2 as old
import concurrency_runtime_v3 as new

def third(folder,queue):
    try:
        with new.model_slot(Path(folder),dict(token='third')):queue.put('acquired')
    except ValueError:queue.put('blocked')

class ModelOverlapTests(unittest.TestCase):
    def test_active_v2_A_slot0_B_slot1_and_third_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d)
            with old.owned_lock(directory/'model.lock',dict(token='A',pid=100)):
                before=(directory/'model.lock').read_bytes()
                with new.model_slot(directory,dict(token='B',pid=200)) as index:
                    self.assertEqual(index,1);queue=multiprocessing.Queue();p=multiprocessing.Process(target=third,args=(str(directory),queue));p.start();p.join(20)
                    self.assertEqual(p.exitcode,0);self.assertEqual(queue.get(timeout=2),'blocked');self.assertEqual(before,(directory/'model.lock').read_bytes())
                self.assertTrue((directory/'model.lock').exists());self.assertFalse((directory/'model_slot1.lock').exists())

    def test_exact_B_only_and_RAM_before_model(self):
        policy=dict(authorized_B_pilot=dict(snapshot_sha256='B',entrypoint='earlyB'),minimum_free_RAM_KB_before_B=3145728)
        obj=dict(entrypoint=dict(module='earlyB'),budget=dict(forward=19776,backward=192))
        with patch.object(new,'available_memory_KB',return_value=4500000):
            new.check_authorized_model(policy,dict(snapshot_sha256='B'),obj)
            with self.assertRaises(ValueError):new.check_authorized_model(policy,dict(snapshot_sha256='heavyQwen'),obj)
            with self.assertRaises(ValueError):new.check_authorized_model(policy,dict(snapshot_sha256='B'),dict(obj,entrypoint=dict(module='heavyLlama')))
        with patch.object(new,'available_memory_KB',return_value=2000000):
            with self.assertRaises(ValueError):new.check_authorized_model(policy,dict(snapshot_sha256='B'),obj)

    def test_global_A_owner_recognized_and_output_namespace_shared(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);directory=root/'operations/concurrency_runtime_v1';directory.mkdir(parents=True)
            owner=dict(token='A',pid=100);old.create(directory/'model.lock',owner);old.create(root/'operations/research_worker.lock',owner)
            parent=dict(ProcessId=100,CommandLine='python -m concurrency_runtime_v2 --snapshot A');child=dict(ProcessId=101,ParentProcessId=100,CommandLine='python -m research_checks._worker --snapshot A')
            table={100:parent,101:child,200:dict(ProcessId=200,CommandLine='python -m concurrency_runtime_v3 --snapshot B')}
            policy=dict(retired_queue_scripts=[],retired_queue_processes=[],legacy_cpu=dict(processes=[]),grandfathered_v2_A=dict(lock_sha256=new.sha(directory/'model.lock'),processes=[parent,child]))
            with new.model_slot(directory,dict(token='B',pid=200)):
                self.assertEqual(new.legacy_state(root,policy,table),'managed_model')
            a=dict(id='old',entrypoint=dict(args=['--out','same-run']));b=dict(a,id='new')
            shared=set(old.stage_keys(root,a))&set(new.stage_keys(root,b));self.assertEqual(len(shared),1)
            lock=directory/('stage_'+hashlib.sha256(next(iter(shared)).encode()).hexdigest()+'.lock')
            with old.owned_lock(lock,dict(token='A')):
                with self.assertRaises(FileExistsError):
                    with new.owned_lock(lock,dict(token='B')):pass

if __name__=='__main__':unittest.main()
