# Final executable preparation: selector launch and secondary analyses

2026-11-01. New modules only. Approved Aeligibility/selector numerical sources and queued model packets are unchanged. No model or Monte Carlo campaign ran here. No new scientific design or hypothesis was introduced. Actual future input receipts are still required; the code/packet paths are executable without additional methodological decisions.

## Selector packet

After the actual PILOT arrays and eligibility have been independently accepted, prepare the input manifest with the already approved prepare_selector_v5 helper. Then:

```
python -m ab_confirmatory_20261101.prepare_selector_packet_v5 --manifest ACTUAL_ONE_STUDY_SELECTOR_MANIFEST --pilot-snapshot ACTUAL_PILOT_COMPLETION_SNAPSHOT --pilot-review ACTUAL_PILOT_COMPLETION_REVIEW --out NEW_SELECTOR_PACKET
```

This checks the actual original PILOT assembly manifest/raw closure, all candidate eligibility, and accepted fixed r0scale forA. It emits `operations.json` with an empty operation list, zero forward/backward caps, fixed compute budget, exact entrypoint arguments and a research_checks experiment contract. The entrypoint is selector_execution_v5 with explicit `--study A` or `B`. Original case indices/seeds,2000replicates and alpha.05/16 remain frozen. All acceptance snapshot members are flattened into the input manifest, not only result files.

Snapshot/pre-run review/normal canonical launch follow. No operator needs to design a new schedule or statistical rule after PILOT.

## Secondary analysis packets

After actual TEST completion is accepted:

```
python -m ab_confirmatory_20261101.prepare_secondary_v5 --packet ACTUAL_PRIMARY_TEST_PACKET --acceptance-snapshot ACTUAL_TEST_COMPLETION_SNAPSHOT --acceptance-review ACTUAL_TEST_COMPLETION_REVIEW --out NEW_SECONDARY_PACKET
```

The builder supports A and B using config.study. It rejects PILOT and nonprimary A cohorts, validates every sealed raw file against its accepted hash and binds every transitive acceptance member. It emits a zero-model experiment contract and exact entrypoint:

```
python -m ab_confirmatory_20261101.secondary_analysis_v5 --manifest NEW_SECONDARY_PACKET/analysis_manifest.json --out NEW_SECONDARY_PACKET/run
```

Use research_checks snapshot/pre-run review/launch around that entrypoint. Preparation maintenance review is not scientific-stage launch approval.

A invokes the reviewed a_descriptive_records formula on actualr0TEST:30frame/arm cells, including zero/P/allU, native signal, improvements and harm frequency. Pointwise construction uses1999draws. No support slots are added and the primaryr0 family remains separate.

B invokes the reviewed all-method/dose/template RMS formula:288cells=6methods×2operators×4template summaries(so,when,transfer,equal-main-energy mixture)×6doses. ZERO appears exactly once. Energies are pooled before square roots/ratios. All positive, negative and inconclusive cells remain present.

The36 B operator/template/dose diagnostics reconstruct ACTUAL vectors from sealed runtimecache: native JVP primal N0, native endpoint N1, TC base TC0, TC endpoint TC1, and cached native suffix gradient. Cache operation/request/document/model/code identities are checked. Reconstructed endpoint errors must equal stored e0/e1. Endpoint decomposition receives these true anchors, never fakezeros, preserving float32-vs-float64 subtraction diagnostics. TC linear diagnostics use the actual float32 TCdelta prescription; native delta remains the actual endpoint difference. Reconstructed linear errors are checked against stored measurements. Existing endpoint and linear helper formulas are unchanged; method-specific stored linear/vector errors also receive descriptive summaries.

Per-statistic immutable caches use exact input-array hashes, source/runtime/input identity, draw count and seed. Private function namespaces inject this cache around existing helper functions without modifying frozen module globals. Endpoint/linear helpers and method summaries share the same mean-statistic cache. Identical native-signal summaries are reused. Top-level outputs bind all cell receipt hashes; replay rejects corruption and performs no new bootstrap computation for completed cells. Raw inputs remain required and verified. Model calls are always zero.

## Verification and remaining gates

Three cheap secondary fixtures passed: all A30cells and per-statistic replay; B288+36cells, actual nonzero endpoint anchors, oneZERO and replay forbidding any helper recomputation; zero-model packet preflight. One selector-packet fixture passed. After transitive acceptance-closure additions, both cheap packet preflights passed again. No numerical calibration suite or model test was repeated. Numerical formulas already have their preserved shared-kernel evidence.

Fixtures mock external review acceptance and numerical summary calls where stated; they test orchestration/cache/schema, not scientific coverage. Actual Aeligibility was separately finalized through real canonical review. Actual PILOT/TEST results and their own completion/pre-run reviews remain future execution gates, not unfinished implementation. Articles remain deferred until experiments are complete.
