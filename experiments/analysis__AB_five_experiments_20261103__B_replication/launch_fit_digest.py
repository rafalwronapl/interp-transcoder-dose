"""Reviewed safe handoff during cache-only replay; never interrupt new measurement."""
from pathlib import Path
import ctypes,json,sys,time,subprocess
from research_checks.gate import read,sha,verify_review,create
from concurrency_a270_q06_20261102 import process_table
from concurrency_runtime_v2 import same_process
H=Path(__file__).parent;R=H.resolve().parents[2]
def main():
    prefix=H.resolve().relative_to(R).as_posix()
    verify_review(R,prefix+'/fit_digest_snapshot_v3.json',prefix+'/fit_digest_review_v3.json','pre_run')
    p=read(H/'fit_digest_handoff.json');table=process_table()
    assert all(same_process(v,table.get(v['ProcessId'])) for v in p['processes'])
    assert sha(R/'operations/research_worker.lock')==p['lock_sha256']
    assert sha(H/'run/ledger.jsonl')==p['ledger_sha256']
    status=read(H/'run/STATUS.json');assert status['stage']=='TEST_curve' and status['logical_attempts']==22129
    assert not (H/'fit_digest_handoff_done.json').exists()
    kernel=ctypes.windll.kernel32;kernel.OpenProcess.restype=ctypes.c_void_p
    kernel.TerminateProcess.argtypes=[ctypes.c_void_p,ctypes.c_uint];kernel.WaitForSingleObject.argtypes=[ctypes.c_void_p,ctypes.c_ulong];kernel.CloseHandle.argtypes=[ctypes.c_void_p]
    suspend=ctypes.windll.ntdll.NtSuspendProcess;resume=ctypes.windll.ntdll.NtResumeProcess
    suspend.argtypes=[ctypes.c_void_p];suspend.restype=ctypes.c_long
    resume.argtypes=[ctypes.c_void_p];resume.restype=ctypes.c_long
    pid=p['child'];handle=kernel.OpenProcess(0x00100801,False,pid)
    if not handle:raise OSError('Cannot open exact replay child')
    suspended=False;stopped=False
    try:
        assert same_process(next(x for x in p['processes'] if x['ProcessId']==pid),process_table().get(pid))
        if suspend(handle)!=0:raise OSError('Could not suspend exact child')
        suspended=True
        # No worker thread can reserve a new attempt between this durable-ledger
        # check and termination. Any changed ledger resumes the child and aborts.
        assert sha(H/'run/ledger.jsonl')==p['ledger_sha256']
        assert same_process(next(x for x in p['processes'] if x['ProcessId']==pid),process_table().get(pid))
        if not kernel.TerminateProcess(handle,3):raise OSError('Stop failed')
        if kernel.WaitForSingleObject(handle,10000)!=0:raise OSError('Child exit unconfirmed')
        stopped=True
    finally:
        if suspended and not stopped:
            if resume(handle)!=0:raise OSError('Could not resume child after failed handoff')
        kernel.CloseHandle(handle)
    for _ in range(100):
        if not (R/'operations/research_worker.lock').exists():break
        time.sleep(.1)
    assert not (R/'operations/research_worker.lock').exists()
    assert sha(H/'run/ledger.jsonl')==p['ledger_sha256']
    create(H/'fit_digest_handoff_done.json',dict(previous_status=status,previous_processes=p['processes'],ledger_unchanged=True,new_scientific_calls_interrupted=0,reason='Avoid repeated immutable74.8MB FIT serialization; same exact digest'))
    return subprocess.run([sys.executable,'-m','research_checks','launch','--snapshot',prefix+'/fit_digest_snapshot_v3.json','--review',prefix+'/fit_digest_review_v3.json'],cwd=R).returncode
if __name__=='__main__':sys.exit(main())
