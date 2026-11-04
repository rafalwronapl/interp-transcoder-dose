"""Read-only arithmetic/provenance audit of complete immutable recipient groups."""
import json,hashlib,sys
from pathlib import Path
import numpy as np
from threadpoolctl import threadpool_limits
threadpool_limits(1)
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from research_checks.gate import digest
from research_checks.persistence import request_key
from ab_confirmatory_20261101.baselines_b import predict
STAGE=ROOT/'analysis/AB_confirmatory_execution_20261101/B_descriptive_TEST_v8';RUN=STAGE/'run'
OUT=Path(__file__).parent/'b_test_descriptive_closed_recipients';OUT.mkdir(exist_ok=True)
cfg=json.loads((STAGE/'config.json').read_text());docs=json.loads((STAGE/'corpus.json').read_text())['documents'];tokens=json.loads((STAGE/'tokens.json').read_text())
hashes={}
for artifact in [STAGE/'config.json',STAGE/'corpus.json',STAGE/'tokens.json',Path(__file__)]:
 hashes[artifact.relative_to(ROOT).as_posix()]=hashlib.sha256(artifact.read_bytes()).hexdigest()
assert cfg['phase']=='TEST' and cfg['scientific_objective_v8']=='fixed256_B_descriptive_TEST_no_family_inference' and cfg['primary_inference_authorized'] is False
assert len(docs)==1536 and len({d['block'] for d in docs})==256
def receipt(p):
 raw=p.read_bytes();hashes[p.relative_to(ROOT).as_posix()]=hashlib.sha256(raw).hexdigest();obj=json.loads(raw)
 assert digest(obj['payload'])==obj['payload_sha256'],p
 return obj['payload']
identity=receipt(RUN/'identity.json');fit=receipt(ROOT/cfg['frozen_fit']);assert hashes[cfg['frozen_fit']]==cfg['frozen_fit_sha256'];direction=np.asarray(fit['direction']);base_hashes=dict(hashes)
def close(a,b):np.testing.assert_allclose(a,b,rtol=1e-11,atol=1e-9)
for doc in docs:
 i=doc['id'];folder=RUN/'results'/i;out=OUT/(i+'.json')
 expected={f'{op}_{j}.json' for op in ['full','projected'] for j in range(6)}
 if not folder.exists() or not expected.issubset({p.name for p in folder.glob('*.json')}):continue
 if out.exists():
  prior=json.loads(out.read_text());assert prior['document']==i and prior['identity_digest']==digest(identity)
  assert all(prior['files'].get(k)==v for k,v in base_hashes.items())
  continue
 hashes=dict(base_hashes);memo={};operations=set()
 def operation(name,d,settings):
  cp=receipt(RUN/'completed'/(name+'.json'));assert cp['operation']==name;operations.add(name)
  key=cp['request'];p=RUN/'cache'/(key+'.json')
  if key not in memo:memo[key]=receipt(p)
  q=memo[key];req=dict(model_identity=identity['model'],code_identity=identity['code'],document=dict(document=d,tokens=tokens[d['id']]),intervention=settings,readout=dict(answer_ids=cfg['answer_ids'],orientation='she-minus-he'))
  assert q['request']==req and request_key(req)==key,name
  return q['result']
 donor_doc=next(d for d in docs if d['id']==doc['donor'])
 cap=operation('capture_'+i,doc,dict(mode='natural_with_exact_boundary'));donor=operation('capture_'+doc['donor'],donor_doc,dict(mode='natural_with_exact_boundary'))
 state=cap['states'];z=np.asarray(state['x']);y=np.asarray(state['y']);delta=np.asarray(donor['states']['x'])-z
 gradient=operation('tail_gradient_'+i,doc,dict(mode='tail_gradient',output=y.tolist()));g=np.asarray(gradient['gradient']);parity=abs(gradient['margin']-state['margin']);assert parity<=cfg['gates']['margin_parity']
 operation('tail_backward_'+i,doc,dict(mode='tail_gradient',output=y.tolist()))
 base=operation('tc_base_'+i,doc,dict(mode='TC_base'));tc0=np.asarray(base['output']);nbase=None;max_anchor=0.;max_fp32=0.
 for op,v in [('full',delta),('projected',(delta@direction)*direction)]:
  deriv=operation(f'jvp_{i}_{op}',doc,dict(mode='native_JVP',delta=v.tolist()));n0=np.asarray(deriv['primal']);tangent=np.asarray(deriv['tangent'])
  anchor=float(np.linalg.norm(n0-y)/np.linalg.norm(y));assert np.isfinite(anchor) and anchor<=cfg['gates']['branch_relative'];max_anchor=max(max_anchor,anchor)
  if nbase is not None:assert np.array_equal(nbase,n0)
  nbase=n0
  frozen=np.asarray(operation(f'frozen_{i}_{op}',doc,dict(mode='frozen_TC_direction',delta=v.tolist())))
  for j,c in enumerate(cfg['doses']):
   tag=f'{i}_{op}_{j}';edit=c*v
   n1=np.asarray(operation('native_endpoint_'+tag,doc,dict(mode='native_endpoint',edit=edit.tolist())))
   t1=np.asarray(operation('tc_endpoint_'+tag,doc,dict(mode='TC_endpoint',edit=edit.tolist())))
   pred=dict(NATIVE=n1-n0,TC=(t1.astype(np.float32)-tc0.astype(np.float32)).astype(float),TAYLOR=(np.float32(c)*tangent.astype(np.float32)).astype(float),FROZEN=(np.float32(c)*frozen.astype(np.float32)).astype(float))
   cell=('pooled' if doc['frame']=='transfer' else doc['frame'])+f'_{op}_{j}'
   pred.update({k.upper():value for k,value in predict(fit['cells'][cell],edit,doc['side']).items()})
   margins={}
   for method,value in pred.items():
    assert np.isfinite(value).all();target=(y+value).astype(np.float32)
    margins[method]=operation(f'tail_{tag}_{method}',doc,dict(mode='tail_output',target=target.tolist(),method=method))-state['margin']
   result=receipt(folder/f'{op}_{j}.json');truth=margins['NATIVE']
   assert result['document']==doc and result['operator']==op and result['dose']==c and result['tail_parity_max'] is None
   assert set(result['methods'])=={'TC','FROZEN','TAYLOR','MEAN','RIDGE','ZERO'}
   close(result['native_change'],truth);close(result['native_signal'],truth**2)
   for method,value in pred.items():
    if method=='NATIVE':continue
    expected_method=dict(finite=margins[method],loss=float((margins[method]-truth)**2),vector_error=float(np.sum((value-pred['NATIVE'])**2)),linear_native=float(g@pred['NATIVE']),linear_predicted=float(g@value),linear_vs_linear_error=float((g@(value-pred['NATIVE']))**2),linear_vs_finite_error=float((g@value-truth)**2))
    assert set(result['methods'][method])==set(expected_method)
    for k,val in expected_method.items():close(result['methods'][method][k],val)
   for k,val in dict(finite=0.,loss=truth**2,vector_error=float(np.sum(pred['NATIVE']**2))).items():close(result['methods']['ZERO'][k],val)
   e0=tc0-n0;e1=t1-n1;error=(t1-tc0)-(n1-n0);end=result['endpoints']
   for k,val in dict(e0=e0,e1=e1,energy0=e0@e0,energy1=e1@e1,mixed=-2*e1@e0,delta_error_energy=error@error,identity_max=np.max(np.abs(error-(e1-e0))),fp32_delta_discrepancy_max=np.max(np.abs(pred['TC']-(t1-tc0)))).items():close(end[k],val)
   close(end['delta_error_energy'],end['energy0']+end['energy1']+end['mixed'])
   for k,val in dict(margin_absolute=parity,branch_relative=anchor,branch_absolute=np.max(np.abs(n0-y))).items():close(result['anchors'][k],val)
   max_fp32=max(max_fp32,end['fp32_delta_discrepancy_max'])
 report=dict(document=i,block=doc['block'],frame=doc['frame'],side=doc['side'],result_cells=12,methods=6,operations_checked=len(operations),files=hashes,identity_digest=digest(identity),maximum_branch_relative=max_anchor,maximum_fp32_delta_discrepancy=max_fp32,reviewer='/root/astra_goals_and_concurrency_review',scope='Complete immutable recipient only. All consumed payload/file hashes and exact operation request identities; saved endpoints, native anchors, fixed linear-baseline predictions, targets, losses and linear diagnostics checked. No model/TC forward, bootstrap or scientific inference; no live ledger/STATUS read. Provisional audit pending final closure.')
 out.write_text(json.dumps(report,indent=2)+'\n')
 if sum(1 for _ in OUT.glob('B_*.json'))%16==0:print(i+' audited',flush=True)
print('CLOSED recipient receipts',sum(1 for _ in OUT.glob('B_*.json')),'of1536; incomplete groups skipped',flush=True)
