# HIST02 — smoke test FHE sintético

Unidade histórica do script preservado `experiments/02_fhe_smoke.py`. O script não foi movido nem é chamado pelo executor. O único relatório legado disponível é `results/02_fhe_smoke.json` (e sua projeção CSV); ele registra coincidência de rótulos entre os modos quantizado em claro, simulado e FHE para dois vetores sintéticos.

Os tempos são uma medição histórica pontual, não benchmark. Não há chaves, circuito, amostras, predições individuais, probabilidades, manifesto original ou timestamp de execução disponíveis. Portanto, a importação abaixo só copia o conteúdo verificável para um Run ID novo e registra o hash calculado na importação; não alega reexecução FHE.

```bash
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments plan --config configs/experiments/historical_fhe_smoke_synthetic.yaml
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments run --config configs/experiments/historical_fhe_smoke_synthetic.yaml --execute
```

O notebook é exclusivamente de análise e exige `HIST02_RUN_ID` explícito.
