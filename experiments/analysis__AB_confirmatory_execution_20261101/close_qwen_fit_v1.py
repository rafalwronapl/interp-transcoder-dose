"""Bind actual Qwen FIT closure/runtime; numerical summary uses approved complete_fit."""
from pathlib import Path
import json,hashlib,sys
R=Path(__file__).resolve().parents[2];S=R/'analysis/A_short_replication_qwen_20261101/FIT_ready_v1';P=S.parent/'workflow_runtime_v4'
sys.path.insert(0,str(R))
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def wr(p,x):
 with p.open('x',encoding='utf-8') as f:json.dump(x,f,indent=2)
def main():
 from a_short_qwen_20261101.complete_fit import summarize
 done=rd(S/'run/stage_completed.json')['payload'];assert done['phase']=='FIT'
 runtime=[p for p in (R/'operations/concurrency_runtime_v1').glob('launch_*.json') if rd(p).get('pid')==4004];assert len(runtime)==1;runtime=runtime[0];assert rd(runtime)['returncode']==0
 summarize(S.relative_to(R).as_posix(),(S/'fit_completion_summary_v1.json').relative_to(R).as_posix())
 summary=dict(blocks=32,FIT_MAP_documents=128,FIT_U_documents=128,full_transformer=280,local_suffix=4,forward=284,backward=0,refits_of_prior_models=0,runtime_returncode=0,scope='Own Qwen r0 FIT only; no PILOT/TEST/result',independent_completion_review='pending')
 wr(S/'completion_summary_v1.json',summary)
 (S/'REPORT_COMPLETION_v1.md').write_text('# Qwen FIT completion\n\nCompleted the exact own-model designatedr0 FIT recipe:128FIT_MAP+128FIT_U documents,32disjointblocks, ridge0.01/rank8 U. Exactly280full-transformer+4local suffix operations,0backwards; four qualification groups must pass before remainingFIT. The approved complete_fit builder verifies source/config/model identity, corpus, controls and fitted recipe against the sealed closure. Actual canonical runtime exit0 is bound. Independent completion acceptance remains pending. No prior model FIT was reused/refit; no PILOT/TEST or effect conclusion is claimed.\n',encoding='utf-8')
 files=dict(rd(S/'pre_run_snapshot_v1.json')['payload']['files'])
 files.update(rd(P/'snapshot_v1.json')['payload']['files'])
 for n,h in done['files'].items():files[(S/'run'/n).relative_to(R).as_posix()]=h
 for p in list(S.iterdir())+list(P.iterdir())+[runtime,S/'run/stage_completed.json']:
  if p.is_file() and not p.name.startswith('completion_outputs') and not p.name.startswith('completion_contract'):files[p.relative_to(R).as_posix()]=sha(p)
 wr(S/'completion_outputs_manifest_v1.json',dict(files=files))
 c=rd(S/'contract.json');c['id']='QWEN_FIT_ACTUAL_COMPLETION_V1';c['purpose']='Actual own-modelr0 FIT completion284F0B, controls/vectorfit, noPILOT/TEST.';c['input_manifests'].append((S/'completion_outputs_manifest_v1.json').relative_to(R).as_posix());wr(S/'completion_contract_v1.json',c)
 print(json.dumps(summary))
if __name__=='__main__':main()


