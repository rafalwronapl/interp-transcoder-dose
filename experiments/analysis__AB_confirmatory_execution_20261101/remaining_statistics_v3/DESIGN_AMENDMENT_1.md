# Prospective bridge multiplicity clarification

2026-11-01, before new calibration tests/campaign. Root accepted this correction explicitly.

The number K of eligible family cases depends on historical outcomes. Therefore the historical CP upper must NOT be recomputed with a looser adaptive .05/(2K) allocation. Preserve its original saved upper, verifying it against the historical false count and fixed original total-case upper-tail alpha .05/(2*TOTAL). These original simultaneous upper-bound failure probabilities sum to at most.025. New bridge datasets are independent of the historical samples; conditional on that history, use alpha .05/(2K) for each production-only upper. Their conditional failure probabilities sum to at most.025. Consequently the combined original-upper plus bridge-upper bound has simultaneous MC confidence at least95%. Original failed groups remain excluded.

This supersedes only the earlier sentence about recomputing old bounds. No saved calibration value is altered or rerun.
