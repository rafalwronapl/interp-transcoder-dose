# Second public-artifact B experiment

Gemma-3-1B, L22, public medium16k JumpReLU TC without affine skip. 256 fresh name-pair TEST blocks, three shared templates;32 FIT blocks. Full donor operator only. Prior exploratory artifact exposure disclosed.

Descriptive finite-corpus comparison; nominal pointwise block intervals conditional on this FIT. No calibrated family/population rejection claim.

| Dose | Method | Relative RMS | Absolute RMS | Native RMS |
|---|---|---:|---:|---:|
| 0.05 | TC | 1.3418225621616118 | 0.06967132272482071 | 0.051922902989933004 |
| 0.05 | FROZEN | 1.321727268897434 | 0.06862791676211055 | 0.051922902989933004 |
| 0.05 | TAYLOR | 0.23559285622730708 | 0.012232665019011699 | 0.051922902989933004 |
| 0.05 | RIDGE | 0.8478399858463911 | 0.04402231333608833 | 0.051922902989933004 |
| 0.05 | MEAN | 0.9491468831829458 | 0.049282461538705365 | 0.051922902989933004 |
| 0.05 | ZERO | 1.0 | 0.051922902989933004 | 0.051922902989933004 |
| 1.0 | TC | 1.153807211686916 | 0.440628129319152 | 0.38189060083524234 |
| 1.0 | FROZEN | 1.2312239890160495 | 0.4701928689281029 | 0.38189060083524234 |
| 1.0 | TAYLOR | 2.69856783032909 | 1.0305576901190325 | 0.38189060083524234 |
| 1.0 | RIDGE | 0.5079663606191274 | 0.19398757866092994 | 0.38189060083524234 |
| 1.0 | MEAN | 0.6699406012663986 | 0.2558440187415485 | 0.38189060083524234 |
| 1.0 | ZERO | 1.0 | 0.38189060083524234 | 0.38189060083524234 |

Main so/when mixture crossover (Taylor better at .05, TC better at1): True.
TC beats ridge at1: False.

All144 cells are preserved in run/summary.json;9216 document-dose rows in run/rows.json. This extension does not isolate model scale, layer, or architecture. Three templates reuse the same256lexicalblocks. A negative outcome is retained and does not trigger artifact substitution.

Accounting:80932heterogeneous forward operations,0backward,1 model-load attempt. Completed cache preserved. Independent completion review remains pending in completion_review.json.
