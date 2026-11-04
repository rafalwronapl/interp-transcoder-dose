# Coherent B power and precision generator — root draft1

2026-11-01. Prospective extension to N_SELECTOR_DESIGN_ROOT; requires implementation/synthetic verification and independent review before PILOT. No new measurements; no alteration of running calibration.

## Joint observed block object

PILOT rows are independent name-pair blocks. Within row retain paired full/projected,so/when,recipient sides and doses; compute prescribed equally weighted main-template means. For power retain8 jointly paired nonnegative scalar FINITE-MARGIN energies:

S_f1,E_TC_f1,E_Taylor_f1,S_p1,E_TC_p1,E_Taylor_p1,S_fsmall,E_TC_fsmall.

S is native marginchange squared and identically zero-predictor error; all E are squared margin prediction errors. B1 uses S_f1-E_TC_f1 and E_Taylor_f1-E_TC_f1;B3 correspondingprojected;B2 uses the same full-c1 columns and full-small columns. Never independently generate B2 from unrelated noise after generating B1.

## Fixed alternative and infeasibility

Let m_j be empirical PILOT means of these positive-energy columns,treated solely as nuisance scales/shape. Hold all THREE native S means fixed. Require m_S_f1>.04 and m_S_p1>.04;otherwise the stipulated .04 superiority-to-zero alternative with positiveTCerror is infeasible at retained signal scale. Report INFEASIBLE_FIXED_ALTERNATIVE,do not inflate native signal,reduce target or useepsilon.

Target means:T_E_TC_f1=m_S_f1-.04,T_E_Taylor_f1=m_S_f1;T_E_TC_p1=m_S_p1-.04,T_E_Taylor_p1=m_S_p1. Set T_E_TC_fsmall=m_S_fsmall*exp(.20)*(T_E_TC_f1/m_S_f1). Native signal targets are their PILOTmeans. Then population B1/B3 improvements are each.04 and B2logcontrast.20 by construction; verify numerically before simulations. A zero/nonfinite sourcecolumnmean makes the generator inconclusive;never fill,drop,addepsilon or searchanotheroperator.

For each column q_ij=x_ij/m_j. Two prespecified shape scenarios gamma=1 and1.5: r_ij=q_ij^gamma/mean_i(q_ij^gamma). Candidate finitepopulation X*_ij=T_j*r_ij. Resample WHOLE rowindices with replacement jointly across allcolumns,then run production estimands/IUT/Holm on each Nsample. Rowpairing/rankdependence is retained; nonlinearstress changes covariance and must NOT be described as exact covariance preservation. The population means are targetsexactly. These are prospective statistical alternatives,not simulated native language models or guaranteed worst-case populations. Reportbothscenarioresults;require both for the design decision.

## Precision separate from forced power alternatives

Precision rows retain the2operator×2main-template×(TCerror,nativesignal) structure atc1;pool mixture AFTER constructing means. Use empirical nuisance means,not artificial targetTCmeans above. Apply samegamma pairedpositiveshape construction normalized to ORIGINAL columnmeans. For each Nsimulate all12 intervals jointly;event is all absRMS halfwidths<=.10 and all relativeRMS halfwidths<=.02. Coverage and assurance are distinct; actual interval procedure needs separate calibration. Zero/nonfiniteaggregate or bootstrap degeneracy counts as failure/inconclusive,not a deletedreplicate.

## Monte Carlo allocation update

The earlier6probability budget covers only one scenario. This extension fixes2gamma scenarios:2N×(A-power,B-power,Bprecision)×2scenarios=12selection probabilities when A uses its specified baseline/stressed centered residual scenarios. One-sidedClopperPearson lowerbounds alpha=.05/12 give simultaneous>=95% MC confidence across these12. Allocate additional acceptancegates separately; if power and precision are simulated by an approximation with a productionmethodbridge, the bridge has its OWN explicit MCerrorbudget and reduces the claimed guarantee unless overallalpha is split. Freeze all budgets before PILOT,not after results.

CandidateN must pass bothgamma/scenarios,applicable fixed nullcalibration,and exact or validatedconservative productionpower/precision. A/B selected independently; no posthoc bestscenario. No earlyacceptance from partialMC; optional earlyREJECTION is allowed only if a deterministic bound proves even all remaining fixedreplicates succeeding cannot satisfy the frozen final lowerbound. Preserve counts and reason,never extend untilpass.

## Needed checks

Synthetic inputs with sharedenergies,known covariance,zero columns,boundaryS=.04,pairedpermutations andmissingrows. Verify targetmean equations,sharedB1/B2columns,positivity,scenario normalization,fullblock pairing,IUT/Holm andjoint12precision. Compare method-level numericalp/intervalbehavior withproduction20000drawprocedure; no assumption of universal validity from previous finite nullscenarios. Publish feasibility/limitations,not a guarantee that any real pilot will yield N<=256.
