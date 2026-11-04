"""Reversible NTFS attribute maintenance; never rewrite scientific contents."""
import argparse, ctypes, hashlib, json, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
STAGE=ROOT/'analysis/AB_confirmatory_execution_20261101/A_stability_calibration_v1'
BASE=STAGE/'run'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x):
    with p.open('x',encoding='utf-8') as f: json.dump(x,f,indent=2)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def allocated(p):
    high=ctypes.c_ulong(0)
    fn=ctypes.windll.kernel32.GetCompressedFileSizeW
    fn.argtypes=[ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_ulong)]
    fn.restype=ctypes.c_ulong
    low=fn(str(p),ctypes.byref(high))
    if low==0xffffffff and ctypes.get_last_error():raise OSError('allocated size failed')
    return (high.value<<32)+low
def main():
    a=argparse.ArgumentParser();a.add_argument('--apply',action='store_true');args=a.parse_args()
    if args.apply:
        plan=read(OUT/'compression_plan_v1.json')
        for cell in plan['cases']:
            receipt=OUT/('compressed_case_'+cell['case']+'_v1.json')
            if receipt.exists():continue
            directory=(BASE/cell['case']).resolve()
            if not directory.is_relative_to(BASE.resolve()):raise ValueError('scope escape')
            actual=sorted(directory.glob('*_data.json'))
            if [p.name for p in actual]!=list(cell['files']):raise ValueError('frozen file set changed')
            result=subprocess.run(['compact.exe','/C','/I','/Q','*_data.json'],cwd=directory,capture_output=True,text=True)
            after=0
            for p in actual:
                expected=cell['files'][p.name];s=p.stat()
                if sha(p)!=expected['sha256'] or s.st_size!=expected['logical_bytes'] or s.st_mtime_ns!=expected['mtime_ns']:
                    raise ValueError('content or timestamp changed: '+str(p))
                after+=allocated(p)
            write(receipt,dict(case=cell['case'],returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,
                files_verified=len(actual),api_reported_storage_before=cell['allocated_bytes'],api_reported_storage_after=after,
                content_size_mtime_preserved=True,free_C_bytes=shutil.disk_usage(ROOT).free,
                undo_command=['compact.exe','/U','/I','/Q','*_data.json'],undo_cwd=str(directory),
                storage_measure='GetCompressedFileSizeW; uncompressed value is logical size, not cluster-rounded allocation'))
            if result.returncode:raise ValueError('compact nonzero; no file deleted or rewritten')
            if shutil.disk_usage(ROOT).free>=int(2.5*1024**3):break
        return
    approved=read(STAGE/'completion_snapshot_v1.json')['payload']['files']
    cases=[]
    for i in reversed(range(18)):
        directory=BASE/f'{i:02d}';files={};total=0;logical=0
        for p in sorted(directory.glob('*_data.json')):
            s=p.stat();h=approved[p.relative_to(ROOT).as_posix()]
            files[p.name]=dict(sha256=h,logical_bytes=s.st_size,mtime_ns=s.st_mtime_ns)
            total+=allocated(p);logical+=s.st_size
        if len(files)!=2000:raise ValueError('unexpected closed case size')
        cases.append(dict(case=f'{i:02d}',files=files,logical_bytes=logical,allocated_bytes=total))
    plan=dict(scope='Only closed A_stability run00..17 *_data.json; no active/Qwen/B files',cases=cases,
              files=36000,logical_bytes=sum(x['logical_bytes'] for x in cases),
              allocated_bytes=sum(x['allocated_bytes'] for x in cases),free_C_bytes=shutil.disk_usage(ROOT).free,
              method='NTFS compact attribute only; exact approved SHA/size/mtime verified after each case',
              stop_free_C_bytes=int(2.5*1024**3),new_model_or_MC_calls=0)
    write(OUT/'compression_plan_v1.json',plan)
    print(json.dumps({k:v for k,v in plan.items() if k!='cases'}))
if __name__=='__main__':main()
