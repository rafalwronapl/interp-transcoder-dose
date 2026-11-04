import tempfile,json
from pathlib import Path
import numpy as np
from .common import *
from .worker import execute,preflight
from ab_confirmatory_20261101.runtime import Runtime
class Tail:
    def __init__(self):self.calls=0
    def capture(self,d):
        self.calls+=1;x=[float(d['side']),0.,0.];return dict(answer_ids=d['answer_ids'],states=dict(x=x,y=x,margin=x[0]))
    def margin(self,r,t):self.calls+=1;return float(np.asarray(t)@np.array([1.,2.,3.]))
class TC:
    threshold=np.array([1.]);decoder=np.array([[1.,2.,3.]])
    def encode(self,z):p=2*float(z[0]);return dict(pre=[p],output=(max(p,0)*(p>1)*self.decoder[0]).tolist())
def main():
    docs=[dict(id='d'+str(s),donor='d'+str(1-s),block='b',frame='so',side=s,ids=[s],answer_ids=[1,2]) for s in [0,1]]
    ops=dict(operations=[dict(id='control_'+str(i),kind='forward') for i in range(8)]+[dict(id='fresh_parity_so_s'+str(s),kind='forward') for s in [0,1]]+[dict(id=d['id']+'_'+a,kind='forward') for d in docs for a in ['capture','tcbase','tcend','nativebranch','NATIVE','FULL']+ARMS])
    controls=[dict(record=dict(answer_ids=[1,2],states=dict(y=[1.,2.,3.],margin=14.)),document=dict(id='FIT'+str(k)),gradient=[1.,2.,3.]) for k in range(2)]
    identity=dict(model='synthetic',code='synthetic');cfg=dict(rho=1.,eps=.25)
    with tempfile.TemporaryDirectory() as temp:
        out=Path(temp);tail=Tail();account,result=execute(out,docs,controls,cfg,[[0]]*6,identity,ops,tail,TC(),lambda x:x.tolist())
        assert result['so']['eligible_contexts']==1 and result['so']['excluded_contexts']==1
        assert result['so']['primary_top_minus_controls']==0
        assert account['skips']==6 and account['aliases']==5
        freeze=unwrap(out/'TARGETS_FROZEN.json');assert freeze['before_any_native_endpoint'] and freeze['before_any_scientific_suffix']
        ledger=[json.loads(l)['record'] for l in (out/'ledger.jsonl').read_text().splitlines()]
        from datetime import datetime
        freeze_time=json.loads((out/'TARGETS_FROZEN.json').read_text())['created_utc']
        assert all(r['utc']>=freeze_time for r in ledger if r['event']=='attempt' and any(r['operation'].endswith('_'+a) for a in ['NATIVE','FULL','nativebranch']+ARMS))
        before={p.relative_to(out).as_posix():p.read_bytes() for p in out.rglob('*') if p.is_file()};calls=tail.calls
        assert execute(out,docs,controls,cfg,[[0]]*6,identity,ops,tail,TC(),lambda x:x.tolist())==(account,result) and tail.calls==calls
        assert before=={p.relative_to(out).as_posix():p.read_bytes() for p in out.rglob('*') if p.is_file()}
    with tempfile.TemporaryDirectory() as temp:
        out=Path(temp);rt=Runtime(out,identity,ops);rt.record(dict(event='attempt',operation='control_0',kind='forward',request='x'))
        try:preflight(out,identity,ops)
        except ValueError:pass
        else:raise AssertionError('Uncertain reservation accepted')
    (HERE/'fixtures.json').write_text(json.dumps(dict(passed=True,hooks=True,data=True,pilot=True,accounting=True,restart=True,checks=['actual_execute_global_target_freeze','fresh_fullhead_tail_parity','joint_all6_exclusion','alias_accounting','block_aggregation','eight_signed_FIT_controls','byte_identical_complete_replay','uncertain_attempt_blocks_load']),indent=2)+'\n',encoding='utf-8')
    print('synthetic PASS')
if __name__=='__main__':main()

