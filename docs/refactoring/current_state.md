# Estado atual antes da refatoração

> Baseline de diagnóstico registrada em 27 de novembro de 2026. Este documento
> descreve o estado local observado; não interpreta resultados experimentais nem
> altera o protocolo científico.

## Escopo e comandos de inspeção

Foram lidos `AGENTS.md`, `README.md` e
`artigo/protocolo-experimental.md`. Também foram inspecionados o estado do Git,
a árvore de arquivos, os requisitos, os scripts, os módulos, os testes, os
artefatos locais e as regras de ignorados.

Comandos de validação executados:

```bash
PYTHONPATH=. python -m pytest -q
venv/bin/python -m pytest -q
```

O primeiro comando não foi executado porque `python` não está disponível no
`PATH` desta sessão (`/bin/bash: python: command not found`). O segundo concluiu
com êxito: **8 testes passaram em 1,25 s**. O interpretador usado no segundo
comando foi Python 3.12.3. Esta observação não prova que todos os ambientes
documentados estejam equivalentes.

## Estado do Git e coexistência de trabalho local

- Branch atual: `main`.
- Último commit observado: `702fd3b docs: distingue sample e base completa Freddie`.
- Não havia alterações em arquivos rastreados nem alterações preparadas
  (`git diff --stat` e `git diff --cached --stat` sem saída).
- Havia conteúdo não rastreado. Portanto, ele deve ser considerado trabalho
  local de outros agentes até coordenação explícita.

| Área não rastreada | Evidência observada | Tratamento durante a migração |
| --- | --- | --- |
| `AGENTS.md` | Instruções de trabalho locais | Não mover nem substituir. |
| `datasets/` | Aproximadamente 674 MB; arquivos Freddie Mac, Lending Club e documentação | Dados/documentos locais; não versionar nem relocalizar. |
| `ckksml/` | Aproximadamente 3 MB; PDFs e wheel `ckksml-0.1.0-py3-none-any.whl` | Auditoria/artefatos da biblioteca; não redistribuir nem mover. |
| `dataset-audits-prompt.md`, `libs-audit-prompt.md` | Prompts de frentes de auditoria | Não editar sem coordenação. |

Os diretórios `data/`, `results/`, `venv/` e `.venv-fhe/` existem localmente.
`data/raw/*`, `data/processed/*`, `results/*` e ambientes virtuais já estão
ignorados, com exceção dos respectivos `.gitkeep`. `datasets/` e `ckksml/` não
estão cobertos pela regra atual de `.gitignore`, embora tenham arquivos
não rastreados; isso é um risco de publicação a tratar na etapa de governança.

## Inventário implementado

### Código reutilizável

| Caminho | Responsabilidade atual | Dependências principais |
| --- | --- | --- |
| `src/fhe_credit/policies.py` | Políticas simuladas de cutoff, capacidade e utilidade, além de discordância | NumPy |
| `src/fhe_credit/experiment_results.py` | Comparação pareada e relatório JSON/CSV local | NumPy, biblioteca padrão |
| `src/fhe_credit/download_data.py` | Download e manifesto do UCI 350 | `ucimlrepo`, pandas |
| `src/fhe_credit/dataset_audit/` | Auditoria em streaming de dados Freddie Mac/Lending Club, alvos exploratórios e relatórios | NumPy, pandas, arquivos locais em `datasets/` |

### Experimentos existentes

| Caminho | Estado e escopo declarado | Saídas/dependências |
| --- | --- | --- |
| `experiments/01_baseline.py` | Baseline exploratório UCI em claro; árvore de decisão | `data/raw/features.csv`, `target.csv`, scikit-learn, `policies.py` |
| `experiments/02_fhe_smoke.py` | Smoke test sintético Concrete ML; compara classes em claro, simulação e FHE | Concrete ML, `experiment_results.py`, `results/` |
| `experiments/03_fhe_uci_smoke.py` | Smoke test UCI de uma observação; não é benchmark | UCI local, Concrete ML, scikit-learn, `experiment_results.py` |
| `experiments/dataset_audit/` | Scripts de auditoria de datasets sem treinamento/modelagem FHE | `datasets/`, `dataset_audit/`, `results/dataset_audit/` |

Os resultados locais de `02_fhe_smoke` e `03_fhe_uci_smoke` existem em JSON e
CSV, mas são ignorados pelo Git. Há uma coleção maior de resultados de auditoria
em `results/dataset_audit/`, também ignorada. A existência desses arquivos não
foi usada para reexecutar ou validar os experimentos nesta baseline.

### Testes e ambientes

- Testes: `tests/test_policies.py`, `tests/test_experiment_results.py` e
  `tests/dataset_audit/test_runner.py`; 8 casos passaram no `venv` local.
- Não há pacote instalável (`pyproject.toml`, `setup.py` e `setup.cfg` não foram
  encontrados), nem integração contínua observada.
- `requirements-base.txt` declara intervalos amplos; `requirements-fhe.txt`
  fixa Concrete ML 1.9.0; `requirements-fhe-lock.txt` é um snapshot existente.
- Não foram encontrados notebooks, configuração YAML, Jupyter ou Jupytext no
  inventário de dependências instalado consultado.

## Dependências e problemas de organização

1. Os scripts têm caminhos relativos e parâmetros embutidos (semente, bits,
   modelo e caminhos). Isso dificulta executar uma configuração versionada e
   registrar sua configuração efetiva.
2. `01_baseline.py` e `03_fhe_uci_smoke.py` repetem carregamento, seleção de
   colunas e divisão UCI 60/20/20. A extração futura deve preservar o
   comportamento histórico e ser coberta por testes antes de substituir esses
   scripts.
3. `experiment_results.write_report` escreve nomes fixos e pode sobrescrever
   uma execução anterior; não há `Run ID`, manifesto unificado, checkpoint nem
   retomada.
4. A auditoria de dados já usa `results/dataset_audit/checkpoints`, mas essa
   convenção é independente dos relatórios FHE e ainda não forma um registro
   central de execuções.
5. `README.md` descreve `.venv`, mas o ambiente presente é `venv`; além disso,
   `python` ausente no `PATH` impediu o comando de teste prescrito. A
   documentação deve explicitar a ativação/uso do interpretador sem presumir o
   estado do shell.
6. O README menciona `artigo/README.md` e `artigo/manuscrito.md`, mas os
   arquivos rastreados são `artigo/artigo.md` e não incluem `artigo/README.md`.
   Isso é uma inconsistência de navegação a corrigir separadamente e sem
   renomear o manuscrito existente sem aprovação.

## Delimitações e bloqueadores científicos

- O protocolo e os três experimentos históricos são explicitamente UCI 350;
  os smoke tests não são evidência para Freddie Mac.
- A direção solicitada menciona Freddie Mac Standard Samples de 2015 a 2024,
  mas a auditoria local observada contém `sample_2015.zip` até
  `sample_2021.zip`. Não há base observada para afirmar cobertura 2022--2024.
- Há uma frente de auditoria local em curso que explora Freddie Mac e Lending
  Club. Qualquer migração desses módulos, dados ou resultados requer
  coordenação com seus responsáveis.
- CKKSML está apenas como artefato local não rastreado nesta baseline. Não foi
  instalado, executado nem assumido compatível.
- Não foram executados benchmarks, treinamento definitivo, download adicional
  ou inferência FHE durante este diagnóstico.

## Preservação proposta para a próxima etapa

Manter os scripts numerados como entradas históricas imutáveis na primeira
migração; adicionar adaptadores/configurações e um executor novo ao redor deles.
Somente após comparação de saídas e aprovação explícita os trechos repetidos
devem ser extraídos para módulos. Dados privados/restritos e resultados locais
permanecem fora do controle de versão.
