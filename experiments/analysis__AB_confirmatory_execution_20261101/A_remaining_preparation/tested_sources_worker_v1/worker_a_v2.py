"""Narrow injected Runtime adapter around immutable worker_a implementation.

No files/globals persistently changed: original Runtime binding restored in
finally. Only approved cross-stage natural/native operations bypass new calls.
All newly measured operations use the unchanged Runtime/worker implementation.
"""
import argparse
import json
from pathlib import Path
from research_checks.gate import digest,verify_review
from research_checks.persistence import immutable,request_key
from .prepare import ROOT,sha
from .runtime import Runtime
from . import worker_a
from .schedule_a_v2 import schedule
from .admission_a_v2 import validate as validate_admission


def read(path):
    obj=json.loads(Path(path).read_text(encoding='utf-8'))
    if obj['payload_sha256']!=digest(obj['payload']):raise ValueError('corrupt A source receipt')
    return obj['payload']


def adapter_sources():
    return {name:sha(ROOT/name) for name in ['ab_confirmatory_20261101/worker_a_v2.py','ab_confirmatory_20261101/schedule_a_v2.py','ab_confirmatory_20261101/admission_a_v2.py','ab_confirmatory_20261101/campaign_authorization.py','ab_confirmatory_20261101/offline_io_v4.py','ab_confirmatory_20261101/offline_io_v3.py']}


def verify_source_stage(folder):
    folder=ROOT/folder;completion=read(folder/'stage_completed.json')
    for name,expected in completion['files'].items():
        if sha(folder/name)!=expected:raise ValueError('source A stage artifact changed: '+name)
    return completion,read(folder/'identity.json')


def preload_reuse(cfg,target_model):
    stages={};reused={}
    for label,path in cfg.get('reuse_stages',{}).items():
        completion,identity=verify_source_stage(path)
        if identity['model']!=target_model or completion['identity']!=identity:
            raise ValueError('import stage model/identity mismatch')
        stages[label]=(ROOT/path,completion,identity)
    for operation,label in cfg.get('reuse_operations',{}).items():
        if label not in stages:raise ValueError('unknown source stage')
        folder,completion,identity=stages[label]
        cp=folder/'completed'/f'{operation}.json';done=read(cp)
        if done['operation']!=operation:raise ValueError('import operation mismatch')
        rp=folder/'cache'/(done['request']+'.json');payload=read(rp);request=payload['request']
        if request_key(request)!=done['request'] or request['model_identity']!=target_model or request['code_identity']!=identity['code']:
            raise ValueError('source request/identity mismatch')
        for p in [cp,rp]:
            if completion['files'].get(p.relative_to(folder).as_posix())!=sha(p):
                raise ValueError('import absent from sealed source stage')
        reused[operation]=dict(request=request,result=payload['result'],source=dict(stage=str(folder),
             completion_sha256=sha(folder/'stage_completed.json'),operation_receipt=str(cp),operation_sha256=sha(cp),
             cache_receipt=str(rp),cache_sha256=sha(rp)))
    return reused


def runtime_class(reused):
    class ReusingRuntime(Runtime):
        def compute(self,operation,document,intervention,readout,function,extra_operations=()):
            if operation not in reused:
                return super().compute(operation,document,intervention,readout,function,extra_operations)
            if extra_operations or operation in self.ops:raise ValueError('import must not consume a new scheduled call')
            old=reused[operation];request=old['request']
            if (request['model_identity']!=self.identity['model'] or request['document']!=document
                    or request['intervention']!=intervention or request['readout']!=readout):
                raise ValueError('cross-stage operation semantics differ')
            immutable(self.folder/'reused'/f'{operation}.json',dict(operation=operation,source=old['source'],
                target_identity=self.identity,source_request=request_key(request),new_model_calls=0))
            return old['result']
    return ReusingRuntime


def validate_qualification(cfg,model):
    q=cfg['qualification'];snapshot=verify_review(ROOT,q['snapshot'],q['review'])
    oldcfg=json.loads((ROOT/q['config']).read_text(encoding='utf-8'))
    oldmodel=json.loads((ROOT/oldcfg['model_identity']).read_text(encoding='utf-8'))['A']
    if oldmodel!=model or oldcfg['study']!='A' or oldcfg['phase']!='FIT_ONLY':
        raise ValueError('qualification model/operator scope mismatch')
    controls_path=ROOT/oldcfg['output']/'controls.json';controls=read(controls_path)
    if len(controls)!=5 or not all(c['passed'] is True for c in controls):raise ValueError('r0 qualification incomplete')
    for p in [ROOT/q['config'],ROOT/oldcfg['model_identity'],controls_path]:
        if snapshot['payload']['files'].get(p.relative_to(ROOT).as_posix())!=sha(p):
            raise ValueError('qualification source not bound by approved snapshot')
    # Same branch/operator implementation bytes must be in the old review.
    for name in ['ab_confirmatory_20261101/native.py','ab_confirmatory_20261101/worker_a.py','ab_confirmatory_20261101/fitting.py']:
        if snapshot['payload']['files'].get(name)!=sha(ROOT/name):raise ValueError('qualified operator source changed')
    if cfg['control_documents']:raise ValueError('v2 reuses qualification; duplicate controls forbidden')


def main(config_path):
    cfg=json.loads((ROOT/config_path).read_text(encoding='utf-8'))
    if cfg['adapter_sources']!=adapter_sources():raise ValueError('A adapter source changed')
    model=json.loads((ROOT/cfg['model_identity']).read_text(encoding='utf-8'))['A']
    validate_qualification(cfg,model)
    docs=json.loads((ROOT/cfg['corpus']).read_text(encoding='utf-8'))['documents']
    validate_admission(cfg,model,docs)
    actual=json.loads((ROOT/cfg['schedule']).read_text(encoding='utf-8'))
    if actual!=schedule(cfg,docs):raise ValueError('A exact schedule mismatch')
    reused=preload_reuse(cfg,digest(model))
    original=worker_a.Runtime
    worker_a.Runtime=runtime_class(reused)
    try:return worker_a.main(config_path)
    finally:worker_a.Runtime=original


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);args=p.parse_args();main(args.config)
