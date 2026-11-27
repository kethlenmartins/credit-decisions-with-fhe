# Reprodução

## Ambiente

Em um ambiente Python isolado, instale as dependências base:

```bash
venv/bin/python -m pip install -r requirements-base.txt
```

Para abrir e validar notebooks em kernel local, instale opcionalmente:

```bash
venv/bin/python -m pip install -r requirements-notebooks.txt
```

Os ambientes Concrete ML e CKKSML são independentes e não são necessários para HIST01. Não se presume compatibilidade entre eles.

HIST02 e HIST03 podem importar os relatórios JSON legados com o ambiente base: o adaptador não importa Concrete ML, não gera chaves e não compila circuitos. Concrete ML é listado como dependência histórica dos scripts preservados, não como requisito da importação.

## Localizar, validar e planejar

```bash
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments list
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments validate --config experiments/historical/HIST01_uci_plaintext_baseline/config.yaml
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments plan --config experiments/historical/HIST01_uci_plaintext_baseline/config.yaml
```

## Executar e consultar HIST01

Após obter UCI por `PYTHONPATH=. venv/bin/python -m src.fhe_credit.download_data`, execute explicitamente:

```bash
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments run --config experiments/historical/HIST01_uci_plaintext_baseline/config.yaml --execute
```

Guarde o `run_id` retornado. Ele identifica a execução privada em `experiments/historical/HIST01_uci_plaintext_baseline/results/runs/`.

```bash
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments verify --run-id RUN_ID
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments analyze --run-id RUN_ID
MPLCONFIGDIR=/tmp/matplotlib venv/bin/python -m pytest -q tests/test_experiment_units.py
```

O teste acima valida os notebooks em kernel limpo sem executar experimentos. Para análise de um resultado real no VS Code/Jupyter local, defina `HIST01_RUN_ID` no ambiente do kernel antes de abrir o notebook. O notebook não cria execução; resultados privados, predições e dados são ignorados pelo Git.

## Importar relatórios históricos sem FHE

```bash
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments plan --config experiments/historical/HIST02_fhe_synthetic_smoke/config.yaml
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments run --config experiments/historical/HIST02_fhe_synthetic_smoke/config.yaml --execute
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments verify --run-id RUN_ID
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments analyze --run-id RUN_ID
```

Troque HIST02 por HIST03 para o smoke UCI. O Run ID retorna uma cópia rastreável do relatório local e um `import_record.json`; o hash ali é calculado na importação, não é um hash da execução histórica. Esses comandos não reexecutam FHE.
