"""Seal completed C2 acquisition evidence without model/statistical execution."""
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', choices=['qwen', 'gemma'], required=True)
    parser.add_argument('--runtime-receipt', required=True)
    parser.add_argument('--review-evidence', action='append', default=[])
    args = parser.parse_args()
    stage = ROOT / 'analysis/C2_fresh_fit_holdout_20261102' / args.model
    expected = dict(qwen=(5020, 896, 4096), gemma=(8604, 1280, 7296))[args.model]
    forward, captures, heads = expected
    contract = read(stage / 'contract.json')
    if contract['budget'] != dict(forward=forward, backward=0):
        raise ValueError('Exact frozen C2 budget required')
    schedule = read(ROOT / contract['schedule'])['operations']
    if len(schedule) != forward or len({op['id'] for op in schedule}) != forward:
        raise ValueError('Exact unique C2 schedule required')
    runtime_path = (ROOT / args.runtime_receipt).resolve()
    if not runtime_path.is_relative_to(ROOT):
        raise ValueError('Runtime path escape')
    runtime = read(runtime_path)
    if runtime.get('returncode') != 0:
        raise ValueError('Actual canonical exit0 required')
    matches = [read(p) for p in stage.glob('pre_run_snapshot_v*.json')
               if read(p)['snapshot_sha256'] == runtime['snapshot_sha256']]
    if len(matches) != 1:
        raise ValueError('Exactly one matching actual pre-run version required')
    pre = matches[0]
    seal = read(stage / 'run/stage_completed.json')['payload']
    if seal != dict(forward=forward, backward=0, LLM_loads=1, head_calls=heads,
                    captures=captures, fresh_FITs=3, holdout_blocks=32):
        raise ValueError('Exact completed C2 seal required')
    result = read(stage / 'run/result.json')
    canonical = json.dumps(result['payload'], sort_keys=True, separators=(',', ':'),
                           ensure_ascii=False, allow_nan=False).encode()
    if hashlib.sha256(canonical).hexdigest() != result['payload_sha256']:
        raise ValueError('Result payload corruption')
    forecast_path = stage / 'run/forecast_frozen.json'
    if result['payload']['forecast_sha256'] != sha(forecast_path):
        raise ValueError('Actual result must bind frozen forecast')
    corpus_path = stage / 'corpus.json'
    documents = read(corpus_path)['documents']
    captured_ids = {p.stem.removeprefix('capture_')
                    for p in (stage / 'run/completed').glob('capture_*.json')}
    if len(documents) != captures or captured_ids != {d['id'] for d in documents}:
        raise ValueError('All and only assigned C2 natural documents must be captured')
    create(stage / 'exposure_consumed_v1.json', dict(
        model=args.model, documents=documents, corpus_sha256=sha(corpus_path),
        completed_stage_sha256=sha(stage / 'run/stage_completed.json'),
        pre_run_snapshot_sha256=runtime['snapshot_sha256'],
        scope='These exact assigned FIT/HOLDOUT documents are now exposed by C2; '
              'never describe their original reserved allocations as fresh confirmation. '
              'Original corpus bytes and failed stability/admission decisions remain unchanged.'))
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
    for name in args.review_evidence:
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError('Review evidence escape')
        files[path.relative_to(ROOT).as_posix()] = sha(path)
    files[Path(__file__).resolve().relative_to(ROOT).as_posix()] = sha(Path(__file__))
    summary = dict(model=args.model, forward=forward, backward=0, LLM_loads=1,
                   captures=captures, head_calls=heads, fresh_FITs=3, holdout_blocks=32,
                   runtime_returncode=0, pre_run_snapshot_sha256=runtime['snapshot_sha256'],
                   result_sha256=sha(stage / 'run/result.json'),
                   forecast_sha256=sha(forecast_path), new_calls_by_closure=0,
                   new_statistics_by_closure=0, independent_completion_review='pending')
    create(stage / 'completion_summary_v1.json', summary)
    path = stage / 'completion_summary_v1.json'
    files[path.relative_to(ROOT).as_posix()] = sha(path)
    create(stage / 'completion_outputs_manifest_v1.json', dict(files=files))
    contract['id'] += '_COMPLETION'
    contract['purpose'] = 'Completed fresh C2 acquisition closure; no new computation'
    contract['input_manifests'].append(
        (stage / 'completion_outputs_manifest_v1.json').relative_to(ROOT).as_posix())
    create(stage / 'completion_contract_v1.json', contract)
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
