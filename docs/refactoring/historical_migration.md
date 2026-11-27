# Migração histórica controlada

## HIST01

`experiments/01_baseline.py` foi preservado sem alteração. A unidade `experiments/historical/HIST01_uci_plaintext_baseline/` registra uma configuração recuperada diretamente do script: UCI local em `data/raw`, colunas numéricas sem `ID`, duas divisões estratificadas com `random_state=42`, árvore com profundidade 3 e mínimo de 100 observações por folha, métricas AUC/AP/Brier e cutoff exploratório 0,2.

O adaptador implementa o mesmo fluxo em diretório de Run ID isolado; não redireciona nem substitui a saída do script original. A comparação reexecutada na máquina local produziu igualdade após o arredondamento que o script original já aplica: 18.000/6.000/6.000 observações, AUC 0,7382, AP 0,4799, Brier 0,1379 e aprovação 0,8212.

A equivalência de tempos não foi avaliada. Os artefatos históricos previamente ignorados não continham predições, probabilidades ou manifestos suficientes para comparar uma execução antiga; a evidência é uma reexecução controlada do script preservado e do adaptador no mesmo dataset local.

HIST02 e HIST03 foram apenas registrados como históricos. Não foram movidos, adaptados nem executados nesta etapa.
