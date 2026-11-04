"""Prepare completion review only after sealed native run and queue success."""
import json,subprocess,sys
from .common import HERE,ROOT,read,sha,unwrap
from .report import main as report

def main():
    queue=unwrap(HERE/'queue_finished.json');assert queue['B_returncode']==0,'B launch did not complete successfully'
    cfg=read(HERE/'config.json');out=ROOT/cfg['output'];seal=unwrap(out/'stage_completed.json')
    for name,h in seal['files'].items():assert sha(out/name)==h,'Completed output changed'
    report()
    names=[p for p in out.rglob('*') if p.is_file()]
    files={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(names)}
    (HERE/'completion_output_manifest.json').write_text(json.dumps(dict(files=files),indent=2)+'\n',encoding='utf-8')
    prefix=HERE.relative_to(ROOT).as_posix();contract=read(HERE/'stage2_contract.json')
    contract.update(id='B_NORM_NATIVE_COMPLETION_20261103',kind='maintenance',purpose='Completion review: actual native-readout results, numericalnormmatching, exactbudget,posthocconditionalclaims; preserve previousBstrength-matchingnegativefinding.',entrypoint=None,schedule=None,budget=None)
    contract['input_manifests']=[prefix+'/stage2_input_manifest.json',prefix+'/completion_output_manifest.json']
    contract['tracked_files'] += [prefix+'/'+x for x in ['report.py','finish.py','REPORT.txt','FINAL_ANALYSIS.json','stage1_snapshot.json','stage1_launch.log','stage1_launch.err','review/stage1_pre_run_review.json','stage2_snapshot_v2.json','review/stage2_pre_run_review_v2.json','queue_snapshot_v2.json','review/queue_review_v2.json','QUEUE_LAUNCH.json','queue_started.json','queue_finished.json','queue_verify.log','queue.log','queue.err','stage2_launch.log','stage2_launch.err']]
    (HERE/'completion_contract.json').write_text(json.dumps(contract,indent=2)+'\n',encoding='utf-8')
    with (HERE/'completion_snapshot.log').open('wb') as log:
        result=subprocess.run([sys.executable,'-m','research_checks','snapshot',prefix+'/completion_contract.json','--phase','completion','--out',prefix+'/completion_snapshot.json'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    assert result.returncode==0,'Completion snapshot failed'
    print(read(HERE/'completion_snapshot.json')['snapshot_sha256'])
if __name__=='__main__':main()
