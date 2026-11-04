"""Bounded serial execution after A; never bypasses canonical review/lock."""
from pathlib import Path
import json,time,subprocess,sys
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
A=BASE.parent/'A_L21'
def status(**values):
    p=BASE/'queue_status.tmp';p.write_text(json.dumps(dict(utc=time.time(),**values)),encoding='utf-8');p.replace(BASE/'queue_status.json')
def command(args,label):
    with (BASE/(label+'.log')).open('w',encoding='utf-8') as stdout,(BASE/(label+'.err')).open('w',encoding='utf-8') as stderr:
        return subprocess.run([sys.executable,*args],cwd=ROOT,stdout=stdout,stderr=stderr).returncode
start=time.monotonic();status(stage='waiting_A_main',model_calls=0)
while time.monotonic()-start<24*3600:
    failure=A/'main_launch_exit.json'
    if failure.exists() and json.loads(failure.read_text()).get('returncode',0)!=0:
        status(stage='blocked_A_failed',details=json.loads(failure.read_text()));sys.exit(2)
    if (A/'main_run/completed.json').exists() and not (ROOT/'operations/research_worker.lock').exists():break
    time.sleep(30)
else:status(stage='bounded_wait_expired',model_calls=0);sys.exit(2)
prefix=BASE.relative_to(ROOT).as_posix()
status(stage='canonical_launch')
code=command(['-m','research_checks','launch','--snapshot',prefix+'/pre_run_snapshot_v2.json','--review',prefix+'/pre_run_review_v2.json'],'launch')
(BASE/'launch_exit.json').write_text(json.dumps(dict(returncode=code)))
if code:status(stage='launch_failed',returncode=code);sys.exit(code)
code=command(['-m','analysis.AB_five_experiments_20261103.B_mechanism.complete'],'completion_prepare')
if not code:code=command(['-m','research_checks','snapshot',prefix+'/completion_contract.json','--phase','completion','--out',prefix+'/completion_snapshot.json'],'completion_snapshot')
status(stage='awaiting_independent_completion_review' if not code else 'completion_prepare_failed',returncode=code)
sys.exit(code)
