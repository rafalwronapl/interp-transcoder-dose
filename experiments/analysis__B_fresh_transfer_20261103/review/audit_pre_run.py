import json,re
from pathlib import Path
from collections import Counter
from transformers import AutoTokenizer
from research_checks.gate import read,sha
R=Path(__file__).resolve().parents[3];B=R/'analysis/B_fresh_transfer_20261103'
c=read(B/'corpus.json');ds=c['documents'];assert len(ds)==256
assert Counter(d['frame'] for d in ds)==dict(so=64,when=64,transfer=64,object=64)
assert len({d['block'] for d in ds})==32
names={n.lower() for d in ds for n in d['names']};assert len(names)==64
for p,h in c['freshness_inventory'].items():
 assert sha(R/p)==h
 assert not names.intersection(w.lower() for w in re.findall('[A-Za-z]+',(R/p).read_text(encoding='utf-8'))),p
ident=read(R/read(B/'config.json')['model_identity']);tok=AutoTokenizer.from_pretrained(ident['B']['folder'],local_files_only=True)
index={d['id']:d for d in ds}
for d in ds:
 assert index[d['donor']]['donor']==d['id']
 assert index[d['donor']]['block']==d['block'] and index[d['donor']]['frame']==d['frame']
 assert tok.encode(d['text'],add_special_tokens=True)==d['ids']
 for word,i in zip([' her',' him'] if d['frame']=='object' else [' she',' he'],d['answer_ids']):
  assert tok.encode(d['text']+word,add_special_tokens=True)==d['ids']+[i]
ops=read(B/'schedule.json')['operations'];assert len(ops)==len({o['id'] for o in ops})==3088
mf=read(B/'input_manifest.json')['files']
assert all(p in mf for p in ['analysis/B_norm_control_20261103/common.py','analysis/B_norm_control_20261103/worker.py','ab_confirmatory_20261101/native.py','ab_confirmatory_20261101/native_tail_b.py','research_checks/__init__.py'])
out=dict(passed=True,contexts=256,blocks=32,unique_names=64,freshness_files=len(c['freshness_inventory']),contextual_token_checks=512,scheduled_forward=3088,backward=0,scope='No pretrained model calls; actual worker fixture separately executed; source/algebra/manual dependency review')
(B/'review/independent_pre_run_audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(out)
