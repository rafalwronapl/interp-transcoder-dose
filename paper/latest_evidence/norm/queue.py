"""One bounded, exact-allowlist A-to-B queue. No model imports."""
import ctypes,json,os,subprocess,sys,time
from ctypes import wintypes
from pathlib import Path
from .common import HERE,ROOT,read,sha,unwrap,put,digest

def alive(pid,expected_creation=None):
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];k.OpenProcess.restype=wintypes.HANDLE
    k.GetExitCodeProcess.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD)];k.GetExitCodeProcess.restype=wintypes.BOOL
    k.GetProcessTimes.argtypes=[wintypes.HANDLE]+[ctypes.POINTER(wintypes.FILETIME)]*4;k.GetProcessTimes.restype=wintypes.BOOL
    k.CloseHandle.argtypes=[wintypes.HANDLE]
    handle=k.OpenProcess(0x1000,False,int(pid))
    if not handle:
        if ctypes.get_last_error()==5:return True
        return False
    try:
        creation,exit_time,kernel,user=[wintypes.FILETIME() for _ in range(4)]
        assert k.GetProcessTimes(handle,ctypes.byref(creation),ctypes.byref(exit_time),ctypes.byref(kernel),ctypes.byref(user))
        born=(creation.dwHighDateTime<<32)|creation.dwLowDateTime
        if expected_creation is not None and born!=expected_creation:raise ValueError('A PID reused by another process')
        code=wintypes.DWORD();assert k.GetExitCodeProcess(handle,ctypes.byref(code));return code.value==259
    finally:k.CloseHandle(handle)

def state(cfg,is_alive=alive):
    receipt=ROOT/cfg['A_exit_receipt'];active=any(is_alive(p) for p in cfg['A_processes'])
    if not receipt.exists():return 'running' if active else 'dead_without_receipt'
    r=read(receipt)
    if r['snapshot_sha256']!=cfg['A_snapshot']:raise ValueError('Unexpected A snapshot receipt')
    if r['returncode']!=0:raise ValueError('A canonical launch failed: '+str(r['returncode']))
    seal_path=ROOT/cfg['A_completed'];seal=unwrap(seal_path)
    if seal['complete'] is not True:raise ValueError('A completion absent/false')
    if active or (ROOT/'operations/research_worker.lock').exists():return 'awaiting_release'
    for name,h in seal['files'].items():
        p=(seal_path.parent/name).resolve();p.relative_to(seal_path.parent.resolve())
        if sha(p)!=h:raise ValueError('Changed A completion file '+name)
    return 'ready'

def validate_B(cfg):
    for field,h in [('B_snapshot','B_snapshot_file_sha256'),('B_review','B_review_file_sha256')]:
        assert sha(ROOT/cfg[field])==cfg[h],'Changed B queue authorization'
    s=read(ROOT/cfg['B_snapshot']);r=read(ROOT/cfg['B_review'])
    assert digest(s['payload'])==s['snapshot_sha256']==r['snapshot_sha256']==cfg['B_snapshot_sha256']
    assert r['verdict']=='approved' and r['independent'] is True

def main():
    cfg=read(HERE/'queue_config.json');assert sha(HERE/'queue.py')==cfg['queue_code_sha256'];validate_B(cfg)
    lock=HERE/'queue.lock';fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    os.write(fd,str(os.getpid()).encode());os.close(fd)
    try:
        put(HERE/'queue_started.json',dict(pid=os.getpid(),config_sha256=sha(HERE/'queue_config.json'),maximum_wait_seconds=cfg['maximum_wait_seconds']))
        start=time.monotonic();dead_since=None
        while True:
            status=state(cfg,lambda pid:alive(pid,cfg['A_process_filetimes'][str(pid)]))
            (HERE/'queue_status.json').write_text(json.dumps(dict(status=status,elapsed_seconds=time.monotonic()-start))+'\n',encoding='utf-8')
            if status=='ready':break
            if time.monotonic()-start>cfg['maximum_wait_seconds']:raise TimeoutError('A-to-B queue deadline reached')
            if status=='dead_without_receipt':
                if dead_since is None:dead_since=time.monotonic()
                elif time.monotonic()-dead_since>30:raise RuntimeError('A processes ended without canonical receipt')
            else:dead_since=None
            time.sleep(cfg['poll_seconds'])
        validate_B(cfg)
        with (HERE/'stage2_launch.log').open('wb') as stdout,(HERE/'stage2_launch.err').open('wb') as stderr:
            result=subprocess.run([sys.executable,'-m','research_checks','launch','--snapshot',cfg['B_snapshot'],'--review',cfg['B_review']],cwd=ROOT,stdout=stdout,stderr=stderr,check=False)
        put(HERE/'queue_finished.json',dict(B_returncode=result.returncode,A_exit_receipt_sha256=sha(ROOT/cfg['A_exit_receipt']),B_snapshot_sha256=cfg['B_snapshot_sha256']))
        if result.returncode:raise RuntimeError('B canonical launch failed: '+str(result.returncode))
    except Exception as error:
        put(HERE/'queue_failed.json',dict(error=type(error).__name__,message=str(error)));raise
    finally:lock.unlink(missing_ok=True)
if __name__=='__main__':main()
