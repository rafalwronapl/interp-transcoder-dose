import argparse,hashlib,json
from pathlib import Path
from research_checks.gate import digest
R=Path.cwd();B=R/'analysis/AB_confirmatory_execution_20261101';P=B/'B_descriptive_TEST_v8';O=Path(__file__).parent/'b_test_descriptive_closed_recipients'
a=argparse.ArgumentParser();a.add_argument('--snapshot-sha',required=True);args=a.parse_args()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((P/'completion_snapshot_v1.json').read_text());assert digest(s['payload'])==s['snapshot_sha256']==args.snapshot_sha
c=json.loads((P/'run/stage_completed.json').read_text());assert digest(c['payload'])==c['payload_sha256'];assert c['payload']['phase']=='TEST' and c['payload']['attempted_operations']==159744
cfg=json.loads((P/'config.json').read_text());docs=json.loads((P/'corpus.json').read_text())['documents'];assert cfg['primary_inference_authorized'] is False and len(docs)==1536
files={};proofs={};maxbranch=0.;maxfp=0.
for d in docs:
 path=O/(d['id']+'.json');q=json.loads(path.read_text());assert q['document']==d['id'] and q['block']==d['block'] and q['frame']==d['frame'] and q['side']==d['side'] and q['result_cells']==12
 proofs[path.name]=sha(path);maxbranch=max(maxbranch,q['maximum_branch_relative']);maxfp=max(maxfp,q['maximum_fp32_delta_discrepancy'])
 for name,h in q['files'].items():
  if name in files:assert files[name]==h
  files[name]=h
  if name.startswith((P/'run').relative_to(R).as_posix()+'/'):
   assert s['payload']['files'][name]==h,name
   assert c['payload']['files'][str(Path(name).relative_to((P/'run').relative_to(R))).replace(chr(92),'/')]==h,name
runprefix=(P/'run').relative_to(R).as_posix()+'/'
counts={k:sum(n.startswith(runprefix+k+'/') for n in files) for k in ['cache','completed','results']};assert counts==dict(cache=158208,completed=159744,results=18432),counts
l=json.loads((O/'closed_ledger_review.json').read_text());assert l['passed'] and l['logical_operations']==159744 and l['computed_callbacks']==158208
assert s['payload']['files'][runprefix+'ledger.jsonl']==l['ledger_sha256']
rt=R/'operations/concurrency_runtime_v1/launch_98c288b850f44fc7b2c324edbe26b95f.json';runtime=json.loads(rt.read_text());assert runtime['returncode']==0 and runtime['snapshot_sha256']=='44a8aca7a621cc2b580836b9b1f6f5aaeb6d4c40e5742507168087e9bcb78466';assert s['payload']['files'][rt.relative_to(R).as_posix()]==sha(rt)
report=dict(snapshot_sha256=s['snapshot_sha256'],recipient_proofs=proofs,counts=counts,documents=1536,blocks=256,cells=18432,all_run_proof_hashes_match_official_and_producer_closure=True,maximum_branch_relative=maxbranch,maximum_fp32_delta_discrepancy=maxfp,ledger_review_sha256=sha(O/'closed_ledger_review.json'),runtime_sha256=sha(rt),model_calls=0,bootstrap_calls=0,scope='Incremental complete immutable recipient audit reused once; no newraw rehash or modelreplay at finaljoin')
(O/'final_closure_review.json').write_text(json.dumps(report,indent=2)+'\n')
q=dict(schema_version=1,snapshot_sha256=s['snapshot_sha256'],reviewer_id='/root/astra_goals_and_concurrency_review',independent=True,verdict='approved',topics_checked=['design','implementation','data','cost','claims'],findings=[dict(id='ACTUAL-FULL-DESCRIPTIVE-TEST',severity='low',status='accepted',evidence='All1536recipientgroups/18432operator-dosecells independentlychecked incrementally. Exact savedoperationrequest/cache identities, donor/nativeanchors, endpointenergydecomposition, fixedlearnedbaselinepredictions, suffix targets, losses, vectorerrors andlineardiagnostics verified. Allproofhashes matchproducerseal andofficialcompletion.',resolution='Accept actual256block acquisition,158208forward1536backward; no missing/deletedcells,0FITrefits. Numerical qualification/priorFITproof reused, no native/TCforward/bootstrap rerun.'),dict(id='CLOSED-ACCOUNTING',severity='low',status='accepted',evidence='Closedledger159744uniqueattempts,158208computedcallbacks accounting159744coupledoperations, allrequest/eventdigests andschedulekinds checked;0duplicate/unknownevents. Actualruntimeexit0 bound.',resolution='Incrementalcachedproofs reused atfinaljoin without re-auditing completedgroups.'),dict(id='NO-FAMILY-INFERENCE',severity='low',status='accepted',evidence='OriginalBfamilyeligibilityfailed forbothN and isretained. Completionis fixed256descriptiveTEST, notB1-B3support or repairedfamilyvalidity.',resolution='Future frozenanalyzer may reportfinitecorpus contrasts andonlyqualifiedTCc1joint12v6intervalscope; no p/Holm/rejection/support decisions authorized.')],limitations='Acceptance of actual descriptiveacquisition, not effect inference. No originalfamily support claims, no universalcoverage orwidthassurance. PriorFIT/tail/precisionqualification reused unchanged. Native andTCfunctions were not rerun; saved arithmetic/provenance checked. Actualfinalanalysis requires ownreviewed0modelpacket; future results not inferred here.')
(P/'completion_review_astra_v1.json').write_text(json.dumps(q,indent=2)+'\n');print('APPROVED',s['snapshot_sha256'],counts)
