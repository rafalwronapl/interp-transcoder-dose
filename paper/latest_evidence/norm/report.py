"""Summarize sealed native-readout diagnostic; no model calls or selection."""
import json
import numpy as np
from .common import HERE,ROOT,read,unwrap,sha,put
from .worker import ARMS

def main():
    cfg=read(HERE/'config.json');out=ROOT/cfg['output'];seal=unwrap(out/'stage_completed.json')
    for name,h in seal['files'].items():assert sha(out/name)==h,'Changed completed output'
    summary=unwrap(out/'SUMMARY.json');rows=[unwrap(p) for p in sorted((out/'results').glob('*.json'))];eligible=[r for r in rows if r['eligible']]
    blocks=sorted({r['document']['block'] for r in eligible});metrics={}
    for arm in ARMS:
        def bm(fn):return float(np.mean([np.mean([fn(r) for r in eligible if r['document']['block']==b]) for b in blocks])) if blocks else None
        metrics[arm]=dict(MSE=bm(lambda r:r['loss'][arm]),MSE_increment=bm(lambda r:r['loss'][arm]-r['reference_loss']),signed_effect=bm(lambda r:r['effects'][arm]),absolute_effect=bm(lambda r:abs(r['effects'][arm])))
    reference_mse=float(np.mean([np.mean([r['reference_loss'] for r in eligible if r['document']['block']==b]) for b in blocks])) if blocks else None
    targets=[unwrap(HERE/name) for name in unwrap(HERE/'TARGETS_FROZEN.json')['files']]
    alltargets=[t for r in targets if r['eligible'] for t in r['targets']]
    numerical=dict(intended_norm=cfg['rho'],actual_norm_range=[min(t['actual_norm'] for t in alltargets),max(t['actual_norm'] for t in alltargets)],
        maximum_rounding_norm=max(t['rounding_norm'] for t in alltargets),maximum_rounding_bound=max(t['rounding_bound'] for t in alltargets),
        amplification_range=[min(t['amplification'] for t in alltargets),max(t['amplification'] for t in alltargets)],maximum_direction_cosine_error=max(abs(1-t['direction_cosine']) for t in alltargets))
    result=dict(summary=summary,metrics=metrics,reference_MSE=reference_mse,numerical=numerical,accounting=seal['accounting'],native_loads=seal['native_loads'],
        stage_completed_sha256=sha(out/'stage_completed.json'),targets_frozen_sha256=sha(HERE/'TARGETS_FROZEN.json'),native_prefix_calls=0,TC_calls=0,new_backward_calls=0)
    put(HERE/'FINAL_ANALYSIS.json',result)
    lines=['B norm-control — completed posthoc native-readout diagnostic, 2026-11-03','',
        'Question: do FIT top32 TC mask-removal directions affect native readout differently from five fixed alternative-group directions at equal output-vector norm?',
        'Changed estimand: TC mask-induced prediction directions normalized around TC_FULL/RR reference. Historical ON arm is not used. These are neither equal native feature-switch counts nor direct native neuron/circuit interventions.',
        '',f"Scope:32historicalTESTblocks,128contexts,so/when,2sides,full operator,dose1. Eligible {summary['eligible_contexts']}/{summary['contexts']},eligibleblocks {summary['eligible_blocks']}. Transfer excluded. Existing outcomes were exposed; this is posthoc, not fresh confirmation.",
        f"Six groups fixed before measurement: originaltop32 and five approvedB-FITalternativegroups (seeds20261103..20261107,overlap28..31features). FIT32blocks/128documents fixed rho=q10(min-six-norms)={cfg['rho']:.12f}; eps=rho/4={cfg['eps']:.12f}. JointALL6eligibility,cap4. FITeligible127/128; no TESTretuning.",
        'All targetvectors and eligibility were hash-sealed in TARGETS_FROZEN.json before any new readout. Target_g=TC_FULL_target−rho*S_g/norm(S_g), where S_g is the summed signed threshold-switch decoder contribution. Native error D was not used for construction.',
        '',f"Primary contrast (top MSEincrement minus equal mean offivecontrolincrements; equal blockweights): {summary['primary_top_minus_controls']:.12g}. Positive means top removal caused a larger squared-error increase aroundTC_FULL; negative means a smaller increase. This does not itself establish importance of a native circuit.",
        f"TC_FULL/RR referenceMSE on sameeligibleblocks: {reference_mse:.12g}.",
        'Group | MSE | increment vsTC_FULL | mean signed readout effect | mean absolute readout effect']
    for a,m in metrics.items():lines.append(f"{a} | {m['MSE']:.12g} | {m['MSE_increment']:.12g} | {m['signed_effect']:.12g} | {m['absolute_effect']:.12g}")
    lines+=['','Frame summaries (samefrozen pooledFITscale/groups):']
    for f,s in summary['per_frame'].items():lines.append(f"{f}:eligible{s['eligible_contexts']}/{s['contexts']},blocks{s['eligible_blocks']}; topminuscontrols MSEincrement {s['primary_top_minus_controls']:.12g}.")
    lines+=['',f"Numerical matching afterfloat32:actualnormrange {numerical['actual_norm_range']}; intendedrho{cfg['rho']}; maxroundingnorm {numerical['maximum_rounding_norm']:.9g}; maxdeclaredroundingbound {numerical['maximum_rounding_bound']:.9g}; amplificationrange {numerical['amplification_range']}. Full context/group diagnostics retained.",
        '',f"Actual cost: {seal['accounting']['forward_attempts']}native suffix attempts,0backward,0TCforwards,0newnativeprefixforwards; {seal['accounting']['aliases']}exacttargetaliases,{seal['accounting']['skips']}skippedlogicalarms. Native model loads {seal['native_loads']}; TCloads0. Maximumreviewedbudget776logicalsuffixes included8technicalcontrols.",
        'Technical controls:two same-value native revalidations;four genuinelynew signed half-historical-step gradient-direction probes;two deliberate TC_FULL same-target parityrevalidations. These checks do not replace historical results or count as new scientific comparisons. Controls and parity tolerances passed before direction readouts.',
        '', 'Interpretation/limits: empirical finite-corpus diagnostic conditional on these FIT-selected directions,oneTCartifact,one she-minus-he readout and oneinterventioncondition. Equal vector norm does not imply equal number of switches,semanticcontent,curvature ornative circuit importance. Five controls overlap heavily; the unit is32blocks,notfive independent controlreplications. Original failed unscaled strengthmatching remains a valid distinct result.',
        'Everyeligiblecontext contributes allsix directions; missing contexts would be excludedjointly and explicitly reported. No bestgroup/condition chosen from newoutcomes. Negative results are retained. No globalnovelty,modelunderstanding orgeneralization claim.',
        '', 'Independent pre-run review and canonical launch were required. Final independent review: pending; consult review/completion_review receipt for actual status rather than this frozen report line.',
        'Evidence: PLAN.txt,config.json,FIT_SCALE_FREEZE.json,TARGETS_FROZEN.json,stage1_snapshot.json,stage2_snapshot_v2.json,review/,run/stage_completed.json,run/SUMMARY.json,run/results/,run/controls/,FINAL_ANALYSIS.json. All input/cache/model/code identities bound in stage2_input_manifest.json.']
    p=HERE/'REPORT.txt';data=('\n'.join(lines)+'\n').encode('utf-8')
    if p.exists():assert p.read_bytes()==data
    else:p.write_bytes(data)
    print(json.dumps(dict(primary=summary['primary_top_minus_controls'],eligible=summary['eligible_contexts'],cost=seal['accounting'])))
if __name__=='__main__':main()
