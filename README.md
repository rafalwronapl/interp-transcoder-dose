# A Dose-Dependent Crossover in Transcoder Fidelity: Beating Local Linearization Is Not Finite-Effect Accuracy

Author: Rafał Wrona (independent researcher)

A public Gemma-3-270M layer-15 transcoder predicts the downstream pronoun-readout effect of full donor patches with 10.11% relative RMS error (native-vector Taylor 129.96%, ridge 28.05%), while the ranking reverses at small dose. A Gemma-3-1B layer-22 transcoder repeats the crossover but loses to zero change at the full patch; a Qwen3-0.6B CLT component stays at the zero-change baseline.

## Contents

- `paper/` – LaTeX source, figures, compiled `main.pdf` (article with appendix) and `supplement.pdf` (full extended record of all earlier stages, failed forecasts, operation accounting).
- `paper/evidence*`, `paper/*_evidence/` – compact evidence copied for the manuscript: frozen protocols, summaries, independent review receipts, source hashes.
- `experiments/` – code, protocols, reports, summaries, configs and reviews of each experiment stage:
- `experiments/analysis__AB_confirmatory_execution_20261101` (lab path `analysis/AB_confirmatory_execution_20261101`)
- `experiments/analysis__AB_five_experiments_20261103__B_replication` (lab path `analysis/AB_five_experiments_20261103/B_replication`)
- `experiments/analysis__AB_five_experiments_20261103__B_mechanism` (lab path `analysis/AB_five_experiments_20261103/B_mechanism`)
- `experiments/analysis__AB_fast_followups_20261103__B_switch` (lab path `analysis/AB_fast_followups_20261103/B_switch`)
- `experiments/analysis__B_norm_control_20261103` (lab path `analysis/B_norm_control_20261103`)
- `experiments/analysis__B_fresh_transfer_20261103` (lab path `analysis/B_fresh_transfer_20261103`)
- `experiments/analysis__Qwen06_ABC_extension_20261102` (lab path `analysis/Qwen06_ABC_extension_20261102`)
  Per-condition result rows of a stage are merged into `rows.jsonl.gz` (one JSON object per original row file). Files larger than 5 MB (frozen forecasts, fitted models, schedules) are stored as `.gz`.
- `lab_code/` – shared lab modules imported by the experiment workers (model loading, native hooks, tensor encoding, launch/review gate).

## Not included

Model weights (public Hugging Face checkpoints: Qwen/Qwen3-0.6B-Base, google/gemma-3-270m, google/gemma-3-1b-pt, Gemma Scope 2 transcoders, BlueLightAI Qwen3-0.6B CLT), raw activation caches, per-call ledgers and intermediate bundles (several GB). Two frozen forecast files exceed GitHub limits even compressed; their SHA-256 hashes are recorded in the stage manifests.

## Reproducing tables

Every table in `paper/main.tex` reproduces values from the `summary.json` / `REPORT` files of the corresponding stage; no numbers in the manuscript are recomputed at writing time. Re-running a stage requires the model checkpoints and the lab environment (Python 3, PyTorch, transformers); workers expect the original lab layout (`lab_code/` at the repository root of the lab).

Paths inside configs refer to the author's local lab layout and are kept unchanged for provenance.

## License

Code: MIT. Text, figures and data: CC BY 4.0.
