# Final primary and stability analysis preparation

No model calls. Articles are edited only after all experiments and independent result reviews.

Three independent modes: `A` (frozen r0 primary family), `B` (primary family and joint12 precision), `STABILITY` (all16 FITs on exactly the shared TEST blocks). Only actual TEST128/256 assemblies are accepted. PILOT cannot be relabeled a final result. Primary1999draws, Bprecision20000draws, pointwise crossed stability1999draws; frozen reviewed numerical kernels unchanged.

After the actual TEST raw stage has an independent completion receipt, assemble its results using the approved A/B assembler. Then:

```
python -m ab_confirmatory_20261101.prepare_final_analysis_v5 --manifest ACTUAL_ASSEMBLY_MANIFEST --mode A --acceptance-snapshot ACTUAL_COMPLETION_SNAPSHOT --acceptance-review ACTUAL_COMPLETION_REVIEW --out analysis/AB_confirmatory_execution_20261101/A_final_analysis_ready_v1
```

Use mode `B` for B. For `STABILITY`, use the complete16-FIT assembly and an acceptance snapshot that includes both the primary and shared-TEST stability raw closures. The builder binds the designated accepted r0 FIT and its vector scale automatically; an arbitrary alternative FIT is rejected. It emits a derived analysis manifest binding that scale, so the worker consumes exactly the reviewed inputs.

Each generated contract has zero model budget and an empty operation schedule. Freeze it, obtain a separate pre-run review, then Sol executes:

```
python -m research_checks launch --snapshot ACTUAL_PRE_RUN_SNAPSHOT --review ACTUAL_PRE_RUN_REVIEW
```

Actual immutable result is `result.json`; repeated calls verify identity and reuse it. Every raw input is required in the independently accepted closure. Block IDs must be unique and match the array block axis; stability requires exactly16 x N x4. Failed hypotheses, undefined precision and unmet width targets stay visible. Statistical eligibility, precision calibration and finite-scenario limitations remain separate from the analysis output.

The actual two-test receipt covers A/B numerical dispatch, immutable replay, PILOT rejection and mismatched block axes. Existing numerical stability tests are reused; designated-scale/acceptance wiring is additionally reviewed statically. No pretrained tests or completed calibration simulations were repeated. Secondary all-method/template/dose/endpoint/linear reports are prepared in a separate module, without adding a hypothesis family.
