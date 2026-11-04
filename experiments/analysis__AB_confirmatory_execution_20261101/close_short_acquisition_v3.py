"""Metadata-only closure of an already finished short PILOT/TEST stage."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def create(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--packet', required=True)
    parser.add_argument('--runtime-receipt', required=True)
    args = parser.parse_args()
    stage = ROOT / args.packet
    runtime_path = ROOT / args.runtime_receipt
    runtime = read(runtime_path)
    if runtime.get('returncode') != 0:
        raise ValueError('Actual runtime exit0 is required')
    sealed = read(stage / 'run/stage_completed.json')
    payload = sealed.get('payload', sealed)
    cfg = read(stage / 'config.json')
    pre_run = read(stage / 'pre_run_snapshot_v1.json')
    if runtime.get('snapshot_sha256') != pre_run['snapshot_sha256']:
        raise ValueError('Runtime belongs to another stage')
    phase = cfg['phase']
    if phase not in ('PILOT', 'TEST'):
        raise ValueError('Acquisition phases only')
    schedule = read(ROOT / cfg['schedule'])
    operations = schedule['operations']
    expected = 1024 if phase == 'PILOT' else 8192
    if len(operations) != expected:
        raise ValueError('Unexpected fixed short schedule')
    files = dict(pre_run['payload']['files'])
    files[Path(__file__).resolve().relative_to(ROOT).as_posix()] = digest(Path(__file__))
    launch = read(stage / 'launch_receipt_v1.json')
    command = launch['args']
    for option in ('--policy', '--policy-snapshot', '--policy-review'):
        path = ROOT / command[command.index(option) + 1]
        files[path.relative_to(ROOT).as_posix()] = digest(path)
        if option == '--policy-snapshot':
            files.update(read(path)['payload']['files'])
    if launch.get('resource_assessment'):
        path = ROOT / launch['resource_assessment']
        files[path.relative_to(ROOT).as_posix()] = digest(path)
    for relative, value in payload['files'].items():
        files[(stage / 'run' / relative).relative_to(ROOT).as_posix()] = value
    for path in list(stage.iterdir()) + [stage / 'run/stage_completed.json', runtime_path]:
        if path.is_file() and not path.name.startswith('completion_'):
            files[path.relative_to(ROOT).as_posix()] = digest(path)
    events = stage / 'status_events'
    if events.exists():
        for path in events.glob('*.json'):
            files[path.relative_to(ROOT).as_posix()] = digest(path)
    summary = dict(phase=phase, forward=expected, backward=0,
                   blocks=32 if phase == 'PILOT' else 256,
                   documents=256 if phase == 'PILOT' else 2048,
                   runtime_returncode=0, independent_review='pending',
                   scope='Acquisition only; no fitting, bootstrap, selection or hypothesis conclusion')
    create(stage / 'completion_summary_v1.json', summary)
    files[(stage / 'completion_summary_v1.json').relative_to(ROOT).as_posix()] = digest(stage / 'completion_summary_v1.json')
    create(stage / 'completion_outputs_manifest_v1.json', dict(files=files))
    contract = read(stage / 'contract.json')
    contract['id'] = contract['id'] + '_ACTUAL_COMPLETION'
    contract['purpose'] = summary['scope']
    contract['input_manifests'].append((stage / 'completion_outputs_manifest_v1.json').relative_to(ROOT).as_posix())
    create(stage / 'completion_contract_v1.json', contract)
    print(json.dumps(summary))

if __name__ == '__main__':
    main()
