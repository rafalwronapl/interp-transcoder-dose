"""Versioned metadata correction and fixed-group frame summaries; no refitting."""
import copy,json
import numpy as np
from analyze import HERE,ROOT,read,sha,save,distances,distributions

def main():
    r=read(HERE/'FIT_FEASIBILITY.json');docs=r['documents']
    frames=sorted({d['frame'] for d in docs});blocks=np.array([d['block'] for d in docs]);unique=np.unique(blocks)
    assert len(docs)==128 and len(unique)==32 and frames==['so','when']
    correction=dict(schema_version=1,reason='Original frozen worker/protocol/report incorrectly described actual FIT as64blocks/so-only. Numeric worker used all128documents and32actualblocks. Correct metadata without rerunning matching or changing any selected group.',
        supersedes={x:sha(HERE/x) for x in ['analyze.py','PROTOCOL.txt','INVENTORY.json','FIT_FEASIBILITY.json','FROZEN_GROUPS.json','REPORT.txt']},
        correct_scope=dict(documents=128,blocks=32,frames=frames,operator='full',dose=1),
        numerical_adoption='All original pooled numeric distributions, scores, thresholds, decoder algebra, heuristic groups and analytic bound adopted unchanged; tolerance resampling dynamically used32blocks. Per-frame diagnostics added posthoc for fixed groups only.',
        model_loads=0,pretrained_forwards=0)
    v=copy.deepcopy(r);v['scope']='Historical FIT only:32independent blocks,128documents,frames so/when,full operator dose1; selection and primary matching objective pooled across frames; no TEST readouts'
    v['missing_conditions']=['full dose .05 FIT endpoints','projected dose .05 and1 FIT endpoints','transfer FIT frame']
    v['scope_correction']=correction;v['posthoc_frame_summaries']={}
    for frame in frames:
        keep=np.array([d['frame']==frame for d in docs]);bb=blocks[keep]
        tc=np.asarray(r['top_distribution']['count'])[keep];tn=np.asarray(r['top_distribution']['norm'])[keep]
        rng=np.random.default_rng(20261102);null=[]
        for _ in range(128):
            half=np.isin(bb,rng.permutation(unique)[:len(unique)//2]);null.append(distances(tc[half],tn[half],tc[~half],tn[~half]))
        tol=np.quantile(null,.95,axis=0);groups=[]
        for g in r['groups']:
            c=np.asarray(g['distribution']['count'])[keep];n=np.asarray(g['distribution']['norm'])[keep];ds=distances(c,n,tc,tn)
            groups.append(dict(seed=g['seed'],W1_count_norm=ds.tolist(),distribution=distributions(c,n),within_frame_FIT_band=bool(np.all(ds<=tol))))
        v['posthoc_frame_summaries'][frame]=dict(documents=int(keep.sum()),blocks=len(np.unique(bb)),top_distribution=distributions(tc,tn),tolerance_count_norm=tol.tolist(),groups=groups,
            interpretation='Descriptive posthoc stratification of unchanged pooled-selected groups, not a separate per-frame selection/optimization or independent test.')
    save(HERE/'FIT_FEASIBILITY_v2.json',v)
    groups=read(HERE/'FROZEN_GROUPS.json');groups['condition']=dict(operator='full',dose=1,frames=frames,blocks=32,selection='pooled acrossso/when');groups['supersedes_sha256']=sha(HERE/'FROZEN_GROUPS.json')
    save(HERE/'FROZEN_GROUPS_v2.json',groups)
    inv=read(HERE/'INVENTORY.json');inv['missing']=['FIT .05 full endpoint preactivations','FIT .05 and1 projected endpoint preactivations','transfer FIT frame'];inv['supersedes_sha256']=sha(HERE/'INVENTORY.json')
    save(HERE/'INVENTORY_v2.json',inv);save(HERE/'SCOPE_CORRECTION_v2.json',correction)
    text=(HERE/'REPORT.txt').read_text(encoding='utf-8')
    text=text.replace('64 independent blocks,128 recipient documents, so frame','32 independent blocks,128 recipient documents, so/when frames (64documents each), pooled selection/matching objective')
    text=text.replace('Additional when/transfer FIT frames are absent from this source_index FIT. For the same64blocks and2sides,2frames would need256newnativecaptures if no compatible capture exists elsewhere, plus TC encodings (at most256base+1024endpoints for4conditions before donor/end deduplication).',
        'Only transfer FIT frame is absent from this source_index FIT. For the same32blocks and2sides, one frame would need64newnativecaptures if no compatible capture exists elsewhere, plus TC encodings (at most64base+256endpoints for4conditions before donor/end deduplication).')
    text=text.replace('so/full/c1 FIT','pooled so+when/full/c1 FIT').replace('Observed so/full/c1 requires','Observed so+when/full/c1 requires')
    text=text.replace('FIT_FEASIBILITY.json (all per-context distributions); FROZEN_GROUPS.json','FIT_FEASIBILITY_v2.json (all per-context distributions and posthoc per-frame summaries); FROZEN_GROUPS_v2.json')
    text='CORRECTED REPORT v2 — supersedes REPORT.txt scope and missing-frame accounting; original artifacts preserved.\nOriginal worker/protocol incorrectly said64blocks/so-only; actual input and numerical computations used32blocks and bothso/when frames. See SCOPE_CORRECTION_v2.json. No matching recomputation or model calls.\n\n'+text
    text+='\nPosthoc per-frame diagnostics, unchanged pooled-selected groups:\n'
    for frame,a in v['posthoc_frame_summaries'].items():
        text+=f"{frame}:32blocks,64documents; top mean count {a['top_distribution']['mean_count']:.6f}, norm {a['top_distribution']['mean_norm']:.6f}; frame-specific descriptive bands {a['tolerance_count_norm']}.\n"
        for g in a['groups']:text+=f"  seed{g['seed']}: mean count {g['distribution']['mean_count']:.6f}, norm {g['distribution']['mean_norm']:.6f}; W1 {g['W1_count_norm']}; within bands={g['within_frame_FIT_band']}.\n"
    text+='These frame summaries were added after the pooled result; they did not select/retune groups or bands used in the primary pooled feasibility calculation. The analytic norm bound is pooled acrossso/when, not automatically a frame-specific impossibility proof.\n'
    p=HERE/'REPORT_v2.txt';data=text.encode('utf-8')
    if p.exists():assert p.read_bytes()==data
    else:p.write_bytes(data)
    print(json.dumps(correction['correct_scope']))

if __name__=='__main__':main()
