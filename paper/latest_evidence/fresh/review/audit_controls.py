import json
from pathlib import Path
import numpy as np
from research_checks.gate import read,digest
from analysis.B_fresh_transfer_20261103.common import unwrap,source
R=Path(__file__).resolve().parents[3];B=R/'analysis/B_fresh_transfer_20261103';O=B/'run'
ledger=[json.loads(l)['record'] for l in (O/'ledger.jsonl').read_text().splitlines()];ats={r['operation']:r for r in ledger if r['event']=='attempt'}
def op(n):return unwrap(O/'cache'/(ats[n]['request']+'.json'))
for k,e in enumerate(read(B/'controls.json')):
 rec=source(e['capture'])['result'];g=np.asarray(source(e['gradient'])['result']['gradient']);y=np.asarray(rec['states']['y']);gn=np.linalg.norm(g);h=.25*min(1e-3*max(1,np.linalg.norm(y)),.01/gn);targets=[y,y+h*g/gn,y-h*g/gn,y];v=[]
 for j,t in enumerate(targets):
  c=op('control_'+str(4*k+j));np.testing.assert_array_equal(c['request']['intervention']['target'],t.astype(np.float32));v.append(c['result'])
 assert abs(v[0]-rec['states']['margin'])<=1e-4 and abs(v[3]-v[0])<=1e-4 and v[1]-v[0]>1e-4 and v[2]-v[0]<-1e-4
 assert unwrap(O/'controls'/f'{k}.json')['values']==v
errors={}
for frame in ['so','when','transfer','object']:
 for side in [0,1]:
  d=next(d for d in read(B/'corpus.json')['documents'] if d['frame']==frame and d['side']==side);rec=op(d['id']+'_capture')['result'];p=op('fresh_parity_'+frame+'_s'+str(side));np.testing.assert_array_equal(p['request']['intervention']['target'],np.asarray(rec['states']['y'],np.float32));err=abs(p['result']-rec['states']['margin']);assert err<=1e-4;errors[frame+str(side)]=err
out=dict(passed=True,historical_control_calls=8,new_quarter_step_signed_probes=4,fresh_fullhead_suffix_parities=8,errors=errors,pretrained_calls=0)
(B/'review/independent_controls_audit.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
