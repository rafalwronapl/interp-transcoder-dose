"""Offline frozen inputs for second-artifact B; no pretrained inference."""
from pathlib import Path
import json,hashlib
import numpy as np
from ab_confirmatory_20261101.prepare import ROOT,sha
from analysis.AB_five_experiments_20261103.B_replication.worker import operations
HERE=Path(__file__).resolve().parent
REL=HERE.relative_to(ROOT).as_posix()
def put(n,x):
 p=HERE/n
 if p.exists():raise ValueError('Refusing overwrite '+n)
 p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main():
 source=ROOT/'analysis/AB_confirmatory_execution_20261101/corpus'
 pool=json.loads((source/'qualified_pools_v1.json').read_text());old=json.loads((source/'corpus_v1.json').read_text())
 seen={w.casefold() for b in old['blocks'] for w in b['words']}
 seen.update(json.loads((source/'observed_words_v2.json').read_text()))
 rng=np.random.default_rng(20261103)
 selected={}
 for k in ['male','female']:
  words=sorted(w for w in pool[k] if w.casefold() not in seen)
  selected[k]=[words[i] for i in rng.permutation(len(words))[:288]]
  assert len(selected[k])==288
 docs=[];blocks=[]
 frames=dict(so='{n} was tired after the long trip, so',when='When {n} opened the old letter,',transfer='{n} put the travel bag beside the door because')
 for j in range(288):
  split='FIT' if j<32 else 'TEST';block=f'B2_{split}_{j:04d}';words=[selected['male'][j],selected['female'][j]]
  blocks.append(dict(id=block,split=split,words=words))
  for frame,tpl in frames.items():
   if split=='FIT' and frame=='transfer':continue
   for side in [0,1]:
    docs.append(dict(id=f'{block}_{frame}_{side}',donor=f'{block}_{frame}_{1-side}',block=block,split=split,frame=frame,side=side,text=tpl.format(n=words[side])))
 from transformers import AutoTokenizer
 model=ROOT/'models/gemma-3-1b-pt';tc=ROOT/'models/gemma_scope/gemma-3-1b-pt/transcoder/layer_22_width_16k_l0_medium'
 tok=AutoTokenizer.from_pretrained(str(model),local_files_only=True)
 answers=[tok.encode(w,add_special_tokens=False) for w in [' she',' he']]
 if any(len(a)!=1 for a in answers):raise ValueError('Readout not single token')
 tokens={d['id']:tok.encode(d['text'],add_special_tokens=True) for d in docs}
 assert len(set(d['text'] for d in docs))==len(docs)
 controls=[d['id'] for d in docs if d['block']==blocks[0]['id']]
 cfg=dict(model=model.relative_to(ROOT).as_posix(),tc=tc.relative_to(ROOT).as_posix(),layer=22,threads=2,
  answer_ids=[a[0] for a in answers],controls=controls,doses=[.05,.1,.25,.5,1.,2.],operator='full',
  fit_blocks=32,test_blocks=256,gates=dict(margin_absolute=2e-4,branch_relative=1e-4),
  selection='Deepest available local Gemma3-1B no-affine medium16k public transcoder; availability/cost rule, prior historical exposure disclosed. No new outcome screening.')
 put('config.json',cfg);put('tokens.json',tokens);put('corpus.json',dict(blocks=blocks,documents=docs,
  freshness='Disjoint names against frozen Nov1 qualified historical inventory and all Nov1 FIT/PILOT/TEST blocks; later A/C noun cohorts do not use these name prompts. No pretraining freshness claim.',seed=20261103))
 ops=operations(docs,controls);put('operations.json',ops)
 inputs=[p for folder in [model,tc] for p in sorted(folder.iterdir()) if p.is_file()]
 inputs += [source/n for n in ['qualified_pools_v1.json','corpus_v1.json','observed_words_v2.json','historical_input_manifest.json']]
 put('input_manifest.json',dict(files={p.relative_to(ROOT).as_posix():sha(p) for p in inputs}))
 dependencies=['ab_confirmatory_20261101/__init__.py','ab_confirmatory_20261101/prepare.py','ab_confirmatory_20261101/native.py','ab_confirmatory_20261101/native_tail_b.py','ab_confirmatory_20261101/transcoder.py','ab_confirmatory_20261101/runtime.py','ab_confirmatory_20261101/baselines_b.py','ab_confirmatory_20261101/test_native_tail_b.py','ab_confirmatory_20261101/test_transcoder.py','analysis/Qwen06_ABC_extension_20261102/bundle_runtime.py','research_checks/gate.py','research_checks/persistence.py',REL+'/worker.py']
 put('code_manifest.json',dict(files={p:sha(ROOT/p) for p in dependencies}))
 put('cost.json',dict(total_forward=len(ops['operations']),backward=0,model_loads=1,fit_documents=128,test_documents=1536,
  controls=4,full_natural_captures=1664,technical_full_calls=12,physical_persistent_bundles=1664+128+1536+4,
  note='Full captures and local/JVP/TC/suffix calls are heterogeneous; one jointTEST curve bundle perdoc; ZERO is algebra no model call. Readout suffix layers23-25 dynamic attention.',
  statistical_scope='Finite corpus comparisons with1999 nominal pointwise block bootstrap, no family rejection/calibration or successgate.'))
 gates=[dict(id=k,category=k,evidence=REL+'/test_evidence.json',pointer='/'+k,op='eq',expected=True,reason=v) for k,v in dict(hooks='Actual synthetic native exact-tail and TC tests; pretrained numerical controls scheduled before TEST.',data='Fresh nameblock pairing and FIT/TEST separation with exact tokens.',pilot='Bounded technical qualification on4FITcontexts beforeTEST; no outcome-based artifact choice.',accounting='Exact frozen forward schedule; bundle durable attempts, all expected operations consumed.',restart='Replay produces no calls; missing receipt recovered fromcache; corruption rejected; uncertain attempts fail closed.').items()]
 tracked=dependencies+[REL+'/'+n for n in ['prepare.py','tests.py','PROTOCOL.txt','config.json','tokens.json','corpus.json','operations.json','cost.json','code_manifest.json','test_evidence.json','tests.log']]
 contract=dict(schema_version=1,id='B_SECOND_ARTIFACT_G1B_L22_20261103_v1',kind='experiment',primary_agent='/root',purpose='Frozen second publicartifact full dosecurve on256freshblocks with FIT-only baselines; no positive-result requirement.',tracked_files=tracked,tracked_trees=[],input_manifests=[REL+'/input_manifest.json'],gates=gates,circuits=[],structural_scope='L22 postfeedforward branch output at finalposition then complete dynamic native layers23-25 and finalnorm/head; scheduled nonzero input/output/tail qualification on4FITcontexts beforeTEST.',entrypoint=dict(module='analysis.AB_five_experiments_20261103.B_replication.worker',args=[]),schedule=REL+'/operations.json',budget=dict(forward=len(ops['operations']),backward=0))
 put('contract.json',contract);print(json.dumps(dict(documents=len(docs),blocks=len(blocks),operations=len(ops['operations']),answers=cfg['answer_ids'])))
if __name__=='__main__':main()
