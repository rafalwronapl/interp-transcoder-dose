"""Metadata-only closure of the two frozen C3 capture-only stages."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def create(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--model', choices=['llama', 'gemma270'], required=True)
    p.add_argument('--runtime-receipt', required=True)
    args = p.parse_args()
    stage = ROOT / 'analysis/C3_noD_more_models_20261102' / (args.model + '_capture')
    contract = read(stage / 'contract.json')
    pre = read(stage / 'pre_run_snapshot_v1.json')
    runtime_path = (ROOT / args.runtime_receipt).resolve()
    if not runtime_path.is_relative_to(ROOT):
        raise ValueError('Runtime escape')
    runtime = read(runtime_path)
    if runtime.get('returncode') != 0 or runtime['snapshot_sha256'] != pre['snapshot_sha256']:
        raise ValueError('Matching actual exit0 required')
    if contract['budget'] != dict(forward=924, backward=0):
        raise ValueError('Exact C3 capture-only budget required')
    schedule = read(ROOT / contract['schedule'])['operations']
    scheduled = {o['id'] for o in schedule}
    completed = {p.stem for p in (stage / 'run/completed').glob('*.json')}
    if len(schedule) != 924 or len(scheduled) != 924 or completed != scheduled:
        raise ValueError('All and only924 scheduled completions required')
    seal = read(stage / 'run/stage_completed.json')['payload']
    if any(seal.get(k) != v for k, v in dict(forward=924, backward=0,
                                            LLM_loads=1, captures=896).items()):
        raise ValueError('Exact closed capture seal required')
    controls = read(stage / 'run/controls.json')['payload']
    if len(controls) != 4 or not all(c['passed'] for c in controls):
        raise ValueError('Four qualified controls required')
    documents = read(stage / 'corpus.json')['documents']
    if len(documents) != 896 or {d['id'] for d in documents} != {
            i.removeprefix('capture_') for i in scheduled if i.startswith('capture_')}:
        raise ValueError('Exact consumed document allocation required')
    create(stage / 'exposure_consumed_v1.json', dict(
        model=args.model, documents=documents,
        corpus_sha256=sha(stage / 'corpus.json'),
        completed_stage_sha256=sha(stage / 'run/stage_completed.json'),
        pre_run_snapshot_sha256=pre['snapshot_sha256'],
        scope='C3 target-specific responses now consumed; texts were used on othermodels. '
              'Do not call these allocations fresh confirmation later; original history unchanged.'))
    files = dict(pre['payload']['files'])
    for path in stage.rglob('*'):
        if path.is_file() and not path.name.startswith('completion_'):
            files[path.relative_to(ROOT).as_posix()] = sha(path)
    files[runtime_path.relative_to(ROOT).as_posix()] = sha(runtime_path)
    command = read(stage / 'launch_receipt_v1.json')['args']
    for option in ['--policy', '--policy-snapshot', '--policy-review']:
        path = ROOT / command[command.index(option) + 1]
        files[path.relative_to(ROOT).as_posix()] = sha(path)
        if option == '--policy-snapshot':
            files.update(read(path)['payload']['files'])
    files[Path(__file__).resolve().relative_to(ROOT).as_posix()] = sha(Path(__file__))
    summary = dict(model=args.model, forward=924, backward=0, LLM_loads=1,
                   full_transformer=920, control_suffix=4, natural_captures=896,
                   runtime_returncode=0, new_calls_by_closure=0,
                   noD_forecasts_produced=0, oracle_forecasts_produced=0,
                   finite_holdout_head_outcomes=0, independent_completion_review='pending')
    create(stage / 'completion_summary_v1.json', summary)
    path = stage / 'completion_summary_v1.json'
    files[path.relative_to(ROOT).as_posix()] = sha(path)
    create(stage / 'completion_outputs_manifest_v1.json', dict(files=files))
    contract['id'] += '_COMPLETION'
    contract['purpose'] = 'C3 capture-only completion; no fitting/forecast/head execution'
    contract['input_manifests'].append(
        (stage / 'completion_outputs_manifest_v1.json').relative_to(ROOT).as_posix())
    create(stage / 'completion_contract_v1.json', contract)
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
