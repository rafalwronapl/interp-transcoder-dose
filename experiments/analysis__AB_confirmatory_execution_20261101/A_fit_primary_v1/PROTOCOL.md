# A primary r0: FIT-only stage, v1

Root,2026-11-01. Requires independent pre-run approval; this document is not approval.

## Scope amendment

Explicitly amends the earlier unfinished requirement to finalize inference/N selection before every FIT capture. Obtain only the already designated primary r0 from fixed FIT data, with NO PILOT/TEST, hypothesis tests or selection using readout performance. Captured margins must not determine hypotheses, statistical thresholds or TEST size. Inferential procedures and N-selection still require freezing/review before PILOT; TEST has a separate gate. This separation permits useful fitting while calibration continues.

## Fixed data and recipe

Exact local Gemma-3-1b-pt identity; float32 CPU eager,two threads. Layer25 of26,last prompt position. x is post-pre-feedforward normalization; M is post-feedforward normalization output; recipient residual R fixed. Readout logit(is)-logit(are), literal token IDs bound in tokens.json. Donors provide normalized-input/branch-output changes. No reduced attention circuit is evaluated.

48 disjoint lexical blocks:16FIT_MAP,16FIT_U,16FIT_EXT;448 documents. MAP and U each128 records on F0/F1 with all four side/distractor conditions. EXT192 records on T0/T2/T5, sharing16 blocks across the three arms. Exact slice of reviewed corpus; donor/token identities bound. Population is the qualified WordNet pool, including rare/technical terms, not representative everyday English. Tokenization does not establish competence; no outcome-based exclusions.

P:global scalar input RMS,centered ridge,unpenalized intercept,lambda0.01 with n*lambda dual penalty,FIT_MAP only. Labels are native donor-minus-recipient branch deltas. U0:uncentered SVD of FIT_U deltas,rank8. Uctrl/U2/U5:the same FIT_U stacked with respective T0/T2/T5 EXT deltas,equal counts/common blocks. Deterministic SVD sign; deficient rank fails technically,no adaptive rank. P shared; no readout labels select P/U; retain every U. Future power-design vector scale=.05*mean squared native-delta norm on r0 FIT_U,numeric value frozen before PILOT; not a support threshold.

## Qualification and budget

Five fixed control recipients in config.json cover F0/F1/T0/T2/T5. Capture them and donors first (10 records,one import). Each gets input/output sham,full-head parity,donor-input branch parity,positive output perturbation,unreachable earlier-position negative control,and local final-suffix parity. Final-layer positionwise MLP edit at previous token cannot reach final token through subsequent attention. Positive sensitivity is measured.

Frozen gates:sham/negative margin<=1e-5;donor branch relative error<=1e-4 with positive donor norm;full-head/suffix parity<=1e-4;positive margin change>=1e-6;negative edit norm>0. All must pass BEFORE remaining FIT captures. Technical failure preserves evidence and stops expansion; retries/repairs require reviewed amendments, not scientific relabeling.

477 NEW full-transformer forwards=447 new natural captures+30 controls;5 local suffix calls;0backward;482 operations total. One existing capture imported only via exact reviewed model/layer/document/token/dtype/operator compatibility and immutable receipt binding. Prior cost reported separately. cost_estimate.json provides estimates, not guarantees; one-record timing is not a throughput benchmark. One model worker; preserve unrelated services/calibration.

Canonical research_checks launch,hidden/logged,hash-bound dependencies and durable operation cache/receipts. No automatic retry reserve:consumed attempt without durable result cannot silently repeat. Complete-stage replay verifies hashes and returns without loading a model. Bound source files stay unchanged while other preparation proceeds elsewhere.

## Completion

Retain raw captures,ledger,controls,FIT_r0.json containing P/fourU/vector scale/provenance,and completion manifest. Independent completion review/canonical verification,update living Dorobek,copy evidence to separate A folder. Outcome is a fitted realization with scoped technical checks,not confirmation of A1-A3. Future PILOT/TEST binds frozen fit; no refitting or selection using TEST. Additional15 independent FIT cohorts are a separate stability stage requiring its own design/calibration/review.
