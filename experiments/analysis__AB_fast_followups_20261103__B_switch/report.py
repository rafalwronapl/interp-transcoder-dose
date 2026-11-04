"""Report completed cache-only run; added analytic triangle-inequality audit."""
import json,itertools
from pathlib import Path
import numpy as np
from analyze import HERE,ROOT,OLD,read,unwrap,sha,save

def main():
    r=read(HERE/'FIT_FEASIBILITY.json');selection=unwrap(OLD/'run_v3/FEATURE_SELECTION.json')
    assert selection['top']==r['top']
    # Post-run support audit, no new optimization/selection: for any disjoint32
    # mean(||sum_j s_ij d_j||) <= sum_j mean(|s_ij|)||d_j|| <= sum32 largest scores.
    scores=np.asarray(selection['scores']);available=np.setdiff1d(np.arange(len(scores)),r['top'])
    bound=float(np.sort(scores[available])[-32:].sum());lower=max(0,r['top_distribution']['mean_norm']-bound)
    certificate=dict(type='Post-run analytic norm-support audit; no selection change',
        proof='For every disjoint size32 group G, E||sum(j in G) s_ij d_j|| <= sum(j in G) E|s_ij| ||d_j|| <= sum32 largest alternative historical FIT scores. W1(norm_top,norm_G)>=abs(mean_top-mean_G).',
        max_mean_norm_upper_bound=bound,W1_norm_lower_bound=lower,FIT_norm_band=r['tolerance_count_norm'][1],
        proves_no_disjoint32_can_meet_norm_band=bool(lower>r['tolerance_count_norm'][1]),
        historical_selection_sha256=sha(OLD/'run_v3/FEATURE_SELECTION.json'))
    save(HERE/'ANALYTIC_NORM_BOUND.json',certificate)
    overlap=[[len(set(a['features'])&set(b['features'])) for b in r['groups']] for a in r['groups']]
    lines=['B-FIT — completed cache-only feasibility analysis, 2026-11-03',
        '', 'Independent pre-run review APPROVED: review/pre_run_review_v1.json, snapshot fac5f4f7df97ded249121c7d280cd33202915226036d4ac2db0398cdb899b47a.',
        'Canonical research_checks launcher completed exit0. Completion independent review: PENDING; see later completion_review receipt.',
        '', 'Scope: historical Gemma270M L15, FIT64 independent blocks,128 recipient documents, so frame, full operator dose1 only. Historical top32 preserved; no TEST readouts used for group selection.',
        'Exact selective numeric tensor access: threshold[16384],w_dec[16384,640] from existing local params.safetensors; no encoder tensor/native checkpoint loaded; no native or TC class instantiated.',
        'Actual new native model loads0; TC model loads0; native forwards0; TC forwards0. Cache-only array algebra. Input inventory and all790inputs bound by input_manifest.json; exact params SHA ca3a2fc2c75ffa1c4305497ee1aba381bdedff90a49aeda5db82083e80e194ca.',
        '', 'Observed results:',f"Top32 mean actual switches/context {r['mean_top_count']:.6f}; mean summed contribution norm {r['top_distribution']['mean_norm']:.6f}.",
        f"Alternative features switching at least once: {len(r['alternative_switching_features'])}; all alternatives combined mean count {r['mean_all_alternatives_count']:.6f}. Top count exceeds ALL alternatives in{r['contexts_top_count_exceeds_all_alternatives']}/128contexts. These facts alone do not establish distribution-wide impossibility.",
        f"FIT-derived descriptive W1 bands: count {r['tolerance_count_norm'][0]:.6f}, norm {r['tolerance_count_norm'][1]:.6f}. Whole-block split variability, not equivalence-test thresholds.",
        'Seed | mean count | mean norm | W1count | W1norm | within both bands']
    for g in r['groups']:
        lines.append(f"{g['seed']} | {g['distribution']['mean_count']:.6f} | {g['distribution']['mean_norm']:.6f} | {g['W1_count_norm'][0]:.6f} | {g['W1_count_norm'][1]:.6f} | {g['within_FIT_heterogeneity_tolerance']}")
    lines.extend([f"Unique candidate groups: {len({tuple(g['features']) for g in r['groups']})}/5; pairwise overlap range {min(overlap[i][j] for i in range(5) for j in range(i))}..{max(overlap[i][j] for i in range(5) for j in range(i))}/32. Seeds are not independent biological/statistical samples.",
        '', 'Post-run analytical support audit (no retuning):',
        f"For ANY disjoint size32 group, triangle inequality gives mean norm <= {bound:.6f}; therefore W1norm from top32 >= {lower:.6f}. This {'exceeds' if lower>r['tolerance_count_norm'][1] else 'does not exceed'} the fixed descriptive FIT norm band {r['tolerance_count_norm'][1]:.6f}.",
        f"Norm-band infeasibility certificate: {certificate['proves_no_disjoint32_can_meet_norm_band']}. See ANALYTIC_NORM_BOUND.json for exact bound/proof. The frozen optimizer itself is a bounded heuristic and does not establish global feasibility/infeasibility.",
        '', 'Interpretation and limits:',
        'All five candidate groups fail joint count/norm matching. Preserve negative outcome; do not call these strength-matched controls. Candidate groups are frozen in FROZEN_GROUPS.json only for audit, not approved B-MASK execution.',
        'This is a restricted support/feasibility result, not evidence of unique native mechanisms, exceptional semantic importance, readout usefulness, or general model understanding. It adds no new native-readout/TC accuracy result. Original top32 was deliberately selected by FIT contribution strength, which limits available disjoint alternatives.',
        'No fresh population inference; no TEST balancing guarantee. The bands are descriptive and this FIT was already used in historical top32 selection. Reported analytical bound is expressly post-run.',
        '', 'Missing measured cache and exact minimum additional FIT work:',
        'Observed so/full/c1 requires0newmodelcalls and is complete. Missing current-document conditions:128full/.05 +128projected/.05 +128projected/1 endpoints=384 additional TC input encodings if directly evaluated,0nativeforwards; all128baseencodings can be reused. No such stage launched. A separately reviewed pure linear encoder-cache derivation could be considered, but cannot silently substitute float rounding/threshold conventions.',
        'Additional when/transfer FIT frames are absent from this source_index FIT. For the same64blocks and2sides,2frames would need256newnativecaptures if no compatible capture exists elsewhere, plus TC encodings (at most256base+1024endpoints for4conditions before donor/end deduplication). Availability elsewhere was not exhaustively inventoried; these are conditional operation counts, not claims of required new calls. No time estimate fabricated.',
        '', 'Small follow-up design, proposed only:',
        'Before B-MASK, choose an explicit response to failed balance: preserve top32 and collect independent FIT condition support; or preregister a different question allowing weaker/overlapping/variable-size controls, reporting that changed estimand. Do not relax bands or enlarge controls just to produce a positive result within this analysis.',
        'If valid controls become available, freeze algorithm/tolerances/groups, then exact ONLY/EXCEPT suffixes on historical TEST are posthoc. Minimal scope from plan: so/full/c1. The historical32blocks provide64so-frame recipient documents. Five controls and two arms per group imply at most640newnative suffix evaluations before exact target aliases/deduplication; existing top32/ON/OFF/native results reused. Prefix cache validity and unique target count must be checked in the separate B-MASK plan, reviewed and canonically launched. No B-MASK calls authorized by this report.',
        '', 'Evidence: INVENTORY.json; input_manifest.json; fixtures.json; FIT_FEASIBILITY.json (all per-context distributions); FROZEN_GROUPS.json; ANALYTIC_NORM_BOUND.json; review/pre_run_review_v1.json; pre_run_snapshot.json; launch.log/launch.err. Historical producer worker_v3.py, geometry.py, transcoder.py bound in manifest.',
        'Literature boundary: this specific strength-support audit adds no novelty claim; use established B13 sources and plans/DALSZE_EKSPERYMENTY_A_B_20261103.txt. Planned follow-ups are not findings.'])
    data=('\n'.join(lines)+'\n').encode('utf-8');p=HERE/'REPORT.txt'
    if p.exists():assert p.read_bytes()==data
    else:p.write_bytes(data)
    print(json.dumps(certificate))

if __name__=='__main__':main()
