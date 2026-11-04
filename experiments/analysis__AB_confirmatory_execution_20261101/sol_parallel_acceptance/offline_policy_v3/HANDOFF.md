# PostTEST offline execution — 2026-11-01

This new policy preserves `concurrency_runtime_v2.py`, one model lane, two CPU slots and every old policy. Its only policy delta adds zero-model entrypoints `ab_confirmatory_20261101.analyze_b_descriptive_v8` and `a_short_llama_20261101.analysis`. Historical resource observations inherited from the prior policy are not fresh RAM measurements. Every actual analysis contract still needs canonical pre-run snapshot and independent review.

Maintenance snapshot: `snapshot_v1.json`, SHA `f64f923e6b177dc5b4612a6ec40c38d643ed66f3dabdd36e2276ffe64e883fdd`. Use the independent maintenance review when issued, not this document as authorization.

After actual B closure and independent acceptance, executor runs from repository root (substitute actual versioned completion filenames if needed):

```powershell
python -X utf8=1 -m ab_confirmatory_20261101.prepare_b_descriptive_analysis_v9 --packet analysis/AB_confirmatory_execution_20261101/B_descriptive_TEST_v8 --completion-snapshot analysis/AB_confirmatory_execution_20261101/B_descriptive_TEST_v8/completion_snapshot_v1.json --completion-review analysis/AB_confirmatory_execution_20261101/B_descriptive_TEST_v8/completion_review_astra_v1.json --out analysis/AB_confirmatory_execution_20261101/B_descriptive_analysis_v9
python -X utf8=1 -m research_checks snapshot analysis/AB_confirmatory_execution_20261101/B_descriptive_analysis_v9/contract.json --phase pre_run --out analysis/AB_confirmatory_execution_20261101/B_descriptive_analysis_v9/pre_run_snapshot_v1.json
```

Builder verifies the accepted completion phase and exact config/corpus/closed159744-op acquisition. All18432 actual consumed result records must be closed and accepted. Frozen descriptive-source hashes, original family failures, resource amendment and accepted v6qualification49967 provenance are carried into the input manifest. Static local Python imports are automatically included in the new analysis contract; no manual source patching is needed. The schedule is empty and budget0F/0B. No raw measurement or method selection is performed by packet construction.

After exact analysis pre-run review, launch using unchanged runtime and this new policy:

```powershell
python -X utf8=1 -m concurrency_runtime_v2 --snapshot analysis/AB_confirmatory_execution_20261101/B_descriptive_analysis_v9/pre_run_snapshot_v1.json --review analysis/AB_confirmatory_execution_20261101/B_descriptive_analysis_v9/pre_run_review_astra_v1.json --policy analysis/AB_confirmatory_execution_20261101/sol_parallel_acceptance/offline_policy_v3/migration_policy.json --policy-snapshot analysis/AB_confirmatory_execution_20261101/sol_parallel_acceptance/offline_policy_v3/snapshot_v1.json --policy-review analysis/AB_confirmatory_execution_20261101/sol_parallel_acceptance/offline_policy_v3/review_astra_v1.json
```

The entrypoint is exactly the prospectively frozen `analyze_b_descriptive_v8 --packet <original TEST packet> --out <analysis>/result.json`. It computes all finite-corpus contrasts/cells and only the originally qualified TC c1 joint12 v6 intervals (1999 draws, fixed seed2026110191). B family validity remains failed; no family p/Holm/rejection/support labels are authorized. Missing/incomplete outcomes are retained as incomplete, never replaced or omitted.

For Qwen/Llama use the already prepared unchanged `a_short_llama_20261101.prepare_offline --mode analysis` route in `../SHORT_FIXED_EXECUTION_HANDOFF.md`, followed by canonical actual-packet review and the same new policy. No selector MC or new inference method is introduced. Native queue remains B → Qwen → Llama; zero-model analysis can use available reviewed CPU slots. Independent acceptance of final scientific outputs is still required.
