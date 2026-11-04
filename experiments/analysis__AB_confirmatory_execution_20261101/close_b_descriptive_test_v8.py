"""Mechanical B descriptive acquisition closure; no model or statistics rerun."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];S=R/'analysis/AB_confirmatory_execution_20261101/B_descriptive_TEST_v8';P=R/'analysis/AB_confirmatory_execution_20261101/sol_parallel_acceptance/concurrency_migration_v2'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def wr(p,x):
 with p.open('x',encoding='utf-8') as f:json.dump(x,f,indent=2)
def main():
 sealed=rd(S/'run/stage_completed.json');d=sealed['payload'];assert d['attempted_operations']==159744 and d.get('phase',d.get('scope'))=='TEST'
 matches=[p for p in (R/'operations/concurrency_runtime_v1').glob('launch_*.json') if rd(p).get('pid')==16396];assert len(matches)==1;runtime=matches[0];assert rd(runtime)['returncode']==0
 counts=dict(cache=sum(k.startswith('cache/') for k in d['files']),completed=sum(k.startswith('completed/') for k in d['files']),capture_completed=sum(k.startswith('completed/capture_') for k in d['files']),result_cells=sum(k.startswith('results/') for k in d['files']))
 assert counts==dict(cache=158208,completed=159744,capture_completed=1536,result_cells=18432),counts
 summary=dict(blocks=256,documents=1536,forward=158208,backward=1536,logical_operations=159744,counts=counts,cost=rd(S/'cost.json'),new_FIT_calls=0,repeated_prior_measurements=0,runtime_returncode=0,runtime_completed=rd(runtime)['completed_utc'],scope='Fixed256 descriptive TEST; no original Bfamily/Holm/support claims; futureanalysis TCc1v6joint12CIs only',independent_completion_review='pending',scientific_effect_report='Notcomputedbythisclosurehelper')
 wr(S/'completion_summary_v1.json',summary)
 (S/'REPORT_COMPLETION_v1.md').write_text('# B fixed256 descriptive TEST acquisition completion\n\nAll256prespecified blocks/1536documents completed the unchanged qualified native measurement grid:158208forward+1536backward operations, all sixmethods/doses/bothoperators and transfer,18432resultcells. Frozen ownFIT/qualifiedtail were reused without recapture/refit. All159744operations and158208callback caches are durable; final canonical runtime exited0. Cost categories are retained exactly from the frozen cost.json.\n\nThis is the prospectively authorized resource-capped DESCRIPTIVE branch. Both original Bfamily candidateNs remained ineligible; no originalB1-B3family p/Holm/support claim or80percentpower assurance is authorized. No resultstatistic/CI/bootstrap is calculated by this closure. The separately frozen analyzer may report all finite-corpus cells and only the qualified TCc1joint12v6intervals after accepted closure and its own reviewed zeromodelpacket. Independent completion acceptance is pending; all failures/negative controls/transfer remain preserved, no complete-case selection.\n',encoding='utf-8')
 files=dict(rd(S/'pre_run_snapshot_v1.json')['payload']['files']);files.update(rd(P/'snapshot_v1.json')['payload']['files'])
 for n,h in d['files'].items():files[(S/'run'/n).relative_to(R).as_posix()]=h
 for p in list(S.iterdir())+[runtime,S/'run/stage_completed.json',P/'migration_policy.json',P/'snapshot_v1.json',R/'analysis/AB_confirmatory_execution_20261101/astra_goals_concurrency_review/concurrency_review_v2_slots.json']:
  if p.is_file():files[p.relative_to(R).as_posix()]=sha(p)
 events=S/'status_events'
 if events.exists():
  for p in events.glob('*.json'):files[p.relative_to(R).as_posix()]=sha(p)
 wr(S/'completion_outputs_manifest_v1.json',dict(files=files));c=rd(S/'contract.json');c['id']='B_DESCRIPTIVE_ACTUAL_ACQUISITION_COMPLETION_V8';c['purpose']='Acceptanceofcompletefixed2561536doc159744opdescriptiveacquisition; no originalinferentialfamily/CIclaimbyclosure.';c['input_manifests'].append((S/'completion_outputs_manifest_v1.json').relative_to(R).as_posix());wr(S/'completion_contract_v1.json',c)
 print(json.dumps(dict(blocks=256,documents=1536,forward=158208,backward=1536,counts=counts,runtime_returncode=0,review='pending')))
if __name__=='__main__':main()
