import json,os,re
import numpy as np
from .common import *
FRAMES=dict(so='{n} was tired after the long trip, so',when='When {n} opened the old letter,',transfer='{n} put the travel bag beside the door because',object='{n} was waiting outside, and the receptionist greeted')
def write(name,obj):(HERE/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
def main():
    poolpath=ROOT/'analysis/AB_confirmatory_execution_20261101/corpus/qualified_pools_v1.json';pool=read(poolpath)
    paths=[]
    for base,dirs,files in os.walk(ROOT):
        dirs[:]=[d for d in dirs if d not in {'.git','models','node_modules','__pycache__','cache','results','completed','aliases','targets','.venv','venv'} and not d.startswith(('run','fixture','synthetic','tmp')) and Path(base,d)!=HERE]
        for fn in files:
            if fn.endswith('.json') and ('corpus' in fn.lower() or fn.lower() in {'source_index.json','documents.json'}):
                if 'pool' not in fn.lower():paths.append(Path(base)/fn)
    assert paths
    observed=set();inventory={}
    for p in paths:
        raw=p.read_text(encoding='utf-8');observed.update(w.lower() for w in re.findall(r'[A-Za-z]+',raw));inventory[p.relative_to(ROOT).as_posix()]=sha(p)
    # Include the historical lexical exposure registry even when not a corpus.
    exp=ROOT/'analysis/AB_confirmatory_execution_20261101/corpus/observed_words_v2.json';observed.update(w.lower() for w in read(exp));inventory[exp.relative_to(ROOT).as_posix()]=sha(exp)
    rng=np.random.default_rng(20261103)
    pools={g:[pool[g][i] for i in rng.permutation(len(pool[g])) if pool[g][i].lower() not in observed] for g in ['male','female']}
    assert min(map(len,pools.values()))>=32
    from transformers import AutoTokenizer
    identpath=ROOT/'analysis/AB_confirmatory_execution_20261101/B_fit_primary_v1/model_identity.json';ident=read(identpath)
    tok=AutoTokenizer.from_pretrained(ident['B']['folder'],local_files_only=True)
    pairs={}
    for name,a,b in [('subject',' she',' he'),('object',' her',' him')]:
        aa=tok.encode(a,add_special_tokens=False);bb=tok.encode(b,add_special_tokens=False);assert len(aa)==len(bb)==1;pairs[name]=[aa[0],bb[0]]
    assert pairs['subject']==[1304,668]
    docs=[]
    for i in range(32):
        names=[pools['male'][i],pools['female'][i]]
        for frame,tpl in FRAMES.items():
            for side in [0,1]:
                block=f'B_FRESH_20261103_{i:04d}';did=f'{block}_{frame}_s{side}';text=tpl.format(n=names[side]);ids=tok.encode(text,add_special_tokens=True)
                ans=pairs['object' if frame=='object' else 'subject']
                for word,aid in zip([' her',' him'] if frame=='object' else [' she',' he'],ans):assert tok.encode(text+word,add_special_tokens=True)==ids+[aid],'Context-boundary token mismatch'
                docs.append(dict(id=did,block=block,donor=f'{block}_{frame}_s{1-side}',frame=frame,side=side,text=text,names=names,ids=ids,answer_ids=ans))
    write('corpus.json',dict(documents=docs,frames=FRAMES,readouts=pairs,seed=20261103,population='NLTK exclusive male/female category names; not certified real-world gender',freshness_inventory=inventory,selected_absent_from_inventory=True))
    old=read(ROOT/'analysis/AB_five_experiments_20261103/B_mechanism/source_index.json');controls=[old['controls'][k] for k in sorted(old['controls'])[:2]]
    write('controls.json',controls)
    cfg=dict(rho=101.51097375004979,eps=101.51097375004979/4,groups_source='analysis/AB_fast_followups_20261103/B_switch/FROZEN_GROUPS_v2.json',model_identity=identpath.relative_to(ROOT).as_posix(),threads=1,max_forward=3088)
    write('config.json',cfg)
    ops=[dict(id='control_'+str(i),kind='forward') for i in range(8)]+[dict(id='fresh_parity_'+f+'_s'+str(s),kind='forward') for f in FRAMES for s in [0,1]]
    for d in docs:
        ops.extend(dict(id=d['id']+'_'+a,kind='forward') for a in ['capture','tcbase','tcend','nativebranch','NATIVE','FULL']+ARMS)
    write('schedule.json',dict(operations=ops));assert len(ops)==3088
    names=[poolpath,identpath,ROOT/cfg['groups_source'],exp]+paths
    for e in controls:
        for v in e.values():names.extend([ROOT/v['cache'],ROOT/v['receipt']])
    for part in ['B','TC']:
        for name,v in ident[part]['files'].items():
            assert sha(name)==v['sha256'];names.append(Path(name))
    names += [ROOT/p for p in ['analysis/B_norm_control_20261103/common.py','analysis/B_norm_control_20261103/worker.py']]
    names += list((ROOT/'ab_confirmatory_20261101').glob('*.py'))+list((ROOT/'research_checks').glob('*.py'))
    for p in [ROOT/'analysis/__init__.py',HERE/'__init__.py',ROOT/'analysis/B_norm_control_20261103/__init__.py']:
        if p.exists():names.append(p)
    names += [p for p in HERE.glob('*') if p.is_file() and p.suffix in {'.py','.txt','.json'} and p.name not in {'input_manifest.json','contract.json','snapshot.json'}]
    write('input_manifest.json',dict(files={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(names))}))
    prefix=HERE.relative_to(ROOT).as_posix();ev=prefix+'/fixtures.json'
    contract=dict(schema_version=1,id='B_FRESH_TRANSFER_20261103',kind='experiment',primary_agent='/root/next_b_fresh',purpose='Fresh fixed-norm direction confirmation and grammatical object-pronoun readout transfer',tracked_files=[prefix+'/'+n for n in ['worker.py','prepare.py','common.py','PLAN.txt','corpus.json','config.json','controls.json','fixtures.py','fixtures.json','input_manifest.json']],tracked_trees=[],input_manifests=[prefix+'/input_manifest.json'],gates=[dict(id=k,category=k,evidence=ev,pointer='/'+k,op='eq',expected=True,reason='Actual worker synthetic end-to-end '+k+' controls; literal corpus contextual tokenizer assertions run by preparation') for k in ['hooks','data','pilot','accounting','restart']],circuits=[],structural_scope='L15 postfeedforward output replacement reaches both later decoder blocks and readout; exact dynamic suffix adapter plus signed sensitivity controls.',entrypoint=dict(module='analysis.B_fresh_transfer_20261103.worker',args=[]),schedule=prefix+'/schedule.json',budget=dict(forward=3088,backward=0))
    write('contract.json',contract);print(dict(fresh_pairs=32,documents=len(docs),readouts=pairs,inventory_files=len(inventory),budget=3088))
if __name__=='__main__':main()
