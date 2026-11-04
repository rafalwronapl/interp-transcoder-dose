"""A schedule with explicit cross-stage imported operations omitted from cost."""
from .schedule_a import schedule as original_schedule


def schedule(cfg,documents):
    ops=original_schedule(cfg,documents)['operations']
    reused=set(cfg.get('reuse_operations',{}))
    names={o['id'] for o in ops}
    if not reused<=names:raise ValueError('reuse operation is outside literal stage scope')
    if any(not (name.startswith('capture_') or name.endswith('_native')) for name in reused):
        raise ValueError('only natural captures/native suffix may be imported')
    return dict(operations=[o for o in ops if o['id'] not in reused])
