# N01 — árvore Freddie Mac: sklearn e Concrete ML

Experimento **EXPLORATORY**. O target é ocorrência observada de status de delinquency `>= 3` dentro de 12 meses desde a First Payment Date. Pré-pagamento (`01`) anterior ao horizonte é negativo; códigos `02`, `03`, `09`, `96`, códigos desconhecidos e seguimento menor que o horizonte são excluídos. Não é uma definição final de risco, nem valida concessão real.

Treino: 2015--2017; validação: 2019; teste exploratório: 2021. As sete features são numéricas de originação e códigos `999`/`9999` são tratados como ausentes. Medianas e clipping são ajustados apenas no treino.

```bash
PYTHONPATH=src .venv-fhe/bin/python -m fhe_credit.experiments run --config experiments/04_numerical_fidelity/N01_freddie_mac_decision_tree/config.yaml --execute
```

O run gera resultados privados por Run ID. Não versionar predições, modelo, dados nem artefatos FHE.
