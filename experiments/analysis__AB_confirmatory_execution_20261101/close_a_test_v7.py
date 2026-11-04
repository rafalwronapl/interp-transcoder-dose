"""Mechanical closure of completed A TEST; no model/replay/statistical analysis."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];S=R/'analysis/A_estimation_v7/TEST_v1';V=R/'analysis/A_estimation_v7/recovery_status_v1'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def wr(p,x):
 with p.open('x',encoding='utf-8') as f:json.dump(x,f,indent=2)
def main():
 sealed=rd(S/'run/stage_completed.json');assert sealed['payload']['attempted_operations']==35840
 matches=[p for p in (R/'operations/concurrency_runtime_v1').glob('launch_*.json') if rd(p).get('pid')==5708]
 assert len(matches)==1;runtime=matches[0];assert rd(runtime)['returncode']==0
 files=dict(rd(V/'pre_run_snapshot_v1.json')['payload']['files'])
 for n,h in rd(S/'pre_run_snapshot_v1.json')['payload']['files'].items():
  assert n not in files or files[n]==h,(n,'conflict')
  files[n]=h
 for n,h in sealed['payload']['files'].items():files[(S/'run'/n).relative_to(R).as_posix()]=h
 summary=dict(blocks=256,documents=5120,full_transformer=5120,local_suffix=30720,forward=35840,backward=0,reused_charged_prefix=501,new_recovery_forward=35339,refits=0,new_PILOT_operations=0,TEST_N=256,scope='Fixed resource-capped estimation amendment; original power infeasibility retained; no80percent joint-power assurance',runtime_returncode=0,independent_completion_review='pending')
 wr(S/'completion_summary_v1.json',summary)
 (S/'REPORT_COMPLETION_v1.md').write_text('# A fixed256 TEST acquisition completion\n\nAll5120 documents/256 prespecified TEST blocks completed5120 full-transformer and30720 local suffix operations,0backward. Original501durable operations were reused cache-only after the preserved STATUS publication failure; recovery computed only35339 remaining forward operations. Original source/config/measurement identities and designatedr0 FIT were unchanged. No FIT/PILOT/model prefix was repeated.\n\nThis is the user-authorized fixed resource-capped estimation amendment. Original frozen joint-power infeasibility remains a negative finding; no80percent joint-power or target precision assurance is claimed. Acquisition closure supplies no hypothesis conclusion. All3hypotheses and negative/wide intervals remain for the separately reviewed analysis. Independent acquisition acceptance is pending.\n',encoding='utf-8')
 for folder in [S,V]:
  for p in folder.iterdir():
   if p.is_file() and not p.name.startswith('completion_'):files[p.relative_to(R).as_posix()]=sha(p)
 for p in [S/'completion_summary_v1.json',S/'run/stage_completed.json',runtime]:files[p.relative_to(R).as_posix()]=sha(p)
 wr(S/'completion_outputs_manifest_v1.json',dict(files=files))
 c=rd(V/'contract.json');c['id']='A_ESTIMATION_TEST_COMPLETION_V7';c['purpose']='Acceptance of fixed256 acquisition35840F0B, including501cache-only prefix and35339recoveryF; no hypothesis claim.';c['input_manifests'].append((S/'completion_outputs_manifest_v1.json').relative_to(R).as_posix());wr(S/'completion_contract_v1.json',c)
 print(json.dumps(summary))
if __name__=='__main__':main()
