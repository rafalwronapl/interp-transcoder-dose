# Independent marginal-calibration assessment — 2026-11-01

Reviewer /root/sol_ab_execution/statistical_review. Decision: current marginal calibration does not establish its frozen readiness criterion; main PILOT/TEST should remain unstarted. This assessment does not stop or modify calibration_final_v1. No model calls were made by this reviewer. It does not reassess the separately reviewed single technical capture.

## What the completed receipts establish

The final-v1 rule requires simultaneous Clopper–Pearson upper bounds no larger than nominal+0.01. It allocates Monte Carlo error across16cases×4intervals. The rule is unchanged here. At the0.05 threshold:

| Heterogeneous mean scenario | Rejections | Estimate | Simultaneous CP interval | Interpretation |
|---|---:|---:|---|---|
| N128 |615/10000|0.0615|[0.053725,0.069970]|Evidence of exceeding nominal0.05; neither proof of exceeding0.06 nor evidence of staying below0.06. |
| N256 |538/10000|0.0538|[0.046522,0.061785]|Neither nominal0.05 nor tolerance0.06 is demonstrated to be exceeded; upper≤0.06 is not established. |

At N128 the lower bounds also exceed nominal0.025 and0.016667: [0.030331,0.043005] and [0.020796,0.031558]. Neither lower bound exceeds its corresponding nominal+0.01 tolerance. At N256 the two smaller-threshold upper bounds satisfy their tolerance limits. Thus N128 shows actual nominal inflation in this simulated distribution; N256's failed0.05 gate is a certification failure due to an interval crossing the tolerance, not demonstrated inflation above the allowed tolerance. The exact machine-readable distinction is marginal_gate_interpretation_v2.json.

Construction99%CI coverage passes in these receipts: N1289768/10000, simultaneous lower0.971307; N2569840/10000, lower0.979341. CI coverage does not repair hypothesis-test size; these are separate calculations.

## Recommended correction before TEST

Preserve all v1 receipts and finish its frozen calibration. Then introduce an explicit method-v2 amendment with a fixed conservative mapping **p_safe=min(1,2p_raw)** applied to every primitive component before IUT and Holm. Retain and report the raw p values, safe p values, effect estimates and intervals. Keep the original hypotheses, estimands, families, corpus and outcome-freeze rules. A support decision should also require the preregistered effect direction. This safeguard is equivalent to requiring twice the one-sided tail in the predicted direction; it is a more conservative inferential choice made before scientific TEST, not a change in the expected effect or a success threshold selected from TEST.

The multiplier2 is a candidate safeguard, not a mathematical universal guarantee. Freeze it once, with new source/specification hashes, then validate using an independent new Monte Carlo seed family. Use the same original readiness tolerances rather than moving a failed boundary. At the Holm operating levels0.05,0.025,0.016667, method-v2 needs raw-tail calibration at0.025,0.0125,0.008333. The current receipts contain only the first of these; they cannot certify the amendment by themselves. Do not repeatedly tune the multiplier on successive validation samples until a result passes. If method-v2 fails, report the result and make a separately justified amendment or a scientific infeasibility decision.

The new validation must cover the full A/B IUT/Holm families and least-favorable partial nulls, not marginal tests alone. A per-component allowance of nominal+0.01 does **not** by itself imply family FWER0.05; inflated component sizes can accumulate through the family procedure. Retain separate empirical family calibration and state its accepted tolerance explicitly. Preserve heavy-tailed positive-energy and heterogeneous mean scenarios, zero/missing handling, and the20000draw production bridge. Recalculate power at the originally chosen effect scales and precision assurance using the amended inference; a conservative p mapping can increase requiredN. The two-sided-equivalent significance safeguard does not change the point estimands or automatically change the RMS precision intervals.

Increasing simulation repetitions can narrow uncertainty for N256, but it cannot undo the N128 evidence of nominal inflation. Do not extend a fixed10000replication run only because its bound narrowly fails, and then reuse its original fixed-sample confidence claim after stopping on success. A fresh predeclared larger validation run, or a genuinely anytime-valid Monte Carlo confidence sequence, would be needed for that strategy. Increasing N might improve asymptotics but is not a general proof of control, and should remain governed by the outcome-independent N rule.

## Alternatives and their limits

An upper confidence bound on the conditional bootstrap exceedance probability can guard against Monte Carlo underestimation of the tail. It does **not** correct an inaccurate bootstrap approximation to the sampling distribution. With20000draws, its effect near0.05 will usually be much smaller than a factor2 safeguard. It may be an additional conservative implementation detail after review, but is not a sufficient theoretical response to the observed heterogeneous scenario.

A sign-flip/permutation test is exact only under a justified exchangeability or symmetry null, stronger than the required null about a mean contrast. A sign/rank test can change the scientific estimand. Neither should silently replace the present tests. A robust mean/studentized alternative may be studied in a new pre-TEST method version, but requires its own assumptions, null calibration and power checks. There is no useful unrestricted finite-sample, distribution-free guarantee for arbitrary unbounded mean contrasts without further assumptions. Claim only finite-scenario empirical calibration for the tested design.

## Scope

Read statistics.py, validation.py and the immutable spec/source receipts plus completed heterogeneous/normal mean and normal ratio calibration records. Source hashes are in source_manifest_v2.json. The current calibration is still running; no future/unpublished outcome is assumed. This report is a methodological recommendation and CHANGES_REQUESTED readiness assessment, not a canonical launch approval.
