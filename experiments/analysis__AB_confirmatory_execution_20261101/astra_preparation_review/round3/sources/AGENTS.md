# Research workflow

## Required independent review (user instruction, 2026-10-20)

- The user explicitly requests a separate agent to review potential mistakes after our work. After substantive changes to a research plan, implementation, analysis or conclusions, obtain a fresh independent agent review BEFORE the final answer. Also obtain a pre-run review BEFORE expensive/pretrained experiment stages. This authorizes delegation for these reviews; it does not authorize paid external providers.
- Follow `plans/RESEARCH_REVIEW_POLICY.md`. The main agent implements; a separate reviewer examines the actual files, evidence and a hash-bound snapshot. Do not write an approval in the reviewer's name. Resolve blocker/high findings and obtain re-review of the changed snapshot. Record other findings and their disposition.
- New experiment workers must use `python -m research_checks launch --snapshot ... --review ...`. Run the inexpensive preflight and synthetic tests first; provide required hook/data/pilot/accounting/restart evidence. The launcher checks evidence and review BEFORE importing the worker. If agent review is unavailable, report that limitation and leave the expensive stage unstarted; do not silently waive it. This is a machine/agent gate, not a request for renewed user permission.
- Before evaluating a reduced circuit, verify layer/position/within-block reachability to EVERY required checkpoint, then a nonzero numerical sensitivity control. A natural-state match or same-value sham alone cannot establish sensitivity. Changing an attention output cannot feed the same layer's attention input. An MLP cannot transmit between token positions.
- Bind all actually read historical raw records, activations, datasets, imported local code and model identity, not just convenient subsets. Freeze the input set before its first use; data captured only after a run is a posthoc snapshot. Cache keys must include document, coordinates/settings, readout, model and code identities. Immutable receipts must survive resume byte-for-byte; test partial failure and restart before scale-up.
- Preserve E023 and earlier frozen code/data/reports. Methodological corrections go in `analysis/E023_method_review/`; new scientific comparisons use a new experiment ID and fresh holdouts. Do not "repair" a negative finding by changing its historical criteria.
- Negative outcomes of valid experiments are useful. Prevent structurally impossible, under-instrumented or unauditable runs; do not promise all hypotheses will succeed. Report procedural completion separately from questions actually tested and supported.

- User preference: check nearest existing work BEFORE proposing each new hypothesis. Record the closest papers and the exact difference. Do not label an idea unique merely because a search returned no exact match.
- Persistent hypotheses are in hypotheses.json and the linked private Page. Keep each hypothesis, falsifier and novelty status available for later sessions.
- E001 is an exploratory pilot on Qwen3-0.6B-Base, not a population study or a claim that the Goodfire hypothesis is proven.
- Never tune a protocol, neuron selection or agent prompt using held-out intervention outcomes. Use a new experiment identifier for any new scientific comparison.
- Preserve raw API responses, costs, failures, frozen forecasts, source/data/protocol hashes, and implementation amendments. Report unsuccessful results.
- Start long computations detached with logs; on Windows use Start-Process -WindowStyle Hidden. Check for an existing process before starting another.
- Do not provision cloud GPUs as part of a local rerun. Respect the protocol's API budget. Credentials stay in the environment and must not appear in logs or artifacts.
- Record actual model revision, dtype and whether measurements occur before the answer. A native SwiGLU neuron is the product coordinate before down_proj.
- Verify same-value sham patches, replacement coordinates, token alignment and first-token versus full-answer metrics.
- Report subgroup and sign-regime coverage. A lack of relevant contexts limits what a null result can establish.
- Read README.txt for execution and artifact locations. Do not commit model weights or credentials.
- E002 uses the user's existing Codex session/subscription for agent tasks and local Qwen inference. Do not use OpenRouter, Claude, separately billed APIs, or purchase additional credits for E002. The older API budget/client applies only to historical E001. Preserve that history.
- For E002, follow plans/E002_PLAN.txt: fresh-context task packets, auditable tool traces, and freeze all forecasts before test interventions. A fresh subagent context does not itself restrict access to shared files. Checkpoint on Codex availability limits; never switch to a paid provider automatically.
