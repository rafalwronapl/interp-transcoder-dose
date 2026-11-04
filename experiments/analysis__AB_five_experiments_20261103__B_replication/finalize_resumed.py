"""Offline extension: disclose exact operational restart and actual load count."""
from pathlib import Path
import json
from research_checks.gate import read,sha
H=Path(__file__).resolve().parent;R=H.parents[2]
def main():
    assert (H/'completion_snapshot.json').exists()
    resumes=list((H/'run/resume_loads').glob('*.json'))
    loads=int((H/'run/model_load_attempt.json').exists())+len(resumes)
    text=(H/'REPORT.md').read_text().replace('1 model-load attempt.',f'{loads} model-load attempts.')
    summary=read(H/'run/summary.json')['payload']
    cell=lambda frame,dose,method:next(r for r in summary if r['frame']==frame and r['dose']==dose and r['method']==method)
    tc=cell('main_mixture',1.,'TC');ridge=cell('main_mixture',1.,'RIDGE');small=cell('main_mixture',.05,'TC');tsmall=cell('main_mixture',.05,'TAYLOR');tlarge=cell('main_mixture',1.,'TAYLOR')
    text+='\nInterpretation: ranking crossover and useful predictive accuracy are distinct outcomes. '
    text+=f"At c=.05, TC/Taylor relative RMS are {100*small['relative_rms']:.3f}%/{100*tsmall['relative_rms']:.3f}%; at c=1, {100*tc['relative_rms']:.3f}%/{100*tlarge['relative_rms']:.3f}%. Ridge at c=1 is {100*ridge['relative_rms']:.3f}% and zero-change is100%. "
    if tc['relative_rms']>=1 or tc['rms_error']>=ridge['rms_error']:
        text+='The strong useful-accuracy regime of Gemma270M is NOT reproduced by this artifact: the TC result must not be described as a second demonstration of10%error or superiority to the simple baselines. '
    text+='All six doses and the transfer frame are retained; no artifact substitution or changed success criterion follows this outcome.\n'
    for frame in ['so','when','transfer','main_mixture']:
        text+=f'\nFull frozen dose curve: {frame}. Relative RMS in percent; absolute columns in logits.\n\n| Dose | TC% | Taylor% | Ridge% | Mean% | Frozen% | Zero% | TC absolute RMS | Native RMS |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|\n'
        for dose in [.05,.1,.25,.5,1.,2.]:
            values=[100*cell(frame,dose,m)['relative_rms'] for m in ['TC','TAYLOR','RIDGE','MEAN','FROZEN','ZERO']]
            text+='| '+str(dose)+' | '+' | '.join(f'{v:.4f}' for v in values)+f" | {cell(frame,dose,'TC')['rms_error']:.8g} | {cell(frame,dose,'TC')['native_rms']:.8g} |\n"
    text+='\nAll144 metric cells and nominal pointwise95% block intervals remain in run/summary.json. These are conditional finite-corpus descriptions; no calibrated familywise population rejection is claimed.\n'
    text+='\nOperational recovery: the initial worker exited after383durableTESTcontexts because a Windows reader briefly prevented replacing advisory STATUS.json. A separately reviewed narrow status-publication wrapper resumed the same scientific worker/cache identity; valid completed measurements were read from cache. The full80932logical operation schedule contains no duplicate attempts. Cache replay traversal cost time but did not repeat inference. Resume provenance: resume_snapshot.json/resume_review.json and status_resume.py.\n'
    text+='A second controlled handoff occurred only during cache-only replay at379/383contexts, with the exact child suspended and unchanged ledger verified before stop. It memoized the exact digest of the immutable74.8MB FIT object; all numerical code/cachekeys stayed unchanged and FIT immutability was rechecked before completion. It avoided1535redundant FIT serializations, not scientific measurements. See fit_digest_review_v3.json and fit_digest_handoff_done.json.\n'
    (H/'REPORT_v2.md').write_text(text)
    evidence=dict(actual_model_loads=loads,resume_receipts=len(resumes),scientific_attempts=80932,backward=0,source='Original load receipt plus explicit resume_loads; finaluniqueledger checked by completion packet')
    (H/'restart_accounting.json').write_text(json.dumps(evidence,indent=2)+'\n')
    files=[H/n for n in ['completion_snapshot.json','completion_manifest.json','REPORT_v2.md','restart_accounting.json','finalize_resumed.py','resume_snapshot.json','resume_review.json','resume_audit.json','status_resume.py','fit_digest_snapshot_v3.json','fit_digest_review_v3.json','fit_digest_handoff_done.json','fit_digest_resume.py','independent_completion_audit.json']]+resumes+[H/'run/model_load_attempt.json',R/'operations/research_launch_fc26fff9b0634e559f5df2d103c6736d.json']
    (H/'final_manifest.json').write_text(json.dumps(dict(files={p.relative_to(R).as_posix():sha(p) for p in files}),indent=2)+'\n')
    c=read(H/'completion_contract.json');c['id']+='_RESUMED';c['purpose']='Layered final report correcting actual model load count and disclosing reviewed telemetry recovery; no new scientific computations.'
    c['input_manifests']=[(H/'final_manifest.json').relative_to(R).as_posix()];c['tracked_files']+=[(H/n).relative_to(R).as_posix() for n in ['REPORT_v2.md','restart_accounting.json','finalize_resumed.py']]
    (H/'final_contract.json').write_text(json.dumps(c,indent=2)+'\n')
if __name__=='__main__':main()
