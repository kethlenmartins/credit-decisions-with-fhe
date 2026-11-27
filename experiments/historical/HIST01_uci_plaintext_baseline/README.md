# HIST01 — baseline UCI em texto claro

Unidade histórica que recupera a configuração de `experiments/01_baseline.py` sem mover ou modificar o script original. O dataset UCI 350 contém portadores de cartão existentes; este experimento não valida underwriting real, Freddie Mac, políticas financeiras definitivas ou inferência FHE.

Planeje com:

```bash
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments plan --config experiments/historical/HIST01_uci_plaintext_baseline/config.yaml
```

A execução requer os arquivos locais ignorados `data/raw/features.csv` e `data/raw/target.csv`, e autorização explícita:

```bash
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments run --config experiments/historical/HIST01_uci_plaintext_baseline/config.yaml --execute
```

Os resultados privados são gravados em `results/runs/<run-id>/` dentro desta unidade. Use o notebook em modo de análise após obter um Run ID verificável.
