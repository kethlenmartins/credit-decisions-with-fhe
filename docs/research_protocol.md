# Protocol v0.1 (pre-registered intentions)

## Main research question
How does quantization precision for FHE-compatible credit-risk models affect simulated credit decision stability and encrypted inference cost?

## Hypotheses
- H1: Reduced bit precision can alter decisions even with small AUC changes.
- H2: Decision disagreements concentrate near a policy cutoff.
- H3: Quantization settings produce measurable latency/stability trade-offs.

## Dataset and limitations
UCI 350: Default of Credit Card Clients. Historical cardholder dataset, not an application approval dataset. No counterfactual outcomes for denied applicants. Retrospective simulations only.

## Splits and leakage control
Stratified train/validation/test = 60/20/20; fixed seed 42. Fit all transformations on train. Fit any calibration and select all policy thresholds on validation. Evaluate final results on untouched test. Prefer additional seeds as time allows.

## Policies
A: PD cutoff, initially candidates 0.10/0.20/0.30, adjust using validation distribution and report rationale.
B: Approve bottom 20/40/60% by score, with deterministic tie-breaking.
C: Stylized utility U = EAD * ((1-PD)*r - PD*LGD) - c. Assumptions fixed before test; credit limit is an exposure proxy only, not new loan principal.

## Measurement
Compare (i) float baseline, (ii) quantized clear model, (iii) actual encrypted inference. Separate model differences from FHE correctness. Measure AUC, AP, Brier, decision disagreement, approval rate, observed defaults among approved, latency, compilation, encryption, decryption, memory when feasible.

## Feasibility gate
Run 1 encrypted inference using a shallow decision tree and supported Concrete ML version. If actual FHE is prohibitively slow, do full policy evaluation on quantized clear inference and a prespecified stratified FHE sample; report selection and scope clearly.

## Scientific cautions
A decision tree's predict_proba may produce discretized leaf frequencies, not calibrated PD. Evaluate calibration and, if used, fit calibration on validation without leakage. Approval-by-capacity uses ranking across the full sample and is an offline portfolio policy, not per-request encrypted execution. Policy logic is evaluated after decrypting model output in v0.1; do not claim end-to-end encrypted decisioning.
