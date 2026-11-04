"""Random-only actual worker integration: shared TEST reuse and no recapture."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import torch
from transformers import Gemma3TextConfig,Gemma3ForCausalLM
from research_checks.gate import digest
from . import worker_a,worker_a_v2
from .schedule_a import schedule as original_schedule
from .schedule_a_v2 import schedule
from .runtime import Runtime


class Tests(unittest.TestCase):
    def test_real_random_worker_shared_test_and_zero_forward_stability(self):
        torch.set_num_threads(2);torch.manual_seed(9271);rng=np.random.default_rng(9272)
        conf=Gemma3TextConfig(vocab_size=128,hidden_size=32,intermediate_size=64,num_hidden_layers=3,
           num_attention_heads=2,num_key_value_heads=1,head_dim=16,sliding_window=32,
           layer_types=['sliding_attention','sliding_attention','full_attention'])
        model=Gemma3ForCausalLM(conf).eval().float();docs=[];tokens={}
        for split,count,frames in [('FIT_MAP',8,['F0','F1']),('FIT_U',8,['F0','F1']),('FIT_EXT',8,['T0','T2','T5']),('TEST',1,['T0','T2','T5','T6','T7'])]:
            for block in range(count):
                for frame in frames:
                    for q in [0,1]:
                        common=rng.integers(3,120,size=3).tolist()
                        for side in [0,1]:
                            name=f'{split}_{block}_{frame}_{q}_{side}'
                            docs.append(dict(id=name,donor=f'{split}_{block}_{frame}_{q}_{1-side}',study='A',
                                cohort='r0' if split!='TEST' else 'shared',split=split,frame=frame,block=f'{split}_{block}',side=side,q=q,text=name))
                            tokens[name]=dict(ids=[2]+common+[41+side],answer_ids=[10,20])
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            def put(name,value):
                p=folder/name;p.write_text(json.dumps(value));return str(p)
            corpus=put('corpus.json',dict(documents=docs));tokenfile=put('tokens.json',tokens)
            identity=put('model.json',dict(A=dict(folder='synthetic_random_only',files={},dtype='float32')))
            def config(phase,out):
                cfg=dict(study='A',phase=phase,corpus=corpus,tokens=tokenfile,model_identity=identity,output=str(folder/out),threads=2,
                    documents=[d['id'] for d in docs if (d['split']=='TEST')==(phase=='TEST')],control_documents=[],
                    fit_cohorts=['r0'] if phase!='TEST' else [],evaluate_cohorts=[] if phase!='TEST' else ['r0'],
                    evaluate_splits=[] if phase!='TEST' else ['TEST'],frozen_fits={} if phase!='TEST' else {'r0':str(folder/'fit/FIT_r0.json')},
                    gates=dict(sham_abs=1e-5,branch_rel=1e-4,parity_abs=1e-5,positive_margin=1e-7))
                cfg['schedule']=put(out+'_operations.json',original_schedule(cfg,docs));return cfg
            train=config('FIT_ONLY','fit');test=config('TEST','primary')
            with patch('transformers.AutoModelForCausalLM.from_pretrained',return_value=(model,{})) as loader:
                worker_a.main(put('train.json',train));worker_a.main(put('test.json',test))
                self.assertEqual(loader.call_count,2)
                source_bytes={p:p.read_bytes() for p in (folder/'primary').rglob('*') if p.is_file()}
                cfg=dict(test,stage_kind='STABILITY',adapter_sources=worker_a_v2.adapter_sources(),
                    output=str(folder/'stability'),evaluate_cohorts=['r1','r2'],
                    frozen_fits={c:str(folder/'fit/FIT_r0.json') for c in ['r1','r2']},
                    reuse_stages={'primary_test':str(folder/'primary')},
                    reuse_operations={op:'primary_test' for d in docs if d['split']=='TEST' for op in ['capture_'+d['id'],'suffix_'+d['id']+'_native']})
                cfg['schedule']=put('stability_operations.json',schedule(cfg,docs));path=put('stability.json',cfg)
                self.assertEqual(len(schedule(cfg,docs)['operations']),200)
                # Random fixture intentionally mocks only external real-model
                # qualification/admission. Actual Runtime/cache/worker execute.
                with patch.object(worker_a_v2,'validate_qualification'),patch.object(worker_a_v2,'validate_admission'),patch('ab_confirmatory_20261101.native.Native.forward',side_effect=AssertionError('duplicate full forward')):
                    worker_a_v2.main(path)
                    self.assertEqual(loader.call_count,3)
                    worker_a_v2.main(path);self.assertEqual(loader.call_count,3)
                self.assertIs(worker_a.Runtime,Runtime)
                self.assertTrue(all(p.read_bytes()==raw for p,raw in source_bytes.items()))
                self.assertEqual(len(list((folder/'stability/reused').glob('*.json'))),40)
                self.assertEqual(len(list((folder/'stability/results/r1').glob('*.json'))),20)
                for d in [d for d in docs if d['split']=='TEST']:
                    original=worker_a_v2.read(folder/'primary/results/r0'/f'{d["id"]}.json')
                    for c in ['r1','r2']:
                        imported=worker_a_v2.read(folder/f'stability/results/{c}'/f'{d["id"]}.json')
                        self.assertEqual(imported['native_h'],original['native_h']);self.assertEqual(imported['values'],original['values'])
                cache=next((folder/'primary/cache').glob('*.json'));raw=cache.read_bytes();cache.write_bytes(raw+b' ')
                with patch.object(worker_a_v2,'validate_qualification'),patch.object(worker_a_v2,'validate_admission'):
                    with self.assertRaisesRegex(ValueError,'artifact changed'):worker_a_v2.main(path)
                self.assertEqual(loader.call_count,3);cache.write_bytes(raw)

    def test_reuse_rejects_semantic_mismatch_without_computation(self):
        model='model';source=dict(model_identity=model,code_identity='old',document={'x':1},intervention={'mode':'native'},readout={'r':1})
        reused={'capture_x':dict(request=source,result={'value':7},source={'fixture':True})}
        with tempfile.TemporaryDirectory() as folder:
            runtime=worker_a_v2.runtime_class(reused)(folder,dict(model=model,code='new'),dict(operations=[]))
            with self.assertRaisesRegex(ValueError,'semantics differ'):
                runtime.compute('capture_x',{'x':2},{'mode':'native'},{'r':1},lambda:self.fail('called'))
            self.assertEqual(len(runtime.attempts),0)
            result=runtime.compute('capture_x',{'x':1},{'mode':'native'},{'r':1},lambda:self.fail('called'))
            self.assertEqual(result,{'value':7});self.assertEqual(len(runtime.attempts),0)

    def test_schedule_rejects_predicted_arm_import(self):
        cfg=dict(documents=['x'],control_documents=[],evaluate_splits=['TEST'],evaluate_cohorts=['r0'],
                 reuse_operations={'suffix_x_r0_P':'source'})
        with self.assertRaises(ValueError):schedule(cfg,[dict(id='x',split='TEST')])


if __name__=='__main__':unittest.main(verbosity=2)
