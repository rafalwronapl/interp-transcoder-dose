# B precision v6 additive execution path

No model, Monte Carlo calibration or selector campaign was executed while preparing these modules. Historical percentile failures and caches are unchanged. Candidate numerical tests are root-owned; eight cheap integration fixtures passed. New v6 qualification retains the same eight laws, using independent fixed-seed samples; this is not unseen-law validation. No second-order accuracy claim is made for Pareto3.

## Qualification packet

Actual packet: `B_precision_v6_calibration_v1/contract_v3.json`, `input_manifest_v3.json`, `pre_run_snapshot_v3.json`. Fixed qualification seed2026110161, exact8 cases x2000 datasets x1999 draws. One-sided CP alpha.05/8, joint12 coverage lower>=.95 for every case at each N. No20k bridge, retries, threshold relaxation or early acceptance. Candidate code, direct prepare.py dependency, protocol, root3-test receipt and calibration-only immutable/undefined fixtures are frozen separately from future adapters. Launch only after its independent pre-run review and the reviewed runtime-policy addition; A selector retains queue priority.

## Actual eligibility

After qualification and existing family/scalar suites finish:

    python -m ab_confirmatory_20261101.precision_eligibility_v6 build --out NEW_B_ELIGIBILITY --precision-folder ACTUAL_V6_CALIBRATION/run

This reuses existing original family/scalar/missing evidence read-only and binds complete new method-specific calibration closure. A fresh maintenance snapshot/independent review of the emitted contract is required before:

    python -m ab_confirmatory_20261101.precision_eligibility_v6 finalize --folder NEW_B_ELIGIBILITY --snapshot ACTUAL_SYNTHESIS_SNAPSHOT --review ACTUAL_SYNTHESIS_REVIEW

Old failed precision cannot pass the v6 method identity/spec/case closure checks. Negative gates stay negative.

## Native PILOT and TEST

    python -m ab_confirmatory_20261101.prepare_precision_v6 native --phase PILOT --authorization ACTUAL_B_AUTHORIZATION --tail-stage B_tail_qualification_v1_PATH --tail-snapshot ACCEPTED_TAIL_SNAPSHOT --tail-review ACCEPTED_TAIL_REVIEW --out NEW_B_PILOT

Use the established accepted authorization-manifest/corpus builder. This new builder creates a new packet using the frozen existing acquisition builder, then binds the new native admission wrapper and v6 sources before snapshot. Every native packet still requires original preflight and independent pre-run review. The wrapper verifies v6 eligibility before unchanged measurement machinery; TEST also requires exact v6 method/spec/candidate identity in its accepted selector receipt. No worker source is edited.

## Selector

First join accepted actual B PILOT assembly and finalized v6 eligibility using the existing `prepare_selector_v5 --study B` manifest builder. Then:

    python -m ab_confirmatory_20261101.prepare_precision_v6 selector --manifest ACTUAL_B_SELECTOR_MANIFEST --pilot-snapshot ACCEPTED_B_PILOT_SNAPSHOT --pilot-review ACCEPTED_B_PILOT_REVIEW --out NEW_B_SELECTOR

Bpower delegates the exact original v4 kernel with unchanged seed and original case indices. Bprecision uses exact1999 candidate draws, fresh fixed selector seed2026110167,2000 fixed replicates and CP alpha.05/16 lower>=.90. Scenarios1/1.5, cases1,2,4,5,7,8,10,11, width goals.10/.02 and minimum qualifying N remain unchanged. Undefined precision counts failure. No20k bridge. Fresh samples from the same selected empirical/scenario laws are not independent-law validation.

## Final B TEST report

    python -m ab_confirmatory_20261101.prepare_precision_v6 final --manifest ACTUAL_B_TEST_ASSEMBLY_MANIFEST --eligibility-manifest ACTUAL_V6_ELIGIBILITY_MANIFEST --acceptance-snapshot ACCEPTED_TEST_SNAPSHOT --acceptance-review ACCEPTED_TEST_REVIEW --out NEW_B_FINAL

The builder deterministically joins the accepted assembly and actual eligibility without operator-designed formulas; block count is structural. It emits the reviewed final wrapper using the same direct1999 v6 procedure and unchanged B family kernel. All generated CPU packets still need individual pre-run snapshots/reviews and reviewed lane launches. Raw/TEST acceptance is not replaced by preparation approval. Final outputs retain negative or inconclusive outcomes.
