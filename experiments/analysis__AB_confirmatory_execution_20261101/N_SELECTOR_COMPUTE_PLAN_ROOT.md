# Selector computation and reuse — root draft1

2026-11-01. Complements N_SELECTOR_DESIGN_ROOT and B_POWER_GENERATOR_DESIGN_ROOT. Explicit implementable option for bounded offlinecost; requires independent methodology and implementationreview before PILOT. No pretrainedcalls. Do not restart existingnullcalibration.

Freeze12selection cases:2N×2nuisancescenarios×(A jointpower,B jointpower,Bjoint12precision). Neligibility fromfinishednullcalibration;skipineligibleN with explicitreason,notnewtests. Power uses exactpairedblockstatistics plusp_safe2/IUT/Holm at1999bootstrapdraws in10000fixedreplicates percase. Precision uses1999drawconstruction as an approximation only,not an unqualified substitute forproduction20000. Case/dataset/replicate seeds deterministic and separatelyrecorded. Savegeneratedsufficientstatistics and decisions;neverregenerate a completedreplicate due to review.

For first1000prespecifiedreplicates in eachcase,evaluate the SAMEgenerateddataset also withproduction20000drawprocedure. Reusealreadycomputed1999result. Count overstatementevent:reduced-drawsimulationdeclaresjointsuccess butproductiondoesnot. Forprecision,successmeans all12widthgoals simultaneously;forpower allthreehypothesessupported. Degenerate/incomplete simulations countasfailure;reportthem.

Compute one-sidedCP lower L for reduced-drawsuccessprobability from10000replicates,and one-sidedCP upper U for overstatementprobability from1000pairedreplicates. Perboundalpha=.05/24 gives simultaneous>=95%MC across12L+12U. Conservative production-success lowerbound=max(0,L-U),by P(prodSuccess)>=P(reducedSuccess)-P(reducedSuccess,notprodSuccess). Independence of the two estimators is unnecessary for the unionbound;the first1000overlap intentionally saveswork. Compare thislowerbound with.80power/.90assurance. No assumption that reduceddraws are automaticallyconservative. No posthoclargerbridge to lowerU; failure meanscandidatefails underthisselector.

Exactproduction10k replicates could be an alternative PROSPECTIVE version,not an outcome-triggered fallback. This draft chooses fixed1999+paired1000productionbridge toboundcost beforePILOT;reportthat conservativeU maymakeNinfeasible. Use directproductionintervals for finalTESTreport regardless ofselectorapproximation.

No earlyacceptance. Earlyrejectionallowed only when fixedremainingreplicates cannotpossibly meet the final conservativebound evenifallremainingreducedsuccessesoccurandallremainingbridgediscordancesarezero. Saveproof/numerators/remainingcounts. This changesonlyruntime,notdecision. Ifbridgeisomittedbecauseboundalreadyfails,recordnotexecuted;neverpretendallreplicatescompleted.

ThisMCconfidence applies toselectionprobabilities under the frozen finite empirical/scenario generators,not universal populationcoverage or proof thatPILOT32 captures alltails. Separateintervalcoveragecalibration and statisticalfamilyeligibility remainrequired. Intervals/reportingmustlabels nominalconstructionlevels honestly.
