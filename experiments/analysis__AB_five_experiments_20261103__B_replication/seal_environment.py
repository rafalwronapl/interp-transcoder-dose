"""Pre-run software/source binding amendment; never touches scientific outcomes."""
from pathlib import Path
from importlib.metadata import version,distribution
import json
from ab_confirmatory_20261101.prepare import ROOT,sha
HERE=Path(__file__).resolve().parent;REL=HERE.relative_to(ROOT).as_posix()
def main():
 dist=distribution('transformers');base=Path(dist.locate_file('transformers'))
 files=[base/p for p in ['models/gemma3/modeling_gemma3.py','models/gemma3/configuration_gemma3.py','modeling_utils.py','cache_utils.py','masking_utils.py','modeling_rope_utils.py']]
 if not all(p.exists() for p in files):raise ValueError('Missing semantic sources')
 software=dict(versions={p:version(p) for p in ['torch','transformers','numpy','safetensors','tokenizers']},files={str(p):sha(p) for p in files})
 (HERE/'software_identity.json').write_text(json.dumps(software,indent=2)+'\n')
 contract=json.loads((HERE/'contract.json').read_text())
 for p in ['ab_confirmatory_20261101/test_native_tail_b.py','ab_confirmatory_20261101/test_transcoder.py',REL+'/software_identity.json',REL+'/seal_environment.py']:
  if p not in contract['tracked_files']:contract['tracked_files'].append(p)
 (HERE/'contract.json').write_text(json.dumps(contract,indent=2)+'\n')
 code=json.loads((HERE/'code_manifest.json').read_text())
 code['files']={p:sha(ROOT/p) for p in code['files']}
 for p in ['ab_confirmatory_20261101/test_native_tail_b.py','ab_confirmatory_20261101/test_transcoder.py',REL+'/software_identity.json']:
  code['files'][p]=sha(ROOT/p)
 (HERE/'code_manifest.json').write_text(json.dumps(code,indent=2)+'\n')
 print(json.dumps(software['versions']))
if __name__=='__main__':main()
