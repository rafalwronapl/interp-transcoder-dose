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

Accounting:80932heterogeneous forward operations,0backward,3 model-load attempts. Completed cache preserved. Independent completion review remains pending in completion_review.json.

Interpretation: ranking crossover and useful predictive accuracy are distinct outcomes. At c=.05, TC/Taylor relative RMS are 134.182%/23.559%; at c=1, 115.381%/269.857%. Ridge at c=1 is 50.797% and zero-change is100%. The strong useful-accuracy regime of Gemma270M is NOT reproduced by this artifact: the TC result must not be described as a second demonstration of10%error or superiority to the simple baselines. All six doses and the transfer frame are retained; no artifact substitution or changed success criterion follows this outcome.

Full frozen dose curve: so. Relative RMS in percent; absolute columns in logits.

| Dose | TC% | Taylor% | Ridge% | Mean% | Frozen% | Zero% | TC absolute RMS | Native RMS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.05 | 144.9499 | 20.3338 | 86.0012 | 95.1054 | 140.8849 | 100.0000 | 0.084613 | 0.058373967 |
| 0.1 | 134.0781 | 45.9950 | 87.6395 | 96.1900 | 140.3929 | 100.0000 | 0.13766698 | 0.10267668 |
| 0.25 | 104.7194 | 129.3388 | 75.4406 | 79.6591 | 117.4463 | 100.0000 | 0.21310524 | 0.20350122 |
| 0.5 | 102.1264 | 182.1987 | 49.0523 | 51.8704 | 85.3817 | 100.0000 | 0.37732181 | 0.3694654 |
| 1.0 | 99.0145 | 277.6503 | 57.0572 | 71.2869 | 125.3488 | 100.0000 | 0.4040011 | 0.40802218 |
| 2.0 | 44.6066 | 112.1153 | 36.0660 | 45.7305 | 100.0600 | 100.0000 | 2.4539776 | 5.5013785 |

Full frozen dose curve: when. Relative RMS in percent; absolute columns in logits.

| Dose | TC% | Taylor% | Ridge% | Mean% | Frozen% | Zero% | TC absolute RMS | Native RMS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.05 | 113.3312 | 28.2514 | 82.6521 | 94.5863 | 115.6926 | 100.0000 | 0.050485905 | 0.04454723 |
| 0.1 | 108.7597 | 58.4098 | 78.5594 | 90.9441 | 116.2755 | 100.0000 | 0.089860941 | 0.082623386 |
| 0.25 | 110.2916 | 119.2709 | 54.3240 | 63.8588 | 109.9025 | 100.0000 | 0.22664104 | 0.20549255 |
| 0.5 | 114.4200 | 152.6390 | 38.5047 | 45.1288 | 104.8363 | 100.0000 | 0.42422355 | 0.37076004 |
| 1.0 | 134.0842 | 259.1305 | 41.0173 | 60.8182 | 120.0980 | 100.0000 | 0.47443588 | 0.35383437 |
| 2.0 | 38.6572 | 109.4758 | 32.9918 | 41.4523 | 100.5797 | 100.0000 | 2.03959 | 5.2760989 |

Full frozen dose curve: transfer. Relative RMS in percent; absolute columns in logits.

| Dose | TC% | Taylor% | Ridge% | Mean% | Frozen% | Zero% | TC absolute RMS | Native RMS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.05 | 136.0211 | 25.1552 | 87.3134 | 92.2491 | 127.2000 | 100.0000 | 0.04914361 | 0.036129402 |
| 0.1 | 115.8738 | 53.1093 | 86.2611 | 89.2011 | 125.3020 | 100.0000 | 0.076281065 | 0.06583117 |
| 0.25 | 105.7421 | 115.6039 | 66.9208 | 65.7922 | 109.0286 | 100.0000 | 0.16414314 | 0.15522972 |
| 0.5 | 108.9479 | 151.1644 | 45.8913 | 47.0944 | 97.7044 | 100.0000 | 0.30903939 | 0.28365796 |
| 1.0 | 137.4261 | 267.2595 | 60.8123 | 74.9801 | 127.5521 | 100.0000 | 0.37622451 | 0.27376493 |
| 2.0 | 49.3220 | 110.7607 | 37.8002 | 49.3511 | 101.7664 | 100.0000 | 2.1517077 | 4.3625756 |

Full frozen dose curve: main_mixture. Relative RMS in percent; absolute columns in logits.

| Dose | TC% | Taylor% | Ridge% | Mean% | Frozen% | Zero% | TC absolute RMS | Native RMS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.05 | 134.1823 | 23.5593 | 84.7840 | 94.9147 | 132.1727 | 100.0000 | 0.069671323 | 0.051922903 |
| 0.1 | 124.7416 | 51.2345 | 84.1876 | 94.1631 | 131.4429 | 100.0000 | 0.11624798 | 0.093190999 |
| 0.25 | 107.5687 | 124.3577 | 65.6342 | 72.1160 | 113.7003 | 100.0000 | 0.21997727 | 0.20449931 |
| 0.5 | 108.4690 | 168.0184 | 44.0767 | 48.6048 | 95.6390 | 100.0000 | 0.4014582 | 0.37011328 |
| 1.0 | 115.3807 | 269.8568 | 50.7966 | 66.9941 | 123.1224 | 100.0000 | 0.44062813 | 0.3818906 |
| 2.0 | 41.8618 | 110.8586 | 34.6272 | 43.7330 | 100.3093 | 100.0000 | 2.256317 | 5.3899158 |

All144 metric cells and nominal pointwise95% block intervals remain in run/summary.json. These are conditional finite-corpus descriptions; no calibrated familywise population rejection is claimed.

Operational recovery: the initial worker exited after383durableTESTcontexts because a Windows reader briefly prevented replacing advisory STATUS.json. A separately reviewed narrow status-publication wrapper resumed the same scientific worker/cache identity; valid completed measurements were read from cache. The full80932logical operation schedule contains no duplicate attempts. Cache replay traversal cost time but did not repeat inference. Resume provenance: resume_snapshot.json/resume_review.json and status_resume.py.
A second controlled handoff occurred only during cache-only replay at379/383contexts, with the exact child suspended and unchanged ledger verified before stop. It memoized the exact digest of the immutable74.8MB FIT object; all numerical code/cachekeys stayed unchanged and FIT immutability was rechecked before completion. It avoided1535redundant FIT serializations, not scientific measurements. See fit_digest_review_v3.json and fit_digest_handoff_done.json.
