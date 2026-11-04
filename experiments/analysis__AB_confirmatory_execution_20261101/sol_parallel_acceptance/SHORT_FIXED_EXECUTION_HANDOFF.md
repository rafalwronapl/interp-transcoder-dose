# Short fixed256 execution handoff — 2026-11-01

Order authorized by the user: finish actual B descriptive TEST, then Qwen PILOT → TEST, then Llama PILOT → TEST. Executor owns all launches, builders and official snapshots. No parallel native launches. Articles remain deferred.

Both actual FIT stages are independently accepted: Qwen completion `1a6cd4a519e0292b979840a05aaea78b6f05023d0eae68d71bc5837482a8b92a`; Llama completion `bae3011cc529440d2f5fab6e9a72b1b7c98da0f4eba7598f20f0f5eb5ed9a682`. Each authoritative receipt is `FIT_ready_v1/completion_review_sol_v1.json`. Qwen evidence is `FIT_ready_v1/fit_completion_summary_v1.json`; Llama evidence is `FIT_ready_v1/run/fit_acceptance_summary.json`.

The actual PILOT packets are `analysis/A_short_replication_{qwen,llama}_20261101/PILOT_ready_v1`: 32 blocks, 256 documents, 1024 forward / 0 backward each. Executor added recursive local import closure to contracts only, preserving root v3 helper/config/corpus/schedule bytes. Astra independently checked actual admission and original schedules for both. Official snapshots/reviews are still authoritative; this handoff does not supply approval.

## Future TEST construction

Do not build TEST until the respective PILOT is durably closed and independently accepted. Run the following PowerShell commands from the repository root, substituting only MODEL and the actual PILOT completion snapshot/review filenames if versioned. TEST output must be new and absent.

```powershell
$shortModel = 'qwen' # later 'llama', after Qwen TEST finishes
$shortRoot = "analysis/A_short_replication_${shortModel}_20261101"
$fitEvidence = if ($shortModel -eq 'qwen') { "$shortRoot/FIT_ready_v1/fit_completion_summary_v1.json" } else { "$shortRoot/FIT_ready_v1/run/fit_acceptance_summary.json" }
python -X utf8=1 -m prepare_short_fixed_v3 --model $shortModel --phase TEST --out "$shortRoot/TEST_fixed256_v3" --base-workflow "$shortRoot/PILOT_ready_v1_authorization/manifest.json" --eligibility analysis/AB_confirmatory_execution_20261101/eligibility_synthesis_v5/A_actual_v1/eligibility_manifest.json --fit-evidence $fitEvidence --fit-snapshot "$shortRoot/FIT_ready_v1/completion_snapshot_v1.json" --fit-review "$shortRoot/FIT_ready_v1/completion_review_sol_v1.json" --pilot-evidence "$shortRoot/PILOT_ready_v1/run/stage_completed.json" --pilot-snapshot "$shortRoot/PILOT_ready_v1/completion_snapshot_v1.json" --pilot-review "$shortRoot/PILOT_ready_v1/completion_review_astra_v1.json"
```

Before freezing, executor applies the same reviewed recursive AST local-import closure metadata procedure used in the actual PILOT packets. This includes `recovery_a_status_v1.py` and its transitive local imports. Preserve builder-emitted contract backup and addition receipt; do not edit source/config/corpus/operations. Confirm exact original TEST prefix256 blocks / 2048 documents / 8192 forward / 0 backward. Freeze canonical pre-run snapshot, obtain independent exact-snapshot review, and launch via the approved canonical runtime. No new power selector, Monte Carlo selection or sample extension.

Reusable additive CLI (focused review required before using; never apply to already frozen actual PILOTs):

```powershell
python -X utf8=1 analysis/AB_confirmatory_execution_20261101/sol_parallel_acceptance/close_local_imports.py --contract "$shortRoot/TEST_fixed256_v3/contract.json"
```

The utility refuses snapshot-bearing directories and existing closure receipts, writes the original contract backup, and adds only local static Python dependencies plus their exact SHA256 receipt. The CLI imports and reuses the exact executor PILOT closure function without running its hardcoded main. Read-only closure over both original PILOT contracts reproduced 37 bound local Python files each, with no packet writes (tool7977cc). Dynamic worker modules are already builder tracked. Apply the same CLI to the new final-analysis contract before its snapshot.

`short_fixed_workflow_v3.py` and `prepare_short_fixed_v3.py` are frozen by accepted Llama FIT. Their TEST admission validates actual own FIT and accepted disjoint PILOT. It handles Qwen `phase` + model file SHA and Llama `scope` + model-dictionary digest. `test_short_future_test_v3.py` passed five isolated gate fixtures (0.305 s): both real format variants accepted; wrong N, wrong model and TEST substituted for PILOT rejected. Mocks stand in only for canonical prerequisites; these fixtures do not replace actual stage review. No models, fitting, bootstrap or MC calls occurred.

## Offline assembly and final analysis

After actual TEST acquisition closes, assemble immutable raw results using unchanged model-specific assembly:

```powershell
# Qwen
python -X utf8=1 -m a_short_qwen_20261101.assemble --packet analysis/A_short_replication_qwen_20261101/TEST_fixed256_v3 --out analysis/A_short_replication_qwen_20261101/TEST_assembly_fixed256_v3
# Llama
python -X utf8=1 -m a_short_llama_20261101.analysis assemble --input analysis/A_short_replication_llama_20261101/TEST_fixed256_v3 --out analysis/A_short_replication_llama_20261101/TEST_assembly_fixed256_v3
```

With the actual independent TEST completion snapshot/review, build the zero-model final packet:

```powershell
python -X utf8=1 -m a_short_llama_20261101.prepare_offline --mode analysis --arrays "$shortRoot/TEST_assembly_fixed256_v3/manifest.json" --eligibility analysis/AB_confirmatory_execution_20261101/eligibility_synthesis_v5/A_actual_v1/eligibility_manifest.json --completion-snapshot "$shortRoot/TEST_fixed256_v3/completion_snapshot_v1.json" --completion-review "$shortRoot/TEST_fixed256_v3/completion_review_astra_v1.json" --out "$shortRoot/final_fixed256_v3"
```

Apply recursive source-import closure to this new packet metadata before freeze/review as well. `prepare_offline` analysis mode checks accepted raw TEST membership and both existing A eligibility receipts; it does not demand selected-N or whole-A/B completion. `analysis.analyze` uses contrasts `[256,2]`, unique block IDs, one frozen own r0, unchanged 1999-draw inference. T5 is the sole primary model hypothesis, Bonferroni across two prespecified models (alpha .025 each, absent model does not shrink family). T2 is descriptive and its decision p fields are removed. No 80% joint power or width assurance claim. This final-analysis path is source-inspected for admission compatibility; actual raw results and final output still require independent acceptance. Never call `prepare_offline --mode selector` for this amended workflow.

The metadata-only import additions, actual execution receipts and later TEST acceptance must remain visible. No fabricated campaign-completed flag or prior-selector success is permitted.
