# Actual eligibility and independent-study selection, v5

2026-11-01. No numerical v4 source or running calibration changed. No model or new Monte Carlo campaign ran during this preparation. Six cheap tests passed. Actual A evidence was synthesized:128ineligible,256eligible before independent review; every failed128case is retained.

`prepare_eligibility_v5 build --study A --out NEW_DIRECTORY` reads all36 frozen A family cases perN, four scalar coverage cases perN and the completed14-test missing/degenerate suite. B uses54family and eight scalar coverage cases perN, plus all four completed joint12precision coverage cases perN from `--precision-folder ACTUAL_RUN_DIRECTORY`. The universe is derived and checked against the frozen180-case definition, not guessed as45per group. Missing files, changed source identities, contradictory count/bound/PASS flags and incomplete precision replicate closures fail; no missing result is converted into PASS. Raw scalar type-I failures are not used as coverage failures, because fixedsafe2 leaves intervals unchanged and its family validity has a separate gate.

Build creates immutable per-requirement/eligibility/synthesis receipts plus input manifest and a canonical maintenance contract. Negative eligibility is a valid reviewed finding. It does not prevent reviewing the synthesis. Snapshot and independent review follow:

```
python -m research_checks snapshot ACTUAL_DIRECTORY/contract.json --phase completion --out ACTUAL_DIRECTORY/completion_snapshot.json
python -m research_checks verify --snapshot ACTUAL_DIRECTORY/completion_snapshot.json --review ACTUAL_REVIEW
python -m ab_confirmatory_20261101.prepare_eligibility_v5 finalize --folder ACTUAL_DIRECTORY --snapshot ACTUAL_DIRECTORY/completion_snapshot.json --review ACTUAL_REVIEW
```

Finalize canonically verifies the actual review and runs the corrected eligibility validator for both candidate Ns against all bound inputs. Only then is `eligibility_manifest.json` exported. Paths are absolute in the portable manifest and normalized to workspace-relative at the canonical verifier boundary by eligibility_paths_v5; no frozen statistical logic is patched. Root's acquisition-authority builder consumes this actual finalized manifest for PILOT/TEST.

Independent selection input is prepared from actual sealed PILOT arrays and this reviewed eligibility:

```
python -m ab_confirmatory_20261101.prepare_selector_v5 --study A --arrays-manifest ACTUAL_A_PILOT_ASSEMBLY/manifest.json --eligibility-manifest ACTUAL_A_ELIGIBILITY/eligibility_manifest.json --out NEW_A_SELECTOR_MANIFEST --fit-snapshot analysis/AB_confirmatory_execution_20261101/A_fit_primary_v1/completion_snapshot_infrastructure_v2.json --fit-review analysis/AB_confirmatory_execution_20261101/A_fit_primary_v1/completion_review_infrastructure_v2.json
python -m ab_confirmatory_20261101.selector_execution_v5 --study A --manifest ACTUAL_A_SELECTOR_MANIFEST --out NEW_A_SELECTION_OUTPUT
```

Use B analogously, omitting FIT-scale arguments. Each numerical campaign still requires its own independently reviewed launch contract. These command lines identify executable entrypoints, not permission to bypass review.

Only arrays for the requested study are required. A uses original case indices0,3,6,9; B uses1,2,4,5,7,8,10,11. Indices,seed generation,core numerical run_case,2000replicates and alpha.05/16 remain unchanged. Running A alone does not spend B's unused error budget or fabricate B data/results. Output `selected` contains only the executed study; `cases` contains its complete four/eight case slots, including explicit ineligible candidates. Root campaign_authorization already accepts this schema.

A `v_target` is no longer accepted as a freely chosen scalar: the selector requires manifested `fit_scale:{evidence,snapshot,review}`, canonical acceptance of the designated frozen r0 FIT receipt and exact agreement with its recorded V_target. The input helper reads that accepted value automatically. B has no artificial dependency on A FIT.

Code ownership: selector_execution_v5 transferred to this author for this change; selector_v4 and all numerical/calibration sources remain frozen. New helpers are prepare_eligibility_v5.py and prepare_selector_v5.py. Tests cover study-only inputs/index allocation, actual A receipt consistency without simulations, missing evidence, falsifiedPASS, incomplete Bprecision closure and unbound FIT scale. Actual B synthesis waits for genuine completed B evidence; it has no alternate methodological choice left to make.
