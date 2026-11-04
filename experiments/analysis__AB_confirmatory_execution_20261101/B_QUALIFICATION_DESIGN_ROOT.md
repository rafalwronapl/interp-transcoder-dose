# B numerical and reference qualification — root draft1

2026-11-01. Implements unresolved details of ROOT_STAGE_HANDOFF; fresh independent review before B FIT. No edits to running A dependencies/environment. Sol creates exact schedule/contracts and tests, root/Astra review method.

## Spaces, native base and cache

Use native local N0=N(z) and N1=N(z+h) in all vector endpoints, Taylor and labels. CapturedM0 remains the intervention anchor. Save and qualify N0 versusM0; do not hide the discrepancy by replacing one. Compute localN0 once per recipient OR reuse identical scheduled JVP primal (same input,dtype,branchimplementation); count the actual choice,not both. All methods use same endpoints. Native finite margin uses M0+(N1-N0); qualification compares with actual normalized-input edit at c1.

## Independent reference semantics

Primary source: [Google Gemma Scope2 tutorial](https://colab.research.google.com/drive/1NhWjg7n0nhfW--CjtsOdw5A5J_-Bzn4r?usp=sharing), linked by the [official Google model card](https://huggingface.co/google/gemma-scope-2-270m-pt/blob/main/README.md). Read2026-11-01 via indexed tutorial text; direct Colab open returned sign-in,so do not claim a downloaded full notebook or commit-pinned official library.

The tutorial's encoder applies a strict threshold mask to ReLU(preactivation); decoder adds its bias,and optional affine skip maps the original input directly to output. Input/output hooks are post pre-feedforward norm and post post-feedforward norm. Thus multiplying an unrestricted preactivation by the mask is equivalent only with a proven nonnegative-threshold invariant. Preserve ReLU generally. Frozen-mask linear response also respects the active ReLU region. Implement an independently expressed, provenance-bound reference formula and compare actualartifact adapter outputs; label this formula conformance,not certification of all SAELens or model behavior. No package installation during active A needed. Store source note and exact referencecodehash,synthetic threshold-boundary cases and reference parity receipts.

Offline tests include positive,zero,negative thresholds,preactivation at/above/belowthreshold,affine present/absent,orientation/shapes,FP32 formulas and FP64 diagnostic arithmetic. Test actual artifact only in reviewed B stage. Compare adapter/reference inFP32 with maxabsolute<=1e-5 AND vector norm difference<=1e-5*max(norm(reference),1); record both,not only Boolean. Nonfinite outputs fail. These tolerances are prospective and require numerical review before measurement.

## Fixed pretrained recipients and gates

Four recipients:firstFITblock,so/when×two recipient sides; donors remain within block/template. No outcome-based replacement. Capture required natural records once. Gate1 uses ONLY full-operator hook/native/TC/sham/positive/JVP/FD checks on these recipients; it authorizes the remaining NATURAL FIT captures only. Then freeze finalw from all128 FIT captures. Gate2 runs PROJECTED JVP/FD checks on the SAME four cached recipients using finalw; it authorizes expanded local endpoints/baselinefitting. Never use a four-record surrogate direction,never recapture existingnaturalrecords,and never treat gate1 as projected qualification.

Sham input margin and same-output gradient-forward margin must match native baseline within1e-5. Local N0 vsM0 and input-patch vsoutput-patch branch relative norm<=1e-4 with nonzero branch norm; their downstream margins<=1e-4 absolute. Full-head versus declared readout margin<=1e-4. Record signals and rounding discrepancies. Never apply final-layer unreachable-previous-token logic to reachable layer15.

For positive sensitivity,obtain native suffix gradient g at capturedM0 through a same-output patched forward/backward. This call also serves output-sham and can later serve the linear diagnostic; schedule once. Fail zero/nonfiniteg. Unit direction=g/||g||,amplitude=.01*max(||M0||,1),fixed before measurement. Positive injected margin change must exceed max(1e-5,10*observed_max_sham_error,64*float32eps*max(1,abs(native_margin))). Report actual change,gradientnorm,amplitude and floor. A deliberately aligned control tests sensitivity/reachability,not a hypothesis effect. No direction/amplitude search if it fails.

## Native Taylor qualification

For each qualifying recipient and full/projected undosed delta_z,use torch JVP through actual normalized native branch:full belongs to gate1;projected belongs to gate2 AFTER finalw is frozen from all128captures. Store Jdelta once per recipient/operator;scale by each dose for predictions. All finite-input endpoints are still separately computed. Reuse JVP primal for localN0 when identical and check duplicate primal consistency rather than acquire another baseevaluation.

Directional finite-difference steps h=.001 and .0005 times the UNDosed delta_z; central differences [N(z+h delta_z)-N(z-h delta_z)]/(2h). Both must satisfy ||FD-Jdelta|| <= 1e-5*max(||N0||,1)+.02*||Jdelta||. Record each discrepancy,step,signalnorm androundingbaseline. Require finite derivatives; a zero projected direction is explicitly recorded,not replaced. This gate checks local computation at two fixed scales,not large-dose Taylor accuracy. Failure stops expanded B stage and requires diagnosed numerical/operator amendment; no silent looser gate or favorable step selection.

Cost perqualrecipient:one gradient-bearing forward+backward reusedforoutputsham/linearcontrol,onepositiveforward plus other nonredundantsham/parity calls;two baseJVP and8local finite-difference endpoints (2operators×2steps×2signs). Record JVP primal/tangent work separately from localordinarycalls,fullforwards andbackwards. Use exactschedule,not this descriptivecount as authorization. Reuse alreadycaptured endpoints/controlrecords whenever allidentitiesmatch; no whole-stage rerun for proseupdates.
