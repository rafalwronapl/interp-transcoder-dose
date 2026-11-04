# B precision repair v6 — prospective method amendment

2026-11-01. Authorized by user to repair B after old precision calibration failed. This amendment is chosen from method/known synthetic-calibration evidence, before any B scientific PILOT or TEST acquisition. Historical v4 failures remain failures. No new measurement is repeated to relabel a result.

## Frozen candidate

Preserve primary B1–B3, their estimands and thresholds, operator/dose/template definitions, finite native-margin errors, N candidates128/256, absolute RMS halfwidth .10logit and relative RMS halfwidth .02. Only the precision-interval procedure changes. Each independent row is one paired name block; sides are pooled first. For each operator append equal so/when energy mixture BEFORE logs or ratios.

All12 statistics are resampled together: absolute log RMS=.5log(meanE); relative log RMS=.5(log(meanE)−log(meanS)). Influence values are .5(E/meanE−1) and .5(E/meanE−S/meanS). Centered sample influence SD divided by sqrt(N) gives SE. Each of1999 shared-row bootstrap resamples recomputes means, influences and SE. Take max over all12 absolute studentized centered deviations. Use rank ceil(.99×2000)=1980 of1999 maxima. Joint intervals are exp(theta_hat ± q×SE_hat); compute halfwidth in ORIGINAL units.

Zero/nonfinite mean, observed SE or any resampled coordinate SE makes the complete interval set undefined. Never drop a draw or add an epsilon. Such undefined datasets count as coverage/assurance failures. No second-order-accuracy promise for Pareto3, whose third moment is not finite.

## Qualification and downstream consistency

Use exact1999 production,2000 independent datasets per each of8 fixed historical-law cases (two N ×lognormal035,pareto3,lognormal1,heterogeneous) with new fixed seeds. Freeze seeds before first simulation; no old calibration sample is reused as independent validation. Joint all12 coverage uses known population truth. One-sided Clopper–Pearson lower bounds at alpha=.05/8 must reach .95 for every relevant N case. Counts fixed; no extension until pass. Reusing scenario laws selected after observing failure is method development followed by independent simulation, not unseen-law validation or distribution-free proof.

Selector precision assurance uses this exact method and1999 draws,2000 fixed replicates, predeclared nuisance scenarios1/1.5, unchanged .90assurance goal and conservative alpha=.05/16 per MC bound. No1999-to20000 bridge. Power hypotheses and their approved kernel remain unchanged. New eligibility must bind candidate source/spec/actual calibration closure and review; an old failed precision flag cannot be replaced by an unsupported Boolean. Native acquisition requires actual new eligibility; selector and final B report use the same v6 precision procedure.

If qualification or assurance fails, record infeasibility under the frozen cap. Do not substitute another method inside this campaign. Any subsequent method would need another explicit version and independent prospective review.

## Rationale and limits

The old1999-screen Bonferroni marginal tails had about .83 draws; its20000 production tails had about8.33. A joint maximum at1999 draws uses about20 upper-tail draws and preserves dependence. Studentization addresses a different problem from merely taking logarithms: monotone log-percentile backtransformation alone essentially preserves the percentile construction. This motivates a candidate, not proof it will pass finite-sample calibration.

Primary methodological references: [Hall1988, theoretical comparison of bootstrap intervals](https://doi.org/10.1214/aos/1176350933); [Hall and LePage, bootstrap studentized mean](https://www.ism.ac.jp/editsec/aism/48/29.html); [JSS2024 simultaneous max-t construction](https://www.jstatsoft.org/index.php/jss/article/download/v108i03/4527). Their settings do not establish coverage for this particular RMS estimator; the planned calibration is still required.

Implementation: `ab_confirmatory_20261101/precision_candidate_v6.py`. New integrations and launch packets are separate files. All frozen running workers, original statistical sources and caches remain preserved. No B scientific effect is inferred from this repair.
