"""Prepare bound source inventory and exact operation budget, without model calls."""
from pathlib import Path
import json,runpy
from analysis.B_mechanism_20261102.common import ROOT,read,sha,rel,put,unwrap
BASE=Path(__file__).resolve().parent
OLD=ROOT/'analysis/AB_confirmatory_execution_20261101/B_descriptive_TEST_v8'
FIT=ROOT/'analysis/AB_confirmatory_execution_20261101/B_fit_primary_v1'
QUAL=ROOT/'analysis/AB_confirmatory_execution_20261101/B_tail_qualification_v1'

def build():
    manifest={};index=dict(documents=[],captures={},cells=[],fit=[],controls={})
    def bind(p):
        name=rel(p)
        if name not in manifest:manifest[name]=sha(p)
        return name
    opmemo={}
    def op(folder,name):
        key=(str(folder),name)
        if key in opmemo:return opmemo[key]
        receipt=folder/'run/completed'/f'{name}.json';v=unwrap(receipt)
        cache=folder/'run/cache'/f"{v['request']}.json"
        opmemo[key]=dict(receipt=bind(receipt),cache=bind(cache));return opmemo[key]
    cfg=read(OLD/'config.json');docs=read(ROOT/cfg['corpus'])['documents']
    fit_path=bind(ROOT/cfg['frozen_fit'])
    selected=[d for d in docs if 16<=d['index']<48];assert len(selected)==192
    lookup={(d['index'],d['frame'],d['side']):d for d in selected}
    index['documents']=selected
    for d in selected:
        i=d['id'];index['captures'][i]=op(OLD,'capture_'+i)
        for operator in ['full','projected']:
            for ci,c in [(0,.05),(4,1.)]:
                tag=f'{i}_{operator}_{ci}'
                index['cells'].append(dict(id=tag,document=d,operator=operator,dose=c,
                    tcbase=op(OLD,'tc_base_'+i),tcend=op(OLD,'tc_endpoint_'+tag),
                    native=op(OLD,'tail_'+tag+'_NATIVE'),tc=op(OLD,'tail_'+tag+'_TC'),frozen=op(OLD,'tail_'+tag+'_FROZEN'),
                    partners=[f"{lookup[(16+(d['index']-16+k)%32,d['frame'],d['side'])]['id']}_{operator}_{ci}" for k in [1,7]]))
    fdocs=read(FIT/'corpus.json')['documents']
    for d in fdocs:index['fit'].append(dict(document=d,capture=op(FIT,'capture_'+d['id'])))
    oldidx=read(ROOT/'analysis/B_mechanism_20261102/stage1_v1/source_index.json')
    for i,item in oldidx['controls'].items():
        index['controls'][i]=item
        for entry in item.values():
            for value in entry.values():
                if isinstance(value,str) and (ROOT/value).is_file():bind(ROOT/value)
    for folder,ver in [(OLD,1),(QUAL,2)]:
        for name in [f'completion_snapshot_v{ver}.json',f'completion_review_astra_v{ver}.json','run/identity.json']:bind(folder/name)
    for f in [ROOT/cfg['model_identity'],OLD/'config.json',ROOT/cfg['corpus'],ROOT/cfg['tokens'],FIT/'corpus.json',BASE/'PROTOCOL.txt']:bind(f)
    ident=read(ROOT/cfg['model_identity'])
    for group in ['B','TC']:
        for name,meta in ident[group]['files'].items():
            assert (ROOT/name).stat().st_size==meta['bytes'];manifest[rel(ROOT/name)]=meta['sha256']
    ops=[]
    def add(i,kind='forward'):ops.append(dict(id=i,kind=kind))
    for i in index['controls']:
        for arm in ['gradient','plus','minus']:add('control_'+i+'_'+arm)
        add('control_'+i+'_backward','backward')
    for item in index['fit']:
        for arm in ['base','end']:add('fit_'+item['document']['id']+'_'+arm)
    for d in selected:add('encode_base_'+d['id'])
    for cell in index['cells']:
        add('encode_end_'+cell['id'])
        for arm in ['FULL','ONLY_top','EXCEPT_top','ONLY_random','EXCEPT_random','ON','OFF','BASE']:add('decode_'+cell['id']+'_'+arm)
        for arm in ['partner1','partner7','ONLY_top','EXCEPT_top','ONLY_random','EXCEPT_random','ON','OFF','BASE']:add(cell['id']+'_'+arm)
    put(BASE/'source_index.json',index);bind(BASE/'source_index.json')
    put(BASE/'operations.json',dict(operations=ops));bind(BASE/'operations.json')
    conf=dict(source_index=rel(BASE/'source_index.json'),schedule=rel(BASE/'operations.json'),output=rel(BASE/'run'),
        input_manifest=rel(BASE/'input_manifest.json'),model_identity=cfg['model_identity'],frozen_fit=fit_path,threads=1)
    put(BASE/'config.json',conf);bind(BASE/'config.json')
    helper='analysis/AB_confirmatory_execution_20261101/close_short_pilot_imports_v1.py'
    seeds=[rel(BASE/n) for n in ['prepare.py','worker.py','geometry.py','fixtures.py']]+[helper]
    closure=runpy.run_path(str(ROOT/helper))['closure']
    tracked=sorted(set(seeds)|set(closure(seeds)))
    for name in tracked:bind(ROOT/name)
    # Dynamic imports used only after approval are explicit dependencies.
    for name in ['ab_confirmatory_20261101/native.py','ab_confirmatory_20261101/native_tail_b.py','ab_confirmatory_20261101/transcoder.py']:
        for path in set([name])|set(closure([name])):bind(ROOT/path)
    put(BASE/'input_manifest.json',dict(files=manifest))
    budget={k:sum(o['kind']==k for o in ops) for k in ['forward','backward']}
    put(BASE/'budget.json',dict(**budget,documents=len(selected),cells=len(index['cells']),fit_documents=len(fdocs),native_capture=0,scientific_backward=0))
    put(BASE/'contract.json',dict(schema_version=1,id='AB5_B_MECHANISM_20261103',kind='experiment',primary_agent='/root',
        purpose='Same-dose whole residual and FIT-selected feature switching; posthoc oracle finite-corpus diagnostics.',
        tracked_files=tracked+[rel(BASE/'PROTOCOL.txt'),rel(BASE/'budget.json'),rel(BASE/'fixtures.json')],tracked_trees=[],input_manifests=[rel(BASE/'input_manifest.json')],
        gates=[dict(id=k,category=k,evidence=rel(BASE/'fixtures.json'),pointer='/passed',op='eq',expected=True,reason='Detailed fixtures and accepted adapter parity/control adoption reviewed independently.') for k in ['hooks','data','pilot','accounting','restart']],
        circuits=[],structural_scope='Original L15 output to exact dynamic L16/L17 then head; accepted adapter reused with fixed FIT controls.',
        entrypoint=dict(module='analysis.AB_five_experiments_20261103.B_mechanism.worker',args=['--config',rel(BASE/'config.json')]),schedule=rel(BASE/'operations.json'),budget=budget))
    print(json.dumps(budget))
if __name__=='__main__':build()
