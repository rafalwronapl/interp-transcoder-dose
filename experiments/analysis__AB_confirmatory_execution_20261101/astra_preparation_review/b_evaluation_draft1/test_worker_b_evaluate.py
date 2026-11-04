"""End-to-end acquisition/restart tests on random tiny weights only."""
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import torch
from transformers import Gemma3TextConfig,Gemma3ForCausalLM
from research_checks.gate import digest
from research_checks.persistence import immutable
from .prepare import sha
from .transcoder import Transcoder
from .worker_b_evaluate import main,schedule,unwrap

class EvaluationTests(unittest.TestCase):
    def test_qualification_replay_and_partial_resume(self):
        torch.set_num_threads(2);torch.manual_seed(719)
        config=Gemma3TextConfig(vocab_size=128,hidden_size=32,intermediate_size=64,num_hidden_layers=4,
            num_attention_heads=2,num_key_value_heads=1,head_dim=16,sliding_window=4,
            layer_types=['sliding_attention','sliding_attention','full_attention','sliding_attention'])
        model=Gemma3ForCausalLM(config).eval().float()
        state={k:torch.randn(*s)*.1 for k,s in dict(w_enc=(32,48),b_enc=(48,),w_dec=(48,32),b_dec=(32,),
            threshold=(48,),affine_skip_connection=(32,32)).items()}
        tc=Transcoder(state)
        docs=[dict(id=f'd{s}',donor=f'd{1-s}',block='b0',study='B',split='FIT',frame='transfer',side=s) for s in [0,1]]
        tokens={d['id']:dict(ids=[2,11,25,41+d['side'],18,22],answer_ids=[10,20]) for d in docs}
        ident=dict(B=dict(folder='random',files={}),TC=dict(folder='mock',files={}))
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)
            def put(name,obj):
                dest=p/name;dest.write_text(json.dumps(obj),encoding='utf-8');return str(dest)
            fit=p/'fit.json';immutable(fit,dict(identity=dict(model=digest(ident)),direction=[1.]+[0.]*31,cells={}))
            cfg=dict(phase='TAIL_QUALIFICATION',frozen_fit=str(fit),frozen_fit_sha256=sha(fit),
                corpus=put('corpus.json',dict(documents=docs)),tokens=put('tokens.json',tokens),
                model_identity=put('identity.json',ident),output=str(p/'run'),threads=2,layer=1,answer_ids=[10,20],
                doses=[.05,2.],gates=dict(margin_parity=1e-4,gradient_relative=1e-4,gradient_absolute=1e-5,branch_relative=1e-4))
            cfg['schedule']=put('operations.json',schedule(cfg,docs));path=put('config.json',cfg)
            from .runtime import Runtime
            real_compute=Runtime.compute;calls=[0]
            def fail_once(self,*args,**kwargs):
                calls[0]+=1
                # Interruption between operations preserves a durable prefix.
                if calls[0]==13:raise RuntimeError('deliberate interruption')
                return real_compute(self,*args,**kwargs)
            with patch('transformers.AutoModelForCausalLM.from_pretrained',return_value=(model,{})) as loader,patch('ab_confirmatory_20261101.transcoder.load',return_value=tc):
                with patch.object(Runtime,'compute',fail_once):
                    with self.assertRaisesRegex(RuntimeError,'deliberate interruption'):main(path)
                durable={f:f.read_bytes() for folder in ['cache','completed'] for f in (p/'run'/folder).glob('*.json')}
                main(path)
                self.assertTrue(all(f.read_bytes()==b for f,b in durable.items()))
                self.assertTrue(unwrap(p/'run/qualification.json')['passed'])
                self.assertEqual(len(list((p/'run/completed').glob('*.json'))),len(schedule(cfg,docs)['operations']))
                completed={f:f.read_bytes() for f in (p/'run').rglob('*') if f.is_file()}
                before=loader.call_count;main(path)
                self.assertEqual(loader.call_count,before)
                self.assertTrue(all(f.read_bytes()==b for f,b in completed.items()))
                for result in (p/'run/results').rglob('*.json'):
                    r=unwrap(result);self.assertLessEqual(r['tail_parity_max'],1e-4)
                    self.assertAlmostEqual(r['methods']['ZERO']['loss'],r['native_signal'])
                    self.assertLess(r['endpoints']['identity_max'],1e-12)
                # A different split and changed frozen bytes must fail before model loading.
                invalid=dict(cfg,phase='PILOT')
                with self.assertRaises(ValueError):main(put('bad.json',invalid))
                self.assertEqual(loader.call_count,before)
                fit.write_text('{}')
                with self.assertRaisesRegex(ValueError,'FIT changed'):main(path)
                self.assertEqual(loader.call_count,before)

if __name__=='__main__':unittest.main()
