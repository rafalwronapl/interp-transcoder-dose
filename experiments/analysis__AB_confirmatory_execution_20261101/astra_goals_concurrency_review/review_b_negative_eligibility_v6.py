import json,hashlib
from pathlib import Path
import numpy as np
from scipy.stats import beta
from research_checks.gate import digest,verify_review
R=Path.cwd();B=R/'analysis/AB_confirmatory_execution_20261101';P=B/'eligibility_synthesis_v6/B_actual_negative_v1';O=Path(__file__).parent/'b_negative_eligibility_v6';O.mkdir(exist_ok=True)
s=json.loads((P/'snapshot_v1.json').read_text());assert digest(s['payload'])==s['snapshot_sha256']=='529ae145f195afa74f2193f91f11f29bac2faff2182ce493502ff55f905e8bdb'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 p=Path(p);q=json.loads(p.read_text());assert digest(q['payload'])==q['payload_sha256'];assert s['payload']['files'][p.relative_to(R).as_posix()]==sha(p);return q['payload']
cases=read(B/'family_calibration_v2/cases.json');summary={};failed=[]
for n,expected_pass in [(128,46),(256,52)]:
 e=read(P/f'B{n}_eligibility.json');assert e['eligible'] is False and e['requirements']==dict(family_null=False,missing_degenerate=True,pointwise_coverage=True,precision_coverage=True)
 g=read(P/f'B{n}_family_null.json');rows=[read(x) for x in g['case_receipts']];assert len(rows)==g['case_count']==54
 assert sorted(digest(q['case']) for q in rows)==sorted(digest(q) for q in cases if q['study']=='B' and q['n']==n)
 for q in rows:
  k=q['false_rejections'];m=q['repetitions'];a=.05/len(cases);lo=0 if k==0 else float(beta.ppf(a/2,k,m-k+1));hi=1 if k==m else float(beta.ppf(1-a/2,k+1,m-k));np.testing.assert_allclose(q['simultaneous_mc_bounds'],[lo,hi],rtol=1e-12,atol=1e-14)
  assert q['fwer']==k/m and q['passed']==(hi<=.06) and m==2000 and q['draws']==1999
  if not q['passed']:failed.append(dict(case=q['case'],false_rejections=k,bounds=[lo,hi]))
 assert sum(q['passed'] for q in rows)==expected_pass
 assert g['failed_cases']==[q['case']['id']+':'+q['case']['distribution'] for q in rows if not q['passed']]
 coverage=read(P/f'B{n}_pointwise_coverage.json');assert coverage['passed'] and len(coverage['case_receipts'])==8
 for q in map(read,coverage['case_receipts']):assert q['coverage_gate'] and q['n']==n
 missing=read(P/f'B{n}_missing_degenerate.json');assert missing['passed'];test=read(missing['evidence']);assert test['errors']==test['failures']==test['exit_code']==0
 precision=read(P/f'B{n}_precision_coverage.json');assert precision['passed'] and len(precision['case_receipts'])==4
 for path in precision['case_receipts']:
  path=Path(path);i=int(path.parent.name);old=json.loads((Path(__file__).parent/f'v6_closed_cases/case_{i:02d}.json').read_text());assert old['case_sha256']==sha(path)
  q=read(path)['result'];assert q['case']['n']==n and q['passed'] and q['coverage_successes']==old['coverage_successes'] and q['coverage_lower']==old['coverage_lower']
  for name,h in q['artifacts'].items():assert s['payload']['files'][(path.parent/name).relative_to(R).as_posix()]==h
 summary[str(n)]=dict(family_pass=expected_pass,family_total=54,precision_pass=4,pointwise_pass=8,missing_degenerate=True,eligible=False)
report=dict(snapshot_sha256=s['snapshot_sha256'],summary=summary,failed_family_cases=failed,precision_reused='All8 prior independent4000artifact case audits exactcaseSHA matched;32000artifacthashes match newmanifest without rawre-audit',family_scope='Actual108case receipts/spec/counts/CP/gate arithmetic checked, no dataset/bootstrap regeneration',model_calls=0,simulations=0)
(O/'evidence_review.json').write_text(json.dumps(report,indent=2)+'\n')
review=dict(schema_version=1,snapshot_sha256=s['snapshot_sha256'],reviewer_id='/root/astra_goals_and_concurrency_review',independent=True,verdict='approved',topics_checked=['design','implementation','data','cost','claims'],findings=[dict(id='ACTUAL-NEGATIVE-ELIGIBILITY',severity='low',status='accepted',evidence='All108actual Bfamilycase receipts match fixedcase definition. Counts/CP simultaneousbounds and frozenupper<=.06 rule independently recomputed:12846/54PASS,25652/54PASS. Bothfamily gatesfalse; allrequiredgatesAND leaves bothNineligible.',resolution='Accept completed negative qualification, not repaired or waived familyvalidity. Precision8/8PASS cannot turn B1-B3familyeligible.'),dict(id='REUSE-QUALIFIED-PRECISION',severity='low',status='accepted',evidence='All8exactv6caseSHA match prior independent4000artifact-per-caseaudits;32000artifacthashes match newmanifest. Pointwise8casesperN and existing14correctness-test proof reused. No rawprecisionre-audit/model/MC.',resolution='Original v6finite-scenario joint12coverage scope retained, no universal coverage or widthassurance claim.')],limitations='Maintenance acceptance of actual completed eligibility synthesis including negative results. Familyreview checks savedcase counts/spec/CP/source provenance; it does not regenerate simulations. Precision priorfullraw audits reused exacthash. Doesnot authorize confirmatory BTEST/familyinference; current descriptiveTEST amendment remainsseparate. No new scientific data or criteria edits.')
(P/'review_astra_v1.json').write_text(json.dumps(review,indent=2)+'\n');print('SCOPED REVIEW APPROVED',s['snapshot_sha256'],flush=True)
verified=verify_review(R,(P/'snapshot_v1.json').relative_to(R).as_posix(),(P/'review_astra_v1.json').relative_to(R).as_posix(),'completion');assert verified['snapshot_sha256']==s['snapshot_sha256']
(P/'canonical_verify_astra_v1.json').write_text(json.dumps(dict(passed=True,snapshot_sha256=s['snapshot_sha256'],phase='completion',review_sha256=sha(P/'review_astra_v1.json'),new_model_calls=0,new_simulations=0),indent=2)+'\n');print('CANONICAL PASS',flush=True)
