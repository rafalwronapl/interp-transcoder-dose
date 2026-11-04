# Astra preparation audit ? round 3

Snapshot ce61441c5fef1ef3e65eb96cfb4fc955089a34db578965a6fcc70da64261ed1c captures 34 actual read sources. Draft code inspection only, not launch approval.

AP5 HIGH sequencing issue is resolved by explicit gate1/full controls, remaining natural captures, final direction, then gate2/projected controls. The code follows this order and reuses cached qualification endpoints.

AP6 HIGH independently reported during code review: expected TC output reused production encoder preactivation. The captured round3 code already resolves it by independently applying F.linear to the input/raw encoder weights/bias. Root was asked for a mutant encoder test before executable approval.

AP7 HIGH independently reported during code review: runtime request code identity omitted config. The captured round3 code already resolves it by hashing sources plus config SHA256. Root was asked for mismatch-cache evidence before executable approval. Active A already used this binding and was unaffected.

AP8 medium, open in this snapshot: nonzero branch norm must be enforced explicitly, not replaced by denominator max(norm,1e-30). Save actual norm, gradient norm/amplitude and both TC discrepancy diagnostics for audit. This is a pre-B-launch code consistency issue, not a reason to repeat A.

AP9 medium, open documentary clarity: the18 scalar stability scenarios establish pointwise interval calibration only. Declare no joint four-component coverage; all-four width attainment may remain descriptive.

The N computation bridge is valid: for reduced success R and production success P, Pr(P)>=Pr(R)-Pr(R and notP). Simultaneous lower/upper one-sided CP bounds for12 cases use24 bounds; overlap of first1000 paired draws does not invalidate the union bound. This is conditional on the frozen empirical generator, not population-tail coverage.

Official indexed tutorial formula was independently retrieved using the exact query supplied by root. ReLU, strict threshold, decoder bias, optional input skip and norm hook coordinates are corroborated; no commit-pinned upstream runtime certification is claimed. See reference_lookup_v2.json.

The reference callable now schedules both adapter and independent reference evaluations. Exact future packet, source-stable synthetic tests, canonical snapshot and review remain required before B launch. No pretrained calls or edits outside reviewer-owned directory.
