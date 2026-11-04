"""Pure geometry and durable-cache regression checks; no pretrained loads."""
from pathlib import Path
import tempfile,json
import numpy as np
from research_checks.persistence import cached,immutable
from ab_confirmatory_20261101.runtime import Runtime
from analysis.B_mechanism_20261102.common import put
from .geometry import residual_target,feature_arms,ARMS

def run():
    checks={}
    n=np.array([2.,3.],np.float32);t=n+[3.,4.]
    target,meta=residual_target(n,t,[100.,200.],[100.,202.])
    assert np.allclose(target,n+[0,5]) and meta['actual_norm']==5
    assert residual_target(n,t,[1,2],[1,2])[0] is None
    checks['same_dose_whole_residual_norm_and_zero']=True
    h,meta=feature_arms([2.,0.,2.,0.],[0.,2.,3.,0.],[1.,1.,1.,1.],[0,1],[2,3])
    assert np.array_equal(h['ONLY_top'],[0,2,3,0])
    assert np.array_equal(h['BASE'],[0,0,3,0])
    assert np.array_equal(h['ON'],[0,2,3,0]) and np.array_equal(h['OFF'],[0,0,3,0])
    assert meta['on']==1 and meta['off']==1
    checks['switch_masks_on_off_negative_relu_and_complements']=True
    with tempfile.TemporaryDirectory() as tmp:
        out=Path(tmp);schedule={'operations':[{'id':'a','kind':'forward'}]};rt=Runtime(out,dict(model='m',code='c'),schedule)
        count=[0]
        def f():count[0]+=1;return [1,2]
        args=('a',dict(id='x'),dict(target=[1,2]),dict(readout='r'),f)
        assert rt.compute(*args)==[1,2];before=(out/'ledger.jsonl').read_bytes()
        rt=Runtime(out,dict(model='m',code='c'),schedule);assert rt.compute(*args)==[1,2] and count==[1]
        assert (out/'ledger.jsonl').read_bytes()==before
        try:rt.compute('a',dict(id='x'),dict(target=[2,2]),dict(readout='r'),f)
        except ValueError:pass
        else:raise AssertionError('Changed target accepted')
        checks['immutable_replay_changed_request_rejected']=True
    with tempfile.TemporaryDirectory() as tmp:
        rt=Runtime(Path(tmp),dict(model='m',code='c'),schedule)
        def fail():raise RuntimeError('simulated after reservation')
        try:rt.compute('a',{},dict(target=0),{},fail)
        except RuntimeError:pass
        rt=Runtime(Path(tmp),dict(model='m',code='c'),schedule)
        try:rt.compute('a',{},dict(target=0),{},lambda:1)
        except ValueError:pass
        else:raise AssertionError('uncertainattempt retried')
        checks['uncertain_reservation_halts']=True
    put(Path(__file__).parent/'fixtures.json',dict(passed=all(checks.values()),checks=checks,pretrained_calls=0))
    print(checks)
if __name__=='__main__':run()
