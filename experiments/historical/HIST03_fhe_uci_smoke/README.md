# HIST03 — smoke test FHE UCI

Unidade histórica do script preservado `experiments/03_fhe_uci_smoke.py`. O relatório local disponível é `results/03_fhe_uci_smoke.json` (e sua projeção CSV). Ele registra coincidência de rótulos para uma observação UCI entre os modos quantizado em claro, simulado e FHE; também registra o rótulo float dessa observação.

Não estão disponíveis a observação selecionada, as predições completas, probabilidades, índices das divisões, modelo/circuito, chaves, manifesto original e timestamp. A importação usa o executor apenas para criar um registro de artefato legado, sem chamar Concrete ML, gerar chaves ou compilar circuito. Os tempos históricos não são benchmarks robustos nem evidência de superioridade entre esquemas FHE.

```bash
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments plan --config experiments/historical/HIST03_fhe_uci_smoke/config.yaml
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments run --config experiments/historical/HIST03_fhe_uci_smoke/config.yaml --execute
```

O notebook é exclusivamente de análise e exige `HIST03_RUN_ID` explícito.
