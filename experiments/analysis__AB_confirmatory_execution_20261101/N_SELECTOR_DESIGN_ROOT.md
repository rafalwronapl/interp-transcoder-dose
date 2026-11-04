# Root: prospective N selector design, draft1

2026-11-01. Preparation only; no launch authorization. Sol implements, tests and obtains independent review. Preserve prior calibration failures. Does not block separately approved fixed r0 FIT-only capture. Freeze this design, implementation and numerical calibration before PILOT; freeze selected N before TEST. Any unresolved element below is a real gate, not permission to improvise after outcomes.

## Scope and eligibility

Separate N for A and B, candidate128 or256 independent TEST blocks; maximum256. PILOT32 disjoint blocks each. Candidate N is eligible only if its exact final statistical procedure passes all applicable predeclared calibration gates (family partial nulls, tails, degeneracy and the bridge to production20000 bootstrap draws). A failed N128 calibration excludes128 under that version; do not extend simulation until it passes, relax its bound, or substitute a new rule after PILOT. N256 requires its own evidence, not automatic eligibility. Any prospectively redesigned validation version requires independent review and preserved earlier failures.

Primary A remains r0. Proposed conservative component p=min(1,2*p_raw) before IUT/Holm is only a candidate. Establish finite-scenario calibration and power empirically; scaling p does not prove universal validity. Do not modify current running calibration source files.

## Physical alternatives and assurance

Retain the current premeasurement operational design targets from sample_size_spec.json: A1_L,A2_L,A3_L=.04 logit²; A2_V=.05 times r0 FIT_U mean squared native delta norm (numerical value frozen before PILOT). B1 and B3 component improvements=.04logit²; B2 natural-log pooled energy-ratio contrast=.20. These are design resolutions, not observed effects or required scientific support thresholds. A difference of MSE=.04 is not generally a difference of RMS=.20; do not advertise that equivalence or infer answer-accuracy gains from this MSE scale.

Require JOINT probability all three primary hypotheses in a study are supported>=.80 under the fixed design alternative, using the exact component tests/IUT/Holm and missing-data policy. Individual marginal powers must also be reported; they do not substitute for joint power.

B precision at c1:2 operators(full/projected) ×3 cells(so,when,equal-energy mixture) ×2 metrics(absRMS,relativeRMS)=12 intervals. Goals:halfwidth<=.10logit absolute and<=.02 relative, ALL12 simultaneously with assurance>=.90. Report actual nominal99% Bonferroni construction and calibrated population coverage goal>=.95 separately. Mixture pools energies before taking square roots/ratios. This precision does not establish the old5–8% effect or superiority by itself.

## Allowed PILOT use

PILOT is independent of TEST. A: form full paired block component vectors, center each column, inflate residuals1.5, and add the fixed target vector; resample blocks jointly to retain covariance. Never select N from observed PILOT support signs or from a smaller alternative chosen to match the data. A2 vector scale comes only from the already frozen FIT_U formula.

B mean-contrast power may similarly use centered paired residual vectors, but the nonlinear B2 statistic and its dependence with B1/B3 require an explicitly coherent positive-energy generator. Do NOT merely center the log-ratio estimate and treat it as the production ratio test. Specify and review an estimator-level simulation that preserves shared TC/native energies and covariance while imposing the fixed contrast, or use a prespecified family of coherent positive-energy distributions calibrated to dispersion and tested for target agreement. This is an unresolved implementation gate before PILOT, not delegated post-PILOT model selection.

Precision necessarily depends on native-signal and error scales, not covariance alone. Explicitly amend the earlier blanket covariance-only PILOT wording: B pooled positive energies may inform precision nuisance scales, solely through the frozen width rule, retaining both favorable and unfavorable scales; no searching templates/artifacts/operators based on PILOT errors. This access must be approved before PILOT. Power target magnitudes remain fixed. Zero/degenerate denominators are inconclusive, not epsilon-adjusted or dropped.

## Selection, simulation uncertainty and failures

Use common paired resampling across all components/precision cells within each simulated dataset. Count failed/undefined replicates as failures for joint power/assurance, and report their counts; never delete them. For each candidate report empirical joint power, all12 precision widths, assurance and Monte Carlo confidence bounds. Choose the smallest ELIGIBLE candidate whose simultaneous lower Monte Carlo bounds meet the study's power requirement and (for B) precision requirement. If none passes, outcome INFEASIBLE_UNDER_FROZEN_CAP; do not launch TEST or redefine the goals. Preserve PILOT evidence; a separately justified future design is allowed only as a new reviewed version.

Implement Monte Carlo counts/seed streams as a fixed finite specification before PILOT. Candidate proposal:10000 design replicates per candidate, deterministic PCG64 streams distinct from calibration and measurement. At most6 primary selection probabilities(Apower/Bpower/Bprecision ×2N); use one-sided Clopper-Pearson lower bounds with alpha=.05/6 for joint MC confidence>=.95. Additional acceptance gates require their own allocated multiplicity budget, not reuse of this claim. Fixed count, no optional extra draws until pass. Assess compute cost before approval.

If analytic approximations replace nested bootstrap in N selection, independently validate that they conservatively approximate the actual joint production power and precision event across frozen scenarios. A convenient normal approximation is not enough. Direct production-method simulation is the fallback subject to reviewed feasibility; never silently declare an unvalidated approximation ready. The20000-draw bridge must address very sparse tails in the12-interval construction and Monte Carlo instability.

## Separate stability module

Sixteen total FIT realizations is provisional; r0 may run separately. Additional15 require a prespecified numerical precision goal for between-FIT conclusions and calibrated crossed FIT×TEST inference. Shared TEST dependence is mandatory. Do not let stability averages replace r0 hypotheses. If joint goal is infeasible, report that scope rather than silently reduce the number of fits or choose the best realization.

## Required output before approval

Versioned selector spec, exact generator formulas, tests including zero/missing/corrupt cases, synthetic alternative verification, calibrated power/precision/MC receipts, cost schedule, frozen seed map and independent review. Later PILOT input hashes and selected N receipt must reproduce bit-for-bit without TEST data. No historical outcome-based reinterpretation.
