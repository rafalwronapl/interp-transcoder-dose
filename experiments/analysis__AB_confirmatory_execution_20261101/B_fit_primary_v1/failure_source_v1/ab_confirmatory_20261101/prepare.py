"""Offline input inventory. Does not import torch or load pretrained weights."""
from pathlib import Path
import hashlib
import json
import os
import re
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/AB_confirmatory_execution_20261101'


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda: f.read(8 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def write(name, obj):
    p = OUT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False)+'\n', encoding='utf-8')


def inventory():
    found = []
    # Enumerate corpus-labelled files throughout the entire repository, including
    # historical cache directories. No history is changed and no results are read.
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules'}
                   and Path(base, d) != OUT]
        for fn in files:
            p = Path(base, fn)
            if p.suffix.lower() in {'.json', '.jsonl', '.csv', '.txt', '.py'} and any(k in fn.lower() for k in ('corpus', 'dataset', 'exposure')):
                found.append(p)
    seen = set()
    manifests = {}
    for p in sorted(found):
        raw = p.read_bytes()
        manifests[p.relative_to(ROOT).as_posix()] = hashlib.sha256(raw).hexdigest()
        seen.update(re.findall('[a-z]+', raw.decode('utf-8-sig', 'replace').casefold()))
    write('corpus/historical_input_manifest.json', {'files': manifests})
    write('corpus/observed_words.json', sorted(seen))
    write('corpus/exposure_manifest.json', {
        'status': 'INVENTORY_ONLY', 'files': len(manifests),
        'selection': 'All repository files whose names contain corpus/dataset/exposure and extension json/jsonl/csv/txt/py; excludes only git/pycache/node_modules and new output.',
        'limitation': 'Filename-labelled local corpus inventory. Completeness requires reviewer inspection of unlabelled historical data sources. No pretraining freshness claim.',
        'created_utc': datetime.now(timezone.utc).isoformat(), 'observed_words': len(seen)})
    models = {}
    for key, folder in [('A', ROOT/'models/gemma-3-1b-pt'), ('B', ROOT/'models/gemma-3-270m'),
                        ('TC', Path('C:/Users/rafal/tcdl/gs2_270m/transcoder/layer_15_width_16k_l0_medium'))]:
        files = {str(p.resolve()): {'sha256': sha(p), 'bytes': p.stat().st_size}
                 for p in sorted(folder.rglob('*')) if p.is_file()}
        models[key] = {'folder': str(folder), 'files': files, 'dtype': 'float32', 'backend': 'CPU eager', 'loaded': False}
    write('model_identity.json', models)
    local = ['mainexp/adapter.py', 'mainexp/__init__.py', 'mainexp/corpus.py',
             'analysis/TC_EXTENDED_20261030/run.py', 'analysis/TC_EXTENDED_20261030/prepare.py',
             'analysis/MAIN_CONFIRM_20261031/build_corpus_mc.py', 'analysis/MAIN_CONFIRM_20261031/run_confirm_mc.py']
    write('historical_adapter_manifest.json', {'files': {f: sha(ROOT/f) for f in local}})
    print(json.dumps({'historical_files': len(manifests), 'words': len(seen),
                      'model_files': {k: len(v['files']) for k,v in models.items()}}))


if __name__ == '__main__':
    inventory()
