# Offline implementation handoff

2026-11-01. New source only; existing workers, fitting code, calibrations and cached measurements were not edited. No pretrained call and no large calibration/selection campaign was launched here. Scientific results remain unknown. The14-test receipt is correctness evidence, not a statistical eligibility result.

## Implemented entrypoints

Run from `C:/Users/rafal/interpretability-lab`, interpreter `C:/Users/rafal/miniconda3/python.exe -X utf8`. These are the literal module/argument vectors for independently reviewed research_checks contracts. They are NOT a waiver of launch review. Root/Sol creates the stage contract/snapshot, then runs `python -m research_checks launch --snapshot ACTUAL --review ACTUAL` as required by repository policy.

| Task | Module and arguments |
|---|---|
| Cheap correctness checks | `-m ab_confirmatory_20261101.selector_tests_v3` |
| B joint12 interval coverage | `-m ab_confirmatory_20261101.eligibility_calibration_v3 precision --out analysis/AB_confirmatory_execution_20261101/remaining_statistics_v3/precision_coverage_run_v1` |
| Existing-law production family bridge | `-m ab_confirmatory_20261101.eligibility_calibration_v3 family --manifest PATH_TO_FROZEN_FAMILY_MANIFEST --out analysis/AB_confirmatory_execution_20261101/remaining_statistics_v3/family_bridge_run_v1` |
|16-FIT crossed interval calibration | `-m ab_confirmatory_20261101.stability_validation_v3 --out analysis/AB_confirmatory_execution_20261101/remaining_statistics_v3/stability_run_v1` |
| Select N from PILOT | `-m ab_confirmatory_20261101.selector_v3 --manifest PATH_TO_FROZEN_PILOT_MANIFEST --out PATH_TO_NEW_SELECTION_OUTPUT` |
| Final primary analysis | `-m ab_confirmatory_20261101.analysis_ab_v3 --manifest PATH_TO_FROZEN_ANALYSIS_MANIFEST --out PATH_TO_IMMUTABLE_RESULT_JSON` |

Resume the SAME command/output only after process/liveness checks. Changed source/runtime/input/spec identities reject old receipts; do not delete receipts to bypass that rejection. A prospective new version must retain the old evidence and explicitly decide reuse. Different stability `--case INDEX` values can address the18 fixed cases separately; do not run the same case concurrently. Completion aggregation reuses all existing case outputs.

## Input contracts

Every input manifest is plain JSON with `files` mapping manifest-relative or absolute path to SHA256. Every actual raw input, model/fit/corpus identity and array-construction source used upstream must appear in the stage's reviewed input set. The offline module verifies all manifest hashes before computation; it cannot infer raw files omitted by an upstream author.

Final analysis manifest fields: `study` (`A` or `B`), `arrays` (manifested NPZ path), `files`. A NPZ arrays `readout_errors` and `vector_errors` have shape `[block,5frames,4conditions,5arms]`. Frames=T0,T2,T5,T6,T7; conditions=s0q0,s0q1,s1q0,s1q1; arms=P,U0,Uctrl,U2,U5. Values are squared errors. B `energies` has shape `[block,2operators,2main_templates,2sides,6doses,3energies]`; operators=full/projected, templates=so/when, doses=.05,.1,.25,.5,1,2; energies=native finite-margin signal squared,TC finite-margin error squared,Taylor finite-margin error squared. No vector-energy substitution is allowed.

Selector manifest fields: `split:"PILOT"`, `arrays`, `v_target:240107.0870612265`, `files`, `eligibility`. NPZ `A_power` is32x4 in order A1L,A2V,A2L,A3L; `B_power` is32x8 in order S_f1,E_TC_f1,E_Taylor_f1,S_p1,E_TC_p1,E_Taylor_p1,S_fsmall,E_TC_fsmall; `B_precision` is32x2x2x2 with axes block,operator,so/when,error/native_signal. These arrays are produced by `a_components`/`b_components`; never use per-record ratios. The frozen FIT_r0 receipt and source of the V target belong in the reviewed manifest.

Eligibility is indexed `eligibility["A" or "B"]["128" or "256"]`. Each entry has `eligible` bool and paths `evidence`, `snapshot`, `review`. The evidence is an immutable research_checks.persistence receipt whose payload has `study`, `n`, `eligible`, `requirements`, `requirement_receipts`. Requirements are `family_null`, `production_bridge`, `missing_degenerate` and, for B, `precision_coverage`. Each requirement path identifies a separate immutable payload with `passed` bool. All evidence paths and the canonical snapshot/review are in `files`; the canonical review must track the eligibility and requirement receipts. Flags must match the actual receipt values. The family_null receipt additionally has `case_definition` and ordered `case_receipts`, pointing to the ORIGINAL v2 cases.json and every original case for that study/N. Any historical failure forces family_null false; no summary can override it. Root emits/reviews these synthesis receipts from completed calibrations, including exact linkage to the production bridge/coverage summaries. Missing calibration is not eligibility.

Family bridge manifest has `cases` (original immutable180-case definitions), `receipts` (ordered180 original immutable case result paths), and `files` including each. The bridge requires the exact existing case universe/order,2000repetitions,1999draws and recomputes original all-case CP upper from stored counts to verify the saved bound. No bridge begins before all original case receipts exist. Failed study/N groups are excluded as a whole. New independent seeds generate NEW bridge datasets under the old laws; original datasets/results are not rerun or falsely paired.

## Worker-facing offline APIs

`a_records(expected_documents, result_payloads_by_document_id, cohort="r0")` accepts actual worker_a result payloads. Full prescribed document cells must be listed; duplicate/omitted expected cells fail. Missing result records remain NaN in the affected block components, yielding inconclusive affected hypotheses with p=1 in the fixed three-slot family. No block deletion. It returns components and missing-ID/block-order metadata. `a_descriptive_records` additionally reports all30 frame/arm cells includingzero, P, allU, signals and harm frequency; all intervals descriptive pointwise99%.

`b_components(energies)` returns the eight power energies and c1 precision tensor. `b_descriptives(native_margin,predictions)` accepts `[block,2operators,3templates,2sides,6doses]` finite-margin changes; template3 is fixed transfer. Predictions is a mapping including TC/frozen-mask/Taylor/cellmean/ridge as acquired; zero is added exactly. Output retains every method/operator/dose and separate so/when/transfer/main-mixture RMS. Main mixture pools energies before ratios/square roots. Missing/zero cells remain explicit, without epsilon or complete-case replacement.

`endpoint_decomposition(N0,N1,TC0,TC1)` consumes one fixed template/operator/dose `[block,side2,vector]` cell, forms float64 endpoint errors, exact energy/cross/bias/centered-covariance identities and logs float32-vs-float64 subtraction discrepancy. Its confidence intervals resample independent blocks after averaging sides. `linear_readout_diagnostics(g,D_native,D_TC,finite_native_margin)` distinguishes TC-linear vs native-linear and TC-linear vs native-finite targets. These functions do not make finite nonlinear readout decomposition claims or add primary support slots.

`stability_report(components,v_target)` accepts all16 FITs x128/256 shared TEST blocks x4components, uses the same crossed bootstrap, reports per-FIT contrasts, descriptive between-FIT SD, pointwise99%mean intervals and physical width goals. Missing cells mark population summary incomplete. No joint coverage/rare-reversal/future-fit safety claim. Primaryr0 remains separate.

## Cost and remaining gates

Eight single synthetic timing probes are preserved in timing_v1; never regenerate them merely for review.20k kernels took A .455/.809s, B power .943/1.833s, B precision .359/.702s and stability .956/1.090s atN128/256. Probes predate addition of the runtime fingerprint and purely descriptive helper functions; tested bootstrap kernels are unchanged. They are timing evidence only, not coverage/power observations.

Linear extrapolation excluding JSON/hashing/I/O and resource contention: selector all12cases5.38h; crossed18cases5.63h; Bprecision8cases1.30h. Family bridge worst-case180eligiblecases54.3h; excluded failed groups reduce that. Per group: A12836cases4.55h,A25636cases8.09h,B12854cases14.15h,B25654cases27.50h. Each selector case uses37,991,000 bootstrap draws; each coverage case21,999,000; each family bridge case20,000,000. Prefix reuse is included. These are planning estimates, not deadlines or reasons to relax gates. Raw datasets/receipts consume multiple GB and many files; no hidden repeated model cost.

Before PILOT: finish existing null calibration, execute approved production/coverage qualification, derive reviewed eligibility receipts, review all selector/worker input construction, freeze targets and rules. Before added FIT: crossed calibration must pass and the extra FIT contract/cost must be independently approved. Before TEST: selector must finish, N/fits/forecasts freeze and actual TEST contract receive its own review. No statistical qualification result exists yet from these new modules. Negative or infeasible outcomes are retained and require no retry-until-pass.
