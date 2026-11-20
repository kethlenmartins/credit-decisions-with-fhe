# FHE Credit Decision Stability

Research question: How does quantization precision for FHE-compatible credit-risk models affect decision stability and encrypted inference cost?

## Scope
- UCI Default of Credit Card Clients (30,000 observations; existing cardholders)
- Decision Tree baseline; quantization levels 3–7 bits subject to compiler feasibility
- Three *simulated* policies: PD cutoff, fixed approval fraction, stylized expected utility
- Compare floating-point reference, quantized clear execution, and actual FHE execution

## Quick start
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-base.txt
python -m src.fhe_credit.download_data
python experiments/01_baseline.py
pytest -q
```

FHE dependencies are isolated; see `requirements-fhe.txt`. Concrete ML compatibility varies by Python version/platform; test in a supported Linux environment and pin versions after a successful smoke test.

## Research integrity
- Fit preprocessing on train only; select thresholds on validation only; report test once.
- The dataset covers *existing* cardholders, not rejected applicants; results are retrospective simulations, not causal credit policy evaluations.
- Treat model scores as probabilities only after evaluating/calibrating on validation data.
- No real client data or production underwriting decisions.
- Raw data are downloaded from UCI and not committed; check the source license/attribution before redistributing.

See `docs/research_protocol.md` and `docs/literature_matrix.csv`.

## GitHub private repository bootstrap

Create a **private** repository named `fhe-credit-decision` on GitHub without generating README, license, or gitignore. Then run:

```bash
git init -b main
git add .
git commit -m "chore: initialize reproducible FHE credit research"
git remote add origin git@github.com:YOUR_LOGIN/fhe-credit-decision.git
git push -u origin main
```

The dataset is downloaded on each machine with `python -m src.fhe_credit.download_data`. See `docs/data_provenance.md`.
