# Validação final da refatoração estrutural

## Escopo e decisão

Validação concluída em 27 de novembro de 2026 para a infraestrutura experimental. Não foram executados FHE, geração de chaves, compilação de circuitos, download de dados ou mudanças em auditorias concorrentes.

## Evidências verificadas

- O registro ativo `experiments/registry.yaml` é a única lista de unidades; `configs/registry/experiments.yaml` apenas redireciona para ele.
- HIST01 permanece reproduzível pelo adaptador existente e a comparação já demonstrada é apenas das métricas agregadas arredondadas: AUC 0,7382, AP 0,4799, Brier 0,1379 e aprovação 0,8212, para 18.000/6.000/6.000 observações.
- A execução histórica original de HIST01 não forneceu predições, probabilidades, índices de divisão, lista/ordem de features, hiperparâmetros serializados ou métricas sem arredondamento. Os artefatos atuais permitem verificar a reexecução controlada, mas não provar identidade integral retrospectiva.
- HIST02 tem `results/02_fhe_smoke.json` e CSV: configuração/ambiente parcial, tempos e concordância de classes para dois vetores. HIST03 tem o análogo UCI para uma observação. Ambos carecem de manifesto original, timestamp, chaves, circuito, entradas/predições individuais e probabilidades; HIST03 também carece dos índices das divisões e da observação escolhida.
- Os notebooks de visão geral, template, HIST01, HIST02 e HIST03 possuem IDs de célula válidos e únicos, não têm outputs e executam em kernel limpo sem iniciar experimento.
- `git check-ignore` confirmou proteção para runs, resultados públicos não revisados, análises, checkpoints, modelos, chaves e artefatos CKKSML. Resultados privados e dados locais não foram acrescentados aos arquivos rastreados.

## Comandos validados

```bash
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments list
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments validate --config experiments/historical/HIST02_fhe_synthetic_smoke/config.yaml
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments plan --config experiments/historical/HIST03_fhe_uci_smoke/config.yaml
PYTHONPATH=. venv/bin/python -m pytest -q
```

Também foram validados estruturalmente todos os notebooks com `nbformat`; a suíte executa-os em kernel limpo. A importação HIST02/HIST03 requer somente o ambiente base e o JSON legado local; com `--execute`, cria um Run ID de importação, não uma execução FHE.

## Limitações e recomendação

Não houve ambiente base novo criado nem instalação, para não modificar ambientes existentes; a validação usou o ambiente local já disponível. Resultados de smoke tests são técnicos e históricos, não benchmarks nem conclusões científicas. Recomenda-se encerrar a refatoração estrutural e aguardar aprovação explícita antes de integrar auditorias científicas.
