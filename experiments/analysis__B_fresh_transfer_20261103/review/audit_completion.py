import json
from pathlib import Path
from collections import Counter
import numpy as np
from safetensors import safe_open
from research_checks.gate import read,sha,digest
from analysis.B_fresh_transfer_20261103.common import unwrap
R=Path(__file__).resolve().parents[3];B=R/'analysis/B_fresh_transfer_20261103';O=B/'run';done=unwrap(O/'stage_completed.json')
for p,h in done['files'].items():assert sha(O/p)==h
ledger=[]
for l in (O/'ledger.jsonl').read_text().splitlines():
 e=json.loads(l);assert digest(e['record'])==e['sha256'];ledger.append(e['record'])
attempts={e['operation']:e for e in ledger if e['event']=='attempt'};assert len(attempts)==sum(e['event']=='attempt' for e in ledger)
def op(k):
 e=attempts[k];v=unwrap(O/'cache'/(e['request']+'.json'));assert digest(v['request'])==e['request'];return v
seal=json.loads((O/'TARGETS_FROZEN.json').read_text());freeze=unwrap(O/'TARGETS_FROZEN.json')
for p,h in freeze['files'].items():assert sha(O/p)==h
cfg=read(B/'config.json');ident=read(R/cfg['model_identity']);groups=read(R/cfg['groups_source']);groups=[groups['top']]+[g['features'] for g in groups['groups']]
with safe_open(str(Path(ident['TC']['folder'])/'params.safetensors'),framework='numpy') as f:dec=f.get_tensor('w_dec');th=f.get_tensor('threshold')
rows=[];norms=[];alias_count=skip_count=0
for d in read(B/'corpus.json')['documents']:
 tag=d['id'];target=unwrap(O/'targets'/(tag+'.json'));row=unwrap(O/'results'/(tag+'.json'));assert row['document']==d
 base=op(tag+'_tcbase')['result'];end=op(tag+'_tcend')['result'];cap=op(tag+'_capture')['result']
 ref=np.asarray(cap['states']['y'],np.float32)+(np.asarray(end['output'],np.float32)-np.asarray(base['output'],np.float32));np.testing.assert_array_equal(ref,target['reference_target'])
 vs=[]
 for g in groups:
  a=np.asarray(base['pre'])[g];b=np.asarray(end['pre'])[g];v=(np.maximum(b,0)*((b>th[g]).astype(float)-(a>th[g]).astype(float)))@dec[g].astype(float);vs.append(v)
 ns=np.linalg.norm(vs,axis=1);np.testing.assert_allclose(ns,target['raw_norms'],rtol=1e-13,atol=1e-9);assert target['eligible']==bool(np.all(ns>=cfg['eps']))==row['eligible']
 native=np.asarray(op(tag+'_nativebranch')['result'],np.float32);known={};measured={}
 arms=['NATIVE','FULL'];ys=[native,ref]
 if target['eligible']:
  for v,n,t in zip(vs,ns,target['targets']):
   y=(ref.astype(float)-cfg['rho']*v/n).astype(np.float32);np.testing.assert_array_equal(y,t['target']);norms.append(float(np.linalg.norm(y.astype(float)-ref)));ys.append(y)
  arms+=['top32']+['control_'+str(s) for s in range(20261103,20261108)]
 else:skip_count+=6
 for a,y in zip(arms,ys):
  key=y.tobytes();name=tag+'_'+a
  if key in known:
   al=unwrap(O/'aliases'/(name+'.json'));assert al['value']==known[key] and al['target_sha256']==digest(y.tolist());alias_count+=1;value=known[key]
  else:
   cache=op(name);np.testing.assert_array_equal(cache['request']['intervention']['target'],y);assert cache['request']['readout']['answer_ids']==d['answer_ids'];value=cache['result'];known[key]=value
  measured[a]=value
 assert row['native_margin']==measured['NATIVE'] and row['reference_margin']==measured['FULL'];assert row['reference_loss']==(measured['FULL']-measured['NATIVE'])**2
 if target['eligible']:
  for a in arms[2:]:assert row['margins'][a]==measured[a] and row['effects'][a]==measured[a]-measured['FULL'] and row['loss'][a]==(measured[a]-measured['NATIVE'])**2
 rows.append(row)
for name,e in attempts.items():
 if not(name.startswith(('control_','fresh_parity_')) or name.endswith(('_capture','_tcbase','_tcend'))):assert e['utc']>=seal['created_utc']
summary=unwrap(O/'SUMMARY.json');contrasts={}
for frame,s in summary.items():
 rr=[r for r in rows if r['eligible'] and (r['document']['frame'] in ['so','when'] if frame=='primary_so_when' else r['document']['frame']==frame)];blocks=sorted({r['document']['block'] for r in rr});vals=[]
 for b in blocks:
  rs=[r for r in rr if r['document']['block']==b];vals.append(np.mean([r['loss']['top32']-np.mean([r['loss'][a] for a in r['loss'] if a!='top32']) for r in rs]))
 result=float(np.mean(vals)) if vals else None;assert result is None or abs(result-s['primary_top_minus_controls'])<1e-12;assert s['eligible_contexts']==len(rr);contrasts[frame]=result
assert len(rows)==256 and len(attempts)+alias_count+skip_count==3088
result=dict(passed=True,contexts=256,attempts=len(attempts),aliases=alias_count,skips=skip_count,actual_norm_range=[min(norms),max(norms)],contrasts=contrasts,all256targets_recomputed_from_actual_TC_outputs=True,all_actual_or_aliased_suffixes_recomputed=True,global_freeze_before_scientific_calls=True,pretrained_calls=0)
(B/'review/independent_completion_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
