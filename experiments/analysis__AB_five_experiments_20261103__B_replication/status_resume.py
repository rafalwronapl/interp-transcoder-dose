"""Reviewed operational resume; frozen scientific worker and cache identity retained."""
from pathlib import Path
import json,time,uuid
from . import worker as w
BASE=Path(__file__).parent;ROOT=w.ROOT
ORIGINAL_REPLACE=Path.replace
def status_replace(path,target):
    if path.resolve()!=BASE/'run/STATUS.tmp' or Path(target).resolve()!=BASE/'run/STATUS.json':
        return ORIGINAL_REPLACE(path,target)
    for delay in [0,.01,.03,.1,.2]:
        if delay:time.sleep(delay)
        try:return ORIGINAL_REPLACE(path,target)
        except PermissionError:pass
    # Telemetry is advisory. Durable cache/ledger publication remains fail-closed.
    return Path(target)
def main():
    from importlib.metadata import version
    packet=json.loads((BASE/'resume_inputs.json').read_text())
    for p,h in packet['files'].items():
        if w.sha(ROOT/p)!=h:raise ValueError('Resume input changed '+p)
    software=json.loads((BASE/'software_identity.json').read_text())
    for package,v in software['versions'].items():
        if version(package)!=v:raise ValueError('Software changed')
    for p,h in software['files'].items():
        if w.sha(p)!=h:raise ValueError('Software source changed')
    cfg=json.loads((BASE/'config.json').read_text());docs=json.loads((BASE/'corpus.json').read_text())['documents'];tokens=json.loads((BASE/'tokens.json').read_text())
    ops=w.operations(docs,cfg['controls']);assert ops==json.loads((BASE/'operations.json').read_text())
    manifest=json.loads((BASE/'input_manifest.json').read_text());files=json.loads((BASE/'code_manifest.json').read_text())['files']
    for p,h in {**manifest['files'],**files}.items():
        if w.sha(ROOT/p)!=h:raise ValueError('Frozen scientific input changed '+p)
    identity=dict(model=w.digest(manifest),code=w.digest(dict(files=files,config=cfg)),corpus=w.sha(BASE/'corpus.json'),tokens=w.sha(BASE/'tokens.json'))
    out=BASE/'run';runtime=w.BundleRuntime(out,identity,ops)
    if (out/'completed.json').exists():
        for p,h in w.unwrap(out/'completed.json')['files'].items():
            if w.sha(out/p)!=h:raise ValueError('Completed output changed')
        return
    assert (out/'MODEL_STARTED').exists()
    w.immutable(out/'resume_loads'/(uuid.uuid4().hex+'.json'),dict(identity=identity,reason='Windows advisory status publication failure; frozen cache retained'))
    engine=w.Engine(cfg)
    Path.replace=status_replace
    try:result=w.measure(cfg,engine,runtime,docs,tokens,out)
    finally:Path.replace=ORIGINAL_REPLACE
    assert len(runtime.attempts)==len(runtime.ops)
    w.immutable(out/'completed.json',dict(result=result,files={p.relative_to(out).as_posix():w.sha(p) for p in out.rglob('*') if p.is_file() and p.name not in ['STATUS.json','completed.json','STATUS.tmp']}))
    try:(out/'STATUS.json').write_text(json.dumps(dict(stage='completed',**result)))
    except PermissionError:pass
if __name__=='__main__':main()
