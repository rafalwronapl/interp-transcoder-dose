# B artifact and reproducibility table — 2026-11-02

Metadata only: no downloads, model calls, statistics, or large weight/raw hashes. SHA values for weights are inherited from accepted frozen identities. Repository links are recorded identifiers, not a new live web audit.

| Item | Recorded identity / execution | Evidence |
|---|---|---|
| Native model | `google/gemma-3-270m` @ `9b0cfec892e2bc2afd938c98eabe4e4a7b1e0ca1`; checkpoint `abb58eb73aece5163624090d5383c59cbcdb9e9539ec84cb864f74386c4b21d5` (536223056 bytes) | Frozen B model_identity; prior takeover alias/source manifest |
| Public TC | `google/gemma-scope-2-270m-pt` @ `b218cd5d69dc2fa71cff448b68d625e6c9702d49` / `transcoder/layer_15_width_16k_l0_medium`; params `ca3a2fc2c75ffa1c4305497ee1aba381bdedff90a49aeda5db82083e80e194ca` | Public-repository capture + original HF download metadata agree; local original params remain hardlinked |
| Architecture | JumpReLU, width16384, targetL0=60, no affine skip | TC config; target is not measured activity |
| Hooks | model.layers.15.pre_feedforward_layernorm.output → post_feedforward_layernorm.output; final prompt token | Native/ExactTail sources and actual technical qualification |
| Native remainder | Layers16/17 + finalnorm/head, original full-sequence states/kwargs; no KV cache | ExactTail; no last-layer shortcut |
| Arithmetic | CPU eager,float32,2torch threads; checkpoint config declares bfloat16; FP64 endpoint checks separately | Frozen TEST environment/config and source |
| Readout | logit(' she')−logit(' he'); tokenIDs1304/668; BOS2; recipient/donor final coordinates independent | Frozen tokenization metadata |
| Runtime | Python3.13.11; torch2.11.0+cpu; transformers5.5.4; numpy2.4.4; scipy1.17.0; UTF8mode1 | Actual TEST completion snapshot |
| Licenses | TC card records CC-BY4.0; base model, local software and dataset notices not consolidated | Explicit gaps below; TC license does not stand in for base terms |

## Actual stage identities

| Stage | Scope / budget | Accepted completion snapshot |
|---|---|---|
| `B_fit_reference_recovery_v2` | Accepted composite128-record FIT; original1860F4B plus separate4unfused referenceF; two actual LLM loads after preserved failure. | `d0d3ef007a9c3e9741729ccb7c04f007021ac8590f992dabd6d92d48164585f4` / `analysis/AB_confirmatory_execution_20261101/B_fit_reference_recovery_v2/completion_review_astra_v1.json` |
| `B_tail_qualification_v1` | Technical exact-tail/full-native output and gradient qualification;4unusedFIT documents;152F8B. | `3403ce5da8ce3a7aca00910a46d7a7da5a1af1a63e910451b0a884c889e17dd5` / `analysis/AB_confirmatory_execution_20261101/B_tail_qualification_v1/completion_review_astra_v2.json` |
| `B_precision_v6_calibration_v1` | Prospective synthetic finite-scenario qualification;8cases2000datasets1999draws,0modelcalls; not universal coverage or family validity. | `49967dcfcd6f1bf4cdf500fda0694d656af1baa190df8801a96a1e0c6769b580` / `analysis/AB_confirmatory_execution_20261101/B_precision_v6_calibration_v1/completion_review_astra_v1.json` |
| `B_pilot_early_v7` | Acquisition-only32paired blocks192documents,19776F192B; no refit/selection/inference. | `431ca09b1128967c3ff4b22d94bde02e852fa5d8dfd638881246762bf133d0d5` / `analysis/AB_confirmatory_execution_20261101/B_pilot_early_v7/completion_review_astra_v1.json` |
| `B_descriptive_TEST_v8` | Fixed256paired blocks1536documents,158208F1536B; family-ineligible finite-corpus study, no p/Holm/support claims. | `3a247b07f32fc030d9ac24efc74aea8a60eba38ddc3d97425a65d10da41b24f1` / `analysis/AB_confirmatory_execution_20261101/B_descriptive_TEST_v8/completion_review_astra_v1.json` |

## Statistical and provenance limits

Both original Bfamily candidates remain ineligible. Fixed256 TEST is descriptive, retaining all six methods/doses and transfer. v6 qualifies only theTC c1 joint12 interval procedure in fixed synthetic scenarios; no Holm, rejection or support label, universal coverage,80%power or achieved-width guarantee. Earlier failed procedures remain failed. One selected artifact/frozenFIT is not a random sample of public transcoders.

The original PROTOCOL_B.md is explicitly a draft; current accepted contracts/snapshots and immutable v8 amendment are authoritative. TC config names the base model with the literal `-pt` alias; the recorded native checkpoint/cache repository is `google/gemma-3-270m`. No Git HEAD is available because this workspace is not a git repository; use per-file source hashes.

## Gaps / pending items

- **BASE_LICENSE (missing_local_record)**: No base-model LICENSE/model-card terms file in inspected frozen model folder or HF snapshot. Do not substitute TC CC-BY4.0 for base-model terms or claim redistribution clearance.
- **LOCAL_CODE_LICENSE (missing_local_record)**: Workspace has no root LICENSE and is not a git repository; no upstream code commit/license is certified. Per-file sourceSHA256 is authoritative for this release inventory.
- **TOKENIZER_COMMIT (qualified_provenance)**: Tokenizer fileSHA256 values are frozen independently. Model cache revision is linked through prior config/checkpoint provenance; a separate per-tokenizer download metadata record was not recovered.
- **TC_CODE_REVISION (not_recorded)**: Public HF artifact/revision and CC-BY4.0 card are recorded. No particular upstream GitHub/library source commit is certified; exact local adapter/unfused-reference source hashes are supplied.
- **DATA_LICENSE (not_consolidated)**: NLTK Names exclusive-category source is recorded in protocol. Its redistribution notice/license was not consolidated in the inspected release inputs; local holdout is not pretraining-freshness certification.
- **FINAL_REPORT (pending)**: B final report/result/snapshot/review are not yet available at inventory; fill only from actual closed outputs. No numerical result invented.
- **BUNDLE_LOCATION (pending_root_choice)**: Compact/full bundle destination not assigned. Commands assume preserved repository-relative layout; original absolute request paths remain historical provenance.
- **PORTABILITY (known_constraint)**: Canonical native rerun needs pinned weights, exact runtime, accepted manifests and new authorized output. Compact saved-output inspection needs no weights. Reanalysis into a NEW result uses relocated absolute request identity, so byte-identical cached request replay is not promised.

Exact command tiers and compact-bundle requirements are in `REPRODUCIBILITY_COMMANDS.md`; JSON includes all frozen model/tokenizer file hashes, source hashes, stage entrypoints and actual snapshot runtime flags.
