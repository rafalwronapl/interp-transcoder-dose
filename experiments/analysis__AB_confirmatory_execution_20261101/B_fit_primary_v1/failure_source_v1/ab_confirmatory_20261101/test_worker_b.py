"""Actual B FIT runner on random tiny Gemma only; never pretrained weights."""
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import torch
from transformers import Gemma3TextConfig,Gemma3ForCausalLM
from .worker_b import main,schedule
from .transcoder import Transcoder

class WorkerBTests(unittest.TestCase):
    def test_two_gates_fit_replay_and_scope(self):
        torch.set_num_threads(2);torch.manual_seed(184)
        cfg=Gemma3TextConfig(vocab_size=128,hidden_size=32,intermediate_size=64,num_hidden_layers=3,
            num_attention_heads=2,num_key_value_heads=1,head_dim=16,sliding_window=32,
            layer_types=['sliding_attention','sliding_attention','full_attention'])
        model=Gemma3ForCausalLM(cfg).eval().float()
        state={k:torch.randn(*s)*.1 for k,s in dict(w_enc=(32,48),b_enc=(48,),w_dec=(48,32),b_dec=(32,),
            threshold=(48,),affine_skip_connection=(32,32)).items()}
        tc=Transcoder(state);docs=[];tokens={}
        for block in range(4):
            for frame in ['so','when']:
                for side in [0,1]:
                    i=f'{block}_{frame}_{side}'
                    docs.append(dict(id=i,donor=f'{block}_{frame}_{1-side}',block=f'b{block}',study='B',
                        cohort='r0',split='FIT',frame=frame,side=side,text=i))
                    tokens[i]=dict(ids=[2,11+block,25 if frame=='so' else 27,41+side],answer_ids=[10,20])
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            def put(name,value):
                dest=p/name;dest.write_text(json.dumps(value));return str(dest)
            config=dict(study='B',phase='FIT_ONLY',corpus=put('corpus.json',dict(documents=docs)),
                tokens=put('tokens.json',tokens),model_identity=put('identity.json',dict(B=dict(folder='random',files={}),TC=dict(folder='mockTC',files={}))),
                output=str(p/'run'),threads=2,expected_documents=len(docs),layer=1,answer_ids=[10,20],
                control_documents=[d['id'] for d in docs if d['block']=='b0'],
                gates=dict(fd_base=1e-5,fd_relative=.02,branch_relative=1e-4,sham_abs=1e-5,margin_parity=1e-4))
            config['schedule']=put('schedule.json',schedule(config,docs));path=put('config.json',config)
            with patch('transformers.AutoModelForCausalLM.from_pretrained',return_value=(model,{})) as loader,patch('ab_confirmatory_20261101.transcoder.load',return_value=tc):
                main(path);self.assertEqual(loader.call_count,1)
                original={x:x.read_bytes() for x in (p/'run').rglob('*') if x.is_file()}
                main(path);self.assertEqual(loader.call_count,1)
                self.assertTrue(all(x.read_bytes()==v for x,v in original.items()))
                changed=dict(config,threads=3)
                with self.assertRaises(ValueError):main(put('mismatched.json',changed))
                self.assertEqual(loader.call_count,1)
                fit=json.loads((p/'run/FIT_B.json').read_text())['payload']
                self.assertEqual(len(fit['cells']),36)
                self.assertAlmostEqual(np.linalg.norm(fit['direction']),1.)
                records=[json.loads(x)['record'] for x in (p/'run/ledger.jsonl').read_text().splitlines()]
                attempts=[x for x in records if x['event']=='attempt']
                self.assertEqual(len(attempts),len(schedule(config,docs)['operations']))
                ids=[x['operation'] for x in attempts]
                # Full qualification precedes noncontrol capture; final
                # projected JVP follows the complete natural FIT acquisition.
                self.assertLess(ids.index('tc_reference_0_when_1'),ids.index('capture_1_so_0'))
                self.assertGreater(ids.index('jvp_0_so_0_projected'),ids.index('capture_3_when_1'))
                bad=dict(config,phase='TEST');badpath=put('bad.json',bad)
                with self.assertRaises(ValueError):main(badpath)
                self.assertEqual(loader.call_count,1)
                # A corrupted encoder must not pass the independent formula
                # merely by returning the same wrong preactivation to it.
                mutant=dict(config,output=str(p/'mutant'))
                mutantpath=put('mutant.json',mutant)
                def wrong_encoder(z):
                    pre=z@tc.wenc+tc.benc+.5;mask=pre>tc.threshold
                    return (torch.relu(pre)*mask)@tc.wdec+tc.bdec+z@tc.skip,pre,mask
                with patch.object(tc,'forward',side_effect=wrong_encoder):
                    with self.assertRaisesRegex(ValueError,'gate1 failed'):main(mutantpath)
                self.assertEqual(loader.call_count,2)
                self.assertFalse((p/'mutant/FIT_B.json').exists())
                # Corruption cannot be treated as completed cache.
                (p/'run/FIT_B.json').write_text('{}')
                with self.assertRaises(ValueError):main(path)
                self.assertEqual(loader.call_count,2)

if __name__=='__main__':unittest.main()
