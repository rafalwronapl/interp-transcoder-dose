import json,multiprocessing,os,sys,tempfile,unittest
import hashlib
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
import concurrency_runtime_v1 as old
import concurrency_runtime_v2 as new

def contender(folder,queue):
    try:
        with new.cpu_slot(Path(folder),dict(token='third',pid=os.getpid())):queue.put('acquired')
    except ValueError:queue.put('blocked')

class TwoSlotTests(unittest.TestCase):
    def test_active_v1_consumes_slot0_and_third_process_cannot_enter(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d)
            with old.owned_lock(directory/'cpu.lock',dict(token='v1',pid=123)):
                before=(directory/'cpu.lock').read_bytes()
                with new.cpu_slot(directory,dict(token='v2',pid=456)) as index:
                    self.assertEqual(index,1)
                    queue=multiprocessing.Queue();p=multiprocessing.Process(target=contender,args=(str(directory),queue));p.start();p.join(20)
                    self.assertEqual(p.exitcode,0);self.assertEqual(queue.get(timeout=2),'blocked')
                    self.assertEqual((directory/'cpu.lock').read_bytes(),before)
                self.assertFalse((directory/'cpu_slot1.lock').exists());self.assertTrue((directory/'cpu.lock').exists())
            self.assertFalse(list(directory.glob('*.lock')))

    def test_two_v2_slots_then_exact_cap(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d)
            with new.cpu_slot(directory,dict(token='first')) as a:
                with new.cpu_slot(directory,dict(token='second')) as b:
                    self.assertEqual((a,b),(0,1))
                    with self.assertRaises(ValueError):
                        with new.cpu_slot(directory,dict(token='third')):pass

    def test_cross_version_stage_namespace_collision(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d);obj=dict(id='stage',entrypoint=dict(args=['--out','same']))
            keys=old.stage_keys(directory,obj);changed=dict(obj,id='new-review-same-output')
            shared=set(keys)&set(new.stage_keys(directory,changed));self.assertEqual(len(shared),1)
            path=directory/('stage_'+hashlib.sha256(next(iter(shared)).encode()).hexdigest()+'.lock')
            with old.owned_lock(path,dict(token='old')):
                with self.assertRaises(FileExistsError):
                    with new.owned_lock(path,dict(token='new')):pass

    def test_model_lane_is_single_across_versions_and_cpu_is_separate(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d)
            with old.owned_lock(directory/'model.lock',dict(token='old-model')):
                with self.assertRaises(FileExistsError):
                    with new.owned_lock(directory/'model.lock',dict(token='new-model')):pass
                with new.cpu_slot(directory,dict(token='cpu')) as index:self.assertEqual(index,0)

    def test_both_versions_children_are_recognized_and_unknown_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);directory=root/'operations/concurrency_runtime_v1';directory.mkdir(parents=True)
            new.create(directory/'cpu.lock',dict(pid=100,token='old'))
            new.create(directory/'cpu_slot1.lock',dict(pid=200,token='new'))
            table={100:dict(ProcessId=100,CommandLine='python -m concurrency_runtime_v1 --snapshot old'),200:dict(ProcessId=200,CommandLine='python -m concurrency_runtime_v2 --snapshot new'),101:dict(ProcessId=101,ParentProcessId=100,CommandLine='python -m research_checks._worker --snapshot old'),201:dict(ProcessId=201,ParentProcessId=200,CommandLine='python -m research_checks._worker --snapshot new')}
            policy=dict(retired_queue_scripts=[],retired_queue_processes=[],legacy_cpu=dict(processes=[]),grandfathered_v1_cpu=dict(lock_sha256=new.sha(directory/'cpu.lock'),processes=[table[100],table[101]]))
            self.assertIsNone(new.legacy_state(root,policy,table))
            table[300]=dict(ProcessId=300,ParentProcessId=2,CommandLine='python -m research_checks._worker --snapshot unexpected')
            with self.assertRaises(ValueError):new.legacy_state(root,policy,table)
            del table[300];table[200]['CommandLine']='unrelated reused PID'
            with self.assertRaises(ValueError):new.legacy_state(root,policy,table)

if __name__=='__main__':unittest.main()
