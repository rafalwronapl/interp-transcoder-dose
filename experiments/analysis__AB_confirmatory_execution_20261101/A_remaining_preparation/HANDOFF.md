# A remaining execution preparation

2026-11-01. New modules only; no frozen worker/source/cache was edited and no pretrained inference ran. Existing r0 FIT and qualification are preserved. Articles are deferred until the experiments are finished.

## Concrete packets

| Packet | New full forwards | New exact local suffix calls | Backward | Admission |
|---|---:|---:|---:|---|
| PILOT_draft_v1:32blocks/640documents |640|3840|0|false|
| TEST128_draft_v1:128blocks/2560documents |2560|15360|0|false|
| TEST256_draft_v1:256blocks/5120documents |5120|30720|0|false|
| FIT15_draft_v1:r1–r15,48FITblocks each |6720|0|0|false|
| Future stability evaluation on shared TEST128 |0|192000|0|requires actual completed TEST and15FIT|
| Future stability evaluation on shared TEST256 |0|384000|0|requires actual completed TEST and15FIT|

Every materialized packet contains literal corpus/tokens/config, operation list, cost/readiness receipts, source/model manifests and an executable research_checks contract. Missing scientific admission is an actual false gate, not prose-only caution. Direct worker invocation also checks prerequisites before importing/loading the model. Draft packets must not be edited into readiness: rebuild at a new path with actual reviewed inputs.

Primary and future stability use one unchanged native model implementation, last layer/final position, the same finite suffix and fixed recipient residual. Root approved reuse of all five r0qualification controls, with no repeated controls or TEST-dependent qualification gate. Existing r0 completion review must first be adopted/reviewed under current research_checks infrastructure: the zero-call-launcher infrastructure amendment made the old canonical snapshot stale. No model or qualification measurement is repeated for that adoption.

## Executable preparation commands

From laboratory root, use `C:/Users/rafal/miniconda3/python.exe -X utf8` followed by:

```
-m ab_confirmatory_20261101.prepare_a_v2 --kind PILOT --out NEW_PACKET --authorization-manifest ACTUAL_A_PILOT_AUTHORIZATION --qualification-manifest CURRENT_R0_ADOPTION_JSON --test-evidence analysis/AB_confirmatory_execution_20261101/A_remaining_preparation/worker_tests_v1.json
-m ab_confirmatory_20261101.prepare_a_v2 --kind TEST --n 128 --out NEW_PACKET --authorization-manifest ACTUAL_A_TEST_AUTHORIZATION --qualification-manifest CURRENT_R0_ADOPTION_JSON --test-evidence analysis/AB_confirmatory_execution_20261101/A_remaining_preparation/worker_tests_v1.json
-m ab_confirmatory_20261101.prepare_a_v2 --kind ADDITIONAL_FIT --out NEW_PACKET --admission ACTUAL_STABILITY_COVERAGE_ADMISSION --qualification-manifest CURRENT_R0_ADOPTION_JSON --test-evidence analysis/AB_confirmatory_execution_20261101/A_remaining_preparation/worker_tests_v1.json
-m ab_confirmatory_20261101.prepare_a_v2 --kind STABILITY --n 128 --out NEW_PACKET --source-test ACTUAL_PRIMARY_TEST_RUN_DIRECTORY --extra-fit ACTUAL_15FIT_RUN_DIRECTORY --admission ACTUAL_COMPLETION_ADMISSIONS --qualification-manifest CURRENT_R0_ADOPTION_JSON --test-evidence analysis/AB_confirmatory_execution_20261101/A_remaining_preparation/worker_tests_v1.json
```

Use the independently selected128 or256, never a convenient substitute. `CURRENT_R0_ADOPTION_JSON` contains ROOT-relative `config`, `snapshot`, `review`; config remains original r0 FIT config, while snapshot/review are a fresh current-infrastructure acceptance of unchanged r0 evidence. The builder validates actual prerequisites/qualification before emitting a ready packet. New model-stage snapshot and independent pre-run review then precede the ordinary `research_checks launch --snapshot ... --review ...` command. Maintenance approval alone does not authorize these runs.

PILOT/TEST authorization schema is root-owned campaign_authorization.py. It validates exact corpus prefix, both candidate eligibility receipts, actual scalar/family/precision requirements, and canonical selector completion/selectedN for TEST. It uses eligibility_paths_v5.py to normalize canonical-review paths without modifying frozen numerical v4 code. No fictitious generic eligibility bool is substituted.

Additional FIT admission JSON contains `coverage:{evidence,snapshot,review}`, with ROOT-relative paths. Evidence is the immutable completed stability_validation_v4 summary whose `/payload/result/all_passed` is true, bound in its canonical completion review. This gate precedes extra FIT acquisition.

Stability admission JSON contains `test_completion` and `extra_fit_completion`, each with ROOT-relative evidence/snapshot/review paths. Evidence is the corresponding actual `stage_completed.json`; its model identity must match, and canonical reviews must bind it. The exact same TEST run must be configured as the reuse source. All15 frozen FIT files must exist. The future packet cannot be materialized from placeholders.

## Reuse implementation and tests

worker_a_v2 injects a scoped Runtime adapter into the unchanged worker_a, restoring its original binding in `finally`. Only explicitly declared natural capture/native-suffix operations can be imported. Preflight verifies every sealed source-stage artifact and source identity. Each imported request must match model, exact document/tokens, intervention R/M/arm and readout; source code identity is separately retained. Imported operations are absent from new call schedule and receive immutable provenance receipts. New predictions use the unchanged Runtime and are charged once. Neither another FIT's P/U prediction nor a source request with changed semantics can be imported.

The actual randomGemma integration passed3tests: FIT→primaryTEST→two synthetic stability cohorts,40imported operations,200newlocal suffixes,0full forwards during stability (Native.forward deliberately raises), exact agreement with same-fit reference, source bytes preserved, replay0newloads, corrupt source rejected before load, and mismatched semantics rejected. Real-model qualification/admission are explicitly mocked in this random test; it does not establish scientific admission. Tested source copies and worker_tests_v1.json preserve that run. The only subsequent worker amendment adds eligibility_paths_v5.py to dependency identity; numerical/runtime logic is unchanged. Do not repeat the random inference merely for review.

Two separate inexpensive synthetic tests exercise16FIT×3sharedblocks immutable records→NPZ, byte-preserving assembly replay, corrupted arrays, append-after-closure rejection and consumed-attempt no-retry. Every result actually read by assembly must belong to the verified stage closure. All input receipts/source identities are bound. These are synthetic correctness checks, not model results or calibration.

## Analysis assembly

```
-m ab_confirmatory_20261101.assemble_a_v2 --primary-packet ACTUAL_PILOT_OR_PRIMARY_TEST_PACKET --out NEW_ASSEMBLY_FOLDER
-m ab_confirmatory_20261101.assemble_a_v2 --primary-packet ACTUAL_PRIMARY_TEST_PACKET --stability-packet ACTUAL_STABILITY_PACKET --out NEW_ASSEMBLY_FOLDER
```

Outputs contain readout/vector error tensors, A_power block components, explicit block IDs and, when all cohorts are present, `[16,N,4]` stability_components. The manifest binds all sealed raw receipts and assembly/statistical source/runtime identities. No model loading occurs. Missing/incomplete stages are not silently complete-case filtered. Primary analysis uses analysis_ab_v4 with1999draws; descriptive stability uses its separate stability_report API, never replacing r0 hypotheses.

The A-only PILOT assembler deliberately does not invent B arrays. Root is adding independent-study selection to the v5 selector execution adapter while preserving frozen MC bounds/seed indices. Use that approved shared entrypoint once available.

## Remaining exact gates and cost limits

1. Fresh current-infrastructure adoption/review of unchanged r0 qualification/FIT evidence.
2. Actual root campaign-authorization receipts and independent stage review for PILOT/TEST; selectedN before TEST.
3. Accepted crossed calibration plus its review before additional15FIT; completed reviewed TEST/15FIT before stability reuse.
4. Final observed outputs, offline analysis and completion review remain unmeasured; no positive scientific result is claimed.

The large stability suffix count is explicit. Existing r0 FIT JSON is28,686,206bytes;15additional dense fits can be hundreds ofMB on disk. Full repeated request vectors in immutable suffix caches can make stability output multipleGB. This is a planning limitation, not an unapproved stopping threshold. Exact call counts above are hard schedule/accounting bounds; measured time/disk/RAM still require reporting. No automatic retry reserve or unseen extra model call is included.
