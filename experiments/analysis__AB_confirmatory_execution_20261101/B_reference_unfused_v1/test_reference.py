"""Actual reference arithmetic check with random weights only."""
import sys,json
from pathlib import Path
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root))
import torch,numpy as np
from ab_confirmatory_20261101.reference_b_unfused import reference
from ab_confirmatory_20261101.transcoder import Transcoder
torch.set_num_threads(2);torch.manual_seed(190)
state={k:torch.randn(*s) for k,s in dict(w_enc=(16,64),b_enc=(64,),w_dec=(64,16),b_dec=(16,),threshold=(64,),affine_skip_connection=(16,16)).items()}
errors=[]
for skip in [True,False]:
    local=dict(state)
    if not skip:local.pop('affine_skip_connection')
    tc=Transcoder(local)
    for scale in [1.,100.]:
        z=torch.randn(16)*scale;expected=reference(local,z);actual=tc.forward(z)[0].double().numpy()
        np.testing.assert_array_equal(expected,actual);errors.append(float(np.max(np.abs(expected-actual))))
p=Path(__file__).parent
(p/'reference_test.json').write_text(json.dumps(dict(random_only=True,pretrained_calls=0,cases=len(errors),maximum_errors=errors,passed=True),indent=2)+'\n')
print(json.dumps(dict(passed=True,cases=len(errors),pretrained_calls=0)))
