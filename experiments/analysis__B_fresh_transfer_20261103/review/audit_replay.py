import json
from pathlib import Path
import transformers
from research_checks.gate import sha
from analysis.B_fresh_transfer_20261103 import worker
O=worker.HERE/'run'
before={p.relative_to(O).as_posix():sha(p) for p in O.rglob('*') if p.is_file()}
def forbidden(*a,**kw):raise AssertionError('Completed replay attempted pretrained load')
old=transformers.AutoModelForCausalLM.from_pretrained;transformers.AutoModelForCausalLM.from_pretrained=forbidden
try:worker.main()
finally:transformers.AutoModelForCausalLM.from_pretrained=old
after={p.relative_to(O).as_posix():sha(p) for p in O.rglob('*') if p.is_file()};assert before==after
v=dict(passed=True,files_unchanged=len(before),new_calls=0,new_model_loads=0,scope='Independent actual worker.main with blocked native loader; byte hashes before/after allrunfiles')
(worker.HERE/'review/independent_replay_audit.json').write_text(json.dumps(v,indent=2)+'\n');print(v)
