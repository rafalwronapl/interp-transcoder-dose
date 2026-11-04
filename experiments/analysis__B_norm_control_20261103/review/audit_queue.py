"""Independent queue checks; canonical launch is never invoked here."""
import json,tempfile,hashlib
from pathlib import Path
from unittest.mock import patch
from analysis.B_norm_control_20261103 import queue as q,queue_fixtures as f
from research_checks.gate import digest
here=Path(__file__).resolve().parent;actual=q.HERE
f.HERE=here;f.run()
cfg=q.read(actual/'queue_config.json');q.validate_B(cfg)
for pid in cfg['A_processes']:
    assert q.alive(pid,cfg['A_process_filetimes'][str(pid)])
    try:q.alive(pid,cfg['A_process_filetimes'][str(pid)]+1)
    except ValueError:pass
    else:raise AssertionError('PID reuse accepted')
with tempfile.TemporaryDirectory(dir=here) as td:
    root=Path(td);(root/'operations').mkdir();(root/'run').mkdir()
    c=dict(A_exit_receipt='exit.json',A_completed='run/completed.json',A_snapshot='a',A_processes=[1,2])
    (root/'exit.json').write_text('{"snapshot_sha256":"a","returncode":0}')
    q.put(root/'run/completed.json',dict(complete=True,files={}))
    (root/'operations/research_worker.lock').write_text('held')
    with patch.object(q,'ROOT',root):
        assert q.state(c,lambda _:False)=='awaiting_release'
    # Execute the real bounded wait control flow with a mocked clock and forbidden launcher.
    for status,maxwait,error in [('running',10,TimeoutError),('dead_without_receipt',10000,RuntimeError)]:
        sandbox=root/status;sandbox.mkdir();clock=[-31.]
        def now():clock[0]+=31;return clock[0]
        fake=dict(cfg,maximum_wait_seconds=maxwait)
        original_read=q.read;original_sha=q.sha
        with patch.object(q,'HERE',sandbox),patch.object(q,'read',side_effect=lambda p:fake if Path(p).name=='queue_config.json' else original_read(p)),patch.object(q,'sha',side_effect=lambda p:cfg['queue_code_sha256'] if Path(p).name=='queue.py' else ('config' if Path(p).name=='queue_config.json' else original_sha(p))),patch.object(q,'validate_B'),patch.object(q,'state',return_value=status),patch.object(q.time,'monotonic',side_effect=now),patch.object(q.time,'sleep'),patch.object(q.subprocess,'run',side_effect=AssertionError('Unexpected B launch')):
            try:q.main()
            except error:pass
            else:raise AssertionError('Queue did not fail closed')
        assert not (sandbox/'queue.lock').exists()
s=q.read(actual/'queue_snapshot_v2.json');assert digest(s['payload'])==s['snapshot_sha256']
for p,h in s['payload']['files'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
r=dict(passed=True,snapshot_sha256=s['snapshot_sha256'],snapshot_files=len(s['payload']['files']),author_failure_tests_reproduced=True,exact_B_allowlist=True,live_A_creation_times_checked=True,PID_reuse_rejected=True,global_lock_blocks_launch=True,deadline_and_dead_without_receipt_fail_closed=True,canonical_B_invocations=0,model_calls=0)
(here/'queue_independent_audit.json').write_text(json.dumps(r,indent=2)+'\n')
print(r)
