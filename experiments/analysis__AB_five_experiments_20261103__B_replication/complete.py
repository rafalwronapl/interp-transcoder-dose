"""Offline completion packet; reads finished results, never reruns measurements."""
from pathlib import Path
import json
from ab_confirmatory_20261101.prepare import ROOT,sha
from research_checks.gate import digest
HERE=Path(__file__).resolve().parent;REL=HERE.relative_to(ROOT).as_posix()
def unwrap(p):
 x=json.loads(p.read_text());assert x['payload_sha256']==digest(x['payload']);return x['payload']
def put(n,x):(HERE/n).write_text(json.dumps(x,indent=2)+'\n')
def main():
 out=HERE/'run';completion=unwrap(out/'completed.json')
 for name,h in completion['files'].items():
  if sha(out/name)!=h:raise ValueError('Completed evidence changed '+name)
 rows=unwrap(out/'rows.json');summary=unwrap(out/'summary.json')
 ops=json.loads((HERE/'operations.json').read_text())['operations'];expected={o['id'] for o in ops}
 ledger=[]
 for line in (out/'ledger.jsonl').read_text().splitlines():
  x=json.loads(line);assert x['sha256']==digest(x['record']);ledger.append(x['record'])
 attempted=[op for r in ledger if r['event']=='attempt' for op in r['coupled_operations']]
 assert len(attempted)==len(set(attempted))==80932 and set(attempted)==expected
 assert len(rows)==9216 and len(summary)==144 and len({(r['document'],r['dose']) for r in rows})==9216
 assert len({r['block'] for r in rows})==256
 primary=[r for r in summary if r['frame']=='main_mixture' and r['dose'] in [.05,1.]]
 def cell(c,m):return next(r for r in primary if r['dose']==c and r['method']==m)
 crossing=cell(.05,'TC')['rms_error']>cell(.05,'TAYLOR')['rms_error'] and cell(1.,'TC')['rms_error']<cell(1.,'TAYLOR')['rms_error']
 ridge=cell(1.,'TC')['rms_error']<cell(1.,'RIDGE')['rms_error']
 report=['# Second public-artifact B experiment','',
  'Gemma-3-1B, L22, public medium16k JumpReLU TC without affine skip. 256 fresh name-pair TEST blocks, three shared templates;32 FIT blocks. Full donor operator only. Prior exploratory artifact exposure disclosed.','',
  'Descriptive finite-corpus comparison; nominal pointwise block intervals conditional on this FIT. No calibrated family/population rejection claim.','',
  '| Dose | Method | Relative RMS | Absolute RMS | Native RMS |','|---|---|---:|---:|---:|']
 for r in primary:report.append(f"| {r['dose']} | {r['method']} | {r['relative_rms']} | {r['rms_error']} | {r['native_rms']} |")
 report += ['',f'Main so/when mixture crossover (Taylor better at .05, TC better at1): {crossing}.',f'TC beats ridge at1: {ridge}.','',
  'All144 cells are preserved in run/summary.json;9216 document-dose rows in run/rows.json. This extension does not isolate model scale, layer, or architecture. Three templates reuse the same256lexicalblocks. A negative outcome is retained and does not trigger artifact substitution.','',
  'Accounting:80932heterogeneous forward operations,0backward,1 model-load attempt. Completed cache preserved. Independent completion review remains pending in completion_review.json.']
 (HERE/'REPORT.md').write_text('\n'.join(report)+'\n')
 put('completion_checks.json',dict(ledger_valid=True,unique_attempts=80932,all_scheduled_attempted=True,rows=9216,cells=144,test_blocks=256,crossover=crossing,beats_ridge_at1=ridge,model_calls_in_completion=0))
 files=[p for p in out.rglob('*') if p.is_file()]+[HERE/n for n in ['pre_run_snapshot_v2.json','pre_run_review_v3.json','worker.py','config.json','corpus.json','tokens.json','operations.json','input_manifest.json','code_manifest.json','software_identity.json','PROTOCOL.txt','completion_checks.json','REPORT.md','complete.py']]
 put('completion_manifest.json',dict(files={p.relative_to(ROOT).as_posix():sha(p) for p in files}))
 contract=dict(schema_version=1,id='B_SECOND_ARTIFACT_G1B_L22_COMPLETION_20261103_v1',kind='maintenance',primary_agent='/root/b_second_artifact_five',purpose='Offline completion accounting and finite-corpus summary of accepted fixed second-artifact acquisition; no model or bootstrap replay.',tracked_files=[REL+'/complete.py',REL+'/completion_checks.json',REL+'/REPORT.md'],tracked_trees=[],input_manifests=[REL+'/completion_manifest.json'],gates=[dict(id='all_operations',category='accounting',evidence=REL+'/completion_checks.json',pointer='/all_scheduled_attempted',op='eq',expected=True,reason='Complete unique durable schedule; all finalizedoutputs hashverified.')],circuits=[],structural_scope='No new intervention; completed exactnative suffix measurements summarized unchanged.',entrypoint=None,schedule=None,budget=None)
 put('completion_contract.json',contract)
 print(json.dumps(dict(crossover=crossing,beats_ridge_at1=ridge,rows=len(rows),cells=len(summary))))
if __name__=='__main__':main()
