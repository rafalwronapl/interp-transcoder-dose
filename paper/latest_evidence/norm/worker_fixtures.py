"""Exercise actual suffix-worker pipeline with a synthetic linear suffix."""
import tempfile
from pathlib import Path
import numpy as np
from .common import HERE,put,sha,normalize_targets
from .worker import execute,ARMS,guarded_load
from ab_confirmatory_20261101.runtime import Runtime

class FakeTail:
    def __init__(self):self.calls=0
    def margin(self,record,target):self.calls+=1;return float(np.asarray(target,float)@np.array([1.,2.,3.]))

def run():
    checks={};tail=FakeTail();g=np.array([1.,2.,3.]);controls=[]
    for k in range(2):
        y=np.array([1.,2.,3.])+k;controls.append(dict(record=dict(states=dict(y=y.tolist(),margin=float(y@g))),document=dict(id='FIT_'+str(k)),gradient=g.tolist()))
    items=[]
    for k,frame in enumerate(['so','when']):
        ref=np.array([2.,3.,4.])+k;result=normalize_targets(ref,[[1.,2.,3.]]*6,1.,.25)
        if k==1:result.update(eligible=False,under_eps_groups=[0],targets=[])
        result.update(cell='cell'+str(k),document=dict(id='TEST_'+str(k),block='block'+str(k),frame=frame),reference_target=ref.tolist(),reference_margin=float(ref@g),native_margin=float(ref@g)-.3,record=dict(states=dict(y=ref.tolist(),margin=float(ref@g))))
        items.append(result)
    ops=dict(operations=[dict(id='control_'+str(k)+'_'+arm,kind='forward') for k in range(2) for arm in ['sham','plus','minus']]+
             [dict(id='reference_parity_'+str(k),kind='forward') for k in range(2)]+
             [dict(id=i['cell']+'_'+a,kind='forward') for i in items for a in ARMS])
    with tempfile.TemporaryDirectory() as temp:
        out=Path(temp);identity=dict(model='synthetic',code='synthetic')
        accounting,summary=execute(out,items,controls,tail,identity,ops,items)
        assert accounting==dict(forward_attempts=9,backward_attempts=0,aliases=5,skips=6)
        assert summary['eligible_contexts']==summary['eligible_blocks']==1 and summary['excluded_contexts']==1
        assert abs(summary['primary_top_minus_controls'])<1e-12
        checks['actual_worker_controls_aliases_joint_skips_block_summary']=True
        before={p.relative_to(out).as_posix():p.read_bytes() for p in out.rglob('*') if p.is_file()};calls=tail.calls
        assert execute(out,items,controls,tail,identity,ops,items)==(accounting,summary) and tail.calls==calls
        assert before=={p.relative_to(out).as_posix():p.read_bytes() for p in out.rglob('*') if p.is_file()}
        checks['actual_worker_replay_no_new_calls_byte_identical_receipts']=True
    with tempfile.TemporaryDirectory() as temp:
        rt=Runtime(Path(temp),dict(model='m',code='c'),dict(operations=[dict(id='failed',kind='forward')]))
        def fail():raise RuntimeError('Simulated failure after reservation')
        args=('failed',dict(id='x'),dict(target=[1]),dict(answer_ids=[1,2]),fail)
        try:rt.compute(*args)
        except RuntimeError:pass
        else:raise AssertionError('Failure missing')
        rt=Runtime(Path(temp),dict(model='m',code='c'),dict(operations=[dict(id='failed',kind='forward')]))
        try:rt.compute(*args)
        except ValueError:pass
        else:raise AssertionError('Uncertain reservation retried')
        checks['uncertain_attempt_fail_closed_no_rerun']=True
        load_calls=[]
        try:guarded_load(Path(temp),dict(model='m',code='c'),dict(operations=[dict(id='failed',kind='forward')]),lambda:load_calls.append(1))
        except ValueError:pass
        else:raise AssertionError('Uncertain attempt reached loader')
        assert not load_calls
        checks['actual_guard_uncertain_attempt_rejected_before_load']=True
    with tempfile.TemporaryDirectory() as temp:
        out=Path(temp);identity=dict(model='m',code='c');ops=dict(operations=[]);rt=Runtime(out,identity,ops)
        put(out/'stage_completed.json',dict(files={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()}));loads=[]
        assert guarded_load(out,identity,ops,lambda:loads.append(1)) is None and not loads
        try:guarded_load(out,dict(model='m',code='CHANGED'),ops,lambda:loads.append(1))
        except ValueError:pass
        else:raise AssertionError('Stale completed identity accepted')
        assert not loads
        checks['actual_guard_completed_replay_and_changed_identity_before_load']=True
    put(HERE/'worker_fixtures_v2.json',dict(passed=all(checks.values()),checks=checks,native_model_loads=0,TC_model_loads=0,pretrained_calls=0,synthetic_suffix_calls=tail.calls,worker_sha256=sha(HERE/'worker.py')))
    print(checks)
if __name__=='__main__':run()
