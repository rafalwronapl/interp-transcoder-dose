# Independent pre-run review: one native capture

Reviewer: `/root/sol_ab_execution/single_capture_review`.
Verdict: **approved**, solely for snapshot `85b0db98fa1df7068ddb4333906a4c300649eff006421a128053b514dd431332` and the stage described below.

Read actual AGENTS/review policy, stage protocol, packet, manifest, identity, operations, evidence, contract, preparation code, production worker, production tests, persistence implementation and canonical snapshot verification implementation. No inherited approval was used.

The stage executes one complete natural Gemma-3-1b forward, no backward, on the frozen A/r0/FIT_MAP literal at final token and decoder layer 25 of 26. The hooks record the actual MLP argument, first-linear argument, post-feedforward normalization output, residual before feedforward normalization and final-normalization input. Because the selected block is the last block, the checked residual identity is appropriate. Hook handles are removed even on failure; nonfinite captures and failed identities are rejected. `logits_to_keep=1` still performs the complete native decoder path and retains only final-position logits. No intervention or reduced circuit is evaluated.

The frozen technical-only amendment is appropriate: a single natural observation need not establish perturbation sensitivity or freeze a statistical sample size to support its stated technical purpose. This does not waive those requirements for later intervention/FIT/hypothesis stages. This record cannot by itself support any A/B claim or automatically become a fitted sample.

Independent checks completed without pretrained loading:

- `python -m research_checks check .../contract.json`: all five category gates and 1-forward/0-backward accounting pass.
- `python -m unittest ab_confirmatory_20261101.test_single_capture`: both tests pass. Actual tiny Gemma capture checks the within-forward identities; mocked production loader checks zero-load/zero-forward replay, unchanged receipt bytes and refusal to retry after a failed reserved capture.
- Actual frozen tokenizer encodes the literal to exactly the packet IDs; answer IDs decode to ` is` and ` are` in the stated orientation.
- Recomputed canonical snapshot equals the supplied SHA, including current model-file hashes, evidence, transitive research_checks source and environment identity.

The attempt reservation precedes the measured forward and blocks unreviewed repeated computation after partial failure. Failures during loading before reservation can be retried without consuming a native measurement. Cache completion is content-bound and immutable. The canonical launch lock remains necessary to exclude concurrent workers; author must perform the protocol's live resource/process check before hidden detached launch.

Limits: synthetic models do not prove trained-model numerical success, sham, nonzero sensitivity, transfer, fit utility or statistical adequacy. There was no pretrained load, forward or scientific-result inspection by this reviewer. Actual run receipts, identities, timing, resource use and the limited interpretation require independent completion audit. Model/library identity has the environment-binding limits documented by research_checks. No blocker or high finding remains.
