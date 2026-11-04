"""Independent closed-campaign accounting: metadata/proof reuse, no raw replay."""
import collections,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'analysis/AB_confirmatory_execution_20261101'
TARGET=BASE/'accounting_closed_campaign_20261102_v1.json'
OUT=Path(__file__).resolve().parent/'campaign_accounting_v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    with p.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def main():
    a=read(TARGET);assert len(a['stages'])==14 and len({s['id'] for s in a['stages']})==14
    totals=collections.Counter();hashes={};checks=[]
    review_names={'single_technical':'completion_review_v1.json','A_FIT_r0':'completion_review_sol/completion_review_v2.json','A_PILOT':'completion_review_sol_v1.json','A_fixed256_TEST':'completion_review_astra_v1.json','B_FIT_composite':'../B_fit_reference_recovery_v2/completion_review_astra_v1.json','B_tail_technical':'completion_review_astra_v2.json','B_descriptive_PILOT':'completion_review_astra_v1.json','B_descriptive_TEST':'completion_review_astra_v1.json'}
    def bind(path):
        path=path.resolve();name=path.relative_to(ROOT).as_posix()
        if name not in hashes:hashes[name]=sha(path)
        return hashes[name]
    for s in a['stages']:
        folder=ROOT/s['folder'];contract=read(folder/'contract.json');budget=contract['budget']
        for name,h in s['evidence_sha256'].items():assert bind(ROOT/name)==h,name
        cost=read(folder/'cost.json') if (folder/'cost.json').exists() else None
        review_path=(folder/review_names.get(s['id'],'completion_review_sol_v1.json')).resolve();r=read(review_path)
        assert r['independent'] is True and r['verdict']=='approved';bind(review_path)
        expected=dict(forward=s['forward'],backward=s['backward'])
        if s['id']=='B_FIT_composite':assert budget==dict(forward=1860,backward=4) and expected==dict(forward=1864,backward=4)
        else:assert budget==expected
        assert sum(s['components'].values())==s['forward']
        if cost:
            if 'full_transformer' in cost:expected_components=dict(full_transformer=cost['full_transformer'],local_suffix=cost['local_suffix'])
            elif 'total_forward' in cost:expected_components=dict(full_transformer=cost['full_forward'],local_suffix=cost['local_suffix'])
            elif 'local_suffix' in cost:expected_components=dict(full_transformer=cost['full_forward'],local_suffix=cost['local_suffix'])
            elif s['id']=='B_tail_technical':expected_components=dict(full_transformer=cost['full_forwards'],local_native=cost['local_native_endpoints'],native_JVP=cost['local_JVP'],TC_reference=cost['local_TC'],tail=cost['tail_forwards'])
            else:expected_components=dict(full_transformer=cost['full_forward'],local_native=cost['local_native'],native_JVP=cost['local_JVP'],TC_reference=cost['local_TC'],tail=cost.get('native_tail_forward',cost.get('tail_forward')))
            assert expected_components==s['components'],s['id']
        if s['id']=='single_technical':assert s['components']==dict(full_transformer=1)
        if s['id']=='A_FIT_r0':
            ops=read(folder/'operations.json')['operations'];suffix=sum(o['id'].endswith('_suffix_parity') for o in ops)
            assert len(ops)==482 and suffix==5 and s['components']==dict(full_transformer=477,local_suffix=5)
            replay=read(folder/'actual_cached_replay_v1.json');assert replay['exit_code']==0 and replay['all_bytes_preserved'] and replay['before']==replay['after'];bind(folder/'actual_cached_replay_v1.json')
            cfg=read(folder/'config.json');assert len(cfg.get('imports',{}))==1
            imported=next(iter(cfg['imports'].values()));assert 'single_capture_v1' in str(imported)
        totals.update({k:s[k] for k in ['forward','backward','language_model_loads']});totals.update(s['components'])
        assert s['language_model_loads']==(2 if s['id'] in ['A_fixed256_TEST','B_FIT_composite'] else 1)
        checks.append(dict(stage=s['id'],budget_and_components=True,prior_independent_completion_review=review_path.relative_to(ROOT).as_posix()))
    assert dict(totals)==a['totals']
    before=BASE/'B_fit_reference_recovery_v2/ledger_before.jsonl';rows=[json.loads(line)['record'] for line in before.read_text().splitlines()];kinds=collections.Counter(r['kind'] for r in rows if r['event']=='attempt');assert kinds==dict(forward=60,backward=4);bind(before)
    recovery=read(BASE/'B_fit_reference_recovery_v2/completion_summary_v1.json');assert recovery['reused_initial_logical_operations']==64 and recovery['recovery_new_forward']==1800 and recovery['main_forward_operations']==1860 and recovery['main_backward_operations']==4 and recovery['combined_forward_operations']==1864 and recovery['new_unfused_reference_operations']==4
    original=read(BASE/'B_fit_primary_v1/operations.json')['operations'];reference=read(BASE/'B_reference_unfused_v1/operations.json')['operations'];assert len(reference)==4 and all(o['kind']=='forward' for o in reference) and not ({o['id'] for o in original}&{o['id'] for o in reference})
    assert read(BASE/'B_fit_reference_recovery_v2/contract.json')['budget']==dict(forward=1800,backward=0)
    counts=collections.Counter(o['id'].split('_')[0] for o in original if o['kind']=='forward');assert counts['capture']==128 and sum(counts[k] for k in ['donor','sham','gradient','positive','full'])==24
    assert counts['endpoint']+counts['base']+counts['fd']==1692 and counts['jvp']==8 and counts['tc']+len(reference)==12
    reference_source=ROOT/'ab_confirmatory_20261101/reference_b_unfused.py';text=reference_source.read_text();assert 'load_file' in text and 'from_pretrained' not in text and 'AutoModel' not in text;bind(reference_source)
    prefix=read(ROOT/'analysis/A_estimation_v7/recovery_status_v1/prefix_audit.json');assert [prefix[k] for k in ['attempts','computed','cache','completed']]==[501]*4 and prefix['unknown_consumed']==0 and prefix['model_calls']==0
    remaining=read(ROOT/'analysis/A_estimation_v7/recovery_status_v1/contract.json')['budget'];assert remaining==dict(forward=35339,backward=0) and 501+remaining['forward']==35840
    bind(ROOT/'analysis/A_estimation_v7/recovery_status_v1/prefix_audit.json');bind(ROOT/'analysis/A_estimation_v7/recovery_status_v1/contract.json')
    single_replay=read(BASE/'single_capture_v1/actual_cached_replay_v1.json');assert single_replay['exit_code']==0 and single_replay['before']==single_replay['after'] and single_replay['all_receipt_cache_bytes_preserved'];bind(BASE/'single_capture_v1/actual_cached_replay_v1.json')
    for model in ['Qwen','Llama']:
        for phase,ops in [('PILOT',1024),('TEST',8192)]:
            q=Path(__file__).resolve().parent/f'{model}_{phase}_raw_v1/audit_summary.json';v=read(q);assert v['audit_complete'] and v['unique_operations_audited']==ops and v['new_model_fit_bootstrap_MC_calls']==0;bind(q)
    OUT.mkdir(exist_ok=True);artifact_hash=sha(TARGET)
    evidence=dict(accounting_sha256=artifact_hash,stage_checks=checks,totals=dict(totals),B_original_preserved_prefix=dict(kinds),B_reference_separate_four_F=True,A_original501_plus_recovery35339=True,single_capture_not_recounted_in_Afit=True,language_model_loads_basis='14closed acquisition groups plus two documented fail/resume additional loads; zero-load cached replays excluded, TC-only safetensors reference load excluded.',evidence_files_sha256=hashes,no_raw_rehash_model_or_MC=True)
    (OUT/'audit.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    review=dict(schema_version=1,artifact='analysis/AB_confirmatory_execution_20261101/accounting_closed_campaign_20261102_v1.json',artifact_sha256=artifact_hash,reviewer_id='/root/sol_parallel_acceptance',independent=True,verdict='approved',topics_checked=['design','implementation','data','cost','claims'],findings=[],totals_verified=dict(totals),evidence='sol_parallel_acceptance/campaign_accounting_v1/audit.json',limitations='Mechanical accounting review of the14closed current campaign stage groups, not a new scientific inference or all historical machine/process activity. Small frozen contracts/costs, evidence hashes and prior independently accepted closure/ledger/replay proofs were reused; no full native raw-data rehash, model/refit/bootstrap/MC or canonical CLI replay.239803forward is heterogeneous logical accounting, not239803full-transformer passes or FLOPs/time; only13342are full-transformer forwards.1740backward separate; nativeJVP separate from gradient backprop. TC_reference combinesTC applications and small reference diagnostics, not25952reference tests.16LLMloads counts one per acquisition group plus preserved A_TEST/B_FITfail-resume extras; TC-only load and zero-load cache replay excluded. System sleep/walltime separate. Accountingv1 bytes and historical failures remain unchanged; pending review field is superseded by this external hash-bound receipt.')
    (BASE/'accounting_closed_campaign_review_sol_v1.json').write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(approved_artifact_sha256=artifact_hash,totals=dict(totals),evidence_files=len(hashes))))
if __name__=='__main__':main()
