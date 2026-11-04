# B3/B5: complete fixed-corpus diagnostics

32 previously observed blocks16–47;768 cells. Posthoc oracle diagnosis, no fresh holdout or population claim. All strata and negative contrasts retained.
B3 changes whole residual direction using two same-dose partners while preserving norm. B5 manipulates FIT-selected feature switches versus random pools of the same32features. Actual switched-feature counts and vector norms are NOT matched. The full-dose random pool is usually inactive, so this control does not isolate feature identity at equal intervention strength. These interventions concern the replacement operator, not recovery of a native circuit.

| Stratum | partner1 − RR | partner7 − RR | EXCEPT top − EXCEPT random | ONLY top − ONLY random |
|---|---:|---:|---:|---:|
| pooled/full/0.05 | 0.00095412344 | 0.00063640703 | -0.00028406124 | 0.00027257754 |
| pooled/full/1.0 | 0.037870819 | 0.075064589 | 8.8213429 | -8.6535416 |
| pooled/projected/0.05 | 0.0042405985 | 0.0030658671 | -0.00037993198 | 0.0003741503 |
| pooled/projected/1.0 | 0.11522559 | 0.13081751 | 7.33723 | -7.2887856 |
| so/full/0.05 | 0.0020390648 | 0.0017755656 | -8.8125834e-05 | 8.3730886e-05 |
| so/full/1.0 | 0.042890065 | 0.041479012 | 14.372377 | -13.967455 |
| so/projected/0.05 | 0.0064419416 | 0.0042583939 | -8.9882209e-05 | 8.9231717e-05 |
| so/projected/1.0 | 0.17790432 | 0.19401135 | 12.214265 | -12.141427 |
| transfer/full/0.05 | 0.00064903117 | -0.00015941649 | -0.00040515942 | 0.00040099971 |
| transfer/full/1.0 | 0.026731801 | 0.11541313 | 3.6358265 | -3.5614972 |
| transfer/projected/0.05 | 0.0026687276 | 0.0025611201 | -0.00069855967 | 0.00070333007 |
| transfer/projected/1.0 | 0.079373558 | 0.13602357 | 3.1905906 | -3.1135473 |
| when/full/0.05 | 0.00017427436 | 0.00029307196 | -0.00035889848 | 0.00033300204 |
| when/full/1.0 | 0.04399059 | 0.068301624 | 8.455825 | -8.431673 |
| when/projected/0.05 | 0.0036111263 | 0.0023780874 | -0.00035135405 | 0.00032988911 |
| when/projected/1.0 | 0.088398882 | 0.062417595 | 6.6068347 | -6.6113828 |

Positive first/second columns mean the original residual direction has lower loss than that partner. Positive third means removing FIT-selected switches harms more than removing random switches. Negative fourth means retaining FIT-selected switches beats retaining random switches. These are descriptive conditional comparisons, not universal necessity/sufficiency claims.

Cumulative actual charged operations: {'forward': 7829, 'backward': 4}; components: {'initial_failed': {'forward': 461, 'backward': 4}, 'qualification': {'forward': 2}, 'corrected': {'forward': 7366}}. Adopted results are not charged again. The initial failed stage and qualification remain in cumulative cost.
The initial failure occurred after461F+4B due to thread-dependent float32 reduction;2TC-only qualification calls at historical2threads reproduced both failed vectors bitwise. Corrected TC encoding/decoding uses2threads; native suffix1thread. Actual1thread FIT-selected groups and valid controls are explicitly preserved; every evaluated endpoint retains exact parity checks.
Actual switching counts by condition: {"full/0.05": {"contexts": 192, "mean_random": 0.005208333333333333, "mean_top": 0.328125, "random_zero": 191}, "full/1.0": {"contexts": 192, "mean_random": 0.020833333333333332, "mean_top": 8.3125, "random_zero": 188}, "projected/0.05": {"contexts": 192, "mean_random": 0.0, "mean_top": 0.16145833333333334, "random_zero": 192}, "projected/1.0": {"contexts": 192, "mean_random": 0.005208333333333333, "mean_top": 4.078125, "random_zero": 191}}
Independent final completion review pending.
