"""Queue failure/allowlist tests with synthetic receipts only."""
import tempfile
from pathlib import Path
from unittest.mock import patch
from . import queue
from .common import HERE,put,sha

def run():
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp);cfg=dict(A_exit_receipt='exit.json',A_completed='run/completed.json',A_snapshot='a',A_processes=[1,2])
        with patch.object(queue,'ROOT',root):
            assert queue.state(cfg,lambda p:True)=='running'
            assert queue.state(cfg,lambda p:False)=='dead_without_receipt'
            (root/'exit.json').write_text('{"snapshot_sha256":"a","returncode":1}')
            try:queue.state(cfg,lambda p:False)
            except ValueError:pass
            else:raise AssertionError('A error swallowed')
            (root/'exit.json').write_text('{"snapshot_sha256":"WRONG","returncode":0}')
            try:queue.state(cfg,lambda p:False)
            except ValueError:pass
            else:raise AssertionError('Wrong predecessor accepted')
            (root/'exit.json').write_text('{"snapshot_sha256":"a","returncode":0}')
            (root/'run').mkdir();(root/'run/evidence.txt').write_text('valid');put(root/'run/completed.json',dict(complete=True,files={'evidence.txt':sha(root/'run/evidence.txt')}))
            assert queue.state(cfg,lambda p:True)=='awaiting_release'
            assert queue.state(cfg,lambda p:False)=='ready'
            (root/'run/evidence.txt').write_text('changed')
            try:queue.state(cfg,lambda p:False)
            except ValueError:pass
            else:raise AssertionError('Changed A seal accepted')
    put(HERE/'queue_fixtures.json',dict(passed=True,checks=['running/dead status','A nonzero fails','wrong snapshot fails','requires process/lock release','all A sealed files checked'],model_calls=0))
    print('Queue fixtures PASS')
if __name__=='__main__':run()
