# B reproducibility commands and bundle requirements

These commands are recorded interfaces, not evidence of a new run. This task executed only the metadata inventory and saved-source checksum checker. It did not execute a model, retokenize, load weights, run calibration or regenerate statistics. The first final B report was still pending at inventory time; do not run a replay before that original report is closed and independently accepted.

## 1. Compact bundle: inspect saved metadata without weights

Preserve repository-relative paths. Include this folder and every file listed in `artifact_reproducibility_table.json` → `source_files_sha256` (46small source/config/corpus/token/contract/review files in the current inventory). The tokenizer/model weight files need not be supplied; their recorded hashes remain in the table. From the bundle root:

```powershell
python -X utf8=1 papers/B_release_metadata_20261102/verify_saved_B_artifacts.py metadata --root .
```

This standard-library checker hashes only the listed small files, refuses weight/large files, and prints explicit gaps. It is not a canonical reconstruction of omitted native calls, nor a claim that all historical identities/licenses are certified. The actual lab metadata check passed46/46 with no missing files, no weights and no statistics.

After the actual final result SHA has been added from closed evidence, include the saved `analysis/AB_confirmatory_execution_20261101/B_descriptive_analysis_v9/result.json` and run:

```powershell
python -X utf8=1 papers/B_release_metadata_20261102/verify_saved_B_artifacts.py saved-report --root .
```

This verifies the saved result file and immutable payload checksum and prints its descriptive contrasts. It performs no bootstrap/model calls. Until the result exists and its SHA is bound in the release table, this command deliberately exits2; it never generates a missing result. Final statistical acceptance remains the original independent result/completion review.

## 2. Optional offline numerical reproduction, no weights

This is a statistical rerun on an isolated copy, **not** a cache-only inspection. It was not executed by the metadata task. It needs exact frozen Python source/transitive imports and the recorded NumPy/SciPy/Python runtime, plus:

- `B_descriptive_TEST_v8/config.json` and `corpus.json`;
- `B_descriptive_TEST_v8/run/stage_completed.json` with the original result hash map;
- all18432closed `run/results/<document>/{full,projected}_{0..5}.json` records (1536documents ×2operators ×6doses);
- the frozen v6 candidate/calibration identity source and its imported metadata helpers; preserve package/repository layout;
- accepted qualification/failure/amendment provenance and original model/tokenizer identities for interpretation.

The analyzer does not load model/TC weights or read the full capture cache. It reads the closed result records, checks their membership, and recomputes the prospectively frozen descriptive report and1999-draw TCc1joint12 intervals. Exact module interface:

```powershell
python -X utf8=1 -m ab_confirmatory_20261101.analyze_b_descriptive_v8 --packet analysis/AB_confirmatory_execution_20261101/B_descriptive_TEST_v8 --out reproduced/B_descriptive_v8_result.json
```

Use a NEW output path. This command is for an isolated reproduction after the original result is published. It is not authorization to bypass the laboratory's canonical launch/review policy. The original governed execution uses the separately reviewed0F/0B contract and runtime. Compact bundles omit weights/full raw caches, so the original canonical all-input admission will correctly fail if its required files are absent. Do not weaken that gate to make a compact bundle look complete.

Relocation changes absolute source paths in the new request identity. Frozen mathematics/seeds and input bytes can be reproduced, but byte-identical cached request reuse across arbitrary locations or third-party binaries is not promised. Saved-output verification in tier1 avoids this issue entirely.

## 3. Governed original final-analysis launch (full evidence tree)

After accepted TEST closure, the exact prepared builder interface is:

```powershell
python -X utf8=1 -m ab_confirmatory_20261101.prepare_b_descriptive_analysis_v9 --packet analysis/AB_confirmatory_execution_20261101/B_descriptive_TEST_v8 --completion-snapshot analysis/AB_confirmatory_execution_20261101/B_descriptive_TEST_v8/completion_snapshot_v1.json --completion-review analysis/AB_confirmatory_execution_20261101/B_descriptive_TEST_v8/completion_review_astra_v1.json --out analysis/AB_confirmatory_execution_20261101/B_descriptive_analysis_v9
```

The authorized executor already started this builder once; do not run it again over the same output or while its verification is active. Then the executor freezes the emitted contract and obtains actual independent pre-run review before launching the unchanged analyzer through `concurrency_runtime_v2` with `sol_parallel_acceptance/offline_policy_v3/{migration_policy.json,snapshot_v1.json,review_astra_v1.json}`. Exact template:

```powershell
python -X utf8=1 -m concurrency_runtime_v2 --snapshot analysis/AB_confirmatory_execution_20261101/B_descriptive_analysis_v9/pre_run_snapshot_v1.json --review analysis/AB_confirmatory_execution_20261101/B_descriptive_analysis_v9/pre_run_review_astra_v1.json --policy analysis/AB_confirmatory_execution_20261101/sol_parallel_acceptance/offline_policy_v3/migration_policy.json --policy-snapshot analysis/AB_confirmatory_execution_20261101/sol_parallel_acceptance/offline_policy_v3/snapshot_v1.json --policy-review analysis/AB_confirmatory_execution_20261101/sol_parallel_acceptance/offline_policy_v3/review_astra_v1.json
```

Do not describe these pending files as completed/approved until the actual executor/reviewer receipts exist. There are no new model calls in this final-analysis packet.

## 4. Historical native stage entrypoints — traceability only

All measurements below are already acquired and independently accepted. These are exact contract entrypoints, **not instructions to repeat models**. Fresh execution requires the original pinned model/TC weights, complete manifests/runtime, a new permitted output/contract, canonical pre-run verification and independent review; changing output/config changes identity. The compact evidence bundle intentionally ships no weights.

```text
# Accepted FIT continuation, retaining original64logical operations and separate4unfused referenceF
python -X utf8=1 -m ab_confirmatory_20261101.worker_b_serialization_recovery --config analysis/AB_confirmatory_execution_20261101/B_fit_primary_v1/config.json --amendment analysis/AB_confirmatory_execution_20261101/B_fit_reference_recovery_v2/amendment.json
# Technical exact-tail qualification
python -X utf8=1 -m ab_confirmatory_20261101.worker_b_evaluate --config analysis/AB_confirmatory_execution_20261101/B_tail_qualification_v1/config.json
# Early acquisition-only PILOT
python -X utf8=1 -m ab_confirmatory_20261101.worker_b_pilot_only_v7 --config analysis/AB_confirmatory_execution_20261101/B_pilot_early_v7/config.json
# Fixed256 descriptive TEST
python -X utf8=1 -m ab_confirmatory_20261101.worker_b_descriptive_v8 --config analysis/AB_confirmatory_execution_20261101/B_descriptive_TEST_v8/config.json
```

The synthetic qualification entrypoint is `ab_confirmatory_20261101.b_precision_calibration_v6 --out analysis/AB_confirmatory_execution_20261101/B_precision_v6_calibration_v1/run`; it would rerun/read calibration and is not a compact saved-result inspection. Do not invoke it merely to review the release.

## 5. Weight retrieval and licensing boundary

The table pins native repository`google/gemma-3-270m`, recorded revision`9b0cfec892e2bc2afd938c98eabe4e4a7b1e0ca1`, and public TC repository`google/gemma-scope-2-270m-pt`, revision`b218cd5d69dc2fa71cff448b68d625e6c9702d49`, artifact`transcoder/layer_15_width_16k_l0_medium`. Retrieve only under the applicable repository terms and independently compare recorded fileSHA values. This task made no network request/download. The TC card records CC-BY4.0; base-model terms, local code license and dataset notices remain explicit release gaps. The table does not grant redistribution permission or replace the applicable terms.
