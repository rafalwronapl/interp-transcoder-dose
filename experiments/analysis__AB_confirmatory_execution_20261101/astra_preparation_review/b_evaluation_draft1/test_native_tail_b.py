"""Exact tail/full equivalence at two nonlast layers; random model only."""
import json,unittest
import numpy as np
import torch
from transformers import Gemma3TextConfig,Gemma3ForCausalLM
from .native_tail_b import ExactTail,encode,decode

class TailTests(unittest.TestCase):
    def test_tail_dynamic_attention_and_gradient(self):
        torch.set_num_threads(2);torch.manual_seed(712)
        cfg=Gemma3TextConfig(vocab_size=128,hidden_size=32,intermediate_size=64,num_hidden_layers=4,
            num_attention_heads=2,num_key_value_heads=1,head_dim=16,sliding_window=4,
            layer_types=['sliding_attention','sliding_attention','full_attention','sliding_attention'])
        model=Gemma3ForCausalLM(cfg).eval().float();rng=np.random.default_rng(712)
        for layer in [1,2]:
            tail=ExactTail(model,layer,[10,20]);ids=[2,13,24,35,46,57]
            record=tail.capture(ids);record=json.loads(json.dumps(record,allow_nan=False))
            before=json.dumps(record,sort_keys=True);y=np.asarray(record['states']['y'])
            self.assertAlmostEqual(tail.margin(record,y),record['states']['margin'],places=6)
            delta=rng.normal(size=y.shape)
            for dose in [.05,2.]:
                target=(y+dose*delta).astype(np.float32)
                exact=tail.margin(record,target)
                full=tail.native.forward(ids,'output',target,full_head=True)['margin'][0]
                np.testing.assert_allclose(exact,full,atol=1e-6,rtol=1e-6)
                g=tail.gradient(record,target)['gradient']
                reference=tail.native.gradient(ids,target[None])[0]
                np.testing.assert_allclose(g,reference,atol=1e-6,rtol=1e-5)
            self.assertEqual(before,json.dumps(record,sort_keys=True));tail.close()

    def test_masks_preserve_nonfinite_bytes(self):
        x=torch.tensor([0.,float('-inf'),torch.finfo(torch.float32).min])
        restored=decode(json.loads(json.dumps(encode(x),allow_nan=False)))
        self.assertEqual(x.numpy().tobytes(),restored.numpy().tobytes())

if __name__=='__main__':unittest.main()
