"""Cheap gate-only fixtures. No models, fitting, Monte Carlo, or stage writes."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path.cwd()))
import short_fixed_workflow_v3 as workflow
from a_short_qwen_20261101.prepare import FROZEN_CORPUS_SHA256

class FutureTest(unittest.TestCase):
    def exercise(self,model,change=None):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);base=root/'auth';base.mkdir()
            corpus=root/'analysis/A_short_replication_qwen_20261101/shared_corpus_v1.json'
            corpus.parent.mkdir(parents=True)
            docs=[dict(split='TEST',index=i) for i in range(256)]
            corpus.write_text(json.dumps(dict(documents=docs)))
            fit=root/f'analysis/A_short_replication_{model}_20261101/FIT_ready_v1/run'/('FIT.json' if model=='qwen' else 'FIT_r0.json')
            amendment=dict(version=3,objective=workflow.OBJECTIVE,fixed_TEST_blocks=256,PILOT_blocks=32,primary='T5_L_U0_minus_L_P',secondary='T2_descriptive',alpha_per_model=.025,power_assurance=False,precision_assurance=False,interim_looks=False,sample_extension=False,original_unexecuted_selector='cancelled_prospectively',whole_AB_completed=False)
            completed=dict(scope='TEST',attempted_operations=35840,files={**{f'completed/{i}':'h' for i in range(35840)},**{f'results/r0/{i}':'h' for i in range(5120)}})
            runtime=base/'runtime';runtime.write_text(json.dumps(dict(returncode=0,snapshot_sha256='dfc8514fcf32201bc664f145f1838b0e06303b751406064f4ce5e5e566d3cb2b')))
            pilot=dict(identity=dict(model='model-hash'),**({'phase':'PILOT'} if model=='qwen' else {'scope':'PILOT'}))
            receipts={base/'amendment':amendment,base/'complete':completed,base/'fit-evidence':dict(model=model,technical_passed=True,fit_sha256='h'),base/'pilot-evidence':pilot,fit:dict(model_sha256='model-hash',identity=dict(model='model-hash'))}
            m=dict(model=model,objective=workflow.OBJECTIVE,amendment='amendment',A_acquisition_completion='complete',A_runtime_completion='runtime',eligibility={},fit_completion=dict(evidence='fit-evidence',snapshot='fit-snapshot',review='fit-review'),pilot_completion=dict(evidence='pilot-evidence',snapshot='pilot-snapshot',review='pilot-review'))
            cfg=dict(phase='TEST',admission_manifest='auth/manifest',corpus='unused',selected_n=256)
            if model=='qwen':cfg.update(study='A_SHORT_QWEN',frozen_fit=str(fit))
            else:cfg.update(model=model,frozen_fits=dict(r0=str(fit)))
            if change:change(cfg,pilot)
            files={str(base/name):'h' for name in ['amendment','complete','runtime','fit-evidence','fit-snapshot','fit-review','pilot-evidence','pilot-snapshot','pilot-review']}
            def snapshot(*args):return dict(payload=dict(files={fit.relative_to(root).as_posix():'h','auth/fit-evidence':'h','auth/pilot-evidence':'h'}))
            with patch.object(workflow,'ROOT',root),patch.object(workflow,'manifested_json',return_value=(m,dict(files=files))),patch.object(workflow,'read_receipt',side_effect=lambda p:receipts[p]),patch.object(workflow,'sha',side_effect=lambda p:FROZEN_CORPUS_SHA256 if p==corpus else 'h'),patch.object(workflow,'verify_at_root',side_effect=snapshot),patch.object(workflow,'validate_eligibility',return_value=True):
                return workflow.validate(cfg,source_binding=False,documents=docs)
    def test_actual_qwen_phase_format(self):self.assertTrue(self.exercise('qwen'))
    def test_actual_llama_scope_format(self):self.assertTrue(self.exercise('llama'))
    def test_wrong_n_rejected(self):
        with self.assertRaisesRegex(ValueError,'size'):self.exercise('qwen',lambda c,p:c.update(selected_n=128))
    def test_wrong_model_rejected(self):
        with self.assertRaisesRegex(ValueError,'different model'):self.exercise('llama',lambda c,p:p['identity'].update(model='other'))
    def test_test_cannot_replace_pilot(self):
        with self.assertRaisesRegex(ValueError,'PILOT'):self.exercise('qwen',lambda c,p:p.update(phase='TEST'))

if __name__=='__main__':unittest.main()
