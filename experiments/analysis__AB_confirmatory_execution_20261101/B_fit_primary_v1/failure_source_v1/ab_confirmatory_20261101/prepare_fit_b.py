"""Root-authored B FIT packet materializer. No model calls or test reruns."""
import json,os,shutil
from pathlib import Path
from .prepare import ROOT,OUT,sha
from .worker_b import schedule,DEPENDENCIES

def main():
    stage=OUT/'B_fit_primary_v1';stage.mkdir(exist_ok=True)
    def put(name,value):
        p=stage/name
        if p.exists():raise ValueError('version rather than overwrite '+str(p))
        p.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    source=json.loads((OUT/'corpus/corpus_v1.json').read_text(encoding='utf-8'))
    all_tokens=json.loads((OUT/'corpus/tokens_v1.json').read_text(encoding='utf-8'))
    docs=[d for d in source['documents'] if d['study']=='B' and d['split']=='FIT' and d['frame'] in ('so','when')]
    if len(docs)!=128:raise ValueError('wrong FIT corpus')
    ids={d['id'] for d in docs};tokens={i:all_tokens[i] for i in ids}
    if len({d['block'] for d in docs})!=32 or any(d['donor'] not in ids for d in docs):raise ValueError('bad FIT pairing')
    identities=json.loads((OUT/'model_identity.json').read_text(encoding='utf-8'))
    identities={k:identities[k] for k in ('B','TC')}
    # Workspace-only snapshot schema: hardlink existing exact TC bytes, no
    # download or duplicate disk allocation, never write weights in place.
    original=identities['TC'];local=ROOT/'models/ab_gs2_270m_l15';local.mkdir(exist_ok=True)
    newfiles={}
    for path,meta in original['files'].items():
        target=local/Path(path).name
        if not target.exists():os.link(path,target)
        if sha(target)!=meta['sha256']:raise ValueError('TC source/link changed')
        newfiles[str(target)]=meta
    identities['TC']=dict(original,folder=str(local),files=newfiles,original_folder=original['folder'],storage='hardlinked read-only-by-policy')
    put('model_identity.json',identities)
    put('model_manifest.json',dict(files={Path(p).relative_to(ROOT).as_posix():v['sha256'] for item in identities.values() for p,v in item['files'].items()}))
    put('corpus.json',dict(documents=docs,source_sha256=sha(OUT/'corpus/corpus_v1.json'),scope='B FIT so/when only'))
    put('tokens.json',tokens)
    first=sorted({d['block'] for d in docs})[0];controls=[d['id'] for d in docs if d['block']==first]
    rel=stage.relative_to(ROOT).as_posix()
    cfg=dict(study='B',phase='FIT_ONLY',corpus=rel+'/corpus.json',tokens=rel+'/tokens.json',model_identity=rel+'/model_identity.json',
        output=rel+'/run',threads=2,expected_documents=128,layer=15,answer_ids=tokens[docs[0]['id']]['answer_ids'],control_documents=controls,
        schedule=rel+'/operations.json',gates=dict(fd_base=1e-5,fd_relative=.02,branch_relative=1e-4,sham_abs=1e-5,margin_parity=1e-4))
    if len(controls)!=4:raise ValueError('bad qualification cohort')
    put('config.json',cfg);ops=schedule(cfg,docs);put('operations.json',ops)
    counts={k:sum(o['kind']==k for o in ops['operations']) for k in ('forward','backward')}
    if counts!=dict(forward=1860,backward=4):raise ValueError('unexpected operations '+str(counts))
    put('cost_estimate.json',dict(logical_budget=counts,natural_full_forwards=128,qualification_full_forwards=24,
        full_transformer_forwards=152,backwards=4,local_native_endpoints=1536,local_native_bases=124,
        finite_difference_endpoints=32,local_jvp=8,TC_evaluations=4,independent_reference_evaluations=4,
        model_loads=1,automatic_retry_reserve=0,elapsed_estimate='Unmeasured; report actual time. Mostly local branch work after128captures.',
        estimated_RAM_GiB='3–5, verify beforelaunch',estimated_disk_MiB='100–400; parameters separately hardlinked,no weight copy in delivery'))
    # Copy root protocols once into the stage, before snapshot. Later prose
    # changes outside this packet cannot change the frozen execution contract.
    documents=['ROOT_STAGE_HANDOFF.md','PROTOCOL_B.md','PROTOCOL_B_CONTROLS.md','B_QUALIFICATION_DESIGN_ROOT.md','B_REFERENCE_RETRIEVAL.md']
    for name in documents:
        target=stage/name
        if target.exists():raise ValueError('existing protocol '+name)
        shutil.copyfile(OUT/name,target)
    put('input_manifest.json',dict(files={p.relative_to(ROOT).as_posix():sha(p) for p in [OUT/'lexical_review/review_v3.json',OUT/'corpus/corpus_v1.json',OUT/'corpus/tokens_v1.json']}))
    # Actual test receipt is separately written after successful tests. This
    # materializer never manufactures a PASS and preflight fails until present.
    gates=[]
    for category,pointer,expected,reason in [
        ('hooks','/two_stage_qualification_tested',True,'Full gate1 then naturalcapture then finalFITw thenprojectedgate2; end-to-end random test.'),
        ('data','/literal_documents',128,'Reviewed corpus subset,paired main-template FIT, noPILOT/TEST.'),
        ('pilot','/scientific_inference',False,'Separately reviewed fixedFIT-only scope; no Nselection or hypothesis test.'),
        ('accounting','/scheduled_forward',1860,'152full+1692localnative+8JVP+8TC/reference;4backwards distinct.'),
        ('restart','/zero_load_replay_tested',True,'Actual B FIT replay preserves bytes without loads, config mismatch/corruption rejected.')]:
        gates.append(dict(id=category,category=category,evidence=rel+'/test_evidence.json',pointer=pointer,op='eq',expected=expected,reason=reason))
    deps=['ab_confirmatory_20261101/'+n for n in DEPENDENCIES+['prepare_fit_b.py','test_worker_b.py','test_transcoder.py']]
    contract=dict(schema_version=1,id='AB_B_PRIMARY_FIT_ONLY_20261101_v1',kind='experiment',primary_agent='/root',
        purpose='Fixed new B FIT capture, full qualification then final direction/projected qualification, native-vector baselines. NoPILOT/TEST.',
        tracked_files=deps+[rel+'/'+n for n in documents+['config.json','corpus.json','tokens.json','model_identity.json','cost_estimate.json','synthetic_tests.log']],
        tracked_trees=[],input_manifests=[rel+'/model_manifest.json',rel+'/input_manifest.json'],gates=gates,circuits=[],
        structural_scope='Full native layer15 postnorm output replacement with complete later native attention/MLP. No last-layer shortcut. Nonzero measured sensitivity and input/output parity; finalw only after128natural FIT captures.',
        entrypoint=dict(module='ab_confirmatory_20261101.worker_b',args=['--config',rel+'/config.json']),schedule=rel+'/operations.json',budget=counts)
    put('contract.json',contract)
    print(json.dumps(dict(stage=rel,documents=len(docs),budget=counts,tests='REQUIRES actual separate receipt')))

if __name__=='__main__':main()
