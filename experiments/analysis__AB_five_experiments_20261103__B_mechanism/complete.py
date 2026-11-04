"""Offline completion packet, no inference reruns or model calls."""
from pathlib import Path
from analysis.B_mechanism_20261102.common import ROOT,read,sha,rel,put,unwrap
BASE=Path(__file__).resolve().parent

def main():
    out=BASE/'run';seal=unwrap(out/'stage_completed.json')
    for name,h in seal['files'].items():
        if sha(out/name)!=h:raise ValueError('Changed output '+name)
    summary=unwrap(out/'SUMMARY.json');rows=[unwrap(p) for p in sorted((out/'results').glob('*.json'))]
    assert len(rows)==768 and len({r['document']['block'] for r in rows})==32
    text=['# B residual and feature-switch diagnostics','',
      '32 previously observed blocks16--47;768 cells; posthoc oracle diagnostics. Both partners and all feature arms retained. No fresh-holdout or population claim.',
      'Group selection used FIT switch-vector magnitude only. Endpoint masks were manipulated at fixed endpoint preactivations; effects concern this replacement operator, not native circuit recovery.','',
      '| Stratum | RR loss | Partner1 | Partner7 | Only top | Except top | Only random | Except random |','|---|---:|---:|---:|---:|---:|---:|---:|']
    for k,v in summary['groups'].items():
        values=[v[a]['mean_loss'] for a in ['RR','partner1','partner7','ONLY_top','EXCEPT_top','ONLY_random','EXCEPT_random']]
        text.append('| '+k+' | '+' | '.join('undefined' if x is None else f'{x:.8g}' for x in values)+' |')
    text+=['','ON/OFF/BASE/FROZEN, signed effects, actual norms, per-cell finite interactions and rounding are retained in SUMMARY.json and results/. Missing/zero directions remain explicitly undefined.','',
      f"Actual charged operations: {seal['attempted']}; explicit aliases {seal['aliases']}; undefined skips {seal['skips']}.",
      'Independent final review pending in completion_review.json.']
    (BASE/'REPORT.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    put(BASE/'completion_checks.json',dict(passed=True,cells=768,blocks=32,model_calls_in_report=0,**{k:seal[k] for k in ['attempted','aliases','skips']}))
    files=[p for p in out.rglob('*') if p.is_file()]+[BASE/n for n in ['REPORT.md','completion_checks.json','complete.py','pre_run_snapshot_v2.json','pre_run_review_v2.json','PROTOCOL.txt','source_index.json','config.json','operations.json','input_manifest.json']]
    put(BASE/'completion_manifest.json',dict(files={rel(p):sha(p) for p in files}))
    put(BASE/'completion_contract.json',dict(schema_version=1,id='AB5_B_MECHANISM_COMPLETION_20261103',kind='maintenance',primary_agent='/root',purpose='Offline accounting and descriptive report of same-dose residual and FIT-selected feature switching.',
        tracked_files=[rel(BASE/n) for n in ['complete.py','REPORT.md','completion_checks.json']],tracked_trees=[],input_manifests=[rel(BASE/'completion_manifest.json')],
        gates=[dict(id='completed',category='accounting',evidence=rel(BASE/'completion_checks.json'),pointer='/passed',op='eq',expected=True,reason='Complete immutable768cells and workerterminal coverage assertion.')],
        circuits=[],structural_scope='Offline report of accepted native suffix interventions only.',entrypoint=None,schedule=None,budget=None))
if __name__=='__main__':main()
