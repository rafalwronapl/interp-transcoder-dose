"""Materialize new FIT-transfer tail qualification; zero model calls here."""
import json
from pathlib import Path
from .prepare import ROOT,OUT,sha
from .worker_b_evaluate import schedule,DEPENDENCIES,unwrap

def main():
    stage=OUT/'B_tail_qualification_v1'
    if stage.exists():raise ValueError('Version existing packet rather than overwrite')
    old=OUT/'B_fit_primary_v1';fit=old/'run/FIT_B.json'
    completed=unwrap(old/'run/stage_completed.json')
    for name,h in completed['files'].items():
        if sha(old/'run'/name)!=h:raise ValueError('Changed completed FIT evidence')
    source=OUT/'corpus/corpus_v1.json';token_source=OUT/'corpus/tokens_v1.json'
    pool=[d for d in json.loads(source.read_text(encoding='utf-8'))['documents']
          if d['study']=='B' and d['split']=='FIT' and d['frame']=='transfer']
    blocks=sorted({d['block'] for d in pool})[:2]
    docs=[d for d in pool if d['block'] in blocks]
    if len(docs)!=4 or any(d['donor'] not in {x['id'] for x in docs} for d in docs):raise ValueError('Need four paired unused FIT transfer records')
    previous={d['id'] for d in json.loads((old/'corpus.json').read_text())['documents']}
    if previous.intersection(d['id'] for d in docs):raise ValueError('Would repeat existing natural captures')
    all_tokens=json.loads(token_source.read_text());tokens={d['id']:all_tokens[d['id']] for d in docs}
    stage.mkdir();rel=stage.relative_to(ROOT).as_posix()
    def put(name,obj):
        (stage/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
    put('corpus.json',dict(documents=docs,scope='First two FIT transfer pairs, unused by main-template FIT'))
    put('tokens.json',tokens)
    oldcfg=json.loads((old/'config.json').read_text())
    cfg=dict(study='B',phase='TAIL_QUALIFICATION',corpus=rel+'/corpus.json',tokens=rel+'/tokens.json',
        model_identity=oldcfg['model_identity'],frozen_fit=fit.relative_to(ROOT).as_posix(),frozen_fit_sha256=sha(fit),
        output=rel+'/run',threads=2,layer=oldcfg['layer'],answer_ids=oldcfg['answer_ids'],doses=[.05,2.],
        gates=dict(margin_parity=1e-4,branch_relative=1e-4,gradient_relative=1e-4,gradient_absolute=1e-5),schedule=rel+'/operations.json')
    put('config.json',cfg);ops=schedule(cfg,docs);put('operations.json',ops)
    budget={k:sum(o['kind']==k for o in ops['operations']) for k in ('forward','backward')}
    put('cost.json',dict(budget=budget,new_documents=4,repeated_natural_captures=0,full_forwards=56,
        tail_forwards=52,local_native_endpoints=16,local_TC=20,local_JVP=8,backwards=8,
        purpose='Technical equivalence only; neither scientific PILOT nor TEST. Every new call separately recorded.'))
    inputs=[source,token_source,old/'run/stage_completed.json',fit,ROOT/oldcfg['model_identity'],
            OUT/'lexical_review/review_v3.json']
    inputs.extend(old/'run'/name for name in completed['files'])
    # FIT acceptance is independently supplied before review/launch. No invented approval.
    put('input_manifest.json',dict(files={p.relative_to(ROOT).as_posix():sha(p) for p in inputs}))
    protocol='''# B exact native tail qualification\n\nTechnical stage on four previously unused FIT-transfer recipients (first two fixed name pairs).\nNo PILOT/TEST, no refit, no scientific claim. Frozen FIT direction used without selection.\nFull and projected interventions at fixed doses .05 and2 compare actual full-forward margins\nwith exact common-prefix reuse for NATIVE, TC and TAYLOR predictions. All later native\nattention/MLP layers execute dynamically; no attention freezing or KV-cache approximation.\nNatural margin and native branch anchors checked for every recipient; gradient parity checked\nat the natural anchor. Full margin tolerance1e-4, branch relative1e-4, gradient relative1e-4\nand absolute1e-5. Any failure stops; no threshold adjustment from these measurements.\nNew captures are distinct from existing128FIT main-template captures. Completed operation\ncache is preserved on resume. Failed attempted operations without durable results require\na separately reviewed amendment, never an automatic retry. Zero-load complete replay.\nRandom-weight end-to-end test and separate independent FIT completion review required before launch.\n'''
    (stage/'PROTOCOL.md').write_text(protocol,encoding='utf-8')
    gates=[]
    for category,pointer,value,why in [
        ('hooks','/exact_tail_integration_passed',True,'Random full/tail parity, acquisition, cache and anchor tests.'),
        ('data','/unused_fit_documents',4,'Four literal new FIT transfer recipients; no TEST access.'),
        ('pilot','/scientific_inference',False,'Technical equivalence only.'),
        ('accounting','/scheduled_forward',budget['forward'],'Exact complete forward/backward schedule, full vs local cost separate.'),
        ('restart','/zero_load_replay_passed',True,'Durable prefix preserved and complete replay loads no model.')]:
        gates.append(dict(id=category,category=category,evidence=rel+'/test_evidence.json',pointer=pointer,op='eq',expected=value,reason=why))
    gates.append(dict(id='fit_review',category='data',evidence=rel+'/fit_acceptance.json',pointer='/verdict',op='eq',expected='approved',reason='Actual independent completion review of imported frozen FIT.'))
    tracked=['ab_confirmatory_20261101/'+n for n in DEPENDENCIES+['prepare_tail_b.py','test_worker_b_evaluate.py','test_native_tail_b.py']]
    tracked += [rel+'/'+n for n in ['config.json','corpus.json','tokens.json','cost.json','PROTOCOL.md','synthetic_tests.log']]
    put('contract.json',dict(schema_version=1,id='AB_B_TAIL_QUALIFICATION_20261101_v1',kind='experiment',primary_agent='/root',
        purpose='Validate exact downstream tail reuse against full native execution, using four new FIT-transfer recipients.',
        tracked_files=tracked,tracked_trees=[],input_manifests=[rel+'/input_manifest.json',old.relative_to(ROOT).as_posix()+'/model_manifest.json'],
        gates=gates,circuits=[],structural_scope='All native layers after15 execute with dynamic attention. Last-token postnormMLP replacement before residual addition.',
        entrypoint=dict(module='ab_confirmatory_20261101.worker_b_evaluate',args=['--config',rel+'/config.json']),schedule=rel+'/operations.json',budget=budget))
    print(json.dumps(dict(stage=rel,budget=budget,ready_for_launch=False,pending='actual synthetic receipt and independent FIT completion review')))

if __name__=='__main__':main()
