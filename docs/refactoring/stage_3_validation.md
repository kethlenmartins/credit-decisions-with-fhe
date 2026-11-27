# Relatório de validação — etapa 3

## Ciclo HIST01

Foi criado o primeiro experimento orientado a unidade, `hist01-uci-plaintext-baseline`. A configuração local, registro central, adaptador autorizado, execução isolada, manifesto, hashes, notebook e documentação foram implementados sem mover `experiments/01_baseline.py`.

O script preservado foi reexecutado localmente com `PYTHONPATH=.`. O adaptador foi executado por CLI com `PYTHONPATH=src`, gerando o Run ID `run-20261127T132415338632Z-d2a30fc17ad04da8a604dd82c03b47ed` em `experiments/historical/HIST01_uci_plaintext_baseline/results/runs/`. `verify` retornou `valid: true`; o manifesto possui `dataset_hash` e hashes individuais dos dois CSVs de entrada.

Após o arredondamento de quatro casas já usado pelo script histórico, as saídas coincidiram: 18.000 treino, 6.000 validação, 6.000 teste, AUC 0,7382, AP 0,4799, Brier 0,1379 e aprovação no cutoff exploratório 0,8212. Isso recupera o comportamento histórico local; não produz evidência sobre Freddie Mac, FHE ou crédito real.

Uma primeira execução da nova configuração, antes do ajuste de resolução da CLI, foi preservada em `results/runs/` por compatibilidade e não foi movida nem sobrescrita. A execução acima demonstra o caminho local definitivo.

## Notebooks

Foram criados a visão geral, o template e o notebook HIST01. Os três são válidos e foram executados sequencialmente por `nbclient` em kernel limpo sem produzir execução experimental. O ambiente de sandbox bloqueia sockets locais de kernels Jupyter; a validação foi repetida com autorização para kernel local e passou.

Na validação final da etapa 3, `MPLCONFIGDIR=/tmp/matplotlib venv/bin/python -m pytest -q` passou com **35 testes em 6,06 s**. O aviso de compatibilidade futura do `nbformat` sobre IDs de células ausentes foi corrigido na etapa 4, sem alterar conteúdo científico; o estado final está em `final_validation.md`.

O notebook HIST01 também foi executado em kernel limpo com o Run ID explícito da reprodução acima. Ele verificou os hashes e carregou os artefatos privados em memória, sem salvar outputs no `.ipynb` nem alterar a execução de origem.

## Governança

`.gitignore` protege recursivamente `experiments/**/results/runs/`, análises privadas, resultados públicos por padrão e checkpoints de notebooks. Nenhuma auditoria concorrente, script histórico, dataset local ou artefato CKKSML foi modificado.

## Limitações

- A análise de gráficos HIST01 requer Run ID e artefatos locais explicitamente fornecidos.
- Os resultados são privados e ignorados; não foram publicados.
- A execução notebook em CI depende de suporte a sockets locais do executor do CI.
- HIST02 e HIST03 aguardam integração de análise; não houve execução FHE.
