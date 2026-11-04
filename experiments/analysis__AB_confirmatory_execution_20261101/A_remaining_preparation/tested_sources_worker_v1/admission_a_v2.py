"""Actual reviewed A stage prerequisites, checked before model import/load."""
import json
from research_checks.gate import verify_review,pointer,digest
from .prepare import ROOT,sha


def validate(cfg,model,documents=None):
    kind=cfg['stage_kind'];n=cfg.get('selected_n')
    if kind in ['PILOT','TEST']:
        from .campaign_authorization import validate_acquisition
        if not cfg.get('authorization_manifest'):raise ValueError('A acquisition authorization manifest required')
        return validate_acquisition(cfg,documents)
    required={'ADDITIONAL_FIT':{'coverage':('/payload/result/all_passed',True)},
      'STABILITY':{'test_completion':('/payload/identity/model',digest(model)),
                   'extra_fit_completion':('/payload/identity/model',digest(model))}}[kind]
    if set(cfg.get('admission',{}))!=set(required):raise ValueError('A stage prerequisites not supplied')
    for key,(where,expected) in required.items():
        entry=cfg['admission'][key];snap=verify_review(ROOT,entry['snapshot'],entry['review'])
        path=ROOT/entry['evidence'];relative=path.resolve().relative_to(ROOT).as_posix()
        if snap['payload']['files'].get(relative)!=sha(path):raise ValueError('prerequisite evidence outside approved snapshot')
        if pointer(json.loads(path.read_text(encoding='utf-8')),where)!=expected:
            raise ValueError('A prerequisite failed: '+key)
    if kind=='STABILITY':
        source=ROOT/cfg['reuse_stages']['primary_test']/'stage_completed.json'
        if source.resolve()!=(ROOT/cfg['admission']['test_completion']['evidence']).resolve():
            raise ValueError('reviewed TEST source differs from actual reused TEST')
        fitfolder=(ROOT/cfg['frozen_fits']['r1']).parent
        if (fitfolder/'stage_completed.json').resolve()!=(ROOT/cfg['admission']['extra_fit_completion']['evidence']).resolve():
            raise ValueError('reviewed extra FIT source differs from actual frozen fits')
    return True
