import os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
import concurrency_runtime_qwen_fit_v4 as gate

class HeavyFitAdmissionTests(unittest.TestCase):
    def test_exact_FIT_and_free_native_slots(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);folder=root/'operations/concurrency_runtime_v1';folder.mkdir(parents=True)
            policy=dict(authorized_Qwen_FIT=dict(snapshot_sha256='FIT',entrypoint='qwenfit'),minimum_free_RAM_KB_before_Qwen=7864320)
            snap=dict(snapshot_sha256='FIT');obj=dict(entrypoint=dict(module='qwenfit'),budget=dict(forward=284,backward=0))
            with patch.object(gate,'available_memory_KB',return_value=9000000):
                gate.check_authorized_model(policy,snap,obj,root)
                gate.create(folder/'model_slot1.lock',dict(pid=1,token='prior'))
                with self.assertRaises(ValueError):gate.check_authorized_model(policy,snap,obj,root)
                (folder/'model_slot1.lock').unlink()
                with self.assertRaises(ValueError):gate.check_authorized_model(policy,dict(snapshot_sha256='PILOT'),obj,root)
                with gate.model_slot(folder,dict(pid=os.getpid(),token='Qwen')):
                    gate.check_authorized_model(policy,snap,obj,root)
                    with self.assertRaises(ValueError):
                        with gate.model_slot(folder,dict(pid=1,token='secondheavy')):pass
            with patch.object(gate,'available_memory_KB',return_value=6000000):
                with self.assertRaises(ValueError):gate.check_authorized_model(policy,snap,obj,root)

if __name__=='__main__':unittest.main()
