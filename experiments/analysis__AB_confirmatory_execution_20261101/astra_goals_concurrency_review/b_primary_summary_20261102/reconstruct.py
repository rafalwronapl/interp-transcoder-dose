import json,hashlib,math
from pathlib import Path
import numpy as np
R=Path.cwd();B=R/'analysis/AB_confirmatory_execution_20261101';P=B/'B_descriptive_TEST_v8';A=B/'astra_goals_concurrency_review/b_test_descriptive_closed_recipients';O=Path(__file__).resolve().parent
methods=['TC','TAYLOR','ZERO','MEAN','RIDGE','FROZEN'];settings=[('full',4,1.),('full',0,.05),('projected',4,1.)]
S=np.full((256,2,2,3),np.nan);E=np.full((256,2,2,3,6),np.nan);signed=np.full_like(E,np.nan);V=np.full_like(E,np.nan);files={};proofs={}
for bi in range(256):
 for ti,frame in enumerate(['so','when']):
  for side in [0,1]:
   doc=f'B_TEST_{bi:04d}_{frame}_s{side}';pf=A/(doc+'.json');raw=pf.read_bytes();proof=json.loads(raw);assert proof['document']==doc and proof['result_cells']==12;proofs[pf.relative_to(R).as_posix()]=hashlib.sha256(raw).hexdigest()
   for ci,(op,j,dose) in enumerate(settings):
    path=P/'run/results'/doc/f'{op}_{j}.json';raw=path.read_bytes();name=path.relative_to(R).as_posix();h=hashlib.sha256(raw).hexdigest();assert proof['files'][name]==h;files[name]=h;q=json.loads(raw)['payload'];assert q['operator']==op and q['dose']==dose and q['document']['id']==doc and q['document']['side']==side and q['document']['frame']==frame
    S[bi,ti,side,ci]=q['native_signal'];assert q['native_signal']==q['native_change']**2
    for mi,m in enumerate(methods):
     v=q['methods'][m];E[bi,ti,side,ci,mi]=v['loss'];assert v['loss']==(v['finite']-q['native_change'])**2; signed[bi,ti,side,ci,mi]=v['finite']-q['native_change'];V[bi,ti,side,ci,mi]=v['vector_error']
 if (bi+1)%64==0:print('blocks checked',bi+1,flush=True)
assert len(files)==3072 and np.isfinite(S).all() and np.isfinite(E).all()
summary=[]
for ci,(op,j,dose) in enumerate(settings):
 for ti,label in [(None,'equal_so_when_mixture'),(0,'so'),(1,'when')]:
  sn=S[:,:,:,ci] if ti is None else S[:,ti,:,ci];en=E[:,:,:,ci,:] if ti is None else E[:,ti,:,ci,:];sg=signed[:,:,:,ci,:] if ti is None else signed[:,ti,:,ci,:];vv=V[:,:,:,ci,:] if ti is None else V[:,ti,:,ci,:];signal=float(sn.mean());err=en.mean(axis=tuple(range(en.ndim-1)));sv=sg.mean(axis=tuple(range(sg.ndim-1)));ve=vv.mean(axis=tuple(range(vv.ndim-1)))
  summary.append(dict(operator=op,dose=dose,frame=label,blocks=256,records=1024 if ti is None else 512,mean_native_energy=signal,native_RMS=math.sqrt(signal),methods={m:dict(MSE=float(err[k]),relative_MSE=float(err[k]/signal),absolute_RMSE=math.sqrt(float(err[k])),relative_RMSE=math.sqrt(float(err[k]/signal)),mean_signed_error=float(sv[k]),mean_vector_squared_error=float(ve[k]),fraction_records_error_above_ZERO=float((en[...,k]>sn).mean())) for k,m in enumerate(methods)}))
main=[x for x in summary if x['frame']=='equal_so_when_mixture'];full,small,proj=main
b2=math.log(small['methods']['TC']['relative_MSE'])-math.log(full['methods']['TC']['relative_MSE'])
contrasts=dict(B1_full_c1_native_minus_TC=full['mean_native_energy']-full['methods']['TC']['MSE'],B1_full_c1_Taylor_minus_TC=full['methods']['TAYLOR']['MSE']-full['methods']['TC']['MSE'],B2_small_vs_c1_log_relative_energy=b2,B2_small_over_c1_relative_energy_ratio=math.exp(b2),B3_projected_c1_native_minus_TC=proj['mean_native_energy']-proj['methods']['TC']['MSE'],B3_projected_c1_Taylor_minus_TC=proj['methods']['TAYLOR']['MSE']-proj['methods']['TC']['MSE'])
report=dict(scope='Independent descriptive reconstruction only; no population inference/pvalues/Holm/bootstrap. Equal block/template/side weights; ratios of pooled mean energies, not mean individual ratios. B has no method P; MEAN/RIDGE are fitted baselines.',blocks=256,records_read=3072,summary=summary,finite_contrasts=contrasts,model_calls=0,bootstrap_calls=0)
(O/'independent_summary.json').write_text(json.dumps(report,indent=2)+'\n');(O/'source_manifest.json').write_text(json.dumps(dict(files=files,reused_recipient_proofs=proofs,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n');print(json.dumps(dict(main=main,contrasts=contrasts),indent=2),flush=True)
