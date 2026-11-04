"""Offline final descriptive contrasts and cumulative execution accounting."""
import json
from pathlib import Path
from collections import Counter
from research_checks.gate import read,sha,digest
from analysis.B_mechanism_20261102.common import unwrap
H=Path(__file__).resolve().parent;R=H.parents[2]
def main():
    summary=unwrap(H/'run_v3/SUMMARY.json');seal=unwrap(H/'run_v3/stage_completed.json')
    # complete_v3 already checked every immutable output. Bind that exact
    # manifest; do not perform another identical22k-file read here.
    verified=read(H/'completion_manifest_v3.json')['files']
    for name,h in seal['files'].items():
        assert verified[(H/'run_v3'/name).relative_to(R).as_posix()]==h
    counts={};files=[]
    for label,folder in [('initial_failed',H/'run'),('qualification',H/'qualification/run'),('corrected',H/'run_v3')]:
        ledger=folder/'ledger.jsonl';records=[json.loads(x) for x in ledger.read_text().splitlines()]
        for v in records:assert digest(v['record'])==v['sha256']
        attempts=[v['record'] for v in records if v['record']['event']=='attempt']
        assert len({v['operation'] for v in attempts})==len(attempts)
        counts[label]=dict(Counter(v['kind'] for v in attempts));files.append(ledger)
    cumulative={k:sum(c.get(k,0) for c in counts.values()) for k in ['forward','backward']}
    contrasts={};switch_counts={}
    rows=[unwrap(p) for p in sorted((H/'run_v3/results').glob('*.json'))]
    assert len(rows)==768
    for operator in ['full','projected']:
        for dose in [.05,1.]:
            subset=[r for r in rows if r['operator']==operator and r['dose']==dose]
            switch_counts[f'{operator}/{dose}']=dict(contexts=len(subset),mean_top=sum(r['features']['top_switches'] for r in subset)/len(subset),mean_random=sum(r['features']['random_switches'] for r in subset)/len(subset),random_zero=sum(r['features']['random_switches']==0 for r in subset))
    lines=['# B3/B5: complete fixed-corpus diagnostics','',
      '32 previously observed blocks16–47;768 cells. Posthoc oracle diagnosis, no fresh holdout or population claim. All strata and negative contrasts retained.',
      'B3 changes whole residual direction using two same-dose partners while preserving norm. B5 manipulates FIT-selected feature switches versus random pools of the same32features. Actual switched-feature counts and vector norms are NOT matched. The full-dose random pool is usually inactive, so this control does not isolate feature identity at equal intervention strength. These interventions concern the replacement operator, not recovery of a native circuit.','',
      '| Stratum | partner1 − RR | partner7 − RR | EXCEPT top − EXCEPT random | ONLY top − ONLY random |',
      '|---|---:|---:|---:|---:|']
    for key,v in summary['groups'].items():
        m=lambda arm:v[arm]['mean_loss']
        delta=lambda a,b:None if m(a) is None or m(b) is None else m(a)-m(b)
        vals=[delta('partner1','RR'),delta('partner7','RR'),delta('EXCEPT_top','EXCEPT_random'),delta('ONLY_top','ONLY_random')]
        contrasts[key]=dict(zip(['partner1_minus_RR','partner7_minus_RR','except_top_minus_random','only_top_minus_random'],vals))
        lines.append('| '+key+' | '+' | '.join('undefined' if x is None else f'{x:.8g}' for x in vals)+' |')
    lines+=['','Positive first/second columns mean the original residual direction has lower loss than that partner. Positive third means removing FIT-selected switches harms more than removing random switches. Negative fourth means retaining FIT-selected switches beats retaining random switches. These are descriptive conditional comparisons, not universal necessity/sufficiency claims.',
      '',f'Cumulative actual charged operations: {cumulative}; components: {counts}. Adopted results are not charged again. The initial failed stage and qualification remain in cumulative cost.',
      'The initial failure occurred after461F+4B due to thread-dependent float32 reduction;2TC-only qualification calls at historical2threads reproduced both failed vectors bitwise. Corrected TC encoding/decoding uses2threads; native suffix1thread. Actual1thread FIT-selected groups and valid controls are explicitly preserved; every evaluated endpoint retains exact parity checks.',
      'Actual switching counts by condition: '+json.dumps(switch_counts,sort_keys=True),
      'Independent final completion review pending.']
    (H/'REPORT_v4.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    (H/'final_analysis_v3.json').write_text(json.dumps(dict(scope='posthoc32observedblocks768cells',counts=counts,cumulative=cumulative,contrasts=contrasts,switch_counts=switch_counts),indent=2)+'\n')
    manifest={'files':{}}
    for p in files+[H/'finish_v3.py',H/'REPORT_v4.md',H/'final_analysis_v3.json',H/'qualification/completion_audit.json',H/'completion_snapshot_v3.json',H/'completion_manifest_v3.json']:
        manifest['files'][p.relative_to(R).as_posix()]=sha(p)
    (H/'completion_manifest_v4.json').write_text(json.dumps(manifest,indent=2)+'\n')
    c=read(H/'completion_contract_v3.json');c['id']+='_CUMULATIVE';c['primary_agent']='/root/b_second_artifact_five';c['input_manifests']=[(H/'completion_manifest_v4.json').relative_to(R).as_posix()]
    c['purpose']='Layered extension of exact full raw completion_snapshot_v3: descriptive contrasts and cumulativecost, no repeated inference or fullrawrehash.'
    c['tracked_files'] += [(H/n).relative_to(R).as_posix() for n in ['finish_v3.py','REPORT_v4.md','final_analysis_v3.json']]
    (H/'completion_contract_v4.json').write_text(json.dumps(c,indent=2)+'\n')
if __name__=='__main__':main()
