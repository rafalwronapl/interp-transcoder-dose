import json
from .common import *
def main():
    out=HERE/'run';done=unwrap(out/'stage_completed.json');s=unwrap(out/'SUMMARY.json');corpus=read(HERE/'corpus.json')
    lines=['B fresh confirmation and grammatical readout/context transfer, 2026-11-03','Completed measurements; independent completion review pending (see actual review receipt).',
    '32fresh exclusive-name-category pairs;256contexts; no name reused from frozen historical corpus/source-index inventory. Fixedsixgroups andrho101.51097375004979, full donor normalized-input replacement,dose1. No fit/selection from new readouts.',
    'Primary: equal-block top32 MSEincrement relative toTC_FULL minus equal mean offive overlapping-control increments on so/when. Positive means larger top-direction squared-error increase; no native-circuit interpretation.']
    for f in ['primary_so_when','so','when','transfer','object']:
        r=s[f];lines.append(f"{f}: eligible{r['eligible_contexts']}/{r['contexts']};blocks{r['eligible_blocks']}/{r['blocks']};top-minus-controls MSEincrement={r['primary_top_minus_controls']};groupincrements={json.dumps(r['group_mean_increment'],sort_keys=True)};absoluteeffects={json.dumps(r['group_mean_absolute_effect'],sort_keys=True)}")
    lines.extend(['Readouts:'+json.dumps(corpus['readouts'])+'; so/when/transfer use she-minus-he; object uses her-minus-him after receptionist greeted. The object frame is both a changed construction and changed readout; this does not isolate token identity as cause.',
    'Cost:'+json.dumps(done['accounting'],sort_keys=True)+f";native/TC loads={done['model_loads']}; all attempted operations counted, including local TC/native branch calls and technical controls. No backward/cloud/download.",
    'Limits: fixed model Gemma270M/L15, one artifact, one interventiondose,32blocks; overlapping controls are not independent replications; eligibility conditional on allsixnorms; rare names and category labels do not establish human gender. Fresh confirmation concerns norm-rescaled TC prediction directions, not native switch counts or general language competence.',
    'All scientific targets globally sealed before finite native endpoints/scientific suffixes. Natural captures and16technical controls do not enter selection. Frozen corpus, contextualtoken assertions,input_manifest,run/TARGETS_FROZEN,ledger,results,SUMMARY,stage_completed preserve evidence. Negative results retained.'])
    (HERE/'REPORT.txt').write_text('\n\n'.join(lines)+'\n',encoding='utf-8');print('\n'.join(lines))
if __name__=='__main__':main()
